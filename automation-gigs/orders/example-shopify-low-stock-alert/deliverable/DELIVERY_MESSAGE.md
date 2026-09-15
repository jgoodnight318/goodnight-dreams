Hi! Your Shopify low-stock Slack workflow is ready.

Every morning it checks your catalog for any variant below 10 units, groups
the results by supplier (using the `custom.supplier` metafield), and posts
a Slack message with the list plus a short, ready-to-copy reorder email per
supplier — drafted by Claude, never sent automatically. If nothing's low,
it just posts "all good" so you know it ran.

**Attached:**
- `shopify-low-stock-slack-report.workflow.json` — import this into n8n
- `README.md` — full setup and node-by-node walkthrough
- `TESTING.md` — test cases to try before you rely on it

**3-step setup:**
1. Import the workflow file into n8n.
2. Create three credentials: Shopify Admin API (Header Auth), Anthropic API
   Key (Header Auth), and your Slack account — exact steps in the README.
3. Replace the placeholders (`YOUR_SHOP_NAME`, `YOUR_SLACK_CHANNEL`) and run
   it once by hand to confirm your first report looks right.

One heads up: since the report only needs to draft emails inside Slack, not
send them, I left Gmail out of the build — happy to add real Gmail drafts
as a quick follow-up if you'd rather have that instead.

Let me know how the first run looks — glad to do one round of tweaks
(wording, timing, formatting) to get it exactly right.
