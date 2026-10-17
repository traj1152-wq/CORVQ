import copy
import pytest
from fastapi import HTTPException
from backend.app.database.firestore import FirestoreRepository

class Snapshot:
    def __init__(self,key,value): self.id=key.split('/')[-1];self.value=value;self.exists=value is not None
    def to_dict(self):return copy.deepcopy(self.value)
class Collection:
    def __init__(self,db,path):self.db=db;self.path=path;self.sort=None;self.maximum=None
    def document(self,key):return Document(self.db,self.path+'/'+key)
    def order_by(self,field,direction=None):self.sort=field;return self
    def limit(self,n):self.maximum=n;return self
    def stream(self):
        rows=[Snapshot(k,v) for k,v in self.db.data.items() if k.startswith(self.path+'/') and '/' not in k[len(self.path)+1:]]
        rows.sort(key=lambda s:s.to_dict().get(self.sort,''),reverse=self.sort=='created_at')
        return rows[:self.maximum] if self.maximum else rows
class Document:
    def __init__(self,db,path):self.db=db;self.path=path
    def collection(self,key):return Collection(self.db,self.path+'/'+key)
    def get(self,transaction=None):return Snapshot(self.path,self.db.data.get(self.path))
    def create(self,value):
        assert self.path not in self.db.data
        self.db.data[self.path]=copy.deepcopy(value)
class Client:
    def __init__(self):self.data={}
    def collection(self,key):return Collection(self,key)
    def transaction(self):return self
    def set(self,ref,value):self.data[ref.path]=copy.deepcopy(value)

def test_firestore_repository_contract(monkeypatch):
    firestore=pytest.importorskip('google.cloud.firestore')
    monkeypatch.setattr(firestore,'transactional',lambda fn:fn)
    client=Client()
    repo=FirestoreRepository('offline-project','team-one',client)
    other=FirestoreRepository('offline-project','team-two',client)
    case={'id':'case-one','created_at':'2026-10-17T00:00:00Z','records':[{'id':'TX-1'}],'findings':[],'graph':{'edges':[]}}
    repo.save(case)
    assert case['revision']==1
    assert repo.get('case-one')['records']==case['records']
    assert other.get('case-one') is None
    assert 'records' not in repo.list()[0]
    stale=repo.get('case-one');updated=copy.deepcopy(stale)
    updated['status']='clear';repo.save(updated)
    with pytest.raises(HTTPException) as exc:repo.save(stale)
    assert exc.value.status_code==409
    repo.audit('case-one','review',{'actor_uid':'reviewer-1'})
    assert repo.events('case-one')[0]['detail']['actor_uid']=='reviewer-1'
    assert other.events('case-one')==[]
    oversized={**case,'id':'too-large','records':['x'*900000]}
    with pytest.raises(HTTPException) as exc:repo.save(oversized)
    assert exc.value.status_code==413
