
import os
import sys
import asyncio
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Load env vars
load_dotenv()

# MONKEY PATCH SSL to bypass proxy issues
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

from projects.backend.services.email_service import email_service


async def test_send_invoice():
    print("Sending test invoice email...")
    try:
        success = await email_service.send_invoice_email(
            user_email="hello@thejaggerypoint.com",
            user_name="Pankaj Sarkar",
            invoice_details={
                "invoice_number": "TEST-INV-AGENCY-001",
                "date": "January 24, 2026",
                "plan_name": "Agency Annual",
                "period_start": "Jan 24, 2026",
                "period_end": "Jan 24, 2027",
                "currency": "USD",
                "amount": "4997.00"
            }
        )
        
        if success:
            print("✅ Email sent successfully!")
        else:
            print("❌ Failed to send email (check logs/SendGrid key)")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_send_invoice())
