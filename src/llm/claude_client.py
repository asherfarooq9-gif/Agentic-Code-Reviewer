"""Anthropic Claude client wrapper with token accounting + model selection."""
from __future__ import annotations

import logging
from dataclasses import dataclass

from anthropic import Anthropic

logger = logging.getLogger("agentic_reviewer.llm")

_DEFAULT_MAX_TOKENS = 2048


@dataclass(frozen=True)
class TokenUsage:
    input_tokens: int
    output_tokens: int
    model: str


class ClaudeClient:
    """Wraps the Anthropic SDK. Picks a cheap or deep model per call."""

    def __init__(
        self,
        api_key: str,
        model_default: str,
        model_deep: str,
        *,
        max_retries: int = 3,
    ) -> None:
        if not api_key:
            raise ValueError("Anthropic API key is required")
        self._model_default = model_default
        self._model_deep = model_deep
        self._client = Anthropic(api_key=api_key, max_retries=max_retries)

    def complete(
        self,
        messages: list[dict],
        *,
        deep: bool = False,
        max_tokens: int = _DEFAULT_MAX_TOKENS,
        system: str | None = None,
    ) -> tuple[str, TokenUsage]:
        """Send messages, return (text, usage). No tool use yet (M2+)."""
        model = self._model_deep if deep else self._model_default
        kwargs: dict = {"model": model, "max_tokens": max_tokens, "messages": messages}
        if system:
            kwargs["system"] = system
        resp = self._client.messages.create(**kwargs)
        text = "".join(
            block.text for block in resp.content if getattr(block, "type", None) == "text"
        )
        usage = TokenUsage(resp.usage.input_tokens, resp.usage.output_tokens, model)
        logger.info(
            "Claude %s: in=%d out=%d", model, usage.input_tokens, usage.output_tokens
        )
        return text, usage
