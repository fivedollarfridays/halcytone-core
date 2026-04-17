# halcytone-core

Fusion, session lifecycle, and storage orchestration for the Halcytone biofeedback fleet.

## Status

**v0.1.0 — consumer stub.** This release is intentionally minimal: it proves that `halcytone-contracts` v0.1.0 is actually consumable from a real downstream repo. No fusion logic, no sensor orchestration, no storage engine yet — those arrive in later sprints.

The module `halcytone_core.wiring` imports every public surface of `halcytone-contracts` and the test suite constructs each model, round-trips JSON, applies the SQLite DDL to an in-memory database, and exercises `validate_stream_roster` + `check_contract_version`. If the contracts package drifts from what this release was built against, `halcytone-core` fails at import or on the first test rather than silently producing bad data.

## Architecture position

```
halcytone-sensors  →  LSL streams  →  halcytone-core  →  StateVectors + manifest
                                            ↓
                                      halcytone-{audio,hud,publish}
```

`halcytone-core` is the only fleet repo that consumes every public surface of `halcytone-contracts`. That makes it the strongest forcing function for the contract: if a contract change breaks core, it would have broken the full fleet — catch it here first.

## Install

```bash
pip install -e '.[dev]'
```

`halcytone-contracts` is pulled in as a git dependency pinned to `v0.1.0`:

```toml
halcytone-contracts @ git+https://github.com/fivedollarfridays/halcytone-contracts.git@v0.1.0
```

For local multi-repo development, override the git install with an editable sibling checkout:

```bash
pip install -e ../halcytone-contracts
pip install -e '.[dev]'  # re-run after so core's metadata is registered
```

## Versioning

Follows the [halcytone-contracts versioning policy](https://github.com/fivedollarfridays/halcytone-contracts#versioning). While both packages are in 0.x, `halcytone-core` pins `halcytone-contracts` to a specific tag — minor contract bumps (e.g. `0.1 → 0.2`) are breaking and require a deliberate re-pin.

## Tests

```bash
pytest
ruff check .
```
