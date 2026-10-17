import copy
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app import auth
from backend.app.database import SQLiteRepository
from backend.app.samples import samples

@pytest.fixture
def secured(tmp_path,monkeypatch):
    monkeypatch.setenv('CORVQ_AUTH_MODE','firebase')
    monkeypatch.setenv('CORVQ_STORAGE','sqlite')
    monkeypatch.setenv('CORVQ_DB',str(tmp_path/'cases.db'))
    identities={
        'analyst':{'uid':'a','email':'analyst@example.test','email_verified':True,'corvq_role':'analyst','corvq_workspace':'team-one'},
        'reviewer':{'uid':'r','email':'reviewer@example.test','email_verified':True,'corvq_role':'reviewer','corvq_workspace':'team-one'},
        'viewer':{'uid':'v','email':'viewer@example.test','email_verified':True,'corvq_role':'viewer','corvq_workspace':'team-one'},
        'outsider':{'uid':'o','email':'other@example.test','email_verified':True,'corvq_role':'analyst','corvq_workspace':'team-two'}}
    def verify(token):
        if token not in identities: raise ValueError('invalid or revoked token')
        return identities[token]
    monkeypatch.setattr(auth,'verify_firebase_token',verify)
    return TestClient(app),identities

def headers(role): return {'Authorization':'Bearer '+role}

def create(client,role='analyst'):
    response=client.post('/api/investigations',json={'industry':'banking','records':samples('banking')},headers=headers(role))
    assert response.status_code==200,response.text
    return response.json()

def test_firebase_roles_and_verified_review_identity(secured):
    client,_=secured
    case=create(client)
    assert client.get('/api/me',headers=headers('analyst')).json()['uid']=='a'
    body={'decision':'escalate','analyst':'Forged name','note':'Review the source records.'}
    path=f"/api/investigations/{case['id']}/review"
    assert client.post(path,json=body,headers=headers('analyst')).status_code==403
    review=client.post(path,json=body,headers=headers('reviewer'))
    assert review.status_code==200
    assert review.json()['reviews'][0]['analyst']=='reviewer@example.test'
    assert review.json()['reviews'][0]['actor_uid']=='r'
    assert client.post('/api/investigations',json={'industry':'banking','records':samples('banking')},headers=headers('viewer')).status_code==403
    assert client.get(f"/api/investigations/{case['id']}",headers=headers('viewer')).status_code==200

@pytest.mark.parametrize('suffix',['','/audit','/report'])
def test_workspace_isolation(secured,suffix):
    client,_=secured;case=create(client)
    assert client.get(f"/api/investigations/{case['id']}"+suffix,headers=headers('outsider')).status_code==404
    assert client.get('/api/investigations',headers=headers('outsider')).json()==[]

def test_invalid_unverified_and_unassigned_users(secured):
    client,ids=secured
    assert client.get('/api/me').status_code==401
    assert client.get('/api/me',headers=headers('revoked')).status_code==401
    ids['analyst']['email_verified']=False
    assert client.get('/api/me',headers=headers('analyst')).status_code==403
    ids['analyst']['email_verified']=True
    ids['analyst'].pop('corvq_role')
    assert client.get('/api/me',headers=headers('analyst')).status_code==403

def test_sqlite_optimistic_concurrency(tmp_path):
    repo=SQLiteRepository(str(tmp_path/'db.sqlite'))
    case={'id':'one','status':'awaiting_review'}
    repo.save(case)
    first=repo.get('one');second=copy.deepcopy(first)
    first['status']='clear';repo.save(first)
    second['status']='escalate'
    with pytest.raises(HTTPException) as exc:repo.save(second)
    assert exc.value.status_code==409
    assert repo.get('one')['status']=='clear'

def test_cloud_rejects_ephemeral_storage(secured,monkeypatch):
    client,_=secured;monkeypatch.setenv('K_SERVICE','corvq')
    assert client.get('/api/me',headers=headers('analyst')).status_code==503
