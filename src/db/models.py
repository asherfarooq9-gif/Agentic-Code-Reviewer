"""Domain dataclasses + enums for reviews, findings, metrics."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Severity(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Category(StrEnum):
    BUG = "bug"
    SECURITY = "security"
    PERFORMANCE = "performance"
    STYLE = "style"


class ReviewStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class Review:
    id: int | None
    pr_url: str
    repo: str
    pr_number: int
    status: ReviewStatus
    input_tokens: int
    output_tokens: int
    created_at: str


@dataclass(frozen=True)
class Finding:
    id: int | None
    review_id: int
    file: str
    line: int | None
    severity: Severity
    category: Category
    message: str
    suggested_fix: str | None
    confidence: float | None
    created_at: str


@dataclass(frozen=True)
class Metric:
    id: int | None
    review_id: int | None
    name: str
    value: float
    created_at: str
