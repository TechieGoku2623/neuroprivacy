"""Committed LLM response cache keyed by prompt hash. No live API calls."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from neuroprivacy.schemas import ExtractedField, PolicyExtraction, SpanCitation

SCHEMA_VERSION = "phase0-v1"


def prompt_hash(html: str, schema_version: str = SCHEMA_VERSION) -> str:
    payload = f"{schema_version}\n{html.strip()}\n"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def load_cache(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        return {}
    return raw


def dump_cache(path: Path, cache: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cache, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def cache_entry(extraction: PolicyExtraction) -> dict[str, Any]:
    return {
        "prompt_hash": extraction.prompt_hash,
        "model": "cached-phase0-no-live-api",
        "schema_version": SCHEMA_VERSION,
        "extraction": extraction.model_dump(mode="json"),
    }


def extraction_from_cache(entry: dict[str, Any]) -> PolicyExtraction:
    payload = entry["extraction"]
    fields = {
        name: ExtractedField(
            name=item["name"],
            value=bool(item["value"]),
            span=SpanCitation.model_validate(item["span"]) if item.get("span") else None,
            source="cache",
        )
        for name, item in payload["fields"].items()
    }
    return PolicyExtraction(
        doc_id=payload["doc_id"],
        fields=fields,
        status=payload["status"],
        findings=list(payload.get("findings", [])),
        prompt_hash=entry.get("prompt_hash", payload.get("prompt_hash")),
        extractor="cache",
    )
