---
name: Cascade Web Design — Truck-Door Lettering System
description: Painted-enamel, fleet-livery design system for Cascade Web Design's generated local-trade sites; reference build is Jarmer Electric (Portland, OR electrician).
colors:
  enamel: "#14263e"
  enamel-deep: "#0d1a2c"
  enamel-lit: "#1b3252"
  cream: "#f3e9d5"
  cream-dim: "#cdbfa3"
  gold: "#c9a24b"
  gold-dim: "#8a7440"
  call: "#ff5c1c"
  call-deep: "#c93f0d"
  shade: "#060d16"
typography:
  display:
    fontFamily: "'Alfa Slab One', 'Rockwell', serif"
    fontSize: "clamp(3.4rem, 12.5vw, 6rem)"
    fontWeight: 400
    lineHeight: 0.92
    letterSpacing: "0.01em"
  headline:
    fontFamily: "'Alfa Slab One', 'Rockwell', serif"
    fontSize: "clamp(1.7rem, 4.5vw, 2.3rem)"
    fontWeight: 400
    lineHeight: 1.55
    letterSpacing: "0.03em"
  body:
    fontFamily: "'Barlow Semi Condensed', 'Arial Narrow', sans-serif"
    fontSize: "1.125rem"
    fontWeight: 500
    lineHeight: 1.55
    letterSpacing: "normal"
  label:
    fontFamily: "'Barlow Semi Condensed', 'Arial Narrow', sans-serif"
    fontSize: "1.05rem"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "0.22em"
rounded:
  pill: "6px"
  chip: "8px"
  plate: "10px"
  panel: "14px"
  full: "50%"
spacing:
  gutter: "clamp(.8rem, 3vw, 2rem)"
  panel-pad: "clamp(1.4rem, 4vw, 2.4rem)"
  section-gap: "clamp(1.6rem, 4vw, 2.6rem)"
  door-pad-top: "clamp(2.2rem, 6vw, 4.5rem)"
components:
  button-primary:
    backgroundColor: "linear-gradient(180deg, #f9601f 0%, {colors.call} 45%, {colors.call-deep} 100%)"
    textColor: "#2e0e02"
    typography: "{typography.label}"
    rounded: "{rounded.pill}"
    padding: "0.55rem 1.05rem"
  chip-badge:
    backgroundColor: "linear-gradient(180deg, rgba(27,50,82,.65), rgba(13,26,44,.65))"
    textColor: "{colors.gold}"
    typography: "{typography.label}"
    rounded: "{rounded.chip}"
    padding: "0.5rem 2.3rem"
  card-plate:
    backgroundColor: "{colors.enamel}"
    textColor: "{colors.cream}"
    typography: "{typography.headline}"
    rounded: "{rounded.plate}"
    padding: "1.05rem 1.1rem 0.95rem"
  panel-section:
    backgroundColor: "{colors.enamel}"
    textColor: "{colors.cream}"
    rounded: "{rounded.panel}"
    padding: "{spacing.panel-pad}"
---

# Design System: Cascade Web Design Truck-Door Livery

## Overview

**Creative North Star: "The Painted Service Truck"**

Every generated site is one business's own truck door, lettered at highway scale and parked on the homepage. The world refuses both the stock-photo local-business template and its gradient-SaaS opposite: no cover-photo hero illustrations, nothing borrowed from an asset pack. Depth comes from paint and rivets, not glass — enamel panels are built as three-stop radial gradients with a faint diagonal sheen, business names carry a hard signpainter drop-shade instead of a blurred box-shadow, and every plate is bolted down with a symmetric pair (or quad) of rivets at its corners.

**SPEC PREVIEW placeholder photo, scoped exception (2026-09-16):** the doorframe may carry one hero photo, from the approved set in `websites/assets/heroes/`, chosen by the business's trade. This is a placeholder for the SPEC PREVIEW stage only — a clearly generic, AI-generated stand-in that reads as "a photo of this trade," never as this specific business or its actual staff. It never claims to depict the real crew, truck, or shop, and it is replaced by the client's own photos when the site goes live. Trades with no approved photo (HVAC, roofing, landscaping, and anything else outside the mapped set) keep the original photo-free doorframe. See "Signature Component: Doorframe Hero Photo" below.

