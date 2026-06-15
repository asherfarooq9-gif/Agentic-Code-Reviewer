# Tasks

## M1: Foundation
- [x] Init repo, pyproject.toml, dependencies (uv)
- [x] GitHub client wrapper (PAT auth, parse PR URL, fetch diff)
- [x] Diff parser (file, hunk, line mapping) — wraps `unidiff`
- [x] Claude client wrapper (messages API, retries via SDK, token tracking)
- [x] SQLite schema + migrations (reviews / findings / metrics)
- [x] Config (pydantic-settings) + stdlib logging
- [x] CLI: `arev fetch-pr <url>`, `arev init-db`
- [x] Unit tests: diff parser, config, db round-trip, github client

**Done when:** can fetch any public PR diff via CLI. ✅

## M2: Single-Agent Reviewer
- [x] Orchestrator agent (single pass) — `agents/orchestrator.py`
- [x] Prompt: analyze diff -> JSON findings — `llm/prompts/reviewer.py`
- [x] Diff annotation with new-side line numbers — `agents/annotate.py`
- [x] Robust JSON extraction + per-entry validation (skip bad, no crash)
- [x] Post findings as GitHub review comments — `github/review_poster.py`
- [x] CLI: `arev review --pr <url> [--post] [--deep]`
- [x] Store review + findings + token usage in DB
- [x] Tests: annotate, orchestrator (clean/fenced/prose/malformed), review_poster

**Done when:** runs end-to-end on real PR, posts comments.
Local proof: 31 tests pass, ruff clean, CLI wired. End-to-end on a live PR
needs real ANTHROPIC_API_KEY + GITHUB_TOKEN (user step):
`uv run arev review --pr <url> --post`

## M3: Multi-Agent Specialists
- [x] Split into bug / security / perf / style specialists (asyncio.gather) — `agents/specialists.py`
- [x] Per-specialist focused prompts — `llm/prompts/specialists.py`
- [x] Async LLM path — `OllamaClient.acomplete`
- [x] Dedup findings + cross-agent agreement confidence — `agents/aggregate.py`
- [x] CLI: `arev review --multi` (default) / `--single`
- [x] Tests: aggregate (dedup/boost/cap/sort), specialists (4 agents, token sum)

**Done when:** parallel agents, dedup works, severity assigned.
Local proof: 39 tests pass, ruff clean. Live run needs Ollama + a real PR.

## M5: Eval Framework
- [x] Labelled eval cases (buggy diff + ground-truth findings) — `eval_data/cases/*.json`
- [x] Dataset loader — `eval/dataset.py`
- [x] Metrics: precision / recall / F1, tp/fp/fn matching by file+line+category — `eval/metrics.py`
- [x] Eval runner over cases, single vs multi — `eval/runner.py`
- [x] CLI: `arev eval [--multi/--single] [--tol N]`
- [x] Tests: metrics (match/tolerance/category/combine), runner+dataset

**Done when:** benchmark report with numbers.
Local proof: 49 tests pass, ruff clean. Real numbers need Ollama running
(`arev eval`). Seed set is 2 cases; expand toward 30-50 real buggy PRs later.

## M4: Context Gathering (deferred — skipped to build M5 first)
- [ ] Tools: read_file, search_codebase, get_function_callers
- [ ] Agent gathers context before flagging -> fewer false positives

(See ROADMAP for M6–M8.)
