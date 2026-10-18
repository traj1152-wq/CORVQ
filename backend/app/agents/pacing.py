"""Process-local model-call pacing for multi-agent free-tier compatibility."""
import asyncio
import os
import time
from threading import Lock

class ModelPacer:
    def __init__(self,clock=time.monotonic):
        self.clock=clock
        self.next_slot=0.0
        self.lock=Lock()
    def reserve(self,requests_per_minute):
        interval=60/max(1,requests_per_minute)
        with self.lock:
            now=self.clock()
            slot=max(now,self.next_slot)
            self.next_slot=slot+interval
        return max(0,slot-now)

pacer=ModelPacer()
async def pace_model_requests(callback_context,llm_request):
    limit=int(os.getenv('CORVQ_MODEL_REQUESTS_PER_MINUTE','4'))
    delay=pacer.reserve(limit)
    if delay:await asyncio.sleep(delay)
    return None
