# Agentic Code Reviewer

AI agent that reviews GitHub PRs — finds bugs, security issues, and performance
problems, posts review comments, and benchmarks against human reviewers. Runs on
a **free, local open-source LLM** (Ollama) — no paid API key.

> Status: **M2 — Single-Agent Reviewer**. Fetch a PR diff, review it with a local
> model, store findings, and post inline GitHub comments. Multi-agent specialists
> (M3) come next.

## Stack
Python 3.11+, **Ollama (local open-source LLM)**, PyGithub, `unidiff`, Typer,
stdlib `sqlite3`, pytest, uv.

## Prerequisites
1. Install [Ollama](https://ollama.com) and start it (`ollama serve`).
2. Pull a code model:
   ```bash
   ollama pull qwen2.5-coder:7b      # default (needs ~8 GB RAM)
   ollama pull qwen2.5-coder:14b     # optional "deep" model
   ```

## Setup
```bash
uv sync
cp .env.example .env   # then fill in GITHUB_TOKEN (only secret needed)
```

## Usage
```bash
# Initialise / migrate the local database
uv run arev init-db

# Inspect a public PR diff
uv run arev fetch-pr https://github.com/<owner>/<repo>/pull/<number>

# Review a PR with the local model (prints findings, stores them)
uv run arev review --pr https://github.com/<owner>/<repo>/pull/<number>

# Also post inline comments + a summary to the PR (needs write-scoped token)
uv run arev review --pr <url> --post

# Use the larger "deep" model
uv run arev review --pr <url> --deep
```

## Develop
```bash
uv run ruff check src tests
uv run pytest -q
```

## Layout
```
src/
  config.py             # env/.env settings (pydantic-settings)
  logging.py            # stdlib logging setup
  cli.py                # Typer CLI -> console script `arev`
  agents/orchestrator.py# diff -> local LLM -> validated findings
  agents/annotate.py    # annotate diff with new-side line numbers
  github/client.py      # PAT auth, PR URL parse, raw diff fetch
  github/diff_parser.py # unified diff -> structured files/hunks/lines
  github/review_poster.py # post inline + summary comments
  llm/ollama_client.py  # local Ollama wrapper + token accounting
  llm/prompts/          # reviewer system prompt
  db/                   # schema.sql, migrate.py, models.py, store.py
tests/                  # unit tests
tasks/                  # todo.md, lessons.md
```

See [tasks/todo.md](tasks/todo.md) for the milestone checklist.
