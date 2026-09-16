#!/usr/bin/env python3
"""Find a public contact email on each prospect's website (homepage + /contact pages).
Skips businesses that already advertise live answering. status: new -> enriched | no_email | skip

  enrich.py [--limit 40] [--fixture-html file.html]   (fixture = offline test)
"""
import argparse, re, urllib.parse
from common import *

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
BAD = ("noreply", "no-reply", "example.com", "sentry", "wixpress", ".png", ".jpg", "godaddy", "squarespace")
SKIP_PHRASES = ("24/7 live answering", "answering service", "24 hour live", "live answering")

def pick_email(html, site):
    dom = urllib.parse.urlparse(site if site.startswith("http") else "https://" + site).netloc.replace("www.", "")
    found = [e for e in set(EMAIL_RE.findall(html)) if not any(b in e.lower() for b in BAD)]
    same = [e for e in found if dom and e.lower().endswith(dom.lower())]
    pref = [e for e in (same or found) if e.split("@")[0].lower() in ("info", "office", "contact", "hello", "service", "sales")]
    return (pref or same or found or [""])[0]

def fetch_site(site, fixture=None):
    if fixture:
        return open(fixture).read()
    if not site.startswith("http"):
        site = "https://" + site
    html = ""
    for path in ("", "/contact", "/contact-us", "/about"):
        try:
            html += http_get(site.rstrip("/") + path, timeout=12)
        except Exception:
            pass
    return html

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--limit", type=int, default=40); ap.add_argument("--fixture-html")
    a = ap.parse_args()
    rows = load(); n = 0
    for r in rows:
        if r["status"] != "new" or n >= a.limit:
            continue
        n += 1
        if r.get("email"):
            r["status"] = "enriched"; continue
        if not r.get("website"):
            r["status"] = "no_email"; continue
        html = fetch_site(r["website"], a.fixture_html)
        if any(p in html.lower() for p in SKIP_PHRASES):
            r["status"] = "skip"; r["notes"] = "already has live answering"; continue
        r["email"] = pick_email(html, r["website"])
        r["status"] = "enriched" if r["email"] else "no_email"
    save(rows)
    log(f"processed {n}: " + ", ".join(f"{s}={sum(1 for r in rows if r['status'] == s)}" for s in ("enriched", "no_email", "skip")))

if __name__ == "__main__":
    main()
