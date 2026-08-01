#!/usr/bin/env python3
"""Collapse runs of consecutive blank lines to at most N.

Reads a text file (or stdin) and rewrites it so that no more than --max
(default 1) consecutive blank lines occur. A line is blank when it contains
no non-whitespace characters (with --whitespace-blank, the default) or when
it is strictly empty (with --strict-empty).

Exit codes:
  0  success
  1  I/O or CLI error
  2  --check mode: input contains at least one run longer than --max
"""
import argparse
import json
import sys


def parse_args(argv=None):
    p = argparse.ArgumentParser(
        description="Collapse runs of consecutive blank lines to at most N."
    )
    p.add_argument("file", nargs="?", default="-",
                   help="Text file to read (default: stdin, use '-' for stdin)")
    p.add_argument("--max", type=int, default=1,
                   help="Maximum consecutive blank lines kept (default: 1)")
    p.add_argument("--strict-empty", action="store_true",
                   help="Only strictly empty lines count as blank (default: whitespace-only also counts)")
    p.add_argument("--check", action="store_true",
                   help="Lint mode: print the collapsible runs and exit 2 when any run exceeds --max")
    p.add_argument("--json", action="store_true", help="Emit a JSON report (with --check)")
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    if args.max < 0:
        print("error: --max must be >= 0", file=sys.stderr)
        return 1

    def is_blank(line):
        s = line.rstrip("\n").rstrip("\r")
        return s == "" if args.strict_empty else s.strip() == ""

    try:
        fh = sys.stdin if args.file == "-" else open(args.file, encoding="utf-8")
    except OSError as e:
        print(f"error: cannot open {args.file}: {e}", file=sys.stderr)
        return 1

    out_lines = []
    runs = []       # (start_line, length) of each run longer than --max
    run_start = None
    run_len = 0
    total_lines = 0
    blanks_removed = 0

    with fh:
        for n, line in enumerate(fh, 1):
            total_lines = n
            stripped = line.rstrip("\n").rstrip("\r")
            if is_blank(line):
                if run_start is None:
                    run_start = n
                run_len += 1
                if run_len <= args.max:
                    out_lines.append("")
                else:
                    blanks_removed += 1
            else:
                if run_start is not None and run_len > args.max:
                    runs.append({"start": run_start, "length": run_len})
                run_start = None
                run_len = 0
                out_lines.append(stripped)
        if run_start is not None and run_len > args.max:
            runs.append({"start": run_start, "length": run_len})

    report = {
        "file": args.file,
        "lines_in": total_lines,
        "lines_out": len(out_lines),
        "blank_removed": blanks_removed,
        "max": args.max,
        "long_runs": runs,
    }

    if args.check:
        if args.json:
            print(json.dumps(report, indent=2, ensure_ascii=False))
        else:
            for r in runs:
                print(f"run of {r['length']} blank lines starting at line {r['start']}")
        return 2 if runs else 0

    sys.stdout.write("".join(l + "\n" for l in out_lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
