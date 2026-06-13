from src.agents.annotate import annotate_diff
from src.github.diff_parser import parse_diff

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


def test_annotate_includes_path_and_content():
    text = annotate_diff(parse_diff(SAMPLE))
    assert "foo.py" in text
    assert "return a + b" in text


def test_annotate_marks_new_line_number():
    text = annotate_diff(parse_diff(SAMPLE))
    # the added line is new-side line 2
    assert "2 +" in text
