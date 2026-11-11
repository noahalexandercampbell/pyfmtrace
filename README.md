# pyfmtrace

Parse, format, and analyze Python tracebacks from the terminal.

## About

`pyfmtrace` turns raw CPython traceback text into structured frames and renders them in formats designed for debugging, issue reports, and documentation. It is a local-only CLI tool with no runtime dependencies beyond the Python standard library.

## Features

- Parse standard tracebacks into structured frames with file, line, function, code, and locals summaries.
- Render formatted output in multiple modes:
  - `markdown` — structured issue / README reports
  - `terminal` — readable debugging output
  - `plain` — clean minimal frames
  - `compact` — one-line frame summaries
- Filter frames with `--max-frames`.
- Hide or show captured locals with `--no-locals`.
- Read from a file path or stdin for shell pipelines.

## Installation

```bash
git clone https://github.com/noahalexandercampbell/pyfmtrace.git
cd pyfmtrace
python -m pip install -e .
```

## Usage

```bash
# pipe a traceback from a test run
python -m pytest --tb=long | pyfmtrace

# format a saved traceback file
pyfmtrace failures/long_traceback.txt

# compact single-line frames
pyfmtrace trace.txt --mode compact

# hide locals
pyfmtrace trace.txt --no-locals

# limit frames
pyfmtrace trace.txt --max-frames 5
```

## Project structure

```
.github/
  workflows/
    ci.yml
.gitignore
LICENSE
pyproject.toml
README.md
src/
  pyfmtrace/
    __init__.py
    cli.py
    formatter.py
    parser.py
tests/
  test_pyfmtrace.py
```

## Tags

`cli`, `debugging`, `traceback`, `developer-tools`, `python`, `traceback-parser`
