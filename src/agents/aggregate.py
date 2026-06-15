"""Deduplicate specialist findings and score cross-agent agreement."""
from __future__ import annotations

from dataclasses import replace

from ..db.models import Severity
from .orchestrator import ReviewFinding

_SEVERITY_RANK = {
    Severity.CRITICAL: 4,
    Severity.HIGH: 3,
    Severity.MEDIUM: 2,
    Severity.LOW: 1,
    Severity.INFO: 0,
}
_AGREEMENT_BOOST = 0.1
_DEFAULT_CONFIDENCE = 0.5


def _dedup_exact(findings: list[ReviewFinding]) -> list[ReviewFinding]:
    """Collapse identical (file, line, category) findings, keeping highest confidence."""
    best: dict[tuple, ReviewFinding] = {}
    for f in findings:
        key = (f.file, f.line, f.category)
        current = best.get(key)
        if current is None or (f.confidence or 0) > (current.confidence or 0):
            best[key] = f
    return list(best.values())


def aggregate(findings: list[ReviewFinding]) -> list[ReviewFinding]:
    """Dedup findings, boost confidence when several agents flag the same line,
    and sort by severity then location."""
    deduped = _dedup_exact(findings)

    categories_per_line: dict[tuple, set] = {}
    for f in deduped:
        categories_per_line.setdefault((f.file, f.line), set()).add(f.category)

    scored: list[ReviewFinding] = []
    for f in deduped:
        agreement = len(categories_per_line[(f.file, f.line)])
        base = f.confidence if f.confidence is not None else _DEFAULT_CONFIDENCE
        confidence = min(1.0, base + _AGREEMENT_BOOST * (agreement - 1))
        scored.append(replace(f, confidence=confidence))

    scored.sort(
        key=lambda f: (-_SEVERITY_RANK.get(f.severity, 0), f.file, f.line or 0)
    )
    return scored
