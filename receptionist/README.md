# receptionist — missed-call text-back service for local businesses

Recurring-revenue service: $149/mo text-back, $349/mo receptionist tier. Built on
Twilio + n8n. One multi-tenant workflow serves every client; each client's config
travels in the query string of their Twilio number's voice URL, so there is no database.

```
index.html                 public landing page with pricing (link targets are Gumroad memberships)
prospect.py                public-data prospect finder (OpenStreetMap, free, no key)
enrich.py                  finds a public contact email on the prospect's site; skips ones with live answering
draft_outreach.py          Claude drafts one personalised intro email per prospect into data/outbox/ (never sends)
templates/                 outreach brief, onboarding questions, go-live email with forwarding codes, FAQ
n8n/missed-call-multitenant.workflow.json   the fulfillment: forwarded call -> TwiML greeting + SMS + log
launchd/                   daily prospect -> enrich -> draft job
RUNBOOK.md                 per-client onboarding (about 4 minutes each) and the daily send step
SETUP.md                   one-time accounts and env
```

## Unit economics per client
| | Text-back | Receptionist |
|---|---|---|
| Price | $149/mo | $349/mo |
| Twilio number | $1.15/mo | $1.15/mo |
| SMS (~60 misses/mo) | ~$0.50 | ~$0.50 |
| Voice minutes (receptionist, ~100 min) | – | ~$15–25 (Vapi/Retell + Twilio) |
| Gumroad fee (10% + 30¢) | ~$15 | ~$35 |
| **Net** | **~$132** | **~$290** |

Ten text-back clients is about $1,300/mo net for a few minutes of onboarding each.

## The daily loop (automated)
1. `prospect.py` pulls up to 40 businesses in the configured city and trade.
2. `enrich.py` finds a public contact email and drops anyone already advertising live answering.
3. `draft_outreach.py` writes up to 25 personalised drafts to `data/outbox/` with a review CSV.

## What stays human, and why
- **Sending the outreach.** The drafts are written for you; you open the outbox and send the ones
  you approve from the outreach mailbox. Unattended bulk cold email from a personal account is the
  fastest way to get the domain blacklisted, and CAN-SPAM requires a working postal address and
  opt-out on every message (the footer has both, but the address has to be yours).
- **No automated test-calls.** An earlier design had the agent phone each business to prove they
  miss calls. Auto-dialled calls sit under TCPA and state robocall rules, and the harness refused to
  build it. The outreach angle uses the published industry statistic instead.
- **Buying the client's Twilio number** is a one-minute console click per client (RUNBOOK.md).
  Everything after that is the n8n workflow.
