"""Shared helpers for the receptionist business scripts. Standard library only."""
import csv, json, os, re, subprocess, sys, time, urllib.request, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("RCP_DATA_DIR", os.path.join(HERE, "data"))
PROSPECTS = os.path.join(DATA, "prospects.csv")
FIELDS = ["id", "name", "category", "city", "phone", "website", "email", "status",
          "drafted_at", "reply_class", "notes"]

def env(name, default=None):
    return os.environ.get(name, default)

def load(path=PROSPECTS):
    if not os.path.exists(path):
        return []
    with open(path, newline="") as f:
        return list(csv.DictReader(f))

def save(rows, path=PROSPECTS, fields=FIELDS):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})
    os.replace(tmp, path)

def norm_phone(p):
    d = re.sub(r"\D", "", p or "")
    if len(d) == 11 and d.startswith("1"):
        d = d[1:]
    return "+1" + d if len(d) == 10 else ""

def http_get(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": "receptionist-research/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read().decode("utf-8", "replace")
        return json.loads(raw) if "json" in r.headers.get("Content-Type", "") else raw

def claude_json(prompt, model=None, timeout=300):
    cmd = ["claude", "-p", prompt, "--output-format", "json"] + (["--model", model] if model else [])
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError(r.stderr[-1000:])
    out = json.loads(r.stdout)
    text = out.get("result", "") if isinstance(out, dict) else str(out)
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError("no JSON in Claude output: " + text[:200])
    return json.loads(m.group(0))

def now():
    return time.strftime("%Y-%m-%dT%H:%M:%S")

def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)
