from __future__ import annotations

from pathlib import Path

from neuroprivacy.diffing import vendor_diff
from neuroprivacy.report import build_report_html, write_report


def test_report_html_includes_all_vendors_and_disclaimer(tmp_path: Path) -> None:
    html = build_report_html()
    assert "vendor-a" in html
    assert "vendor-b" in html
    assert "vendor-c" in html
    assert "vendor-d" in html
    assert "not a legal conclusion" in html
    assert "discloses_sharing" in html
    path = write_report(tmp_path / "index.html")
    assert path.is_file()
    assert "CO-DELETE" in path.read_text(encoding="utf-8")


def test_vendor_a_diff_needs_two_snapshots() -> None:
    import pytest

    with pytest.raises(ValueError, match="Need two dated snapshots"):
        vendor_diff("vendor-a", "2020-01-01")


def test_vendor_d_diff_removes_sharing() -> None:
    older, newer, diffs = vendor_diff("vendor-d", "2025-01-01")
    assert older.filename.startswith("vendor-d-2025-01")
    assert newer.filename.startswith("vendor-d-2025-06")
    sharing = next(item for item in diffs if item.name == "discloses_sharing")
    assert sharing.before is True
    assert sharing.after is False
