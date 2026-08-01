"""Collapse runs of consecutive blank lines into at most N blank lines.

Reads from stdin or a file, writes the collapsed text to stdout. Blank means
empty or whitespace-only (--no-whitespace-blank to require strictly empty).

Exit codes:
    0 - success (or check passed)
    1 - I/O or CLI error
    2 - --check mode and at least one run exceeds the limit
"""

from __future__ import annotations

import argparse
import json
import sys


def _parse_args(argv):
    parser = argparse.ArgumentParser(
        prog="text-collapse-blank-runs",
        description="Collapse runs of consecutive blank lines into at most N blank lines.",
    )
    parser.add_argument("file", nargs="?", default="-",
                        help="text file to read (default: stdin).")
    parser.add_argument("--max", type=int, default=1, metavar="N",
                        help="maximum consecutive blank lines to keep (default: 1).")
    parser.add_argument("--whitespace-blank", dest="whitespace_blank",
                        action="store_true", default=True,
                        help="whitespace-only lines count as blank (default).")
    parser.add_argument("--no-whitespace-blank", dest="whitespace_blank",
                        action="store_false",
                        help="require strictly empty lines (no spaces/tabs).")
    parser.add_argument("--check", action="store_true",
                        help="only verify; exit 2 if a run exceeds the limit.")
    parser.add_argument("--json", action="store_true",
                        help="emit a JSON report.")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="in check mode, suppress non-JSON output.")
    return parser.parse_args(argv)


def _is_blank(line, whitespace_blank):
    if line == "":
        return True
    if whitespace_blank:
        return line.strip(" \t") == ""
    return False


def _process(text, max_blanks, whitespace_blank):
    """Return (out_text, total_runs, violating_runs)."""
    trailing = text.endswith("\n")
    lines = text.split("\n")
    if trailing:
        lines.pop()
    out = []
    runs = 0
    violating = 0
    run = 0
    for line in lines:
        if _is_blank(line, whitespace_blank):
            run += 1
            if run <= max_blanks:
                out.append("")
        else:
            if run > 0:
                runs += 1
                if run > max_blanks:
                    violating += 1
            run = 0
            out.append(line)
    if run > 0:
        runs += 1
        if run > max_blanks:
            violating += 1
    out_text = "\n".join(out)
    if trailing:
        out_text += "\n"
    return out_text, runs, violating


def main(argv=None):
    args = _parse_args(argv)
    if args.max < 0:
        print("error: --max must be >= 0", file=sys.stderr)
        return 1

    try:
        if args.file == "-":
            text = sys.stdin.read()
        else:
            with open(args.file, "r", encoding="utf-8") as fh:
                text = fh.read()
    except OSError as exc:
        print(f"error: cannot read {args.file}: {exc}", file=sys.stderr)
        return 1

    out, runs, violating = _process(text, args.max, args.whitespace_blank)
    report = {
        "file": args.file,
        "blank_runs": runs,
        "violating_runs": violating,
        "max_blanks": args.max,
        "check": args.check,
        "ok": violating == 0,
    }

    if args.check:
        if args.json:
            print(json.dumps(report, indent=2))
        elif not args.quiet:
            status = "ok" if violating == 0 else f"{violating}/{runs} run(s) exceed {args.max} blank(s)"
            print(f"check: {status}", file=sys.stderr)
        return 0 if violating == 0 else 2

    sys.stdout.write(out)
    if args.json:
        print(json.dumps(report, indent=2), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
