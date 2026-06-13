from src.github.diff_parser import LineKind, parse_diff

SAMPLE = """diff --git a/foo.py b/foo.py
index 1111111..2222222 100644
--- a/foo.py
+++ b/foo.py
@@ -1,4 +1,4 @@
 def add(a, b):
-    return a - b
+    return a + b

 def mul(a, b):
"""

NEW_FILE = """diff --git a/new.py b/new.py
new file mode 100644
index 0000000..3333333
--- /dev/null
+++ b/new.py
@@ -0,0 +1,2 @@
+x = 1
+y = 2
"""


def test_parse_diff_basic():
    files = parse_diff(SAMPLE)
    assert len(files) == 1
    f = files[0]
    assert f.path == "foo.py"
    assert not f.is_new and not f.is_deleted
    assert f.added == 1
    assert f.removed == 1
    assert len(f.hunks) == 1


def test_parse_diff_line_mapping():
    f = parse_diff(SAMPLE)[0]
    added = [ln for h in f.hunks for ln in h.lines if ln.kind is LineKind.ADDED]
    removed = [ln for h in f.hunks for ln in h.lines if ln.kind is LineKind.REMOVED]
    assert added[0].new_lineno == 2
    assert added[0].old_lineno is None
    assert removed[0].old_lineno == 2
    assert removed[0].new_lineno is None


def test_parse_new_file():
    f = parse_diff(NEW_FILE)[0]
    assert f.is_new
    assert f.added == 2
    assert f.removed == 0


def test_parse_empty():
    assert parse_diff("") == []
    assert parse_diff("   \n") == []
