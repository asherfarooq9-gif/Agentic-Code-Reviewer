"""Load labelled eval cases (buggy diffs + ground-truth findings) from JSON."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from ..db.models import Category
from .metrics import ExpectedFinding


@dataclass(frozen=True)
class EvalCase:
    id: str
    description: str
    diff: str
    expected: list[ExpectedFinding]


def _parse_expected(raw: list) -> list[ExpectedFinding]:
    return [
        ExpectedFinding(
            file=str(item["file"]),
            line=int(item["line"]),
            category=Category(str(item["category"]).lower()),
        )
        for item in raw
    ]


def load_case(path: Path) -> EvalCase:
    data = json.loads(path.read_text(encoding="utf-8"))
    for field in ("id", "diff", "expected"):
        if field not in data:
            raise ValueError(f"Eval case {path.name} missing required field '{field}'")
    return EvalCase(
        id=str(data["id"]),
        description=str(data.get("description", "")),
        diff=str(data["diff"]),
        expected=_parse_expected(data["expected"]),
    )


def load_cases(cases_dir: str) -> list[EvalCase]:
    directory = Path(cases_dir)
    if not directory.is_dir():
        raise ValueError(f"Eval cases dir not found: {cases_dir}")
    paths = sorted(directory.glob("*.json"))
    if not paths:
        raise ValueError(f"No eval cases (*.json) found in {cases_dir}")
    return [load_case(p) for p in paths]
