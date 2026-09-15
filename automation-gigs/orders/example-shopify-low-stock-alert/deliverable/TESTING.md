# Testing the Shopify Low-Stock Slack Report

Run these by triggering the workflow manually ("Execute workflow" in n8n)
after adjusting test data as described, or by inspecting the
**Flatten and filter low stock (<10)** node's output during a real run.

## Test 1 — Nothing is low

**Setup:** Every variant in your store has 10+ units in stock (or point the
Shopify credential at a test store where that's true).

**Expected result:** The workflow follows the "false" branch of
**Any low stock items?**, and Slack receives:

> ✅ All good — no candle variants are below 10 units today.

No Claude API calls are made.

## Test 2 — One supplier has low stock

**Setup:** In Shopify, set one variant's inventory to 3 units, on a product
with `custom.supplier` = "Wick & Wax Co.".

**Expected result:** Slack receives a message with one supplier section,
similar to:

```
*Low stock report — 2026-09-15*

*Supplier: Wick & Wax Co.*
- Lavender Candle (12oz), SKU LAV-12: 3 left

_Suggested reorder email (copy-paste and edit as needed):_
```
[a short drafted email addressed to Wick & Wax Co. listing the item]
```
```

## Test 3 — Multiple suppliers have low stock

**Setup:** Set inventory below 10 on variants from two different suppliers,
e.g. "Wick & Wax Co." and "Glass Jar Supply".

**Expected result:** Slack receives one message with two clearly separated
supplier sections, each with its own item list and its own drafted email.
Order of suppliers isn't guaranteed — that's fine.

## Test 4 — Missing supplier metafield

**Setup:** Set a variant's inventory below 10 on a product that has no
`custom.supplier` metafield set.

**Expected result:** That item appears in the report under
"Unknown supplier" instead of being dropped or causing an error.

## Test 5 — Shopify credential is wrong

**Setup:** Temporarily break the Shopify credential (e.g. use an invalid
token) and run the workflow.

**Expected result:** Slack receives the error alert from
**Alert: inventory check failed**, describing the failure — the workflow
does not fail silently or throw an unhandled error.

## Test 6 — Claude API call fails for one supplier

**Setup:** Temporarily use an invalid Anthropic API key, with at least one
supplier having low stock.

**Expected result:** The Slack report still posts, listing the low-stock
items for that supplier, but the "Suggested reorder email" section shows:
"Could not generate a draft automatically. Please write a reorder email
manually using the items listed above." The low-stock data itself is never
dropped just because the AI drafting step failed.
