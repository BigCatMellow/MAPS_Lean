#!/usr/bin/env python3
"""Focused tests for the TASK-279 generated active-state projection."""

from __future__ import annotations

import importlib.util
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "render_active_state.py"
SPEC = importlib.util.spec_from_file_location("render_active_state", SCRIPT)
assert SPEC and SPEC.loader
render_active_state = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = render_active_state
SPEC.loader.exec_module(render_active_state)


STATE_TEMPLATE = """# Fixture

Free prose says TASK-999 is RELEASED. It is historical, not lifecycle truth.

<!-- BEGIN GENERATED ACTIVE LANES -->
old generated content
<!-- END GENERATED ACTIVE LANES -->

Another table:

| Task | State |
|---|---|
| TASK-998 | READY |
"""


class RenderActiveStateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.db = self.root / "map.db"
        self.annotations = self.root / "annotations.json"
        self.state = self.root / "current-state.md"
        self.state.write_text(STATE_TEMPLATE, encoding="utf-8")
        with sqlite3.connect(self.db) as conn:
            conn.execute(
                """
                CREATE TABLE tasks (
                    task_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    owner TEXT,
                    claimed_by TEXT
                )
                """
            )
            conn.executemany(
                "INSERT INTO tasks(task_id, status, owner, claimed_by) VALUES (?, ?, ?, ?)",
                [
                    ("TASK-001", "READY", "command-center", None),
                    ("TASK-002", "IN_PROGRESS", "codex-lab-one", "codex-lab-two"),
                ],
            )
        self.write_annotations(
            {
                "TASK-001": {"order": 2, "rationale": "Second.", "gate": ""},
                "TASK-002": {"order": 1, "rationale": "First.", "gate": "Gate text."},
            }
        )

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def write_annotations(self, lanes: dict) -> None:
        self.annotations.write_text(
            json.dumps({"schema_version": 1, "lanes": lanes}, indent=2) + "\n",
            encoding="utf-8",
        )

    def update_task(self, task_id: str, status: str, claimed_by: str | None = None) -> None:
        with sqlite3.connect(self.db) as conn:
            conn.execute(
                "UPDATE tasks SET status=?, claimed_by=? WHERE task_id=?",
                (status, claimed_by, task_id),
            )

    def render(self) -> tuple[bool, list]:
        return render_active_state.render_file(self.state, self.db, self.annotations)

    def test_lifecycle_claim_submit_approve_release_projection(self) -> None:
        transitions = [
            ("READY", None, "| 2 | TASK-001 | READY |"),
            ("IN_PROGRESS", "codex-lab-worker", "| 2 | TASK-001 | IN_PROGRESS |"),
            ("SUBMITTED", None, "| 2 | TASK-001 | SUBMITTED |"),
            ("APPROVED", None, "| 2 | TASK-001 | APPROVED |"),
        ]
        for status, claimant, expected in transitions:
            with self.subTest(status=status):
                self.update_task("TASK-001", status, claimant)
                self.render()
                rendered = self.state.read_text(encoding="utf-8")
                self.assertIn(expected, rendered)
                if claimant:
                    self.assertIn("`codex-lab-worker` recorded", rendered)

        self.update_task("TASK-001", "RELEASED")
        _, diagnostics = self.render()
        rendered = self.state.read_text(encoding="utf-8")
        self.assertNotIn("| 2 | TASK-001 |", rendered)
        self.assertIn("STALE annotation TASK-001: canonical status is RELEASED", rendered)
        self.assertEqual(["STALE"], [item.kind for item in diagnostics])

    def test_annotations_survive_and_repeat_render_is_noop(self) -> None:
        annotation_bytes = self.annotations.read_bytes()
        changed, diagnostics = self.render()
        self.assertTrue(changed)
        self.assertEqual([], diagnostics)
        first = self.state.read_bytes()

        changed, diagnostics = self.render()
        self.assertFalse(changed)
        self.assertEqual([], diagnostics)
        self.assertEqual(first, self.state.read_bytes())
        self.assertEqual(annotation_bytes, self.annotations.read_bytes())

    def test_deterministic_annotation_order(self) -> None:
        self.render()
        rendered = self.state.read_text(encoding="utf-8")
        self.assertLess(rendered.index("| 1 | TASK-002 |"), rendered.index("| 2 | TASK-001 |"))

    def test_orphan_and_stale_annotations_are_explicit(self) -> None:
        self.update_task("TASK-002", "DONE")
        self.write_annotations(
            {
                "TASK-404": {"order": 1, "rationale": "Missing.", "gate": ""},
                "TASK-002": {"order": 2, "rationale": "Finished.", "gate": ""},
                "TASK-001": {"order": 3, "rationale": "Still active.", "gate": ""},
            }
        )
        _, diagnostics = self.render()
        rendered = self.state.read_text(encoding="utf-8")
        self.assertIn("ORPHAN annotation TASK-404: task is absent from map.db", rendered)
        self.assertIn("STALE annotation TASK-002: canonical status is DONE", rendered)
        self.assertEqual(["ORPHAN", "STALE"], [item.kind for item in diagnostics])

    def test_free_prose_and_other_tables_are_preserved_not_parsed(self) -> None:
        self.render()
        rendered = self.state.read_text(encoding="utf-8")
        self.assertIn("Free prose says TASK-999 is RELEASED.", rendered)
        self.assertIn("| TASK-998 | READY |", rendered)
        self.assertNotIn("TASK-999:", rendered)
        self.assertNotIn("TASK-998:", rendered)

    def test_check_mode_reports_drift_without_writing(self) -> None:
        before = self.state.read_bytes()
        changed, diagnostics = render_active_state.render_file(
            self.state, self.db, self.annotations, check=True
        )
        self.assertTrue(changed)
        self.assertEqual([], diagnostics)
        self.assertEqual(before, self.state.read_bytes())


