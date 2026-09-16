#!/usr/bin/env python3
"""Lead engine for Cascade Web Design: finds local trade businesses with NO website
AND a reachable public email, so they can be emailed a free preview site + offer.

This is a sibling of receptionist/prospect.py (same Overpass pattern, same
free/no-key philosophy) extended with two web-search-based methods that catch
Facebook-only and BBB-listed businesses OSM never tagged.

    Method A — overpass   : OpenStreetMap Overpass API. Businesses tagged with
                             email/contact:email but NOT website/contact:website.
                             Fully automated (this script does it end to end).
    Method B — facebook   : `site:facebook.com "<trade>" "<city>" "@gmail.com"`
                             (and variants). Requires a web-search tool (WebSearch)
                             this script cannot call itself — see ingest-search.
    Method C — bbb        : `site:bbb.org "<trade>" "<city>" "Email Address"`,
                             profile fetched and checked for an email + no website
                             link. Also requires WebSearch/WebFetch — see ingest-search.

Usage:
    # Method A, fully automated:
    python3 lead_engine.py overpass --out raw/overpass_raw.json \
        [--cities cities.json] [--radius 15000] [--sleep 3]

    # Methods B/C: an agent runs the WebSearch/WebFetch queries printed by
    # `queries`, saves each hit as {"query":..., "url":..., "title":..., "snippet":...}
    # into a JSON list, then this script extracts business/email candidates:
    python3 lead_engine.py queries --method facebook   # prints the search strings to run
    python3 lead_engine.py queries --method bbb
    python3 lead_engine.py ingest-search --method facebook --in raw/facebook_hits.json --out raw/facebook_raw.json
    python3 lead_engine.py ingest-search --method bbb      --in raw/bbb_hits.json      --out raw/bbb_raw.json

    # Merge all three raw method outputs, dedupe on phone/email, drop rows
    # missing required fields:
    python3 lead_engine.py merge --inputs raw/overpass_raw.json raw/facebook_raw.json raw/bbb_raw.json \
        --out merged_candidates.json

    # Verified leads (name/email/no_website_evidence/... filled in by a human or
    # an agent doing the live-search verification step) are then written directly
    # as the final leads_email_*.json — see websites/tools/leads_to_csv.py to emit
    # the CSV twin.

Standard library only. No API keys.
"""
import argparse, csv, hashlib, json, os, re, sys, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))

OVERPASS_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]

UA = "cascade-lead-engine/1.0 (contact: jms.goodnight@gmail.com)"

# OSM tag selector per trade. Some trades have two conventions in the wild
# (shop=* and craft=*); listing both widens the net.
TRADE_SELECTORS = {
    "plumber": ['["craft"="plumber"]'],
    "electrician": ['["craft"="electrician"]'],
    "hvac": ['["craft"="hvac"]'],
    "roofer": ['["craft"="roofer"]'],
    "landscaper": ['["craft"="gardener"]'],
    "car_repair": ['["shop"="car_repair"]'],
    "painter": ['["craft"="painter"]'],
    "locksmith": ['["shop"="locksmith"]', '["craft"="locksmith"]'],
    "cleaning": ['["craft"="cleaner"]'],
    "handyman": ['["craft"="handyman"]'],
}

