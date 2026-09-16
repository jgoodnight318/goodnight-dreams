#!/usr/bin/env python3
"""Keyword a folder of AI-generated images for stock marketplaces (Adobe Stock, Freepik, Vecteezy).

For every image without a sidecar .json, Claude looks at the file and writes a marketplace-ready
title, 40-49 keywords, and a category. Output: <image>.json next to the image.

  tag.py <images_dir> [--limit 50]
Rules baked in from the contributor guidelines: title 5-200 chars, descriptive not salesy, no brand
names, no people-identifying claims, keywords ordered most-relevant first, AI flag always on.
"""
import argparse, glob, json, os, re, subprocess, sys, time

ADOBE_CATEGORIES = ["Abstract", "Backgrounds", "Business", "Landscapes", "Lifestyle", "Nature", "Technology",
                    "Travel", "Science", "Graphic Resources", "The Environment", "States of Mind"]

PROMPT = """Read the image at {path}. You are keywording it for Adobe Stock and Freepik as an AI-generated stock asset.
Reply with ONLY a JSON object:
{{"title": "5-200 characters, descriptive, what a buyer would search, no brand names, no 'AI' in the title",
  "keywords": ["40 to 49 single words or short phrases, most relevant first, lowercase, no duplicates, no brand names, include subject, setting, mood, colors, style, use-cases like wallpaper/background/banner"],
  "category": "one of: {cats}",
  "mood": "one short phrase"}}"""

def keyword_image(path):
    prompt = PROMPT.format(path=os.path.abspath(path), cats=", ".join(ADOBE_CATEGORIES))
    r = subprocess.run(["claude", "-p", prompt, "--allowedTools", "Read", "--output-format", "json"],
                       capture_output=True, text=True, timeout=240)
    if r.returncode != 0:
        raise RuntimeError(r.stderr[-500:])
    out = json.loads(r.stdout)
    text = out.get("result", "")
    m = re.search(r"\{.*\}", text, re.S)
    d = json.loads(m.group(0))
    # normalise to marketplace limits
    seen, kws = set(), []
    for k in d.get("keywords", []):
        k = re.sub(r"[^a-z0-9 \-]", "", str(k).lower()).strip()
        if k and k not in seen and len(kws) < 49:
            seen.add(k); kws.append(k)
    d["keywords"] = kws
    d["title"] = str(d.get("title", ""))[:200]
    if d.get("category") not in ADOBE_CATEGORIES:
        d["category"] = "Backgrounds"
    d["ai_generated"] = True
    d["cost_usd"] = out.get("total_cost_usd")
    d["keyworded_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    return d

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("images_dir"); ap.add_argument("--limit", type=int, default=50)
    a = ap.parse_args()
    files = sorted(f for ext in ("*.jpg", "*.jpeg", "*.png") for f in glob.glob(os.path.join(a.images_dir, ext)))
    n = 0
    for f in files:
        side = os.path.splitext(f)[0] + ".json"
        if os.path.exists(side) or n >= a.limit:
            continue
        try:
            d = keyword_image(f)
        except Exception as e:
            print("FAILED", f, e); continue
        json.dump(d, open(side, "w"), indent=2); n += 1
        print(f"{os.path.basename(f)}: {d['title'][:70]} [{len(d['keywords'])} kw, {d['category']}]")
    print(f"keyworded {n} image(s)")

if __name__ == "__main__":
    main()
