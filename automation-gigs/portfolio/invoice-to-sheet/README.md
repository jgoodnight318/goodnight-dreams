# Invoice PDF → Google Sheets

Any email with a PDF invoice or receipt is read, the key fields (vendor,
number, dates, subtotal, tax, total) are extracted by Claude, a row is
appended to your Invoices sheet, and the email is labelled *processed*.
If extraction fails or a total is missing, the email is labelled
*needs-review* instead so nothing silently disappears.

**Nodes:** Gmail Trigger (with attachment download) → Extract From File
(PDF) → HTTP Request (Anthropic) → Code → Google Sheets append → Gmail label.

## Setup (10 minutes)
1. Import `invoice-to-sheet.workflow.json`.
2. Credentials: Gmail OAuth2 (used twice), Google Sheets OAuth2, Header
   Auth *Anthropic x-api-key* (header `x-api-key`).
3. In Gmail create labels `processed` and `needs-review`; put their IDs in
   the two Gmail nodes (n8n shows the ID in the label dropdown).
4. Replace `YOUR_SHEET_ID`; create tab `Invoices` with headers:
   `received, from, subject, vendor, invoice_number, invoice_date, due_date, currency, subtotal, tax, total, line_items_summary, needs_review`.
5. Forward yourself a real invoice PDF to test.
