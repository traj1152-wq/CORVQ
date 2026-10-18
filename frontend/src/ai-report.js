const fields = ['amount','source','target','kind'];
export function verifyAtomicClaim(claim, records) {
  const row=records.find(record=>record.id===claim.evidence_id);
  const supported=fields.includes(claim.field);
  const actual=row && supported ? row[claim.field] : null;
  const amount=typeof claim.value==='string' && claim.value.trim()!=='' ? Number(claim.value) : NaN;
  const matches=claim.field==='amount' ? Number.isFinite(amount)&&amount===actual : claim.value===actual;
  return {...claim,actual,status:!row||!supported?'needs_review':matches?'verified':'unsupported',
    reason:!row||!supported?'Source record or supported field unavailable.':matches?'Exact match with the supplied synthetic source record.':'Claim conflicts with the supplied synthetic source record.'};
}
export function validateAIReport(report, records) {
  const strings=(value,max)=>Array.isArray(value)&&value.length<=max&&value.every(s=>typeof s==='string'&&s.length>0&&s.length<=2000);
  if(!report || typeof report.summary!=='string' || !report.summary.trim() || report.summary.length>5000 ||
     !strings(report.hypotheses,6)||!strings(report.limitations,6)||!Array.isArray(report.claims)||report.claims.length<1||report.claims.length>8)
    throw new Error('Gemini returned an incomplete report. No report was saved.');
  for(const claim of report.claims) {
    if(!claim || typeof claim.evidence_id!=='string' || !fields.includes(claim.field) ||
       typeof claim.value!=='string' || claim.value.length>200 || typeof claim.text!=='string'||!claim.text.trim()||claim.text.length>1000)
      throw new Error('Gemini returned an invalid factual claim. No report was saved.');
  }
  // Model-supplied verification labels are never trusted.
  return {summary:report.summary,hypotheses:report.hypotheses,limitations:report.limitations,
    claims:report.claims.map(({evidence_id,field,value,text})=>verifyAtomicClaim({evidence_id,field,value,text},records))};
}
