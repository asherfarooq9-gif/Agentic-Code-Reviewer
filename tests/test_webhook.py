import hashlib
import hmac

from src.github.webhook import parse_pull_request_event, verify_signature


def _sign(secret: str, body: bytes) -> str:
    return "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


def test_verify_empty_secret_fails():
    assert verify_signature("", b"anything", None) is False


def test_verify_valid_signature():
    body = b"payload"
    assert verify_signature("s3cret", body, _sign("s3cret", body)) is True


def test_verify_invalid_signature():
    assert verify_signature("s3cret", b"payload", "sha256=deadbeef") is False


def test_verify_missing_header():
    assert verify_signature("s3cret", b"payload", None) is False


def test_parse_relevant_action():
    event = parse_pull_request_event(
        {"action": "opened", "pull_request": {"html_url": "u", "number": 7}}
    )
    assert event == {"action": "opened", "url": "u", "number": 7}


def test_parse_irrelevant_action():
    assert parse_pull_request_event({"action": "closed", "pull_request": {}}) is None


def test_parse_missing_url():
    assert parse_pull_request_event({"action": "opened", "pull_request": {}}) is None
