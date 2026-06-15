"""Single-pass reviewer orchestrator: diff -> local LLM -> validated findings."""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass

from ..db.models import Category, Severity
from ..github.diff_parser import ParsedFile
from ..llm.ollama_client import OllamaClient, TokenUsage
from ..llm.prompts.reviewer import SYSTEM_PROMPT, build_user_prompt
from .annotate import annotate_diff

logger = logging.getLogger("agentic_reviewer.orchestrator")

_MAX_TOKENS = 4096


@dataclass(frozen=True)
class ReviewFinding:
    file: str
    line: int | None
    severity: Severity
    category: Category
    message: str
    suggested_fix: str | None
    confidence: float | None


def _extract_json_array(text: str) -> list:
    text = text.strip()
    if text.startswith("```"):
        # take content between the first pair of fences
        text = text.split("```", 2)[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1 or end < start:
        raise ValueError("No JSON array found in model output")
    return json.loads(text[start : end + 1])


def _coerce_finding(entry: dict) -> ReviewFinding | None:
    try:
        severity = Severity(str(entry["severity"]).lower())
        category = Category(str(entry["category"]).lower())
        message = str(entry["message"]).strip()
        if not message:
            return None
        line = entry.get("line")
        line = int(line) if line is not None else None
        fix = entry.get("suggested_fix")
        fix = str(fix) if fix else None
        conf = entry.get("confidence")
        conf = float(conf) if conf is not None else None
        return ReviewFinding(
            file=str(entry["file"]),
            line=line,
            severity=severity,
            category=category,
            message=message,
            suggested_fix=fix,
            confidence=conf,
        )
    except (KeyError, ValueError, TypeError) as exc:
        logger.warning("Skipping malformed finding %r: %s", entry, exc)
        return None


def parse_findings(raw_text: str) -> list[ReviewFinding]:
    """Extract + validate findings from raw model text. Skips bad entries."""
    data = _extract_json_array(raw_text)
    if not isinstance(data, list):
        raise ValueError("Model output is not a JSON array")
    coerced = (_coerce_finding(e) for e in data if isinstance(e, dict))
    return [f for f in coerced if f is not None]


def review_diff(
    files: list[ParsedFile], llm_client: OllamaClient, *, deep: bool = False
) -> tuple[list[ReviewFinding], TokenUsage]:
    """Run one reviewer pass over the parsed diff. Returns (findings, usage)."""
    annotated = annotate_diff(files)
    user_prompt = build_user_prompt(annotated)
    text, usage = llm_client.complete(
        [{"role": "user", "content": user_prompt}],
        deep=deep,
        max_tokens=_MAX_TOKENS,
        system=SYSTEM_PROMPT,
    )
    findings = parse_findings(text)
    logger.info("Review produced %d finding(s)", len(findings))
    return findings, usage
