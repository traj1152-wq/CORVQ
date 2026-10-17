"""ASGI request limits. Forwarded headers are deliberately not trusted."""
import os
import time
from collections import deque
from threading import Lock
from starlette.responses import JSONResponse

class RequestLimits:
    def __init__(self, app, max_bytes=None, requests_per_minute=None, ai_per_minute=None, clock=time.monotonic):
        self.app=app
        self.max_bytes=max_bytes or int(os.getenv('CORVQ_MAX_REQUEST_BYTES','2097152'))
        self.limit=requests_per_minute or int(os.getenv('CORVQ_REQUESTS_PER_MINUTE','120'))
        self.ai_limit=ai_per_minute or int(os.getenv('CORVQ_AI_REQUESTS_PER_MINUTE','5'))
        self.clock=clock
        self.buckets={}
        self.lock=Lock()

    def allowed(self, key, limit):
        now=self.clock()
        with self.lock:
            if key not in self.buckets and len(self.buckets)>=10000:
                self.buckets={k:v for k,v in self.buckets.items() if v and now-v[-1]<60}
                if len(self.buckets)>=10000:return False
            bucket=self.buckets.setdefault(key,deque())
            while bucket and now-bucket[0]>=60:bucket.popleft()
            if len(bucket)>=limit:return False
            bucket.append(now)
        return True

    async def __call__(self, scope, receive, send):
        if scope['type']!='http':
            return await self.app(scope,receive,send)
        async def reject(status,detail,headers=None):
            await JSONResponse({'detail':detail},status_code=status,headers=headers)(scope,receive,send)
        headers=dict(scope.get('headers',[]))
        try:
            length=int(headers.get(b'content-length',b'0'))
            if length<0:raise ValueError()
        except ValueError:
            return await reject(400,'Invalid Content-Length')
        if length>self.max_bytes:return await reject(413,'Upload too large; maximum request size is 2 MiB by default')
        if scope.get('path','').startswith('/api/') and scope.get('path')!='/api/health' and scope.get('method')!='OPTIONS':
            peer=(scope.get('client') or ('unknown',0))[0]
            if not self.allowed(('all',peer),self.limit):
                return await reject(429,'Too many requests; retry in one minute',{'Retry-After':'60'})
            if scope['method']=='POST' and scope['path'].endswith('/ai') and not self.allowed(('ai',peer),self.ai_limit):
                return await reject(429,'AI request limit reached; retry in one minute',{'Retry-After':'60'})
        # Buffer a strictly bounded body before routing, including chunked uploads.
        body=bytearray()
        while True:
            message=await receive()
            if message['type']=='http.disconnect':return
            body.extend(message.get('body',b''))
            if len(body)>self.max_bytes:return await reject(413,'Upload too large; split the dataset')
            if not message.get('more_body',False):break
        delivered=False
        async def replay():
            nonlocal delivered
            if not delivered:
                delivered=True
                return {'type':'http.request','body':bytes(body),'more_body':False}
            return await receive()
        async def secure_send(message):
            if message['type']=='http.response.start':
                message={**message,'headers':list(message.get('headers',[]))+[(b'x-content-type-options',b'nosniff'),(b'referrer-policy',b'no-referrer'),(b'cache-control',b'no-store')]}
            await send(message)
        await self.app(scope,replay,secure_send)
