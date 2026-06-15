"""Ollama local LLM client. Free, open-source, no API key required.

Talks to an Ollama server running on the local machine. Exposes the same
`complete()` shape the orchestrator expects, returning (text, TokenUsage).
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

import ollama

logger = logging.getLogger("agentic_reviewer.llm")

_DEFAULT_MAX_TOKENS = 4096
_DEFAULT_TIMEOUT = 180


@dataclass(frozen=True)
class TokenUsage:
    input_tokens: int
    output_tokens: int
    model: str


class OllamaClient:
    """Wraps the Ollama client. Picks a default or deep model per call."""

    def __init__(
        self,
        host: str,
        model_default: str,
        model_deep: str,
        *,
        timeout: int = _DEFAULT_TIMEOUT,
    ) -> None:
        self._model_default = model_default
        self._model_deep = model_deep
        self._client = ollama.Client(host=host, timeout=timeout)

    def complete(
        self,
        messages: list[dict],
        *,
        deep: bool = False,
        max_tokens: int = _DEFAULT_MAX_TOKENS,
        system: str | None = None,
    ) -> tuple[str, TokenUsage]:
        """Send messages to the local model. Returns (text, usage)."""
        model = self._model_deep if deep else self._model_default
        full_messages: list[dict] = []
        if system:
            full_messages.append({"role": "system", "content": system})
        full_messages.extend(messages)

        resp = self._client.chat(
            model=model,
            messages=full_messages,
            options={"num_predict": max_tokens},
        )
        text = resp["message"]["content"]
        usage = TokenUsage(
            int(resp.get("prompt_eval_count", 0) or 0),
            int(resp.get("eval_count", 0) or 0),
            model,
        )
        logger.info(
            "Ollama %s: in=%d out=%d", model, usage.input_tokens, usage.output_tokens
        )
        return text, usage
