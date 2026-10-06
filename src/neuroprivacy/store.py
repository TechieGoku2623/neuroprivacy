"""DuckDB helpers for Phase 0 extraction rows. Local files only."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import duckdb

from neuroprivacy.schemas import FIELD_NAMES, PolicyExtraction


def extraction_row(extraction: PolicyExtraction) -> dict[str, Any]:
    row: dict[str, Any] = {
        "doc_id": extraction.doc_id,
        "status": extraction.status,
        "extractor": extraction.extractor,
        "prompt_hash": extraction.prompt_hash,
    }
    for name in FIELD_NAMES:
        row[name] = extraction.field_value(name)
    return row


def write_extractions(path: Path, rows: list[PolicyExtraction]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    con = duckdb.connect(str(path))
    try:
        con.execute(
            """
            CREATE TABLE extractions (
                doc_id VARCHAR,
                status VARCHAR,
                extractor VARCHAR,
                prompt_hash VARCHAR,
                names_neural_data BOOLEAN,
                covers_generic_device_data BOOLEAN,
                grants_deletion BOOLEAN,
                retention_conflicts_deletion BOOLEAN,
                discloses_sale BOOLEAN,
                discloses_sharing BOOLEAN,
                states_purpose_limitation BOOLEAN,
                states_consent_for_sensitive BOOLEAN
            )
            """
        )
        for extraction in rows:
            row = extraction_row(extraction)
            con.execute(
                """
                INSERT INTO extractions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    row["doc_id"],
                    row["status"],
                    row["extractor"],
                    row["prompt_hash"],
                    row["names_neural_data"],
                    row["covers_generic_device_data"],
                    row["grants_deletion"],
                    row["retention_conflicts_deletion"],
                    row["discloses_sale"],
                    row["discloses_sharing"],
                    row["states_purpose_limitation"],
                    row["states_consent_for_sensitive"],
                ],
            )
    finally:
        con.close()


def count_extractions(path: Path) -> int:
    con = duckdb.connect(str(path), read_only=True)
    try:
        result = con.execute("SELECT COUNT(*) FROM extractions").fetchone()
        return int(result[0]) if result else 0
    finally:
        con.close()
