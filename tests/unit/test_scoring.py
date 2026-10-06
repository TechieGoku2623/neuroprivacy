from __future__ import annotations

from pathlib import Path

from neuroprivacy.extractor import extract_rules
from neuroprivacy.scoring import score_clause, score_extraction, score_html
from neuroprivacy.statutes import CLAUSES

SAMPLE = Path(__file__).resolve().parents[2] / "data" / "sample"


def test_score_gap_when_deletion_missing() -> None:
    extraction = extract_rules("<p>We collect neural data.</p>", "x")
    delete = next(clause for clause in CLAUSES if clause.clause_id == "CO-DELETE")
    finding = score_clause(extraction, delete)
    assert finding.status == "GAP"


def test_score_html_vendor_a_has_compliant_delete() -> None:
    html = (SAMPLE / "vendor-a.html").read_text(encoding="utf-8")
    extraction, findings = score_html(html, "vendor-a")
    assert extraction.status == "COMPLIANT"
    delete = next(item for item in findings if item.clause_id == "CO-DELETE")
    assert delete.status == "COMPLIANT"


def test_score_html_vendor_c_delete_indeterminate() -> None:
    html = (SAMPLE / "vendor-c.html").read_text(encoding="utf-8")
    _extraction, findings = score_html(html, "vendor-c")
    delete = next(item for item in findings if item.clause_id == "CO-DELETE")
    assert delete.status == "INDETERMINATE"


def test_non_policy_clause_is_indeterminate() -> None:
    extraction = extract_rules("<p>We collect neural data.</p>", "x")
    internal = next(clause for clause in CLAUSES if clause.checkability == "internal_record")
    finding = score_clause(extraction, internal)
    assert finding.status == "INDETERMINATE"
    assert "not machine-checkable" in finding.observation


def test_unmapped_policy_clause_is_indeterminate() -> None:
    extraction = extract_rules("<p>We collect neural data.</p>", "x")
    unmapped = next(
        clause
        for clause in CLAUSES
        if clause.checkability == "policy_text" and not clause.schema_fields
    )
    finding = score_clause(extraction, unmapped)
    assert finding.status == "INDETERMINATE"


def test_score_extraction_covers_all_clauses() -> None:
    extraction = extract_rules("<p>device data and the right to delete it.</p>", "x")
    findings = score_extraction(extraction)
    assert len(findings) == len(CLAUSES)
    neural = next(item for item in findings if item.clause_id == "CO-DEF-NEURAL")
    assert neural.status == "INDETERMINATE"
