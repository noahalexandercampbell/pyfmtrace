from __future__ import annotations

import sys
from typing import Optional, Sequence

from pyfmtrace.cli import cli_main
from pyfmtrace.formatter import format_traceback
from pyfmtrace.parser import parse_traceback, Frame, Traceback


def _write_input(path: str, text: str) -> str:
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)
    return path


def test_main_prints_markdown_for_traceback(tmp_path, capsys):
    trace_text = (
        "Traceback (most recent call last):\n"
        '  File "app.py", line 12, in main\n'
        "    run()\n"
        '  File "runner.py", line 44, in run\n'
        "    launch(task)\n"
        "RuntimeError: task failed\n"
    )
    source = _write_input(str(tmp_path / "trace.txt"), trace_text)
    rc = cli_main([source])
    assert rc == 0
    output = capsys.readouterr().out
    assert "Exception: RuntimeError: task failed" in output
    assert "1. `app.py` — line 12, `main`" in output


def test_main_reads_stdin_when_source_omitted(monkeypatch, capsys):
    trace_text = (
        "Traceback (most recent call last):\n"
        "ValueError: boom\n"
    )
    monkeypatch.setattr(sys, "stdin", type("FakeStdin", (), {"read": lambda self: trace_text})())
    rc = cli_main([])
    assert rc == 0
    assert "ValueError: boom" in capsys.readouterr().out


def test_main_returns_nonzero_for_missing_file():
    rc = cli_main(["/tmp/does-not-exist-9218237492.txt"])
    assert rc == 1


def test_main_terminal_mode(tmp_path, capsys):
    trace_text = (
        "Traceback (most recent call last):\n"
        '  File "app.py", line 1, in main\n'
        "    raise ValueError('x')\n"
        "ValueError: x\n"
    )
    source = _write_input(str(tmp_path / "trace.txt"), trace_text)
    rc = cli_main(["-m", "terminal", source])
    assert rc == 0
    output = capsys.readouterr().out
    assert 'File "app.py", line 1, in main' in output


def test_main_plain_mode(tmp_path, capsys):
    trace_text = (
        "Traceback (most recent call last):\n"
        '  File "app.py", line 1, in main\n'
        "    raise ValueError('x')\n"
        "ValueError: x\n"
    )
    source = _write_input(str(tmp_path / "trace.txt"), trace_text)
    rc = cli_main(["-m", "plain", source])
    assert rc == 0
    output = capsys.readouterr().out
    assert "app.py | line 1 | main" in output


def test_main_compact_mode(tmp_path, capsys):
    trace_text = (
        "Traceback (most recent call last):\n"
        '  File "app.py", line 1, in main\n'
        "    raise ValueError('x')\n"
        "ValueError: x\n"
    )
    source = _write_input(str(tmp_path / "trace.txt"), trace_text)
    rc = cli_main(["-m", "compact", source])
    assert rc == 0
    output = capsys.readouterr().out
    assert "main @ app.py:1" in output


def test_main_hides_locals_with_flag(tmp_path, capsys):
    trace_text = (
        "Traceback (most recent call last):\n"
        '  File "app.py", line 1, in main\n'
        "    raise ValueError('x')\n"
        '    value = 42\n'
        "ValueError: x\n"
    )
    source = _write_input(str(tmp_path / "trace.txt"), trace_text)
    rc = cli_main(["--no-locals", source])
    assert rc == 0
    output = capsys.readouterr().out
    assert "Exception: ValueError: x" in output
    assert "Locals:" not in output


def test_parse_traceback_captures_frame():
    trace_text = (
        "Traceback (most recent call last):\n"
        '  File "app.py", line 5, in main\n'
        "    launch()\n"
        "ValueError: bad value\n"
    )
    trace = parse_traceback(trace_text)
    assert trace.exception_type == "ValueError"
    assert trace.exception_message == "bad value"
    assert len(trace.frames) == 1
    assert trace.frames[0].filepath == "app.py"
    assert trace.frames[0].lineno == 5
    assert trace.frames[0].func == "main"


def test_parse_traceback_with_locals():
    trace_text = (
        "Traceback (most recent call last):\n"
        '  File "app.py", line 2, in main\n'
        "    launch(value)\n"
        '    value = "invalid"\n'
        "ValueError: bad value\n"
    )
    trace = parse_traceback(trace_text)
    assert trace.frames[0].locals_summary == {"value": '"invalid"'}


def test_parse_traceback_missing_header():
    trace = parse_traceback("ValueError: oops")
    assert trace.exception_type == "ValueError"
    assert trace.exception_message == "oops"
    assert trace.frames == []


def test_format_markdown_includes_locals():
    trace_text = (
        "Traceback (most recent call last):\n"
        '  File "app.py", line 1, in main\n'
        "    raise ValueError('x')\n"
        '    value = 42\n'
        "ValueError: x\n"
    )
    trace = parse_traceback(trace_text)
    formatted = format_traceback(trace, mode="markdown", show_locals=True)
    assert "Exception: ValueError: x" in formatted
    assert "1." in formatted
    assert "Locals" in formatted


def test_format_plain_mode():
    trace_text = (
        "Traceback (most recent call last):\n"
        '  File "app.py", line 1, in main\n'
        "    raise ValueError('x')\n"
        "ValueError: x\n"
    )
    trace = parse_traceback(trace_text)
    formatted = format_traceback(trace, mode="plain", show_locals=False)
    assert "app.py | line 1 | main" in formatted


def test_format_terminal_mode():
    trace_text = (
        "Traceback (most recent call last):\n"
        '  File "app.py", line 1, in main\n'
        "    raise ValueError('x')\n"
        "ValueError: x\n"
    )
    trace = parse_traceback(trace_text)
    formatted = format_traceback(trace, mode="terminal", show_locals=False)
    assert 'File "app.py", line 1, in main' in formatted


def test_format_terminal_compact_mode():
    trace_text = (
        "Traceback (most recent call last):\n"
        '  File "app.py", line 1, in main\n'
        "    raise ValueError('x')\n"
        "ValueError: x\n"
    )
    trace = parse_traceback(trace_text)
    formatted = format_traceback(trace, mode="terminal", compact=True)
    assert "main @ app.py:1" in formatted


def test_max_frames():
    trace_text = (
        "Traceback (most recent call last):\n"
        '  File "a.py", line 1, in a\n'
        "    b()\n"
        '  File "b.py", line 1, in b\n'
        "    c()\n"
        '  File "c.py", line 1, in c\n'
        "    raise ValueError('x')\n"
        "ValueError: x\n"
    )
    trace = parse_traceback(trace_text)
    formatted = format_traceback(trace, max_frames=2)
    assert "a.py" in formatted
    assert "b.py" in formatted
    assert "c.py" not in formatted
