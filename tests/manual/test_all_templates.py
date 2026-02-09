"""
Comprehensive Email Template Test
Tests all 9 email templates one by one
"""
import os
import asyncio
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
from datetime import datetime

# Load environment variables
load_dotenv()

# Configuration
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL")
SENDGRID_FROM_NAME = os.getenv("SENDGRID_FROM_NAME", "IgniteAI Team")
BUSINESS_ADDRESS = os.getenv("BUSINESS_ADDRESS")
SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:4200")
TEST_EMAIL = "hello@thejaggerypoint.com"

# Initialize Jinja2
TEMPLATE_DIR = Path("projects/backend/email_templates")
jinja_env = Environment(
    loader=FileSystemLoader(str(TEMPLATE_DIR)),
    autoescape=select_autoescape(['html', 'xml'])
)

def render_template(template_name, context):
    """Render email template"""
    # Add common context
    context.update({
        'business_address': BUSINESS_ADDRESS,
        'support_email': SUPPORT_EMAIL,
        'frontend_url': FRONTEND_URL,
        'current_year': datetime.now().year,
        'unsubscribe_url': f"{FRONTEND_URL}/email-preferences"
    })
    
    template = jinja_env.get_template(f"{template_name}.html")
    return template.render(**context)

def send_email(subject, html_content):
    """Send email via SendGrid"""
    message = Mail(
        from_email=(SENDGRID_FROM_EMAIL, SENDGRID_FROM_NAME),
        to_emails=TEST_EMAIL,
        subject=subject,
        html_content=html_content
    )
    
    sg = SendGridAPIClient(SENDGRID_API_KEY)
    response = sg.send(message)
    return response.status_code in [200, 201, 202]

# Test templates
templates = [
    {
        "name": "welcome",
        "subject": "Welcome to IgniteAI, Test User! Your 10 free credits await 🎬",
        "context": {
            "user_name": "Test User",
            "credits": 10,
            "dashboard_url": f"{FRONTEND_URL}/editor"
        }
    },
    {
        "name": "verification",
        "subject": "Verify your IgniteAI email address",
        "context": {
            "user_name": "Test User",
            "verification_link": f"{FRONTEND_URL}/verify-email?token=test_token_123",
            "expiry_hours": 24
        }
    },
    {
        "name": "generation_started",
        "subject": "Your video is being created! 🎬",
        "context": {
            "user_name": "Test User",
            "run_id": "run_1234567890",
            "project_name": "Wireless Earbuds Ad",
            "credits_deducted": 10,
            "new_balance": 90,
            "estimated_time": "3-5 minutes",
            "status_url": f"{FRONTEND_URL}/projects"
        }
    },
    {
        "name": "generation_completed",
        "subject": "Your video is ready! 🎉",
        "context": {
            "user_name": "Test User",
            "run_id": "run_1234567890",
            "project_name": "Wireless Earbuds Ad",
            "video_url": "https://example.com/video.mp4",
            "download_url": "https://example.com/video.mp4",
            "dashboard_url": f"{FRONTEND_URL}/projects",
            "duration": "15s",
            "scenes": 4,
            "generation_time": "4m 23s",
            "credits_used": 10
        }
    },
    {
        "name": "generation_failed",
        "subject": "We encountered an issue with your video generation",
        "context": {
            "user_name": "Test User",
            "run_id": "run_1234567890",
            "project_name": "Wireless Earbuds Ad",
            "error_message": "We're experiencing high demand. Please try again in a few minutes.",
            "credits_refunded": 10,
            "new_balance": 100,
            "retry_url": f"{FRONTEND_URL}/editor",
            "support_url": f"mailto:{SUPPORT_EMAIL}"
        }
    },
    {
        "name": "credit_purchase",
        "subject": "Payment confirmed - 100 credits added to your account",
        "context": {
            "user_name": "Test User",
            "transaction_id": "pay_ABC123XYZ",
            "amount": 49,
            "credits_purchased": 100,
            "new_balance": 150,
            "payment_method": "Razorpay",
            "timestamp": "January 15, 2026 at 12:30 AM",
            "dashboard_url": f"{FRONTEND_URL}/editor"
        }
    },
    {
        "name": "low_credits",
        "subject": "Your IgniteAI credits are running low (8 remaining)",
        "context": {
            "user_name": "Test User",
            "current_balance": 8,
            "videos_remaining": 0,
            "pricing_url": f"{FRONTEND_URL}/pricing",
            "recommended_plan": "Starter"
        }
    },
    {
        "name": "password_reset",
        "subject": "Reset your IgniteAI password",
        "context": {
            "user_name": "Test User",
            "reset_link": f"{FRONTEND_URL}/reset-password?token=reset_token_456",
            "expiry_hours": 1,
            "ip_address": "192.168.1.1",
            "timestamp": "January 15, 2026 at 12:30 AM"
        }
    },
    {
        "name": "scene_regeneration",
        "subject": "Your Hook scene has been regenerated",
        "context": {
            "user_name": "Test User",
            "run_id": "run_1234567890",
            "scene_name": "Hook",
            "video_url": "https://example.com/video_updated.mp4",
            "credits_used": 2,
            "new_balance": 88,
            "dashboard_url": f"{FRONTEND_URL}/projects"
        }
    }
]

print("=" * 70)
print("IgniteAI Email Template Test Suite")
print("=" * 70)
print(f"Sending to: {TEST_EMAIL}")
print(f"Total templates: {len(templates)}")
print()

results = []

for i, template_data in enumerate(templates, 1):
    template_name = template_data["name"]
    subject = template_data["subject"]
    context = template_data["context"]
    
    print(f"[{i}/{len(templates)}] Testing: {template_name}.html")
    print(f"    Subject: {subject[:60]}...")
    
    try:
        # Render template
        html_content = render_template(template_name, context)
        
        # Send email
        success = send_email(subject, html_content)
        
        if success:
            print(f"    ✅ Sent successfully")
            results.append((template_name, True, None))
        else:
            print(f"    ❌ Failed to send")
            results.append((template_name, False, "Send failed"))
    except Exception as e:
        print(f"    ❌ Error: {str(e)}")
        results.append((template_name, False, str(e)))
    
    print()
    
    # Small delay between emails to avoid rate limiting
    if i < len(templates):
        import time
        time.sleep(1)

# Summary
print("=" * 70)
print("Test Summary")
print("=" * 70)

success_count = sum(1 for _, success, _ in results if success)
fail_count = len(results) - success_count

print(f"Total: {len(results)}")
print(f"✅ Successful: {success_count}")
print(f"❌ Failed: {fail_count}")
print()

if fail_count > 0:
    print("Failed templates:")
    for name, success, error in results:
        if not success:
            print(f"  - {name}: {error}")
    print()

print("=" * 70)
print("Next Steps:")
print("1. Check inbox at hello@thejaggerypoint.com")
print("2. Check spam folder if emails not in inbox")
print("3. Verify all templates render correctly")
print("4. Check SendGrid dashboard for delivery status")
print("   https://app.sendgrid.com/email_activity")
print("=" * 70)
