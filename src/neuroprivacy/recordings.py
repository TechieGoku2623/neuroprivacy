"""Write asciinema v2 JSONL recordings from real command output."""

from __future__ import annotations

import json
import time
from collections.abc import Sequence
from pathlib import Path

from typer.testing import CliRunner

from neuroprivacy.cli import app
from neuroprivacy.config import get_settings


def write_cast(
    path: Path, title: str, chunks: Sequence[str], width: int = 120, height: int = 40
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = {
        "version": 2,
        "width": width,
        "height": height,
        "timestamp": int(time.time()),
        "title": title,
        "env": {"SHELL": "/bin/bash", "TERM": "xterm-256color"},
    }
    lines = [json.dumps(header, separators=(",", ":"))]
    elapsed = 0.05
    for chunk in chunks:
        payload = chunk if chunk.endswith("\n") else f"{chunk}\n"
        lines.append(json.dumps([round(elapsed, 6), "o", payload], separators=(",", ":")))
        elapsed += 0.04
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _run(args: list[str]) -> str:
    runner = CliRunner()
    result = runner.invoke(app, args)
    header = "$ neuroprivacy " + " ".join(args)
    body = result.stdout
    if result.exit_code != 0:
        body = f"{body}\n[exit {result.exit_code}]\n"
    return f"{header}\n{body}"


def record_all() -> list[Path]:
    demo_dir = get_settings().repo_root / "demo"
    jobs = (
        (
            "01-extract-with-spans.cast",
            "extract vendor-a with spans",
            _run(["extract", "--doc", "data/sample/vendor-a.html"]),
        ),
        (
            "02-audit-and-conflicts.cast",
            "audit vendor-b and vendor-c conflicts",
            _run(["audit", "--vendor", "vendor-b"])
            + "\n"
            + _run(["audit", "--vendor", "vendor-c", "--show-conflicts"]),
        ),
        (
            "03-drift-and-report.cast",
            "vendor-d drift and HTML report",
            _run(["diff", "--vendor", "vendor-d", "--since", "2025-01-01"])
            + "\n"
            + _run(["report"]),
        ),
    )
    written: list[Path] = []
    for name, title, text in jobs:
        path = demo_dir / name
        write_cast(path, title, text.splitlines())
        written.append(path)
    return written
