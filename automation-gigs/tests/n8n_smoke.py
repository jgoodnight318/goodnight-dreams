"""Import portfolio workflows and run the Shopify graph with external calls stubbed."""
import copy,json,os,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RUNTIME=Path.home()/'.local/share/automation-gigs-runtime/node_modules'
ENV={**os.environ,'PATH':str(RUNTIME/'node/bin')+':'+os.environ['PATH'],'N8N_USER_FOLDER':str(Path.home()/'.local/share/automation-gigs/n8n'),'N8N_DIAGNOSTICS_ENABLED':'false','N8N_VERSION_NOTIFICATIONS_ENABLED':'false'}
BIN=str(RUNTIME/'.bin/n8n')
def call(*args):
 r=subprocess.run([BIN,*args],capture_output=True,text=True,env=ENV,timeout=120)
 if r.returncode:raise RuntimeError('n8n command failed: '+r.stderr[-1000:])
 return r.stdout

def fixture(supplier,qty):
 return {'node':{'title':'Candle','metafield':{'value':supplier},'variants':{'edges':[{'node':{'title':'Blue','sku':'C-'+supplier,'inventoryQuantity':qty}}],'pageInfo':{'hasNextPage':False}}}}

def stub(node,js):
 node['type']='n8n-nodes-base.code';node['typeVersion']=2;node['parameters']={'mode':'runOnceForEachItem','jsCode':js}
 node.pop('credentials',None)

original=json.loads((ROOT/'orders/example-shopify-low-stock-alert/deliverable/shopify-low-stock-slack-report.workflow.json').read_text())
results=[]
with tempfile.TemporaryDirectory(prefix='gigs-n8n-') as td:
 p=Path(td)/'workflow.json'
 for name,payload,expected in [
  ('two-suppliers',{'data':{'products':{'edges':[fixture('A',3),fixture('B',5)],'pageInfo':{'hasNextPage':False}}}},'Post low-stock report'),
  ('empty',{'data':{'products':{'edges':[],'pageInfo':{'hasNextPage':False}}}},'Post all-good message'),
  ('api-error',{'errors':[{'message':'Access denied'}]},'Alert: inventory check failed')]:
  w=copy.deepcopy(original);w['id']='gigs-smoke-'+name;w['name']='SMOKE ONLY '+name
  for n in w['nodes']:
   if n['type']=='n8n-nodes-base.scheduleTrigger':n['type']='n8n-nodes-base.manualTrigger';n['typeVersion']=1;n['parameters']={}
   elif n['name']=='Get products from Shopify':stub(n,'return {json:'+json.dumps(payload)+'};')
   elif n['name']=='Draft reorder email with Claude':stub(n,"return {json:{content:[{text:'Please restock ' + $json.supplier}]}};")
   elif n['type']=='n8n-nodes-base.slack':
    js="return {json:{destination:"+json.dumps(n['name'])+",text:$json.text || ''}};"
    if n['name']=='Post low-stock report':js="if (!$json.text.includes('Supplier: A') || !$json.text.includes('Supplier: B')) throw new Error('Lost supplier'); "+js
    stub(n,js)
  p.write_text(json.dumps(w));call('import:workflow','--input='+str(p))
  out=call('execute','--id='+w['id'],'--rawOutput')
  data=None
  decoder=json.JSONDecoder()
  for i,c in enumerate(out):
   if c=='{':
    try:
     candidate,_=decoder.raw_decode(out[i:])
     if isinstance(candidate,dict) and 'data' in candidate and 'finished' in candidate:data=candidate;break
    except ValueError:pass
  if not data or data.get('status')!='success':raise RuntimeError(name+' failed')
  run=data['data']['resultData']['runData']
  if expected not in run:raise RuntimeError(name+' took the wrong branch')
  results.append({'scenario':name,'expected_final_node':expected,'status':'passed'})
print(json.dumps({'n8n_version':'2.39.5','external_services':'stubbed; no messages sent','results':results},indent=2))