The page is built once as a reusable grammar and re-skinned per business: the enamel hue, the gold accent, and the business's own name/trade/city facts change from site to site; the shade-offset lettering, the rivet-and-chip hardware, the reserved-for-calling orange, the type pairing, and the panel/reveal motion do not. That split is the product — fifty generated sites should read as fifty trucks from the same fleet, never as one template with find-replace.

On a phone, the page has one job: get a call placed. A sticky call bar is always visible, the hero panel breaks its own frame to bleed a full-width orange call panel right under the lettering, and a final call panel closes the page. Safety orange is a verb here, not a color — the instant something isn't a phone call, it isn't orange.

**Key Characteristics:**
- Enamel-and-rivet materiality: every panel is a lit/base/deep radial gradient plus rivet hardware, never a flat fill
- Hard, offset signpainter drop-shadow on display type — depth from paint, not blur
- Orange reserved exclusively for `tel:` actions; everywhere else the palette stays navy/cream/gold
- Alfa Slab One for identity and headline moments, Barlow Semi Condensed for everything else
- One-shot, `prefers-reduced-motion`-gated motion: a single specular glint on load, a staggered panel reveal, a scroll-linked shade deepening — nothing loops

## Colors

Ten values, three roles. One color exists purely to trigger a phone call, one is the per-business identity accent, and the rest are the neutral "materials" (enamel, lettering, ink) that every business's site is built from.

### Primary
- **Safety Orange** (`#ff5c1c`) / **Ember Deep** (`#c93f0d`) — SYSTEM, fixed. The `--call` / `--call-deep` gradient (lit stop `#f9601f`, hardcoded, not promoted to a custom property) appears in exactly two places in the shipped build: the sticky call button and the hero call panel. Nowhere else.
- On-orange ink pair — SYSTEM, fixed: `#2e0e02` (dark chocolate text) and `#fff8ef` (warm paper white for the phone number itself), used only on top of the orange gradient.

### Secondary
- **Signpainter Gold** (`#c9a24b`) / **Gold, Dimmed** (`#8a7440`) — THEME, per-business accent. Carries borders, the "▸" section ticks, "Est./License" language, stat highlights, and rivet hardware. This build's value is Jarmer Electric's instance; a re-theme swaps the hue.

### Neutral
- **Enamel triplet** — THEME, per-business ground hue. `--enamel-lit` (`#1b3252`), `--enamel` (`#14263e`), `--enamel-deep` (`#0d1a2c`) are the three stops of every panel's radial gradient. Shown here is Jarmer Electric's deep navy; a re-theme swaps all three hexes together, never one in isolation.
- **Lettering Cream** (`#f3e9d5`) / **Cream, Dimmed** (`#cdbfa3`) — SYSTEM, fixed. Primary and secondary text ink on enamel, regardless of business.
- **Drop Shade** (`#060d16`) — SYSTEM, fixed. The signpainter offset-shadow ink stacked under every piece of display type.

### Named Rules
**The Orange-Is-a-Verb Rule.** Safety orange (`--call` / `--call-deep`) appears only on elements that place a phone call. It never decorates, highlights, or accents.

**The Per-Business Triplet Rule.** Every enamel ground is a three-stop radial gradient (lit → base → deep) built from one business hue, never a flat single fill. Re-theming a new business means swapping the three hex values that feed the gradient, not the gradient geometry.

## Typography

**Display Font:** Alfa Slab One (with Rockwell, serif fallback)
**Body Font:** Barlow Semi Condensed (with Arial Narrow, sans-serif fallback)

**Character:** a painted slab face for identity moments paired with a condensed California-signage workhorse for everything read at length — the pairing of a hand-lettered truck door and its DOT-vernacular stencil numbers.

