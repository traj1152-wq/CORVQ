"""Publish only static showcase assets to Firebase Hosting, without billing changes."""
import gzip
import hashlib
import json
import subprocess
from pathlib import Path
import requests

root=Path(__file__).resolve().parents[1]
billing=json.loads(subprocess.check_output([str(root/'.tools/google-cloud-sdk/bin/gcloud.cmd'),'billing','projects','describe','corvq-493d5','--format=json'],text=True))
if billing.get('billingEnabled') or billing.get('billingAccountName'):
    raise RuntimeError('Free prototype deployment requires project billing to remain disabled.')
token=subprocess.check_output([str(root/'.tools/google-cloud-sdk/bin/gcloud.cmd'),'auth','print-access-token'],text=True).strip()
session=requests.Session()
session.headers['Authorization']='Bearer '+token
session.headers['x-goog-user-project']='corvq-493d5'
base='https://firebasehosting.googleapis.com/v1beta1'
site='sites/corvq-493d5'
def call(method,url,**kwargs):
    response=session.request(method,url,timeout=120,**kwargs)
    if not response.ok:
        raise RuntimeError(f'Hosting request failed {response.status_code}: {response.text[:1500]}')
    return response.json() if response.content else {}
version=call('POST',f'{base}/{site}/versions',json={'config':{'rewrites':[{'glob':'**','path':'/index.html'}]}})['name']
files={};blobs={}
for path in (root/'frontend/dist').rglob('*'):
    if path.is_file():
        data=gzip.compress(path.read_bytes(),mtime=0);digest=hashlib.sha256(data).hexdigest()
        files['/'+path.relative_to(root/'frontend/dist').as_posix()]=digest;blobs[digest]=data
population=call('POST',f'{base}/{version}:populateFiles',json={'files':files})
for digest in population.get('uploadRequiredHashes',[]):
    call('POST',population['uploadUrl']+'/'+digest,data=blobs[digest],headers={'Content-Type':'application/octet-stream'})
call('PATCH',f'{base}/{version}?updateMask=status',json={'status':'FINALIZED'})
call('POST',f'{base}/{site}/releases',params={'versionName':version},json={})
print('Published https://corvq-493d5.web.app')
