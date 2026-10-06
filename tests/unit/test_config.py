from __future__ import annotations

from neuroprivacy.config import get_settings, network_capture_allowed
from neuroprivacy.logging import configure_logging


def test_settings_point_at_committed_sample_dir() -> None:
    settings = get_settings()
    assert (settings.sample_dir / "vendor-a.html").is_file()
    assert (settings.research_dir / "run_all.py").is_file()
    assert settings.network_capture.enabled is False


def test_network_capture_default_off() -> None:
    assert network_capture_allowed() is False


def test_configure_logging_does_not_raise() -> None:
    configure_logging()


def test_configure_logging_json(monkeypatch: object) -> None:
    monkeypatch.setenv("NEUROPRIVACY_ENV", "prod")  # type: ignore[attr-defined]
    configure_logging()


def test_network_capture_env(monkeypatch: object) -> None:
    monkeypatch.setenv("NEUROPRIVACY_NETWORK_CAPTURE", "1")  # type: ignore[attr-defined]
    settings = get_settings()
    assert settings.network_capture.enabled is True
    assert network_capture_allowed(settings) is True
