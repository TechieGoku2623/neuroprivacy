"""Dated field diffs between designed policy snapshots."""

from __future__ import annotations

from pathlib import Path

from neuroprivacy.extractor import extract_policy
from neuroprivacy.schemas import FIELD_NAMES, FieldDiff, PolicyExtraction, VendorSnapshot
from neuroprivacy.vendors import parse_since, resolve_vendor, snapshots_since


def extract_snapshot(snapshot: VendorSnapshot, cache_path: Path | None = None) -> PolicyExtraction:
    html = snapshot.path.read_text(encoding="utf-8")
    return extract_policy(
        html,
        doc_id=f"{snapshot.vendor_id}-{snapshot.snapshot_date.isoformat()}",
        cache_path=cache_path,
    )


def field_diffs(
    before: PolicyExtraction, after: PolicyExtraction, older: VendorSnapshot, newer: VendorSnapshot
) -> list[FieldDiff]:
    diffs: list[FieldDiff] = []
    for name in FIELD_NAMES:
        left = before.fields[name]
        right = after.fields[name]
        if left.value == right.value:
            continue
        diffs.append(
            FieldDiff(
                name=name,
                before=left.value,
                after=right.value,
                before_span=left.span,
                after_span=right.span,
                before_date=older.snapshot_date,
                after_date=newer.snapshot_date,
            )
        )
    return diffs


def vendor_diff(
    vendor: str,
    since: str,
    cache_path: Path | None = None,
) -> tuple[VendorSnapshot, VendorSnapshot, list[FieldDiff]]:
    since_date = parse_since(since)
    selected = snapshots_since(resolve_vendor(vendor), since_date)
    if len(selected) < 2:
        raise ValueError(
            f"Need two dated snapshots for {vendor} since {since}. Found {len(selected)}."
        )
    older, newer = selected[0], selected[-1]
    before = extract_snapshot(older, cache_path=cache_path)
    after = extract_snapshot(newer, cache_path=cache_path)
    return older, newer, field_diffs(before, after, older, newer)
