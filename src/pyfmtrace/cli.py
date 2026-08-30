from __future__ import annotations

import argparse
import sys
from typing import List, Optional, Sequence

from pyfmtrace.formatter import format_traceback
from pyfmtrace.parser import parse_traceback


def _read_input(source: Optional[str]) -> str:
    if source is None:
        return sys.stdin.read()
    try:
        with open(source, "r", encoding="utf-8") as handle:
            return handle.read()
    except OSError as exc:
        print(f"pyfmtrace: cannot read file: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="pyfmtrace",
        description="Parse, format, and analyze Python tracebacks.",
    )
    parser.add_argument(
        "source",
        nargs="?",
        help="Path to a traceback text file. Reads stdin when omitted.",
    )
    parser.add_argument(
        "-m",
        "--mode",
        choices=["markdown", "terminal", "plain", "compact"],
        default="markdown",
        help="Output format. Default: markdown",
    )
    parser.add_argument(
        "--no-locals",
        action="store_true",
        help="Hide captured local variables from frames.",
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        default=None,
        help="Limit the number of frames included.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="pyfmtrace 0.1.0",
    )

    args = parser.parse_args(list(argv) if argv is not None else None)

    try:
        text = _read_input(args.source)
    except SystemExit:
        return 1

    trace = parse_traceback(text)
    output = format_traceback(
        trace,
        mode=args.mode,
        show_locals=not args.no_locals,
        max_frames=args.max_frames,
        compact=args.mode == "compact",
    )
    print(output)
    return 0


def cli_main(argv: Optional[Sequence[str]] = None) -> int:
    return main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
