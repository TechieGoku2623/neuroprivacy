from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from neuroprivacy.vendors import parse_since, resolve_doc, resolve_vendor, snapshots_since


def test_resolve_vendor_d_has_two_dated_snapshots() -> None:
    snaps = resolve_vendor("vendor-d")
    assert len(snaps) == 2
    assert snaps[0].snapshot_date == date(2025, 1, 15)
    assert snaps[1].snapshot_date == date(2025, 6, 15)


def test_resolve_unknown_vendor() -> None:
    with pytest.raises(KeyError):
        resolve_vendor("vendor-z")


def test_snapshots_since_filters() -> None:
    snaps = resolve_vendor("vendor-d")
    after_march = snapshots_since(snaps, date(2025, 3, 1))
    assert len(after_march) == 1
    assert after_march[0].filename == "vendor-d-2025-06.html"


def test_resolve_doc_and_parse_since() -> None:
    assert parse_since("2025-01-01") == date(2025, 1, 1)
    path = resolve_doc(Path("data/sample/vendor-a.html"))
    assert path.is_file()
    with pytest.raises(FileNotFoundError):
        resolve_doc(Path("missing-policy.html"))
