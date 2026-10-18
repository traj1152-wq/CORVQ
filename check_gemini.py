import asyncio
import json
from dotenv import load_dotenv
load_dotenv()
from backend.app.agents import run_agents
from backend.app.core import investigate
from backend.app.models import Record, Claim
from backend.app.samples import samples
from backend.app.proofguard import verify

async def main():
    records=[Record(**r) for r in samples('banking')]
    case=investigate('banking',records,'Gemini connection validation')
    try:
        result=await asyncio.wait_for(run_agents(case),timeout=300)
        checks=[verify(Claim(**c),records) for c in result['claims']]
        print(json.dumps({'success':True,'summary':result['summary'],'claim_count':len(checks),'verified':sum(c['status']=='verified' for c in checks),'unsupported':sum(c['status']=='unsupported' for c in checks),'metrics':result['metrics']}))
    except Exception as exc:
        code=getattr(exc,'code',None)
        print(json.dumps({'success':False,'error_type':type(exc).__name__,'code':str(code) if code else None,'message':str(getattr(exc,'message',str(exc))).replace(__import__('os').environ['GEMINI_API_KEY'],'[REDACTED]')}))
        raise SystemExit(1)
asyncio.run(main())
