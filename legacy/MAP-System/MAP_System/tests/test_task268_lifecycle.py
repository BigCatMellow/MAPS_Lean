#!/usr/bin/env python3
"""End-to-end lifecycle regressions for TASK-268."""

from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
SCHEMA = ROOT / "migration" / "schema.sql"
MAP_TASK = ROOT / "scripts" / "map_task.py"
EXPORTER = ROOT / "migration" / "export_to_files.py"
PYTHON = ROOT / ".venv" / "bin" / "python"

if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from MAP_System.db.claims import claim_review


def init_claimed_task(db: Path) -> None:
    with sqlite3.connect(db) as conn:
        conn.executescript(SCHEMA.read_text(encoding="utf-8"))
        conn.execute(
            """
            INSERT INTO agents (agent_id, label, agent_type, status)
            VALUES
                ('worker-a', 'Worker A', 'core', 'available'),
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
                ('TASK-LC', 'TEST', 'Lifecycle seam', 'Regression fixture',
                 'implementation', 'implementer', 'IN_PROGRESS',
                 'command-center', 'worker-a', datetime('now', '+30 minutes'),
                 datetime('now'), 1, 3)
            """
        )
        conn.execute(
            """
            INSERT INTO task_acceptance_criteria (task_id, criterion)
            VALUES ('TASK-LC', 'submission stays synchronized')
            """
        )
        conn.execute(
            """
            INSERT INTO task_output_paths (task_id, path)
            VALUES ('TASK-LC', 'MAP_System/artifacts/tests/task-lc.md')
            """
        )


def export_initial_state(db: Path, mirror_root: Path) -> None:
    result = subprocess.run(
        [
            str(PYTHON),
            str(EXPORTER),
            "--db",
            str(db),
            "--output-dir",
            str(mirror_root),
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def run_submit(
    db: Path,
    mirror_root: Path,
    event_log: Path,
    *,
    actor: str,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            str(PYTHON),
            str(MAP_TASK),
            "--db",
            str(db),
            "--output-dir",
            str(mirror_root),
            "--event-log",
            str(event_log),
            "submit",
            "TASK-LC",
            "--actor",
            actor,
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
    )


def load_graph_task(mirror_root: Path) -> dict:
    graph = json.loads(
        (mirror_root / "workflow" / "task_graph.json").read_text(encoding="utf-8")
    )
    return next(task for task in graph["tasks"] if task["task_id"] == "TASK-LC")


def test_submit_synchronizes_sqlite_event_mirrors_and_reviewer_identity() -> None:
    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)
        db = temp / "map.db"
        mirrors = temp / "mirror"
        event_log = temp / "events.jsonl"
        init_claimed_task(db)
        export_initial_state(db, mirrors)

        result = run_submit(db, mirrors, event_log, actor="worker-a")
        assert result.returncode == 0, result.stderr

        with sqlite3.connect(db) as conn:
            task_row = conn.execute(
                """
                SELECT status, claimed_by, lease_expires_at, heartbeat_at
                FROM tasks WHERE task_id='TASK-LC'
                """
            ).fetchone()
            db_events = conn.execute(
                """
                SELECT event_type, sender_id
                FROM events
                WHERE task_id='TASK-LC' AND event_type='SUBMISSION'
                """
            ).fetchall()
        assert task_row == ("SUBMITTED", None, None, None), task_row
        assert db_events == [("SUBMISSION", "worker-a")], db_events

        events = [
            json.loads(line)
            for line in event_log.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        assert len(events) == 1, events
        event = events[0]
        assert event["type"] == "SUBMISSION"
        assert event["sender"] == event["actor"] == "worker-a"
        assert event["task_id"] == event["target"] == "TASK-LC"
        assert event["action"] == "submission"
        assert event["trace_id"] == "task:TASK-LC"

        task_mirror = json.loads(
            (mirrors / "tasks" / "TASK-LC.json").read_text(encoding="utf-8")
        )
        assert task_mirror["status"] == "SUBMITTED"
        assert load_graph_task(mirrors)["status"] == "SUBMITTED"

        # Reproduce the second live seam: a valid reviewer that has never been
        # registered can claim the now-open queue and receives a durable,
        # diagnosable identity/claim record.
        assert claim_review("TASK-LC", "fresh-reviewer", db_path=db) is True
        with sqlite3.connect(db) as conn:
            agent = conn.execute(
                "SELECT agent_type, status FROM agents WHERE agent_id='fresh-reviewer'"
            ).fetchone()
            review = conn.execute(
                """
                SELECT reviewer_id, completed_at FROM reviews
                WHERE task_id='TASK-LC'
                """
            ).fetchone()
        assert agent == ("core", "available"), agent
        assert review == ("fresh-reviewer", None), review


def test_submit_refuses_a_non_claimant_without_side_effects() -> None:
    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)
        db = temp / "map.db"
        mirrors = temp / "mirror"
        event_log = temp / "events.jsonl"
        init_claimed_task(db)
        export_initial_state(db, mirrors)

        result = run_submit(db, mirrors, event_log, actor="worker-b")
        assert result.returncode == 1
        assert "not claimed by worker-b" in result.stderr
        assert not event_log.exists()

        with sqlite3.connect(db) as conn:
            row = conn.execute(
                "SELECT status, claimed_by FROM tasks WHERE task_id='TASK-LC'"
            ).fetchone()
            event_count = conn.execute(
                "SELECT count(*) FROM events WHERE task_id='TASK-LC'"
            ).fetchone()[0]
        assert row == ("IN_PROGRESS", "worker-a"), row
        assert event_count == 0
        assert load_graph_task(mirrors)["status"] == "IN_PROGRESS"


def test_repeat_submit_emits_no_duplicate_event() -> None:
    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)
        db = temp / "map.db"
        mirrors = temp / "mirror"
        event_log = temp / "events.jsonl"
        init_claimed_task(db)
        export_initial_state(db, mirrors)

        first = run_submit(db, mirrors, event_log, actor="worker-a")
        second = run_submit(db, mirrors, event_log, actor="worker-a")
        assert first.returncode == 0, first.stderr
        assert second.returncode == 1
        assert "status=SUBMITTED" in second.stderr

        events = [
            json.loads(line)
            for line in event_log.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        assert len(events) == 1, events
        with sqlite3.connect(db) as conn:
            count = conn.execute(
                """
                SELECT count(*) FROM events
                WHERE task_id='TASK-LC' AND event_type='SUBMISSION'
                """
            ).fetchone()[0]
        assert count == 1


def main() -> int:
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_")]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"{len(tests)} TASK-268 lifecycle tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
