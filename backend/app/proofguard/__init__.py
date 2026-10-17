from ..models import Claim

def verify(claim: Claim, records):
    record = next((r for r in records if r.id == claim.evidence_id), None)
    if record is None:
        return {**claim.model_dump(), 'status': 'needs_review', 'actual': None, 'reason': 'Referenced evidence is absent'}
    actual = getattr(record, claim.field)
    if claim.field == 'amount':
        try:
            from decimal import Decimal, InvalidOperation
            supported = Decimal(str(claim.value)) == Decimal(str(actual))
        except (InvalidOperation, ValueError):
            supported = False
    else:
        supported = str(actual) == str(claim.value)
    return {**claim.model_dump(), 'status': 'verified' if supported else 'unsupported',
            'actual': actual, 'reason': 'Exact field match' if supported else 'Claim conflicts with referenced record'}
