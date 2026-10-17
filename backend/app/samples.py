"""Explicitly labelled synthetic fixtures, shared by API and exported datasets."""
def samples(industry):
    if industry == 'banking':
        rows = [('TX-001','ACC-1042','ACC-2087',145000),('TX-002','ACC-2087','ACC-3091',142500),('TX-003','ACC-3091','ACC-1042',140000),('TX-004','ACC-4103','ACC-5028',7200),('TX-005','ACC-5028','ACC-6014',3450),('TX-006','ACC-1042','ACC-4103',12500),('TX-007','ACC-6014','ACC-7021',18900),('TX-008','ACC-7021','ACC-5028',5300)]
        return [dict(id=i, source=s, target=t, amount=a, timestamp=f'2026-10-17T{9+n:02}:00:00Z', kind='transfer') for n,(i,s,t,a) in enumerate(rows)]
    rows = [('ORD-001','BUY-100','SELL-201',4200,'purchase'),('ORD-002','BUY-100','SELL-201',4200,'purchase'),('ORD-003','BUY-100','SELL-201',4200,'purchase'),('REF-001','SELL-201','BUY-100',4200,'refund'),('REF-002','SELL-201','BUY-102',3800,'refund'),('REF-003','SELL-201','BUY-103',5600,'refund'),('ORD-004','BUY-104','SELL-202',2300,'purchase'),('ORD-005','BUY-105','SELL-203',8100,'purchase')]
    return [dict(id=i,source=s,target=t,amount=a,timestamp=f'2026-10-17T{9+n:02}:00:00Z',kind=k) for n,(i,s,t,a,k) in enumerate(rows)]
