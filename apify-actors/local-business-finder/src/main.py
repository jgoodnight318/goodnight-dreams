"""Local Business Finder. Queries OpenStreetMap's public Overpass API for businesses in a city
by category, and returns contact-ready records (name, phone, website, email, address,
coordinates). Free public data (ODbL), no key. Fixture mode (FIXTURE_DIR env) serves saved
responses for offline tests."""
import asyncio, json, os, re
import httpx
from apify import Actor

FIXTURES = os.environ.get("FIXTURE_DIR")
OVERPASS_DEFAULT = "https://overpass-api.de/api/interpreter"
UA = {"User-Agent": "local-business-finder-actor (Apify; contact via Apify console)"}

# category -> OSM tag selector (same convention as receptionist/prospect.py, expanded)
CATEGORIES = {
    "plumber": '["craft"="plumber"]', "electrician": '["craft"="electrician"]',
    "hvac": '["craft"="hvac"]', "roofer": '["craft"="roofer"]',
    "locksmith": '["craft"="locksmith"]', "landscaper": '["craft"="gardener"]',
    "painter": '["craft"="painter"]', "carpenter": '["craft"="carpenter"]',
    "dentist": '["amenity"="dentist"]', "doctor": '["amenity"="doctors"]',
    "vet": '["amenity"="veterinary"]', "chiropractor": '["healthcare"="chiropractor"]',
    "physiotherapist": '["healthcare"="physiotherapist"]', "optician": '["shop"="optician"]',
    "pharmacy": '["amenity"="pharmacy"]',
    "restaurant": '["amenity"="restaurant"]', "cafe": '["amenity"="cafe"]',
    "bar": '["amenity"="bar"]', "bakery": '["shop"="bakery"]',
    "hairdresser": '["shop"="hairdresser"]', "beauty_salon": '["shop"="beauty"]',
    "tattoo": '["shop"="tattoo"]', "gym": '["leisure"="fitness_centre"]',
    "auto_repair": '["shop"="car_repair"]', "car_wash": '["amenity"="car_wash"]',
    "car_dealer": '["shop"="car"]',
    "lawyer": '["office"="lawyer"]', "accountant": '["office"="accountant"]',
    "insurance": '["office"="insurance"]', "real_estate": '["office"="estate_agent"]',
    "hotel": '["tourism"="hotel"]', "florist": '["shop"="florist"]',
    "laundry": '["shop"="laundry"]',
}


def build_query(city, category, require_phone, limit):
    sel = CATEGORIES[category]
    city_q = city.replace("\\", "").replace('"', '\\"')
    area = f'area["name"="{city_q}"]["boundary"="administrative"]->.a;'
    if require_phone:
        body = (f'node{sel}["phone"](area.a);way{sel}["phone"](area.a);'
                f'node{sel}["contact:phone"](area.a);way{sel}["contact:phone"](area.a);')
    else:
        body = f'node{sel}(area.a);way{sel}(area.a);'
    return f"[out:json][timeout:90];{area}({body});out center tags {limit};"


def norm_phone(raw):
    if not raw:
        return ""
    raw = raw.split(";")[0].strip()
    digits = re.sub(r"[^\d+]", "", raw)
    return digits


def address_of(t):
    line = " ".join(x for x in [t.get("addr:housenumber"), t.get("addr:street")] if x)
    parts = [line, t.get("addr:city"), t.get("addr:state"), t.get("addr:postcode")]
    return ", ".join(x for x in parts if x)


def to_record(el, city, category):
    t = el.get("tags") or {}
    name = t.get("name")
    if not name:
        return None
    phone = norm_phone(t.get("phone") or t.get("contact:phone"))
    lat = el.get("lat") or (el.get("center") or {}).get("lat")
    lon = el.get("lon") or (el.get("center") or {}).get("lon")
    return {"name": name, "category": category, "city": city, "phone": phone,
            "website": t.get("website") or t.get("contact:website") or "",
            "email": t.get("email") or t.get("contact:email") or "",
            "address": address_of(t), "latitude": lat, "longitude": lon,
            "openingHours": t.get("opening_hours") or "",
            "osmId": f'{el.get("type")}/{el.get("id")}'}


async def fetch(client, url, query):
    if FIXTURES:
        key = re.sub(r"[^a-z0-9]+", "_", query.lower()).strip("_")[:120] + ".json"
        p = os.path.join(FIXTURES, key)
        if not os.path.exists(p):
            raise FileNotFoundError(f"no fixture for query -> {key}")
        return json.load(open(p))
    r = await client.post(url, data={"data": query}, timeout=120, headers=UA)
    r.raise_for_status()
    return r.json()


async def main():
    async with Actor:
        inp = await Actor.get_input() or {}
        city = (inp.get("city") or "").strip()
        cats = inp.get("categories") or []
        require_phone = bool(inp.get("requirePhone", True))
        limit = int(inp.get("maxPerCategory", 200))
        overpass = inp.get("overpassUrl") or OVERPASS_DEFAULT
        bad = [c for c in cats if c not in CATEGORIES]
        if bad:
            Actor.log.warning(f"unknown categories skipped: {bad}")
        cats = [c for c in cats if c in CATEGORIES]
        seen_phones, seen_osm, total = set(), set(), 0
        async with httpx.AsyncClient() as client:
            for i, cat in enumerate(cats):
                if i:
                    await asyncio.sleep(2)  # Overpass fair-use: don't hammer the public endpoint
                try:
                    data = await fetch(client, overpass, build_query(city, cat, require_phone, limit))
                except Exception as e:
                    Actor.log.warning(f"{city}/{cat}: {e}")
                    continue
                out = []
                for el in data.get("elements") or []:
                    r = to_record(el, city, cat)
                    if not r:
                        continue
                    if r["phone"]:
                        if r["phone"] in seen_phones:
                            continue
                        seen_phones.add(r["phone"])
                    elif require_phone:
                        continue
                    else:
                        if r["osmId"] in seen_osm:
                            continue
                        seen_osm.add(r["osmId"])
                    out.append(r)
                if out:
                    await Actor.push_data(out)
                    await Actor.charge(event_name="business", count=len(out))
                    total += len(out)
                Actor.log.info(f"{city}/{cat}: {len(out)} businesses")
        await Actor.set_value("SUMMARY", {"city": city, "categories": cats, "businesses": total})
