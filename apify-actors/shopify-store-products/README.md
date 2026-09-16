# Shopify Store Products Scraper

Export the full product catalog of any Shopify store as clean JSON, straight from the store's
public catalog endpoint. No login, no API key, no proxies. Give it one or more store domains and
get every product with variants, SKUs, prices, compare-at prices, availability, images, tags,
vendor and product type. Point it at a single collection with `collectionHandle`, or flatten to
one row per variant for spreadsheets and price monitoring.

Works for competitor price tracking, dropshipping research, catalog migration, stock monitoring,
and feeding product data to AI agents.

## What you get
One record per product (or per variant with `flattenVariants`): `store`, `productId`, `title`,
`handle`, `url`, `vendor`, `productType`, `tags`, `priceMin`, `priceMax`, `available`, `images`,
`options`, `createdAt`, `updatedAt`, `publishedAt`, and `variants` (id, title, SKU, price,
compare-at price, availability, weight).

## Limits
Reads the store's public catalog (250 products per page), which contains every product visible in
the online store. Stores that have disabled their public catalog feed (rare) return an error and
are skipped with a warning.

## Pricing
Pay per event: **$1 per 1,000 product records** ($0.001 each). With `flattenVariants` each variant
row counts as one record. A 3,000-product store costs about $3.

## Example input
```json
{ "stores": ["allbirds.com", "shop.gymshark.com"], "flattenVariants": false }
```
