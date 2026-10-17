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
