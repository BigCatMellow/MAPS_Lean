#!/usr/bin/env python3
"""Regression tests for durable helper-note capacity metadata."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from MAP_System.graph.runner import scan_helper_notes  # noqa: E402


def test_manual_active_note_counts_and_terminal_note_does_not() -> None:
    """The documented plain bullet metadata drives capacity, not prose labels."""
    with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
        note_dir = Path(tmp) / "inbox" / "helpers"
        note_dir.mkdir(parents=True)
        (note_dir / "helper-active.md").write_text(
            "# Helper Assignment - audit\n\n"
            "- status: active\n"
            "- owner: codex-lab-lilo\n"
            "- scope: one bounded audit\n",
            encoding="utf-8",
        )
        (note_dir / "helper-complete.md").write_text(
            "# Helper Assignment - completed audit\n\n"
            "- status: complete\n"
            "- owner: codex-lab-lilo\n"
            "- scope: preserved evidence\n",
            encoding="utf-8",
        )

        state = scan_helper_notes({"helper_policy": {"notes_dir": str(note_dir)}})

    assert state["active_helper_notes"] == ["helper-active"]
    note_by_tag = {note["tag"]: note for note in state["helper_notes"]}
    assert note_by_tag["helper-active"]["status"] == "active"
    assert note_by_tag["helper-complete"]["status"] == "complete"



def test_active_helper_without_model_tier_is_reported():
    """TASK-269: helper-agent-guide.md requires the approved model tier to be
    recorded, but nothing could check it until the contract had a field. An
    ACTIVE helper with no `model:` line is reported; one with a tier is not.

    A non-active note is deliberately NOT reported even without a tier: finished
    notes are historical evidence and are not reopened to backfill, so flagging
    them would produce permanent unfixable noise."""
    with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
        note_dir = Path(tmp) / "inbox" / "helpers"
        note_dir.mkdir(parents=True)
        (note_dir / "helper-tiered.md").write_text(
            "# Helper Assignment - review\n\n"
            "- status: active\n"
            "- owner: claude-lab-gabi\n"
            "- provider: claude\n"
            "- model: sonnet\n"
            "- scope: bounded review\n",
            encoding="utf-8",
        )
        (note_dir / "helper-untiered.md").write_text(
            "# Helper Assignment - review\n\n"
            "- status: active\n"
            "- owner: claude-lab-gabi\n"
            "- provider: claude\n"
            "- scope: bounded review\n",
            encoding="utf-8",
        )
        (note_dir / "helper-finished-untiered.md").write_text(
            "# Helper Assignment - old audit\n\n"
            "- status: complete\n"
            "- owner: claude-lab-gabi\n"
            "- provider: claude\n"
            "- scope: preserved evidence\n",
            encoding="utf-8",
        )

        state = scan_helper_notes({"helper_policy": {"notes_dir": str(note_dir)}})

    assert state["helpers_missing_model_tier"] == ["helper-untiered"], (
        state["helpers_missing_model_tier"])
    # capacity accounting must be untouched by this change
    assert sorted(state["active_helper_notes"]) == ["helper-tiered", "helper-untiered"]
    assert any("record no model tier" in e for e in state["events"])


def test_blank_model_tier_counts_as_missing():
    """`- model:` with nothing after it must not satisfy the contract."""
    with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
        note_dir = Path(tmp) / "inbox" / "helpers"
        note_dir.mkdir(parents=True)
        (note_dir / "helper-blank.md").write_text(
            "# Helper Assignment - review\n\n"
            "- status: active\n"
            "- model:   \n"
            "- scope: bounded review\n",
            encoding="utf-8",
        )
        state = scan_helper_notes({"helper_policy": {"notes_dir": str(note_dir)}})
    assert state["helpers_missing_model_tier"] == ["helper-blank"]



def test_missing_tier_key_is_declared_on_map_state():
    """Regression for a bug this task hit in its own implementation.

    scan_helper_notes returned helpers_missing_model_tier and the unit tests
    passed, but the field arrived EMPTY in real runner output while the event
    line correctly named one helper. MapState is a TypedDict and the graph drops
    keys it does not declare, so a field can be computed, logged, and still be
    invisible to every consumer. Unit tests that call scan_helper_notes directly
    cannot see this. Assert the declaration itself."""
    from MAP_System.graph.runner import MapState

    assert "helpers_missing_model_tier" in MapState.__annotations__, (
        "helpers_missing_model_tier must be declared on MapState or the graph "
        "will silently drop it from runner output")


if __name__ == "__main__":
    test_manual_active_note_counts_and_terminal_note_does_not()
    print("PASS manual active helper note counts; terminal note does not")
    test_active_helper_without_model_tier_is_reported()
    print("PASS active helper without model tier is reported")
    test_blank_model_tier_counts_as_missing()
    print("PASS blank model tier counts as missing")
    test_missing_tier_key_is_declared_on_map_state()
    print("PASS missing-tier key is declared on MapState")
