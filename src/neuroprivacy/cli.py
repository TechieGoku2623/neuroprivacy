"""Phase 0 CLI. Full audit application is Phase 2."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from neuroprivacy import SAFETY_DISCLAIMER, __version__
from neuroprivacy.config import get_settings, network_capture_allowed
from neuroprivacy.logging import configure_logging
from neuroprivacy.schemas import SampleDocument

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
    console.print(SAFETY_DISCLAIMER)
    console.print(
        f"Network capture enabled: {network_capture_allowed(settings)} "
        "(operator-owned devices only; off in Phase 0)."
    )
    if dry_run:
        console.print(
            "\nDry run only. A full `neuroprivacy audit` CLI is Phase 2; "
            "this command exists so `make demo` can show that the sample set "
            "is designed, not scraped."
        )
    console.print(f"Sample directory: {settings.sample_dir}")


@app.command("sample-path")
def sample_path() -> None:
    """Print the committed sample directory path."""

    console.print(str(get_settings().sample_dir.resolve()))


def repo_root() -> Path:
    return get_settings().repo_root
