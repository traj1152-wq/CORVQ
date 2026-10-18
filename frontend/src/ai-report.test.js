import test from 'node:test';
import assert from 'node:assert/strict';
import {validateAIReport,verifyAtomicClaim} from './ai-report.js';
const records=[{id:'TX-001',amount:145000,source:'A',target:'B',kind:'transfer'}];
test('AI claims use source evidence, ignoring model-supplied verification labels',()=>{
  const result=validateAIReport({summary:'Synthetic transfer for review.',hypotheses:[],limitations:['Synthetic data only.'],claims:[
    {evidence_id:'TX-001',field:'amount',value:'50000',text:'Wrong amount',status:'verified'},
    {evidence_id:'TX-001',field:'amount',value:'145000',text:'Exact amount'},
    {evidence_id:'MISSING',field:'source',value:'A',text:'Unknown source'}]},records);
  assert.deepEqual(result.claims.map(c=>c.status),['unsupported','verified','needs_review']);
  assert.equal(result.claims[0].actual,145000);
});
test('incomplete or malformed model reports never become saved reports',()=>{
  for(const value of [null,{}, {summary:'x',hypotheses:[],limitations:[],claims:[]},
    {summary:'x',hypotheses:[],limitations:[],claims:[{evidence_id:'TX-001',field:'amount',value:145000,text:'x'}]}])
    assert.throws(()=>validateAIReport(value,records),/No report was saved/);
  assert.equal(verifyAtomicClaim({evidence_id:'TX-001',field:'amount',value:'',text:'Empty'},records).status,'unsupported');
});
