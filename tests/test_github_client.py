import pytest
import responses

from src.github.client import GitHubClient, parse_pr_url


def test_parse_pr_url_ok():
    assert parse_pr_url("https://github.com/octocat/Hello-World/pull/42") == (
        "octocat",
        "Hello-World",
        42,
    )


def test_parse_pr_url_trailing_path():
    assert parse_pr_url("https://github.com/o/r/pull/7/files") == ("o", "r", 7)


@pytest.mark.parametrize(
    "bad",
    [
        "",
        "https://github.com/o/r",
        "not a url",
        "https://github.com/o/r/issues/1",
    ],
)
def test_parse_pr_url_bad(bad):
    with pytest.raises(ValueError):
        parse_pr_url(bad)


def test_client_requires_token():
    with pytest.raises(ValueError):
        GitHubClient("")


@responses.activate
def test_fetch_diff_mocked():
    diff = "diff --git a/x b/x\n"
    responses.add(
        responses.GET,
        "https://api.github.com/repos/o/r/pulls/3",
        body=diff,
        status=200,
        content_type="text/plain",
    )
    client = GitHubClient("ghp_fake")
    assert client.fetch_diff("https://github.com/o/r/pull/3") == diff


@responses.activate
def test_fetch_diff_404():
    responses.add(
        responses.GET,
        "https://api.github.com/repos/o/r/pulls/9",
        status=404,
    )
    client = GitHubClient("ghp_fake")
    with pytest.raises(ValueError):
        client.fetch_diff("https://github.com/o/r/pull/9")
