#!/usr/bin/env python3
"""Isolated submission-authorship regressions for TASK-274."""

from __future__ import annotations

import json
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
SCHEMA = ROOT / "migration" / "schema.sql"
PRODUCTION_EVENT_LOG = ROOT / "events" / "events.jsonl"

import sys

if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from MAP_System.db.claims import submit_task


def init_claimed_task(db: Path) -> None:
    with sqlite3.connect(db) as conn:
        conn.executescript(SCHEMA.read_text(encoding="utf-8"))
        conn.execute(
            """
            INSERT INTO agents (agent_id, label, agent_type, status)
            VALUES
                ('worker-a', 'Worker A', 'core', 'available'),
                ('worker-b', 'Worker B', 'core', 'available'),
                ('command-center', 'Command Center', 'core', 'available')
            """
        )
        conn.execute(
            """
            INSERT INTO tasks
                (task_id, project_id, title, description, task_type, role,
                 status, owner, claimed_by, lease_expires_at, heartbeat_at,
                 attempt, max_attempts)
            VALUES
                ('TASK-SUB', 'TEST', 'Submission event', 'Regression fixture',
                 'implementation', 'implementer', 'IN_PROGRESS',
                 'command-center', 'worker-a', datetime('now', '+30 minutes'),
                 datetime('now'), 1, 3)
            """
        )
        conn.execute(
            """
            INSERT INTO task_output_paths (task_id, path)
            VALUES ('TASK-SUB', 'MAP_System/artifacts/tests/task-sub.md')
            """
        )


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_success_emits_exact_event_and_preserves_row_contract() -> None:
    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)
        db = temp / "map.db"
        event_log = temp / "custom-events.jsonl"
        init_claimed_task(db)

        assert submit_task(
            "TASK-SUB",
            "worker-a",
            db_path=db,
            event_log=event_log,
        ) is True

        with sqlite3.connect(db) as conn:
            row = conn.execute(
                """
                SELECT status, claimed_by, lease_expires_at, heartbeat_at, attempt
                FROM tasks WHERE task_id='TASK-SUB'
                """
            ).fetchone()
            events = conn.execute(
                """
                SELECT event_type, sender_id, summary, artifact_paths
                FROM events WHERE task_id='TASK-SUB'
                """
            ).fetchall()
        assert row == ("SUBMITTED", None, None, None, 1), row
        assert events == [
            (
                "SUBMISSION",
                "worker-a",
                "TASK-SUB submitted for independent review by worker-a.",
                '["MAP_System/artifacts/tests/task-sub.md"]',
            )
        ], events

        payloads = read_jsonl(event_log)
        assert len(payloads) == 1, payloads
        event = payloads[0]
        assert event["type"] == "SUBMISSION"
        assert event["task_id"] == event["target"] == "TASK-SUB"
        assert event["sender"] == event["actor"] == "worker-a"
        assert event["action"] == "submission"
        assert event["trace_id"] == "task:TASK-SUB"


def test_repeat_submit_returns_false_and_emits_no_duplicate() -> None:
    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)
        db = temp / "map.db"
        event_log = temp / "events.jsonl"
        init_claimed_task(db)

        assert submit_task("TASK-SUB", "worker-a", db_path=db, event_log=event_log)
        assert not submit_task("TASK-SUB", "worker-a", db_path=db, event_log=event_log)
        assert len(read_jsonl(event_log)) == 1
        with sqlite3.connect(db) as conn:
            count = conn.execute(
                """
                SELECT count(*) FROM events
                WHERE task_id='TASK-SUB' AND event_type='SUBMISSION'
                """
            ).fetchone()[0]
        assert count == 1


def test_wrong_claimant_failure_has_no_event_or_mutation() -> None:
    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)
        db = temp / "map.db"
        event_log = temp / "events.jsonl"
        init_claimed_task(db)

        assert not submit_task(
            "TASK-SUB",
            "worker-b",
            db_path=db,
            event_log=event_log,
        )
        assert read_jsonl(event_log) == []
        with sqlite3.connect(db) as conn:
            row = conn.execute(
                "SELECT status, claimed_by FROM tasks WHERE task_id='TASK-SUB'"
            ).fetchone()
            count = conn.execute("SELECT count(*) FROM events").fetchone()[0]
        assert row == ("IN_PROGRESS", "worker-a")
        assert count == 0


def test_lost_race_emits_no_event() -> None:
    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)
        db = temp / "map.db"
        event_log = temp / "events.jsonl"
        init_claimed_task(db)

        with patch("MAP_System.db.claims.release_task", return_value=False):
            assert not submit_task(
                "TASK-SUB",
                "worker-a",
                db_path=db,
                event_log=event_log,
            )
        assert read_jsonl(event_log) == []
        with sqlite3.connect(db) as conn:
            count = conn.execute("SELECT count(*) FROM events").fetchone()[0]
        assert count == 0


def test_default_for_scratch_db_is_scratch_local_not_production() -> None:
    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)
        db = temp / "map.db"
        scratch_log = temp / "events.jsonl"
        init_claimed_task(db)
        production_before = (
            PRODUCTION_EVENT_LOG.stat().st_size
            if PRODUCTION_EVENT_LOG.exists()
            else None
        )

        assert submit_task("TASK-SUB", "worker-a", db_path=db)
        assert len(read_jsonl(scratch_log)) == 1
        production_after = (
            PRODUCTION_EVENT_LOG.stat().st_size
            if PRODUCTION_EVENT_LOG.exists()
            else None
        )
        assert production_after == production_before


def test_event_log_failure_occurs_after_committed_transition() -> None:
    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)
        db = temp / "map.db"
        event_log_directory = temp / "event-log-directory"
        event_log_directory.mkdir()
        init_claimed_task(db)

        try:
            submit_task(
                "TASK-SUB",
                "worker-a",
                db_path=db,
                event_log=event_log_directory,
            )
        except IsADirectoryError:
            pass
        else:
            raise AssertionError("expected event-log append failure")

        with sqlite3.connect(db) as conn:
            row = conn.execute(
                "SELECT status, claimed_by FROM tasks WHERE task_id='TASK-SUB'"
            ).fetchone()
            count = conn.execute("SELECT count(*) FROM events").fetchone()[0]
        assert row == ("SUBMITTED", None)
        assert count == 0


def test_absence_means_unknown_author_not_no_self_review() -> None:
    note = (
        ROOT / "artifacts" / "tests" / "task-submission-event-delivery-note.md"
    ).read_text(encoding="utf-8")
    assert "UNKNOWN AUTHOR" in note
    assert "never evidence that no self-review occurred" in note


def main() -> int:
    tests = [
        value
        for name, value in sorted(globals().items())
        if name.startswith("test_")
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"{len(tests)} submission-event tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
