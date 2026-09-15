#!/usr/bin/env python3
"""Read-only email intake. Email is a lead signal, never proof of payment."""
import argparse, email, fcntl, hashlib, imaplib, json, os, re, smtplib, sqlite3, sys, time
from datetime import datetime, timedelta
from email.header import decode_header, make_header
from email.message import EmailMessage
from email.utils import parseaddr
from pathlib import Path

PATTERNS = re.compile(r'new order|order requirements|offer (?:was )?accepted|new contract|milestone .*funded', re.I)
DEFAULT_ROOT = Path.home() / '.local/share/automation-gigs'

def load_config():
    path = Path.home() / '.config/automation-gigs.env'
    if path.exists():
        for line in path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                if key.startswith('GIGS_'): os.environ.setdefault(key, value.strip().strip('"').strip("'"))

def clean(value):
    try: return str(make_header(decode_header(str(value or ''))))
    except (LookupError, UnicodeError): return str(value or '')

def platform_for(sender):
    addr = parseaddr(sender)[1].lower()
    domain = addr.rsplit('@',1)[-1]
    for domain_root, name in [('fiverr.com','fiverr'),('upwork.com','upwork')]:
        if domain == domain_root or domain.endswith('.'+domain_root): return name
    # Apple's relay masks Upwork senders. These remain unverified candidates.
    if domain == 'privaterelay.appleid.com' and re.search(r'(^|[._-])upwork[._-]', addr): return 'upwork-relay'
    return None

def body_text(msg):
    plain, html = [], []
    for part in msg.walk():
        if part.get_content_disposition() == 'attachment': continue
        if part.get_content_type() not in ['text/plain','text/html']: continue
        raw = part.get_payload(decode=True)
        if not raw: continue
        try: text = raw.decode(part.get_content_charset() or 'utf-8', 'replace')
        except LookupError: text = raw.decode('utf-8','replace')
        (plain if part.get_content_type() == 'text/plain' else html).append(text)
    return ('\n'.join(plain) or re.sub('<[^>]+>', ' ', '\n'.join(html)))[:60000]

def connect_db(root):
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    db = sqlite3.connect(root / 'intake.sqlite3')
    db.execute('CREATE TABLE IF NOT EXISTS messages (id TEXT PRIMARY KEY, folder TEXT NOT NULL, notified INTEGER DEFAULT 0)')
    return db

def ingest(raw, root, db):
    if len(raw) > 2_000_000: return None
    msg = email.message_from_bytes(raw)
    sender, subject = clean(msg.get('From')), clean(msg.get('Subject'))
    platform = platform_for(sender)
    if not platform or not PATTERNS.search(subject): return None
    # Full digest, independent of read/unread flags and server sequence numbers.
    identity = (str(msg.get('Message-ID')) + sender).encode() if msg.get('Message-ID') else raw
    key = hashlib.sha256(identity).hexdigest()
    if db.execute('SELECT id FROM messages WHERE id=?',(key,)).fetchone(): return None
    folder = root / 'orders' / (platform + '-' + key[:24])
    folder.mkdir(parents=True, exist_ok=True, mode=0o700)
    (folder/'brief.md').write_text('# Unverified email notification\n\n'+subject+'\n\n'+body_text(msg))
    status = {'state':'NEEDS_ORDER_REVIEW', 'subject':subject, 'platform':platform,
              'funding_verified':False, 'scope_reviewed':False, 'received_at':time.time(),
              'next_action':'Open the order on the platform; confirm funded scope and actual requirements. Then replace brief.md and create approval.json.'}
    (folder/'STATUS.json').write_text(json.dumps(status,indent=2))
    db.execute('INSERT INTO messages(id,folder) VALUES (?,?)',(key,str(folder)));db.commit()
    return folder

def notify_pending(db):
    if os.getenv('GIGS_NOTIFY_ENABLED') != '1': return 0
    user, password = os.getenv('GIGS_IMAP_USER'), os.getenv('GIGS_IMAP_PASS')
    recipient = os.getenv('GIGS_NOTIFY_TO',user)
    count=0
    for key, folder in db.execute('SELECT id,folder FROM messages WHERE notified=0').fetchall():
        status=json.loads((Path(folder)/'STATUS.json').read_text())
        m=EmailMessage();m['From']=user;m['To']=recipient;m['Subject']='[gigs] Check new order notification'
        m.set_content('A possible order needs review on the platform.\n\n'+status['subject']+'\n\n'+status['next_action']+'\nLocal folder: '+folder)
        with smtplib.SMTP_SSL('smtp.gmail.com',465,timeout=30) as smtp:
            smtp.login(user,password);smtp.send_message(m)
        db.execute('UPDATE messages SET notified=1 WHERE id=?',(key,));db.commit();count+=1
    return count

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--eml',type=Path,help='Import one downloaded notification without mailbox access')
    parser.add_argument('--check',action='store_true',help='Check configuration without logging in or sending mail')
    args=parser.parse_args();load_config();os.umask(0o077)
    user,password=os.getenv('GIGS_IMAP_USER'),os.getenv('GIGS_IMAP_PASS')
    root=Path(os.getenv('GIGS_DATA_DIR',str(DEFAULT_ROOT)))
    if args.check:
        print(json.dumps({'mail_configured':bool(user and password),'data_dir':str(root),'automatic_paid_builds':False,'notification_enabled':os.getenv('GIGS_NOTIFY_ENABLED')=='1'}));return 0 if user and password else 2
    if not args.eml and not(user and password):
        print('Mailbox not configured; no mail read, no build started.');return 2
    root.mkdir(parents=True,exist_ok=True,mode=0o700)
    with (root/'intake.lock').open('w') as lock:
        try: fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError: return 0
        db=connect_db(root);handled=0
        try:
            if args.eml:
                handled=int(ingest(args.eml.read_bytes(),root,db) is not None)
            else:
                with imaplib.IMAP4_SSL('imap.gmail.com',timeout=30) as mailbox:
                    mailbox.login(user,password)
                    typ,_=mailbox.select('INBOX',readonly=True)
                    if typ != 'OK': raise RuntimeError('Cannot open inbox')
                    since=(datetime.now()-timedelta(days=14)).strftime('%d-%b-%Y')
                    typ,data=mailbox.uid('search',None,'SINCE',since)
                    if typ != 'OK': raise RuntimeError('Cannot search inbox')
                    for uid in data[0].split()[-200:]:
                        typ,parts=mailbox.uid('fetch',uid,'(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT)])')
                        if typ != 'OK': continue
                        header=next((x[1] for x in parts if isinstance(x,tuple)),b'')
                        msg=email.message_from_bytes(header)
                        if not platform_for(clean(msg.get('From'))) or not PATTERNS.search(clean(msg.get('Subject'))): continue
                        typ,parts=mailbox.uid('fetch',uid,'(BODY.PEEK[])')
                        raw=next((x[1] for x in parts if isinstance(x,tuple)),b'')
                        if typ=='OK' and raw: handled+=int(ingest(raw,root,db) is not None)
            sent=notify_pending(db) if not args.eml else 0
            print(json.dumps({'new_candidates':handled,'notifications':sent,'paid_builds_started':0}));return 0
        finally: db.close()
if __name__=='__main__':
    try: sys.exit(main())
    except Exception as exc:
        print('Intake failed: '+type(exc).__name__+'; pending candidates retained.');sys.exit(1)
