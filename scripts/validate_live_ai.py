"""Explicit live AI validation for an existing synthetic fixture only.

Uses Gemini API quota and approved ADC to persist its result. Does not mint user tokens.
"""
import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[1]/'.env')
from backend.app.agents import run_agents
from backend.app.database.firestore import FirestoreRepository
from backend.app.models import Claim,Record
from backend.app.proofguard import verify
from backend.app.samples import samples

parser=argparse.ArgumentParser()
parser.add_argument('--case-id',required=True)
parser.add_argument('--workspace',default='corvq')
args=parser.parse_args()

async def main():
    repo=FirestoreRepository(os.environ['CORVQ_FIREBASE_PROJECT'],args.workspace)
    case=repo.get(args.case_id)
    if not case or case['records']!=samples(case['industry']):
        raise SystemExit('This tool only runs on the exact included synthetic fixture')
    try:
        output=await asyncio.wait_for(run_agents(case),timeout=300)
        records=[Record(**r) for r in case['records']]
        checks=[verify(Claim(**c),records) for c in output['claims']]
        case['ai']=output
        case['claims'].extend(checks)
        repo.save(case)
        repo.audit(case['id'],'ai_validation_completed',{'execution':'approved-backend-validation',**output['metrics']})
        saved=FirestoreRepository(os.environ['CORVQ_FIREBASE_PROJECT'],args.workspace).get(case['id'])
        print(json.dumps({'success':True,'persisted':bool(saved.get('ai')),'claims':len(checks),
            'verified':sum(c['status']=='verified' for c in checks),
            'unsupported':sum(c['status']=='unsupported' for c in checks),
            'needs_review':sum(c['status']=='needs_review' for c in checks),
            'metrics':output['metrics']}))
    except Exception as exc:
        print(json.dumps({'success':False,'error_type':type(exc).__name__,'provider_code':getattr(exc,'code',None)}))
        raise SystemExit(1)

asyncio.run(main())
