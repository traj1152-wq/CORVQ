import fixtures from './showcase-data.json' with {type:'json'};
import {liveAIEnabled,investigateWithGemini} from './showcase-ai.js';
import {verifyAtomicClaim} from './ai-report.js';
const cases = new Map();
const events = new Map();
const clone = value => JSON.parse(JSON.stringify(value));
const event = (id, action, detail) => {
  const rows = events.get(id) || [];
  rows.push({seq:rows.length+1, at:new Date().toISOString(), action, detail});
  events.set(id, rows);
};
export async function showcaseRequest(path, options={}) {
  const body = options.body ? JSON.parse(options.body) : {};
  if(path==='/health') return {status:'ok',authentication:'showcase',storage:'browser memory',ai:{configured:liveAIEnabled()}};
  if(path==='/me') return {name:'Demo analyst',role:'showcase',workspace:'synthetic samples'};
  if(path.startsWith('/samples/')) return clone(fixtures[path.split('/').pop()]);
  if(path==='/investigations') {
    if(!options.method) return clone([...cases.values()]);
    const fixture=fixtures[body.industry];
    if(!fixture || JSON.stringify(body.records)!==JSON.stringify(fixture.records)) throw new Error('Showcase mode supports included synthetic samples only.');
    const result=clone(fixture); result.id=crypto.randomUUID(); result.created_at=new Date().toISOString();
    cases.set(result.id,result);event(result.id,'sample_loaded',{mode:'showcase',synthetic:true});return clone(result);
  }
  const [, , id, action] = path.split('/');
  const item=cases.get(id);
  if(!item) throw new Error('Load a synthetic sample to start the showcase.');
  if(action==='audit') return clone(events.get(id)||[]);
  if(action==='report') return clone({...item,audit:events.get(id)||[],showcase:true});
  if(action==='verify') {
    const result=verifyAtomicClaim(body,item.records);
    item.claims.push(result);event(id,'demo_claim_checked',result);return clone(result);
  }
  if(action==='ai') {
    try {
      const report=await investigateWithGemini(clone(item));
      item.ai=report;item.claims.push(...report.claims);event(id,'gemini_report_completed',{model:report.model,prompt_version:report.prompt_version,...report.metrics});
      return clone(item);
    }catch(error){event(id,'gemini_report_failed',{message:error.message});throw error;}
  }
  if(action==='review') {
    item.reviews.push({...body,analyst:body.analyst+' (demo)',at:new Date().toISOString()});
    item.status=body.decision;event(id,'demo_review',{decision:body.decision});return clone(item);
  }
  if(action) throw new Error('This feature requires the full backend. Explore Evidence, ProofGuard, Human review, and report export in this showcase.');
  return clone(item);
}
