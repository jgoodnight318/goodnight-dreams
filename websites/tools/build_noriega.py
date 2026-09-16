#!/usr/bin/env python3
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from site_template import render_site
from icons import icon

cfg = dict(
    meta_title="Mobile Diesel Repair in Sacramento, CA | Noriega Mobile Diesel | (916) 779-9294",
    meta_description="Noriega Mobile Diesel: 24/7 mobile truck and trailer diesel repair in Sacramento, CA. We come to your rig, day or night. Call (916) 779-9294.",
    legal_name="Noriega Mobile Diesel",
    phone_e164="+19167799294",
    phone_display="(916) 779-9294",
    slug="noriega-mobile-diesel",
    hero_line1="NORIEGA",
    hero_line2="MOBILE DIESEL",
    callbar_main="NORIEGA",
    callbar_second="MOBILE DIESEL",
    arc_text="SACRAMENTO · CALIF.",
    arc_aria="Sacramento, California, mobile diesel truck and trailer repair",
    since_text="24/7 MOBILE SERVICE · TRUCK &amp; TRAILER",
    hero_call_sub="Sacramento mobile diesel repair, 24/7.",
    mailto_subject="Noriega Mobile Diesel site",
    c_enamel="#1e2733",
    c_enamel_deep="#131a22",
    c_enamel_lit="#2a3644",
    c_gold="#d0942e",
    c_gold_dim="#8f6420",
    plates=[
        ("24/7", "Roadside and shop calls, day or night"),
        ("Mobile Service", "We come to your truck or yard"),
        ("CA Registered LLC", "State-registered diesel repair business"),
    ],
    services=[
        (icon("truck"), "Roadside breakdown calls", "We come to you, any time, any day"),
        (icon("wrench-hvac"), "Engine & drivetrain repair", "Diagnostics, rebuilds, and repairs"),
        (icon("diagnostic"), "Diagnostics & emissions", "Check-engine lights, sensor faults, DPF"),
        (icon("brake"), "Brakes & air systems", "Air brakes, lines, and valves"),
        (icon("battery"), "Batteries & electrical", "Starters, alternators, wiring"),
        (icon("map-pin"), "Truck & trailer, on site", "Sacramento and the surrounding area"),
    ],
    services_note="Not sure what's wrong? Call and describe it, and we'll tell you what we need to bring.",
    steps=[
        ("YOU CALL", "Tell us what it's doing and where you are."),
        ("WE COME TO YOU", "Roadside, yard, or shop, day or night."),
        ("BACK ON THE ROAD", "Repaired on site whenever possible."),
    ],
    about_html=(
        "<p>Noriega Mobile Diesel is a Sacramento-based mobile repair business for diesel "
        "trucks and trailers, registered as a California LLC in 2024.</p>"
        "<p>Instead of towing your rig to a shop, the crew comes to the truck or trailer "
        "wherever it's parked, and takes calls around the clock.</p>"
    ),
    reviews_html=(
        '<div class="gstars">CA LLC</div>'
        '<div class="r-sub">Active, registered August 2024</div>'
        '<a class="r-link" href="https://www.bizprofile.net/ca/sacramento/noriega-mobile-diesel-truck">Read the filing yourself &rarr;</a>'
        '<p class="smallprint">Registration status from the California Secretary of State public record, September 2026.</p>'
    ),
    address_lines="6260 Belleau Wood Lane, Sacramento, CA 95822<br>Mobile service, Sacramento and the surrounding area.",
    directions_query="Noriega+Mobile+Diesel%2C+6260+Belleau+Wood+Lane%2C+Sacramento%2C+CA+95822",
    footer_nap="Noriega Mobile Diesel &middot; 6260 Belleau Wood Lane, Sacramento, CA 95822 &middot; (916) 779-9294",
    ldjson={
        "@context": "https://schema.org",
        "@type": "AutoRepair",
        "name": "Noriega Mobile Diesel",
        "telephone": "+19167799294",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "6260 Belleau Wood Lane",
            "addressLocality": "Sacramento",
            "addressRegion": "CA",
            "postalCode": "95822",
            "addressCountry": "US",
        },
        "openingHours": "Mo-Su 00:00-24:00",
        "areaServed": "Sacramento, CA metro",
        "sameAs": [
            "https://www.bizprofile.net/ca/sacramento/noriega-mobile-diesel-truck",
            "https://www.wrenchmap.com/california/sacramento/noriega-mobile-diesel-sacramento-ca",
        ],
    },
)

out = render_site(cfg)
out_path = os.path.join(os.path.dirname(__file__), "..", "sites", "noriega-mobile-diesel", "index.html")
with open(out_path, "w") as f:
    f.write(out)
print(f"wrote {out_path}, {len(out.encode('utf-8'))} bytes")
