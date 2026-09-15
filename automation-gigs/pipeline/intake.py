#!/usr/bin/env python3
"""Poll the inbox for new Fiverr / Upwork orders, fulfill them, notify James.

Runs every 15 min from launchd. Stateless apart from the orders/ folder and
the IMAP \\Seen flag. Standard library only.

Env (put in ~/.config/automation-gigs.env, loaded by the launchd plist):
  GIGS_IMAP_USER   gmail address that receives Fiverr/Upwork mail
  GIGS_IMAP_PASS   gmail App Password (not the account password)
  GIGS_NOTIFY_TO   where to send the "ready to deliver" note (email or SMS gateway)
  GIGS_ORDERS_DIR  default: <repo>/automation-gigs/orders
  GIGS_MODEL       optional claude model override
"""
import email, imaplib, json, os, re, smtplib, subprocess, sys, time, zipfile
from email.header import decode_header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

HERE = os.path.dirname(os.path.abspath(__file__))
ORDERS = os.environ.get("GIGS_ORDERS_DIR", os.path.join(HERE, "..", "orders"))
USER = os.environ.get("GIGS_IMAP_USER")
PASS = os.environ.get("GIGS_IMAP_PASS")
NOTIFY = os.environ.get("GIGS_NOTIFY_TO", USER)
MODEL = os.environ.get("GIGS_MODEL")

# Subject patterns that mean "a buyer has committed money / sent requirements".
ORDER_SUBJECTS = [
    re.compile(r"new order", re.I),                 # Fiverr: "You have a new order from X"
    re.compile(r"order requirements", re.I),        # Fiverr: buyer submitted requirements
    re.compile(r"offer (was )?accepted", re.I),     # Upwork: proposal/offer accepted
    re.compile(r"new contract", re.I),              # Upwork
    re.compile(r"milestone .*funded", re.I),        # Upwork
]
SENDERS = ("fiverr.com", "upwork.com")

def clean(s):
    out = []
    for part, enc in decode_header(s or ""):
        out.append(part.decode(enc or "utf-8", "replace") if isinstance(part, bytes) else part)
    return "".join(out)

def body_text(msg):
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                return part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8", "replace")
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                html = part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8", "replace")
                return re.sub(r"<[^>]+>", " ", html)
        return ""
    return msg.get_payload(decode=True).decode(msg.get_content_charset() or "utf-8", "replace")

def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60]

def notify(subject, text, attach=None):
    m = MIMEMultipart()
    m["From"], m["To"], m["Subject"] = USER, NOTIFY, subject
    m.attach(MIMEText(text, "plain"))
    if attach and os.path.exists(attach):
        part = MIMEBase("application", "zip")
        part.set_payload(open(attach, "rb").read()); encoders.encode_base64(part)
        part.add_header("Content-Disposition", f'attachment; filename="{os.path.basename(attach)}"')
        m.attach(part)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(USER, PASS); s.send_message(m)

def zip_dir(d, out):
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(d):
            for f in files:
                p = os.path.join(root, f); z.write(p, os.path.relpath(p, d))

def fulfill(order_dir):
    cmd = [sys.executable, os.path.join(HERE, "fulfill.py"), order_dir]
    if MODEL: cmd += ["--model", MODEL]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    return r.returncode, r.stdout + r.stderr

def main():
    if not (USER and PASS):
        print("GIGS_IMAP_USER / GIGS_IMAP_PASS not set"); sys.exit(2)
    os.makedirs(ORDERS, exist_ok=True)
    M = imaplib.IMAP4_SSL("imap.gmail.com"); M.login(USER, PASS); M.select("INBOX")
    typ, data = M.search(None, "UNSEEN")
    handled = 0
    for num in data[0].split():
        typ, raw = M.fetch(num, "(BODY.PEEK[])")
        msg = email.message_from_bytes(raw[0][1])
        sender = clean(msg.get("From", "")).lower()
        subject = clean(msg.get("Subject", ""))
        if not any(d in sender for d in SENDERS) or not any(p.search(subject) for p in ORDER_SUBJECTS):
            continue
        platform = "fiverr" if "fiverr" in sender else "upwork"
        mid = re.sub(r"[^a-zA-Z0-9]", "", msg.get("Message-ID", str(time.time())))[-10:]
        order_dir = os.path.join(ORDERS, f"{time.strftime('%Y%m%d')}-{platform}-{slug(subject)}-{mid}")
        if os.path.exists(order_dir):
            M.store(num, "+FLAGS", "\\Seen"); continue
        os.makedirs(order_dir)
        text = body_text(msg)
        with open(os.path.join(order_dir, "brief.md"), "w") as f:
            f.write(f"# {subject}\n\nPlatform: {platform}\nFrom: {sender}\nReceived: {msg.get('Date')}\n\n---\n\n{text}\n")
        M.store(num, "+FLAGS", "\\Seen")
        rc, log = fulfill(order_dir)
        open(os.path.join(order_dir, "fulfill.log"), "w").write(log)
        status = {}
        try: status = json.load(open(os.path.join(order_dir, "STATUS.json")))
        except Exception: pass
        state = status.get("state", "FAILED")
        z = os.path.join(order_dir, "deliverable.zip")
        if os.path.isdir(os.path.join(order_dir, "deliverable")):
            zip_dir(os.path.join(order_dir, "deliverable"), z)
        dm = os.path.join(order_dir, "deliverable", "DELIVERY_MESSAGE.md")
        dmsg = open(dm).read() if os.path.exists(dm) else "(no delivery message produced)"
        qs = status.get("questions_for_buyer") or []
        note = (f"Order: {os.path.basename(order_dir)}\nState: {state}\n\n{status.get('summary','')}\n\n"
                + (("Ask the buyer first:\n- " + "\n- ".join(qs) + "\n\n") if qs else "")
                + "Paste this as the delivery message and attach deliverable.zip:\n\n" + dmsg)
        notify(f"[gigs] {state}: {subject[:60]}", note, z if os.path.exists(z) else None)
        handled += 1
    M.logout()
    print(f"{time.strftime('%H:%M')} handled {handled} new order(s)")

if __name__ == "__main__":
    main()
