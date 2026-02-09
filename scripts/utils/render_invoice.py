
import os
import sys
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape

# Setup paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'projects/backend/email_templates')
OUTPUT_DIR = os.path.join(BASE_DIR, 'projects/backend/tmp')

# Ensure output dir exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Function to render
def render_template(template_name, context, output_name):
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template(template_name)
    rendered = template.render(**context)
    
    output_path = os.path.join(OUTPUT_DIR, output_name)
    with open(output_path, 'w') as f:
        f.write(rendered)
    print(f"Rendered {template_name} to {output_path}")

# Helper to get logo
import base64
def get_logo():
    try:
        logo_path = os.path.join(BASE_DIR, 'projects/frontend/public/assets/transparent-logo.png')
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as f:
                return base64.b64encode(f.read()).decode('utf-8')
    except:
        return ""
    return ""

# Test Data
context = {
    "user_name": "Pankaj Sarkar",
    "user_email": "hello@thejaggerypoint.com",
    "invoice_number": "INV-2026-001",
    "date": "January 24, 2026",
    "plan_name": "Agency Annual",
    "period_start": "Jan 24, 2026",
    "period_end": "Jan 24, 2027",
    "currency": "USD",
    "amount": "4997.00",
    "business_name": "IgniteAI",
    "business_address": "Bangalore, India",
    "support_email": "support@igniteai.com",
    "frontend_url": "https://app.igniteai.in",
    "logo_data": get_logo()
}

if __name__ == "__main__":
    print("Rendering templates...")
    render_template("invoice.html", context, "preview_invoice.html")
    render_template("invoice_body.html", context, "preview_invoice_body.html")
    print("Done.")
