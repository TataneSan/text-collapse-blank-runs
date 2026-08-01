# text-collapse-blank-runs

Collapse runs of consecutive blank lines in a text file down to at most N
(default 1) — like `cat -s`, but with a configurable cap and a lint mode.

Pure Python standard library. No dependencies.

## Features

- Keeps at most `--max N` consecutive blank lines (N can be 0)
- Whitespace-only lines count as blank by default, `--strict-empty` opts out
- `--check` lint mode lists oversized runs and exits 2 (CI-friendly)
- `--json` machine-readable report
- Reads stdin when the file is omitted or `-`

## Install

```bash
pip install .
# or directly from GitHub
pip install git+https://github.com/TataneSan/text-collapse-blank-runs.git
```

## Usage

```bash
text-collapse-blank-runs notes.txt
text-collapse-blank-runs --max 0 file.txt            # remove all blank lines
cat doc.md | text-collapse-blank-runs --max 2 -
text-collapse-blank-runs --check --max 1 doc.md      # lint: exit 2 when runs exceed 1
text-collapse-blank-runs --check --json doc.md       # lint report as JSON
```

## Example

```bash
$ printf 'a\n\n\n\nb\n' | text-collapse-blank-runs -
a

b
```

## Exit codes

| Code | Meaning                                          |
| ---: | ------------------------------------------------ |
|    0 | Success                                          |
|    1 | I/O or CLI error                                 |
|    2 | `--check` and a blank run exceeds `--max`        |

## License

MIT
