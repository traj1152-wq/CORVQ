from datetime import datetime, timezone
from uuid import uuid4
from ..adapters import analyze, validate, VERSIONS

def investigate(industry, records, name):
    validate(industry, records)
    findings = analyze(industry, records)
    entities = sorted({e for r in records for e in (r.source, r.target)})
    return {'id': str(uuid4()), 'industry': industry, 'name': name,
        'created_at': datetime.now(timezone.utc).isoformat(), 'status': 'awaiting_review',
        'rule_version': VERSIONS[industry], 'records': [r.model_dump() for r in records],
        'findings': [f.model_dump() for f in findings], 'claims': [], 'reviews': [],
        'graph': {'nodes': [{'id': e, 'label': e} for e in entities],
            'edges': [{'id': r.id, 'source': r.source, 'target': r.target, 'label': f'INR {r.amount:,.0f}', 'kind': r.kind} for r in records]},
        'summary': {'records': len(records), 'entities': len(entities), 'findings': len(findings),
            'high_risk': sum(f.severity == 'high' for f in findings), 'total_value': sum(r.amount for r in records)}}
