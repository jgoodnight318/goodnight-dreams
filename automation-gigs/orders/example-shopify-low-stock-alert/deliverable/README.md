# Shopify Low-Stock Slack Report

Every morning this workflow checks your Shopify catalog for any variant with
fewer than 10 units in stock, groups the results by supplier (using the
`custom.supplier` product metafield), and posts a Slack message with:

- A list of low-stock variants per supplier
- A short, ready-to-copy reorder email drafted by Claude for each supplier
- If nothing is low, it just posts "all good" so you know the check ran

No emails are ever sent automatically — the drafts are for you to copy,
review, and send yourself from Gmail (or wherever you like).

## Decision made for you

The brief mentioned Gmail, but since the workflow only needs to *draft* the
reorder text inside the Slack message (not send anything), Gmail isn't wired
in as an integration — that keeps the build simpler and avoids asking for
Gmail access it doesn't need. If you'd like it to also create real Gmail
drafts instead of just showing the text in Slack, that's a small add-on.

## Node-by-node walkthrough

1. **Every morning at 8am** (Schedule Trigger) — runs daily at 08:00 in your
   n8n instance's timezone. Change `triggerAtHour` in the node if you want a
   different time.
2. **Get products from Shopify** (HTTP Request) — calls the Shopify Admin
   GraphQL API for up to 250 products (100 variants each), pulling each
   variant's `inventoryQuantity` and the product's `custom.supplier`
   metafield in one request.
3. **Alert: inventory check failed** (Slack) — only fires if step 2 fails
   (bad credentials, wrong store URL, API downtime). Posts an error message
   to Slack instead of the workflow failing silently.
4. **Flatten and filter low stock (<10)** (Code) — turns the nested Shopify
   response into a flat list of variants and keeps only the ones with
   quantity below 10.
5. **Any low stock items?** (IF) — branches depending on whether anything
   is low.
6. **Post all-good message** (Slack) — sent when nothing is low.
7. **Group low-stock items by supplier** (Code) — groups the low-stock
   variants into one item per supplier, with a formatted list of items for
   each.
8. **Draft reorder email with Claude** (HTTP Request) — calls the Claude
   API (`claude-sonnet-5`) once per supplier to draft a short reorder email
   listing that supplier's low items. If this call fails for a supplier,
   the workflow doesn't stop — it flows through to step 9 with the error
   attached so a fallback note can be used instead.
9. **Extract Claude draft (with fallback)** (Code) — pulls the drafted
   email text out of Claude's response, or inserts a fallback note if the
   API call failed, so a low-stock supplier is never silently dropped from
   the report.
10. **Combine supplier reports** (Aggregate) — merges all the per-supplier
    results back into a single list.
11. **Build Slack message** (Code) — formats the final Slack message: one
    section per supplier with its low-stock items and drafted email.
12. **Post low-stock report** (Slack) — posts the final message.

## Setup steps

1. **Import the workflow**
   - In n8n: Workflows → Add workflow → ⋯ menu → Import from File → select
     `shopify-low-stock-slack-report.workflow.json`.

2. **Create the Shopify credential**
   - In your Shopify admin, create a custom app with `read_products` access
     and generate an Admin API access token.
   - In n8n, create a credential of type **Header Auth** named
     `Shopify Admin API` with:
     - Name: `X-Shopify-Access-Token`
     - Value: your access token
   - Open the **Get products from Shopify** node, select that credential,
     and replace `YOUR_SHOP_NAME` in the URL with your store's
     `.myshopify.com` name.
   - Check that the API version in the URL (`2024-01`) is still a
     currently-supported Shopify API version when you set this up, and
     update it if not.

3. **Create the Anthropic credential**
   - In n8n, create a credential of type **Header Auth** named
     `Anthropic API Key` with:
     - Name: `x-api-key`
     - Value: your Anthropic API key
   - Select it on the **Draft reorder email with Claude** node.

4. **Create the Slack credential**
   - In n8n, create a **Slack** credential (OAuth2 or bot token) with
     permission to post messages to your channel.
   - In all three Slack nodes (**Alert: inventory check failed**,
     **Post all-good message**, **Post low-stock report**), select that
     credential and replace `YOUR_SLACK_CHANNEL` with your channel name or
     ID.

5. **Set the `custom.supplier` metafield**
   - This workflow assumes products already have a `custom.supplier`
     metafield set in Shopify. Products without it will show up grouped
     under "Unknown supplier" in the report, not get dropped.

6. **Adjust the schedule**
   - The **Every morning at 8am** node runs daily at 08:00 in n8n's server
     timezone. Edit `triggerAtHour` on that node for a different time.

## Run it once by hand

1. Open the workflow in n8n.
2. Click **Execute workflow** at the bottom of the canvas — this runs it
   once immediately, ignoring the schedule.
3. Check the execution log: each node should show green. Then check your
   Slack channel for the resulting message.
4. If the Shopify or Claude step fails, open that node's output in the
   execution log for the error detail before troubleshooting.

## A note on inventory data

Shopify's `inventoryQuantity` field on a variant returns an aggregated
available quantity. If you stock the same SKU across multiple locations and
want a location-specific low-stock check instead, the GraphQL query in the
**Get products from Shopify** node will need to be extended to query
`inventoryItem.inventoryLevels` per location — let us know if that's your
setup and we can adjust the query.
