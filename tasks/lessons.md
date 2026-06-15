# Lessons

Append a dated note whenever a correction or surprise occurs during development.

## M1
- (none yet)

## M2
- 2026-06-15: Dropped the paid Anthropic dependency. Owner wants a free,
  fully local open-source model. Swapped to Ollama (`qwen2.5-coder`) behind the
  same `complete()` interface, so the orchestrator/CLI were unchanged except the
  client construction. Only secret now required is `GITHUB_TOKEN`.
