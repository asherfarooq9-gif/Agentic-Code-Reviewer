from src.agents.context import gather_context
from src.agents.tools import CodebaseTools
from src.github.diff_parser import parse_diff

DIFF = """diff --git a/pkg/a.py b/pkg/a.py
--- a/pkg/a.py
+++ b/pkg/a.py
@@ -1,2 +1,2 @@
 def helper(x):
-    return x + 1
+    return x + 2
"""


def test_gather_context_includes_surrounding_code(tmp_path):
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    (pkg / "a.py").write_text("def helper(x):\n    return x + 2\n", encoding="utf-8")
    tools = CodebaseTools(str(tmp_path))
    ctx = gather_context(tools, parse_diff(DIFF))
    assert "pkg/a.py" in ctx
    assert "helper" in ctx


def test_gather_context_skips_missing_files(tmp_path):
    tools = CodebaseTools(str(tmp_path))
    # file referenced by the diff is absent from the checkout -> skipped, no crash
    assert gather_context(tools, parse_diff(DIFF)) == ""
