# Setup and launch gates

The build is a starting point for a service business. There are no verified sales from this system. Setup time depends on account checks and live integration testing.

## Account status on the Mini
- Upwork already exists. Do not create a duplicate account. The latest ID submission is awaiting review; existing proposals remain separate from Project Catalog setup.
- Fiverr: account @jgoodnight318 created with jms.goodnight@gmail.com. Seller profile and first gig are complete. The gig is saved; phone and identity verification are complete. Form W-9 remains before publication.
- The portfolio page in this draft PR is not deployed to main yet. Do not advertise links as live before deployment.

## Local intake

Real order data is kept OUTSIDE this public repository at `~/.local/share/automation-gigs/orders/`. The inbox is read-only: no unread flags are changed. A notification creates an unverified candidate; it does not prove a funded order or trigger model spending.

Create `~/.config/automation-gigs.env` with mode 600:
```
GIGS_IMAP_USER=jms.goodnight@gmail.com
GIGS_IMAP_PASS=<Google app password>
GIGS_NOTIFY_TO=jms.goodnight@gmail.com
GIGS_NOTIFY_ENABLED=1
```
Do not paste this credential into chat or commit it. If Google does not allow an app password, use the existing signed-in browser to inspect orders and download their notifications as `.eml` files; `intake.py --eml /path/to/order.eml` provides local intake without mail credentials.

```
python3 automation-gigs/pipeline/intake.py --check
python3 automation-gigs/pipeline/install.py
python3 automation-gigs/pipeline/install.py --enable
```
The installer prepares an absolute-path launch agent and enables it only after mail is configured. It does not claim the mail connection is tested. Run intake once to validate real IMAP/SMTP access before relying on the schedule.

## From candidate to fulfillment
1. Open the actual platform order. Confirm funding, deadline, purchased scope, actual requirements and permission to use any supplied data. Email subjects alone are not sufficient.
2. Replace the candidate `brief.md` with the agreed brief and save `approval.json`:
```
{"funding_verified":true,"scope_reviewed":true,"platform_order_url":"<actual order URL>","kind":"n8n","max_build_cost_usd":4}
```
3. Run `python3 automation-gigs/pipeline/fulfill.py /absolute/private/order-directory`. No tool access is given to the model. There are at most two calls sharing the total budget.
4. `NEEDS_REVIEW` means structure and basic credential scanning passed. Import into the target n8n version, connect test credentials, run the agreed acceptance cases, and record actual evidence. Do not activate sending actions without testing and authorization.
5. Resolve NEEDS_INFO with the buyer. Replies are NOT automatically merged or rerun. Update the same verified order; don't create a new paid build from each email.
6. Deliver only after acceptance tests and attachment review. Sending a ZIP is not the completion of testing.

## Local verification
```
python3 -m unittest discover -s automation-gigs/tests -v
node automation-gigs/tests/test_shopify.mjs
```
Mock runs validate plumbing only. The historical $400 brief is synthetic, with no $400 sale. Its original reported model cost was $1.1782; fees, sales work, setup, tests, revisions and support are additional costs.

## Local n8n verification runtime
n8n 2.39.5 with Node 24 is installed separately at `~/.local/share/automation-gigs-runtime`. Its private test database is under `~/.local/share/automation-gigs/n8n`. Four inactive workflow imports succeeded. `python3 automation-gigs/tests/n8n_smoke.py` ran the Shopify graph for multiple suppliers, no low stock, and GraphQL errors; external API and messaging nodes were replaced with stubs. These tests sent no messages and do not prove real credentials work.

Claude Code is signed into the owner's Max subscription on this Mini. Local runs may consume subscription usage; the sample API-dollar estimate is not a cash-profit calculation. The CLI is configured with a per-call API budget and at most two calls; verify usage behavior for the selected authentication method before unattended paid builds.
