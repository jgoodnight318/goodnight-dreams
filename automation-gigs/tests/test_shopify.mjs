import {readFileSync} from 'node:fs';
import assert from 'node:assert/strict';
import vm from 'node:vm';
const wf=JSON.parse(readFileSync(new URL('../orders/example-shopify-low-stock-alert/deliverable/shopify-low-stock-slack-report.workflow.json',import.meta.url)));
const nodes=Object.fromEntries(wf.nodes.map(n=>[n.name,n]));
function run(name,json,extra={}) {
 const code=nodes[name].parameters.jsCode;
 return JSON.parse(JSON.stringify(vm.runInNewContext(`(function(){${code}\n})()`,{$json:json,$input:{first:()=>({json})},...extra},{timeout:1000})));
}
const variant=(sku,quantity)=>({node:{title:sku,sku,inventoryQuantity:quantity}});
const product=(supplier,variants)=>({node:{title:'Candle',metafield:{value:supplier},variants:{edges:variants,pageInfo:{hasNextPage:false}}}});
const response=edges=>({data:{products:{edges,pageInfo:{hasNextPage:false}}}});
const flat='Flatten and filter low stock (<10)';
assert.throws(()=>run(flat,{errors:[{message:'denied'}]}));
assert.throws(()=>run(flat,{}));
const paginated=response([]);paginated.data.products.pageInfo.hasNextPage=true;assert.throws(()=>run(flat,paginated));
const vp=response([product('A',[])]);vp.data.products.edges[0].node.variants.pageInfo.hasNextPage=true;assert.throws(()=>run(flat,vp));
assert.throws(()=>run(flat,response([product('A',[variant('null',null)])])));
assert.equal(run(flat,response([]))[0].json.lowStockItems.length,0);
const low=run(flat,response([product('A',[variant('low',3),variant('ok',10)]),product('__proto__',[variant('negative',-1)])]))[0].json;
assert.equal(low.lowStockItems.length,2);
const grouped=run('Group low-stock items by supplier',low);
assert.equal(grouped.length,2);assert.ok(grouped.some(g=>g.json.supplier==='__proto__'));
assert.equal(nodes['Extract Claude draft (with fallback)'].parameters.mode,'runOnceForEachItem');
const reports=grouped.map(g=>run('Extract Claude draft (with fallback)',{content:[{text:'Please restock.'}]},{$:()=>({item:g})}).json);
assert.equal(reports.length,2);assert.equal(reports[1].supplier,'__proto__');
const text=run('Build Slack message',{supplierReports:reports})[0].json.text;
assert.ok(text.includes('\n'));assert.ok(!text.includes('\\n'));assert.ok(text.includes('negative'));
console.log('Shopify logic: 10 scenarios passed (fixtures, no live services).');
