"""Typer CLI. Console script entrypoint `arev`."""
from __future__ import annotations

import typer

from .config import load_settings
from .db.migrate import run_migrations
from .github.client import GitHubClient, parse_pr_url
from .github.diff_parser import parse_diff
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


@app.command("init-db")
def init_db() -> None:
    """Create or migrate the SQLite database."""
    settings = load_settings()
    version = run_migrations(settings.db_path)
    typer.echo(f"DB ready at {settings.db_path} (schema v{version})")


if __name__ == "__main__":
    app()
