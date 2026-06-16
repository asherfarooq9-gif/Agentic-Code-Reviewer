# Agentic Code Reviewer

AI agent that reviews GitHub PRs — finds bugs, security issues, and performance
problems, posts inline review comments, and benchmarks itself against ground-truth
labels. Runs on a **free, local open-source LLM** (Ollama) — no paid API key.

> Status: **M7 — Web Dashboard**. Multi-agent specialists review a PR diff with a
> local model, dedup and score findings, store them, post inline GitHub comments,
> auto-review via webhook, and surface everything in a dashboard. Eval framework
> reports precision/recall/F1 against labelled cases.

## Stack
Python 3.11+, **Ollama (local open-source LLM)**, FastAPI + uvicorn, PyGithub,
`unidiff`, Typer, stdlib `sqlite3`, pytest, ruff, uv.

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
uv run arev init-db
```

## Usage
```bash
# Inspect a public PR diff
uv run arev fetch-pr https://github.com/<owner>/<repo>/pull/<number>

# Review a PR (multi-agent by default; prints findings, stores them)
uv run arev review --pr https://github.com/<owner>/<repo>/pull/<number>

# Single-pass instead of 4 specialists
uv run arev review --pr <url> --single

# Also post inline comments + summary to the PR (needs write-scoped token)
uv run arev review --pr <url> --post

# Use the larger "deep" model
uv run arev review --pr <url> --deep

# Gather surrounding-code context from a local checkout (fewer false positives)
uv run arev review --pr <url> --repo-path /path/to/local/checkout

# Benchmark against labelled cases — prints P / R / F1
uv run arev eval [--single] [--deep] [--tol N]

# Run the webhook server + dashboard
uv run arev serve --host 0.0.0.0 --port 8000
```

## Web server
`arev serve` runs a FastAPI app:
- `GET /` — dashboard (stats cards, severity bars, recent reviews)
- `GET /healthz` — liveness
- `GET /api/stats` — totals + findings by severity
- `GET /api/reviews` — recent reviews
- `GET /api/reviews/{id}/findings` — findings for a review
- `POST /webhook` — GitHub `pull_request` events (HMAC-verified) → auto-review

## Develop
```bash
uv run ruff check src tests
uv run pytest -q
```

## Layout
```
src/
  config.py               # env/.env settings (pydantic-settings)
  logging.py              # stdlib logging setup
  cli.py                  # Typer CLI -> console script `arev`
  agents/
    orchestrator.py       # single-pass: diff -> local LLM -> validated findings
    specialists.py        # 4 parallel specialists (bug/security/perf/style)
    aggregate.py          # dedup + cross-agent agreement confidence
    annotate.py           # annotate diff with new-side line numbers
    context.py            # surrounding-code context for findings
    tools.py              # codebase tools: read_file, search_codebase, callers
  github/
    client.py             # PAT auth, PR URL parse, raw diff fetch
    diff_parser.py        # unified diff -> structured files/hunks/lines
    review_poster.py      # post inline + summary comments
    webhook.py            # signature verify + event handling
  llm/
    ollama_client.py      # local Ollama wrapper + token accounting
    prompts/              # reviewer + per-specialist system prompts
  eval/
    dataset.py            # labelled case loader
    metrics.py            # precision / recall / F1, tp/fp/fn matching
    runner.py             # eval over cases, single vs multi
  api/
    app.py                # FastAPI app: dashboard, JSON API, webhook
    dashboard.py          # static dashboard HTML/JS
  db/                     # schema.sql, migrate.py, models.py, store.py
tests/                    # unit + API tests (72 passing)
eval_data/cases/          # labelled buggy-diff cases
tasks/                    # todo.md, lessons.md
```

See [tasks/todo.md](tasks/todo.md) for the milestone checklist.
