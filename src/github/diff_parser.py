"""Parse unified diffs into structured files/hunks/lines with line mapping.

Wraps the battle-tested `unidiff` library; adds frozen dataclasses and
old/new line-number mapping that later milestones use to anchor comments.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from unidiff import PatchSet


class LineKind(StrEnum):
    ADDED = "added"
    REMOVED = "removed"
    CONTEXT = "context"


@dataclass(frozen=True)
class ParsedLine:
    kind: LineKind
    content: str
    old_lineno: int | None
    new_lineno: int | None


@dataclass(frozen=True)
class ParsedHunk:
    old_start: int
    old_len: int
    new_start: int
    new_len: int
    lines: list[ParsedLine]


@dataclass(frozen=True)
class ParsedFile:
    path: str
    old_path: str
    hunks: list[ParsedHunk]
    is_new: bool
    is_deleted: bool

    @property
    def added(self) -> int:
        return sum(1 for h in self.hunks for ln in h.lines if ln.kind is LineKind.ADDED)

    @property
    def removed(self) -> int:
        return sum(1 for h in self.hunks for ln in h.lines if ln.kind is LineKind.REMOVED)


def _line_kind(line) -> LineKind:
    if line.is_added:
        return LineKind.ADDED
    if line.is_removed:
        return LineKind.REMOVED
    return LineKind.CONTEXT


def parse_diff(diff_text: str) -> list[ParsedFile]:
    """Parse a unified diff string into a list of ParsedFile. Empty -> []."""
    if not diff_text or not diff_text.strip():
        return []

    patch = PatchSet(diff_text)
    files: list[ParsedFile] = []
    for pf in patch:
        hunks: list[ParsedHunk] = []
        for h in pf:
            lines = [
                ParsedLine(
                    kind=_line_kind(ln),
                    content=ln.value.rstrip("\n"),
                    old_lineno=ln.source_line_no,
                    new_lineno=ln.target_line_no,
                )
                for ln in h
            ]
            hunks.append(
                ParsedHunk(
                    old_start=h.source_start,
                    old_len=h.source_length,
                    new_start=h.target_start,
                    new_len=h.target_length,
                    lines=lines,
                )
            )
        files.append(
            ParsedFile(
                path=pf.path,
                old_path=pf.source_file,
                hunks=hunks,
                is_new=pf.is_added_file,
                is_deleted=pf.is_removed_file,
            )
        )
    return files
