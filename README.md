# text-collapse-blank-runs

Collapse runs of consecutive blank lines into at most N blank lines
(default 1). Reads from a file or stdin, writes the result to stdout.

## Features

- Collapses any run of blank (empty or whitespace-only) lines into a single
  one by default; `--max N` keeps up to N blank lines
- `--whitespace-blank` considers lines containing only spaces/tabs as blank
  (default: yes; use `--no-whitespace-blank` for strict empty lines)
- Preserves the trailing newline of the input
- `--check` CI mode: exit 2 when the file contains a run longer than the limit
- `--json` machine-readable report
- Pure standard library, Python >= 3.9

## Installation

```bash
pip install .
# or directly from GitHub
pip install git+https://github.com/TataneSan/text-collapse-blank-runs.git
```

## Usage

```bash
# Basic: collapse to 1 blank line max (stdin)
printf 'a\n\n\n\nb\n' | text-collapse-blank-runs -
# a
# 
# b

# Keep up to 2 blank lines
text-collapse-blank-runs --max 2 long-doc.txt

# Strict mode: only truly empty lines count
text-collapse-blank-runs --no-whitespace-blank spaced.txt

# CI check: exit 2 if any run exceeds N blanks
text-collapse-blank-runs --check --max 1 file.txt

# JSON report
text-collapse-blank-runs --json file.txt
```

### Options

| Flag | Description |
|---|---|
| `--max N` | maximum consecutive blank lines to keep (default 1) |
| `--whitespace-blank` / `--no-whitespace-blank` | whitespace-only lines count as blank (default: yes) |
| `--check` | only verify, exit 2 if a run exceeds N blanks |
| `--json` | emit a JSON report |
| `-q, --quiet` | in check mode, suppress non-JSON output |

## Exit codes

- `0` — success (or check passed)
- `1` — I/O or CLI error
- `2` — check failed (at least one run exceeds the limit)

## License

MIT — see [LICENSE](LICENSE).
