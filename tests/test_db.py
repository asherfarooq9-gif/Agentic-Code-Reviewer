from src.db.migrate import run_migrations
from src.db.models import Category, ReviewStatus, Severity
from src.db.store import Store


def test_migrate_idempotent(tmp_path):
    db = str(tmp_path / "t.db")
    assert run_migrations(db) == 1
    assert run_migrations(db) == 1  # second run must not raise


def test_review_finding_roundtrip(tmp_path):
    db = str(tmp_path / "t.db")
    with Store(db) as store:
        review = store.create_review("https://github.com/o/r/pull/1", "o/r", 1)
        assert review.id is not None
        assert review.status is ReviewStatus.PENDING

        finding = store.add_finding(
            review.id,
            "foo.py",
            Severity.HIGH,
            Category.BUG,
            "off by one",
            line=10,
            confidence=0.8,
        )
        assert finding.id is not None

        got = store.get_review(review.id)
        assert got is not None
        assert got.pr_number == 1

        findings = store.list_findings(review.id)
        assert len(findings) == 1
        assert findings[0].severity is Severity.HIGH
        assert findings[0].line == 10

        store.update_review_status(review.id, ReviewStatus.COMPLETED)
        assert store.get_review(review.id).status is ReviewStatus.COMPLETED


def test_record_metric(tmp_path):
    db = str(tmp_path / "t.db")
    with Store(db) as store:
        metric = store.record_metric("precision", 0.75)
        assert metric.id is not None
        assert metric.value == 0.75
