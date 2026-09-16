# Local Business Finder (phone, website, email)

Build a contact-ready list of local businesses in any city, worldwide, from OpenStreetMap's
public database. Pick a city and one or more of 33 categories (trades, health, food, personal
care, auto, professional services) and get back business name, phone, website, email, street
address, coordinates and opening hours — deduplicated by phone number so the same business never
appears twice. No API key, no login, no proxies.

Made for lead lists, CRM imports, local SEO audits, service-area research, and outreach
campaigns for agencies selling to local businesses.

## Categories
plumber, electrician, hvac, roofer, locksmith, landscaper, painter, carpenter, dentist, doctor,
vet, chiropractor, physiotherapist, optician, pharmacy, restaurant, cafe, bar, bakery,
hairdresser, beauty_salon, tattoo, gym, auto_repair, car_wash, car_dealer, lawyer, accountant,
insurance, real_estate, hotel, florist, laundry

## What you get
One record per business: `name`, `category`, `city`, `phone`, `website`, `email`, `address`,
`latitude`, `longitude`, `openingHours`, `osmId`. With **requirePhone** (default on) every record
has a phone number; turn it off to also collect businesses that only list a website or address.

## Data source and coverage
OpenStreetMap via the Overpass API (data © OpenStreetMap contributors, ODbL). Coverage is
community-maintained: dense in North America, Europe and large cities worldwide, thinner in rural
areas. Email is listed for a minority of businesses; phone and website coverage is much higher.

## Pricing
Pay per event: **$5 per 1,000 businesses** ($0.005 each). A 3-category sweep of one mid-size city
typically returns 100–400 contactable businesses — under $2.

## Example input
```json
{ "city": "Phoenix", "categories": ["plumber", "hvac", "electrician"], "requirePhone": true }
```
