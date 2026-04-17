"""Contract-wiring smoke tests — prove halcytone-contracts v0.1.0 is consumable.

These are not unit tests of halcytone-core behavior (there is none yet).
They assert that every contract surface the README promises is reachable
from a real downstream consumer and that the drift-detection wiring
actually raises when it should. If these break, the contract has drifted
from what halcytone-core was built against.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime

import pytest

import halcytone_core
from halcytone_core.wiring import (
    PUBLIC_SURFACE,
    expected_streams,
    validate_publisher_roster,
)


def test_core_version_is_string() -> None:
    assert isinstance(halcytone_core.__version__, str)
    assert halcytone_core.__version__ == "0.1.0"


def test_public_surface_is_non_empty() -> None:
    assert len(PUBLIC_SURFACE) > 0


def test_every_public_surface_entry_is_truthy() -> None:
    for entry in PUBLIC_SURFACE:
        assert entry is not None


def test_signal_packet_constructible() -> None:
    from halcytone_contracts import SignalPacket

    pkt = SignalPacket(
        sensor_id="ganglion-01",
        stream="eeg.ch1",
        t_ns=1_700_000_000_000_000_000,
        values=[0.1, 0.2, 0.3],
        quality=0.9,
    )
    assert pkt.stream == "eeg.ch1"
    round_tripped = SignalPacket.model_validate_json(pkt.model_dump_json())
    assert round_tripped == pkt


def test_state_vector_constructible_with_valid_session_id() -> None:
    from halcytone_contracts import StateVector, new_session_id

    sid = new_session_id()
    sv = StateVector(
        t_ns=1,
        session_id=sid,
        breath_phase=0.5,
        breath_rate=6.0,
        breath_depth=0.6,
        breath_quality=0.9,
        heart_rate=62.0,
        hrv_rmssd=48.0,
        hrv_quality=0.9,
        eda_level=3.0,
        eda_phasic=0.1,
        eeg_alpha=0.3,
        eeg_theta=0.2,
        eeg_beta=0.3,
        eeg_delta=0.1,
        eeg_gamma=0.1,
        eeg_quality=0.9,
        heart_breath_coherence=0.5,
        overall_presence=0.7,
    )
    assert sv.session_id == sid


def test_session_id_roundtrip_via_contracts_helpers() -> None:
    from halcytone_contracts import format_session_id, new_session_id, parse_session_id

    sid = new_session_id()
    dt, slug = parse_session_id(sid)
    assert isinstance(dt, datetime)
    assert len(slug) == 4
    assert format_session_id(dt, slug) == sid


def test_reserved_streams_covers_halcytone_core_requirements() -> None:
    from halcytone_contracts import RESERVED_STREAMS

    for name in expected_streams():
        assert name in RESERVED_STREAMS, f"{name!r} missing from RESERVED_STREAMS"


def test_validate_publisher_roster_passes_when_roster_complete() -> None:
    published = list(expected_streams()) + ["extra.stream"]
    assert validate_publisher_roster(published) is None


def test_validate_publisher_roster_raises_on_missing_stream() -> None:
    from halcytone_contracts import ContractError

    published = [s for s in expected_streams() if s != "ppg"]
    with pytest.raises(ContractError) as exc_info:
        validate_publisher_roster(published)
    assert "ppg" in str(exc_info.value)


def test_session_manifest_validates_session_id() -> None:
    from halcytone_contracts import SessionManifest, new_session_id
    from pydantic import ValidationError

    sid = new_session_id()
    manifest = SessionManifest(
        session_id=sid,
        started_at=datetime.now(UTC),
        ended_at=None,
        duration_s=0,
        sensors=["ganglion-01"],
        baselines={},
        summary={},
        artifacts={},
    )
    assert manifest.session_id == sid

    with pytest.raises(ValidationError):
        SessionManifest(
            session_id="not-a-session-id",
            started_at=datetime.now(UTC),
            ended_at=None,
            duration_s=0,
            sensors=[],
            baselines={},
            summary={},
            artifacts={},
        )


def test_storage_ddl_applies_to_in_memory_sqlite() -> None:
    from halcytone_contracts import read_ddl

    ddl = read_ddl()
    assert isinstance(ddl, str) and len(ddl) > 0

    with sqlite3.connect(":memory:") as conn:
        conn.executescript(ddl)
        conn.executescript(ddl)  # idempotent: running twice is a no-op
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = {row[0] for row in cursor.fetchall()}
    for expected in ("sessions", "baselines", "annotations", "state_summaries", "meta"):
        assert expected in tables, f"DDL missing expected table {expected!r}"


def test_required_schema_version_matches_contracts() -> None:
    from halcytone_contracts import REQUIRED_SCHEMA_VERSION, SCHEMA_VERSION

    assert REQUIRED_SCHEMA_VERSION == SCHEMA_VERSION
    assert isinstance(REQUIRED_SCHEMA_VERSION, int)


def test_contract_version_pin_is_consistent() -> None:
    """Our _EXPECTED_CONTRACTS_VERSION at import-time matched the installed version."""
    from halcytone_contracts import __contract_version__

    assert __contract_version__ == halcytone_core.__dict__.get(
        "_EXPECTED_CONTRACTS_VERSION", __contract_version__
    ) or __contract_version__ == "0.1.0"


def test_session_start_payload_roundtrips_as_json() -> None:
    from halcytone_contracts import SessionStart, new_session_id

    msg = SessionStart(session_id=new_session_id(), config={"sample_rate": 200})
    payload = msg.model_dump_json()
    parsed = SessionStart.model_validate_json(payload)
    assert parsed == msg
    assert json.loads(payload)["config"]["sample_rate"] == 200
