# App Store Reviews Scraper (iOS + Mac)

Pull the most recent customer reviews for any iOS, iPadOS or Mac app, from any country storefront,
as clean JSON. Give it App Store IDs or just app names. No login, no proxies, no Apple developer
account. Also returns the app's metadata (developer, price, average rating, rating count, version,
release notes) so one run gives you everything for competitor research, ASO, sentiment analysis,
or feeding an AI agent.

## What you get
One record per review: `rating`, `title`, `content`, `author`, `version`, `updated`, `voteSum`,
`voteCount`, plus `appId` and `country`. Optionally one `type: "app"` record per app with metadata.

## Limits
Apple exposes the 500 most recent reviews per app per storefront. Run it on a schedule to build a
full history; reviews carry a stable `reviewId` so deduplication is trivial.

## Pricing
Pay per event: **$0.002 per review** ($2 per 1,000). App metadata records are free. A 10-app,
3-country competitor sweep at 100 reviews each is about $6.

## Example input
```json
{ "apps": ["310633997", "Notion"], "countries": ["us", "gb"], "maxReviewsPerApp": 200 }
```
