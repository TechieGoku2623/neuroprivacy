"""Phase 0–3 CLI: extract, audit, diff, and a static HTML scorecard."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from neuroprivacy import SAFETY_DISCLAIMER, __version__
from neuroprivacy.capture import NetworkCaptureRefused, attempt_network_capture
from neuroprivacy.config import get_settings, network_capture_allowed
from neuroprivacy.diffing import vendor_diff
from neuroprivacy.extractor import extract_keyword_baseline, extract_policy
from neuroprivacy.logging import configure_logging
from neuroprivacy.report import default_report_path, write_report
from neuroprivacy.schemas import AuditFinding, PolicyExtraction, SampleDocument
from neuroprivacy.scoring import score_extraction
from neuroprivacy.statutes import CLAUSES
from neuroprivacy.vendors import resolve_doc, resolve_vendor

app = typer.Typer(no_args_is_help=True, add_completion=False)
console = Console(width=140)

SAMPLES: tuple[SampleDocument, ...] = (
    SampleDocument(
        sample_id="vendor-a",
        filename="vendor-a.html",
        path_exercised="explicit neural data + deletion right",
        why_present="Names neural data and grants deletion. Designed compliant observation.",
        expected_behavior="Extractor cites neural-data and deletion spans. Status COMPLIANT.",
    ),
    SampleDocument(
        sample_id="vendor-b",
        filename="vendor-b.html",
        path_exercised="generic device data only",
        why_present="Never uses neural/brain/EEG. Keyword baseline misses this.",
        expected_behavior=(
            "Keyword baseline names_neural_data=false and no generic cover. "
            "Rules extractor flags generic device data."
        ),
    ),
    SampleDocument(
        sample_id="vendor-c",
        filename="vendor-c.html",
        path_exercised="deletion contradicted by retention",
        why_present="Deletion clause and a cannot-delete retention clause in the same document.",
        expected_behavior="Status INDETERMINATE. Do not emit a single compliant/gap label.",
    ),
    SampleDocument(
        sample_id="vendor-d",
        filename="vendor-d-2025-01.html + vendor-d-2025-06.html",
        path_exercised="policy drift / clause removed",
        why_present="Sharing clause present in January snapshot, absent in June snapshot.",
        expected_behavior="Diff reports discloses_sharing true→false. Monitoring cadence input.",
    ),
)


@app.callback()
def _main() -> None:
    configure_logging()


def _disclaimer() -> None:
    console.print(SAFETY_DISCLAIMER)


def _load_html(path: Path) -> tuple[Path, str, PolicyExtraction]:
    resolved = resolve_doc(path)
    html = resolved.read_text(encoding="utf-8")
    extraction = extract_policy(
        html, doc_id=resolved.stem, cache_path=get_settings().llm_cache_path
    )
    return resolved, html, extraction


def _print_fields(extraction: PolicyExtraction) -> None:
    table = Table(title=f"Structured fields — {extraction.doc_id} ({extraction.extractor})")
    table.add_column("field")
    table.add_column("value")
    table.add_column("source")
    table.add_column("span text")
    table.add_column("offsets")
    for name, field in extraction.fields.items():
        if field.span is None:
            span_text, offsets = "—", "—"
        else:
            span_text = field.span.text
            offsets = f"{field.span.start}:{field.span.end}"
        table.add_row(name, str(field.value).lower(), field.source, span_text, offsets)
    console.print(table)
    console.print(f"document status: {extraction.status}")
    for finding in extraction.findings:
        console.print(f"  observation: {finding}")
    if extraction.prompt_hash:
        console.print(f"prompt_hash: {extraction.prompt_hash}")


def _print_scorecard(extraction: PolicyExtraction, findings: list[AuditFinding]) -> None:
    by_id = {clause.clause_id: clause for clause in CLAUSES}
    table = Table(title=f"CO/CA clause scorecard — {extraction.doc_id}")
    table.add_column("clause")
    table.add_column("citation")
    table.add_column("status")
    table.add_column("observation")
    for finding in findings:
        clause = by_id[finding.clause_id]
        table.add_row(finding.clause_id, clause.citation, finding.status, finding.observation)
    console.print(table)


def _print_conflicts(extraction: PolicyExtraction, findings: list[AuditFinding]) -> None:
    deletion = extraction.fields["grants_deletion"]
    retention = extraction.fields["retention_conflicts_deletion"]
    console.print("[bold]Conflicting spans[/bold]")
    if deletion.span is None or retention.span is None:
        console.print("  no paired deletion/retention spans")
        return
    console.print(
        f'  1. grants_deletion: "{deletion.span.text}" [{deletion.span.start}:{deletion.span.end}]'
    )
    console.print(
        f'  2. retention_conflicts_deletion: "{retention.span.text}" '
        f"[{retention.span.start}:{retention.span.end}]"
    )
    delete = next(item for item in findings if item.clause_id == "CO-DELETE")
    console.print(f"  CO-DELETE status: {delete.status}")
    console.print(f"  observation: {delete.observation}")


@app.command("version")
def version() -> None:
    """Print the package version."""

    console.print(f"neuroprivacy {__version__}")


@app.command("demo-plan")
def demo_plan(
    dry_run: bool = typer.Option(True, "--dry-run/--no-dry-run"),
) -> None:
    """List the four designed policy documents and the path each exercises."""

    settings = get_settings()
    console.print("[bold]neuroprivacy designed sample policies[/bold]\n")
    for sample in SAMPLES:
        console.print(f"[bold]{sample.sample_id}[/bold]  {sample.filename}")
        console.print(f"  path:     {sample.path_exercised}")
        console.print(f"  expected: {sample.expected_behavior}")
        if "+" in sample.filename:
            for part in sample.filename.split(" + "):
                console.print(f"  file:     {settings.sample_dir / part}")
        else:
            console.print(f"  file:     {settings.sample_dir / sample.filename}")
        console.print()
    _disclaimer()
    console.print(
        f"Network capture enabled: {network_capture_allowed(settings)} "
        "(operator-owned devices only; refuses unless operator_owns_device=true)."
    )
    if dry_run:
        console.print(
            "\nDry run only. Designed fixtures listed above. "
            "`make demo` runs extract, audit, diff, and report on these files."
        )
    console.print(f"Sample directory: {settings.sample_dir}")


@app.command("sample-path")
def sample_path() -> None:
    """Print the committed sample directory path."""

    console.print(str(get_settings().sample_dir.resolve()))


@app.command("extract")
def extract(
    doc: Annotated[Path, typer.Option("--doc", help="Policy HTML path")],
) -> None:
    """Extract typed fields with source spans and character offsets."""

    _path, _html, extraction = _load_html(doc)
    console.print("[bold]neuroprivacy extract[/bold]")
    console.print(f"doc: {_path}")
    console.print("LLM: committed cache only (no live model). Span-level citation is mandatory.")
    _print_fields(extraction)
    missing_span = [
        name for name, field in extraction.fields.items() if field.value and field.span is None
    ]
    if missing_span:
        console.print(f"citation gap (true without span): {', '.join(missing_span)}")
    else:
        console.print("span-level citation: every true field has character offsets.")
    _disclaimer()


@app.command("audit")
def audit(
    vendor: str = typer.Option(..., "--vendor", help="Designed vendor id (vendor-a..d)"),
    show_conflicts: bool = typer.Option(False, "--show-conflicts"),
) -> None:
    """Score a vendor policy against encoded CO/CA clauses."""

    snapshots = resolve_vendor(vendor)
    latest = snapshots[-1]
    html = latest.path.read_text(encoding="utf-8")
    extraction = extract_policy(html, doc_id=vendor, cache_path=get_settings().llm_cache_path)
    keyword = extract_keyword_baseline(html, doc_id=f"{vendor}-keyword")
    findings = score_extraction(extraction)
    console.print("[bold]neuroprivacy audit[/bold]")
    console.print(f"vendor: {vendor}  file: {latest.path.name}  dated: {latest.snapshot_date}")
    console.print(f"extractor status: {extraction.status}  source: {extraction.extractor}")
    console.print("[bold]Keyword baseline comparison[/bold]")
    console.print(
        f"  names_neural_data={str(keyword.field_value('names_neural_data')).lower()}  "
        f"covers_generic_device_data="
        f"{str(keyword.field_value('covers_generic_device_data')).lower()}"
    )
    if not keyword.field_value("names_neural_data") and not keyword.field_value(
        "covers_generic_device_data"
    ):
        console.print(
            "  baseline finds nothing: no neural/brain/EEG token and no generic-cover rule."
        )
    else:
        console.print("  baseline located at least one neural or cover token.")
    console.print(
        "  rules extractor "
        f"names_neural_data={str(extraction.field_value('names_neural_data')).lower()}  "
        f"covers_generic_device_data="
        f"{str(extraction.field_value('covers_generic_device_data')).lower()}"
    )
    _print_fields(extraction)
    _print_scorecard(extraction, findings)
    if show_conflicts:
        _print_conflicts(extraction, findings)
    _disclaimer()


@app.command("diff")
def diff(
    vendor: str = typer.Option(..., "--vendor"),
    since: str = typer.Option(..., "--since", help="ISO date, e.g. 2025-01-01"),
) -> None:
    """Dated field diff for a vendor with more than one snapshot."""

    older, newer, diffs = vendor_diff(vendor, since, cache_path=get_settings().llm_cache_path)
    console.print("[bold]neuroprivacy diff[/bold]")
    console.print(f"vendor: {vendor}  since: {since}")
    console.print(f"  {older.snapshot_date}  {older.filename}")
    console.print(f"  {newer.snapshot_date}  {newer.filename}")
    table = Table(title="Removed or changed clauses")
    table.add_column("field")
    table.add_column("before")
    table.add_column("after")
    table.add_column("change")
    if not diffs:
        console.print("No field changes after the since date.")
    for item in diffs:
        change = "removed clause" if item.before and not item.after else "added clause"
        table.add_row(
            item.name,
            f"{str(item.before).lower()} ({item.before_date})",
            f"{str(item.after).lower()} ({item.after_date})",
            change,
        )
    if diffs:
        console.print(table)
    _disclaimer()


@app.command("report")
def report(
    out: Annotated[Path | None, typer.Option("--out", help="HTML output path")] = None,
) -> None:
    """Write a static HTML scorecard from committed sample data."""

    path = write_report(out or default_report_path())
    console.print(f"wrote {path}")
    _disclaimer()


@app.command("capture")
def capture() -> None:
    """Network-capture stub. Refuses unless operator_owns_device=true."""

    settings = get_settings()
    console.print("[bold]neuroprivacy capture stub[/bold]")
    console.print(
        f"enabled={settings.network_capture.enabled}  "
        f"operator_owns_device={settings.network_capture.operator_owns_device}"
    )
    try:
        attempt = attempt_network_capture(settings)
    except NetworkCaptureRefused as exc:
        console.print(str(exc))
        _disclaimer()
        raise typer.Exit(code=2) from exc
    console.print(attempt.reason)
    _disclaimer()


@app.command("demo")
def demo() -> None:
    """Full walkthrough on committed samples. No credentials."""

    settings = get_settings()
    console.print("[bold]neuroprivacy demo — Phase 0–3 walkthrough[/bold]\n")
    extract(doc=settings.sample_dir / "vendor-a.html")
    console.print()
    audit(vendor="vendor-b", show_conflicts=False)
    console.print()
    audit(vendor="vendor-c", show_conflicts=True)
    console.print()
    diff(vendor="vendor-d", since="2025-01-01")
    console.print()
    report(out=default_report_path())


def repo_root() -> Path:
    return get_settings().repo_root
