import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.samples import samples
from backend.app.models import Record, Claim
from backend.app.proofguard import verify
from backend.app.core import investigate

@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv('CORVQ_DB', str(tmp_path/'test.db'))
    monkeypatch.delenv('CORVQ_API_TOKEN', raising=False)
    monkeypatch.delenv('GEMINI_API_KEY', raising=False)
    return TestClient(app)

def create(client, industry='banking'):
    response=client.post('/api/investigations',json={'industry':industry,'records':samples(industry)})
    assert response.status_code==200, response.text
    return response.json()

@pytest.mark.parametrize('industry,rule',[('banking','circular_transfer'),('ecommerce','refund_cluster')])
def test_adapters(client,industry,rule):
    case=create(client,industry)
    assert any(f['rule']==rule for f in case['findings'])
    assert len(case['graph']['edges'])==len(case['records'])
    assert set(e['id'] for e in case['graph']['edges'])==set(r['id'] for r in case['records'])
    known={r['id'] for r in case['records']}
    assert all(set(f['evidence_ids'])<=known for f in case['findings'])

def test_cycle_counterfactual_persists_original(client):
    original=create(client)
    result=client.post(f"/api/investigations/{original['id']}/counterfactual",json={'remove_ids':['TX-003']})
    assert result.status_code==200
    child=result.json()
    # The unrelated three-account cycle remains; only the target cycle disappears.
    assert any('TX-003' in f['evidence_ids'] for f in child['comparison']['resolved'])
    assert not any('TX-003' in f['evidence_ids'] for f in child['findings'])
    assert len(client.get(f"/api/investigations/{original['id']}").json()['records'])==8
    assert child['parent_id']==original['id']

def test_ecommerce_counterfactual(client):
    case=create(client,'ecommerce')
    child=client.post(f"/api/investigations/{case['id']}/counterfactual",json={'remove_ids':['REF-003']}).json()
    assert not any(f['rule']=='refund_cluster' for f in child['findings'])
    assert any(f['rule']=='repeat_orders' for f in child['findings'])

@pytest.mark.parametrize('value,evidence,status',[(145000,'TX-001','verified'),('145000','TX-001','verified'),(50000,'TX-001','unsupported'),(145000,'MISSING','needs_review'),('not a number','TX-001','unsupported')])
def test_proofguard(value,evidence,status):
    result=verify(Claim(evidence_id=evidence,field='amount',value=value,text='Amount assertion'),[Record(**r) for r in samples('banking')])
    assert result['status']==status
    assert result['evidence_id']==evidence

def test_conflicting_source():
    result=verify(Claim(evidence_id='TX-001',field='source',value='OTHER',text='Source assertion'),[Record(**r) for r in samples('banking')])
    assert result['status']=='unsupported' and result['actual']=='ACC-1042'

def test_review_audit_report(client):
    case=create(client)
    base=f"/api/investigations/{case['id']}"
    response=client.post(base+'/review',json={'analyst':'Test Analyst','decision':'escalate','note':'Review circular transfer evidence.'})
    assert response.json()['status']=='escalate'
    assert client.get(base).json()['reviews'][0]['analyst']=='Test Analyst'
    assert client.get(base+'/audit').json()[-1]['action']=='human_review'
    report=client.get(base+'/report')
    assert report.status_code==200 and report.json()['audit']
    assert client.get('/api/investigations').json()[0]['id']==case['id']

def test_validation_and_auth(client,monkeypatch):
    rows=samples('banking');rows[1]['id']=rows[0]['id']
    assert client.post('/api/investigations',json={'industry':'banking','records':rows}).status_code==422
    rows=samples('banking');rows[0]['amount']=-1
    assert client.post('/api/investigations',json={'industry':'banking','records':rows}).status_code==422
    assert client.post('/api/investigations',json={'industry':'ecommerce','records':samples('banking')}).status_code==422
    monkeypatch.setenv('CORVQ_API_TOKEN','test-secret')
    assert client.get('/api/investigations').status_code==401
    assert client.get('/api/investigations',headers={'Authorization':'Bearer test-secret'}).status_code==200

def test_counterfactual_replacements(client):
    case=create(client)
    changed={**case['records'][0], 'amount':500}
    child=client.post(f"/api/investigations/{case['id']}/counterfactual",json={'replacements':[changed]}).json()
    assert not any(f['rule']=='large_transfer' and 'TX-001' in f['evidence_ids'] for f in child['findings'])

def test_unconfigured_ai_is_honest(client):
    case=create(client)
    assert client.post(f"/api/investigations/{case['id']}/ai").status_code==503
    assert 'ai' not in client.get(f"/api/investigations/{case['id']}").json()

def test_invalid_evidence_and_missing_case(client):
    case=create(client)
    base=f"/api/investigations/{case['id']}"
    assert client.post(base+'/counterfactual',json={'remove_ids':['MISSING']}).status_code==422
    assert client.post(base+'/counterfactual',json={'remove_ids':[r['id'] for r in case['records']]}).status_code==422
    assert client.get('/api/investigations/missing').status_code==404
    rows=samples('banking');rows[0]['timestamp']='bad-date'
    assert client.post('/api/investigations',json={'industry':'banking','records':rows}).status_code==422

def test_no_findings_is_valid(client):
    row={**samples('banking')[0],'amount':100}
    case=client.post('/api/investigations',json={'industry':'banking','records':[row]}).json()
    assert case['findings']==[]

def test_cloud_auth_fail_closed(client,monkeypatch):
    monkeypatch.setenv('K_SERVICE','corvq')
    assert client.get('/api/investigations').status_code==503

def test_ai_endpoint_verifies_generated_claims(client,monkeypatch):
    import backend.app.main as main
    monkeypatch.setattr(main,'configuration',lambda: {'configured':True})
    async def fake_workflow(case):
        return {'summary':'Offline integration fixture','hypotheses':[], 'recommendations':[],
            'claims':[{'evidence_id':'TX-001','field':'amount','value':145000,'text':'Supported amount'},
                      {'evidence_id':'TX-001','field':'amount','value':1,'text':'Conflicting amount'}],
            'metrics':{'model':'offline-fixture','latency_ms':1,'prompt_version':'test'}}
    monkeypatch.setattr(main,'run_agents',fake_workflow)
    case=create(client)
    result=client.post(f"/api/investigations/{case['id']}/ai")
    assert result.status_code==200
    assert [c['status'] for c in result.json()['claims']]==['verified','unsupported']
    assert client.get(f"/api/investigations/{case['id']}/audit").json()[-1]['action']=='ai_completed'
