# goodnight-dreams

Public storefront + link-in-bio for Goodnight Dreams. Plain HTML/CSS/JS
(no Jekyll, no framework, no build step). Dark theme matching the
"Quiet Hours" brand. Hosted on GitHub Pages.

Live: https://jgoodnight318.github.io/goodnight-dreams/

## Pages

| Path            | What it is |
|-----------------|------------|
| `/`             | Storefront — every live Gumroad product, the podcast, YouTube, wallpaper teasers |
| `/link/`        | Link-in-bio page (Wren Ashby persona) for Instagram/TikTok/YouTube bios |
| `/wallpapers/`  | Gallery of wallpaper-pack preview covers (no full-res files) |
| `/vivid-walls/` | Landing page for Ambient Loops Vol. 1 as a Vivid Walls (Mac) content pack — import steps + buy link. Link target for the Vivid Walls site/app "more scenes" |
| `/tools/`       | Free single-page tools (empty until the problem-miner pipeline ships one) |
| `/countdown/`   | GTA 6 countdown + news tracker (independent fan project, original art only) |
| `/podcast/`     | Quiet Hours podcast info + episode list (feed not yet on Spotify/Apple) |
| `/privacy/`     | Privacy policy — no analytics, no cookies, no tracking |

Analytics: **none**. No Plausible, no GA, no pixel of any kind — this
repo intentionally ships zero analytics rather than a paid or
self-hosted alternative. See `/privacy/` for the full statement.

## Deploy

```
cd ~/Projects/goodnight_site
./deploy.sh
```

`deploy.sh` validates `products.json`, syncs any single-file HTML tools
from `~/Projects/digital_products/public/tools/` into `/tools/`, then
commits and pushes to `main`. GitHub Pages serves whatever is on `main`
at "/" — there is no separate CI build.

First-time setup (already done for this repo, kept here for reference):

```
gh repo create jgoodnight318/goodnight-dreams --public --source=. --push
gh api -X POST repos/jgoodnight318/goodnight-dreams/pages \
  -f "source[branch]=main" -f "source[path]=/"
```

## Registering a new product

Other pipelines (Etsy/Gumroad packers, the wallpaper generator, etc.)
register a new SKU by appending one object to the `products` array in
`products.json` — no HTML edit required, `index.html` and
`wallpapers/index.html` read this file at load time.

```json
{
  "key": "unique-slug",
  "name": "Display Name",
  "category": "sleep | wallpaper | bundle",
  "tagline": "One line, under ~90 characters.",
  "price": "$X.XX",
  "url": "https://goodnightdreams32.gumroad.com/l/unique-slug",
  "cover": "assets/covers/unique-slug.jpg",
  "badge": "New | Best Value | Coming soon | null",
  "featured": false,
  "status": "live | coming_soon"
}
```

- `cover` is a path relative to the site root; drop the image into
  `assets/covers/` first (square, ~1200x1200, already-branded cover
  art — not a raw full-resolution wallpaper).
- `url: null` + `status: "coming_soon"` shows the card without a
  purchase link (used for packs finished but not yet listed).
- `featured: true` puts it in the "Start here" section at the top —
  keep this to 0–1 products.
- Prices should match what's actually live on Gumroad — verify with
  the product page before committing, don't copy from a `LISTING.md`
  suggested price without checking (suggested and live prices drift).

Run `./deploy.sh` after editing to publish.

## Registering a new free tool

Drop a single self-contained `.html` file into
`~/Projects/digital_products/public/tools/` (the problem-miner's output
directory). The next `./deploy.sh` run copies it into `/tools/` and
lists it on `/tools/index.html` automatically, titled from its
filename. No further edit needed.

## Design notes

- Shared styling lives in `assets/style.css`; `/link/` and
  `/countdown/` keep their own inline styles (ported from the internal
  tailnet versions) since they're meant to also work as standalone
  single-file pages.
- Every product/episode/wallpaper on the site carries the same AI/
  procedural-generation disclosure used in the source `LISTING.md`
  files and the internal link-in-bio page — don't drop it when adding
  new copy.
- No full-resolution wallpaper or audio files are committed to this
  repo — cover art and preview collages only. Sale files stay behind
  Gumroad.
