from __future__ import annotations

from neuroprivacy.statutes import all_clauses, clauses_by_statute, coverage_counts


def test_clause_catalog_covers_both_statutes() -> None:
    clauses = all_clauses()
    assert len(clauses) >= 16
    assert clauses_by_statute("CO_HB24_1058")
    assert clauses_by_statute("CA_SB_1223")
    ids = [clause.clause_id for clause in clauses]
    assert len(ids) == len(set(ids))
    for clause in clauses:
        assert clause.citation
        assert clause.summary


def test_coverage_counts_sum() -> None:
    counts = coverage_counts()
    parts = (
        counts["n_policy_text"]
        + counts["n_network_or_product"]
        + counts["n_internal_record"]
        + counts["n_cannot_check"]
    )
    assert parts == counts["n_clauses"]
    assert counts["n_policy_text"] >= 1
