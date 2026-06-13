# Agentic Code Reviewer

AI agent that reviews GitHub PRs — finds bugs, security issues, and performance
problems, posts review comments, and benchmarks against human reviewers.

> Status: **M1 — Foundation**. Fetch any public PR diff via CLI; GitHub / Claude /
> DB / config plumbing in place and unit-tested. Reviewing comes in M2.

## Stack
Python 3.11+, Anthropic SDK, PyGithub, `unidiff`, Typer, stdlib `sqlite3`, pytest, uv.

## Setup
```bash
uv sync
cp .env.example .env   # then fill in ANTHROPIC_API_KEY and GITHUB_TOKEN
```

## Usage (M1)
```bash
# Initialise / migrate the local database
uv run arev init-db

# Fetch a public PR diff and print a summary
uv run arev fetch-pr https://github.com/<owner>/<repo>/pull/<number>
```

## Develop
```bash
uv run ruff check src tests
uv run pytest -q
```

## Layout
```
src/
  config.py            # env/.env settings (pydantic-settings)
  logging.py           # stdlib logging setup
  cli.py               # Typer CLI -> console script `arev`
  github/client.py     # PAT auth, PR URL parse, raw diff fetch
  github/diff_parser.py# unified diff -> structured files/hunks/lines
  llm/claude_client.py # Anthropic wrapper + token accounting
  db/                  # schema.sql, migrate.py, models.py, store.py
tests/                 # unit tests
tasks/                 # todo.md, lessons.md
```

See [tasks/todo.md](tasks/todo.md) for the milestone checklist.
