"""Fraction of CO/CA neural-data provisions checkable from policy text."""

from __future__ import annotations

import sys
from pathlib import Path

from neuroprivacy.statutes import CLAUSES, coverage_counts

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import md_table, write_json  # noqa: E402

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"


def main() -> None:
    counts = coverage_counts()
    n = counts["n_clauses"]
    policy_frac = counts["n_policy_text"] / n
    rows = []
    by_statute: dict[str, dict[str, int]] = {}
    for clause in CLAUSES:
        bucket = by_statute.setdefault(clause.statute, {"n": 0, "policy_text": 0, "other": 0})
        bucket["n"] += 1
        if clause.machine_checkable_from_policy:
            bucket["policy_text"] += 1
        else:
            bucket["other"] += 1
        rows.append(
            [
                clause.clause_id,
                clause.statute,
                clause.citation,
                clause.checkability,
                "yes" if clause.machine_checkable_from_policy else "no",
            ]
        )

    if policy_frac >= 0.50:
        decision = (
            f"{counts['n_policy_text']}/{n} = {policy_frac:.3f} of encoded "
            "provisions are machine-checkable from policy text. Phase 2 should "
            "center on extraction + deterministic scoring. Network capture stays optional."
        )
    else:
        decision = (
            f"Only {counts['n_policy_text']}/{n} = {policy_frac:.3f} of encoded "
            "provisions are checkable from policy text. Narrow the product to "
            "those clauses or accept that most duties are unmeasured without "
            "operator-owned device observation."
        )

    payload = {
        **counts,
        "policy_text_fraction": policy_frac,
        "by_statute": {
            name: {
                **stats,
                "policy_text_fraction": stats["policy_text"] / stats["n"],
            }
            for name, stats in by_statute.items()
        },
        "decision": decision,
        "clauses": [clause.model_dump(mode="json") for clause in CLAUSES],
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    write_json(RESULTS / "results.json", payload)
    table = md_table(
        ["clause_id", "statute", "citation", "checkability", "policy-text?"],
        rows,
    )
    statute_rows = [
        [
            name,
            str(stats["n"]),
            str(stats["policy_text"]),
            f"{stats['policy_text'] / stats['n']:.3f}",
        ]
        for name, stats in sorted(by_statute.items())
    ]
    md = (
        "# statute_coverage results\n\n"
        f"Encoded clauses: {n}. Policy-text checkable: {counts['n_policy_text']} "
        f"({policy_frac:.3f}). Network/product: {counts['n_network_or_product']}. "
        f"Internal record: {counts['n_internal_record']}. Cannot check: "
        f"{counts['n_cannot_check']}.\n\n"
        f"Decision: {decision}\n\n"
        "## By statute\n\n"
        f"{md_table(['statute', 'n', 'policy-text', 'fraction'], statute_rows)}\n\n"
        "## Clauses\n\n"
        f"{table}\n"
    )
    (RESULTS / "results.md").write_text(md, encoding="utf-8")
    print(md)


if __name__ == "__main__":
    main()
