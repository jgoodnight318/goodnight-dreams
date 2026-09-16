#!/usr/bin/env python3
"""Install this checkout's launch agent only when mail credentials are configured."""
import argparse,json,os,plistlib,subprocess,sys
from pathlib import Path
from intake import load_config
p=argparse.ArgumentParser();p.add_argument('--enable',action='store_true');args=p.parse_args()
load_config()
root=Path.home()/'.local/share/automation-gigs';root.mkdir(parents=True,exist_ok=True,mode=0o700)
logs=root/'logs';logs.mkdir(exist_ok=True)
script=Path(__file__).resolve().with_name('intake.py')
config={'Label':'com.james.automation-gigs','ProgramArguments':[sys.executable,str(script)],'StartInterval':900,'RunAtLoad':True,'WorkingDirectory':str(script.parent),'StandardOutPath':str(logs/'intake.out.log'),'StandardErrorPath':str(logs/'intake.err.log'),'ProcessType':'Background'}
prepared=root/'com.james.automation-gigs.plist';prepared.write_bytes(plistlib.dumps(config))
configured=bool(os.getenv('GIGS_IMAP_USER') and os.getenv('GIGS_IMAP_PASS'))
if not args.enable:
 print(json.dumps({'prepared':str(prepared),'mail_configured':configured,'loaded':False}));sys.exit(0)
if not configured:
 print('Prepared launch agent; not loaded because mailbox credentials are missing.');sys.exit(2)
agent=Path.home()/'Library/LaunchAgents'/prepared.name
if agent.exists():
 print('Existing launch agent found; inspect before replacing.');sys.exit(2)
agent.write_bytes(prepared.read_bytes())
subprocess.run(['launchctl','bootstrap','gui/'+str(os.getuid()),str(agent)],check=True)
print('Installed read-only order intake every 15 minutes. Paid builds require a verified order.')
