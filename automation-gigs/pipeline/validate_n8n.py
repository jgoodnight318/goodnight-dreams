#!/usr/bin/env python3
"""Structural checks only; execution and customer acceptance are separate gates."""
import json,re,sys
from pathlib import Path
SECRET_PATTERNS=[re.compile(r'sk-ant-[A-Za-z0-9_-]{20,}'),re.compile(r'sk-[A-Za-z0-9]{32,}'),re.compile(r'xox[baprs]-[A-Za-z0-9-]{10,}'),re.compile(r'AKIA[0-9A-Z]{16}'),re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),re.compile(r'gh[pousr]_[A-Za-z0-9]{30,}')]
def validate(path):
    try:
        raw=Path(path).read_text();w=json.loads(raw)
    except (ValueError,OSError): return ['Invalid JSON file']
    if not isinstance(w,dict): return ['Top level must be an object']
    errors=[];nodes=w.get('nodes');conns=w.get('connections')
    if not isinstance(nodes,list) or not nodes:return ['nodes must be a nonempty list']
    if not isinstance(conns,dict):return ['connections must be an object']
    if not isinstance(w.get('name'),str) or not w['name']:errors.append('Missing workflow name')
    names=[];types=[]
    for i,n in enumerate(nodes):
        if not isinstance(n,dict):errors.append('Node must be an object');continue
        for key in ['id','name','type','typeVersion','position','parameters']:
            if key not in n:errors.append(f'Node {i} missing {key}')
        if not isinstance(n.get('name'),str):errors.append('Invalid node name');continue
        names.append(n['name']);types.append(str(n.get('type','')))
        if not isinstance(n.get('parameters'),dict):errors.append('Invalid node parameters')
        pos=n.get('position')
        if not isinstance(pos,list) or len(pos)!=2 or any(not isinstance(x,(int,float)) for x in pos):errors.append('Invalid position')
    if len(set(names))!=len(names):errors.append('Duplicate node names')
    for src,outputs in conns.items():
        if src not in names:errors.append('Unknown source node')
        if not isinstance(outputs,dict):errors.append('Invalid connection outputs');continue
        for kind,branches in outputs.items():
            if not isinstance(branches,list):errors.append('Invalid branches');continue
            for branch in branches:
                if not isinstance(branch,list):errors.append('Invalid branch');continue
                for c in branch:
                    if not isinstance(c,dict) or c.get('node') not in names or not isinstance(c.get('index'),int) or c['index']<0 or c.get('type')!=kind:errors.append('Invalid connection target')
    if not any(t.lower().endswith(('trigger','webhook','cron','schedule')) for t in types):errors.append('No recognized trigger node')
    if any(p.search(raw) for p in SECRET_PATTERNS):errors.append('Possible embedded credential')
    return errors
if __name__=='__main__':
    bad=0
    for p in sys.argv[1:]:
        e=validate(p);bad+=bool(e);print(('FAIL ' if e else 'OK ')+p)
        for x in e:print(' - '+x)
    sys.exit(bool(bad))
