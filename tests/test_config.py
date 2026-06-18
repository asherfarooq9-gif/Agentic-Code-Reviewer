import pytest
from pydantic import ValidationError

from src.config import Settings


def test_missing_token_raises(monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.setenv("WEBHOOK_SECRET", "dummy_secret")
    with pytest.raises(ValidationError, match="GITHUB_TOKEN"):
        Settings(_env_file=None)


def test_missing_webhook_secret_raises(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_test")
    monkeypatch.delenv("WEBHOOK_SECRET", raising=False)
    with pytest.raises(ValidationError, match="WEBHOOK_SECRET"):
        Settings(_env_file=None)


def test_loads_with_env(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_test")
    monkeypatch.setenv("WEBHOOK_SECRET", "dummy_secret")
    settings = Settings(_env_file=None)
    assert settings.github_token == "ghp_test"
    assert str(settings.db_path).endswith(".db")
    assert settings.ollama_host.startswith("http")
    assert settings.model_default
    assert settings.model_deep
