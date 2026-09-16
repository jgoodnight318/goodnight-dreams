#!/usr/bin/env python3
"""Cascade Web Design — Truck-Door Lettering System, generator.

Parametrizes the proven Jarmer Electric build (websites/sites/jarmer-electric/index.html)
per websites/DESIGN.md's SYSTEM vs THEME split, so each new prospect is a content/color
config plus a call to render_site(), not a hand-copied HTML file.

SYSTEM (fixed, do not vary per site): fonts, layout grammar, orange call-only rule,
cream/shade inks, rivet/panel/reveal mechanics, footer credit, motion script.
THEME (per business): business name/lockup, trade copy, enamel triplet + gold accent,
services/steps/trust content, JSON-LD facts.

Known, deliberate deviation from the Jarmer reference: Jarmer's CSS declares a
'BarlowSemiCondensed-700.woff2' @font-face whose file was never actually shipped
(websites/sites/jarmer-electric/fonts/ only has 500 and 600) -- a dead font-face that
404s in production. This template does not repeat that: font-weight tops out at 600,
which is within DESIGN.md's documented "600-700" emphasis range, and no third font
file is fetched.
"""
import html as _html
import json
import re
from string import Template

FONT_CSS = """@font-face { font-family: 'Alfa Slab One'; src: url('fonts/AlfaSlabOne-400.woff2') format('woff2'); font-weight: 400; font-display: swap; }
@font-face { font-family: 'Barlow Semi Condensed'; src: url('fonts/BarlowSemiCondensed-500.woff2') format('woff2'); font-weight: 500; font-display: swap; }
@font-face { font-family: 'Barlow Semi Condensed'; src: url('fonts/BarlowSemiCondensed-600.woff2') format('woff2'); font-weight: 600; font-display: swap; }"""

# Hero placeholder photo system -- see DESIGN.md "Signature Component: Doorframe
# Hero Photo". Approved set lives in websites/assets/heroes/ (AI-generated, generic,
# uniform patches/name tags blurred). One photo per SPEC PREVIEW site, chosen by
# trade; a trade with no mapped photo keeps the original photo-free doorframe.
HERO_PHOTO_DIMS = {
    "plumber": (1109, 768),
    "electrician": (1330, 768),
    "auto": (1243, 768),
    "pet": (1268, 692),
}
HERO_PHOTO_ALT = {
    "plumber": "Plumber at work",
    "electrician": "Electrician at work",
    "auto": "Auto mechanic at work",
    "pet": "Pet groomer at work",
}
# trade string (lowercased, spaces/hyphens normalized to "_") -> hero photo basename
HERO_PHOTO_TRADES = {
    "plumber": "plumber",
    "plumbing": "plumber",
    "electrician": "electrician",
    "electrical": "electrician",
    "car_repair": "auto",
    "auto": "auto",
    "auto_repair": "auto",
    "tint": "auto",
    "window_tint": "auto",
    "wraps": "auto",
    "vehicle_wraps": "auto",
    "diesel": "auto",
    "mobile_diesel": "auto",
    "performance": "auto",
    "pet_grooming": "pet",
    "pet_groomer": "pet",
}


def hero_photo_for_trade(trade):
    """Map a free-text trade to a hero-photo basename, or None. Trades with no
    approved placeholder (hvac, roofing, landscaping, etc.) return None and the
    site keeps the existing photo-free doorframe -- this is the expected, common
    case, not a fallback error."""
    if not trade:
        return None
    key = re.sub(r"[\s-]+", "_", trade.strip().lower())
    return HERO_PHOTO_TRADES.get(key)


def hero_photo_html(base):
    """Render the door-photo markup for an approved hero-photo basename, or ''
    when base is None (photo-free doorframe, unchanged from the SYSTEM default)."""
    if not base:
        return ""
    if base not in HERO_PHOTO_DIMS:
        raise ValueError(f"unknown hero photo basename: {base!r}")
    w, h = HERO_PHOTO_DIMS[base]
    alt = esc(HERO_PHOTO_ALT[base])
    return (
        f'<div class="door-photo"><img src="images/{base}-900.jpg" '
        f'srcset="images/{base}-900.jpg 900w, images/{base}.jpg {w}w" '
        f'sizes="(max-width: 1060px) 100vw, 1060px" '
        f'width="{w}" height="{h}" alt="{alt}" loading="eager" fetchpriority="high"></div>'
    )

