# How this earns money

We sell a working automation for a specific business process. Buyers pay for setup, integration testing and a supported handover. Code generation reduces production time; it does not supply demand, credentials, acceptance testing or customer support.

## First transaction
A small business wants a daily low-stock report grouped by supplier. Before accepting $400, confirm its n8n version, Shopify API access, product/variant counts, inventory definition, Slack destination, timezone and expected sample output. The portfolio workflow is a starting point with explicit limits, not an untested file we send unchanged.

A funded platform order enters the private queue. We verify the scope, prepare the brief, run a capped build, import into the correct n8n version, test normal/empty/error cases, and deliver the workflow plus evidence. One revision is included. Avoid activating messaging against real destinations until the customer-approved test is complete.

## Acquisition experiment: first 14 days after publication
- Upwork Catalog project 2099999933366679169 is approved and visible. After Fiverr finishes reviewing the submitted W-9, publish its saved gig with the same focused offer and honest demo.
- Reuse the existing Upwork account; don't create a second profile. ID review may limit publishing.
- Review a small set of recent, relevant buyer requests daily. Draft tailored proposals that reference the exact requested workflow. Paid Connects spend and proposal sending follow the user's existing authorization and any current platform limits; do not buy more without approval.
- Answer relevant inbound messages, confirm scope, and suggest a small repair when a full build is unnecessary. No bulk unsolicited messages or invented experience.
- Record impressions, clicks, qualified inquiries, funded orders, total build/testing time, revisions and net proceeds in `sales-ledger.csv`.
- If impressions are near zero after 7 days, change category/title/keywords. If people click but do not inquire, change proof or positioning. If 10 qualified conversations yield no paid work, review the objections before expanding into more gigs. These are review thresholds, not sales promises.

## Unit economics (USD)
Fiverr pays freelancers 80% of an order. A $400 order leaves $320 before production costs. If model usage were the original sample's $1.18, that leaves $318.82 BEFORE testing time, revisions, tools, tax and refunds. It is not $398.82 profit.

Upwork's fee is 0–15% per contract, shown when proposing/contracting. A $450 order leaves $382.50–450 before Connects, production, tax and other costs. Do not hardcode one fee for every job.

$600/day averaged across 30 days is $18,000/month. At $320 per $400 Fiverr order, that's at least 57 completed orders per month before other costs. This is a substantial sales and delivery workload, not passive income. We should prove the first 3–5 profitable deliveries before scaling.

A later recurring service can offer defined monitoring and a small allowance of fixes, priced after measuring workload. Monthly billing would require real ongoing value; it is not free margin. Don't sell unlimited support.

## Current gates
- Fiverr account @jgoodnight318 created; seller profile and first gig are saved. Phone and identity verification are complete. The W-9 was submitted September 15 and reached Done. Fiverr confirmed receipt and says verification will take the coming days; publication remains locked pending that review.
- Upwork Catalog project 2099999933366679169 is approved and visible at $150/$450/$850, with one simultaneous project. Existing account ID review remains a separate check.
- IMAP/SMTP credential configuration and a real read/send check before enabling launchd.
- Live Shopify/Slack/Anthropic acceptance tests on approved test accounts. Fixture tests and import checks do not validate authentication, API access or live side effects.
- PR review and merge before the public GitHub Pages portfolio is live.

## Sources checked September 15, 2026
- Fiverr earnings: https://help.fiverr.com/hc/en-us/articles/9234443621137-Your-earnings-page
- Upwork fee: https://support.upwork.com/hc/en-us/articles/211062538-Learn-about-the-Freelancer-Service-Fee
- Fiverr setup/gallery requirements: https://help.fiverr.com/hc/en-us/articles/360010451397-Creating-a-Gig
- Shopify versioning: https://shopify.dev/docs/api/usage/versioning

## Monitoring
The existing “Find buyers with paid projects” monitor now checks both marketplaces at 08:00, 14:00 and 20:00 Pacific. It stays quiet when unchanged and notifies about meaningful new inquiries, funded orders or status changes. This browser-based monitor is active; the separate IMAP intake daemon is not configured.
