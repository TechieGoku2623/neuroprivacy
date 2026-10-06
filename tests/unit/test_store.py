from __future__ import annotations

from pathlib import Path

from neuroprivacy.extractor import extract_rules
from neuroprivacy.store import count_extractions, write_extractions


def test_write_and_count_extractions(tmp_path: Path) -> None:
    rows = [
        extract_rules("<p>We collect neural data.</p>", "a"),
        extract_rules("<p>device data and the right to delete it.</p>", "b"),
    ]
    path = tmp_path / "extra.duckdb"
    write_extractions(path, rows)
    assert count_extractions(path) == 2
    write_extractions(path, rows[:1])
    assert count_extractions(path) == 1
