import pytest

from src.agents.tools import CodebaseTools


def _make_repo(tmp_path):
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    (pkg / "a.py").write_text(
        "def helper(x):\n    return x + 1\n\n\ndef main():\n    return helper(5)\n",
        encoding="utf-8",
    )
    (pkg / "b.py").write_text(
        "from pkg.a import helper\n\nval = helper(10)\n", encoding="utf-8"
    )
    return tmp_path


def test_read_file_full(tmp_path):
    tools = CodebaseTools(str(_make_repo(tmp_path)))
    assert "def helper" in tools.read_file("pkg/a.py")


def test_read_around_is_line_numbered(tmp_path):
    tools = CodebaseTools(str(_make_repo(tmp_path)))
    text = tools.read_around("pkg/a.py", 5, context=2)
    assert "def main" in text
    assert "5:" in text


def test_search_codebase_finds_all(tmp_path):
    tools = CodebaseTools(str(_make_repo(tmp_path)))
    files = {h.file for h in tools.search_codebase(r"helper")}
    assert "pkg/a.py" in files
    assert "pkg/b.py" in files


def test_get_function_callers_excludes_definition(tmp_path):
    tools = CodebaseTools(str(_make_repo(tmp_path)))
    hits = tools.get_function_callers("helper")
    assert all("def helper" not in h.text for h in hits)
    assert any(h.file == "pkg/b.py" for h in hits)


def test_path_traversal_blocked(tmp_path):
    tools = CodebaseTools(str(_make_repo(tmp_path)))
    with pytest.raises(ValueError):
        tools.read_file("../secret.txt")


def test_missing_root_raises():
    with pytest.raises(ValueError):
        CodebaseTools("does-not-exist-xyz-123")
