#!/usr/bin/env python3
"""Turn keyworded images into marketplace upload batches.

  export.py <images_dir> --target adobe|freepik|vecteezy --out <batch_dir>

adobe:    copies images + writes adobe.csv (Filename,Title,Keywords,Category,Releases) matching the
          Adobe Stock contributor CSV template; upload the folder by SFTP (see README), then in the
          contributor portal tick "Created using generative AI tools" (the CSV cannot set it).
freepik:  copies images + writes freepik.csv (filename,title,keywords,ai_generated) for bulk import.
vecteezy: copies images + writes vecteezy.csv (filename,title,keywords).
Images already exported to a target are recorded in <images_dir>/.exported.json and skipped.
"""
import argparse, csv, glob, json, os, shutil

ADOBE_CAT_ID = {"Abstract": 1, "Backgrounds": 11, "Business": 3, "Landscapes": 8, "Lifestyle": 9, "Nature": 12,
                "Technology": 16, "Travel": 18, "Science": 14, "Graphic Resources": 7, "The Environment": 21, "States of Mind": 15}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("images_dir"); ap.add_argument("--target", required=True, choices=["adobe", "freepik", "vecteezy"])
    ap.add_argument("--out", required=True); a = ap.parse_args()
    ledger_p = os.path.join(a.images_dir, ".exported.json")
    ledger = json.load(open(ledger_p)) if os.path.exists(ledger_p) else {}
    os.makedirs(a.out, exist_ok=True)
    rows = []
    for side in sorted(glob.glob(os.path.join(a.images_dir, "*.json"))):
        base = os.path.splitext(side)[0]
        img = next((base + e for e in (".jpg", ".jpeg", ".png") if os.path.exists(base + e)), None)
        if not img or a.target in ledger.get(os.path.basename(img), []):
            continue
        d = json.load(open(side)); fn = os.path.basename(img)
        shutil.copy2(img, os.path.join(a.out, fn))
        kw = ", ".join(d["keywords"])
        if a.target == "adobe":
            rows.append([fn, d["title"], kw, ADOBE_CAT_ID.get(d.get("category"), 11), ""])
        elif a.target == "freepik":
            rows.append([fn, d["title"], kw, "true"])
        else:
            rows.append([fn, d["title"], kw])
        ledger.setdefault(fn, []).append(a.target)
    header = {"adobe": ["Filename", "Title", "Keywords", "Category", "Releases"],
              "freepik": ["filename", "title", "keywords", "ai_generated"],
              "vecteezy": ["filename", "title", "keywords"]}[a.target]
    with open(os.path.join(a.out, f"{a.target}.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(header); w.writerows(rows)
    json.dump(ledger, open(ledger_p, "w"), indent=2)
    print(f"{a.target}: {len(rows)} asset(s) staged in {a.out}")

if __name__ == "__main__":
    main()
