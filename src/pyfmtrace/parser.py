from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Frame:
    filepath: str
    lineno: int
    func: str
    code_line: str
    locals_summary: dict[str, str] = field(default_factory=dict)


@dataclass
class Traceback:
    message: str
    exception_type: str
    exception_message: str
    frames: List[Frame] = field(default_factory=list)


_FRAME_RE = re.compile(
    r'^\s*File ["\']?(?P<file>[^"\']+)["\']?, line (?P<lineno>\d+), in (?P<func>.+)$'
)
_EXC_RE = re.compile(r"^(?P<type>[A-Za-z_][A-Za-z0-9_.]*)(?::\s*(?P<msg>.+))?$")
_MORE_RE = re.compile(r"^\s*\((?P<more>\d+) more.*\)$")
_HIDDEN_RE = re.compile(r"^\s*\[(?P<hidden>\d+) frames? hidden.*\]$")
_LOCAL_RE = re.compile(r"^\s*(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>.+)$")


def parse_traceback(text: str) -> Traceback:
    """Parse a CPython-style traceback string into a structured Traceback."""
    lines = text.splitlines()
    frames: list[Frame] = []
    exception_type = ""
    exception_message = ""
    in_traceback_block = False

    i = 0
    while i < len(lines):
        line = lines[i].rstrip("\n")
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if stripped.startswith("Traceback (most recent call last):"):
            in_traceback_block = True
            i += 1
            continue

        if stripped.startswith("The above exception was the direct cause of the following exception:"):
            i += 1
            continue

        if in_traceback_block:
            frame_match = _FRAME_RE.match(stripped)
            if frame_match:
                filepath = frame_match.group("file")
                lineno = int(frame_match.group("lineno"))
                func = frame_match.group("func")
                code_line = ""
                locals_summary: dict[str, str] = {}

                i += 1
                while i < len(lines):
                    inner = lines[i].rstrip("\n")
                    inner_stripped = inner.strip()
                    if not inner_stripped:
                        i += 1
                        break
                    if inner_stripped.startswith("File "):
                        break
                    if _EXC_RE.match(inner_stripped):
                        break
                    if _MORE_RE.match(inner_stripped) or _HIDDEN_RE.match(inner_stripped):
                        i += 1
                        break
                    if not code_line:
                        code_line = inner_stripped
                    else:
                        local_match = _LOCAL_RE.match(inner_stripped)
                        if local_match:
                            locals_summary[local_match.group("name")] = local_match.group(
                                "value"
                            ).strip()
                    i += 1
                frames.append(
                    Frame(
                        filepath=filepath,
                        lineno=lineno,
                        func=func,
                        code_line=code_line,
                        locals_summary=locals_summary,
                    )
                )
                continue

            exc_match = _EXC_RE.match(stripped)
            if exc_match:
                exception_type = exc_match.group("type")
                exception_message = exc_match.group("msg") or ""
                i += 1
                continue

            if _MORE_RE.match(stripped) or _HIDDEN_RE.match(stripped):
                i += 1
                continue

            i += 1
            continue

        exc_match = _EXC_RE.match(stripped)
        if exc_match:
            exception_type = exc_match.group("type")
            exception_message = exc_match.group("msg") or ""
            i += 1
            continue

        i += 1

    message = f"{exception_type}: {exception_message}".strip(": ") if exception_type else ""
    return Traceback(
        message=message,
        exception_type=exception_type,
        exception_message=exception_message,
        frames=frames,
    )
