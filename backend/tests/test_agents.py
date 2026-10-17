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
