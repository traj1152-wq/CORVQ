"""Never allow developer .env settings to turn regression tests into cloud calls."""
import pytest

@pytest.fixture(autouse=True)
def isolated_runtime(monkeypatch,tmp_path):
    for name in ('CORVQ_AUTH_MODE','CORVQ_API_TOKEN','CORVQ_FIREBASE_PROJECT','GEMINI_API_KEY','GOOGLE_API_KEY','K_SERVICE'):
        monkeypatch.delenv(name,raising=False)
    monkeypatch.setenv('CORVQ_STORAGE','sqlite')
    monkeypatch.setenv('CORVQ_DB',str(tmp_path/'isolated.db'))
