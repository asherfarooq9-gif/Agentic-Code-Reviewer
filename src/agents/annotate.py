"""Render parsed diffs with new-side line numbers for precise anchoring."""
from __future__ import annotations

from ..github.diff_parser import LineKind, ParsedFile


def annotate_file(pf: ParsedFile) -> str:
    header = pf.path
    if pf.is_new:
        header += " (new file)"
    elif pf.is_deleted:
        header += " (deleted)"

    lines: list[str] = [f"### {header}"]
    for hunk in pf.hunks:
        last = hunk.new_start + hunk.new_len - 1
        lines.append(f"@@ new lines {hunk.new_start}-{last} @@")
        for ln in hunk.lines:
            if ln.kind is LineKind.ADDED:
                marker, num = "+", ln.new_lineno
            elif ln.kind is LineKind.REMOVED:
                marker, num = "-", ln.old_lineno
            else:
                marker, num = " ", ln.new_lineno
            numtext = str(num) if num is not None else ""
            lines.append(f"{numtext:>5} {marker} {ln.content}")
    return "\n".join(lines)


def annotate_diff(files: list[ParsedFile]) -> str:
    return "\n\n".join(annotate_file(f) for f in files)
