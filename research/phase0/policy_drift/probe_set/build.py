"""Build 12 months × 5 vendors of synthetic Wayback-style snapshots."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
VENDORS = ("alpha", "beta", "gamma", "delta", "epsilon")
MONTHS = [f"2025-{month:02d}" for month in range(1, 13)]


def _body(vendor: str, revision: int) -> str:
    sharing = ""
    if vendor == "delta" and revision == 0:
        sharing = "<p>We share neural data with third parties for measurement.</p>"
    # Month is metadata only. Hashing the dated wrapper would count every
    # snapshot as a change even when the policy text is identical.
    return (
        f"<html><head><title>Vendor {vendor} privacy policy</title></head><body>"
        f"<h1>Vendor {vendor} privacy policy</h1>"
        "<p>Synthetic Wayback-style snapshot. Not a live scrape.</p>"
        "<p>We collect neural data from the consumer headset.</p>"
        "<p>You have the right to delete neural data.</p>"
        f"{sharing}"
        f"<p>Revision token: {vendor}-{revision}</p>"
        "</body></html>\n"
    )


def _revision(vendor: str, month: str) -> int:
    index = MONTHS.index(month)
    if vendor == "alpha":
        return index
    if vendor == "beta":
        return index // 3
    if vendor == "gamma":
        return 0 if index < 6 else 1
    if vendor == "delta":
        return 0 if index < 5 else 1
    return 0


def main() -> None:
    snapshots = []
    for vendor in VENDORS:
        for month in MONTHS:
            revision = _revision(vendor, month)
            html = _body(vendor, revision)
            digest = hashlib.sha256(html.encode("utf-8")).hexdigest()
            snapshots.append(
                {
                    "vendor": vendor,
                    "month": month,
                    "revision": revision,
                    "sha256": digest,
                    "html": html,
                }
            )
    path = HERE / "snapshots.json"
    path.write_text(json.dumps({"snapshots": snapshots}, indent=2) + "\n", encoding="utf-8")
    (HERE / "README.md").write_text(
        "# policy_drift probe set\n\n"
        "60 synthetic dated snapshots (5 vendors × 12 months). Not live scrapes.\n",
        encoding="utf-8",
    )
    print(f"wrote {len(snapshots)} snapshots")


if __name__ == "__main__":
    main()