### Hierarchy
- **Display** (400, `clamp(3.4rem, 12.5vw, 6rem)`, line-height .92): the business name (`h1`). Carries the two-step hard drop-shadow (`2px 2px` + `4px 4px`, ink `--shade`) plus a 1px gold glow. Also used at smaller scale for the "since"/stat numerals on trust plates, the star rating, and the numbered step discs — always the display face for a painted numeral or identity word, never for a sentence.
- **Headline** (400, `clamp(1.7rem, 4.5vw, 2.3rem)`, line-height 1.55 inherited): section headings (`h2`), each led by a gold "▸" tick.
- **Body** (500–700, `1.125rem` base, line-height 1.55): running copy. Weight climbs to 600–700 for emphasized labels (service names, footer credit) without changing face.
- **Label** (600–700, ~`1.05rem`, letter-spacing `.14em`–`.34em`): short all-caps taglines and badges — the "since" chip, the hero call's "CALL THE SHOP" lead-in, the arced "PORTLAND · OREGON" SVG text (`.34em`, the widest tracking in the system), and the `h1`'s "ELECTRIC" subline (`.14em`).

### Named Rules
**The Slab-for-Identity Rule.** Alfa Slab One is reserved for identity and headline moments — the business name, section headings, and the big painted numerals (ratings, stats, step numbers). Barlow Semi Condensed carries every other word on the page.

**The Typed-Caps Rule.** Nothing on the page uses `text-transform`. Every all-caps moment (the tagline, the "since" badge, the arc text, the call lead-in) is typed in caps in the source content itself. A generator populating business facts into these slots must supply pre-cased strings, not rely on CSS.

## Layout

Single-column content spine, `max-width: 1060px`, centered, mobile-first. Horizontal gutters and vertical section rhythm are fluid `clamp()` values, not fixed breakpoint jumps: gutter `clamp(.8rem, 3vw, 2rem)`, section-to-section gap `clamp(1.6rem, 4vw, 2.6rem)`, panel interior padding `clamp(1.4rem, 4vw, 2.4rem)`.

Columns appear only above three min-width thresholds, each tied to the content it serves: services grid and the 1-2-3 steps strip go 2-up/3-up at `700px`, trust plates go 3-up at `720px`, the about/reviews split goes `3fr / 2fr` at `860px`. Below those widths everything is a single stacked column — the default state, not a fallback.

A sticky call bar (`position: sticky; top: 0; z-index: 10`) pins above the stack at all times. Below `480px` it drops the trade word ("ELECTRIC") and keeps only the business surname and the phone number — the number itself never truncates or shrinks past legibility.

## Elevation & Depth

Hybrid: mostly flat, layered enamel with hairline gold-dim borders (`1.5px`), and depth read through **hard, offset text-shadow** rather than blur. The one true soft, blurred `box-shadow` on a container appears only once a reveal panel has settled onto the stack (`0 10px 26px -14px rgba(0,0,0,.55)`) — depth is earned by motion, not resting state.

### Shadow Vocabulary
- **Signpainter drop-shade** (`text-shadow: 2px 2px 0 var(--shade), 4px 4px 0 var(--shade), 5px 5px 0 rgba(6,13,22,.55), 0 0 1px var(--gold)`): the default treatment for every display-face word (`h1`, `h2`, plate numerals, step discs, star rating). Hard-edged, stacked, never blurred.
- **Rivet bolt-head** (`box-shadow: 0 1px 2px rgba(0,0,0,.5)`): the small literal shadow under every rivet dot.
- **Call button lift** (`box-shadow: 0 3px 9px rgba(0,0,0,.45), inset 0 1px 0 rgba(255,255,255,.35)`): the one glossy, literal-object shadow — reserved for the call button's raised-enamel edge.
- **Panel settle** (`box-shadow: 0 10px 26px -14px rgba(0,0,0,.55)`): applied only after a `.reveal` panel finishes animating in.

