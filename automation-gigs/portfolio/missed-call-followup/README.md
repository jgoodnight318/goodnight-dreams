# Missed call → instant text-back

When a call to your Twilio number goes unanswered, the caller gets a text
within seconds (different wording after hours), and the miss is logged to a
Google Sheet so nothing falls through.

**Nodes:** Webhook (Twilio status callback) → IF missed → IF business hours
→ Twilio SMS (two variants) → Google Sheets append.

## Setup (10 minutes)
1. Import `missed-call-followup.workflow.json`, activate it, copy the
   production webhook URL from the first node.
2. Twilio Console → your phone number → Voice → *Call status changes*:
   paste the webhook URL, method POST.
3. Credentials: Twilio (Account SID + Auth Token), Google Sheets OAuth2.
4. Replace `YOUR_TWILIO_NUMBER`, `YOUR_BUSINESS_NAME`, `YOUR_BOOKING_LINK`,
   `YOUR_SHEET_ID`, `YOUR_TIMEZONE` (e.g. `America/Phoenix`). Create a sheet
   tab `Missed calls` with headers `when, caller, status, texted`.
5. Test: call the number from your cell and don't pick up.
