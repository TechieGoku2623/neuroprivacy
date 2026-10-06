"""Deterministic statutory scoring. Observations, not legal conclusions."""

from __future__ import annotations

from neuroprivacy.extractor import extract_policy
from neuroprivacy.schemas import AuditFinding, AuditStatus, PolicyExtraction, StatutoryClause
from neuroprivacy.statutes import CLAUSES


def score_clause(extraction: PolicyExtraction, clause: StatutoryClause) -> AuditFinding:
    if clause.checkability != "policy_text":
        return AuditFinding(
            clause_id=clause.clause_id,
            observation=(
                f"{clause.citation} is not machine-checkable from policy text "
                f"({clause.checkability}). Unmeasured in Phase 0."
            ),
            status="INDETERMINATE",
        )

    if not clause.schema_fields:
        return AuditFinding(
            clause_id=clause.clause_id,
            observation=(
                f"{clause.citation} is policy-text-checkable in principle, but "
                "the Phase 0 schema has no field for it. Unmeasured."
            ),
            status="INDETERMINATE",
        )

    hits = [extraction.fields[name] for name in clause.schema_fields if name in extraction.fields]
    if clause.clause_id in {"CO-DELETE"}:
        if extraction.field_value("retention_conflicts_deletion"):
            return AuditFinding(
                clause_id=clause.clause_id,
                observation="Deletion is stated and contradicted by retention. INDETERMINATE.",
                status="INDETERMINATE",
                cited_spans=[f.span for f in hits if f.span is not None],
            )
        if extraction.field_value("grants_deletion"):
            return AuditFinding(
                clause_id=clause.clause_id,
                observation="Deletion right is stated in the policy text.",
                status="COMPLIANT",
                cited_spans=[f.span for f in hits if f.span is not None],
            )
        return AuditFinding(
            clause_id=clause.clause_id,
            observation="No deletion right located in the policy text.",
            status="GAP",
        )

    if clause.clause_id in {
        "CO-DEF-NEURAL",
        "CO-SENSITIVE",
        "CA-DEF-NEURAL",
        "CA-SPI",
        "CA-NOTICE",
        "CA-POLICY-LIST",
    }:
        if extraction.field_value("names_neural_data"):
            status: AuditStatus = "COMPLIANT"
            observation = "Policy names neural data."
        elif extraction.field_value("covers_generic_device_data") and clause.clause_id in {
            "CO-DEF-NEURAL",
            "CA-NOTICE",
        }:
            status = "INDETERMINATE"
            observation = "Coverage is only under generic device data; neural data is not named."
        else:
            status = "GAP"
            observation = "Policy does not name neural data."
        return AuditFinding(
            clause_id=clause.clause_id,
            observation=observation,
            status=status,
            cited_spans=[f.span for f in hits if f.span is not None],
        )

    positive = any(extraction.field_value(name) for name in clause.schema_fields)
    status = "COMPLIANT" if positive else "GAP"
    observation = (
        f"At least one mapped field is present for {clause.citation}."
        if positive
        else f"No mapped field is present for {clause.citation}."
    )
    return AuditFinding(
        clause_id=clause.clause_id,
        observation=observation,
        status=status,
        cited_spans=[f.span for f in hits if f.span is not None],
    )


def score_extraction(extraction: PolicyExtraction) -> list[AuditFinding]:
    return [score_clause(extraction, clause) for clause in CLAUSES]


def score_html(html: str, doc_id: str = "doc") -> tuple[PolicyExtraction, list[AuditFinding]]:
    extraction = extract_policy(html, doc_id=doc_id)
    return extraction, score_extraction(extraction)
