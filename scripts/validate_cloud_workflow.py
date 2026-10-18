"""Validate cloud-backed synthetic workflow without minting or bypassing user tokens.

Uses the approved administrator's ADC only to test storage/service functions.
This is not a replacement for an authenticated browser end-to-end test.
"""
import json
import argparse
import os
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[1]/'.env')
from backend.app.database.firestore import FirestoreRepository
from backend.app.main import counterfactual, report
from backend.app.models import CounterfactualRequest

parser=argparse.ArgumentParser()
parser.add_argument('--case-id',required=True)
parser.add_argument('--workspace',default='corvq')
args=parser.parse_args()
repo=FirestoreRepository(os.environ['CORVQ_FIREBASE_PROJECT'],args.workspace)
identifier=args.case_id
case=repo.get(identifier)
if not case:raise SystemExit('Saved synthetic validation case was not found')
if case['industry']!='banking' or len(case['records'])!=8:
    raise SystemExit('Saved validation case differs from the expected synthetic scenario')
child=counterfactual(identifier,CounterfactualRequest(remove_ids=['TX-003']),repo=repo)
restored=FirestoreRepository(os.environ['CORVQ_FIREBASE_PROJECT'],args.workspace).get(child['id'])
original=repo.get(identifier)
assert len(original['records'])==8 and len(restored['records'])==7
assert child['comparison']['before']==5 and child['comparison']['after']==3
assert any(f['rule']=='circular_transfer' for f in child['comparison']['resolved'])
assert any(c['status']=='verified' for c in original['claims'])
assert any(c['status']=='unsupported' for c in original['claims'])
assert original['reviews'] and original['reviews'][0]['actor_uid']
response=report(identifier,repo=repo)
export=json.loads(response.body)
assert export['audit'] and export['reviews'] and export['records']
print(json.dumps({'storage':'firestore','original_preserved':True,'counterfactual_persisted':bool(restored),
    'findings_before':5,'findings_after':3,'proofguard_supported_and_conflicting':True,
    'verified_review_identity_saved':True,'json_report_with_audit':True,'child_id':child['id'],
    'verification_scope':'cloud-backed service functions, not a fresh browser sign-in'}))

