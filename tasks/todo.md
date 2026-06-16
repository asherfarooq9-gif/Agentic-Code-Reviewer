# Tasks

## M1: Foundation
- [x] Init repo, pyproject.toml, dependencies (uv)
- [x] GitHub client wrapper (PAT auth, parse PR URL, fetch diff)
- [x] Diff parser (file, hunk, line mapping) — wraps `unidiff`
- [x] LLM client wrapper (local Ollama, retries, token tracking)
- [x] SQLite schema + migrations (reviews / findings / metrics)
- [x] Config (pydantic-settings) + stdlib logging
- [x] CLI: `arev fetch-pr <url>`, `arev init-db`
- [x] Unit tests: diff parser, config, db round-trip, github client

**Done:** fetch any public PR diff via CLI. ✅

## M2: Single-Agent Reviewer
- [x] Orchestrator agent (single pass) — `agents/orchestrator.py`
- [x] Prompt: analyze diff -> JSON findings — `llm/prompts/reviewer.py`
- [x] Diff annotation with new-side line numbers — `agents/annotate.py`
- [x] Robust JSON extraction + per-entry validation (skip bad, no crash)
- [x] Post findings as GitHub review comments — `github/review_poster.py`
- [x] CLI: `arev review --pr <url> [--post] [--deep]`
- [x] Store review + findings + token usage in DB
- [x] Tests: annotate, orchestrator (clean/fenced/prose/malformed), review_poster

**Done:** runs end-to-end, posts comments. Live run needs Ollama + GITHUB_TOKEN. ✅

## M3: Multi-Agent Specialists
- [x] Split into bug / security / perf / style specialists (async) — `agents/specialists.py`
- [x] Per-specialist focused prompts — `llm/prompts/specialists.py`
- [x] Async LLM path — `OllamaClient.acomplete`
- [x] Dedup findings + cross-agent agreement confidence — `agents/aggregate.py`
- [x] CLI: `arev review --multi` (default) / `--single`
- [x] Tests: aggregate (dedup/boost/cap/sort), specialists (4 agents, token sum)

**Done:** parallel agents, dedup works, severity assigned. ✅

## M4: Context Gathering
- [x] Tools: read_file, search_codebase, get_function_callers — `agents/tools.py`
- [x] Surrounding-code context before flagging -> fewer false positives — `agents/context.py`
- [x] CLI: `arev review --repo-path <local checkout>`

**Done:** context wired into review path. ✅

## M5: Eval Framework
- [x] Labelled eval cases (buggy diff + ground-truth findings) — `eval_data/cases/*.json`
- [x] Dataset loader — `eval/dataset.py`
- [x] Metrics: precision / recall / F1, tp/fp/fn by file+line+category — `eval/metrics.py`
- [x] Eval runner over cases, single vs multi — `eval/runner.py`
- [x] CLI: `arev eval [--multi/--single] [--tol N]`
- [x] Tests: metrics (match/tolerance/category/combine), runner+dataset

**Done:** benchmark report wired. ⚠️ Seed set is **2 cases** — real numbers pending (see Backlog). ✅

## M6: Webhook + Auto-Review
- [x] FastAPI app + `arev serve` — `api/app.py`
- [x] `POST /webhook` with HMAC signature verify — `github/webhook.py`
- [x] Auto-review on `pull_request` events
- [x] CI workflows — `.github/workflows/ci.yml`, `self-review.yml`
- [x] Tests: webhook (signature valid/invalid, event filter), api

**Done:** server auto-reviews PRs on push/open. ✅

## M7: Web Dashboard
- [x] Stats aggregation query — `db/store.py`
- [x] JSON API: `/api/stats`, `/api/reviews`, `/api/reviews/{id}/findings` — `api/app.py`
- [x] Dark dashboard UI (stats cards, severity bars, recent reviews) — `api/dashboard.py`
- [x] Tests: dashboard + stats endpoint — `tests/test_dashboard.py`

**Done:** dashboard served at `/`. ✅

---

## Backlog / Left to do
- [ ] **Live end-to-end proof** — run `arev review --pr <real url>` with Ollama serving
      + GITHUB_TOKEN; never executed against a real PR yet.
- [ ] **Expand eval set** — grow `eval_data/cases/` from 2 → 30–50 real buggy PRs,
      run `arev eval`, record P/R/F1 (single vs multi) in README. Core pitch needs
      real numbers.
- [ ] **Dashboard live check** — run `arev serve` with seeded DB, verify `/` renders.
- [ ] Optional: CSV/JSON export of findings; per-repo filtering on dashboard.

## State
72 tests pass · ruff clean · all milestones M1–M7 committed on `main`.
