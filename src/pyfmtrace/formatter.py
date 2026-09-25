from __future__ import annotations

from typing import List, Optional

from pyfmtrace.parser import Frame, Traceback

Mode = str


def _terminal_frame(frame: Frame, index: int, show_locals: bool) -> str:
    header = f"  {index + 1}. File \"{frame.filepath}\", line {frame.lineno}, in {frame.func}"
    parts = [header]
    if frame.code_line:
        parts.append(f"       {frame.code_line}")
    if show_locals and frame.locals_summary:
        parts.append("       Locals:")
        for name, value in frame.locals_summary.items():
            parts.append(f"         {name} = {value}")
    return "\n".join(parts)


def _markdown_frame(frame: Frame, index: int, show_locals: bool) -> str:
    header = f"{index + 1}. `{frame.filepath}` — line {frame.lineno}, `{frame.func}`"
    parts = [header]
    if frame.code_line:
        parts.append(f"   ```python\n   {frame.code_line}\n   ```")
    if show_locals and frame.locals_summary:
        parts.append("   **Locals:**")
        for name, value in frame.locals_summary.items():
            parts.append(f"   - `{name}` = {value}")
    return "\n".join(parts)


def _compact_frame(frame: Frame, index: int) -> str:
    code = f" — {frame.code_line}" if frame.code_line else ""
    return f"{index + 1}. {frame.func} @ {frame.filepath}:{frame.lineno}{code}"


def _plain_frame(frame: Frame, index: int, show_locals: bool) -> str:
    header = f"{index + 1}. {frame.filepath} | line {frame.lineno} | {frame.func}"
    parts = [header]
    if frame.code_line:
        parts.append(f"   {frame.code_line}")
    if show_locals and frame.locals_summary:
        parts.append("   Locals:")
        for name, value in frame.locals_summary.items():
            parts.append(f"     {name} = {value}")
    return "\n".join(parts)


def format_traceback(
    trace: Traceback,
    mode: Mode = "markdown",
    show_locals: bool = True,
    max_frames: Optional[int] = None,
    compact: bool = False,
) -> str:
    frames = trace.frames
    if max_frames is not None and max_frames >= 0:
        frames = frames[:max_frames]

    if compact and mode != "terminal":
        mode = "terminal"

    parts: List[str] = []

    if trace.message:
        parts.append(f"Exception: {trace.message}")
    else:
        parts.append("Exception: (unknown)")

    if not frames:
        parts.append("  (no frames captured)")
        return "\n".join(parts)

    parts.append("")

    for idx, frame in enumerate(frames):
        if compact:
            parts.append(_compact_frame(frame, idx))
        elif mode == "markdown":
            parts.append(_markdown_frame(frame, idx, show_locals))
        elif mode == "plain":
            parts.append(_plain_frame(frame, idx, show_locals))
        else:
            parts.append(_terminal_frame(frame, idx, show_locals))

    return "\n".join(parts)
