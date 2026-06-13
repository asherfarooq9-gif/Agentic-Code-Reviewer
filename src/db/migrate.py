"""SQLite migration runner. Idempotent; tracks schema_version."""
from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

SCHEMA_PATH = Path(__file__).parent / "schema.sql"
CURRENT_VERSION = 1


def _utcnow() -> str:
    return datetime.now(UTC).isoformat()


def run_migrations(db_path: str) -> int:
    """Apply the schema if needed. Safe to call repeatedly. Returns version."""
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        row = conn.execute("SELECT MAX(version) FROM schema_version").fetchone()
        current = row[0] if row and row[0] is not None else 0
        if current < CURRENT_VERSION:
            conn.execute(
                "INSERT INTO schema_version (version, applied_at) VALUES (?, ?)",
                (CURRENT_VERSION, _utcnow()),
            )
        conn.commit()
        return CURRENT_VERSION
    finally:
        conn.close()
