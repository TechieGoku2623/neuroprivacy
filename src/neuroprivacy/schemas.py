"""Data contracts for policy extraction, statutory clauses, and sample docs."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

FIELD_NAMES: tuple[str, ...] = (
    "names_neural_data",
    "covers_generic_device_data",
    "grants_deletion",
    "retention_conflicts_deletion",
    "discloses_sale",
    "discloses_sharing",
    "states_purpose_limitation",
    "states_consent_for_sensitive",
)

AuditStatus = Literal["COMPLIANT", "GAP", "INDETERMINATE"]
Checkability = Literal["policy_text", "network_or_product", "internal_record", "cannot_check"]
RaterName = Literal["gold", "extractor", "keyword", "rater2"]


class SpanCitation(BaseModel):
    """Byte-offset citation into the stripped policy text."""

    text: str
    start: int
    end: int


class ExtractedField(BaseModel):
    """One schema field with an optional span-level citation."""

    name: str
    value: bool
    span: SpanCitation | None = None
    source: Literal["rules", "cache", "keyword", "rater2"] = "rules"


class PolicyExtraction(BaseModel):
    """Structured extraction from one policy document."""

    doc_id: str
    fields: dict[str, ExtractedField]
    status: AuditStatus
    findings: list[str] = Field(default_factory=list)
    prompt_hash: str | None = None
    extractor: Literal["rules", "cache", "keyword", "rater2"] = "rules"

    def field_value(self, name: str) -> bool:
        return self.fields[name].value


class GoldLabel(BaseModel):
    """Hand labels for one probe document (labeling pass 1)."""

    doc_id: str
    values: dict[str, bool]
    status: AuditStatus
    notes: str = ""


class SampleDocument(BaseModel):
    """One designed demo policy in data/sample/."""

    sample_id: str
    filename: str
    path_exercised: str
    why_present: str
    expected_behavior: str


class StatutoryClause(BaseModel):
    """One encoded provision from HB24-1058 or SB 1223."""

    clause_id: str
    statute: Literal["CO_HB24_1058", "CA_SB_1223"]
    citation: str
    summary: str
    checkability: Checkability
    schema_fields: list[str] = Field(default_factory=list)
    notes: str = ""

    @property
    def machine_checkable_from_policy(self) -> bool:
        return self.checkability == "policy_text"


class AuditFinding(BaseModel):
    """Deterministic observation against one statute clause."""

    clause_id: str
    observation: str
    status: AuditStatus
    cited_spans: list[SpanCitation] = Field(default_factory=list)
