"""Run a reviewer over labelled eval cases and aggregate metrics."""
from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass

from ..github.diff_parser import parse_diff
from .dataset import EvalCase
from .metrics import EvalMetrics, combine, compute_metrics

logger = logging.getLogger("agentic_reviewer.eval")

# reviewer_fn(files, llm_client, *, deep) -> (findings, usage)
ReviewerFn = Callable[..., tuple[list, object]]


@dataclass(frozen=True)
class CaseResult:
    case_id: str
    metrics: EvalMetrics


@dataclass(frozen=True)
class EvalReport:
    per_case: list[CaseResult]
    overall: EvalMetrics


def run_eval(
    cases: list[EvalCase],
    reviewer_fn: ReviewerFn,
    llm_client: object,
    *,
    deep: bool = False,
    line_tolerance: int = 3,
) -> EvalReport:
    """Review each case, score predictions vs labels, aggregate."""
    results: list[CaseResult] = []
    for case in cases:
        files = parse_diff(case.diff)
        findings, _usage = reviewer_fn(files, llm_client, deep=deep)
        metrics = compute_metrics(findings, case.expected, line_tolerance=line_tolerance)
        logger.info(
            "Eval %s: tp=%d fp=%d fn=%d", case.id, metrics.tp, metrics.fp, metrics.fn
        )
        results.append(CaseResult(case.id, metrics))

    overall = combine([r.metrics for r in results]) if results else EvalMetrics(0, 0, 0)
    return EvalReport(results, overall)
