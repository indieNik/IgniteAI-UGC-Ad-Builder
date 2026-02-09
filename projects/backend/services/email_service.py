"""
Email Service for IgniteAI
Handles all email communications using SendGrid
"""
import os
import asyncio
from typing import Dict, Optional, List
from datetime import datetime
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, Category
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
import base64
import io
from xhtml2pdf import pisa
from sendgrid.helpers.mail import Mail, Email, To, Content, Category, Attachment, FileContent, FileName, FileType, Disposition


logger = logging.getLogger(__name__)

# Email service configuration
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", "noreply@igniteai.com")
SENDGRID_FROM_NAME = os.getenv("SENDGRID_FROM_NAME", "IgniteAI Team")
BUSINESS_ADDRESS = os.getenv("BUSINESS_ADDRESS", "123 Innovation St, San Francisco, CA 94105")
SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL", "support@igniteai.com")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:4200")
EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "true").lower() == "true"
EMAIL_RETRY_ATTEMPTS = int(os.getenv("EMAIL_RETRY_ATTEMPTS", "3"))

# Initialize Jinja2 template environment
TEMPLATE_DIR = Path(__file__).parent.parent / "email_templates"
jinja_env = Environment(
    loader=FileSystemLoader(str(TEMPLATE_DIR)),
    autoescape=select_autoescape(['html', 'xml'])
)


