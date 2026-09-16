# Inbound lead qualifier

Every unread sales-type email hitting your Gmail is read by Claude, scored
0–100 for buying intent, logged to a Google Sheet, and — if it scores 60 or
more — posted to Slack with a suggested reply and a link back to the thread.
API failures post a warning to the same channel instead of dropping the lead.

**Nodes:** Gmail Trigger → HTTP Request (Anthropic Messages API) → Code
(parse) → IF (score ≥ 60) → Slack alert + Google Sheets append. Error branch → Slack.

## Setup (10 minutes)
1. n8n → Workflows → Import from file → `lead-qualifier.workflow.json`.
2. Credentials to create: Gmail OAuth2, Google Sheets OAuth2, Slack bot
   token (scope `chat:write`), and a **Header Auth** credential named
   *Anthropic x-api-key* with header name `x-api-key` and your Anthropic key.
   Assign each on its node.
3. Replace `YOUR_SHEET_ID` (from the sheet URL) and `YOUR_SLACK_CHANNEL`.
   Create a sheet tab called `Leads` with headers:
   `received, from, subject, score, intent, summary, suggested_reply, gmail_link`.
4. Optional: tune the Gmail search query on the trigger and the 60 threshold on the IF node.
5. Activate. Send yourself a test email containing “interested in pricing”.
