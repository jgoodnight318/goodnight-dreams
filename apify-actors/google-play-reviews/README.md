# Google Play Reviews Scraper (Android)

Pull the most recent customer reviews for any Android app on Google Play, from any country
storefront, as clean JSON. Give it package IDs (like `com.whatsapp`) or just app names. No login,
no proxies, no Google Play developer account. Also returns the app's metadata (developer, score,
rating count, installs, price, current version) so one run gives you everything for competitor
research, ASO, sentiment analysis, or feeding an AI agent.

## What you get
One record per review: `rating`, `content`, `author`, `thumbsUp`, `reviewCreatedVersion`, `at`,
`replyContent`, `repliedAt`, plus `appId` and `country`. Optionally one `type: "app"` record per
app with metadata. Google Play reviews have no title field, so `title` is always `null`.

## Limits
Google exposes reviews without requiring login, but through an unofficial endpoint (this Actor
uses the `google-play-scraper` library, which scrapes Google Play's own public web pages) rather
than a documented API — Google can change the page structure at any time. There's no fixed cap
like Apple's 500, but Google Play only serves the most recent slice of the full review history per
pull. The pattern that works: run this on a schedule and dedupe on the stable `reviewId` to build a
full history over time.

## Pricing
Pay per event: **$2 per 1,000 reviews** ($0.002 each). App metadata records are free. A 10-app
competitor sweep at 100 reviews each is about $2.

## Example input
```json
{ "apps": ["com.whatsapp", "Notion"], "country": "us", "maxReviewsPerApp": 200 }
```
