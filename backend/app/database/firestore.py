"""Firestore storage selected explicitly; no resources are provisioned here."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from uuid import uuid4
from fastapi import HTTPException
from . import summary

class FirestoreRepository:
    def __init__(self, project, workspace, client=None):
        if client is None:
            from google.cloud import firestore
            client=firestore.Client(project=project)
        self.client=client
        self.cases=client.collection('workspaces').document(workspace).collection('investigations')

    def save(self, investigation):
        from google.cloud import firestore
        ref=self.cases.document(investigation['id'])
        body=json.dumps(investigation)
        if len(body.encode('utf-8'))>850000:
            raise HTTPException(413,'Investigation exceeds the Firestore document limit; split the dataset')
        expected=investigation.get('revision',0)
        @firestore.transactional
        def commit(transaction):
            snapshot=ref.get(transaction=transaction)
            current=snapshot.to_dict() if snapshot.exists else {}
            if current.get('revision',0)!=expected:
                raise HTTPException(409,'Investigation changed; reload and retry')
            updated={**investigation,'revision':expected+1}
            transaction.set(ref,{'body':json.dumps(updated),'revision':expected+1,
                'created_at':updated['created_at'],'summary':summary(updated)})
        commit(self.client.transaction())
        investigation['revision']=expected+1

    def get(self, identifier):
        snapshot=self.cases.document(identifier).get()
        return json.loads(snapshot.to_dict()['body']) if snapshot.exists else None

    def list(self):
        from google.cloud import firestore
        return [s.to_dict()['summary'] for s in self.cases.order_by('created_at',direction=firestore.Query.DESCENDING).limit(100).stream()]

    def audit(self, identifier, action, detail):
        self.cases.document(identifier).collection('audit').document(str(uuid4())).create({
            'at':datetime.now(timezone.utc).isoformat(),'action':action,'detail':detail})

    def events(self, identifier):
        return [dict(seq=s.id,**s.to_dict()) for s in self.cases.document(identifier).collection('audit').order_by('at').stream()]
