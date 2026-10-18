"""Offline ADK wiring tests: never call Gemini or require a real key."""
import pytest
from backend.app.agents import build_agent, configuration
from backend.app.core import investigate
from backend.app.models import Record
from backend.app.samples import samples


def test_adk_orchestrator_builds_offline(monkeypatch):
    pytest.importorskip('google.adk')
    monkeypatch.setenv('GEMINI_API_KEY','offline-test-key')
    monkeypatch.setenv('GOOGLE_API_KEY','offline-test-key')
    case=investigate('banking',[Record(**r) for r in samples('banking')],'Offline test')
    agent=build_agent(case)
    assert [a.name for a in agent.sub_agents] == ['investigation_agent','relationship_agent','policy_agent','report_agent']
    assert all(a.tools for a in agent.sub_agents[:3])
    report=agent.sub_agents[-1]
    assert not report.tools
    assert report.output_schema is not None
    assert '{evidence}' in report.instruction


def test_configuration_does_not_disclose_credentials(monkeypatch):
    monkeypatch.setenv('GEMINI_API_KEY','offline-secret-value')
    assert 'offline-secret-value' not in str(configuration())

def test_transient_provider_errors_retry_with_bounded_attempts(monkeypatch):
    import asyncio
    import backend.app.agents as agents
    calls=[]
    class Busy(Exception):code=503
    async def once(case):
        calls.append(case)
        if len(calls)<3:raise Busy()
        return {'metrics':{'tokens':10}}
    async def no_sleep(_):pass
    monkeypatch.setattr(agents,'_run_agents_once',once)
    monkeypatch.setattr(agents.asyncio,'sleep',no_sleep)
    result=asyncio.run(agents.run_agents({}))
    assert len(calls)==3 and result['metrics']['attempts']==3
    assert result['metrics']['tokens_complete'] is False


def test_quota_errors_do_not_auto_retry(monkeypatch):
    import asyncio
    import backend.app.agents as agents
    calls=[]
    class Quota(Exception):code=429
    async def once(case):calls.append(case);raise Quota()
    monkeypatch.setattr(agents,'_run_agents_once',once)
    with pytest.raises(Quota):asyncio.run(agents.run_agents({}))
    assert len(calls)==1

def test_model_pacing_spaces_all_agent_calls():
    from backend.app.agents.pacing import ModelPacer
    now=[100.0]
    pacer=ModelPacer(clock=lambda:now[0])
    assert pacer.reserve(4)==0
    assert pacer.reserve(4)==15
    assert pacer.reserve(4)==30
    now[0]=200
    assert pacer.reserve(4)==0
