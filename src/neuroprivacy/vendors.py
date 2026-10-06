"""Resolve designed vendor fixtures and dated snapshots.

Public synthetic HTML only. No live fetch, no authenticated scrape.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from neuroprivacy.config import Settings, get_settings
from neuroprivacy.schemas import VendorSnapshot

VENDOR_FILES: dict[str, tuple[str, ...]] = {
    "vendor-a": ("vendor-a.html",),
    "vendor-b": ("vendor-b.html",),
    "vendor-c": ("vendor-c.html",),
    "vendor-d": ("vendor-d-2025-01.html", "vendor-d-2025-06.html"),
}

SNAPSHOT_DATES: dict[str, date] = {
    "vendor-a.html": date(2024, 6, 1),
    "vendor-b.html": date(2024, 6, 1),
    "vendor-c.html": date(2024, 6, 1),
    "vendor-d-2025-01.html": date(2025, 1, 15),
    "vendor-d-2025-06.html": date(2025, 6, 15),
}


def parse_since(value: str) -> date:
    return date.fromisoformat(value)


def resolve_doc(path: Path, settings: Settings | None = None) -> Path:
    cfg = settings or get_settings()
    candidate = path if path.is_absolute() else (Path.cwd() / path)
    if candidate.is_file():
        return candidate.resolve()
    sample = cfg.sample_dir / path.name
    if sample.is_file():
        return sample.resolve()
    raise FileNotFoundError(f"Policy document not found: {path}")


def resolve_vendor(vendor: str, settings: Settings | None = None) -> list[VendorSnapshot]:
    key = vendor.strip().lower()
    if key not in VENDOR_FILES:
        known = ", ".join(sorted(VENDOR_FILES))
        raise KeyError(f"Unknown vendor {vendor!r}. Designed fixtures: {known}.")
    cfg = settings or get_settings()
    snapshots: list[VendorSnapshot] = []
    for filename in VENDOR_FILES[key]:
        path = cfg.sample_dir / filename
        if not path.is_file():
            raise FileNotFoundError(f"Missing designed fixture: {path}")
        snapshots.append(
            VendorSnapshot(
                vendor_id=key,
                filename=filename,
                path=path,
                snapshot_date=SNAPSHOT_DATES[filename],
            )
        )
    return snapshots


def snapshots_since(snapshots: list[VendorSnapshot], since: date) -> list[VendorSnapshot]:
    selected = [item for item in snapshots if item.snapshot_date >= since]
    return selected or snapshots
