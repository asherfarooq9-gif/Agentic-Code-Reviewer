"""SQLite CRUD store. Returns new dataclasses; never mutates inputs."""
from __future__ import annotations

import sqlite3
from datetime import UTC, datetime

from .migrate import run_migrations
from .models import Category, Finding, Metric, Review, ReviewStatus, Severity


def _utcnow() -> str:
    return datetime.now(UTC).isoformat()


class Store:
    """Connection-owning store. Use as a context manager."""

    def __init__(self, db_path: str, *, auto_migrate: bool = True) -> None:
        self._db_path = db_path
        if auto_migrate:
            run_migrations(db_path)
        self._conn = sqlite3.connect(db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")

    def __enter__(self) -> Store:
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def close(self) -> None:
        self._conn.close()

    def create_review(self, pr_url: str, repo: str, pr_number: int) -> Review:
        created = _utcnow()
        cur = self._conn.execute(
            "INSERT INTO reviews (pr_url, repo, pr_number, status, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (pr_url, repo, pr_number, ReviewStatus.PENDING.value, created),
        )
        self._conn.commit()
        return Review(
            cur.lastrowid, pr_url, repo, pr_number, ReviewStatus.PENDING, 0, 0, created
        )

    def update_review_status(self, review_id: int, status: ReviewStatus) -> None:
        self._conn.execute(
            "UPDATE reviews SET status = ? WHERE id = ?", (status.value, review_id)
        )
        self._conn.commit()

    def get_review(self, review_id: int) -> Review | None:
        row = self._conn.execute(
            "SELECT * FROM reviews WHERE id = ?", (review_id,)
        ).fetchone()
        if row is None:
            return None
        return Review(
            row["id"],
            row["pr_url"],
            row["repo"],
            row["pr_number"],
            ReviewStatus(row["status"]),
            row["input_tokens"],
            row["output_tokens"],
            row["created_at"],
        )

    def add_finding(
        self,
        review_id: int,
        file: str,
        severity: Severity,
        category: Category,
        message: str,
        *,
        line: int | None = None,
        suggested_fix: str | None = None,
        confidence: float | None = None,
    ) -> Finding:
        created = _utcnow()
        cur = self._conn.execute(
            "INSERT INTO findings (review_id, file, line, severity, category, "
            "message, suggested_fix, confidence, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                review_id,
                file,
                line,
                severity.value,
                category.value,
                message,
                suggested_fix,
                confidence,
                created,
            ),
        )
        self._conn.commit()
        return Finding(
            cur.lastrowid,
            review_id,
            file,
            line,
            severity,
            category,
            message,
            suggested_fix,
            confidence,
            created,
        )

    def list_findings(self, review_id: int) -> list[Finding]:
        rows = self._conn.execute(
            "SELECT * FROM findings WHERE review_id = ? ORDER BY id", (review_id,)
        ).fetchall()
        return [
            Finding(
                r["id"],
                r["review_id"],
                r["file"],
                r["line"],
                Severity(r["severity"]),
                Category(r["category"]),
                r["message"],
                r["suggested_fix"],
                r["confidence"],
                r["created_at"],
            )
            for r in rows
        ]

    def record_metric(
        self, name: str, value: float, *, review_id: int | None = None
    ) -> Metric:
        created = _utcnow()
        cur = self._conn.execute(
            "INSERT INTO metrics (review_id, name, value, created_at) "
            "VALUES (?, ?, ?, ?)",
            (review_id, name, value, created),
        )
        self._conn.commit()
        return Metric(cur.lastrowid, review_id, name, value, created)
