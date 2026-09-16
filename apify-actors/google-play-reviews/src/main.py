"""Google Play Reviews Scraper. Uses the `google_play_scraper` PyPI package (unofficial, scrapes
Google Play's public web pages/GraphQL endpoints). No credentials. The library is synchronous, so
calls run in a worker thread via asyncio.to_thread to keep the Actor loop non-blocking."""
import json
from datetime import datetime
from urllib.parse import parse_qs, quote, urlparse

from asyncio import to_thread

from apify import Actor
from google_play_scraper import Sort
from google_play_scraper import app as gp_app
from google_play_scraper import reviews as gp_reviews
from google_play_scraper import search as gp_search
# Internal helpers reused only for the confirmed-broken-field workaround below (same helpers the
# library's own search() uses internally to fetch/parse the search page).
from google_play_scraper.constants.regex import Regex
from google_play_scraper.constants.request import Formats
from google_play_scraper.utils.request import get as gp_get

# All three Sort values google_play_scraper actually exposes (checked against v1.2.7).
SORT_MAP = {"newest": Sort.NEWEST, "rating": Sort.RATING, "relevance": Sort.MOST_RELEVANT}
BATCH_SIZE = 200


def to_iso(value):
    return value.isoformat() if isinstance(value, datetime) else value


def _iter_strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, list):
        for v in obj:
            yield from _iter_strings(v)


def _recover_top_hit_app_id(ident, cc, lang):
    """Work around a confirmed bug in google_play_scraper==1.2.7: search()'s top "hero" result
    (the #1 hit for any confident title match) always comes back with appId=None, because
    ElementSpecs.SearchResultOnTop["appId"] reads index [11, 0, 0] of the raw payload, but Google
    Play's current search page only carries indices [0..3] there -- that index no longer exists.
    Reproduced live for "Notion", "Spotify", "Slack" and "WhatsApp": search()[0]["appId"] is None
    for all four even though [0] is unambiguously the right app (title/developer match exactly).
    Falling back to search()[1] instead silently returns a DIFFERENT app (e.g. "Notion" ->
    "Notion Calendar", same developer, so a developer-match heuristic fails too).
    The real package ID is still present in the same payload, embedded in a
    play.google.com/store/apps/details?id=<pkg> share URL. Recover it from there using the same
    request/regex helpers search() itself uses, instead of guessing or returning the wrong app."""
    try:
        url = Formats.Searchresults.build(query=quote(ident), lang=lang, country=cc)
        dom = gp_get(url)
        dataset = {}
        for match in Regex.SCRIPT.findall(dom):
            key_match, value_match = Regex.KEY.findall(match), Regex.VALUE.findall(match)
            if key_match and value_match:
                dataset[key_match[0]] = json.loads(value_match[0])
        top_result = dataset["ds:4"][0][1][0][23][16]
        if not top_result:
            return None
        for s in _iter_strings(top_result):
            if "details?id=" in s:
                ids = parse_qs(urlparse(s).query).get("id")
                if ids:
                    return ids[0]
    except Exception as e:
        Actor.log.info(f"top-hit appId recovery failed for {ident!r}: {e}")
    return None


def resolve_app_id(ident, cc, lang):
    if "." in ident:
        return ident  # package IDs are used directly
    try:
        results = gp_search(ident, n_hits=5, lang=lang, country=cc)
    except Exception as e:
        # google_play_scraper's search() has an unhandled TypeError for some locale/query
        # combinations (reproduced for country="de": the raw payload's hero-result slot is None,
        # and the library only catches IndexError, not TypeError, around that lookup). Treat it
        # as "no result" rather than letting one bad search take down the whole run.
        Actor.log.info(f"search failed for {ident!r} ({cc}): {e}")
        return None
    if not results:
        return None
    if results[0].get("appId"):
        return results[0]["appId"]
    recovered = _recover_top_hit_app_id(ident, cc, lang)
    if recovered:
        return recovered
    for r in results[1:]:  # last resort: next best hit that actually resolved
        if r.get("appId"):
            return r["appId"]
    return None


def app_record(a, app_id, cc):
    return {"type": "app", "appId": app_id, "country": cc, "name": a.get("title"),
             "developer": a.get("developer"), "score": a.get("score"), "ratings": a.get("ratings"),
             "installs": a.get("installs"), "price": a.get("price"), "currency": a.get("currency"),
             "currentVersion": a.get("version"), "genre": a.get("genre"), "url": a.get("url")}


def review_record(r, app_id, cc):
    return {"type": "review", "appId": app_id, "country": cc, "reviewId": r.get("reviewId"),
             "rating": r.get("score"), "title": None, "content": r.get("content"),
             "author": r.get("userName"), "thumbsUp": r.get("thumbsUpCount"),
             "reviewCreatedVersion": r.get("reviewCreatedVersion"), "at": to_iso(r.get("at")),
             "replyContent": r.get("replyContent"), "repliedAt": to_iso(r.get("repliedAt"))}


def fetch_reviews(app_id, cc, lang, sort, max_reviews):
    out, token = [], None
    while len(out) < max_reviews:
        batch, token = gp_reviews(app_id, lang=lang, country=cc, sort=sort,
                                    count=min(BATCH_SIZE, max_reviews - len(out)), continuation_token=token)
        if not batch:
            break
        out.extend(batch)
        if token is None or token.token is None:
            break
    return out[:max_reviews]


async def scrape_app(ident, cc, lang, sort, max_reviews, include_info):
    app_id = await to_thread(resolve_app_id, ident, cc, lang)
    if not app_id:
        Actor.log.warning(f"not found: {ident} ({cc})")
        return [], 0
    items = []
    if include_info:
        try:
            info = await to_thread(gp_app, app_id, lang, cc)
            items.append(app_record(info, app_id, cc))
        except Exception as e:
            Actor.log.info(f"{app_id}/{cc} info: {e}")
    try:
        revs = await to_thread(fetch_reviews, app_id, cc, lang, sort, max_reviews)
    except Exception as e:
        Actor.log.info(f"{app_id}/{cc} reviews: {e}")
        revs = []
    items.extend(review_record(r, app_id, cc) for r in revs)
    return items, len(revs)


async def main():
    async with Actor:
        inp = await Actor.get_input() or {}
        apps = inp.get("apps") or []
        cc = inp.get("country", "us")
        lang = inp.get("language", "en")
        max_reviews = int(inp.get("maxReviewsPerApp", 100))
        sort = SORT_MAP.get(inp.get("sort", "newest"), Sort.NEWEST)
        include_info = bool(inp.get("includeAppInfo", True))
        total = 0
        for ident in apps:
            items, n = await scrape_app(ident, cc, lang, sort, max_reviews, include_info)
            if items:
                await Actor.push_data(items)
                await Actor.charge(event_name="review", count=n)
                total += n
                Actor.log.info(f"{ident} [{cc}]: {n} reviews")
        await Actor.set_value("SUMMARY", {"apps": len(apps), "country": cc, "reviews": total})
