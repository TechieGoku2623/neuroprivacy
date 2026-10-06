from __future__ import annotations

import pytest

from neuroprivacy.capture import NetworkCaptureRefused, attempt_network_capture
from neuroprivacy.config import NetworkCaptureSettings, Settings


def test_capture_refuses_without_operator_owned_device() -> None:
    settings = Settings(
        network_capture=NetworkCaptureSettings(enabled=True, operator_owns_device=False)
    )
    with pytest.raises(NetworkCaptureRefused, match="operator_owns_device"):
        attempt_network_capture(settings)


def test_capture_refuses_when_disabled_even_if_owned() -> None:
    settings = Settings(
        network_capture=NetworkCaptureSettings(enabled=False, operator_owns_device=True)
    )
    with pytest.raises(NetworkCaptureRefused, match="enabled is false"):
        attempt_network_capture(settings)


def test_capture_stub_permits_gated_no_op() -> None:
    settings = Settings(
        network_capture=NetworkCaptureSettings(enabled=True, operator_owns_device=True)
    )
    attempt = attempt_network_capture(settings)
    assert attempt.allowed is True
    assert "No packets are collected" in attempt.reason
