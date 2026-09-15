#!/usr/bin/env python3
"""Fulfill one order: brief.md -> deliverable/ via headless Claude Code.

Usage:
  fulfill.py <order_dir> [--mock] [--model MODEL]

Reads  <order_dir>/brief.md (buyer's requirements + any notes).
Writes <order_dir>/deliverable/*  and  <order_dir>/STATUS.json.

Loop: build -> validate any *.workflow.json -> if invalid, one repair pass
with the validator errors -> final validate. Exit 0 when READY.
"""
import json, os, re, subprocess, sys, time, glob, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
PROMPT = open(os.path.join(HERE, "prompts", "fulfillment.md")).read()
VALIDATOR = os.path.join(HERE, "validate_n8n.py")

def run_claude(prompt, model=None, timeout=900):
    cmd = ["claude", "-p", prompt, "--output-format", "json"]
    if model:
        cmd += ["--model", model]
    t0 = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError(f"claude exited {r.returncode}: {r.stderr[-2000:]}")
    outer = json.loads(r.stdout)
    text = outer.get("result", "") if isinstance(outer, dict) else str(outer)
    return text, time.time() - t0, outer.get("total_cost_usd") if isinstance(outer, dict) else None

def parse_files_json(text):
    text = text.strip()
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError("no JSON object in model output")
    obj = json.loads(m.group(0))
    if "files" not in obj or not isinstance(obj["files"], dict):
        raise ValueError("model output has no 'files' map")
    return obj

def write_files(files, out_dir):
    for rel, content in files.items():
        rel = rel.lstrip("/").replace("..", "")
        p = os.path.join(out_dir, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            f.write(content if isinstance(content, str) else json.dumps(content, indent=2))

def validate_all(out_dir):
    wfs = glob.glob(os.path.join(out_dir, "**", "*.workflow.json"), recursive=True)
    if not wfs:
        return True, ""
    r = subprocess.run([sys.executable, VALIDATOR] + wfs, capture_output=True, text=True)
    return r.returncode == 0, r.stdout

def mock_build(order_dir, out_dir):
    """Offline plumbing test: copies a portfolio workflow as the deliverable."""
    src = os.path.join(HERE, "..", "portfolio", "lead-qualifier")
    for f in os.listdir(src):
        shutil.copy(os.path.join(src, f), out_dir)
    open(os.path.join(out_dir, "DELIVERY_MESSAGE.md"), "w").write("(mock) delivery message\n")
    return {"summary": "mock build", "status": "READY", "questions_for_buyer": [], "files": {}}

def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(2)
    order_dir = os.path.abspath(sys.argv[1])
    mock = "--mock" in sys.argv
    model = None
    if "--model" in sys.argv:
        model = sys.argv[sys.argv.index("--model") + 1]
    brief_path = os.path.join(order_dir, "brief.md")
    if not os.path.exists(brief_path):
        print(f"no brief.md in {order_dir}"); sys.exit(2)
    brief = open(brief_path).read()
    out_dir = os.path.join(order_dir, "deliverable")
    if os.path.isdir(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir)

    status = {"order": os.path.basename(order_dir), "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "passes": []}
    if mock:
        obj = mock_build(order_dir, out_dir)
    else:
        prompt = PROMPT + "\n\n## Buyer brief\n\n" + brief
        text, secs, cost = run_claude(prompt, model)
        status["passes"].append({"kind": "build", "seconds": round(secs), "cost_usd": cost})
        try:
            obj = parse_files_json(text)
        except Exception as e:
            # one retry asking for the contract to be honoured
            text, secs, cost = run_claude(prompt + "\n\nYour previous reply was not a single JSON object. Reply with ONLY the JSON object.", model)
            status["passes"].append({"kind": "build-retry", "seconds": round(secs), "cost_usd": cost, "reason": str(e)})
            obj = parse_files_json(text)
        write_files(obj["files"], out_dir)

    ok, report = validate_all(out_dir)
    status["validation"] = report
    if not ok and not mock:
        repair = (PROMPT + "\n\n## Buyer brief\n\n" + brief +
                  "\n\n## Repair pass\nA previous build produced files that failed validation:\n" + report +
                  "\nReturn the full corrected file set (all files, not just the fixed one).")
        text, secs, cost = run_claude(repair, model)
        status["passes"].append({"kind": "repair", "seconds": round(secs), "cost_usd": cost})
        obj2 = parse_files_json(text)
        shutil.rmtree(out_dir); os.makedirs(out_dir)
        write_files(obj2["files"], out_dir)
        obj["summary"] = obj2.get("summary", obj["summary"])
        obj["questions_for_buyer"] = obj2.get("questions_for_buyer", obj.get("questions_for_buyer", []))
        ok, report = validate_all(out_dir)
        status["validation"] = report

    status["state"] = "READY" if ok and obj.get("status", "READY") == "READY" else ("NEEDS_INFO" if ok else "FAILED_VALIDATION")
    status["summary"] = obj.get("summary", "")
    status["questions_for_buyer"] = obj.get("questions_for_buyer", [])
    status["files"] = sorted(os.path.relpath(p, out_dir) for p in glob.glob(os.path.join(out_dir, "**", "*"), recursive=True) if os.path.isfile(p))
    status["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    json.dump(status, open(os.path.join(order_dir, "STATUS.json"), "w"), indent=2)
    print(json.dumps({k: status[k] for k in ("order", "state", "summary", "questions_for_buyer", "files")}, indent=2))
    sys.exit(0 if status["state"] in ("READY", "NEEDS_INFO") else 1)

if __name__ == "__main__":
    main()
