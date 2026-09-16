"""Website Contact Scraper. Fetches each site's homepage plus up to maxExtraPages same-domain
contact-like pages (contact/about/impressum/team/support/kontakt), and regex-extracts emails,
phone numbers and social profile links. Public HTML only, no JS rendering, no credentials."""
import asyncio, re
from urllib.parse import urljoin, urlparse
import httpx
from apify import Actor

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
TIMEOUT = 20
MAX_HTML_LEN = 2_000_000  # guard against pathologically large pages

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
MAILTO_RE = re.compile(r'mailto:([^"\'\s?<>]+)', re.I)
BAD_EMAIL_SUBSTR = ("example.com", "sentry", "wixpress", "noreply", "no-reply",
                     ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".css", ".js")

TEL_RE = re.compile(r'tel:([+\d][\d\s().\-]{5,})', re.I)
PHONE_RE = re.compile(r'(?<!\w)(\+?\(?\d{1,4}\)?[\d\s().\-]{5,17}\d)(?!\w)')
DATE_RE = re.compile(r'^\d{4}[-/]\d{1,2}[-/]\d{1,2}$|^\d{1,2}[-/]\d{1,2}[-/]\d{2,4}$')
YEAR_RANGE_RE = re.compile(r'^(19|20)\d{2}\s?[-–]\s?(19|20)\d{2}$')  # e.g. copyright "2001-2026"
DIGIT_GROUP_RE = re.compile(r'\D+')
# UUIDs in CDN asset filenames / order / session IDs are dash-grouped hex that can look
# phone-shaped when a slice happens to be all-digit (observed: Shopify image filenames like
# "...3af59f6d-8529-4166-a668-ad09ba1c3910.png" reading as phone "8529-4166"). Mask whole
# UUIDs out before phone matching so no slice of one can be mistaken for a number.
UUID_RE = re.compile(r'(?<![0-9a-f-])[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}(?![0-9a-f-])', re.I)

ANCHOR_RE = re.compile(r'<a\b[^>]*?href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', re.I | re.S)
TAG_RE = re.compile(r'<[^>]+>')
# <script>/<style>/<svg> bodies are the dominant source of phone/email false positives
# (inline SVG icon "d" path data reads as digit/dot/dash runs that match a phone regex,
# and inline JS/CSS carries stray "@" strings). Strip them before any extraction.
NOISE_BLOCK_RE = re.compile(r'<(script|style|svg)\b[^>]*>.*?</\1>', re.I | re.S)
CONTACT_KEYWORDS = re.compile(r'contact|about|impressum|team|support|kontakt', re.I)

SOCIAL_KEYS = ["facebook", "instagram", "linkedin", "twitter", "youtube", "tiktok"]
SOCIAL_PATTERNS = {
    "facebook": re.compile(r'(?:https?:)?//(?:www\.)?facebook\.com/[^"\'\s<>]+', re.I),
    "instagram": re.compile(r'(?:https?:)?//(?:www\.)?instagram\.com/[^"\'\s<>]+', re.I),
    "linkedin": re.compile(r'(?:https?:)?//(?:www\.)?linkedin\.com/[^"\'\s<>]+', re.I),
    "twitter": re.compile(r'(?:https?:)?//(?:www\.)?(?:twitter|x)\.com/[^"\'\s<>]+', re.I),
    "youtube": re.compile(r'(?:https?:)?//(?:www\.)?youtube\.com/[^"\'\s<>]+', re.I),
    "tiktok": re.compile(r'(?:https?:)?//(?:www\.)?tiktok\.com/[^"\'\s<>]+', re.I),
}
# share/intent/embed links aren't the network's own profile page for this site
SOCIAL_JUNK = ("sharer", "share.php", "/share", "share?", "intent/", "dialog/", "plugins/",
               "widget/", "sharearticle", "pin/create", "embed/", "watch?v=", "playlist?list=")


def normalize_origin(raw: str) -> str:
    raw = raw.strip()
    if not re.match(r'^https?://', raw, re.I):
        raw = "https://" + raw
    p = urlparse(raw)
    return f"{p.scheme}://{p.netloc}"


def same_domain(url_a: str, url_b: str) -> bool:
    def bare(u):
        host = urlparse(u).netloc.lower()
        return host[4:] if host.startswith("www.") else host
    return bare(url_a) == bare(url_b)


def discover_candidates(base_url: str, html: str, limit: int) -> list[str]:
    if limit <= 0:
        return []
    seen, out = set(), []
    for href, inner in ANCHOR_RE.findall(html):
        href = href.strip()
        if href.startswith(("mailto:", "tel:", "javascript:", "#")):
            continue
        text = TAG_RE.sub(" ", inner)
        if not (CONTACT_KEYWORDS.search(href) or CONTACT_KEYWORDS.search(text)):
            continue
        abs_url = urljoin(base_url, href).split("#")[0]
        if not same_domain(abs_url, base_url) or abs_url == base_url or abs_url in seen:
            continue
        seen.add(abs_url)
        out.append(abs_url)
        if len(out) >= limit:
            break
    return out


