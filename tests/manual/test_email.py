"""
Test script to verify SendGrid email integration
Sends a test email to verify configuration
"""
import asyncio
import sys
import os
import traceback
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from projects.backend.services.email_service import email_service

async def send_test_email():
    """Send a test email to verify SendGrid configuration"""
    
    print("=" * 60)
    print("IgniteAI Email Service Test")
    print("=" * 60)
    print()
    
    # Test email details
    test_email = "hello@thejaggerypoint.com"
    test_name = "Test User"
    
    print(f"Sending test email to: {test_email}")
    print(f"Template: welcome.html")
    print()
    
    try:
        # Send welcome email as test
        success = await email_service.send_welcome_email(
            user_email=test_email,
            user_name=test_name,
            credits=10
        )
        
        print()
        print("=" * 60)
        if success:
            print("✅ SUCCESS! Test email sent successfully!")
            print()
            print("Next steps:")
            print("1. Check inbox at hello@thejaggerypoint.com")
            print("2. Check spam folder if not in inbox")
            print("3. Verify SendGrid dashboard for delivery status")
            print("   https://app.sendgrid.com/email_activity")
        else:
            print("❌ FAILED! Email was not sent.")
            print()
            print("Troubleshooting:")
            print("1. Check if EMAIL_ENABLED=true in .env")
            print("2. Verify SENDGRID_API_KEY is valid")
            print("3. Ensure SENDGRID_FROM_EMAIL is verified in SendGrid")
            print("4. Check backend logs for detailed errors")
        print("=" * 60)
        
        return success
        
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ ERROR: {str(e)}")
        print()
        print("Full traceback:")
        traceback.print_exc()
        print()
        print("Common issues:")
        print("- Invalid SendGrid API key (401 error)")
        print("- Sender email not verified (403 error)")
        print("- Rate limit exceeded (429 error)")
        print("- Network connectivity issues")
        print("=" * 60)
        return False

if __name__ == "__main__":
    # Run the async function
    result = asyncio.run(send_test_email())
    sys.exit(0 if result else 1)
