#!/usr/bin/env python3
"""Find local service businesses with a listed phone number, from OpenStreetMap (free, no key).

  prospect.py --city "Phoenix" --category plumber [--limit 60] [--fixture file.json]

Appends new businesses to data/prospects.csv with status=new. Dedups on phone.
"""
import argparse, hashlib, json, urllib.parse
from common import *

CATEGORIES = {
    "plumber": '["craft"="plumber"]', "electrician": '["craft"="electrician"]', "hvac": '["craft"="hvac"]',
    "roofer": '["craft"="roofer"]', "locksmith": '["craft"="locksmith"]', "landscaper": '["craft"="gardener"]',
    "dentist": '["amenity"="dentist"]', "vet": '["amenity"="veterinary"]', "auto_repair": '["shop"="car_repair"]',
    "chiropractor": '["healthcare"="chiropractor"]',
}
OVERPASS = "https://overpass-api.de/api/interpreter"

def query(city, category):
    sel = CATEGORIES[category]
    return (f'[out:json][timeout:60];area["name"="{city}"]["boundary"="administrative"]->.a;'
            f'(node{sel}["phone"](area.a);way{sel}["phone"](area.a);'
            f'node{sel}["contact:phone"](area.a);way{sel}["contact:phone"](area.a););out center 200;')

def fetch(city, category, fixture=None):
    if fixture:
        return json.load(open(fixture))
    return http_get(OVERPASS + "?" + urllib.parse.urlencode({"data": query(city, category)}), timeout=90)

def to_rows(payload, city, category):
    rows = []
    for el in payload.get("elements", []):
        t = el.get("tags", {})
        phone = norm_phone(t.get("phone") or t.get("contact:phone"))
        name = t.get("name")
        if not (phone and name):
            continue
        rows.append({"id": hashlib.sha1(phone.encode()).hexdigest()[:10], "name": name, "category": category,
                     "city": city, "phone": phone, "website": t.get("website") or t.get("contact:website") or "",
                     "email": t.get("email") or t.get("contact:email") or "", "status": "new"})
    return rows

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--city", required=True); ap.add_argument("--category", required=True, choices=CATEGORIES)
    ap.add_argument("--limit", type=int, default=60); ap.add_argument("--fixture")
    a = ap.parse_args()
    existing = load(); seen = {r["phone"] for r in existing}
    new = []
    for r in to_rows(fetch(a.city, a.category, a.fixture), a.city, a.category):
        if r["phone"] in seen or len(new) >= a.limit:
            continue
        seen.add(r["phone"]); new.append(r)
    save(existing + new)
    log(f"{a.city}/{a.category}: {len(new)} new prospects (total {len(existing) + len(new)})")

if __name__ == "__main__":
    main()
