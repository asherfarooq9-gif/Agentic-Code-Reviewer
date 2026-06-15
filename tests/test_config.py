import pytest
from pydantic import ValidationError

from src.config import Settings


def test_missing_required_raises(monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_loads_with_env(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_test")
    settings = Settings(_env_file=None)
    assert settings.github_token == "ghp_test"
    assert settings.db_path.endswith(".db")
    assert settings.ollama_host.startswith("http")
    assert settings.model_default
    assert settings.model_deep
