# Lead engine — websites/tools/lead_engine.py

Finds local trade businesses that have **no website of their own** AND a **reachable,
business-tied public email address** — the subset of `no_site_prospects.json` (phone-only,
7/157 emailable) that can actually receive the Cascade Web Design outreach email.

Three independent methods, run and merged (dedupe on phone/email):

## Method A — Overpass (OpenStreetMap)

Fully automated. Same free/no-key Overpass pattern as `receptionist/prospect.py`, extended
to select nodes/ways tagged with `email`/`contact:email` and explicitly lacking
`website`/`contact:website`. One combined query per city (all 10 trades unioned in a single
request) across 35 US/Canada metros, Pacific-Northwest weighted first.

Rerun:
```
python3 websites/tools/lead_engine.py overpass --out websites/tools/raw/overpass_raw.json --sleep 3
```
Add `--resume` to continue an interrupted run (it saves incrementally after every city).
`--cities path.json` overrides the built-in 35-city list; `--radius` defaults to 15000m.

Endpoint note: `overpass-api.de` was fast (~7-50s/query) on 2026-09-16; the `kumi.systems`
mirror was intermittently timing out the same day. The script tries `overpass-api.de` first
and falls back to `kumi.systems`, with exponential backoff, since Overpass mirror health
varies day to day.

## Method B — Facebook-only businesses via web search

Not scriptable end-to-end (no search API key; Facebook itself is behind a login wall, so
pages are never fetched directly — only public search-result snippets are read). Run by an
agent with a WebSearch tool:
```
python3 websites/tools/lead_engine.py queries --method facebook
```
prints the query list (`site:facebook.com "<trade>" "<city>" "@gmail.com"` and variants for
`@yahoo.com`, `@outlook.com`, `"email us"`) for 15 cities x 6 trades (plumber, electrician,
hvac, roofer, landscaper, handyman). An agent runs each query, reads the snippet/synthesis,
and for every candidate independently verifies: no independent website domain, evidence the
business operates now, and the email is tied to the business on the same page. Verified
leads are recorded directly in the final JSON schema (see below) — `ingest-search` exists
for the case where raw `{query,url,title,snippet}` hits are saved to a file first, but this
run had the verifying agent do the extraction and verification in one pass.

## Method C — BBB profiles with a listed email

Same shape as Method B (WebSearch + WebFetch, agent-run, not scriptable):
```
python3 websites/tools/lead_engine.py queries --method bbb
```
prints `site:bbb.org "<trade>" "<city>" "Email Address"` for the same 15 cities x 6 trades.
Candidate profile URLs are fetched with WebFetch (skipped on 403/404, not retried) and kept
only if they show an actual email and no website field, then verified the same 3 ways as
Method B.

## Merge

```
python3 websites/tools/lead_engine.py merge \
  --inputs websites/tools/raw/overpass_raw.json websites/tools/raw/facebook_raw.json websites/tools/raw/bbb_raw.json \
  --out websites/tools/raw/merged_candidates.json
```
Dedupes on normalized phone (digits only) or lowercased email, whichever is present.

## CSV twin

```
python3 websites/tools/lead_engine.py to-csv --in websites/leads_email_2026-09-16.json --out websites/leads_email_2026-09-16.csv
```

## Verification applied to every kept lead

1. **No independent website** — one live web search `"<name>" "<city>"`; a Facebook/Yelp/
   Instagram-only presence is fine, an actual company domain is disqualifying. Query + result
   recorded as `no_website_evidence`.
2. **Operating now** — a listing, review, or post dated within the last ~12 months, URL
   recorded as `operating_evidence_url`.
3. **Email tied to the business** — the same page/tag set that gave the email also shows the
   business name or phone.

Rejected on sight: generic addresses belonging to an aggregator (not the business itself),
personal addresses with no clear business tie, and non-US/Canada phone numbers.

## Hit rates (2026-09-16 run)

<!-- FILLED IN AFTER THE RUN -->

## Productive cities/trades

<!-- FILLED IN AFTER THE RUN -->