### Named Rules
**The Paint-Not-Glass Rule.** Depth reads through hard, offset text-shadow and layered radial-gradient enamel. Soft blurred box-shadows are reserved for small, literal physical objects (a rivet's bolt-head, a button's raised edge) — never used as ambient page depth.

## Shapes

A four-step radius scale tied to element weight: `6px` (pill — the call button), `8px` (chip — the since-badge), `10px` (plate — trust cards), `14px` (panel — the doorframe and every section wrapper), plus true circles (`50%` — rivets, the numbered step discs). Bigger surfaces get bigger radii.

Borders are hairline `1.5px solid var(--gold-dim)` everywhere except the hero doorframe, which gets a heavier `2px solid var(--gold)` inner border plus a second `1px solid var(--gold-dim)` outline offset `6px` outward — a deliberate double-frame, the one place the border weight steps up to mark the page's single most important panel.

Content is clipped only by rounded corners. The hero call panel is the one place the grammar intentionally breaks its own frame: it bleeds past the doorframe's own padding on negative side-margins, a full-bleed orange stripe cutting through the enamel border — reserved for the highest-priority action on the page.

## Components

### Buttons
- **Shape:** pill (`border-radius: 6px`)
- **Primary (call):** `linear-gradient(180deg, #f9601f 0%, var(--call) 45%, var(--call-deep) 100%)` background, `#2e0e02` ink, `700` weight, `.03em` tracking, `.55rem 1.05rem` padding (larger in the finale panel: `.9rem 1.6rem` at `1.3rem` font-size). Every instance carries a phone icon (inline SVG, `currentColor`) before the number.
- **Hover / Focus:** hover brightens (`filter: brightness(1.06)`); active nudges down 1px (`translateY(1px)`); focus-visible gets a `3px solid var(--gold)` outline offset `3px` — the page-wide focus ring, not button-specific.

### Chips
- **Style:** the "since" badge — `1.5px solid var(--gold-dim)` border, `8px` radius, translucent enamel-gradient fill (`rgba(27,50,82,.65)` → `rgba(13,26,44,.65)`), gold label text, a rivet dot flanking each side.
- **State:** static; no interactive variant exists in the shipped build.

### Cards / Containers
- **Corner Style:** `10px` (trust plates) or `14px` (section panels, doorframe)
- **Background:** the enamel triplet radial gradient plus the diagonal sheen overlay (`::after`, a faint `168deg` white-to-transparent wash) — "enamel is never flat."
- **Shadow Strategy:** none at rest; see Elevation & Depth for the settle-in shadow.
- **Border:** `1.5px solid var(--gold-dim)` (doorframe uses the heavier double-frame described in Shapes).
- **Internal Padding:** `clamp(1.4rem, 4vw, 2.4rem)` for section panels; `1.05rem 1.1rem .95rem` for trust plates.

### Navigation
- **Style:** the sticky call bar — enamel-deep background, `1px solid var(--gold-dim)` bottom hairline, business word-mark in the display face on the left, the call button always on the right. No hover-state menu exists; there is no nav beyond the word-mark and the call button.

### Signature Component: Arc-Lettered Tagline
An inline SVG (`viewBox="0 0 560 110"`) with a `<textPath>` following a shallow arc beneath the business name — trade-and-city set in the wide-tracked label style (`.34em`, the widest tracking anywhere in the system), mimicking a hand-lettered sign painter's curve. This, not a straight subhead line, is how every site states its trade and city.

