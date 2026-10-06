from __future__ import annotations

from pathlib import Path

from neuroprivacy.cache import (
    cache_entry,
    dump_cache,
    extraction_from_cache,
    load_cache,
    prompt_hash,
)
from neuroprivacy.extractor import extract_rules


def test_prompt_hash_is_stable() -> None:
    html = "<p>We collect neural data.</p>"
    assert prompt_hash(html) == prompt_hash(f"  {html}  ")
    assert prompt_hash(html) != prompt_hash("<p>other</p>")


def test_round_trip_cache(tmp_path: Path) -> None:
    extraction = extract_rules("<p>We collect neural data. Right to delete.</p>", "t")
    path = tmp_path / "cache.json"
    digest = prompt_hash("<p>We collect neural data. Right to delete.</p>")
    dump_cache(path, {digest: cache_entry(extraction)})
    loaded = load_cache(path)
    restored = extraction_from_cache(loaded[digest])
    assert restored.extractor == "cache"
    assert restored.field_value("names_neural_data") is True
    assert load_cache(tmp_path / "missing.json") == {}


def test_load_cache_rejects_non_object(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text("[]\n", encoding="utf-8")
    assert load_cache(path) == {}
