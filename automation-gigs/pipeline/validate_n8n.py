#!/usr/bin/env python3
"""Validate an n8n workflow JSON export is structurally importable.

Checks: top-level shape, node fields, unique names, connections reference
real nodes, at least one trigger node, no credentials pasted inline.
Exit 0 = valid, 1 = problems (printed one per line).
"""
import json, re, sys

TRIGGER_HINTS = ("trigger", "webhook", "cron", "schedule", "manual")
SECRET_PATTERNS = [
    re.compile(r"sk-ant-[A-Za-z0-9_-]{20,}"),
    re.compile(r"sk-[A-Za-z0-9]{32,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
    re.compile(r"AC[a-f0-9]{32}"),  # Twilio account SID
    re.compile(r"AKIA[0-9A-Z]{16}"),
]

def validate(path):
    errors = []
    try:
        wf = json.load(open(path))
    except Exception as e:
        return [f"not valid JSON: {e}"]
    if not isinstance(wf, dict):
        return ["top level must be an object"]
    nodes = wf.get("nodes")
    conns = wf.get("connections")
    if not isinstance(nodes, list) or not nodes:
        errors.append("'nodes' must be a non-empty list")
        nodes = []
    if not isinstance(conns, dict):
        errors.append("'connections' must be an object")
        conns = {}
    if not wf.get("name"):
        errors.append("'name' missing")
    names = []
    for i, n in enumerate(nodes):
        for k in ("name", "type", "typeVersion", "position", "parameters"):
            if k not in n:
                errors.append(f"node[{i}] missing '{k}'")
        if "name" in n:
            names.append(n["name"])
        pos = n.get("position")
        if not (isinstance(pos, list) and len(pos) == 2 and all(isinstance(x, (int, float)) for x in pos)):
            errors.append(f"node '{n.get('name', i)}' position must be [x, y]")
    dupes = {x for x in names if names.count(x) > 1}
    for d in dupes:
        errors.append(f"duplicate node name '{d}'")
    nameset = set(names)
    for src, outs in conns.items():
        if src not in nameset:
            errors.append(f"connection source '{src}' is not a node")
        main = outs.get("main") if isinstance(outs, dict) else None
        if not isinstance(main, list):
            errors.append(f"connections['{src}'].main must be a list")
            continue
        for branch in main:
            for c in branch or []:
                if c.get("node") not in nameset:
                    errors.append(f"connection {src} -> '{c.get('node')}' targets unknown node")
    if nodes and not any(any(h in (n.get("type", "") + n.get("name", "")).lower() for h in TRIGGER_HINTS) for n in nodes):
        errors.append("no trigger node found (need a Trigger/Webhook/Schedule/Manual node)")
    raw = open(path).read()
    for pat in SECRET_PATTERNS:
        if pat.search(raw):
            errors.append(f"looks like a real secret is pasted inline (pattern {pat.pattern[:12]}...) — use n8n credentials")
    return errors

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: validate_n8n.py <workflow.json> [...]"); sys.exit(2)
    bad = 0
    for p in sys.argv[1:]:
        errs = validate(p)
        if errs:
            bad += 1
            print(f"FAIL {p}")
            for e in errs: print(f"  - {e}")
        else:
            print(f"OK   {p}")
    sys.exit(1 if bad else 0)
