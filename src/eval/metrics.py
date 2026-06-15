"""Eval metrics: match predicted findings to ground-truth labels -> P/R/F1."""
from __future__ import annotations

from dataclasses import dataclass

from ..agents.orchestrator import ReviewFinding
from ..db.models import Category

_DEFAULT_TOLERANCE = 3


@dataclass(frozen=True)
class ExpectedFinding:
    file: str
    line: int
    category: Category


@dataclass(frozen=True)
class EvalMetrics:
    tp: int
    fp: int
    fn: int

    @property
    def precision(self) -> float:
        denom = self.tp + self.fp
        return self.tp / denom if denom else 0.0

    @property
    def recall(self) -> float:
        denom = self.tp + self.fn
        return self.tp / denom if denom else 0.0

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if (p + r) else 0.0


def _matches(pred: ReviewFinding, exp: ExpectedFinding, tol: int) -> bool:
    if pred.file != exp.file or pred.category != exp.category or pred.line is None:
        return False
    return abs(pred.line - exp.line) <= tol


def compute_metrics(
    predicted: list[ReviewFinding],
    expected: list[ExpectedFinding],
    *,
    line_tolerance: int = _DEFAULT_TOLERANCE,
) -> EvalMetrics:
    """Greedy one-to-one match of predictions to labels (same file+category,
    line within tolerance). Returns tp/fp/fn."""
    matched_pred: set[int] = set()
    matched_exp: set[int] = set()
    for ei, exp in enumerate(expected):
        for pi, pred in enumerate(predicted):
            if pi in matched_pred:
                continue
            if _matches(pred, exp, line_tolerance):
                matched_exp.add(ei)
                matched_pred.add(pi)
                break
    tp = len(matched_exp)
    fp = len(predicted) - len(matched_pred)
    fn = len(expected) - len(matched_exp)
    return EvalMetrics(tp, fp, fn)


def combine(metrics_list: list[EvalMetrics]) -> EvalMetrics:
    return EvalMetrics(
        sum(m.tp for m in metrics_list),
        sum(m.fp for m in metrics_list),
        sum(m.fn for m in metrics_list),
    )
