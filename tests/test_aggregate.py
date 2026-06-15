from src.agents.aggregate import aggregate
from src.agents.orchestrator import ReviewFinding
from src.db.models import Category, Severity


def _f(
    category: Category,
    *,
    line: int = 3,
    conf: float = 0.5,
    sev: Severity = Severity.MEDIUM,
    file: str = "a.py",
) -> ReviewFinding:
    return ReviewFinding(file, line, sev, category, "msg", None, conf)


def test_dedup_keeps_higher_confidence():
    out = aggregate([_f(Category.BUG, conf=0.4), _f(Category.BUG, conf=0.8)])
    assert len(out) == 1
    assert out[0].confidence == 0.8  # single category on the line -> no boost


def test_agreement_boost_across_categories():
    out = aggregate([_f(Category.BUG, conf=0.5), _f(Category.SECURITY, conf=0.5)])
    assert len(out) == 2
    assert all(round(o.confidence, 2) == 0.6 for o in out)  # 2 categories -> +0.1


def test_confidence_capped_at_one():
    out = aggregate(
        [
            _f(Category.BUG, conf=0.95),
            _f(Category.SECURITY, conf=0.95),
            _f(Category.PERFORMANCE, conf=0.95),
        ]
    )
    assert all(o.confidence <= 1.0 for o in out)


def test_sorted_by_severity():
    out = aggregate(
        [
            _f(Category.STYLE, line=1, sev=Severity.LOW),
            _f(Category.BUG, line=2, sev=Severity.CRITICAL),
        ]
    )
    assert out[0].severity is Severity.CRITICAL
