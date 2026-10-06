"""Optional network observation stub.

Gated to operator-owned devices. Refuses unless operator_owns_device is true.
No packet capture, no scraping behind authentication, no reverse engineering.
"""

from __future__ import annotations

from neuroprivacy.config import Settings, get_settings
from neuroprivacy.schemas import CaptureAttempt


class NetworkCaptureRefused(RuntimeError):
    """Raised when the capture stub is not allowed to run."""


def attempt_network_capture(
    settings: Settings | None = None,
    *,
    operator_owns_device: bool | None = None,
) -> CaptureAttempt:
    """Refuse unless the operator explicitly owns the device.

    This is a stub. Even a permitted call does not collect traffic.
    """

    cfg = settings or get_settings()
    owns = (
        cfg.network_capture.operator_owns_device
        if operator_owns_device is None
        else operator_owns_device
    )
    enabled = cfg.network_capture.enabled
    if not owns:
        attempt = CaptureAttempt(
            allowed=False,
            operator_owns_device=False,
            enabled=enabled,
            reason=(
                "Network capture refused: operator_owns_device is not true. "
                "This stub never observes a device the operator does not own. "
                "No authenticated scrape. No reverse engineering."
            ),
        )
        raise NetworkCaptureRefused(attempt.reason)
    if not enabled:
        attempt = CaptureAttempt(
            allowed=False,
            operator_owns_device=True,
            enabled=False,
            reason=(
                "Network capture refused: enabled is false. "
                "Set NEUROPRIVACY_NETWORK_CAPTURE=1 only on an operator-owned device."
            ),
        )
        raise NetworkCaptureRefused(attempt.reason)
    return CaptureAttempt(
        allowed=True,
        operator_owns_device=True,
        enabled=True,
        reason=(
            "Capture stub is gated on and would attach only to an operator-owned "
            "device. No packets are collected in this slice. No circumvention."
        ),
    )
