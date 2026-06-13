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

## M3: Multi-Agent Specialists (next)
- [ ] Split into bug / security / perf / style specialists (asyncio.gather)
- [ ] Per-specialist focused prompts + few-shot
- [ ] Orchestrator deduplicates findings
- [ ] Confidence via cross-agent agreement

(See ROADMAP for M4–M8.)
