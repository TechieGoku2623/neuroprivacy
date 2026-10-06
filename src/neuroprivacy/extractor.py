"""Deterministic span extractor plus optional committed LLM cache lookup.

Phase 0 never calls a live model. The keyword baseline is intentionally
narrow (neural/brain/EEG/BCI) so generic "device data" policies are a miss.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Literal

from neuroprivacy.cache import extraction_from_cache, load_cache, prompt_hash
from neuroprivacy.schemas import (
    FIELD_NAMES,
    AuditStatus,
    ExtractedField,
    PolicyExtraction,
    SpanCitation,
)

Source = Literal["rules", "cache", "keyword", "rater2"]

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")

NEURAL_PATTERNS = (
    r"neural data",
    r"neural signals?",
    r"brain activity",
    r"brain[- ]computer",
    r"\beeg\b",
    r"electroencephal",
    r"\bbci\b",
    r"\bmeg\b",
    r"fnirs",
)
GENERIC_DEVICE_PATTERNS = (
    r"device data",
    r"sensor data",
    r"physiological data",
    r"headset data",
    r"wearable data",
)
DELETION_PATTERNS = (
    r"right to delete",
    r"request deletion",
    r"delete your",
    r"erasure",
    r"erase your",
    r"right to be forgotten",
)
KEYWORD_DELETION_PATTERNS = (r"delete", r"deletion")
RETENTION_CONFLICT_PATTERNS = (
    r"cannot delete",
    r"will not delete",
    r"unable to delete",
    r"retain(?:s|ed|ing)? all .{0,40}(?:year|month)",
    r"kept for \d+ years? even after",
    r"retention.{0,40}(?:cannot|will not) delete",
)
SALE_PATTERNS = (r"\bsell\b", r"\bsale\b", r"\bsold\b")
SHARING_PATTERNS = (
    r"third part(?:y|ies)",
    r"share with",
    r"advertisers",
    r"service providers",
)
PURPOSE_PATTERNS = (
    r"purpose limitation",
    r"only for the (?:specified |stated )?purpose",
    r"not used for (?:other|unrelated) purposes",
)
CONSENT_PATTERNS = (
    r"consent",
    r"opt-in",
    r"opt in",
)

# Rater 2 uses a slightly different lexicon so inter-rater kappa is measurable.
RATER2_NEURAL = (r"neural", r"brainwave", r"cortical", r"\beeg\b")
RATER2_DELETION = (r"\bdelete\b", r"deletion")
RATER2_GENERIC = (r"device data",)
RATER2_RETENTION = (r"cannot delete", r"will not delete")
RATER2_SALE = (r"\bsell\b", r"\bsale\b")
RATER2_SHARING = (r"third part",)
RATER2_PURPOSE = (r"purpose limitation", r"specified purpose")
RATER2_CONSENT = (r"consent",)


def strip_html(html: str) -> str:
    text = _TAG_RE.sub(" ", html)
    return _WS_RE.sub(" ", text).strip()


def _find_span(text: str, patterns: tuple[str, ...]) -> SpanCitation | None:
    lowered = text.lower()
    for pattern in patterns:
        match = re.search(pattern, lowered, flags=re.IGNORECASE)
        if match:
            return SpanCitation(
                text=text[match.start() : match.end()], start=match.start(), end=match.end()
            )
    return None


def _field(name: str, text: str, patterns: tuple[str, ...], source: Source) -> ExtractedField:
    span = _find_span(text, patterns)
    return ExtractedField(name=name, value=span is not None, span=span, source=source)


def _retention_conflicts(
    text: str, grants_deletion: bool, patterns: tuple[str, ...], source: Source
) -> ExtractedField:
    span = _find_span(text, patterns)
    value = bool(span is not None and grants_deletion)
    return ExtractedField(
        name="retention_conflicts_deletion",
        value=value,
        span=span if value else None,
        source=source,
    )


def _status(fields: dict[str, ExtractedField]) -> tuple[AuditStatus, list[str]]:
    findings: list[str] = []
    names = fields["names_neural_data"].value
    generic = fields["covers_generic_device_data"].value
    deletion = fields["grants_deletion"].value
    conflict = fields["retention_conflicts_deletion"].value
    if conflict:
        findings.append("Deletion clause is contradicted by a retention clause.")
        return "INDETERMINATE", findings
    if not names and not generic:
        findings.append("Policy does not name neural data or a covering device-data category.")
        return "GAP", findings
    if not deletion:
        findings.append("No deletion right located in the policy text.")
        return "GAP", findings
    if names:
        findings.append("Neural data is named and a deletion right is stated.")
    else:
        findings.append("Coverage is only under a generic device-data category.")
    return "COMPLIANT", findings


def _from_patterns(
    doc_id: str,
    text: str,
    source: Source,
    neural: tuple[str, ...],
    generic: tuple[str, ...],
    deletion: tuple[str, ...],
    retention: tuple[str, ...],
    sale: tuple[str, ...],
    sharing: tuple[str, ...],
    purpose: tuple[str, ...],
    consent: tuple[str, ...],
    html: str,
) -> PolicyExtraction:
    fields = {
        "names_neural_data": _field("names_neural_data", text, neural, source),
        "covers_generic_device_data": _field("covers_generic_device_data", text, generic, source),
        "grants_deletion": _field("grants_deletion", text, deletion, source),
        "discloses_sale": _field("discloses_sale", text, sale, source),
        "discloses_sharing": _field("discloses_sharing", text, sharing, source),
        "states_purpose_limitation": _field("states_purpose_limitation", text, purpose, source),
        "states_consent_for_sensitive": _field(
            "states_consent_for_sensitive", text, consent, source
        ),
    }
    fields["retention_conflicts_deletion"] = _retention_conflicts(
        text, fields["grants_deletion"].value, retention, source
    )
    status, findings = _status(fields)
    return PolicyExtraction(
        doc_id=doc_id,
        fields=fields,
        status=status,
        findings=findings,
        prompt_hash=prompt_hash(html),
        extractor=source,
    )


def extract_rules(html: str, doc_id: str = "doc") -> PolicyExtraction:
    text = strip_html(html)
    return _from_patterns(
        doc_id,
        text,
        "rules",
        NEURAL_PATTERNS,
        GENERIC_DEVICE_PATTERNS,
        DELETION_PATTERNS,
        RETENTION_CONFLICT_PATTERNS,
        SALE_PATTERNS,
        SHARING_PATTERNS,
        PURPOSE_PATTERNS,
        CONSENT_PATTERNS,
        html,
    )


def extract_keyword_baseline(html: str, doc_id: str = "doc") -> PolicyExtraction:
    """Narrow keyword baseline. Misses generic device-data coverage."""

    text = strip_html(html)
    neural = (r"neural", r"brain", r"\beeg\b", r"\bbci\b")
    return _from_patterns(
        doc_id,
        text,
        "keyword",
        neural,
        (),
        KEYWORD_DELETION_PATTERNS,
        (r"cannot delete",),
        (r"\bsell\b",),
        (r"third part",),
        (r"purpose limitation",),
        (r"consent",),
        html,
    )


def extract_rater2(html: str, doc_id: str = "doc") -> PolicyExtraction:
    """Second labeling pass: a simpler rules extractor with a different lexicon."""

    text = strip_html(html)
    return _from_patterns(
        doc_id,
        text,
        "rater2",
        RATER2_NEURAL,
        RATER2_GENERIC,
        RATER2_DELETION,
        RATER2_RETENTION,
        RATER2_SALE,
        RATER2_SHARING,
        RATER2_PURPOSE,
        RATER2_CONSENT,
        html,
    )


def extract_policy(
    html: str,
    doc_id: str = "doc",
    cache_path: Path | None = None,
) -> PolicyExtraction:
    """Rules extractor with optional committed-cache override. No live API."""

    digest = prompt_hash(html)
    if cache_path is not None:
        cache = load_cache(cache_path)
        if digest in cache:
            cached = extraction_from_cache(cache[digest])
            return cached.model_copy(update={"doc_id": doc_id, "prompt_hash": digest})
    extraction = extract_rules(html, doc_id=doc_id)
    return extraction.model_copy(update={"prompt_hash": digest})


def field_vector(extraction: PolicyExtraction) -> list[bool]:
    return [extraction.field_value(name) for name in FIELD_NAMES]
