# Agentic Code Reviewer

I wanted automated code review on my PRs without paying for another API. So I built this: a multi-agent system that runs entirely on my machine, pulls the diff from GitHub, sends it through four specialist reviewers (bug, security, perf, style), deduplicates what they find, and posts inline comments back to the PR. All local. No cloud bill.

The "agentic" part isn't marketing. Each specialist runs independently with its own system prompt and the full diff. They notice different things. An aggregator then scores findings by how many agents agreed and filters out the noise.

Current state: bugs and security findings come back accurate. Performance and style are hit or miss -- the 7B model doesn't always know what "performance" means in context. Running the 14B model helps, but I haven't fully benchmarked that combination yet.

## Stack

Python 3.11, Ollama, FastAPI, PyGithub, unidiff, SQLite, pytest, ruff, uv.

## Requirements

- **Python 3.11+** -- check with `python --version`
- **uv** -- fast Python package manager (replaces pip + venv)
- **Ollama** -- runs the LLM locally, free, no API key
- **Git** -- to clone this repo
- **~8 GB RAM** -- for the default 7B model (14B needs ~16 GB)

## Installation

### 1. Install uv

**macOS / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Restart your terminal after installing.

### 2. Install Ollama

Download from [ollama.com](https://ollama.com) and install it. Then pull the model:

```bash
ollama serve                          # start Ollama (runs in background)
ollama pull qwen2.5-coder:7b         # default model (~4.7 GB download, needs ~8 GB RAM)
ollama pull qwen2.5-coder:14b        # optional larger model (~9 GB download, needs ~16 GB RAM)
```

### 3. Clone and install

```bash
git clone https://github.com/<your-username>/agentic-code-reviewer.git
cd agentic-code-reviewer
uv sync
```

### 4. Configure

```bash
cp .env.example .env
```

Open `.env` and fill in:

```env
GITHUB_TOKEN=ghp_your_token_here
WEBHOOK_SECRET=any_random_string_here
```

**Getting a GitHub token:**
1. Go to github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Give it `repo` scope (or `public_repo` for public repos only)
4. Copy the token into `.env`

**Generating a webhook secret:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
Paste the output into `WEBHOOK_SECRET` in `.env`.

### 5. Initialize the database

```bash
uv run arev init-db
```

Done. Run `uv run arev serve` to start.

## Running it

```bash
# review a PR (4 agents by default, results printed and stored)
uv run arev review --pr https://github.com/<owner>/<repo>/pull/<number>

# post the findings as inline comments directly to the PR
uv run arev review --pr <url> --post

# single pass instead of 4 agents (faster, less thorough)
uv run arev review --pr <url> --single

# use the larger model
uv run arev review --pr <url> --deep

# pass a local checkout for surrounding context (fewer false positives)
uv run arev review --pr <url> --repo-path /path/to/local/checkout

# run the dashboard and webhook server
uv run arev serve --host 0.0.0.0 --port 8000

# benchmark against labelled cases
uv run arev eval [--single] [--deep] [--tol N]

# inspect a raw diff without reviewing
uv run arev fetch-pr https://github.com/<owner>/<repo>/pull/<number>
```

## Dashboard and webhook

`arev serve` starts a FastAPI server on port 8000. Open `http://localhost:8000` for the dashboard: stats cards, severity bars, recent reviews with expandable findings.

To auto-review PRs via GitHub webhook:

1. Expose the server publicly -- [ngrok](https://ngrok.com) works for local dev:
   ```bash
   ngrok http 8000
   ```
2. Go to your repo on GitHub: Settings > Webhooks > Add webhook
3. Set Payload URL to `https://<your-ngrok-url>/webhook`
4. Set Content type to `application/json`
5. Set Secret to the same value as `WEBHOOK_SECRET` in your `.env`
6. Select "Pull requests" events only
7. Save -- GitHub will now send every PR open/update to your server

API endpoints if you want to build on it:

- `GET /api/stats` -- totals and findings by severity
- `GET /api/reviews` -- recent reviews
- `GET /api/reviews/{id}/findings` -- findings for a specific review
- `POST /webhook` -- GitHub pull_request events (HMAC-verified)

## How well does it actually work?

Benchmarked on 26 hand-labelled cases (qwen2.5-coder:7b, single-agent, line tolerance +-3):

| Category | P | R | F1 |
|----------|---|---|----|
| Bug (9 cases) | 0.89 | 0.89 | 0.89 |
| Security (8 cases) | 0.83 | 0.88 | 0.85 |
| Performance (5 cases) | 0.50 | 0.20 | 0.29 |
| Style (4 cases) | 0.08 | 0.25 | 0.12 |
| **Overall** | **0.61** | **0.65** | **0.63** |

Bug and security detection is solid. Performance is honestly bad -- 0.29 F1 means it catches some but misses most, and what it does catch isn't always on the right line. Style is basically noise at this model size. Multi-agent mode and the 14B model help; that's the next thing to benchmark properly.

## Develop

```bash
uv run ruff check src tests    # lint
uv run pytest -q               # run tests (73 passing)
```

## Layout

```
src/
  config.py               # env/.env settings (pydantic-settings)
  logging.py              # stdlib logging setup
  cli.py                  # Typer CLI -> console script `arev`
  agents/
    orchestrator.py       # single-pass: diff -> LLM -> validated findings
    specialists.py        # 4 parallel specialists (bug/security/perf/style)
    aggregate.py          # dedup + cross-agent confidence scoring
    annotate.py           # diff line number mapping
    context.py            # surrounding-code context for findings
    tools.py              # read_file, search_codebase, callers
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
    dashboard.py          # dashboard HTML/JS
  db/                     # schema, migrate.py, models.py, store.py
tests/                    # unit + API tests (73 passing)
eval_data/cases/          # labelled buggy-diff cases
tasks/                    # todo.md, lessons.md
```