# 35 US/Canada metros, Pacific Northwest weighted first (12), then the rest
# of the country (23). One Overpass query per city covers every trade.
DEFAULT_CITIES = [
    # -- Pacific Northwest (weighted) --
    {"city": "Seattle", "state": "WA", "lat": 47.6062, "lon": -122.3321},
    {"city": "Tacoma", "state": "WA", "lat": 47.2529, "lon": -122.4443},
    {"city": "Spokane", "state": "WA", "lat": 47.6588, "lon": -117.4260},
    {"city": "Bellevue", "state": "WA", "lat": 47.6101, "lon": -122.2015},
    {"city": "Everett", "state": "WA", "lat": 47.9790, "lon": -122.2021},
    {"city": "Olympia", "state": "WA", "lat": 47.0379, "lon": -122.9007},
    {"city": "Vancouver", "state": "WA", "lat": 45.6387, "lon": -122.6615},
    {"city": "Portland", "state": "OR", "lat": 45.5152, "lon": -122.6784},
    {"city": "Eugene", "state": "OR", "lat": 44.0521, "lon": -123.0868},
    {"city": "Salem", "state": "OR", "lat": 44.9429, "lon": -123.0351},
    {"city": "Bend", "state": "OR", "lat": 44.0582, "lon": -121.3153},
    {"city": "Boise", "state": "ID", "lat": 43.6150, "lon": -116.2023},
    # -- Rest of the US --
    {"city": "San Francisco", "state": "CA", "lat": 37.7749, "lon": -122.4194},
    {"city": "Sacramento", "state": "CA", "lat": 38.5816, "lon": -121.4944},
    {"city": "Los Angeles", "state": "CA", "lat": 34.0522, "lon": -118.2437},
    {"city": "San Diego", "state": "CA", "lat": 32.7157, "lon": -117.1611},
    {"city": "Las Vegas", "state": "NV", "lat": 36.1699, "lon": -115.1398},
    {"city": "Phoenix", "state": "AZ", "lat": 33.4484, "lon": -112.0740},
    {"city": "Denver", "state": "CO", "lat": 39.7392, "lon": -104.9903},
    {"city": "Salt Lake City", "state": "UT", "lat": 40.7608, "lon": -111.8910},
    {"city": "Albuquerque", "state": "NM", "lat": 35.0844, "lon": -106.6504},
    {"city": "Dallas", "state": "TX", "lat": 32.7767, "lon": -96.7970},
    {"city": "Austin", "state": "TX", "lat": 30.2672, "lon": -97.7431},
    {"city": "Houston", "state": "TX", "lat": 29.7604, "lon": -95.3698},
    {"city": "San Antonio", "state": "TX", "lat": 29.4241, "lon": -98.4936},
    {"city": "Kansas City", "state": "MO", "lat": 39.0997, "lon": -94.5786},
    {"city": "Minneapolis", "state": "MN", "lat": 44.9778, "lon": -93.2650},
    {"city": "Chicago", "state": "IL", "lat": 41.8781, "lon": -87.6298},
    {"city": "Indianapolis", "state": "IN", "lat": 39.7684, "lon": -86.1581},
    {"city": "Columbus", "state": "OH", "lat": 39.9612, "lon": -82.9988},
    {"city": "Nashville", "state": "TN", "lat": 36.1627, "lon": -86.7816},
    {"city": "Atlanta", "state": "GA", "lat": 33.7490, "lon": -84.3880},
    {"city": "Charlotte", "state": "NC", "lat": 35.2271, "lon": -80.8431},
    {"city": "Tampa", "state": "FL", "lat": 27.9506, "lon": -82.4572},
    {"city": "Philadelphia", "state": "PA", "lat": 39.9526, "lon": -75.1652},
]

FACEBOOK_DOMAINS = ["@gmail.com", "@yahoo.com", "@outlook.com"]
FACEBOOK_TRADES = ["plumber", "electrician", "hvac", "roofer", "landscaper", "handyman"]
FACEBOOK_CITIES = [c["city"] for c in DEFAULT_CITIES[:15]]  # PNW + next largest
BBB_TRADES = FACEBOOK_TRADES
BBB_CITIES = FACEBOOK_CITIES

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
GENERIC_LOCAL = {"info", "contact", "admin", "support", "sales", "office", "webmaster", "noreply", "no-reply"}
AGGREGATOR_DOMAINS = {
    "yelp.com", "facebook.com", "bbb.org", "angi.com", "homeadvisor.com", "thumbtack.com",
    "yellowpages.com", "google.com", "nextdoor.com", "instagram.com",
}


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, file=sys.stderr, flush=True)


