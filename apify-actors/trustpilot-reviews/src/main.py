"""Trustpilot Reviews Scraper. Parses the server-rendered `__NEXT_DATA__` JSON blob on
https://www.trustpilot.com/review/{domain} pages (Next.js), fetched with a real headless
Chromium browser via Playwright. Trustpilot fronts every page with an AWS WAF JS
challenge that plain HTTP clients cannot solve; a real browser rides through it
automatically, so this uses one instead of a bare HTTP client. No credentials, no
proxies. Failures (challenge never clears, unrecognized page) are handled by warning
and stopping that company rather than crashing the run."""
import asyncio, json, re
from playwright.async_api import async_playwright, Error as PlaywrightError, TimeoutError as PlaywrightTimeoutError
from apify import Actor

BASE = "https://www.trustpilot.com/review/{domain}"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")
PAGE_SLEEP_SECS = 1
NEXT_DATA_TIMEOUT_MS = 15000  # generous enough to ride through the WAF challenge auto-solve
REVIEW_URL_RE = re.compile(r'^(?:https?://)?(?:www\.)?trustpilot\.com/review/([^/?#]+)', re.IGNORECASE)


def normalize_domain(raw):
    """Accept a bare domain ("monzo.com") or a full trustpilot.com/review/... URL and
    return just the domain segment Trustpilot expects in the /review/{domain} path."""
    raw = (raw or "").strip()
    m = REVIEW_URL_RE.match(raw)
    if m:
        return m.group(1).rstrip("/")
    raw = re.sub(r'^https?://', '', raw, flags=re.IGNORECASE)
    raw = raw.split("/")[0].split("?")[0]
    return raw.strip().rstrip("/")


def company_record(domain, bu):
    if not bu:
        return None
    categories = [c.get("name") for c in (bu.get("categories") or []) if c.get("name")]
    return {
        "type": "company",
        "domain": domain,
        "name": bu.get("displayName"),
        "trustScore": bu.get("trustScore"),
        "totalReviews": bu.get("numberOfReviews"),
        "stars": bu.get("stars"),
        "categories": categories,
        "website": bu.get("websiteUrl"),
        "trustpilotUrl": BASE.format(domain=domain),
    }


def review_record(domain, r):
    consumer = r.get("consumer") or {}
    dates = r.get("dates") or {}
    verification = ((r.get("labels") or {}).get("verification")) or {}
    reply = r.get("reply") or {}
    rating = r.get("rating")
    try:
        rating = int(rating)
    except (TypeError, ValueError):
        rating = None
    return {
        "type": "review",
        "domain": domain,
        "reviewId": r.get("id"),
        "rating": rating,
        "title": r.get("title"),
        "text": r.get("text"),
        "authorName": consumer.get("displayName"),
        "authorCountry": consumer.get("countryCode"),
        "date": dates.get("publishedDate") or dates.get("submittedDate") or dates.get("experiencedDate"),
        "verified": bool(verification.get("isVerified")),
        "replyText": reply.get("message"),
        "replyDate": reply.get("publishedDate"),
    }


async def fetch_next_data(page, domain, page_num):
    """Navigate the shared browser page to one Trustpilot review page and return the
    parsed __NEXT_DATA__ JSON, or None if it never appeared (blocked, timed out, or
    an unrecognized layout)."""
    url = f"{BASE.format(domain=domain)}?page={page_num}&sort=recency"
    try:
        await page.goto(url, wait_until="domcontentloaded")
        # state="attached": a <script> tag is never "visible" (Playwright's default wait
        # state), only ever present/absent in the DOM - waiting for "visible" here would
        # time out even on a fully loaded page.
        await page.wait_for_selector("#__NEXT_DATA__", timeout=NEXT_DATA_TIMEOUT_MS, state="attached")
        raw = await page.evaluate("document.getElementById('__NEXT_DATA__').textContent")
    except PlaywrightTimeoutError:
        Actor.log.warning(f"{domain}: __NEXT_DATA__ never appeared on page {page_num} "
                           f"(timed out after {NEXT_DATA_TIMEOUT_MS // 1000}s, likely blocked) - stopping this company")
        return None
    except PlaywrightError as e:
        Actor.log.warning(f"{domain}: navigation failed on page {page_num}: {e} - stopping this company")
        return None
    try:
        return json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        Actor.log.warning(f"{domain}: __NEXT_DATA__ on page {page_num} was not valid JSON - stopping this company")
        return None


async def scrape_company(page, domain, max_reviews, include_info):
    reviews = []
    company = None
    page_num = 1
    while len(reviews) < max_reviews:
        data = await fetch_next_data(page, domain, page_num)
        if data is None:
            break
        page_props = ((data or {}).get("props") or {}).get("pageProps") or {}
        page_reviews = page_props.get("reviews")
        if page_reviews is None:
            Actor.log.warning(f"{domain}: no review data on page {page_num} (redirected or unrecognized page) - stopping this company")
            break
        if company is None and include_info:
            company = company_record(domain, page_props.get("businessUnit"))
        if not page_reviews:
            break
        for r in page_reviews:
            reviews.append(review_record(domain, r))
        if len(reviews) >= max_reviews:
            break
        total_pages = ((page_props.get("filters") or {}).get("pagination") or {}).get("totalPages")
        if total_pages and page_num >= total_pages:
            break
        page_num += 1
        await asyncio.sleep(PAGE_SLEEP_SECS)
    return company, reviews[:max_reviews]


async def main():
    async with Actor:
        inp = await Actor.get_input() or {}
        companies = [normalize_domain(c) for c in (inp.get("companies") or [])]
        companies = [c for c in companies if c]
        max_reviews = int(inp.get("maxReviewsPerCompany", 100))
        include_info = bool(inp.get("includeCompanyInfo", True))
        total_reviews = 0
        total_companies = 0
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            context = await browser.new_context(user_agent=UA, viewport={"width": 1280, "height": 900}, locale="en-US")
            page = await context.new_page()
            try:
                for domain in companies:
                    company, reviews = await scrape_company(page, domain, max_reviews, include_info)
                    items = ([company] if company else []) + reviews
                    if items:
                        await Actor.push_data(items)
                    if reviews:
                        await Actor.charge(event_name="review", count=len(reviews))
                        total_reviews += len(reviews)
                    if company:
                        total_companies += 1
                    Actor.log.info(f"{domain}: {len(reviews)} reviews" + (", company info" if company else ""))
            finally:
                await browser.close()
        await Actor.set_value("SUMMARY", {"companies": len(companies), "reviews": total_reviews, "companyRecords": total_companies})
