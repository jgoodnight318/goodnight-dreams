# Website Contact Scraper (email, phone, socials)

Turn a plain list of website URLs into outreach-ready contact records. For each site it fetches
the homepage plus a handful of discovered contact/about/team pages, and pulls out email
addresses, phone numbers and social profile links (Facebook, Instagram, LinkedIn, X/Twitter,
YouTube, TikTok). Feed it a lead list from any source, or pair it with a local business finder,
to turn raw domains into contacts a sales or marketing team can actually reach.

## What you get
One record per input website: `emails`, `phones`, `socials` (one canonical profile URL per
network, or `null`), `pagesScanned`, `finalUrl`, and `success`/`error`. A record is pushed for
every input, including sites that fail to load, so buyers always get one row per input.

## Honest limits
- **Public pages only.** It reads the homepage and up to `maxExtraPages` same-domain pages whose
  link text or URL looks like contact, about, impressum, team, support or kontakt. It does not
  crawl the whole site.
- **No JS rendering.** Sites that only render contact info via client-side JavaScript (no plain
  HTML fallback) will yield less. Most business and marketing sites work fine.
- **No guessing.** It never fabricates or permutes emails (no `first.last@domain.com` guessing).
  It only reports what's actually published in the fetched pages.
- Phone number matching is deliberately conservative — it favors missing an odd format over
  reporting junk.

## Pricing
Pay per event: **$5 per 1,000 websites successfully processed** ($0.005 each). Failed fetches
are free.

## Example input
```json
{ "websites": ["apify.com", "allbirds.com"], "maxExtraPages": 3 }
```
