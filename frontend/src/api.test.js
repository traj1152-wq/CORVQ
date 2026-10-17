import test from 'node:test';
import assert from 'node:assert/strict';
import {graphLayout} from './api.js';
test('graph layout preserves directed evidence and handles an empty graph',()=>{
 const graph={nodes:[{id:'A',label:'Account A'},{id:'B',label:'Account B'}],edges:[{id:'TX-1',source:'A',target:'B',label:'INR 100',kind:'transfer'}]};
 const layout=graphLayout(graph);
 assert.equal(layout.nodes[0].data.label,'Account A');
 assert.equal(layout.edges[0].source,'A');assert.equal(layout.edges[0].target,'B');
 assert.ok(Number.isFinite(layout.nodes[1].position.x));
 assert.deepEqual(graphLayout({nodes:[],edges:[]}),{nodes:[],edges:[]});
});

test('request explains network failures, invalid responses, and validation errors',async()=>{
 const {request}=await import('./api.js');
 const originalFetch=globalThis.fetch;
 const originalStorage=globalThis.sessionStorage;
 globalThis.sessionStorage={getItem:()=>null};
 try{
  globalThis.fetch=async()=>{throw new TypeError('Failed to fetch');};
  await assert.rejects(request('/health'),/backend is running on port 8000/);
  globalThis.fetch=async()=>({ok:true,json:async()=>{throw new Error('HTML instead of JSON');}});
  await assert.rejects(request('/health'),/invalid response/);
  globalThis.fetch=async()=>({ok:false,status:422,json:async()=>({detail:[{loc:['body','amount'],msg:'Must be positive'}]})});
  await assert.rejects(request('/investigations'),e=>e.status===422&&e.message==='body.amount: Must be positive');
  globalThis.fetch=async()=>({ok:false,status:401,json:async()=>({detail:'Sign in to continue'})});
  await assert.rejects(request('/me'),e=>e.status===401&&e.message==='Sign in to continue');
 }finally{globalThis.fetch=originalFetch;if(originalStorage===undefined)delete globalThis.sessionStorage;else globalThis.sessionStorage=originalStorage;}
});
