from unittest.mock import MagicMock

from src.agents.orchestrator import ReviewFinding
from src.db.models import Category, Severity
from src.github.review_poster import build_summary, format_comment, post_review


def _finding(line: int | None = 10, sev: Severity = Severity.HIGH) -> ReviewFinding:
    return ReviewFinding("a.py", line, sev, Category.BUG, "bad thing", "do x", 0.8)


def test_format_comment_contains_fields():
    body = format_comment(_finding())
    assert "HIGH" in body
    assert "bad thing" in body
    assert "do x" in body


def test_build_summary_counts():
    summary = build_summary([_finding(sev=Severity.HIGH), _finding(sev=Severity.LOW)])
    assert "2 issue" in summary
    assert "1 high" in summary
    assert "1 low" in summary


def test_build_summary_empty():
    assert "No issues" in build_summary([])


def test_post_review_posts_inline_and_summary():
    pull = MagicMock()
    pull.get_commits.return_value = [MagicMock()]
    client = MagicMock()
    client.get_pull.return_value = pull

    findings = [_finding(line=10), _finding(line=None)]  # second has no line -> skipped
    posted = post_review(client, "https://github.com/o/r/pull/1", findings)

    assert posted == 1
    pull.create_review_comment.assert_called_once()
    pull.create_issue_comment.assert_called_once()