def build_overpass_query(lat, lon, radius):
    stmts = []
    for _trade, selectors in TRADE_SELECTORS.items():
        for sel in selectors:
            for etype in ("node", "way"):
                for emailtag in ("email", "contact:email"):
                    stmts.append(
                        f'{etype}{sel}["{emailtag}"][!"website"][!"contact:website"]'
                        f"(around:{radius},{lat},{lon});"
                    )
    return "[out:json][timeout:120];(" + "".join(stmts) + ");out center tags;"


def tag_to_trade(tags):
    for trade, selectors in TRADE_SELECTORS.items():
        for sel in selectors:
            # sel looks like ["craft"="plumber"] or ["shop"="car_repair"]
            m = re.match(r'\["(\w+(?::\w+)?)"="([^"]+)"\]', sel)
            if m and tags.get(m.group(1)) == m.group(2):
                return trade
    return "unknown"


def overpass_fetch(query, tries=5, timeout=110):
    last_err = None
    for i in range(tries):
        ep = OVERPASS_ENDPOINTS[i % len(OVERPASS_ENDPOINTS)]
        url = ep + "?" + urllib.parse.urlencode({"data": query})
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except Exception as e:  # noqa: BLE001 - overpass mirrors fail in many ways
            last_err = e
            log(f"  overpass attempt {i + 1}/{tries} via {ep} failed: {e}")
            time.sleep(5 * (i + 1))
    raise RuntimeError(f"overpass fetch failed after {tries} tries: {last_err}")


def norm_phone(p):
    d = re.sub(r"\D", "", p or "")
    if len(d) == 11 and d.startswith("1"):
        d = d[1:]
    if len(d) == 10:
        return "+1" + d
    return p or ""


def cmd_overpass(args):
    cities = json.load(open(args.cities)) if args.cities else DEFAULT_CITIES
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    raw = []
    if os.path.exists(args.out) and args.resume:
        raw = json.load(open(args.out))
        done_cities = {r["source_city"] for r in raw}
        cities = [c for c in cities if c["city"] not in done_cities]
        log(f"resuming: {len(done_cities)} cities already done, {len(cities)} remaining")

    for c in cities:
        log(f"querying {c['city']}, {c['state']} (radius {args.radius}m)...")
        try:
            q = build_overpass_query(c["lat"], c["lon"], args.radius)
            payload = overpass_fetch(q)
        except Exception as e:
            log(f"  GAVE UP on {c['city']}: {e}")
            continue
        n = 0
        for el in payload.get("elements", []):
            tags = el.get("tags", {})
            name = tags.get("name")
            email = (tags.get("email") or tags.get("contact:email") or "").strip().lower()
            if not (name and email):
                continue
            phone = norm_phone(tags.get("phone") or tags.get("contact:phone") or "")
            lat = el.get("lat") or (el.get("center") or {}).get("lat")
            lon = el.get("lon") or (el.get("center") or {}).get("lon")
            raw.append({
                "name": name,
                "trade": tag_to_trade(tags),
                "city": c["city"],
                "state": c["state"],
                "phone": phone,
                "email": email,
                "addr": " ".join(filter(None, [tags.get("addr:housenumber"), tags.get("addr:street")])),
                "lat": lat, "lon": lon,
                "osm_id": f"{el.get('type')}/{el.get('id')}",
                "source_method": "overpass",
                "source_city": c["city"],
            })
            n += 1
        log(f"  {c['city']}: {n} raw hits (email present, no website tag)")
        # save incrementally so a crash/rate-limit mid-run doesn't lose progress
        json.dump(raw, open(args.out, "w"), indent=2)
        time.sleep(args.sleep)
    log(f"DONE: {len(raw)} total raw Overpass hits across {len(cities)} cities -> {args.out}")


def cmd_queries(args):
    trades = FACEBOOK_TRADES if args.method == "facebook" else BBB_TRADES
    cities = FACEBOOK_CITIES if args.method == "facebook" else BBB_CITIES
    for city in cities:
        for trade in trades:
            if args.method == "facebook":
                for dom in FACEBOOK_DOMAINS:
                    print(f'site:facebook.com "{trade}" "{city}" "{dom}"')
                print(f'site:facebook.com "{trade}" "{city}" "email us"')
            else:
                print(f'site:bbb.org "{trade}" "{city}" "Email Address"')


