"""Smoke-import every public surface of halcytone-contracts.

This module exists to prove that `halcytone-contracts` v0.1.0 is actually
consumable from a real downstream repo. If the contracts package adds,
renames, or removes a public symbol, this file (and `tests/test_wiring.py`)
fail first — before any production code notices.

The function `expected_streams()` is the single place halcytone-core
declares which reserved streams it needs to see from its publishers.
Sprint 2+ will move this to a richer roster-negotiation protocol; for
now it's a flat list fed to `validate_stream_roster`.
"""

from __future__ import annotations

from collections.abc import Iterable

from halcytone_contracts import (
    RESERVED_STREAMS,
    Annotation,
    ContractError,
    MapperConfigUpdate,
    SessionId,
    SessionManifest,
    SessionStart,
    SessionStop,
    SignalPacket,
    StateVector,
    StreamSpec,
    format_session_id,
    new_session_id,
    parse_session_id,
    read_ddl,
    validate_stream_roster,
)

__all__ = [
    "PUBLIC_SURFACE",
    "expected_streams",
    "validate_publisher_roster",
]


PUBLIC_SURFACE: tuple[object, ...] = (
    SignalPacket,
    StreamSpec,
    RESERVED_STREAMS,
    StateVector,
    SessionStart,
    SessionStop,
    Annotation,
    MapperConfigUpdate,
    SessionManifest,
    SessionId,
    format_session_id,
    parse_session_id,
    new_session_id,
    read_ddl,
    validate_stream_roster,
    ContractError,
)
"""Every public symbol halcytone-core relies on. The test suite asserts
this tuple stays non-empty and that every entry is importable."""


def expected_streams() -> tuple[str, ...]:
    """Return the stream roster halcytone-core v0.1.0 needs from publishers.

    Minimal v0.1 scope: one channel of each modality that the fusion layer
    will eventually consume. Wider rosters (full 4-channel EEG, both HRV
    variants, IMU) land in sprint 2+ once the fusion implementation lands.
    """
    return (
        "eeg.ch1",
        "ppg",
        "hrv.rmssd",
        "eda",
        "skin_temp",
        "breath.envelope",
    )


def validate_publisher_roster(published: Iterable[str]) -> None:
    """Raise `ContractError` if `published` is missing any expected stream."""
    validate_stream_roster(published, expected_streams())
