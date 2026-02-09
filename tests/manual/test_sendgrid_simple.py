"""
Simple SendGrid test - bypasses Firebase
"""
import os
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# Load .env
load_dotenv()

# Get config
api_key = os.getenv("SENDGRID_API_KEY")
from_email = os.getenv("SENDGRID_FROM_EMAIL")
to_email = "hello@thejaggerypoint.com"

print("=" * 60)
print("SendGrid Direct Test")
print("=" * 60)
print(f"API Key: {api_key[:20]}..." if api_key else "API Key: NOT FOUND")
print(f"From: {from_email}")
print(f"To: {to_email}")
print()

if not api_key:
    print("❌ ERROR: SENDGRID_API_KEY not found in .env")
    exit(1)

if not from_email:
    print("❌ ERROR: SENDGRID_FROM_EMAIL not found in .env")
    exit(1)

try:
    # Create message
    message = Mail(
        from_email=from_email,
        to_emails=to_email,
        subject='IgniteAI Test Email',
        html_content='<h1>Test Email</h1><p>This is a test email from IgniteAI to verify SendGrid integration.</p>'
    )
    
    # Send
    print("Sending email...")
    sg = SendGridAPIClient(api_key)
    response = sg.send(message)
    
    print()
    print("=" * 60)
    print(f"✅ SUCCESS!")
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.body}")
    print(f"Response Headers: {response.headers}")
    print("=" * 60)
    print()
    print("Check your inbox at hello@thejaggerypoint.com")
    
except Exception as e:
    print()
    print("=" * 60)
    print(f"❌ ERROR: {str(e)}")
    print()
    print("Common issues:")
    print("- Invalid API key (401)")
    print("- Sender email not verified (403)")
    print("- Rate limit (429)")
    print("=" * 60)
    import traceback
    traceback.print_exc()