def extract_candidates_from_hits(hits, method):
    """hits: list of {"query","url","title","snippet"} from a WebSearch tool run
    by an agent (this script cannot call WebSearch itself)."""
    out = []
    for h in hits:
        blob = " ".join([h.get("title", ""), h.get("snippet", "")])
        emails = set(EMAIL_RE.findall(blob))
        if not emails:
            continue
        for email in emails:
            domain = email.split("@")[-1].lower()
            local = email.split("@")[0].lower()
            if domain in AGGREGATOR_DOMAINS:
                continue
            out.append({
                "name": h.get("business_name") or h.get("title", "").split("|")[0].strip()[:80],
                "trade": h.get("trade", ""),
                "city": h.get("city", ""),
                "state": h.get("state", ""),
                "phone": norm_phone(h.get("phone", "")),
                "email": email.lower(),
                "email_source_url": h.get("url", ""),
                "source_method": method,
                "query": h.get("query", ""),
                "generic_local": local in GENERIC_LOCAL,
            })
    return out


def cmd_ingest_search(args):
    hits = json.load(open(args.infile))
    out = extract_candidates_from_hits(hits, args.method)
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    json.dump(out, open(args.out, "w"), indent=2)
    log(f"{args.method}: {len(hits)} search hits -> {len(out)} email candidates -> {args.out}")


def dedupe_key(row):
    phone = re.sub(r"\D", "", row.get("phone", "") or "")
    email = (row.get("email") or "").strip().lower()
    return phone or email


def cmd_merge(args):
    seen = {}
    for path in args.inputs:
        if not os.path.exists(path):
            log(f"skip (missing): {path}")
            continue
        rows = json.load(open(path))
        for r in rows:
            key = dedupe_key(r)
            if not key:
                continue
            if key not in seen:
                seen[key] = r
    merged = list(seen.values())
    json.dump(merged, open(args.out, "w"), indent=2)
    log(f"merged {len(merged)} unique candidates (by phone/email) -> {args.out}")


def cmd_to_csv(args):
    rows = json.load(open(args.infile))
    fields = ["name", "trade", "city", "state", "phone", "email", "email_source_url",
              "no_website_evidence", "operating_evidence_url", "source_method", "verified_at"]
    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})
    log(f"{len(rows)} rows -> {args.out}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("overpass", help="Method A: live Overpass sweep")
    p.add_argument("--out", default="raw/overpass_raw.json")
    p.add_argument("--cities", help="JSON file overriding DEFAULT_CITIES")
    p.add_argument("--radius", type=int, default=15000)
    p.add_argument("--sleep", type=float, default=3.0)
    p.add_argument("--resume", action="store_true")
    p.set_defaults(func=cmd_overpass)

    p = sub.add_parser("queries", help="print the Method B/C search strings to run")
    p.add_argument("--method", choices=["facebook", "bbb"], required=True)
    p.set_defaults(func=cmd_queries)

    p = sub.add_parser("ingest-search", help="Method B/C: turn saved WebSearch hits into candidates")
    p.add_argument("--method", choices=["facebook", "bbb"], required=True)
    p.add_argument("--in", dest="infile", required=True)
    p.add_argument("--out", required=True)
    p.set_defaults(func=cmd_ingest_search)

    p = sub.add_parser("merge", help="dedupe raw method outputs on phone/email")
    p.add_argument("--inputs", nargs="+", required=True)
    p.add_argument("--out", default="merged_candidates.json")
    p.set_defaults(func=cmd_merge)

    p = sub.add_parser("to-csv", help="write the CSV twin of a verified leads JSON")
    p.add_argument("--in", dest="infile", required=True)
    p.add_argument("--out", required=True)
    p.set_defaults(func=cmd_to_csv)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
