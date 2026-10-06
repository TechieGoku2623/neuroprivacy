from __future__ import annotations

from typer.testing import CliRunner

from neuroprivacy.cli import app, repo_root

runner = CliRunner()


def test_demo_plan_lists_four_designed_paths() -> None:
    result = runner.invoke(app, ["demo-plan", "--dry-run"])
    assert result.exit_code == 0
    assert "vendor-a" in result.stdout
    assert "vendor-b" in result.stdout
    assert "vendor-c" in result.stdout
    assert "vendor-d" in result.stdout
    assert "vendor-a.html" in result.stdout
    assert "vendor-d-2025-01.html" in result.stdout
    assert "vendor-d-2025-06.html" in result.stdout
    assert "Observations only" in result.stdout
    assert "Dry run only" in result.stdout
    assert "Network capture enabled: False" in result.stdout


def test_version() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "neuroprivacy" in result.stdout


def test_sample_path() -> None:
    result = runner.invoke(app, ["sample-path"])
    assert result.exit_code == 0
    assert "data/sample" in result.stdout
    assert (repo_root() / "data" / "sample" / "vendor-a.html").is_file()


def test_extract_vendor_a_has_spans_and_offsets() -> None:
    result = runner.invoke(app, ["extract", "--doc", "data/sample/vendor-a.html"])
    assert result.exit_code == 0
    assert "names_neural_data" in result.stdout
    assert "grants_deletion" in result.stdout
    assert "neural data" in result.stdout
    assert "right to delete" in result.stdout
    assert ":" in result.stdout
    assert "span-level citation" in result.stdout
    assert "Observations only" in result.stdout


def test_audit_vendor_b_keyword_baseline_finds_nothing() -> None:
    result = runner.invoke(app, ["audit", "--vendor", "vendor-b"])
    assert result.exit_code == 0
    assert "baseline finds nothing" in result.stdout
    assert "covers_generic_device_data" in result.stdout
    assert "CO-DEF-NEURAL" in result.stdout
    assert "CA-NOTICE" in result.stdout
    assert "Observations only" in result.stdout


def test_audit_vendor_c_show_conflicts() -> None:
    result = runner.invoke(app, ["audit", "--vendor", "vendor-c", "--show-conflicts"])
    assert result.exit_code == 0
    assert "Conflicting spans" in result.stdout
    assert "right to delete" in result.stdout
    assert "cannot delete" in result.stdout
    assert "INDETERMINATE" in result.stdout
    assert "CO-DELETE status: INDETERMINATE" in result.stdout


def test_diff_vendor_d_removed_sharing() -> None:
    result = runner.invoke(app, ["diff", "--vendor", "vendor-d", "--since", "2025-01-01"])
    assert result.exit_code == 0
    assert "discloses_sharing" in result.stdout
    assert "removed clause" in result.stdout
    assert "2025-01-15" in result.stdout
    assert "2025-06-15" in result.stdout


def test_report_writes_html(tmp_path: object) -> None:
    from pathlib import Path

    out = Path(str(tmp_path)) / "index.html"
    result = runner.invoke(app, ["report", "--out", str(out)])
    assert result.exit_code == 0
    assert out.is_file()
    text = out.read_text(encoding="utf-8")
    assert "vendor-a" in text
    assert "not a legal conclusion" in text


def test_capture_refuses_by_default() -> None:
    result = runner.invoke(app, ["capture"])
    assert result.exit_code == 2
    assert "operator_owns_device" in result.stdout


def test_demo_walkthrough() -> None:
    result = runner.invoke(app, ["demo"])
    assert result.exit_code == 0
    assert "vendor-a" in result.stdout
    assert "baseline finds nothing" in result.stdout
    assert "Conflicting spans" in result.stdout
    assert "removed clause" in result.stdout
    assert "wrote" in result.stdout
