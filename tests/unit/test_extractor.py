from __future__ import annotations

from pathlib import Path

from neuroprivacy.config import get_settings
from neuroprivacy.extractor import (
    extract_keyword_baseline,
    extract_policy,
    extract_rater2,
    extract_rules,
    strip_html,
)

SAMPLE = Path(__file__).resolve().parents[2] / "data" / "sample"


def _html(name: str) -> str:
    return (SAMPLE / name).read_text(encoding="utf-8")


def test_vendor_a_compliant() -> None:
    extraction = extract_rules(_html("vendor-a.html"), "vendor-a")
    assert extraction.field_value("names_neural_data") is True
    assert extraction.field_value("grants_deletion") is True
    assert extraction.field_value("retention_conflicts_deletion") is False
    assert extraction.status == "COMPLIANT"
    assert extraction.fields["names_neural_data"].span is not None


def test_vendor_b_keyword_misses_generic_cover() -> None:
    html = _html("vendor-b.html")
    rules = extract_rules(html, "vendor-b")
    keyword = extract_keyword_baseline(html, "vendor-b")
    assert rules.field_value("covers_generic_device_data") is True
    assert rules.field_value("names_neural_data") is False
    assert keyword.field_value("names_neural_data") is False
    assert keyword.field_value("covers_generic_device_data") is False


def test_vendor_c_indeterminate() -> None:
    extraction = extract_rules(_html("vendor-c.html"), "vendor-c")
    assert extraction.field_value("grants_deletion") is True
    assert extraction.field_value("retention_conflicts_deletion") is True
    assert extraction.status == "INDETERMINATE"


def test_vendor_d_sharing_removed() -> None:
    jan = extract_rules(_html("vendor-d-2025-01.html"), "jan")
    jun = extract_rules(_html("vendor-d-2025-06.html"), "jun")
    assert jan.field_value("discloses_sharing") is True
    assert jun.field_value("discloses_sharing") is False
    assert jan.field_value("names_neural_data") is True
    assert jun.field_value("names_neural_data") is True


def test_extract_policy_uses_cache_when_present() -> None:
    html = _html("vendor-a.html")
    cache_path = get_settings().llm_cache_path
    assert cache_path.is_file()
    extraction = extract_policy(html, "vendor-a", cache_path=cache_path)
    assert extraction.prompt_hash
    assert extraction.extractor == "cache"
    assert extraction.field_value("names_neural_data") is True


def test_extract_policy_without_cache_is_rules() -> None:
    extraction = extract_policy("<p>We collect neural data.</p>", "x")
    assert extraction.extractor == "rules"
    assert extraction.field_value("names_neural_data") is True
    assert extraction.status == "GAP"


def test_rater2_and_strip_html() -> None:
    text = strip_html("<p>Hello   <b>world</b></p>")
    assert text == "Hello world"
    rater2 = extract_rater2("<p>We collect neural data and you may delete it.</p>", "r2")
    assert rater2.field_value("names_neural_data") is True
    assert rater2.extractor == "rater2"