def strip_noise(html: str) -> str:
    return NOISE_BLOCK_RE.sub(" ", html)


def extract_emails(html_all: str) -> list[str]:
    found = set(EMAIL_RE.findall(html_all))
    for m in MAILTO_RE.findall(html_all):
        addr = m.split('?')[0].split('#')[0].strip()
        match = EMAIL_RE.search(addr)
        if match:
            found.add(match.group(0))
    clean = set()
    for e in found:
        el = e.lower()
        if len(el) > 64:
            continue
        if any(b in el for b in BAD_EMAIL_SUBSTR):
            continue
        clean.add(el)
    return sorted(clean)


def _phone_shape_ok(p: str) -> bool:
    """Free-text matches must look like grouped phone digits (2-5 groups of 2-4 digits,
    country-code group after a leading '+' allowed to be 1-3 digits) — otherwise plain digit
    runs from IDs, SKUs, hashes and number sequences (observed: Shopify variant IDs, Fibonacci
    sequences, build hashes) get misread as phone numbers."""
    groups = [g for g in DIGIT_GROUP_RE.split(p) if g]
    if not (2 <= len(groups) <= 5):
        return False
    has_plus = p.strip().startswith('+')
    for i, g in enumerate(groups):
        lo = 1 if (has_plus and i == 0) else 2
        if not (lo <= len(g) <= 4):
            return False
    return True


def extract_phones(html_all: str) -> list[str]:
    tel_hrefs = set(m.strip() for m in TEL_RE.findall(html_all))  # explicit tel: is a strong signal
    free_text = set(m.strip() for m in PHONE_RE.findall(UUID_RE.sub(" ", html_all)))
    phones, seen = [], set()
    for p, trusted in [(p, True) for p in tel_hrefs] + [(p, False) for p in free_text]:
        if not trusted:
            if DATE_RE.match(p.replace(" ", "")) or YEAR_RANGE_RE.match(p) or not _phone_shape_ok(p):
                continue
        digits = re.sub(r"\D", "", p)
        if len(digits) < 7 or len(digits) > 15 or digits in seen:
            continue
        seen.add(digits)
        phones.append(re.sub(r"\s+", " ", p).strip())
    return phones


def clean_social_url(url: str) -> str:
    url = url.strip().rstrip('.,;:)')
    if url.startswith("//"):
        url = "https:" + url
    elif url.startswith("http://"):
        url = "https://" + url[len("http://"):]
    return url.rstrip("/")


def extract_socials(html_all: str) -> dict:
    out = {k: None for k in SOCIAL_KEYS}
    for key, pattern in SOCIAL_PATTERNS.items():
        for m in pattern.findall(html_all):
            url = clean_social_url(m)
            low = url.lower()
            if any(j in low for j in SOCIAL_JUNK):
                continue
            if not urlparse(url).path.strip("/"):
                continue  # bare homepage, not a specific profile
            out[key] = url
            break
    return out


async def fetch_page(client, url):
    r = await client.get(url, timeout=TIMEOUT, headers={"User-Agent": UA}, follow_redirects=True)
    r.raise_for_status()
    return r


async def process_site(client, sem, raw_site, max_extra):
    async with sem:
        website = normalize_origin(raw_site)
        record = {"website": website, "finalUrl": None, "emails": [], "phones": [],
                  "socials": {k: None for k in SOCIAL_KEYS}, "pagesScanned": [],
                  "success": False, "error": None}
        try:
            resp = await fetch_page(client, website)
            final_url = str(resp.url)
            page_html = strip_noise(resp.text[:MAX_HTML_LEN])
            html_all = page_html
            record["finalUrl"] = final_url
            record["pagesScanned"].append(final_url)
            for curl in discover_candidates(final_url, page_html, max_extra):
                try:
                    r2 = await fetch_page(client, curl)
                    html_all += "\n" + strip_noise(r2.text[:MAX_HTML_LEN])
                    record["pagesScanned"].append(str(r2.url))
                except Exception as e:
                    Actor.log.debug(f"{website}: extra page {curl} failed: {e}")
            record["emails"] = extract_emails(html_all)
            record["phones"] = extract_phones(html_all)
            record["socials"] = extract_socials(html_all)
            record["success"] = True
        except Exception as e:
            record["error"] = str(e)
        return record


async def main():
    async with Actor:
        inp = await Actor.get_input() or {}
        websites = inp.get("websites") or []
        max_extra = max(0, min(10, int(inp.get("maxExtraPages", 3))))
        sem = asyncio.Semaphore(5)
        async with httpx.AsyncClient() as client:
            records = await asyncio.gather(*(process_site(client, sem, s, max_extra) for s in websites))
        charged = 0
        for record in records:
            await Actor.push_data(record)
            if record["success"]:
                await Actor.charge(event_name="site", count=1)
                charged += 1
            Actor.log.info(f"{record['website']}: success={record['success']} "
                            f"emails={len(record['emails'])} phones={len(record['phones'])} "
                            f"error={record['error']}")
        await Actor.set_value("SUMMARY", {"websites": len(websites), "chargedSuccess": charged})
