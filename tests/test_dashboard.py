import pytest
from fastapi.testclient import TestClient

from src.api.app import create_app
from src.config import load_settings
from src.db.models import Category, Severity
from src.db.store import Store


@pytest.fixture
def client(tmp_path, monkeypatch):
    db = str(tmp_path / "dash.db")
    with Store(db) as store:
        review = store.create_review("https://github.com/o/r/pull/1", "o/r", 1)
        store.add_finding(
            review.id, "a.py", Severity.HIGH, Category.BUG, "bad", line=3, confidence=0.9
        )
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_test")
    monkeypatch.setenv("DB_PATH", db)
    load_settings.cache_clear()
    yield TestClient(create_app())
    load_settings.cache_clear()


def test_dashboard_html(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Agentic Code Reviewer" in resp.text


def test_api_reviews(client):
    data = client.get("/api/reviews").json()["reviews"]
    assert len(data) == 1
    assert data[0]["findings_count"] == 1
    assert data[0]["repo"] == "o/r"


def test_api_findings(client):
    rid = client.get("/api/reviews").json()["reviews"][0]["id"]
    findings = client.get(f"/api/reviews/{rid}/findings").json()["findings"]
    assert len(findings) == 1
    assert findings[0]["severity"] == "high"


def test_api_stats(client):
    stats = client.get("/api/stats").json()
    assert stats["total_reviews"] == 1
    assert stats["total_findings"] == 1
    assert stats["by_severity"]["high"] == 1
