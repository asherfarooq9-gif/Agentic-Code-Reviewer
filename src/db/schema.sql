-- Agentic Code Reviewer schema (v1). Applied idempotently by migrate.py.

CREATE TABLE IF NOT EXISTS schema_version (
    version    INTEGER NOT NULL,
    applied_at TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS reviews (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    pr_url        TEXT    NOT NULL,
    repo          TEXT    NOT NULL,
    pr_number     INTEGER NOT NULL,
    status        TEXT    NOT NULL DEFAULT 'pending',
    input_tokens  INTEGER NOT NULL DEFAULT 0,
    output_tokens INTEGER NOT NULL DEFAULT 0,
    created_at    TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS findings (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    review_id     INTEGER NOT NULL REFERENCES reviews(id) ON DELETE CASCADE,
    file          TEXT    NOT NULL,
    line          INTEGER,
    severity      TEXT    NOT NULL,
    category      TEXT    NOT NULL,
    message       TEXT    NOT NULL,
    suggested_fix TEXT,
    confidence    REAL,
    created_at    TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS metrics (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    review_id  INTEGER REFERENCES reviews(id) ON DELETE CASCADE,
    name       TEXT    NOT NULL,
    value      REAL    NOT NULL,
    created_at TEXT    NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_findings_review ON findings(review_id);
CREATE INDEX IF NOT EXISTS idx_metrics_review ON metrics(review_id);
