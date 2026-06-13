"""Post review findings to a GitHub PR as inline + summary comments."""
from __future__ import annotations

import logging

from github import GithubException

from ..agents.orchestrator import ReviewFinding
from .client import GitHubClient

logger = logging.getLogger("agentic_reviewer.poster")

_SEVERITY_EMOJI = {
    "critical": "🛑",
    "high": "🔴",
    "medium": "🟠",
    "low": "🟡",
    "info": "🔵",
}
_SEVERITY_ORDER = ["critical", "high", "medium", "low", "info"]


def format_comment(finding: ReviewFinding) -> str:
    emoji = _SEVERITY_EMOJI.get(finding.severity.value, "")
    head = f"{emoji} **{finding.severity.value.upper()} / {finding.category.value}**"
    body = f"{head}\n\n{finding.message}"
    if finding.suggested_fix:
        body += f"\n\n**Suggested fix:**\n{finding.suggested_fix}"
    if finding.confidence is not None:
        body += f"\n\n_confidence: {finding.confidence:.2f}_"
    return body


def build_summary(findings: list[ReviewFinding]) -> str:
    if not findings:
        return "## Agentic Code Reviewer\n\nNo issues found. ✅"
    counts: dict[str, int] = {}
    for finding in findings:
        counts[finding.severity.value] = counts.get(finding.severity.value, 0) + 1
    parts = [f"{counts[s]} {s}" for s in _SEVERITY_ORDER if s in counts]
    return (
        "## Agentic Code Reviewer\n\n"
        f"Found {len(findings)} issue(s): " + ", ".join(parts) + "."
    )


def post_review(client: GitHubClient, url: str, findings: list[ReviewFinding]) -> int:
    """Post inline comments (findings with a line) plus a summary. Returns posted count."""
    pull = client.get_pull(url)
    commits = list(pull.get_commits())
    if not commits:
        raise ValueError("PR has no commits")
    commit = commits[-1]

    posted = 0
    for finding in findings:
        if finding.line is None:
            continue
        try:
            pull.create_review_comment(
                body=format_comment(finding),
                commit=commit,
                path=finding.file,
                line=finding.line,
                side="RIGHT",
            )
            posted += 1
        except GithubException as exc:
            logger.warning(
                "Failed to post comment on %s:%s: %s", finding.file, finding.line, exc
            )

    pull.create_issue_comment(build_summary(findings))
    return posted
