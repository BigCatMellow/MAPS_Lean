#!/usr/bin/env python3
"""Focused tests for the sanctioned task-retirement verb (TASK-295).

Sixteen tasks reached RETIRED via raw SQL because no sanctioned map_task.py
verb existed -- most recently TASK-053 (mapfinish-guru, 2026-07-28), the
third instance of the same missing-lifecycle-verb pattern REPAIR-0009 and
REPAIR-0010/0012 already hit. These tests pin the verb's happy path and its
refusals -- retirement must close out abandoned/superseded work without ever
being usable to quietly reopen or overwrite a completed task.
"""

from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from MAP_System.db.claims import retire_task  # noqa: E402


def make_db(path: Path) -> None:
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(
        """
        CREATE TABLE agents (
            agent_id TEXT PRIMARY KEY,
            label TEXT,
            agent_type TEXT,
            status TEXT
        );
        CREATE TABLE tasks (
            task_id TEXT PRIMARY KEY,
            status TEXT NOT NULL,
            owner TEXT REFERENCES agents(agent_id),
            claimed_by TEXT,
            lease_expires_at TEXT,
            heartbeat_at TEXT,
            updated_at TEXT
        );
        INSERT INTO agents (agent_id, label, agent_type, status)
        VALUES ('owner', 'Owner', 'core', 'available');
        """
    )
    conn.commit()
    conn.close()


def insert_task(
    path: Path, task_id: str, status: str = "APPROVED",
    claimed_by: str | None = None, lease_expires_at: str | None = None,
) -> None:
    with sqlite3.connect(path) as conn:
        conn.execute(
            """
            INSERT INTO tasks (task_id, status, owner, claimed_by, lease_expires_at)
            VALUES (?, ?, 'owner', ?, ?)
            """,
            (task_id, status, claimed_by, lease_expires_at),
        )


def row(path: Path, task_id: str):
    with sqlite3.connect(path) as conn:
        return conn.execute(
            "SELECT status, claimed_by, lease_expires_at FROM tasks WHERE task_id=?",
            (task_id,),
        ).fetchone()


def test_successful_retirement_from_approved() -> None:
    """TASK-053's exact shape: retiring an APPROVED task must be allowed --
    retirement is a closure of abandoned work, not a review verdict, so it
    does not share extend-attempts' narrower terminal set."""
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        make_db(db)
        insert_task(db, "TASK-1", status="APPROVED", claimed_by="claimer", lease_expires_at="2026-01-01")

        result = retire_task(
            "TASK-1", "  mapfinish-guru  ", "  deliverable lost in host rename  ", db_path=db
        )

        assert result == {
            "task_id": "TASK-1",
            "prior_status": "APPROVED",
            "retired_by": "mapfinish-guru",
            "reason": "deliverable lost in host rename",
        }
        assert row(db, "TASK-1") == ("RETIRED", None, None)


def test_successful_retirement_from_other_nonterminal_statuses() -> None:
    """TASK-241-248's shape under TASK-254: retiring superseded-but-not-yet-
    reviewed work must also work from READY/IN_PROGRESS/SUBMITTED/
    CHANGES_REQUESTED, not only APPROVED."""
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        make_db(db)
        for status in ("READY", "IN_PROGRESS", "SUBMITTED", "CHANGES_REQUESTED", "BLOCKED", "CONFLICT"):
            task_id = f"TASK-{status}"
            insert_task(db, task_id, status=status)
            result = retire_task(task_id, "actor", "superseded", db_path=db)
            assert result is not None, status
            assert result["prior_status"] == status
            assert row(db, task_id)[0] == "RETIRED", status


def test_refuses_terminal_statuses() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        make_db(db)
        for status in ("RELEASED", "RETIRED", "DONE"):
            task_id = f"TASK-{status}"
            insert_task(db, task_id, status=status)
            before = row(db, task_id)
            assert retire_task(task_id, "actor", "reason", db_path=db) is None, status
            assert row(db, task_id) == before, status


def test_requires_a_reason() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        make_db(db)
        insert_task(db, "TASK-2", status="APPROVED")
        for bad in ("", "   "):
            try:
                retire_task("TASK-2", "actor", bad, db_path=db)
            except ValueError:
                pass
            else:
                raise AssertionError(f"empty reason {bad!r} must raise")
        assert row(db, "TASK-2")[0] == "APPROVED"


def test_requires_an_actor() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        make_db(db)
        insert_task(db, "TASK-3", status="APPROVED")
        for bad in ("", "   ", None):
            try:
                retire_task("TASK-3", bad, "reason", db_path=db)
            except (ValueError, AttributeError, TypeError):
                pass
            else:
                raise AssertionError(f"actor {bad!r} must raise")
        assert row(db, "TASK-3")[0] == "APPROVED"


