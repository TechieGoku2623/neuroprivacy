"""Process configuration. No secrets are required for Phase 0."""

from __future__ import annotations

import os
from pathlib import Path

from pydantic import BaseModel, Field


class NetworkCaptureSettings(BaseModel):
    """Optional network observation. Off unless the operator opts in.

    Network capture is gated to operator-owned devices. The stub refuses
    unless operator_owns_device is true. Circumvention is out of scope.
    """

    enabled: bool = False
    operator_owns_device: bool = False
    operator_owned_devices_only: bool = True
    require_explicit_opt_in: bool = True


class Settings(BaseModel):
    env: str = Field(default="dev")
    repo_root: Path = Field(default_factory=lambda: Path(__file__).resolve().parents[2])
    pretty_logs: bool = True
    network_capture: NetworkCaptureSettings = Field(default_factory=NetworkCaptureSettings)

    @property
    def sample_dir(self) -> Path:
        return self.repo_root / "data" / "sample"

    @property
    def research_dir(self) -> Path:
        return self.repo_root / "research" / "phase0"

    @property
    def llm_cache_path(self) -> Path:
        return self.sample_dir / "llm_cache.json"


def get_settings() -> Settings:
    enabled = os.environ.get("NEUROPRIVACY_NETWORK_CAPTURE", "0") == "1"
    owns_device = os.environ.get("NEUROPRIVACY_OPERATOR_OWNS_DEVICE", "0") == "1"
    return Settings(
        env=os.environ.get("NEUROPRIVACY_ENV", "dev"),
        pretty_logs=os.environ.get("NEUROPRIVACY_ENV", "dev") != "prod",
        network_capture=NetworkCaptureSettings(
            enabled=enabled,
            operator_owns_device=owns_device,
            operator_owned_devices_only=True,
            require_explicit_opt_in=True,
        ),
    )


def network_capture_allowed(settings: Settings | None = None) -> bool:
    """True only when every gate is satisfied. Default is False."""

    cfg = settings or get_settings()
    capture = cfg.network_capture
    return (
        capture.enabled
        and capture.operator_owns_device
        and capture.operator_owned_devices_only
        and capture.require_explicit_opt_in
    )
