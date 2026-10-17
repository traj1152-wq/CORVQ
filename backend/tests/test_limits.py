import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from backend.app.limits import RequestLimits

def make_app(**options):
    app=FastAPI()
    app.add_middleware(RequestLimits,**options)
    @app.get('/api/test')
    def sample():return {'ok':True}
    @app.post('/api/test/ai')
    def ai():return {'ok':True}
    return TestClient(app)

def test_request_limit_expires_and_ignores_forwarded_ip():
    now=[0.0]
    client=make_app(requests_per_minute=2,clock=lambda:now[0])
    assert client.get('/api/test').status_code==200
    assert client.get('/api/test').status_code==200
    result=client.get('/api/test',headers={'X-Forwarded-For':'different-client'})
    assert result.status_code==429 and result.headers['retry-after']=='60'
    now[0]=60.1
    assert client.get('/api/test').status_code==200

def test_ai_budget_is_separate():
    client=make_app(ai_per_minute=1)
    assert client.post('/api/test/ai').status_code==200
    assert client.post('/api/test/ai').status_code==429
    assert client.get('/api/test').status_code==200

def test_bounded_uploads_and_security_headers():
    client=make_app(max_bytes=128)
    assert client.post('/api/test/ai',content=b'x'*129).status_code==413
    response=client.get('/api/test')
    assert response.headers['x-content-type-options']=='nosniff'
    assert response.headers['cache-control']=='no-store'

@pytest.mark.anyio
async def test_chunked_upload_without_length_is_rejected():
    called=[];sent=[]
    async def app(scope,receive,send):called.append(True)
    messages=iter([{'type':'http.request','body':b'abcd','more_body':True},{'type':'http.request','body':b'efgh','more_body':False}])
    async def receive():return next(messages)
    async def send(message):sent.append(message)
    limits=RequestLimits(app,max_bytes=5)
    await limits({'type':'http','path':'/api/upload','method':'POST','headers':[],'client':('test',1)},receive,send)
    assert sent[0]['status']==413 and not called

@pytest.fixture
def anyio_backend():return 'asyncio'
