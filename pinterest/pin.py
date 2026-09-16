#!/usr/bin/env python3
"""Daily Pinterest pinner for the Gumroad catalog. Standard library only.

Reads products.json, picks the products that have gone longest without a pin, has Claude write a
fresh title + description for each (Pinterest penalises duplicate pins), and posts through the
official Pinterest API v5 with the product's cover image and Gumroad link. Nothing else in this
repo gets traffic on its own; this is the traffic.

  pin.py [--per-day 4] [--dry-run]
Env: PINTEREST_ACCESS_TOKEN (scopes pins:write, boards:read), PINTEREST_BOARD_ID,
     SITE_BASE (default https://jgoodnight318.github.io/goodnight-dreams/)
State: pinterest/state.json (last pin time and angle history per product). Dry-run writes the
pins it would post to pinterest/queue/ instead.
"""
import argparse, json, os, re, subprocess, sys, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
STATE = os.path.join(HERE, "state.json")
QUEUE = os.path.join(HERE, "queue")
SITE = os.environ.get("SITE_BASE", "https://jgoodnight318.github.io/goodnight-dreams/")
API = "https://api.pinterest.com/v5/pins"

ANGLES = ["aesthetic desk setup", "cozy night routine", "study / focus session", "sleep better tonight",
          "minimal dark wallpaper", "rainy day mood", "phone wallpaper refresh", "gift for a night owl",
          "work from home vibe", "seasonal reset"]

def load_state():
    return json.load(open(STATE)) if os.path.exists(STATE) else {}

def save_state(s):
    json.dump(s, open(STATE, "w"), indent=2)

def claude_copy(product, angle):
    prompt = ("Write a Pinterest pin for a digital product. Pinterest users search by mood and use-case, "
              "so lead with the vibe, not the product name. Rules: title under 90 characters, description "
              "80-180 words, natural keywords (no hashtags spam, max 3 hashtags at the end), no emoji, mention it "
              "is an instant download, do not invent features not in the facts. End the description with a plain "
              "call to action. Reply with ONLY JSON: {\"title\": \"...\", \"description\": \"...\"}\n\n"
              f"Angle for this pin: {angle}\n\nFacts:\n{json.dumps(product, indent=2)}")
    r = subprocess.run(["claude", "-p", prompt, "--output-format", "json"], capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        raise RuntimeError(r.stderr[-500:])
    text = json.loads(r.stdout).get("result", "")
    m = re.search(r"\{.*\}", text, re.S)
    return json.loads(m.group(0))

def fallback_copy(product, angle):
    return {"title": f"{product['name']} for a {angle}"[:90],
            "description": f"{product['tagline']} Instant download. {angle.capitalize()} pick from Goodnight Dreams. Tap to see the full pack."}

def trim(text, n):
    """Cut at the last sentence end within n characters (Pinterest caps descriptions at 800)."""
    if len(text) <= n:
        return text
    cut = text[:n]
    i = max(cut.rfind(". "), cut.rfind(".\n"), cut.rfind("!"), cut.rfind("?"))
    return cut[:i + 1] if i > 200 else cut.rsplit(" ", 1)[0]

def post_pin(token, board, title, desc, link, image_url):
    body = json.dumps({"board_id": board, "title": title, "description": desc, "link": link,
                       "media_source": {"source_type": "image_url", "url": image_url}}).encode()
    req = urllib.request.Request(API, data=body, method="POST",
                                 headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--per-day", type=int, default=4); ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    token, board = os.environ.get("PINTEREST_ACCESS_TOKEN"), os.environ.get("PINTEREST_BOARD_ID")
    if not a.dry_run and not (token and board):
        sys.exit("PINTEREST_ACCESS_TOKEN / PINTEREST_BOARD_ID not set (use --dry-run to test)")
    products = [p for p in json.load(open(os.path.join(ROOT, "products.json")))["products"]
                if p.get("status") == "live" and p.get("cover") and p.get("url")]
    state = load_state()
    # least-recently-pinned first
    products.sort(key=lambda p: state.get(p["key"], {}).get("last", 0))
    os.makedirs(QUEUE, exist_ok=True); posted = 0
    for p in products[:a.per_day]:
        hist = state.setdefault(p["key"], {"last": 0, "angles": []})
        angle = next((x for x in ANGLES if x not in hist["angles"]), None) or ANGLES[len(hist["angles"]) % len(ANGLES)]
        facts = {k: p[k] for k in ("name", "category", "tagline", "price")}
        try:
            copy = claude_copy(facts, angle)
        except Exception as e:
            print("claude failed, using fallback:", e); copy = fallback_copy(p, angle)
        link = p["url"]; image = SITE + p["cover"]
        pin = {"product": p["key"], "angle": angle, "title": copy["title"][:100], "description": trim(copy["description"], 800), "link": link, "image": image}
        if a.dry_run:
            json.dump(pin, open(os.path.join(QUEUE, f"{time.strftime('%Y%m%d')}-{p['key']}.json"), "w"), indent=2)
            print("[dry]", pin["title"])
        else:
            res = post_pin(token, board, pin["title"], pin["description"], link, image)
            print("pinned", res.get("id"), pin["title"])
        hist["last"] = int(time.time()); hist["angles"].append(angle); posted += 1
        time.sleep(2)
    save_state(state); print(f"{posted} pin(s) {'queued' if a.dry_run else 'posted'}")

if __name__ == "__main__":
    main()
