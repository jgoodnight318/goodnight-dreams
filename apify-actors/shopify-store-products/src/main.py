"""Shopify Store Products Scraper. Reads any Shopify store's public /products.json endpoint
(250 per page). No credentials, no proxies. Fixture mode (FIXTURE_DIR env) serves saved
responses for offline tests."""
import json, os, re
from urllib.parse import urlparse

import httpx
from apify import Actor

FIXTURES = os.environ.get("FIXTURE_DIR")
UA = {"User-Agent": "Mozilla/5.0 (compatible; shopify-store-products-actor)"}


def normalize_store(raw):
    """Accept 'allbirds.com', 'https://allbirds.com/pages/x', etc. -> https://allbirds.com"""
    raw = str(raw).strip()
    if not re.match(r"^https?://", raw):
        raw = "https://" + raw
    u = urlparse(raw)
    return f"{u.scheme}://{u.netloc}", u.netloc


async def fetch_json(client, url):
    if FIXTURES:
        key = re.sub(r"[^a-z0-9]+", "_", url.lower()).strip("_")[:120] + ".json"
        p = os.path.join(FIXTURES, key)
        if not os.path.exists(p):
            raise FileNotFoundError(f"no fixture for {url} -> {key}")
        return json.load(open(p))
    r = await client.get(url, timeout=30, headers=UA, follow_redirects=True)
    r.raise_for_status()
    return r.json()


def price_range(variants):
    prices = []
    for v in variants:
        try:
            prices.append(float(v.get("price")))
        except (TypeError, ValueError):
            pass
    return (min(prices), max(prices)) if prices else (None, None)


def variant_record(v):
    return {"variantId": v.get("id"), "variantTitle": v.get("title"), "sku": v.get("sku"),
            "price": v.get("price"), "compareAtPrice": v.get("compare_at_price"),
            "available": v.get("available"), "grams": v.get("grams"),
            "requiresShipping": v.get("requires_shipping")}


def product_records(p, base, host, flatten):
    lo, hi = price_range(p.get("variants") or [])
    core = {"store": host, "productId": p.get("id"), "title": p.get("title"),
            "handle": p.get("handle"), "url": f"{base}/products/{p.get('handle')}",
            "vendor": p.get("vendor"), "productType": p.get("product_type"),
            "tags": p.get("tags"), "priceMin": lo, "priceMax": hi,
            "available": any(v.get("available") for v in p.get("variants") or []),
            "images": [i.get("src") for i in p.get("images") or []],
            "options": [o.get("name") for o in p.get("options") or []],
            "createdAt": p.get("created_at"), "updatedAt": p.get("updated_at"),
            "publishedAt": p.get("published_at")}
    if flatten:
        return [{**core, **variant_record(v)} for v in p.get("variants") or []]
    return [{**core, "variants": [variant_record(v) for v in p.get("variants") or []]}]


async def scrape_store(client, base, host, handle, max_products, flatten):
    path = f"/collections/{handle}/products.json" if handle else "/products.json"
    items, got = [], 0
    for page in range(1, 201):
        if max_products and got >= max_products:
            break
        try:
            data = await fetch_json(client, f"{base}{path}?limit=250&page={page}")
        except httpx.HTTPStatusError as e:
            if page == 1:
                Actor.log.warning(f"{host}: {path} returned HTTP {e.response.status_code} "
                                  "(not a Shopify store, or the storefront blocks the endpoint)")
            break
        except Exception as e:
            Actor.log.warning(f"{host} page {page}: {e}")
            break
        products = data.get("products") or []
        if not products:
            break
        for p in products:
            if max_products and got >= max_products:
                break
            items.extend(product_records(p, base, host, flatten))
            got += 1
    return items, got


async def main():
    async with Actor:
        inp = await Actor.get_input() or {}
        stores = inp.get("stores") or []
        handle = (inp.get("collectionHandle") or "").strip() or None
        flatten = bool(inp.get("flattenVariants", False))
        max_products = int(inp.get("maxProductsPerStore", 0))
        total = 0
        async with httpx.AsyncClient() as client:
            for raw in stores:
                base, host = normalize_store(raw)
                items, n = await scrape_store(client, base, host, handle, max_products, flatten)
                if items:
                    await Actor.push_data(items)
                    await Actor.charge(event_name="product", count=len(items))
                    total += n
                Actor.log.info(f"{host}: {n} products ({len(items)} records)")
        await Actor.set_value("SUMMARY", {"stores": len(stores), "products": total})
