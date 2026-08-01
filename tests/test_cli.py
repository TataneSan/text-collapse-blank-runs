import io
import json
import sys
import unittest
from contextlib import redirect_stdout

from text_collapse_blank_runs import cli


def run(argv, stdin_text):
    old = sys.stdin
    sys.stdin = io.StringIO(stdin_text)
    out = io.StringIO()
    try:
        with redirect_stdout(out):
            code = cli.main(argv)
    finally:
        sys.stdin = old
    return code, out.getvalue()


class TestCollapse(unittest.TestCase):
    def test_default_one(self):
        code, out = run(["-"], "a\n\n\n\nb\n")
        self.assertEqual(out, "a\n\nb\n")

    def test_max_zero(self):
        code, out = run(["--max", "0", "-"], "a\n\n\nb\n")
        self.assertEqual(out, "a\nb\n")

    def test_max_two(self):
        code, out = run(["--max", "2", "-"], "a\n\n\n\n\nb\n")
        self.assertEqual(out, "a\n\n\nb\n")

    def test_whitespace_blank(self):
        code, out = run(["-"], "a\n   \n\t\nb\n")
        self.assertEqual(out, "a\n\nb\n")

    def test_strict_empty(self):
        # With --strict-empty, a " "-only line is NOT blank: it passes through
        # and interrupts the blank run.
        code, out = run(["--strict-empty", "-"], "a\n \n\nb\n")
        self.assertEqual(out, "a\n \n\nb\n")
        code, out = run(["--strict-empty", "-"], "a\n\n\n\nb\n")
        self.assertEqual(out, "a\n\nb\n")

    def test_check_violation(self):
        code, out = run(["--check", "-"], "a\n\n\nb\n")
        self.assertEqual(code, 2)
        self.assertIn("line 2", out)

    def test_check_clean(self):
        code, _ = run(["--check", "-"], "a\n\nb\n")
        self.assertEqual(code, 0)

    def test_json(self):
        code, out = run(["--check", "--json", "-"], "a\n\n\n\nb\n")
        d = json.loads(out)
        self.assertEqual(d["blank_removed"], 2)
        self.assertEqual(len(d["long_runs"]), 1)


if __name__ == "__main__":
    unittest.main()
