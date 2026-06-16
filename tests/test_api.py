import hashlib
import hmac
import json

import pytest
from fastapi.testclient import TestClient

from src.api.app import create_app
from src.config import load_settings

_SECRET = "webhook-secret"


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_test")
    monkeypatch.setenv("WEBHOOK_SECRET", _SECRET)
    load_settings.cache_clear()
    yield TestClient(create_app())
    load_settings.cache_clear()


def _sign(body: bytes) -> str:
    return "sha256=" + hmac.new(_SECRET.encode(), body, hashlib.sha256).hexdigest()


def test_healthz(client):
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_webhook_rejects_bad_signature(client):
    resp = client.post(
        "/webhook",
        content=b"{}",
        headers={"X-GitHub-Event": "pull_request", "X-Hub-Signature-256": "sha256=bad"},
    )
    assert resp.status_code == 401


def test_webhook_ignores_non_pr_event(client):
    body = b"{}"
    resp = client.post(
        "/webhook",
        content=body,
        headers={"X-GitHub-Event": "push", "X-Hub-Signature-256": _sign(body)},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "ignored"


def test_webhook_queues_pr_review(client, monkeypatch):
    monkeypatch.setattr("src.api.app.process_pull_request", lambda url: None)
    payload = json.dumps(
        {
            "action": "opened",
            "pull_request": {"html_url": "https://github.com/o/r/pull/1", "number": 1},
        }
    ).encode()
    resp = client.post(
        "/webhook",
        content=payload,
        headers={"X-GitHub-Event": "pull_request", "X-Hub-Signature-256": _sign(payload)},
    )
    assert resp.status_code == 202
