#!/usr/bin/env python3
"""Regression tests for MAP Bedrock's stale_role_bindings runner check.

map-bedrock-operating-structure-2026-08-10.md Sec 2/6 rule 6: a role bound
to an identity that a finalized context-rotation has already superseded
must be caught by machine check, not left to the role itself noticing its
own absence (the exact circularity independent review flagged).
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from MAP_System.graph.runner import scan_role_bindings  # noqa: E402


def _write_bindings(path: Path, bindings: list[dict]) -> None:
    path.write_text(
        json.dumps({"schema_version": 1, "bindings": bindings}),
        encoding="utf-8",
    )


def _write_ledger(path: Path, rotations: dict) -> None:
    body = json.dumps({"schema_version": 1, "revision": 1, "rotations": rotations})
    path.write_text(
        "<!-- hpom: file: shared/context-continuity.md -->\n"
        "<!-- context-rotation-state\n"
        f"{body}\n"
        "-->\n",
        encoding="utf-8",
    )


def test_finalized_rotation_flags_the_role_as_stale() -> None:
    with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
        tmp_path = Path(tmp)
        bindings_path = tmp_path / "bindings.json"
        ledger_path = tmp_path / "ledger.md"
        _write_bindings(
            bindings_path,
            [{"role": "Program Coordinator", "bound_identity": "map-coordinator-hobo"}],
        )
        _write_ledger(
            ledger_path,
            {
                "map-coordinator-hobo": {
                    "phase": "finalized",
                    "finalized_at": "2026-08-10T00:00:00Z",
                    "ack": {"replacement_agent": "map-coordinator-jibo"},
                }
            },
        )

        state = scan_role_bindings(
            {
                "bedrock_bindings_path": str(bindings_path),
                "continuity_ledger_path": str(ledger_path),
                "events": [],
            }
        )

    assert len(state["stale_role_bindings"]) == 1
    finding = state["stale_role_bindings"][0]
    assert finding["role"] == "Program Coordinator"
    assert finding["bound_identity"] == "map-coordinator-hobo"
    assert finding["superseded_by"] == "map-coordinator-jibo"
    assert any("role binding(s) point to a superseded identity" in e for e in state["events"])


def test_live_binding_is_not_flagged() -> None:
    """A binding with no rotation record, or one not yet finalized, is not stale."""
    with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
        tmp_path = Path(tmp)
        bindings_path = tmp_path / "bindings.json"
        ledger_path = tmp_path / "ledger.md"
        _write_bindings(
            bindings_path,
            [{"role": "Program Coordinator", "bound_identity": "map-coordinator-hobo"}],
        )
        _write_ledger(
            ledger_path,
            {
                "map-coordinator-hobo": {
                    "phase": "prepared",
                    "ack": None,
                }
            },
        )

        state = scan_role_bindings(
            {
                "bedrock_bindings_path": str(bindings_path),
                "continuity_ledger_path": str(ledger_path),
                "events": [],
            }
        )

    assert state["stale_role_bindings"] == []


def test_no_ledger_entry_is_not_flagged() -> None:
    with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
        tmp_path = Path(tmp)
        bindings_path = tmp_path / "bindings.json"
        ledger_path = tmp_path / "ledger.md"
        _write_bindings(
            bindings_path,
            [{"role": "Librarian", "bound_identity": "helper-librarian"}],
        )
        _write_ledger(ledger_path, {})

        state = scan_role_bindings(
            {
                "bedrock_bindings_path": str(bindings_path),
                "continuity_ledger_path": str(ledger_path),
                "events": [],
            }
        )

    assert state["stale_role_bindings"] == []


def test_missing_bindings_file_is_not_an_error() -> None:
    with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
        state = scan_role_bindings(
            {
                "bedrock_bindings_path": str(Path(tmp) / "does-not-exist.json"),
                "events": [],
            }
        )
    assert state["stale_role_bindings"] == []


def test_stale_role_bindings_key_is_declared_on_map_state() -> None:
    """Same regression class MapState's TypedDict fields already document:
    an undeclared field is computed correctly but silently dropped from real
    graph output (see test_runner_helper_notes.py's identical assertion for
    helpers_missing_model_tier)."""
    from MAP_System.graph.runner import MapState

    assert "stale_role_bindings" in MapState.__annotations__, (
        "stale_role_bindings must be declared on MapState or the graph "
        "will silently drop it from runner output")


if __name__ == "__main__":
    test_finalized_rotation_flags_the_role_as_stale()
    print("PASS finalized rotation flags the role as stale")
    test_live_binding_is_not_flagged()
    print("PASS live/non-finalized binding is not flagged")
    test_no_ledger_entry_is_not_flagged()
    print("PASS binding with no ledger entry is not flagged")
    test_missing_bindings_file_is_not_an_error()
    print("PASS missing bindings file is not an error")
    test_stale_role_bindings_key_is_declared_on_map_state()
    print("PASS stale_role_bindings key is declared on MapState")
