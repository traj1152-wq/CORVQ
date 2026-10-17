import json
import logging
import os
import hashlib
import asyncio
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[2] / '.env', override=False)
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from .models import AnalyzeRequest, Claim, CounterfactualRequest, ReviewRequest, Record, Industry
from .core import investigate
from .database import SQLiteRepository, ActorRepository
from .auth import authorize, analyst, reviewer, auth_mode, Principal
from .proofguard import verify
from .samples import samples
from .agents import configuration, run_agents

log = logging.getLogger('corvq')
app = FastAPI(title='CORVQ Investigation API', version='0.1.0')
app.add_middleware(CORSMiddleware, allow_origins=[os.getenv('CORVQ_ORIGIN', 'http://localhost:5173'), 'http://127.0.0.1:5173'], allow_methods=['GET','POST'], allow_headers=['Authorization','Content-Type'])
def repository(principal: Principal = Depends(authorize)):
    storage=os.getenv('CORVQ_STORAGE','sqlite')
    if storage=='firestore':
        project=os.getenv('CORVQ_FIREBASE_PROJECT')
        if not project:
            raise HTTPException(503,'Firestore project is not configured')
        try:
            from .database.firestore import FirestoreRepository
            return ActorRepository(FirestoreRepository(project,principal.workspace),principal)
        except ImportError:
            raise HTTPException(503,'Install backend/requirements-cloud.txt')
    if storage!='sqlite':
        raise HTTPException(503,'Unsupported storage configuration')
    if principal.mode=='firebase':
        path=Path(os.getenv('CORVQ_DB','corvq.db'))
        suffix=hashlib.sha256(principal.workspace.encode()).hexdigest()[:20]
        return ActorRepository(SQLiteRepository(str(path.with_name(path.stem+'-'+suffix+path.suffix))),principal)
    return ActorRepository(SQLiteRepository(),principal)

@app.get('/api/me')
def me(principal: Principal = Depends(authorize)):
    return {'uid':principal.uid,'name':principal.name,'role':principal.role,'workspace':principal.workspace,'mode':principal.mode}

def get_case(identifier, repo):
    case = repo.get(identifier)
    if not case:
        raise HTTPException(404, 'Investigation not found')
    return case

@app.get('/api/health')
def health():
    return {'status': 'ok', 'ai': configuration(), 'authentication': auth_mode(), 'storage':os.getenv('CORVQ_STORAGE','sqlite')}

@app.get('/api/samples/{industry}', dependencies=[Depends(authorize)])
def sample(industry: Industry):
    return {'industry': industry, 'name': f'{industry.title()} · synthetic scenario', 'records': samples(industry), 'synthetic': True}

@app.post('/api/investigations', dependencies=[Depends(analyst)])
def create(body: AnalyzeRequest, repo=Depends(repository)):
    try:
        case = investigate(body.industry, body.records, body.name)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    repo.save(case)
    repo.audit(case['id'], 'analysis_completed', {'rule_version': case['rule_version'], 'records': len(body.records)})
    return case

@app.get('/api/investigations', dependencies=[Depends(authorize)])
def history(repo=Depends(repository)):
    return repo.list()

@app.get('/api/investigations/{identifier}', dependencies=[Depends(authorize)])
def read(identifier: str, repo=Depends(repository)):
    return get_case(identifier, repo)

@app.post('/api/investigations/{identifier}/verify', dependencies=[Depends(analyst)])
def verify_claim(identifier: str, claim: Claim, repo=Depends(repository)):
    case = get_case(identifier, repo)
    result = verify(claim, [Record(**r) for r in case['records']])
    case['claims'].append(result)
    repo.save(case)
    repo.audit(identifier, 'claim_verified', result)
    return result

@app.post('/api/investigations/{identifier}/counterfactual', dependencies=[Depends(analyst)])
def counterfactual(identifier: str, body: CounterfactualRequest, repo=Depends(repository)):
    original = get_case(identifier, repo)
    known = {r['id'] for r in original['records']}
    replacement_ids = [r.id for r in body.replacements]
    if not set(body.remove_ids + replacement_ids) <= known:
        raise HTTPException(422, 'Counterfactual references unknown evidence')
    if len(replacement_ids) != len(set(replacement_ids)) or set(replacement_ids) & set(body.remove_ids):
        raise HTTPException(422, 'Replacements must be unique and cannot also be removed')
    replacements = {r.id: r for r in body.replacements}
    records = [replacements.get(r['id'], Record(**r)) for r in original['records'] if r['id'] not in body.remove_ids]
    if not records:
        raise HTTPException(422, 'Keep at least one record')
    try:
        result = investigate(original['industry'], records, original['name']+' · counterfactual')
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    def signature(f):
        return (f['rule'], tuple(f['evidence_ids']))
    before = {signature(f) for f in original['findings']}
    after = {signature(f) for f in result['findings']}
    result['parent_id'] = identifier
    result['comparison'] = {'before': len(before), 'after': len(after),
        'resolved': [f for f in original['findings'] if signature(f) not in after],
        'introduced': [f for f in result['findings'] if signature(f) not in before],
        'removed_ids': body.remove_ids, 'changed_ids': replacement_ids}
    repo.save(result)
    repo.audit(identifier, 'counterfactual_created', {'child_id': result['id'], **result['comparison']})
    repo.audit(result['id'], 'counterfactual_analysis', {'parent_id': identifier})
    return result

@app.post('/api/investigations/{identifier}/review', dependencies=[Depends(reviewer)])
def review(identifier: str, body: ReviewRequest, repo=Depends(repository), principal: Principal=Depends(reviewer)):
    case = get_case(identifier, repo)
    decision={**body.model_dump(), 'actor_uid':principal.uid}
    if principal.mode=='firebase':
        decision['analyst']=principal.name
    case['reviews'].append(decision)
    case['status'] = body.decision
    repo.save(case)
    repo.audit(identifier, 'human_review', decision)
    return case

@app.get('/api/investigations/{identifier}/audit', dependencies=[Depends(authorize)])
def audit(identifier: str, repo=Depends(repository)):
    get_case(identifier, repo)
    return repo.events(identifier)

@app.post('/api/investigations/{identifier}/ai', dependencies=[Depends(analyst)])
async def ai(identifier: str, repo=Depends(repository)):
    case = get_case(identifier, repo)
    if not configuration()['configured']:
        raise HTTPException(503, 'Gemini unconfigured: install requirements-ai.txt and set GEMINI_API_KEY')
    try:
        output = await asyncio.wait_for(run_agents(case), timeout=180)
    except Exception as exc:
        log.error('AI investigation failed: %s', type(exc).__name__)
        repo.audit(identifier, 'ai_error', {'prompt_version': configuration()['prompt_version']})
        raise HTTPException(502, 'AI workflow failed. Check backend logs; no AI report was saved.')
    case['ai'] = output
    case['claims'].extend(verify(Claim(**c), [Record(**r) for r in case['records']]) for c in output['claims'])
    repo.save(case)
    repo.audit(identifier, 'ai_completed', output['metrics'])
    return case

@app.get('/api/investigations/{identifier}/report', dependencies=[Depends(authorize)])
def report(identifier: str, repo=Depends(repository)):
    case = get_case(identifier, repo)
    case['audit'] = repo.events(identifier)
    return Response(json.dumps(case, indent=2), media_type='application/json', headers={'Content-Disposition': f'attachment; filename="corvq-{identifier}.json"'})


