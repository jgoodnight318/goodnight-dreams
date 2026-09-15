#!/usr/bin/env python3
"""Draft a personalised intro email for each enriched prospect. Drafts only: nothing is sent.
Each draft is written to data/outbox/<id>.eml and listed in data/outbox/REVIEW.csv so James can
open the folder, skim, and send the ones he approves from his outreach mailbox (or import the
.eml files into any mail client). Daily cap default 25. CAN-SPAM footer on every draft.

  draft_outreach.py [--limit 25]
Env: RCP_FROM_NAME, RCP_FROM_EMAIL, RCP_POSTAL_ADDRESS, RCP_LANDING_URL
"""
import argparse, csv, os
from email.message import EmailMessage
from common import *

TPL = open(os.path.join(HERE, "templates", "outreach_email.md")).read()

def compose(r):
    prompt = (TPL + "\n\n## Facts (use only these; do not invent anything)\n" + json.dumps({
        "business": r["name"], "category": r["category"], "city": r["city"],
        "landing_url": env("RCP_LANDING_URL", "LANDING_URL"), "from_name": env("RCP_FROM_NAME", "James")}, indent=2)
        + "\n\nReply with ONLY JSON: {\"subject\": \"...\", \"body\": \"...\"}")
    return claude_json(prompt)

def footer():
    return (f"\n\n--\n{env('RCP_FROM_NAME', 'James')} · {env('RCP_POSTAL_ADDRESS', 'POSTAL ADDRESS REQUIRED BY CAN-SPAM')}\n"
            "One-time note; your business contact is publicly listed. Reply STOP and you will not hear from me again.")

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--limit", type=int, default=25); a = ap.parse_args()
    outbox = os.path.join(DATA, "outbox"); os.makedirs(outbox, exist_ok=True)
    review = os.path.join(outbox, "REVIEW.csv"); new_file = not os.path.exists(review)
    rows = load(); n = 0
    with open(review, "a", newline="") as f:
        w = csv.writer(f)
        if new_file:
            w.writerow(["id", "business", "to", "subject", "eml", "drafted_at"])
        for r in rows:
            if n >= a.limit or r["status"] != "enriched" or not r.get("email"):
                continue
            msg = compose(r)
            m = EmailMessage(); m["Subject"] = msg["subject"]; m["To"] = r["email"]
            m["From"] = f"{env('RCP_FROM_NAME', 'James')} <{env('RCP_FROM_EMAIL', 'you@example.com')}>"
            m.set_content(msg["body"] + footer())
            p = os.path.join(outbox, f"{r['id']}.eml"); open(p, "wb").write(bytes(m))
            w.writerow([r["id"], r["name"], r["email"], msg["subject"], p, now()])
            r["status"] = "drafted"; r["drafted_at"] = now(); n += 1
            log(f"drafted -> {r['name']} <{r['email']}>: {msg['subject']}")
    save(rows); log(f"{n} draft(s) in {outbox}")

if __name__ == "__main__":
    main()
