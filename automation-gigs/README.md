# automation-gigs

An automation-services business designed to be run by an agent. Buyers come
inbound from Fiverr and Upwork; a headless Claude Code pipeline builds each
deliverable; James pastes the delivery.

```
listings/     Fiverr gig copy (3 gigs) and Upwork profile, catalog, proposal template
portfolio/    3 importable n8n workflows with README + test cases (public proof of work)
pipeline/     fulfill.py (brief -> deliverable via `claude -p`), intake.py (inbox -> orders),
              validate_n8n.py (structural check + secret scan), prompts/fulfillment.md
orders/       one folder per order: brief.md, deliverable/, STATUS.json, fulfill.log
launchd/      15-minute poller for the Mac mini
SETUP_30_MINUTES.md   the one-time human part
```

## How an order flows
1. Fiverr/Upwork emails "new order" → `intake.py` creates `orders/<id>/brief.md`.
2. `fulfill.py` sends the brief + `prompts/fulfillment.md` to `claude -p`,
   writes the returned files, validates any `*.workflow.json`, runs one
   repair pass if validation fails, and writes `STATUS.json`.
3. `intake.py` zips the deliverable and emails James the delivery message.
4. James pastes it into the order. Done.

## Run it by hand
```
python3 pipeline/fulfill.py orders/<order-dir>            # real build
python3 pipeline/fulfill.py orders/<order-dir> --mock     # plumbing test, no API
python3 pipeline/validate_n8n.py portfolio/*/*.workflow.json
```

`orders/example-shopify-low-stock-alert/` is a real order brief run through
the pipeline end to end; its `deliverable/` is what a buyer receives.

## Pricing
Set from Fiverr/Upwork 2026 demand data (Claude Code specialist demand +938%,
n8n +125% year over year per Fiverr's Business Trends Index). Entry tiers are
priced low to win first reviews; raise Basic to $200 after 5 reviews.