### Signature Component: Doorframe Hero Photo (SPEC PREVIEW placeholder)
One photo, chosen by trade, sits full-bleed behind the doorframe panel — not beside it. It is the first child inside `.doorframe`, `position: absolute; inset: 0`, clipped to the doorframe's own `14px` radius by the doorframe's `overflow: hidden`. A dark enamel gradient (`linear-gradient` navy-to-near-opaque, `--shade`/`--enamel-deep` register, plus the panel's own radial sheen) sits on top of the photo and behind the text, so the `h1`, arc tagline, since-badge and rivets — all promoted to `position: relative; z-index: 1` — keep full contrast; the hero-call panel is unaffected either way since its own orange fill is opaque. `.doorframe` carries `isolation: isolate` so this stacking stays self-contained and can't bleed into neighboring panels. Markup is a real `<img>` (not a CSS background) with `width`/`height` set from the source photo, `loading="eager"` and `fetchpriority="high"` (it is the LCP element when present), a `srcset` offering the 900px-wide mobile variant alongside the full-size original, and generic `alt` text ("Plumber at work") — never a name, claim, or caption. The photo is a *placeholder*: approved, AI-generated, deliberately generic images living in `websites/assets/heroes/` (`plumber.jpg`, `electrician.jpg`, `auto.jpg`, `pet.jpg`, each with a `-900.jpg` mobile variant), one per trade, swapped out for the client's own photography the moment a site goes live. A trade with no approved photo (HVAC, roofing, landscaping, painting, carpentry, and anything else outside the mapped set) gets no `.door-photo` node at all — the original photo-free doorframe is still the SYSTEM default, not a fallback.

### Signature Component: Reveal-Staggered Panel Stack
Every `section` and trust `.plate` carries `.reveal`; an `IntersectionObserver` adds `.in` on first intersection and then unobserves. Elements that cross the threshold **together** (e.g. the three trust plates on load) cascade at `110ms` intervals, capped at 3 steps (`330ms` max); elements that cross alone settle immediately. Both gated behind `document.documentElement.classList.add('js')` (so a no-JS visitor sees the page fully visible) and `prefers-reduced-motion: no-preference` (reduced-motion visitors get everything visible immediately, no animation path at all).

### Named Rules
**The Rivet-Pair Rule.** Any bordered "plate" (doorframe, trust plate, since-badge) gets rivets in a symmetric pair or quad at its corners — 2 or 4, never 1 or an odd count.

**The Once-and-Settle Rule.** The hero's specular glint sweeps exactly once on load; each panel reveals exactly once, then unobserves itself. Nothing on the page loops.

## Do's and Don'ts

### Do:
- **Do** reserve safety orange strictly for `tel:` call actions (The Orange-Is-a-Verb Rule).
- **Do** build every enamel surface as a three-stop lit/base/deep radial gradient plus the faint diagonal sheen overlay — enamel is never a flat fill.
- **Do** type labels and taglines in caps directly in the content, with letter-spacing between `.14em` and `.34em`; never reach for `text-transform: uppercase`.
- **Do** pair rivets at symmetric corners on any bordered plate (doorframe: 4, trust plate: 2, since-badge: 2).
- **Do** stagger panels that enter the viewport together (up to 3 steps, `110ms` apart, capped at `330ms`) and drop straight to instant-visible under `prefers-reduced-motion: reduce`.
- **Do** keep the phone number legible at every breakpoint — the callbar hides the trade word before it ever truncates the number.
- **Do** use at most one hero photo per SPEC PREVIEW site, from the approved set in `websites/assets/heroes/`, chosen by trade, full-bleed behind the doorframe with the dark enamel gradient overlay — never a second photo elsewhere on the page, never a caption or claim attached to it.

### Don't:
- **Don't** use orange anywhere except a call action — no orange badges, borders, icons, or link states.
- **Don't** blur the signpainter drop-shadow into a soft glow; it must stay a hard offset (paint, not glass).
- **Don't** add photography beyond the one approved doorframe placeholder. The rest of the world stays paint, inline-SVG line icons (`26px`, `2px` stroke, gold), and type. The placeholder photo itself is a SPEC PREVIEW-only, clearly generic stand-in — never presented as the real business, staff, or premises, and always replaced by the client's own photos at launch.
- **Don't** loop or repeat the glint sweep or panel reveal; both are one-shot, `prefers-reduced-motion`-gated animations.
- **Don't** widen the content column past `1060px`; every band (door, plates, sections, split) shares that single max-width.
