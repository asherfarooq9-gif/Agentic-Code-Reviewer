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

## M2: Single-Agent Reviewer (next)
- [ ] Orchestrator agent (single pass)
- [ ] Prompt: analyze diff -> JSON findings
- [ ] Post findings as GitHub review comments
- [ ] CLI: `arev review --pr <url>`
- [ ] Store review + findings in DB

(See ROADMAP for M3–M8.)
