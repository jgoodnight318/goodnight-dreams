#!/usr/bin/env bash
# Goodnight Dreams site — rebuild + push.
#
# "Rebuild" for a static, framework-free site means: validate the data files,
# pull in any newly-shipped single-file tools from the digital_products
# pipeline, then commit and push. GitHub Pages (branch source, "/" on main)
# serves whatever lands on main — no separate build/CI step.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

echo "==> Validating products.json"
python3 -c "import json,sys; json.load(open('products.json'))" \
  || { echo "products.json is not valid JSON — aborting"; exit 1; }

echo "==> Syncing tools/ from the problem-miner output (if present)"
SRC_TOOLS="$HOME/Projects/digital_products/public/tools"
python3 - "$SRC_TOOLS" <<'PY'
import json, os, sys, shutil

src = sys.argv[1]
dst = os.path.join(os.getcwd(), "tools")

entries = []
if os.path.isdir(src):
    for name in sorted(os.listdir(src)):
        if not name.endswith(".html") or name == "index.html":
            continue
        shutil.copy2(os.path.join(src, name), os.path.join(dst, name))
        title = name[:-5].replace("-", " ").replace("_", " ").strip().title()
        entries.append({"file": name, "title": title, "description": ""})

with open(os.path.join(dst, "tools.json"), "w") as f:
    json.dump({"tools": entries}, f, indent=2)
    f.write("\n")

print(f"    {len(entries)} tool(s) synced from {src}" if os.path.isdir(src) else f"    {src} not present, tools.json left empty")
PY

echo "==> git add / commit / push"
git add -A
if git diff --cached --quiet; then
  echo "    nothing to commit"
else
  git commit -m "Deploy: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
  git push
fi

echo "==> Done. Pages will update at:"
echo "    https://jgoodnight318.github.io/goodnight-dreams/"
