# Runbook

## Daily (2 minutes)
1. Open `receptionist/data/outbox/REVIEW.csv`. Each row is a drafted intro email.
2. Send the ones you approve from the outreach mailbox (open the `.eml`, or copy subject and body).
   Aim for 10–25 a day, never more, to keep the domain warm.
3. Replies arrive in the outreach mailbox. "Interested" → paste `templates/onboarding_email.md`.
   "STOP" or no → add their email to the `do_not_contact` column in `data/prospects.csv`.

## Per client (4 minutes)
When someone answers the three onboarding questions (business number, hours + booking link, tier):
1. Twilio Console → Phone Numbers → Buy a number → their area code, Voice + SMS. About $1.15/mo.
2. On the number's Voice configuration: **A call comes in → Webhook**, method POST, URL:
   ```
   https://YOUR-N8N/webhook/missed-call?biz=Acme+Plumbing&booking=https://acme.example/book&tz=America/Phoenix&sms_from=%2B16025550100
   ```
   (URL-encode the business name; `sms_from` is the number you just bought, `+` as `%2B`.)
3. Send `templates/golive_email.md` with `{business}`, `{twilio_number}`, `{tier}` filled in. It
   contains the carrier forwarding codes; the client dials one code and is live.
4. Receptionist tier: Vapi (or Retell) dashboard → New assistant → paste the greeting from
   `templates/faq.md`'s "Who" line plus their hours and booking link → Phone numbers → Import from
   Twilio → pick the number → attach the assistant. Then set the Twilio voice URL to Vapi's instead
   of the n8n webhook (Vapi shows the URL).
5. Gumroad membership handles billing and the one-week trial; cancellation email → cancel in Gumroad
   and release the number in Twilio.

## Monthly
- Twilio usage vs. Gumroad payouts; anyone whose number gets zero forwarded calls in 30 days gets a
  check-in email (their forwarding is probably off).
