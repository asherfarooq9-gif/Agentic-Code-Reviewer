"""Codebase context tools: let the reviewer read surrounding code safely.

Operates on a local checkout of the repository being reviewed. All paths are
constrained to the repo root (path-traversal guarded).
"""
from __future__ import annotations

import re
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

_DEFAULT_CONTEXT = 5
_MAX_RESULTS = 50
_SKIP_DIRS = {
    ".git",
    "__pycache__",
    ".venv",
    "node_modules",
    ".ruff_cache",
    ".pytest_cache",
}


@dataclass(frozen=True)
class SearchHit:
    file: str
    line: int
    text: str


class CodebaseTools:
    """Read files and search a local repo checkout, scoped to its root."""

    def __init__(self, root: str) -> None:
        self._root = Path(root)
        if not self._root.is_dir():
            raise ValueError(f"Repo root not found: {root}")

    def read_file(
        self, rel_path: str, *, start: int | None = None, end: int | None = None
    ) -> str:
        """Return file contents. With start/end, return a line-numbered slice."""
        path = self._safe(rel_path)
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        if start is None:
            return "\n".join(lines)
        first = max(1, start)
        last = min(len(lines), end or len(lines))
        return "\n".join(f"{i + 1}: {lines[i]}" for i in range(first - 1, last))

    def read_around(self, rel_path: str, line: int, *, context: int = _DEFAULT_CONTEXT) -> str:
        """Read a line-numbered window around a line."""
        return self.read_file(rel_path, start=line - context, end=line + context)

    def search_codebase(
        self, pattern: str, *, glob: str = "*.py", max_results: int = _MAX_RESULTS
    ) -> list[SearchHit]:
        """Regex-search files matching glob. Returns up to max_results hits."""
        regex = re.compile(pattern)
        hits: list[SearchHit] = []
        for path in self._iter_files(glob):
            try:
                content = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for lineno, line in enumerate(content.splitlines(), 1):
                if regex.search(line):
                    rel = str(path.relative_to(self._root)).replace("\\", "/")
                    hits.append(SearchHit(rel, lineno, line.strip()))
                    if len(hits) >= max_results:
                        return hits
        return hits

    def get_function_callers(
        self, name: str, *, glob: str = "*.py", max_results: int = _MAX_RESULTS
    ) -> list[SearchHit]:
        """Find call sites of `name(`, excluding its definition lines."""
        call_pattern = rf"(?<![\w.]){re.escape(name)}\s*\("
        def_regex = re.compile(rf"\bdef\s+{re.escape(name)}\b")
        hits: list[SearchHit] = []
        for hit in self.search_codebase(call_pattern, glob=glob, max_results=max_results * 2):
            if def_regex.search(hit.text):
                continue
            hits.append(hit)
            if len(hits) >= max_results:
                break
        return hits

    def _safe(self, rel_path: str) -> Path:
        root = self._root.resolve()
        path = (self._root / rel_path).resolve()
        if root != path and root not in path.parents:
            raise ValueError(f"Path escapes repo root: {rel_path}")
        if not path.is_file():
            raise ValueError(f"File not found: {rel_path}")
        return path

    def _iter_files(self, glob: str) -> Iterator[Path]:
        for path in self._root.rglob(glob):
            if any(part in _SKIP_DIRS for part in path.parts):
                continue
            if path.is_file():
                yield path
