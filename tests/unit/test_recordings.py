from __future__ import annotations

from pathlib import Path

from neuroprivacy.recordings import record_all, write_cast


def test_write_cast_is_asciinema_v2(tmp_path: Path) -> None:
    path = tmp_path / "demo.cast"
    write_cast(path, "demo", ["hello", "world"])
    text = path.read_text(encoding="utf-8")
    first, *rest = text.strip().splitlines()
    assert '"version":2' in first or '"version": 2' in first
    assert rest[0].startswith("[")
    assert "hello" in rest[0]


def test_record_all_writes_three_casts() -> None:
    written = record_all()
    names = {path.name for path in written}
    assert names == {
        "01-extract-with-spans.cast",
        "02-audit-and-conflicts.cast",
        "03-drift-and-report.cast",
    }
    for path in written:
        assert path.is_file()
        assert '"version":2' in path.read_text(encoding="utf-8").splitlines()[0]