class EmailService:
    """Service for sending emails via SendGrid"""
    
    def __init__(self):
        self.client = SendGridAPIClient(SENDGRID_API_KEY) if SENDGRID_API_KEY else None
        self.from_email = Email(SENDGRID_FROM_EMAIL, SENDGRID_FROM_NAME)
        
    def _render_template(self, template_name: str, context: Dict) -> str:
        """Render email template with context data"""
        try:
            # Add common context variables
            context.update({
                'business_address': BUSINESS_ADDRESS,
                'support_email': SUPPORT_EMAIL,
                'frontend_url': FRONTEND_URL,
                'current_year': datetime.now().year,
                'unsubscribe_url': f"{FRONTEND_URL}/email-preferences"
            })
            
            template = jinja_env.get_template(f"{template_name}.html")
            return template.render(**context)
        except Exception as e:
            logger.error(f"Error rendering template {template_name}: {str(e)}")
            raise
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        template_name: str,
        context: Dict,
        category: str = "transactional"
    ) -> bool:
        """
        Send an email using SendGrid
        
        Args:
            to_email: Recipient email address
            subject: Email subject line
            template_name: Name of the template file (without .html)
            context: Dictionary of variables for template rendering
            category: Email category for tracking (transactional, operational, marketing)
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not EMAIL_ENABLED:
            logger.info(f"Email disabled. Would have sent '{subject}' to {to_email}")
            return False
            
        if not self.client:
            logger.error("SendGrid client not initialized. Check SENDGRID_API_KEY")
            return False
        
        try:
            # Render HTML content
            html_content = self._render_template(template_name, context)
            
            # Create email message
            message = Mail(
                from_email=self.from_email,
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", html_content)
            )
            
            # Add category for tracking
            message.category = Category(category)
            
            # Send email with retry logic
            for attempt in range(EMAIL_RETRY_ATTEMPTS):
                try:
                    response = self.client.send(message)
                    
                    if response.status_code in [200, 201, 202]:
                        logger.info(f"Email sent successfully to {to_email}: {subject}")
                        
                        # Get message ID safely
                        message_id = None
                        try:
                            if hasattr(response, 'headers') and isinstance(response.headers, dict):
                                message_id = response.headers.get('X-Message-Id')
                            elif hasattr(response, 'headers'):
                                # Try to get as attribute
                                message_id = getattr(response.headers, 'get', lambda x: None)('X-Message-Id')
                        except:
                            pass
                        
                        # Log to Firestore (async, don't block)
                        asyncio.create_task(self._log_email(
                            to_email=to_email,
                            subject=subject,
                            template_name=template_name,
                            category=category,
                            status="sent",
                            sendgrid_message_id=message_id
                        ))
                        
                        return True
                    else:
                        logger.warning(f"SendGrid returned status {response.status_code}")
                        
                except Exception as e:
                    logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                    if attempt < EMAIL_RETRY_ATTEMPTS - 1:
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    else:
                        # Log failure
                        asyncio.create_task(self._log_email(
                            to_email=to_email,
                            subject=subject,
                            template_name=template_name,
                            category=category,
                            status="failed",
                            error=str(e)
                        ))
                        raise
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    async def _log_email(
        self,
        to_email: str,
        subject: str,
        template_name: str,
        category: str,
        status: str,
        sendgrid_message_id: Optional[str] = None,
        error: Optional[str] = None
    ):
        """Log email to Firestore for tracking and analytics"""
        try:
            from projects.backend.services.db_service import db
            
            email_log = {
                "to_email": to_email,
                "subject": subject,
                "template_name": template_name,
                "category": category,
                "status": status,
                "sent_at": datetime.now().isoformat(),
                "sendgrid_message_id": sendgrid_message_id,
                "error": error,
                "opened_at": None,
                "clicked_at": None
            }
            
            db.collection("email_logs").add(email_log)
            
        except Exception as e:
            logger.error(f"Failed to log email: {str(e)}")
    
    # ========== Specific Email Methods ==========
    
    async def send_welcome_email(
        self,
        user_email: str,
        user_name: str,
        credits: int = 10
    ) -> bool:
        """Send welcome email to new users"""
        return await self.send_email(
            to_email=user_email,
            subject=f"Welcome to IgniteAI, {user_name}! Your {credits} free credits await 🎬",
            template_name="welcome",
            context={
                "user_name": user_name,
                "credits": credits,
                "dashboard_url": f"{FRONTEND_URL}/editor"
            },
            category="transactional"
        )
    
    async def send_verification_email(
        self,
        user_email: str,
        user_name: str,
        verification_token: str
    ) -> bool:
        """Send email verification link"""
        verification_link = f"{FRONTEND_URL}/verify-email?token={verification_token}"
        
        return await self.send_email(
            to_email=user_email,
            subject="Verify your IgniteAI email address",
            template_name="verification",
            context={
                "user_name": user_name,
                "verification_link": verification_link,
                "expiry_hours": 24
            },
            category="transactional"
        )
    
    async def send_free_tier_verification_email(
        self,
        user_email: str,
        user_name: str,
        verification_token: str
    ) -> bool:
        """Send email verification link for free tier signup with credit reward"""
        verification_link = f"{FRONTEND_URL}/verify-email?token={verification_token}"
        
        return await self.send_email(
            to_email=user_email,
            subject="Verify your email & claim 10 free credits! 🎁",
            template_name="free_tier_verification",
            context={
                "user_name": user_name,
                "verification_link": verification_link,
                "expiry_hours": 24,
                "credits_reward": 10
            },
            category="transactional"
        )
    
    async def send_generation_started(
        self,
        user_email: str,
        user_name: str,
        run_id: str,
        project_name: str,
        credits_deducted: int = 10,
        new_balance: int = 0,
        estimated_time: str = "3-5 minutes"
    ) -> bool:
        """Send notification when video generation starts"""
        return await self.send_email(
            to_email=user_email,
            subject=f"Your video is being created! 🎬",
            template_name="generation_started",
            context={
                "user_name": user_name,
                "run_id": run_id,
                "project_name": project_name,
                "credits_deducted": credits_deducted,
                "new_balance": new_balance,
                "estimated_time": estimated_time,
                "status_url": f"{FRONTEND_URL}/projects"
            },
            category="operational"
        )
    
    async def send_generation_completed(
        self,
        user_email: str,
        user_name: str,
        run_id: str,
        project_name: str,
        video_url: str,
        stats: Dict
    ) -> bool:
        """Send notification when video generation completes successfully"""
        return await self.send_email(
            to_email=user_email,
            subject=f"Your video is ready! 🎉",
            template_name="generation_completed",
            context={
                "user_name": user_name,
                "run_id": run_id,
                "project_name": project_name,
                "video_url": video_url,
                "download_url": video_url,
                "dashboard_url": f"{FRONTEND_URL}/projects",
                "duration": stats.get("duration", "15s"),
                "scenes": stats.get("scenes", 4),
                "generation_time": stats.get("generation_time", "N/A"),
                "credits_used": stats.get("credits_used", 10)
            },
            category="operational"
        )
    
    async def send_generation_failed(
        self,
        user_email: str,
        user_name: str,
        run_id: str,
        project_name: str,
        error_message: str,
        credits_refunded: int = 10,
        new_balance: int = 0
    ) -> bool:
        """Send notification when video generation fails"""
        # Make error message user-friendly
        friendly_errors = {
            "rate_limit": "We're experiencing high demand. Please try again in a few minutes.",
            "invalid_input": "The uploaded image format is not supported. Please use JPG or PNG.",
            "api_error": "We encountered a temporary issue with our AI service. Please try again.",
        }
        
        user_friendly_error = friendly_errors.get(
            error_message.lower(),
            "We encountered an unexpected error. Our team has been notified."
        )
        
        return await self.send_email(
            to_email=user_email,
            subject="We encountered an issue with your video generation",
            template_name="generation_failed",
            context={
                "user_name": user_name,
                "run_id": run_id,
                "project_name": project_name,
                "error_message": user_friendly_error,
                "credits_refunded": credits_refunded,
                "new_balance": new_balance,
                "retry_url": f"{FRONTEND_URL}/editor",
                "support_url": f"mailto:{SUPPORT_EMAIL}"
            },
            category="operational"
        )
    
    async def send_scene_regeneration_completed(
        self,
        user_email: str,
        user_name: str,
        run_id: str,
        scene_id: str,
        video_url: str,
        credits_used: int = 2,
        new_balance: int = 0
    ) -> bool:
        """Send notification when scene regeneration completes"""
        scene_names = {
            "Hook": "Hook",
            "Feature": "Feature",
            "Lifestyle": "Lifestyle",
            "CTA": "Call-to-Action"
        }
        
        return await self.send_email(
            to_email=user_email,
            subject=f"Your {scene_names.get(scene_id, scene_id)} scene has been regenerated",
            template_name="scene_regeneration",
            context={
                "user_name": user_name,
                "run_id": run_id,
                "scene_name": scene_names.get(scene_id, scene_id),
                "video_url": video_url,
                "credits_used": credits_used,
                "new_balance": new_balance,
                "dashboard_url": f"{FRONTEND_URL}/projects"
            },
            category="operational"
        )
    
    async def send_credit_purchase_confirmation(
        self,
        user_email: str,
        user_name: str,
        transaction: Dict
    ) -> bool:
        """Send confirmation email after credit purchase"""
        return await self.send_email(
            to_email=user_email,
            subject=f"Payment confirmed - {transaction['credits_purchased']} credits added to your account",
            template_name="credit_purchase",
            context={
                "user_name": user_name,
                "transaction_id": transaction.get("transaction_id"),
                "amount": transaction.get("amount"),
                "credits_purchased": transaction.get("credits_purchased"),
                "new_balance": transaction.get("new_balance"),
                "payment_method": transaction.get("payment_method", "Razorpay"),
                "timestamp": transaction.get("timestamp", datetime.now()).strftime("%B %d, %Y at %I:%M %p"),
                "dashboard_url": f"{FRONTEND_URL}/editor"
            },
            category="transactional"
        )
    
    async def send_low_credits_warning(
        self,
        user_email: str,
        user_name: str,
        current_balance: int,
        videos_remaining: int = 0
    ) -> bool:
        """Send warning when user's credit balance is low"""
        return await self.send_email(
            to_email=user_email,
            subject=f"Your IgniteAI credits are running low ({current_balance} remaining)",
            template_name="low_credits",
            context={
                "user_name": user_name,
                "current_balance": current_balance,
                "videos_remaining": videos_remaining,
                "pricing_url": f"{FRONTEND_URL}/pricing",
                "recommended_plan": "Growth" if current_balance < 5 else "Starter"
            },
            category="operational"
        )
    
    async def send_password_reset(
        self,
        user_email: str,
        user_name: str,
        reset_token: str,
        ip_address: Optional[str] = None
    ) -> bool:
        """Send password reset email"""
        reset_link = f"{FRONTEND_URL}/reset-password?token={reset_token}"
        
        return await self.send_email(
            to_email=user_email,
            subject="Reset your IgniteAI password",
            template_name="password_reset",
            context={
                "user_name": user_name,
                "reset_link": reset_link,
                "expiry_hours": 1,
                "ip_address": ip_address,
                "timestamp": datetime.now().strftime("%B %d, %Y at %I:%M %p")
            },
            category="transactional"
        )
    def _get_logo_base64(self) -> str:
        """Read logo image and return as base64 string"""
        try:
            # Navigate to project root from projects/backend/services/email_service.py
            current_dir = Path(__file__).parent
            project_root = current_dir.parent.parent.parent
            
            # Try multiple paths for robustness (local vs docker)
            possible_paths = [
                project_root / "projects" / "frontend" / "public" / "assets" / "transparent-logo.png",
                project_root / "projects" / "frontend" / "src" / "assets" / "transparent-logo.png",
                Path("/app/projects/frontend/public/assets/transparent-logo.png") # Docker absolute
            ]
            
            for logo_path in possible_paths:
                if logo_path.exists():
                    with open(logo_path, "rb") as img_file:
                        return base64.b64encode(img_file.read()).decode('utf-8')
            
            logger.warning(f"Logo not found in any expected location")
            return ""
        except Exception as e:
            logger.error(f"Failed to load logo: {e}")
            return ""

    async def send_invoice_email(
        self,
        user_email: str,
        user_name: str,
        invoice_details: Dict
    ) -> bool:
        """Send invoice/receipt email with PDF attachment"""
        
        # Get logo for PDF
        logo_data = self._get_logo_base64()
        
        # 1. Render PDF content (using invoice.html)
        pdf_html = self._render_template("invoice", {
            "user_name": user_name,
            "user_email": user_email,
            "invoice_number": invoice_details.get("invoice_number"),
            "date": invoice_details.get("date", datetime.now().strftime("%B %d, %Y")),
            "plan_name": invoice_details.get("plan_name", "Subscription"),
            "period_start": invoice_details.get("period_start", ""),
            "period_end": invoice_details.get("period_end", ""),
            "currency": invoice_details.get("currency", "USD"),
            "amount": invoice_details.get("amount", "0.00"),
            "business_name": "IgniteAI",
            "logo_data": logo_data,
        })
        
        # Convert HTML to PDF
        pdf_buffer = io.BytesIO()
        pisa_status = pisa.CreatePDF(
            io.BytesIO(pdf_html.encode("utf-8")),
            dest=pdf_buffer
        )
        
        if pisa_status.err:
            logger.error(f"PDF generation error: {pisa_status.err}")
            return False
            
        pdf_bytes = pdf_buffer.getvalue()
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        # 2. Render Email Body (using invoice_body.html)
        email_body_html = self._render_template("invoice_body", {
             "user_name": user_name,
             "plan_name": invoice_details.get("plan_name", "Subscription"),
             "invoice_number": invoice_details.get("invoice_number"),
             "date": invoice_details.get("date"),
             "amount": invoice_details.get("amount"),
             "currency": invoice_details.get("currency", "USD"),
             "business_name": "IgniteAI",
        })

        # 3. Create Message with Attachment
        message = Mail(
            from_email=self.from_email,
            to_emails=To(user_email),
            subject=f"Your IgniteAI Invoice #{invoice_details.get('invoice_number')}",
            html_content=Content("text/html", email_body_html)
        )
        message.category = Category("transactional")
        
        # Add Attachment
        attachment = Attachment(
            FileContent(pdf_base64),
            FileName(f"Invoice_{invoice_details.get('invoice_number')}.pdf"),
            FileType("application/pdf"),
            Disposition("attachment")
        )
        message.attachment = attachment
        
        # 4. Send via existing client logic
        try:
             response = self.client.send(message)
             if response.status_code in [200, 201, 202]:
                 logger.info(f"Invoice email sent to {user_email}")
                 return True
             else:
                 logger.error(f"Failed to send invoice email: {response.status_code}")
                 return False
        except Exception as e:
             logger.error(f"Exception sending invoice email: {e}")
             return False



# Singleton instance
email_service = EmailService()
