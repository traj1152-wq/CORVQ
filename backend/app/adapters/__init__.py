"""Industry rules operate on validated records and return shared findings."""
from collections import defaultdict
import networkx as nx
from ..models import Finding

VERSIONS = {'banking': 'banking-v1', 'ecommerce': 'ecommerce-v1'}

def validate(industry, records):
    ids = [r.id for r in records]
    if len(ids) != len(set(ids)):
        raise ValueError('Evidence IDs must be unique')
    allowed = {'transfer'} if industry == 'banking' else {'purchase', 'refund'}
    if any(r.kind not in allowed for r in records):
        raise ValueError(f'Invalid record kind for {industry}')
    from datetime import datetime
    for r in records:
        try:
            datetime.fromisoformat(r.timestamp.replace('Z', '+00:00'))
        except ValueError as exc:
            raise ValueError(f'Invalid ISO timestamp for {r.id}') from exc

def analyze(industry, records):
    findings = []
    def add(rule, title, severity, explanation, evidence):
        findings.append(Finding(id=f'{rule}:{len(findings)+1}', title=title, severity=severity,
            explanation=explanation, evidence_ids=sorted(evidence), rule=rule))
    graph = nx.DiGraph()
    for r in records:
        graph.add_edge(r.source, r.target)
    if industry == 'banking':
        for r in records:
            if r.amount >= 100000:
                add('large_transfer', 'High-value transfer', 'medium',
                    f'{r.source} sent INR {r.amount:,.0f} to {r.target}; exceeds the synthetic INR 100,000 review threshold.', [r.id])
        # Bounded-length cycles avoid combinatorial enumeration on uploaded data.
        cycles = list(__import__('itertools').islice(nx.simple_cycles(graph, length_bound=4), 100))
        for cycle in cycles:
            if len(cycle) < 2:
                continue
            pairs = set(zip(cycle, cycle[1:] + cycle[:1]))
            evidence = [r.id for r in records if (r.source, r.target) in pairs]
            add('circular_transfer', 'Circular fund movement', 'high',
                'Directed transfer cycle: ' + ' → '.join(cycle + cycle[:1]) + '. This is a risk indicator, not proof of wrongdoing.', evidence)
    else:
        by_seller = defaultdict(list)
        for r in records:
            if r.kind == 'refund':
                by_seller[r.source].append(r)
        for seller, refunds in by_seller.items():
            if len(refunds) >= 3:
                add('refund_cluster', 'Concentrated refund activity', 'high',
                    f'{seller} issued {len(refunds)} refunds totalling INR {sum(r.amount for r in refunds):,.0f} in this dataset. Synthetic review threshold: 3 refunds.', [r.id for r in refunds])
        pairs = defaultdict(list)
        for r in records:
            if r.kind == 'purchase':
                pairs[(r.source, r.target)].append(r)
        for (buyer, seller), orders in pairs.items():
            if len(orders) >= 3:
                add('repeat_orders', 'Repeated buyer–seller orders', 'medium',
                    f'{buyer} placed {len(orders)} orders with {seller} in this dataset; synthetic review threshold: 3 orders.', [r.id for r in orders])
    return findings
