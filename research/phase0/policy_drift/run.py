"""Change rate across 12 months of synthetic snapshots for 5 vendors."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import duckdb

from neuroprivacy.config import get_settings
from neuroprivacy.extractor import extract_rules

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import md_table, read_json, write_json  # noqa: E402

HERE = Path(__file__).resolve().parent
PROBE = HERE / "probe_set" / "snapshots.json"
RESULTS = HERE / "results"


def _cadence(change_rate: float) -> str:
    if change_rate >= 0.25:
        return "monthly"
    if change_rate >= 0.10:
        return "quarterly"
    return "semiannual"


def main() -> None:
    snapshots = read_json(PROBE)["snapshots"]
    by_vendor: dict[str, list[dict[str, object]]] = {}
    for row in snapshots:
        by_vendor.setdefault(str(row["vendor"]), []).append(row)
    for rows in by_vendor.values():
        rows.sort(key=lambda item: str(item["month"]))

    vendor_rows: list[list[str]] = []
    vendor_stats: dict[str, object] = {}
    n_transitions = 0
    n_changes = 0
    for vendor, rows in sorted(by_vendor.items()):
        changes = 0
        transitions = 0
        for prev, cur in zip(rows, rows[1:], strict=False):
            transitions += 1
            if prev["sha256"] != cur["sha256"]:
                changes += 1
        n_transitions += transitions
        n_changes += changes
        rate = changes / transitions if transitions else 0.0
        vendor_stats[vendor] = {
            "n_snapshots": len(rows),
            "n_changes": changes,
            "n_transitions": transitions,
            "change_rate": rate,
        }
        vendor_rows.append([vendor, str(len(rows)), str(changes), f"{rate:.3f}"])

    change_rate = n_changes / n_transitions if n_transitions else 0.0
    cadence = _cadence(change_rate)

    sample = get_settings().sample_dir
    jan = extract_rules(
        (sample / "vendor-d-2025-01.html").read_text(encoding="utf-8"), "vendor-d-jan"
    )
    jun = extract_rules(
        (sample / "vendor-d-2025-06.html").read_text(encoding="utf-8"), "vendor-d-jun"
    )
    sharing_drift = jan.field_value("discloses_sharing") and not jun.field_value(
        "discloses_sharing"
    )

    con = duckdb.connect()
    con.execute("CREATE TABLE snaps (vendor VARCHAR, month VARCHAR, sha VARCHAR)")
    for row in snapshots:
        con.execute(
            "INSERT INTO snaps VALUES (?, ?, ?)",
            [row["vendor"], row["month"], row["sha256"]],
        )
    distinct = con.execute(
        "SELECT vendor, COUNT(DISTINCT sha) FROM snaps GROUP BY vendor"
    ).fetchall()
    distinct_counts = {str(vendor): int(count) for vendor, count in distinct}
    con.close()

    decision = (
        f"Observed change rate {n_changes}/{n_transitions} = {change_rate:.3f}. "
        f"Recommended monitoring cadence: {cadence}."
    )
    payload = {
        "n_vendors": len(by_vendor),
        "n_snapshots": len(snapshots),
        "n_transitions": n_transitions,
        "n_changes": n_changes,
        "change_rate": change_rate,
        "recommended_cadence": cadence,
        "vendor_stats": vendor_stats,
        "distinct_hashes_by_vendor": distinct_counts,
        "vendor_d_sharing_removed": sharing_drift,
        "decision": decision,
        "sample_d_jan_sha256": hashlib.sha256(
            (sample / "vendor-d-2025-01.html").read_bytes()
        ).hexdigest(),
        "sample_d_jun_sha256": hashlib.sha256(
            (sample / "vendor-d-2025-06.html").read_bytes()
        ).hexdigest(),
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    write_json(RESULTS / "results.json", payload)
    table = md_table(["vendor", "snapshots", "changes", "change rate"], vendor_rows)
    md = (
        "# policy_drift results\n\n"
        f"Vendors: {len(by_vendor)}. Snapshots: {len(snapshots)}. "
        f"Transitions: {n_transitions}. Changes: {n_changes}. "
        f"Change rate: {change_rate:.3f}.\n\n"
        f"Vendor-D sample sharing clause removed: {sharing_drift}.\n\n"
        f"Decision: {decision}\n\n"
        f"{table}\n"
    )
    (RESULTS / "results.md").write_text(md, encoding="utf-8")
    print(md)


if __name__ == "__main__":
    main()