def test_unknown_task_returns_none() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        make_db(db)
        assert retire_task("TASK-NOPE", "actor", "reason", db_path=db) is None


def test_cli_records_auditable_event_and_syncs_mirrors() -> None:
    script = ROOT / "MAP_System" / "scripts" / "map_task.py"
    schema = ROOT / "MAP_System" / "migration" / "schema.sql"
    with tempfile.TemporaryDirectory() as tmp:
        tmpd = Path(tmp)
        db = tmpd / "map.db"
        with sqlite3.connect(db) as conn:
            conn.executescript(schema.read_text())
            conn.execute(
                "INSERT INTO agents (agent_id, label, agent_type, status)"
                " VALUES ('owner','Owner','core','available')"
            )
            conn.execute(
                """
                INSERT INTO tasks
                    (task_id, project_id, title, description, task_type, role,
                     status, owner)
                VALUES
                    ('TASK-900','P','retire probe','probe','implementation',
                     'implementer','APPROVED','owner')
                """
            )

        output_dir = tmpd / "export"
        event_log = tmpd / "events.jsonl"
        proc = subprocess.run(
            [
                sys.executable,
                str(script),
                "--db",
                str(db),
                "--output-dir",
                str(output_dir),
                "--event-log",
                str(event_log),
                "retire",
                "TASK-900",
                "--actor",
                "  review-actor  ",
                "--reason",
                "  target project no longer exists  ",
            ],
            capture_output=True,
            text=True,
        )
        assert proc.returncode == 0, proc.stderr
        result = json.loads(proc.stdout.strip().splitlines()[-1])
        assert result["prior_status"] == "APPROVED"
        assert result["status"] == "RETIRED"
        assert result["retired_by"] == "review-actor"

        with sqlite3.connect(db) as conn:
            task = conn.execute(
                "SELECT status, claimed_by FROM tasks WHERE task_id='TASK-900'"
            ).fetchone()
            event = conn.execute(
                "SELECT event_type, sender_id, summary FROM events"
            ).fetchone()
        assert task == ("RETIRED", None)
        assert event[0:2] == ("PROGRESS", "review-actor")
        for fragment in ("retired by review-actor", "APPROVED", "target project no longer exists"):
            assert fragment in event[2]

        jsonl = [json.loads(line) for line in event_log.read_text().splitlines()]
        assert jsonl[0]["sender"] == "review-actor"
        assert "retired" in jsonl[0]["summary"]

        mirror = json.loads((output_dir / "tasks" / "TASK-900.json").read_text())
        assert mirror["status"] == "RETIRED"


def test_cli_refuses_terminal_status_with_nonzero_exit() -> None:
    script = ROOT / "MAP_System" / "scripts" / "map_task.py"
    schema = ROOT / "MAP_System" / "migration" / "schema.sql"
    with tempfile.TemporaryDirectory() as tmp:
        tmpd = Path(tmp)
        db = tmpd / "map.db"
        with sqlite3.connect(db) as conn:
            conn.executescript(schema.read_text())
            conn.execute(
                "INSERT INTO agents (agent_id, label, agent_type, status)"
                " VALUES ('owner','Owner','core','available')"
            )
            conn.execute(
                """
                INSERT INTO tasks
                    (task_id, project_id, title, description, task_type, role,
                     status, owner)
                VALUES
                    ('TASK-901','P','probe','probe','implementation',
                     'implementer','RELEASED','owner')
                """
            )

        proc = subprocess.run(
            [
                sys.executable, str(script), "--db", str(db),
                "--output-dir", str(tmpd / "export"), "--event-log", str(tmpd / "events.jsonl"),
                "retire", "TASK-901", "--actor", "actor", "--reason", "reason",
            ],
            capture_output=True,
            text=True,
        )
        assert proc.returncode != 0
        assert "RELEASED" in proc.stderr

        with sqlite3.connect(db) as conn:
            task = conn.execute("SELECT status FROM tasks WHERE task_id='TASK-901'").fetchone()
        assert task == ("RELEASED",)


def main() -> int:
    tests = [
        test_successful_retirement_from_approved,
        test_successful_retirement_from_other_nonterminal_statuses,
        test_refuses_terminal_statuses,
        test_requires_a_reason,
        test_requires_an_actor,
        test_unknown_task_returns_none,
        test_cli_records_auditable_event_and_syncs_mirrors,
        test_cli_refuses_terminal_status_with_nonzero_exit,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"{len(tests)}/{len(tests)} retire tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
