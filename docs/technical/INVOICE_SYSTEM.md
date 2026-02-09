# Invoice PDF Generation System

**Date:** January 2026
**Framework:** FastAPI + xhtml2pdf
**Templates:** Jinja2

## Overview
The system generates professional PDF invoices on-the-fly and sends them as email attachments when a subscription payment is successful. It is built using `xhtml2pdf` for HTML-to-PDF conversion and integration with SendGrid.

## Architecture

1.  **Trigger**: Payment success event (Webhook or Manual Trigger).
2.  **Data Collection**: `EmailService` collects user details, plan info, and transaction data.
3.  **Rendering**:
    -   `invoice.html` is rendered with Jinja2 using the transaction data.
    -   `invoice_body.html` is rendered for the email body.
4.  **PDF Conversion**: The rendered HTML is passed to `pisa.CreatePDF` (from `xhtml2pdf`).
5.  **Delivery**: The PDF binary is attached to the SendGrid email object and sent.

## Templates

### `invoice.html` (The PDF)
Located at: `projects/backend/email_templates/invoice.html`

**Design Principles:**
-   **Classic Boxed Layout**: Uses HTML `<table>` structures exclusively. CSS Grid and Flexbox are **NOT** supported by `xhtml2pdf`.
-   **Robustness**:
    -   **No Nested Tables for Alignment**: We use flat table rows with specific column widths (e.g., 60% spacer, 20% label, 20% value) to align elements like "Total".
    -   **Non-Collapsing Spacers**: Empty spacer cells (`<td></td>`) **must** contain `&nbsp;` if they rely on percentage widths. Otherwise, `xhtml2pdf` may collapse them to 0 width, breaking alignment.
    -   **Inline Styles**: Most critical styles are inline or in a `<style>` block within the head.
    -   **Colors**: Uses IgniteAI brand colors (Indigo `#6366F1`).

### `invoice_body.html` (The Email)
Located at: `projects/backend/email_templates/invoice_body.html`

-   Responsive "Card" layout.
-   Contains a clear "Go to Dashboard" call to action.
-   Matches the application's design language.

## Troubleshooting xhtml2pdf

**Common Errors:**
1.  **`TypeError: '>' not supported between instances of 'NoneType' and 'NoneType'`**:
    -   **Cause**: Usually caused by complex nested tables or floating constraints that the engine cannot resolve.
    -   **Fix**: Simplify the table structure. Remove nested tables and use a single table with defined column widths.

2.  **"Negative availWidth" or Content on Left**:
    -   **Cause**: The renderer calculates the available width for a cell as negative or zero, often because an empty cell collapsed.
    -   **Fix**: Add content to empty cells (`&nbsp;`) and ensure `padding` + `width` doesn't exceed 100%.

## Testing

**Manual Test Script**:
```bash
python3 tests/manual/test_invoice_email.py
```
This script sends a real email to `hello@thejaggerypoint.com` with dummy data.

**HTML Preview Script**:
```bash
python3 scripts/utils/render_invoice.py
```
This renders the raw HTML files to `projects/backend/tmp/` so you can visually inspect the layout in a browser before PDF conversion.
