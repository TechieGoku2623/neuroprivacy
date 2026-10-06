"""Run every Phase 0 harness and regenerate the memo and evaluation tables."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
HARNESSES = (
    HERE / "extraction_accuracy" / "probe_set" / "build.py",
    HERE / "extraction_accuracy" / "run.py",
    HERE / "statute_coverage" / "run.py",
    HERE / "policy_drift" / "probe_set" / "build.py",
    HERE / "policy_drift" / "run.py",
    HERE / "render_docs.py",
)


def main() -> None:
    for script in HARNESSES:
        print(f"\n=== {script.relative_to(ROOT)} ===\n")
        subprocess.run([sys.executable, str(script)], check=True, cwd=ROOT)


if __name__ == "__main__":
    main()
