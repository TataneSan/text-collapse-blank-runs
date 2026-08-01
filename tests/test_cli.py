import io
import unittest
from contextlib import redirect_stdout, redirect_stderr

from text_collapse_blank_runs.cli import main


def run(argv, stdin_text=""):
    import sys
    old = sys.stdin
    sys.stdin = io.StringIO(stdin_text)
    out, err = io.StringIO(), io.StringIO()
    try:
        with redirect_stdout(out), redirect_stderr(err):
            code = main(argv)
    finally:
        sys.stdin = old
    return code, out.getvalue(), err.getvalue()


class TestCollapse(unittest.TestCase):
    def test_basic(self):
        code, out, _ = run(["-"], "a\n\n\n\nb\n")
        self.assertEqual(code, 0)
        self.assertEqual(out, "a\n\nb\n")

    def test_max_two(self):
        code, out, _ = run(["--max", "2", "-"], "a\n\n\n\n\nb\n")
        self.assertEqual(out, "a\n\n\nb\n")

    def test_max_zero(self):
        code, out, _ = run(["--max", "0", "-"], "a\n\nb\n")
        self.assertEqual(out, "a\nb\n")

    def test_whitespace_blank(self):
        code, out, _ = run(["-"], "a\n  \n\t\nb\n")
        self.assertEqual(out, "a\n\nb\n")

    def test_strict_empty(self):
        code, out, _ = run(["--no-whitespace-blank", "-"], "a\n  \nb\n")
        self.assertEqual(out, "a\n  \nb\n")

    def test_no_trailing_newline(self):
        code, out, _ = run(["-"], "a\n\n\nb")
        self.assertEqual(out, "a\n\nb")

    def test_check_pass(self):
        code, _, _ = run(["--check", "-q", "-"], "a\n\nb\n")
        self.assertEqual(code, 0)

    def test_check_fail(self):
        code, _, _ = run(["--check", "-q", "-"], "a\n\n\nb\n")
        self.assertEqual(code, 2)

    def test_json(self):
        import json as J
        code, out, _ = run(["--json", "--check", "-"], "a\n\n\nb\n")
        data = J.loads(out)
        self.assertEqual(data["blank_runs"], 1)
        self.assertEqual(data["violating_runs"], 1)


if __name__ == "__main__":
    unittest.main()
