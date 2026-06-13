"""Typer CLI. Console script entrypoint `arev`."""
from __future__ import annotations

import typer

from .agents.orchestrator import review_diff
from .config import load_settings
from .db.migrate import run_migrations
from .db.models import ReviewStatus
from .db.store import Store
from .github.client import GitHubClient, parse_pr_url
from .github.diff_parser import parse_diff
from .github.review_poster import post_review
from .llm.claude_client import ClaudeClient
from .logging import configure_logging

app = typer.Typer(help="Agentic Code Reviewer CLI", no_args_is_help=True)


@app.command("fetch-pr")
def fetch_pr(url: str) -> None:
    """Fetch a public PR diff and print a summary."""
    settings = load_settings()
    configure_logging(settings.log_level)
    owner, repo, number = parse_pr_url(url)
    client = GitHubClient(settings.github_token)
    diff = client.fetch_diff(url)
    files = parse_diff(diff)

    total_added = sum(f.added for f in files)
    total_removed = sum(f.removed for f in files)
    total_hunks = sum(len(f.hunks) for f in files)

    typer.echo(f"PR {owner}/{repo}#{number}")
    typer.echo(f"  files changed: {len(files)}")
    typer.echo(f"  hunks: {total_hunks}")
    typer.echo(f"  +{total_added} / -{total_removed}")
    for f in files:
        flag = "A" if f.is_new else "D" if f.is_deleted else "M"
        typer.echo(f"    [{flag}] {f.path}  (+{f.added}/-{f.removed})")


@app.command("review")
def review(
    pr: str = typer.Option(..., "--pr", help="GitHub PR URL"),
    post: bool = typer.Option(False, "--post/--no-post", help="Post comments to the PR"),
    deep: bool = typer.Option(False, "--deep", help="Use the deep model"),
) -> None:
    """Review a PR diff (single agent pass), store findings, optionally post."""
    settings = load_settings()
    configure_logging(settings.log_level)
    owner, repo, number = parse_pr_url(pr)

    gh = GitHubClient(settings.github_token)
    diff = gh.fetch_diff(pr)
    files = parse_diff(diff)

    claude = ClaudeClient(
        settings.anthropic_api_key, settings.model_default, settings.model_deep
    )

    store = Store(settings.db_path)
    review_row = store.create_review(pr, f"{owner}/{repo}", number)
    store.update_review_status(review_row.id, ReviewStatus.RUNNING)
    try:
        findings, usage = review_diff(files, claude, deep=deep)
        for f in findings:
            store.add_finding(
                review_row.id,
                f.file,
                f.severity,
                f.category,
                f.message,
                line=f.line,
                suggested_fix=f.suggested_fix,
                confidence=f.confidence,
            )
        store.update_review_tokens(review_row.id, usage.input_tokens, usage.output_tokens)
        store.update_review_status(review_row.id, ReviewStatus.COMPLETED)
    except Exception:
        store.update_review_status(review_row.id, ReviewStatus.FAILED)
        store.close()
        raise

    typer.echo(f"PR {owner}/{repo}#{number} — {len(findings)} finding(s)")
    for f in findings:
        loc = f"{f.file}:{f.line}" if f.line is not None else f.file
        typer.echo(f"  [{f.severity.value}/{f.category.value}] {loc} — {f.message}")

    if post:
        posted = post_review(gh, pr, findings)
        typer.echo(f"Posted {posted} inline comment(s) + summary.")

    store.close()
    typer.echo(f"tokens in/out: {usage.input_tokens}/{usage.output_tokens}")


@app.command("init-db")
def init_db() -> None:
    """Create or migrate the SQLite database."""
    settings = load_settings()
    version = run_migrations(settings.db_path)
    typer.echo(f"DB ready at {settings.db_path} (schema v{version})")


if __name__ == "__main__":
    app()
