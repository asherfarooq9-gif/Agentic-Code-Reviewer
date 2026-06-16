"""GitHub webhook helpers: signature verification + pull_request parsing."""
from __future__ import annotations

import hashlib
import hmac

_RELEVANT_ACTIONS = {"opened", "synchronize", "reopened"}


def verify_signature(secret: str, body: bytes, signature_header: str | None) -> bool:
    """Verify the GitHub X-Hub-Signature-256 HMAC. Empty secret skips (dev only)."""
    if not secret:
        return True
    if not signature_header or not signature_header.startswith("sha256="):
        return False
    expected = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature_header)


def parse_pull_request_event(payload: dict) -> dict | None:
    """Return {action, url, number} for review-worthy PR events, else None."""
    if payload.get("action") not in _RELEVANT_ACTIONS:
        return None
    pull = payload.get("pull_request") or {}
    url = pull.get("html_url")
    if not url:
        return None
    return {"action": payload["action"], "url": url, "number": pull.get("number")}
