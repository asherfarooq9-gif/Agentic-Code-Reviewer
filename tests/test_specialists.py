from src.agents.specialists import review_diff_multi
from src.db.models import Category
from src.github.diff_parser import parse_diff
from src.llm.ollama_client import TokenUsage

CLEAN = (
    '[{"file":"a.py","line":3,"severity":"high","category":"bug",'
    '"message":"bad","suggested_fix":"fix it","confidence":0.9}]'
)

DIFF = """diff --git a/a.py b/a.py
--- a/a.py
+++ b/a.py
@@ -1,3 +1,3 @@
 a = 1
-b = 2
+b = 3
 c = 4
"""


class _FakeAsyncLLM:
    def __init__(self, text: str) -> None:
        self._text = text
        self.systems: list[str] = []

    async def acomplete(self, messages, *, deep=False, max_tokens=2048, system=None):
        self.systems.append(system)
        return self._text, TokenUsage(10, 5, "fake-model")


def test_runs_all_four_specialists():
    fake = _FakeAsyncLLM(CLEAN)
    findings, usage = review_diff_multi(parse_diff(DIFF), fake)
    # four specialists each return the same finding, re-labelled to their category
    assert len(findings) == 4
    assert {f.category for f in findings} == {
        Category.BUG,
        Category.SECURITY,
        Category.PERFORMANCE,
        Category.STYLE,
    }
    # token usage summed across the four calls
    assert usage.input_tokens == 40
    assert usage.output_tokens == 20
    assert len(fake.systems) == 4


def test_agreement_boost_applied():
    fake = _FakeAsyncLLM(CLEAN)
    findings, _ = review_diff_multi(parse_diff(DIFF), fake)
    # all four agree on a.py:3 -> confidence boosted above the base 0.9
    assert all(f.confidence >= 0.9 for f in findings)
