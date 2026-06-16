"""Gather surrounding-code context for changed files using CodebaseTools."""
from __future__ import annotations

from ..github.diff_parser import ParsedFile
from .tools import CodebaseTools

_CONTEXT_LINES = 8


def gather_context(tools: CodebaseTools, files: list[ParsedFile]) -> str:
    """Read a window of surrounding code around each changed file's first hunk.

    Missing files (e.g. not present in the local checkout) are skipped, so a
    partial checkout never crashes the review.
    """
    blocks: list[str] = []
    for pf in files:
        if pf.is_deleted or not pf.hunks:
            continue
        anchor = pf.hunks[0].new_start
        try:
            snippet = tools.read_around(pf.path, anchor, context=_CONTEXT_LINES)
        except ValueError:
            continue
        blocks.append(f"# {pf.path} (surrounding code)\n{snippet}")
    return "\n\n".join(blocks)