PAGE = Template(r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>$meta_title</title>
<meta name="description" content="$meta_description">
<link rel="preload" href="fonts/AlfaSlabOne-400.woff2" as="font" type="font/woff2" crossorigin>
<script type="application/ld+json">
$ldjson
</script>
<script>document.documentElement.classList.add('js');</script>
<style>
/* ── Cascade Web Design · truck-door livery world ─────────────────────────── */
$font_css

:root {
  --enamel: $c_enamel;          /* per-business ground hue */
  --enamel-deep: $c_enamel_deep;
  --enamel-lit: $c_enamel_lit;
  --cream: #f3e9d5;            /* lettering cream — system, fixed */
  --cream-dim: #cdbfa3;
  --gold: $c_gold;              /* per-business accent */
  --gold-dim: $c_gold_dim;
  --call: #ff5c1c;             /* safety orange — CALL ACTIONS ONLY, system, fixed */
  --call-deep: #c93f0d;
  --shade: #060d16;            /* signpainter's drop shade — system, fixed */
  --display: 'Alfa Slab One', 'Rockwell', serif;
  --body: 'Barlow Semi Condensed', 'Arial Narrow', sans-serif;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  background: var(--enamel-deep);
  color: var(--cream);
  font-family: var(--body);
  font-weight: 500;
  font-size: 1.125rem;
  line-height: 1.55;
}
::selection { background: var(--gold); color: var(--enamel-deep); }
:focus-visible { outline: 3px solid var(--gold); outline-offset: 3px; }
a { color: var(--cream); }

.panel {
  position: relative;
  background:
    radial-gradient(120% 90% at 30% 0%, var(--enamel-lit) 0%, var(--enamel) 55%, var(--enamel-deep) 100%);
}
.panel::after {
  content: ""; position: absolute; inset: 0; pointer-events: none;
  background: linear-gradient(168deg, rgba(243,233,213,.045) 0%, rgba(243,233,213,0) 28%);
}

.tape {
  position: relative; z-index: 5;
  background: #e8d9ae;
  color: #4a3d1e;
  font-weight: 600; font-size: .95rem; letter-spacing: .01em;
  padding: .55rem 1rem; text-align: center;
  transform: rotate(-.4deg); margin: .6rem .8rem -0.2rem;
  box-shadow: 0 2px 8px rgba(0,0,0,.35);
}
.tape::before, .tape::after {
  content: ""; position: absolute; top: 0; bottom: 0; width: 14px;
  background: inherit; filter: brightness(.92);
}
.tape::before { left: -8px; transform: skewY(6deg); }
.tape::after { right: -8px; transform: skewY(-6deg); }
.tape a { color: inherit; font-weight: 700; }

.callbar {
  position: sticky; top: 0; z-index: 10;
  display: flex; align-items: center; justify-content: space-between; gap: 1rem;
  background: var(--enamel-deep);
  border-bottom: 1px solid var(--gold-dim);
  padding: .6rem clamp(1rem, 4vw, 2.2rem);
}
.callbar .word {
  font-family: var(--display); font-size: 1.05rem; letter-spacing: .04em; color: var(--cream);
  text-decoration: none;
}
.callbar .word span { color: var(--gold); font-size: 1em; }
.btn-call {
  white-space: nowrap;
  display: inline-flex; align-items: center; gap: .55rem;
  background: linear-gradient(180deg, #f9601f 0%, var(--call) 45%, var(--call-deep) 100%);
  color: #2e0e02; text-decoration: none;
  font-weight: 700; font-size: 1.05rem; letter-spacing: .03em;
  padding: .55rem 1.05rem; border-radius: 6px;
  box-shadow: 0 3px 9px rgba(0,0,0,.45), inset 0 1px 0 rgba(255,255,255,.35);
}
.btn-call svg { flex: none; }
@media (max-width: 480px) {
  .callbar { gap: .6rem; }
  .callbar .word span { display: none; }
  .btn-call { font-size: 1rem; padding: .5rem .9rem; }
}
.btn-call:hover { filter: brightness(1.06); }
.btn-call:active { transform: translateY(1px); }

.door {
  max-width: 1060px; margin: clamp(1rem, 3vw, 2.5rem) auto; padding: 0 clamp(.8rem, 3vw, 2rem);
}
.doorframe {
  border: 2px solid var(--gold);
  outline: 1px solid var(--gold-dim); outline-offset: 6px;
  border-radius: 14px;
  padding: clamp(2.2rem, 6vw, 4.5rem) clamp(1.2rem, 5vw, 3.5rem) 0;
  text-align: center; overflow: hidden;
}
.rivet { position: absolute; width: 11px; height: 11px; border-radius: 50%;
  background: radial-gradient(circle at 35% 30%, #e8d9ae, var(--gold-dim) 70%, #5c4d27);
  box-shadow: 0 1px 2px rgba(0,0,0,.5); }
.doorframe { position: relative; isolation: isolate; }
.rivet.tl { top: 12px; left: 12px; } .rivet.tr { top: 12px; right: 12px; }
.rivet.bl { bottom: 12px; left: 12px; } .rivet.br { bottom: 12px; right: 12px; }
/* Hero placeholder photo (SPEC PREVIEW only, replaced by the client's own photos at
   launch) -- full-bleed behind the doorframe panel, dark enamel gradient on top so
   the lettering, arc tagline and orange call panel keep contrast. Absent entirely
   (no .door-photo node) on trades with no approved placeholder. */
.door-photo { position: absolute; inset: 0; z-index: 0; }
.door-photo img { width: 100%; height: 100%; object-fit: cover; display: block; }
.door-photo::after {
  content: ""; position: absolute; inset: 0;
  background:
    linear-gradient(180deg, rgba(6,13,22,.32) 0%, rgba(13,26,44,.72) 48%, rgba(13,26,44,.92) 100%),
    radial-gradient(120% 90% at 30% 0%, rgba(27,50,82,.35) 0%, rgba(13,26,44,.55) 70%);
}
.doorframe h1, .doorframe > .arc, .doorframe > .since { position: relative; z-index: 1; }

h1 {
  font-family: var(--display); font-weight: 400;
  font-size: clamp(3.4rem, 12.5vw, 6rem);
  line-height: .92; letter-spacing: .01em;
  color: var(--cream);
  text-shadow:
    2px 2px 0 var(--shade), 4px 4px 0 var(--shade),
    5px 5px 0 rgba(6,13,22,.55),
    0 0 1px var(--gold);
}
h1 .second { display: block; font-size: .62em; letter-spacing: .14em; color: var(--gold);
  text-shadow: 2px 2px 0 var(--shade), 3px 3px 0 rgba(6,13,22,.5); }
.arc { display: block; margin: .4rem auto 0; width: min(92%, 560px); height: auto; }
.arc text {
  font-family: var(--body); font-weight: 700; font-size: 30px;
  letter-spacing: .34em; fill: var(--cream-dim);
}
.since {
  position: relative; display: inline-block;
  margin-top: 1.05rem; padding: .5rem 2.3rem;
  color: var(--gold); font-weight: 600; font-size: 1.05rem; letter-spacing: .18em;
  border: 1.5px solid var(--gold-dim); border-radius: 8px;
  background: linear-gradient(180deg, rgba(27,50,82,.65), rgba(13,26,44,.65));
}
.since .rivet { width: 7px; height: 7px; top: 50%; margin-top: -3.5px; }
.since .rivet.cl { left: 9px; } .since .rivet.cr { right: 9px; }
@media (max-width: 560px) { .since { font-size: .9rem; padding: .45rem 1.7rem; letter-spacing: .12em; } }
.hero-call {
  display: block; position: relative; overflow: hidden;
  margin: clamp(1.6rem, 4vw, 2.6rem) calc(-1 * clamp(1.2rem, 5vw, 3.5rem)) 0;
  background: linear-gradient(180deg, #f9601f 0%, var(--call) 40%, var(--call-deep) 100%);
  color: #2e0e02; text-decoration: none;
  padding: 1.35rem 1rem 1.5rem;
}
.hero-call .lead { font-weight: 700; font-size: 1.05rem; letter-spacing: .22em; color: #2e0e02; }
.hero-call .num {
  font-family: var(--display); font-size: clamp(1.9rem, 7.5vw, 3.4rem); letter-spacing: .02em;
  color: #fff8ef; text-shadow: 2px 2px 0 rgba(70,17,0,.85), 3px 3px 0 rgba(46,14,2,.5);
}
.hero-call .sub { font-weight: 600; font-size: 1rem; color: #fff8ef; }
.hero-call::before {
  content: ""; position: absolute; top: -20%; bottom: -20%; width: 34%;
  left: -45%; transform: skewX(-18deg);
  background: linear-gradient(90deg, rgba(255,255,255,0) 0%, rgba(255,255,255,.38) 50%, rgba(255,255,255,0) 100%);
}
@media (prefers-reduced-motion: no-preference) {
  .hero-call::before { animation: glint 1.1s cubic-bezier(.22,.61,.36,1) .7s 1 both; }
  @keyframes glint { from { left: -45%; } to { left: 120%; } }
  .js .reveal { opacity: 0; transform: translateY(26px) scale(.994);
    transition: opacity .65s cubic-bezier(.16,1,.3,1), transform .65s cubic-bezier(.16,1,.3,1), box-shadow .65s cubic-bezier(.16,1,.3,1);
    transition-delay: var(--stagger, 0ms); }
  .reveal.in { opacity: 1; transform: none; }
  .js .plate.reveal, .js section .panelbox { box-shadow: 0 0 0 rgba(0,0,0,0); }
  .plate.reveal.in, section .panelbox { box-shadow: 0 10px 26px -14px rgba(0,0,0,.55); }
  h1 { text-shadow: calc(2px + var(--d,0px)) calc(2px + var(--d,0px)) 0 var(--shade),
       calc(4px + var(--d,0px)) calc(4px + var(--d,0px)) 0 var(--shade),
       5px 5px 0 rgba(6,13,22,.55), 0 0 1px var(--gold); }
}

.plates { display: grid; gap: .9rem; grid-template-columns: 1fr;
  max-width: 1060px; margin: 1.4rem auto 0; padding: 0 clamp(.8rem, 3vw, 2rem); }
@media (min-width: 720px) { .plates { grid-template-columns: 1fr 1fr 1fr; } }
/* content-driven variants for businesses with fewer independently-sourced trust facts --
   never pad to 3 with an invented figure; show as many honest plates as are sourced */
.plates.n1 { max-width: 480px; }
@media (min-width: 720px) { .plates.n1 { grid-template-columns: 1fr; } }
.plates.n2 { max-width: 680px; }
@media (min-width: 720px) { .plates.n2 { grid-template-columns: 1fr 1fr; } }
.plate {
  position: relative; border: 1.5px solid var(--gold-dim); border-radius: 10px;
  padding: 1.05rem 1.1rem .95rem; text-align: center;
}
.plate .big { font-family: var(--display); font-size: 1.55rem; color: var(--cream);
  text-shadow: 1.5px 1.5px 0 var(--shade); }
.plate .big .star { color: var(--gold); }
.plate .small { color: var(--cream-dim); font-size: .98rem; font-weight: 600; letter-spacing: .04em; margin-top: .15rem; }
.plate .rivet.tl { top: 7px; left: 7px; } .plate .rivet.tr { top: 7px; right: 7px; }
.plate .rivet { width: 8px; height: 8px; }

section { max-width: 1060px; margin: clamp(1.6rem, 4vw, 2.6rem) auto; padding: 0 clamp(.8rem, 3vw, 2rem); }
.panelbox { border-radius: 14px; border: 1.5px solid var(--gold-dim); padding: clamp(1.4rem, 4vw, 2.4rem); }
h2 {
  font-family: var(--display); font-weight: 400; font-size: clamp(1.7rem, 4.5vw, 2.3rem);
  letter-spacing: .03em; color: var(--cream); text-shadow: 2px 2px 0 var(--shade);
  margin-bottom: 1.1rem;
}
h2 .tick { color: var(--gold); }

.services { display: grid; gap: .3rem .9rem; grid-template-columns: 1fr; margin-top: .4rem; }
@media (min-width: 700px) { .services { grid-template-columns: 1fr 1fr; } }
.service { display: flex; gap: .85rem; align-items: center; padding: .68rem .35rem;
  border-bottom: 1px solid rgba(201,162,75,.28); }
.service:last-child, .service:nth-last-child(2) { border-bottom: 0; }
@media (max-width: 699px) { .service:nth-last-child(2) { border-bottom: 1px solid rgba(201,162,75,.28); } }
.service svg { flex: none; color: var(--gold); }
.service .s-name { font-weight: 600; font-size: 1.12rem; letter-spacing: .02em; }
.service .s-sub { color: var(--cream-dim); font-size: .98rem; font-weight: 500; }
.services-note { margin-top: 1.1rem; color: var(--cream-dim); font-size: 1rem; }

.steps { display: grid; gap: 1.1rem; grid-template-columns: 1fr; }
@media (min-width: 700px) { .steps { grid-template-columns: 1fr 1fr 1fr; } }
.step { text-align: center; padding: .6rem .4rem; }
.step .disc {
  width: 58px; height: 58px; margin: 0 auto .65rem; border-radius: 50%;
  display: grid; place-items: center;
  background: radial-gradient(circle at 32% 28%, var(--enamel-lit), var(--enamel-deep) 75%);
  border: 2px solid var(--gold);
  font-family: var(--display); font-size: 1.6rem; color: var(--cream);
  text-shadow: 1.5px 1.5px 0 var(--shade);
}
.step .st-name { font-weight: 600; font-size: 1.18rem; letter-spacing: .05em; }
.step .st-sub { color: var(--cream-dim); font-size: 1rem; }

.split { display: grid; gap: 1.2rem; grid-template-columns: 1fr; }
@media (min-width: 860px) { .split { grid-template-columns: 3fr 2fr; } }
.about p + p { margin-top: .8rem; }
.gstars { font-family: var(--display); font-size: 2.6rem; color: var(--cream); text-shadow: 2px 2px 0 var(--shade); }
.gstars .star { color: var(--gold); }
.reviews .r-sub { color: var(--cream-dim); font-weight: 600; margin-top: .2rem; }
.reviews a.r-link { display: inline-block; margin-top: .9rem; color: var(--cream); font-weight: 600; }
.smallprint { color: var(--cream-dim); font-size: .88rem; margin-top: 1rem; }

.contact address { font-style: normal; font-size: 1.15rem; line-height: 1.7; }
.contact .row { display: flex; flex-wrap: wrap; gap: .5rem 2rem; margin-top: 1rem; }
.contact a { font-weight: 600; }

.finale { text-align: center; padding-bottom: .4rem; }
.finale .btn-call { font-size: 1.3rem; padding: .9rem 1.6rem; }

footer {
  border-top: 1px solid var(--gold-dim);
  margin-top: clamp(2rem, 5vw, 3.2rem);
  padding: 1.4rem clamp(1rem, 4vw, 2.2rem) 2rem;
  text-align: center; color: var(--cream-dim); font-size: .98rem;
}
footer .nap { font-weight: 600; }
footer .credit { margin-top: .7rem; }
footer .credit a { color: var(--gold); font-weight: 600; }
</style>
</head>
<body>

<p class="tape">SPEC PREVIEW: built for $legal_name_html by Cascade Web Design.
Yours to keep: <a href="mailto:jms.goodnight@gmail.com?subject=$mailto_subject">say the word</a>.</p>

<div class="callbar">
  <a class="word" href="#top">$callbar_main <span>$callbar_second</span></a>
  <a class="btn-call" href="tel:$phone_e164" aria-label="Call $legal_name_html at $phone_display">
    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3 19.5 19.5 0 0 1-6-6 19.8 19.8 0 0 1-3-8.7A2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.13.96.36 1.9.7 2.8a2 2 0 0 1-.45 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.45c.9.34 1.84.57 2.8.7A2 2 0 0 1 22 16.9z"/></svg>
    $phone_display
  </a>
</div>

<main id="top">
  <div class="door">
    <div class="doorframe panel">
      $door_photo_html
      <span class="rivet tl"></span><span class="rivet tr"></span><span class="rivet bl"></span><span class="rivet br"></span>
      <h1>$hero_line1<span class="second">$hero_line2</span></h1>
      <svg class="arc" viewBox="0 0 560 110" role="img" aria-label="$arc_aria">
        <path id="arcpath-$slug" d="M 30 96 Q 280 18 530 96" fill="none"/>
        <text><textPath href="#arcpath-$slug" startOffset="50%" text-anchor="middle">$arc_text</textPath></text>
      </svg>
      <p class="since"><span class="rivet cl"></span>$since_text<span class="rivet cr"></span></p>
      <a class="hero-call" href="tel:$phone_e164">
        <span class="lead">CALL THE SHOP</span><br>
        <span class="num">$phone_display</span><br>
        <span class="sub">$hero_call_sub</span>
      </a>
    </div>
  </div>

  <div class="plates$plates_class">
$plates_html
  </div>

  <section class="reveal">
    <div class="panelbox panel">
      <h2><span class="tick">▸</span> What we take on</h2>
      <div class="services">
$services_html
      </div>
      <p class="services-note">$services_note</p>
    </div>
  </section>

  <section class="reveal">
    <div class="panelbox panel">
      <h2><span class="tick">▸</span> How it goes</h2>
      <div class="steps">
$steps_html
      </div>
    </div>
  </section>

  <section class="reveal">
    <div class="split">
      <div class="panelbox panel about">
        <h2><span class="tick">▸</span> The shop</h2>
        $about_html
      </div>
      <div class="panelbox panel reviews">
        <h2><span class="tick">▸</span> Word around town</h2>
        $reviews_html
      </div>
    </div>
  </section>

  <section class="reveal contact">
    <div class="panelbox panel">
      <h2><span class="tick">▸</span> Find us</h2>
      <address>
        <strong>$legal_name_html</strong><br>
        $address_lines
      </address>
      <div class="row">
        <a href="tel:$phone_e164">$phone_display</a>
        $directions_link
      </div>
    </div>
  </section>

  <section class="finale reveal">
    <a class="btn-call" href="tel:$phone_e164">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3 19.5 19.5 0 0 1-6-6 19.8 19.8 0 0 1-3-8.7A2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.13.96.36 1.9.7 2.8a2 2 0 0 1-.45 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.45c.9.34 1.84.57 2.8.7A2 2 0 0 1 22 16.9z"/></svg>
      CALL $phone_display
    </a>
  </section>
</main>

<footer>
  <div class="nap">$footer_nap</div>
  <div class="credit">Site by <a href="mailto:jms.goodnight@gmail.com?subject=Cascade%20Web%20Design">Cascade Web Design</a> · Vancouver, WA</div>
</footer>

<script>
if (matchMedia('(prefers-reduced-motion: no-preference)').matches) {
  const io = new IntersectionObserver(es => {
    let i = 0;
    es.forEach(e => {
      if (e.isIntersecting) {
        e.target.style.setProperty('--stagger', (Math.min(i++, 3) * 110) + 'ms');
        e.target.classList.add('in'); io.unobserve(e.target);
      }
    });
  }, { rootMargin: '0px 0px -8% 0px' });
  document.querySelectorAll('.reveal').forEach(el => io.observe(el));
  const h1 = document.querySelector('h1');
  let tick = false;
  addEventListener('scroll', () => {
    if (tick) return; tick = true;
    requestAnimationFrame(() => {
      const d = Math.min(scrollY / 600, 1) * 2.5;
      h1.style.setProperty('--d', d.toFixed(2) + 'px');
      tick = false;
    });
  }, { passive: true });
} else {
  document.querySelectorAll('.reveal').forEach(el => el.classList.add('in'));
}
</script>
</body>
</html>
""")


def esc(s):
    return _html.escape(str(s), quote=True)


def plate(big, small):
    return (f'    <div class="plate panel reveal"><span class="rivet tl"></span><span class="rivet tr"></span>\n'
            f'      <div class="big">{big}</div>\n'
            f'      <div class="small">{esc(small)}</div>\n'
            f'    </div>')


def service(svg, name, sub):
    return (f'        <div class="service">\n'
            f'          {svg}\n'
            f'          <div><div class="s-name">{esc(name)}</div><div class="s-sub">{esc(sub)}</div></div>\n'
            f'        </div>')


def step(n, name, sub):
    return (f'        <div class="step">\n'
            f'          <div class="disc">{n}</div>\n'
            f'          <div class="st-name">{esc(name)}</div>\n'
            f'          <div class="st-sub">{esc(sub)}</div>\n'
            f'        </div>')


def render_site(cfg):
    """cfg: dict of THEME values. See websites/sites/*/site_config.py for examples."""
    required = ["meta_title", "meta_description", "legal_name", "phone_e164", "phone_display",
                "slug", "hero_line1", "hero_line2", "callbar_main", "callbar_second",
                "arc_text", "arc_aria", "since_text", "hero_call_sub", "plates", "services",
                "services_note", "steps", "about_html", "reviews_html", "address_lines",
                "footer_nap", "c_enamel", "c_enamel_deep", "c_enamel_lit", "c_gold", "c_gold_dim",
                "ldjson", "mailto_subject"]
    missing = [k for k in required if k not in cfg]
    if missing:
        raise ValueError(f"missing required config keys: {missing}")

    ctx = dict(cfg)
    ctx["legal_name_html"] = esc(cfg["legal_name"])
    ctx["font_css"] = FONT_CSS
    ctx["plates_html"] = "\n".join(plate(*p) for p in cfg["plates"])
    ctx["services_html"] = "\n".join(service(*s) for s in cfg["services"])
    ctx["steps_html"] = "\n".join(step(i + 1, *s) for i, s in enumerate(cfg["steps"]))
    ctx["ldjson"] = json.dumps(cfg["ldjson"], indent=2)
    n_plates = len(cfg["plates"])
    variant = {1: " n1", 2: " n2"}.get(n_plates, "")
    ctx["plates_class"] = cfg.get("plates_class", variant)
    ctx.setdefault("directions_link", "")
    if "directions_query" in cfg and not ctx.get("directions_link"):
        ctx["directions_link"] = f'<a href="https://maps.google.com/?q={cfg["directions_query"]}">Get directions →</a>'

    # Hero placeholder photo: cfg["hero_photo"] names an approved basename directly
    # (e.g. "electrician"); otherwise it's derived from cfg["trade"]. Most trades
    # (hvac, roofing, landscaping, ...) map to None and get no photo -- unchanged
    # doorframe, not an error.
    hero_base = cfg.get("hero_photo") or hero_photo_for_trade(cfg.get("trade"))
    ctx["door_photo_html"] = hero_photo_html(hero_base)

    out = PAGE.substitute(ctx)
    return out


def size_report(html_str, fonts_bytes=44000):
    total = len(html_str.encode("utf-8")) + fonts_bytes
    return {"html_bytes": len(html_str.encode("utf-8")), "fonts_bytes_est": fonts_bytes, "total_bytes_est": total}
