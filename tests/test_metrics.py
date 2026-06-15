from src.agents.orchestrator import ReviewFinding
from src.db.models import Category, Severity
from src.eval.metrics import EvalMetrics, ExpectedFinding, combine, compute_metrics


def _pred(file="a.py", line=10, cat=Category.BUG) -> ReviewFinding:
    return ReviewFinding(file, line, Severity.HIGH, cat, "m", None, 0.9)


def _exp(file="a.py", line=10, cat=Category.BUG) -> ExpectedFinding:
    return ExpectedFinding(file, line, cat)


def test_exact_match_is_tp():
    m = compute_metrics([_pred()], [_exp()])
    assert (m.tp, m.fp, m.fn) == (1, 0, 0)
    assert m.precision == 1.0 and m.recall == 1.0 and m.f1 == 1.0


def test_within_tolerance_matches():
    m = compute_metrics([_pred(line=12)], [_exp(line=10)], line_tolerance=3)
    assert m.tp == 1


def test_outside_tolerance_is_fp_and_fn():
    m = compute_metrics([_pred(line=20)], [_exp(line=10)], line_tolerance=3)
    assert (m.tp, m.fp, m.fn) == (0, 1, 1)


def test_wrong_category_no_match():
    m = compute_metrics([_pred(cat=Category.STYLE)], [_exp(cat=Category.BUG)])
    assert m.tp == 0


def test_extra_prediction_is_fp():
    m = compute_metrics([_pred(), _pred(line=50)], [_exp()])
    assert m.tp == 1 and m.fp == 1


def test_missing_prediction_is_fn():
    m = compute_metrics([], [_exp()])
    assert (m.tp, m.fp, m.fn) == (0, 0, 1)
    assert m.precision == 0.0 and m.recall == 0.0


def test_combine_sums():
    c = combine([EvalMetrics(1, 2, 3), EvalMetrics(4, 5, 6)])
    assert (c.tp, c.fp, c.fn) == (5, 7, 9)
