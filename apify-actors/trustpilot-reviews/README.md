# Trustpilot Reviews Scraper

Pull Trustpilot reviews for any company by domain, as clean JSON. Give it a domain
(`monzo.com`) or a full `trustpilot.com/review/...` URL. No login, no proxies. Also
returns the company's Trustpilot score, star rating, categories and total review count,
so one run gives you everything for reputation monitoring, competitor research, lead
qualification, or feeding an AI sentiment-analysis pipeline.

## What you get
One record per review: `rating`, `title`, `text`, `authorName`, `authorCountry`, `date`,
`verified`, `replyText`, `replyDate`, plus `domain`. Optionally one `type: "company"`
record per domain with `name`, `trustScore`, `totalReviews`, `stars`, `categories`,
`website` and `trustpilotUrl`. Reviews are returned newest first.

## Limits
This reads Trustpilot's public review pages only - no login, no scraping behind
authentication. Trustpilot fronts its site with bot-detection (an AWS WAF JS challenge),
so this actor drives a real headless Chromium browser under the hood instead of plain
HTTP requests - that's slower (roughly 2-4 seconds per review page) but rides through
the challenge. Heavy volume, especially from datacenter IPs, can still get a run
rate-limited or blocked. If that happens the actor logs a warning and stops that company
cleanly rather than crashing the run - schedule smaller runs (fewer companies or fewer
reviews per company) if you hit this.

## Pricing
Pay per event: **$2 per 1,000 reviews** ($0.002 each). Company metadata records are
free. A 10-company sweep at 100 reviews each is about $2.

## Example input
```json
{ "companies": ["www.notion.so", "monzo.com"], "maxReviewsPerCompany": 100, "includeCompanyInfo": true }
```
