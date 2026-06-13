"""GitHub client: PAT auth, PR URL parsing, raw diff fetch."""
from __future__ import annotations

import re

import requests

from github import Auth, Github

_PR_URL_RE = re.compile(
    r"github\.com/(?P<owner>[^/\s]+)/(?P<repo>[^/\s]+)/pull/(?P<number>\d+)"
)
_DEFAULT_TIMEOUT = 30


def parse_pr_url(url: str) -> tuple[str, str, int]:
    """Extract (owner, repo, number) from a GitHub PR URL. Raises ValueError."""
    if not url or not isinstance(url, str):
        raise ValueError("PR URL must be a non-empty string")
    match = _PR_URL_RE.search(url.strip())
    if not match:
        raise ValueError(f"Not a valid GitHub PR URL: {url!r}")
    return match["owner"], match["repo"], int(match["number"])


class GitHubClient:
    """Thin PyGithub wrapper plus raw `.diff` fetch over the REST API."""

    def __init__(self, token: str, *, timeout: int = _DEFAULT_TIMEOUT) -> None:
        if not token:
            raise ValueError("GitHub token is required")
        self._token = token
        self._timeout = timeout
        self._gh = Github(auth=Auth.Token(token))

    def get_pull(self, url: str):
        """Return the PyGithub PullRequest for a PR URL."""
        owner, repo, number = parse_pr_url(url)
        return self._gh.get_repo(f"{owner}/{repo}").get_pull(number)

    def fetch_diff(self, url: str) -> str:
        """Fetch the raw unified diff for a PR. Raises on 404 / rate limit."""
        owner, repo, number = parse_pr_url(url)
        api = f"https://api.github.com/repos/{owner}/{repo}/pulls/{number}"
        resp = requests.get(
            api,
            headers={
                "Authorization": f"Bearer {self._token}",
                "Accept": "application/vnd.github.v3.diff",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            timeout=self._timeout,
        )
        if resp.status_code == 404:
            raise ValueError(f"PR not found (404): {url}")
        if resp.status_code == 403 and "rate limit" in resp.text.lower():
            raise RuntimeError("GitHub API rate limit exceeded")
        resp.raise_for_status()
        return resp.text
