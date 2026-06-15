"""Run the four specialist reviewers concurrently and aggregate results."""
from __future__ import annotations

import asyncio
import logging
from dataclasses import replace

from ..db.models import Category
from ..github.diff_parser import ParsedFile
from ..llm.ollama_client import OllamaClient, TokenUsage
from ..llm.prompts.reviewer import build_user_prompt
from ..llm.prompts.specialists import SPECIALIST_PROMPTS
from .aggregate import aggregate
from .annotate import annotate_diff
from .orchestrator import ReviewFinding, parse_findings

logger = logging.getLogger("agentic_reviewer.specialists")

_MAX_TOKENS = 4096


async def _run_one(
    category: Category,
    system_prompt: str,
    user_prompt: str,
    llm_client: OllamaClient,
    deep: bool,
) -> tuple[list[ReviewFinding], TokenUsage]:
    text, usage = await llm_client.acomplete(
        [{"role": "user", "content": user_prompt}],
        deep=deep,
        max_tokens=_MAX_TOKENS,
        system=system_prompt,
    )
    try:
        findings = parse_findings(text)
    except ValueError:
        logger.warning("Specialist %s returned no parseable findings", category.value)
        findings = []
    # the specialist owns its category; override whatever the model labelled
    findings = [replace(f, category=category) for f in findings]
    return findings, usage


async def _run_all(
    files: list[ParsedFile], llm_client: OllamaClient, deep: bool
) -> tuple[list[ReviewFinding], TokenUsage]:
    user_prompt = build_user_prompt(annotate_diff(files))
    tasks = [
        _run_one(category, prompt, user_prompt, llm_client, deep)
        for category, prompt in SPECIALIST_PROMPTS.items()
    ]
    results = await asyncio.gather(*tasks)

    all_findings: list[ReviewFinding] = []
    total_in = total_out = 0
    model = ""
    for findings, usage in results:
        all_findings.extend(findings)
        total_in += usage.input_tokens
        total_out += usage.output_tokens
        model = usage.model or model
    return all_findings, TokenUsage(total_in, total_out, model)


def review_diff_multi(
    files: list[ParsedFile], llm_client: OllamaClient, *, deep: bool = False
) -> tuple[list[ReviewFinding], TokenUsage]:
    """Run all specialists concurrently, dedup + score, return (findings, usage)."""
    raw_findings, usage = asyncio.run(_run_all(files, llm_client, deep))
    findings = aggregate(raw_findings)
    logger.info("Multi-agent review produced %d finding(s)", len(findings))
    return findings, usage
