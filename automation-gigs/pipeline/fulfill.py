#!/usr/bin/env python3
"""Build a private, reviewed order; structural validation is never delivery approval."""
import argparse, fcntl, glob, json, os, re, shutil, subprocess, sys, tempfile, time
from pathlib import Path
from validate_n8n import validate, SECRET_PATTERNS
HERE = Path(__file__).resolve().parent
PROMPT = (HERE / "prompts/fulfillment.md").read_text()

def atomic_json(path, value):
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(value, indent=2))
    temp.replace(path)

def parse_files_json(text):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)
    obj = json.loads(text)
    if not isinstance(obj, dict) or not isinstance(obj.get("files"), dict):
        raise ValueError("Response must contain a files object")
    if obj.get("status") not in {"READY", "NEEDS_INFO"}:
        raise ValueError("Invalid response status")
    if not isinstance(obj.get("questions_for_buyer", []), list):
        raise ValueError("questions_for_buyer must be a list")
    return obj

def write_files(files, out_dir):
    root = Path(out_dir).resolve()
    if len(files) > 100:
        raise ValueError("More than 100 files")
    total = 0
    for rel, content in files.items():
        name = Path(rel)
        if not rel or name.is_absolute() or ".." in name.parts or "\\" in rel:
            raise ValueError("Unsafe output path")
        dest = root / name
        if not dest.resolve().is_relative_to(root) or dest.is_symlink():
            raise ValueError("Output escapes delivery directory")
        if not isinstance(content, str):
            content = json.dumps(content, indent=2)
        total += len(content.encode())
        if total > 10_000_000:
            raise ValueError("Deliverable exceeds 10 MB")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content)

def validate_all(out_dir, kind="n8n"):
    root = Path(out_dir)
    errors = []
    for required in ["README.md", "TESTING.md", "DELIVERY_MESSAGE.md"]:
        if not (root / required).is_file() or not (root / required).read_text().strip():
            errors.append("Missing " + required)
    wfs = list(root.rglob("*.workflow.json"))
    if kind == "n8n" and not wfs:
        errors.append("No workflow file produced")
    for wf in wfs:
        errors.extend(str(wf.relative_to(root)) + ": " + e for e in validate(wf))
    for file in root.rglob("*"):
        if file.is_symlink():
            errors.append("Symlink in deliverable")
        elif file.is_file():
            raw = file.read_text(errors="replace")
            if any(p.search(raw) for p in SECRET_PATTERNS):
                errors.append(str(file.relative_to(root)) + ": possible embedded credential")
    return not errors, errors

def run_claude(prompt, model, budget):
    # The buyer brief is untrusted data. No shell, file, network, MCP or plugin tools.
    cmd = ["claude", "-p", "--output-format", "json", "--tools", "", "--strict-mcp-config",
           "--mcp-config", '{"mcpServers":{}}', "--disable-slash-commands",
           "--no-session-persistence", "--permission-mode", "dontAsk",
           "--setting-sources", "", "--settings", '{"disableAllHooks":true}',
           "--max-budget-usd", str(budget)]
    if model:
        cmd += ["--model", model]
    start = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="gigs-build-") as cwd:
        r = subprocess.run(cmd, input=prompt, text=True, capture_output=True, cwd=cwd, timeout=900)
    if r.returncode:
        raise RuntimeError("Claude build failed; exit " + str(r.returncode))
    result = json.loads(r.stdout)
    if result.get("is_error"):
        raise RuntimeError("Claude reported an unsuccessful build")
    return result.get("result", ""), round(time.monotonic()-start, 2), result.get("total_cost_usd")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("order_dir", type=Path)
    parser.add_argument("--mock", action="store_true")
    parser.add_argument("--model", default=os.getenv("GIGS_MODEL", "sonnet"))
    args = parser.parse_args()
    order = args.order_dir.resolve()
    order.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.umask(0o077)
    with (order / ".build.lock").open("w") as lock:
        try: fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print("Build already running"); return 2
        status = {"state": "BUILDING", "started": time.time(), "passes": [], "live_services_tested": False}
        try:
            brief = (order / "brief.md").read_text()
            approval = {} if args.mock else json.loads((order / "approval.json").read_text())
            if not args.mock and not (approval.get("funding_verified") is True and approval.get("scope_reviewed") is True and approval.get("platform_order_url")):
                raise ValueError("Verify the funded order and scope in approval.json first")
            budget = float(approval.get("max_build_cost_usd", 0))
            if not args.mock and not (0 < budget <= 10):
                raise ValueError("Set a total build budget between $0 and $10")
            kind = approval.get("kind", "n8n")
            atomic_json(order / "STATUS.json", status)
            with tempfile.TemporaryDirectory(prefix=".staging-", dir=order) as staging:
                out = Path(staging)
                if args.mock:
                    shutil.copytree(HERE.parent / "portfolio/lead-qualifier", out, dirs_exist_ok=True)
                    (out / "DELIVERY_MESSAGE.md").write_text("Synthetic plumbing test; do not deliver.\n")
                    obj = {"status":"READY", "summary":"Synthetic plumbing test", "questions_for_buyer":[]}
                    ok, errors = validate_all(out, kind)
                else:
                    prompt = PROMPT + "\n\n<untrusted_buyer_brief>\n" + brief[:60000] + "\n</untrusted_buyer_brief>"
                    previous = ""
                    for attempt in range(2):
                        text, secs, cost = run_claude(prompt + previous, args.model, budget / 2)
                        status["passes"].append({"seconds":secs, "cost_usd":cost})
                        try:
                            obj = parse_files_json(text)
                            for child in out.iterdir():
                                shutil.rmtree(child) if child.is_dir() else child.unlink()
                            write_files(obj["files"], out)
                            ok, errors = validate_all(out, kind)
                        except (ValueError, TypeError) as exc:
                            ok, errors = False, [str(exc)]
                        if ok: break
                        previous = "\n\nRepair these errors and return ALL files: " + json.dumps(errors) + "\nPrevious output:\n" + text[:80000]
                    if not ok:
                        obj = {"status":"NEEDS_INFO", "summary":"Build failed validation", "questions_for_buyer":[]}
                status.update({"state":"MOCK_PASSED" if args.mock and ok else "NEEDS_REVIEW" if ok and obj["status"] == "READY" and not obj.get("questions_for_buyer") else "NEEDS_INFO" if ok else "FAILED_VALIDATION",
                               "summary":obj.get("summary", ""), "questions_for_buyer":obj.get("questions_for_buyer", []),
                               "validation_errors":errors, "files":sorted(str(f.relative_to(out)) for f in out.rglob("*") if f.is_file())})
                if ok:
                    delivery = order / "deliverable"
                    if delivery.exists():
                        delivery.rename(order / ("previous-deliverable-" + str(time.time_ns())))
                    shutil.copytree(out, delivery)
            status["finished"] = time.time()
        except Exception as exc:
            status.update(state="FAILED", error=str(exc), finished=time.time())
        atomic_json(order / "STATUS.json", status)
        print(json.dumps(status, indent=2))
        return 0 if status["state"] in {"NEEDS_REVIEW", "NEEDS_INFO", "MOCK_PASSED"} else 1
if __name__ == "__main__":
    sys.exit(main())
