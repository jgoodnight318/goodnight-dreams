"""App Store Reviews Scraper. Uses Apple's public iTunes Search API and the public customer-reviews
RSS feed. No credentials. Fixture mode (FIXTURE_DIR env) serves saved responses for offline tests."""
import asyncio, json, os, re
import httpx
from apify import Actor

SEARCH = "https://itunes.apple.com/search?term={term}&country={cc}&entity={entity}&limit=1"
LOOKUP = "https://itunes.apple.com/lookup?id={id}&country={cc}"
REVIEWS = "https://itunes.apple.com/{cc}/rss/customerreviews/page={page}/id={id}/sortby=mostrecent/json"
FIXTURES = os.environ.get("FIXTURE_DIR")

async def fetch_json(client, url):
    if FIXTURES:
        key = re.sub(r"[^a-z0-9]+", "_", url.lower()).strip("_")[:120] + ".json"
        p = os.path.join(FIXTURES, key)
        if not os.path.exists(p):
            raise FileNotFoundError(f"no fixture for {url} -> {key}")
        return json.load(open(p))
    r = await client.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0 (compatible; app-store-reviews-actor)"})
    r.raise_for_status()
    return r.json()

async def resolve_app(client, ident, cc, entity):
    if re.fullmatch(r"\d{6,}", str(ident)):
        data = await fetch_json(client, LOOKUP.format(id=ident, cc=cc))
    else:
        data = await fetch_json(client, SEARCH.format(term=httpx.QueryParams({"t": ident})["t"].replace(" ", "+"), cc=cc, entity=entity))
    res = data.get("results") or []
    return res[0] if res else None

def app_record(a, cc):
    return {"type": "app", "appId": str(a.get("trackId")), "country": cc, "name": a.get("trackName"),
            "developer": a.get("sellerName") or a.get("artistName"), "price": a.get("price"), "currency": a.get("currency"),
            "averageRating": a.get("averageUserRating"), "ratingCount": a.get("userRatingCount"),
            "currentVersion": a.get("version"), "releaseNotes": a.get("releaseNotes"), "genres": a.get("genres"),
            "url": a.get("trackViewUrl"), "minimumOs": a.get("minimumOsVersion"), "contentRating": a.get("contentAdvisoryRating")}

def parse_reviews(feed, app_id, cc):
    entries = (feed.get("feed") or {}).get("entry") or []
    if isinstance(entries, dict):
        entries = [entries]
    out = []
    for e in entries:
        if "im:rating" not in e:
            continue  # first entry on page 1 is the app itself
        out.append({"type": "review", "appId": app_id, "country": cc,
                    "reviewId": (e.get("id") or {}).get("label"),
                    "rating": int((e.get("im:rating") or {}).get("label") or 0),
                    "title": (e.get("title") or {}).get("label"),
                    "content": (e.get("content") or {}).get("label"),
                    "author": ((e.get("author") or {}).get("name") or {}).get("label"),
                    "version": (e.get("im:version") or {}).get("label"),
                    "updated": (e.get("updated") or {}).get("label"),
                    "voteSum": (e.get("im:voteSum") or {}).get("label"),
                    "voteCount": (e.get("im:voteCount") or {}).get("label")})
    return out

async def scrape_app(client, ident, cc, entity, max_reviews, include_info):
    app = await resolve_app(client, ident, cc, entity)
    if not app:
        Actor.log.warning(f"not found: {ident} ({cc})"); return [], 0
    app_id = str(app["trackId"]); items = []
    if include_info:
        items.append(app_record(app, cc))
    got = 0
    for page in range(1, 11):
        if got >= max_reviews:
            break
        try:
            feed = await fetch_json(client, REVIEWS.format(cc=cc, page=page, id=app_id))
        except Exception as e:
            Actor.log.info(f"{app_id}/{cc} page {page}: {e}"); break
        revs = parse_reviews(feed, app_id, cc)
        if not revs:
            break
        revs = revs[: max_reviews - got]; items.extend(revs); got += len(revs)
    return items, got

async def main():
    async with Actor:
        inp = await Actor.get_input() or {}
        apps = inp.get("apps") or []; countries = inp.get("countries") or ["us"]
        entity = inp.get("platform", "software"); max_reviews = int(inp.get("maxReviewsPerApp", 100))
        include_info = bool(inp.get("includeAppInfo", True))
        total = 0
        async with httpx.AsyncClient() as client:
            for ident in apps:
                for cc in countries:
                    items, n = await scrape_app(client, ident, cc, entity, max_reviews, include_info)
                    if items:
                        await Actor.push_data(items)
                        await Actor.charge(event_name="review", count=max(n, 1))
                        total += n
                        Actor.log.info(f"{ident} [{cc}]: {n} reviews")
        await Actor.set_value("SUMMARY", {"apps": len(apps), "countries": countries, "reviews": total})
