import pytest

from src.agents.orchestrator import parse_findings, review_diff
from src.db.models import Category, Severity
from src.github.diff_parser import parse_diff
from src.llm.ollama_client import TokenUsage

CLEAN = (
    '[{"file":"a.py","line":3,"severity":"high","category":"bug",'
    '"message":"bad","suggested_fix":"fix it","confidence":0.9}]'
)
FENCED = "```json\n" + CLEAN + "\n```"
PROSE = "Here are the issues:\n" + CLEAN + "\nThat's all."
MIXED = (
    '[{"file":"a.py","severity":"nope","category":"bug","message":"x"},'
    '{"file":"b.py","line":5,"severity":"low","category":"style","message":"y"}]'
)


def test_parse_clean():
    fs = parse_findings(CLEAN)
    assert len(fs) == 1
    assert fs[0].severity is Severity.HIGH
    assert fs[0].category is Category.BUG
    assert fs[0].line == 3


def test_parse_fenced():
    assert len(parse_findings(FENCED)) == 1


def test_parse_prose_wrapped():
    assert len(parse_findings(PROSE)) == 1


def test_parse_skips_malformed_entry():
    fs = parse_findings(MIXED)
    assert len(fs) == 1
    assert fs[0].file == "b.py"


def test_parse_empty_array():
    assert parse_findings("[]") == []


def test_parse_no_array_raises():
    with pytest.raises(ValueError):
        parse_findings("no json here")


class _FakeLLM:
    def __init__(self, text: str) -> None:
        self._text = text
        self.calls: list[dict] = []

    def complete(self, messages, *, deep=False, max_tokens=2048, system=None):
        self.calls.append({"messages": messages, "deep": deep, "system": system})
        return self._text, TokenUsage(100, 50, "fake-model")


def test_review_diff_end_to_end():
    diff = """diff --git a/a.py b/a.py
--- a/a.py
+++ b/a.py
@@ -1,2 +1,2 @@
-x = 1
+x = 2
 y = 3
"""
    fake = _FakeLLM(CLEAN)
    findings, usage = review_diff(parse_diff(diff), fake)
    assert len(findings) == 1
    assert usage.input_tokens == 100
    assert fake.calls[0]["system"] is not None