class AuthorityLineTests(unittest.TestCase):
    """TASK-310: current-state.md must name authority revision/freshness,
    never present a stale/unavailable/invalid mirror as an unqualified
    snapshot -- and never regress the no-authority-arg backward compatibility
    every existing render_active_state caller/test relies on."""

    def test_no_authority_argument_omits_the_line_entirely(self) -> None:
        self.assertIsNone(render_active_state.authority_line(None))

    def test_fresh_authority_is_a_plain_unqualified_line(self) -> None:
        line = render_active_state.authority_line(
            {
                "freshness": "FRESH",
                "mode": "mirror",
                "authority_host": "192.168.1.153",
                "authority_revision": "sha256:" + "a" * 64,
                "last_successful_sync_at": "2026-07-30T13:10:07Z",
            }
        )
        self.assertIn("`FRESH`", line)
        self.assertIn("192.168.1.153", line)
        self.assertNotIn("do not treat", line.lower())

    def test_authoritative_is_also_a_plain_line(self) -> None:
        line = render_active_state.authority_line(
            {"freshness": "AUTHORITATIVE", "mode": "authority", "authority_host": None}
        )
        self.assertIn("`AUTHORITATIVE`", line)
        self.assertIn("host=`self`", line)

    def test_stale_unavailable_invalid_all_carry_an_explicit_warning(self) -> None:
        for freshness in ("STALE", "UNAVAILABLE", "INVALID"):
            with self.subTest(freshness=freshness):
                line = render_active_state.authority_line(
                    {"freshness": freshness, "mode": "mirror", "last_error": "sync failed"}
                )
                self.assertIn(f"`{freshness}`", line)
                self.assertIn("do not treat this table as", line.lower())
                self.assertIn("sync failed", line)

    def test_missing_last_error_still_renders(self) -> None:
        line = render_active_state.authority_line({"freshness": "UNAVAILABLE"})
        self.assertIn("error=`none`", line)

    def test_omitted_by_default_existing_callers_unaffected(self) -> None:
        """The full render pipeline, called exactly as every pre-existing
        test calls it (no authority kwarg), must not gain the line."""
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            db = root / "map.db"
            annotations = root / "annotations.json"
            state = root / "current-state.md"
            state.write_text(STATE_TEMPLATE, encoding="utf-8")
            with sqlite3.connect(db) as conn:
                conn.execute(
                    "CREATE TABLE tasks (task_id TEXT PRIMARY KEY, status TEXT, "
                    "owner TEXT, claimed_by TEXT)"
                )
            annotations.write_text(
                json.dumps({"schema_version": 1, "lanes": {}}), encoding="utf-8"
            )
            render_active_state.render_file(state, db, annotations)
            rendered = state.read_text(encoding="utf-8")
        self.assertNotIn("Authority freshness", rendered)

    def test_stale_authority_is_visible_in_a_full_render(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            db = root / "map.db"
            annotations = root / "annotations.json"
            state = root / "current-state.md"
            state.write_text(STATE_TEMPLATE, encoding="utf-8")
            with sqlite3.connect(db) as conn:
                conn.execute(
                    "CREATE TABLE tasks (task_id TEXT PRIMARY KEY, status TEXT, "
                    "owner TEXT, claimed_by TEXT)"
                )
            annotations.write_text(
                json.dumps({"schema_version": 1, "lanes": {}}), encoding="utf-8"
            )
            render_active_state.render_file(
                state,
                db,
                annotations,
                authority={"freshness": "STALE", "mode": "mirror", "last_error": "age 400s"},
            )
            rendered = state.read_text(encoding="utf-8")
        self.assertIn("`STALE`", rendered)
        self.assertIn("do not treat this table as", rendered.lower())


if __name__ == "__main__":
    unittest.main()
