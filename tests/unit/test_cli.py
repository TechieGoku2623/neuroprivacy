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
