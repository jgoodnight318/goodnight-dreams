# One-time setup (about 40 minutes)

1. **Twilio** (twilio.com): create account, add $20 credit, upgrade out of trial (required to text
   arbitrary numbers). Note Account SID and Auth Token for the n8n credential.
2. **n8n**: import `n8n/missed-call-multitenant.workflow.json`, create the Twilio credential and a
   Google Sheets credential, create a sheet tab `Missed calls` with headers
   `when, business, caller, open_hours`, replace `YOUR_SHEET_ID`, activate, copy the production
   webhook URL (this is the base of every client's voice URL).
3. **Gumroad** (existing account): two membership products, monthly, 14-day free trial:
   "Missed-Call Text-Back" $149/mo and "Missed-Call Receptionist" $349/mo. Paste their URLs into
   `index.html` in place of `GUMROAD_TEXTBACK_URL` and `GUMROAD_RECEPTIONIST_URL`.
4. **Outreach mailbox**: a dedicated address, ideally on a domain you own (Google Workspace, $7/mo),
   not your personal Gmail. Add a reply-to that reaches you.
5. **Env file** `~/.config/receptionist.env`:
   ```
   RCP_CITY=Phoenix
   RCP_CATEGORY=plumber
   RCP_FROM_NAME=James
   RCP_FROM_EMAIL=hello@yourdomain.com
   RCP_POSTAL_ADDRESS=Your street address, City, ST 00000
   RCP_LANDING_URL=https://jgoodnight318.github.io/goodnight-dreams/receptionist/
   ```
6. **launchd** on the Mac mini:
   ```
   cp receptionist/launchd/com.james.receptionist-prospects.plist ~/Library/LaunchAgents/
   launchctl load ~/Library/LaunchAgents/com.james.receptionist-prospects.plist
   ```
7. Optional, receptionist tier: Vapi or Retell account with Claude as the model.
