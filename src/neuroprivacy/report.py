"""Static HTML scorecard from committed sample policies."""

from __future__ import annotations

from html import escape
from pathlib import Path

from neuroprivacy import SAFETY_DISCLAIMER
from neuroprivacy.config import get_settings
from neuroprivacy.extractor import extract_keyword_baseline, extract_policy, strip_html
from neuroprivacy.schemas import PolicyExtraction
from neuroprivacy.scoring import score_extraction
from neuroprivacy.statutes import CLAUSES
from neuroprivacy.vendors import resolve_vendor


def _span_cell(extraction: PolicyExtraction, name: str) -> str:
    field = extraction.fields[name]
    if field.span is None:
        return "—"
    quoted = escape(field.span.text)
    return f'"{quoted}" [{field.span.start}:{field.span.end}]'


def build_report_html(sample_dir: Path | None = None) -> str:
    settings = get_settings()
    cache = settings.llm_cache_path
    root = sample_dir or settings.sample_dir
    _ = root
    sections: list[str] = [
        "<!DOCTYPE html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8"/>',
        "<title>neuroprivacy scorecard — observations only</title>",
        "<style>",
        "body{font-family:ui-sans-serif,system-ui,sans-serif;margin:2rem;max-width:1100px;color:#122}",
        "h1,h2{color:#0b3d4a}",
        "table{border-collapse:collapse;width:100%;margin:1rem 0}",
        "th,td{border:1px solid #c5d0d4;padding:.45rem .6rem;text-align:left;vertical-align:top}",
        "th{background:#e8f2f4}",
        ".COMPLIANT{color:#0b6b2a;font-weight:600}",
        ".GAP{color:#9b1c1c;font-weight:600}",
        ".INDETERMINATE{color:#8a5a00;font-weight:600}",
        ".note{background:#f6f1e4;padding:.8rem 1rem;border-left:4px solid #c4a35a}",
        "code{background:#eef3f5;padding:.1rem .3rem}",
        "</style>",
        "</head>",
        "<body>",
        "<h1>neuroprivacy scorecard</h1>",
        f'<p class="note">{escape(SAFETY_DISCLAIMER)}</p>',
        "<p>Generated from committed <code>data/sample/</code> fixtures. "
        "LLM extraction uses the committed cache only. Statutory scoring is deterministic. "
        "Network capture is off unless <code>operator_owns_device=true</code>.</p>",
    ]
    for vendor_id in ("vendor-a", "vendor-b", "vendor-c", "vendor-d"):
        snapshots = resolve_vendor(vendor_id)
        latest = snapshots[-1]
        html = latest.path.read_text(encoding="utf-8")
        extraction = extract_policy(html, doc_id=vendor_id, cache_path=cache)
        keyword = extract_keyword_baseline(html, doc_id=f"{vendor_id}-keyword")
        findings = score_extraction(extraction)
        sections.append(f"<h2>{escape(vendor_id)} — {escape(latest.filename)}</h2>")
        sections.append(
            f'<p>Extractor status: <span class="{extraction.status}">{extraction.status}</span>. '
            f"Keyword baseline neural-data: {keyword.field_value('names_neural_data')}. "
            f"Keyword generic cover: {keyword.field_value('covers_generic_device_data')}.</p>"
        )
        sections.append("<table><tr><th>Field</th><th>Value</th><th>Span (offsets)</th></tr>")
        for name, field in extraction.fields.items():
            sections.append(
                "<tr>"
                f"<td><code>{escape(name)}</code></td>"
                f"<td>{field.value}</td>"
                f"<td>{_span_cell(extraction, name)}</td>"
                "</tr>"
            )
        sections.append("</table>")
        sections.append(
            "<table><tr><th>Clause</th><th>Statute</th><th>Status</th><th>Observation</th></tr>"
        )
        by_id = {clause.clause_id: clause for clause in CLAUSES}
        for finding in findings:
            clause = by_id[finding.clause_id]
            sections.append(
                "<tr>"
                f"<td><code>{escape(finding.clause_id)}</code></td>"
                f"<td>{escape(clause.citation)}</td>"
                f'<td class="{finding.status}">{finding.status}</td>'
                f"<td>{escape(finding.observation)}</td>"
                "</tr>"
            )
        sections.append("</table>")
        if vendor_id == "vendor-d" and len(snapshots) == 2:
            older_html = snapshots[0].path.read_text(encoding="utf-8")
            older = extract_policy(older_html, doc_id="vendor-d-jan", cache_path=cache)
            sections.append(
                "<p>Dated drift since 2025-01-01: "
                f"<code>discloses_sharing</code> {older.field_value('discloses_sharing')} → "
                f"{extraction.field_value('discloses_sharing')} "
                f"({escape(snapshots[0].filename)} vs {escape(snapshots[1].filename)}).</p>"
            )
        _ = strip_html(html)
    sections.extend(
        [
            f"<p>{escape(SAFETY_DISCLAIMER)}</p>",
            "</body>",
            "</html>",
            "",
        ]
    )
    return "\n".join(sections)


def write_report(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_report_html(), encoding="utf-8")
    return path


def default_report_path() -> Path:
    return get_settings().repo_root / "docs" / "report" / "index.html"
