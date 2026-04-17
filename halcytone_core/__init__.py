"""halcytone-core — fusion, session lifecycle, storage orchestration.

This package is the consumer of `halcytone-contracts`. At import time it
performs a contract-version check so a mispin crashes loud instead of
later, inside a session, in a way that looks like a sensor bug.

v0.1.0 is a stub — it proves every public surface of halcytone-contracts
v0.1.0 is importable and constructible, wiring no real fusion logic yet.
That comes in later sprints.
"""

from __future__ import annotations

from halcytone_contracts import check_contract_version

__version__: str = "0.1.0"

# The contract version this release of halcytone-core was developed
# against. Pinned to a concrete semver, not `halcytone_contracts.__contract_version__`
# — we want to notice when the installed contracts package drifts from the
# one we were built against.
_EXPECTED_CONTRACTS_VERSION = "0.1.0"

check_contract_version(_EXPECTED_CONTRACTS_VERSION)

__all__ = ["__version__"]
