# PRODUCT.md — Cascade Web Design site generator

## What this is
A generator that produces complete, deployable one-page websites for local service
businesses (plumbers, HVAC, electricians, and adjacent trades) that currently have **no
website at all**. The site is built and deployed to a live preview URL *before* any
contact — the outreach email leads with the finished artifact. Business model: $500
one-time to keep the site (own domain, edits) + $25/mo hosting/maintenance. Sold under
**Cascade Web Design** (James's existing LLC), which also takes the footer credit on
every shipped site ("Site by Cascade Web Design") as the referral loop.

## Who visits the generated sites, and what success is
Two audiences, one page:
1. **The business owner** seeing their own preview for the first time from a cold email.
   Success = "this looks like a real company built this for me specifically" → replies to buy.
2. **Their future customer** (e.g., a Phoenix homeowner with a burst pipe, on a phone,
   stressed, comparison-shopping from Google). Success = taps the call button. Every
   generated site is Persuade mode: the page exists to produce a phone call.

## Product truth and constraints
- Input per site: one prospect record from our lead pipeline (name, trade, city, phone,
  hours, coordinates/address when present) plus whatever is verifiable publicly (Google
  reviews count/rating when we can source it). NEVER invent facts: no fake reviews, fake
  years-in-business, fake licenses, fake photos of "the team" presented as real. If a
  trust element isn't sourced, the design must earn trust without it.
- Scoped exception, decided 2026-09-16: SPEC PREVIEW sites may carry one hero photo from
  the approved, AI-generated placeholder set in `websites/assets/heroes/`, chosen by the
  business's trade (plumber, electrician, auto/car_repair/tint/wraps/diesel/performance,
  pet grooming; other trades keep the photo-free hero). This is not a trust element and
  makes no factual claim: it is a clearly generic stand-in for "a photo of this trade,"
  never presented as this business's real staff, truck, or shop, and it is replaced by
  the client's own photos the moment the site goes live. It does not relax the
  no-invented-facts rule anywhere else on the page.
- Output: static HTML/CSS (+ minimal JS), one page, self-contained, deployed to Vercel
  as <business-slug>.vercel.app previews. Custom domain happens only after purchase.
- Mobile-first is not a preference, it's the product: the paying visitor is on a phone.
- Performance is part of the pitch (we will tell owners "your site loads instantly"):
  hard budget — LCP < 1.5s on 4G, CLS ~0, no blocking third-party scripts, system or
  self-hosted fonts only, images optimized and dimensioned.
- One **signature design system** with deep per-business theming (palette, trade
  iconography, tone of copy, imagery treatment) — 50 sites should feel like siblings
  from one excellent studio, never like one template with find-replace.
- Per-trade copy must read like a competent human wrote it for THIS business: city and
  neighborhood names used naturally, trade-specific services, no filler superlatives.
- Legal floor: real business name/phone only; CAN-SPAM-clean outreach lives in the
  receptionist lane's pipeline, not here; footer credit links to Cascade Web Design.

## Explicit quality bar (from James, verbatim intent)
High quality, "no AI slop": nothing recycled from existing asset packs, no generic
template smell, no stock-photo clichés of grinning models. If imagery is used it is
purpose-built (SVG/graphic treatments are preferred over fake photography). The site
must survive a professional designer's glance.

## Out of scope (v1)
Multi-page sites, booking systems, CMS, client editing UI, SEO content farms. One
excellent page per business, generated + deployed autonomously, sold by James.
