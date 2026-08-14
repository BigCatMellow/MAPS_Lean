#!/usr/bin/env python3
"""Focused tests for the sanctioned attempt-budget extension verb (TASK-293).

REPAIR-0010 (TASK-280) and REPAIR-0012 (TASK-263) both raised max_attempts via
raw SQL because no sanctioned map_task.py verb existed, and REPAIR-0010
explicitly predicted a second occurrence should trigger building one. These
tests pin the verb's happy path and, just as importantly, its refusals -- a
verb that can freely erase a task's attempt/review history would be worse
than the raw-SQL gap it replaces.
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

from MAP_System.db.claims import extend_task_attempts  # noqa: E402


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
            attempt INTEGER NOT NULL DEFAULT 0,
            max_attempts INTEGER NOT NULL DEFAULT 3,
            updated_at TEXT
        );
        INSERT INTO agents (agent_id, label, agent_type, status)
        VALUES ('owner', 'Owner', 'core', 'available');
        """
    )
    conn.commit()
    conn.close()


def insert_task(
    path: Path, task_id: str, status: str = "CHANGES_REQUESTED",
    attempt: int = 3, max_attempts: int = 3,
) -> None:
    with sqlite3.connect(path) as conn:
        conn.execute(
            """
            INSERT INTO tasks (task_id, status, owner, attempt, max_attempts)
            VALUES (?, ?, 'owner', ?, ?)
            """,
            (task_id, status, attempt, max_attempts),
        )


def row(path: Path, task_id: str):
    with sqlite3.connect(path) as conn:
        return conn.execute(
            "SELECT status, attempt, max_attempts FROM tasks WHERE task_id=?",
            (task_id,),
        ).fetchone()


def test_successful_extension() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        make_db(db)
        insert_task(db, "TASK-1", status="CHANGES_REQUESTED", attempt=3, max_attempts=3)

        result = extend_task_attempts(
            "TASK-1", "  claude-lab-niko  ", 4, "  one more small fix  ", db_path=db
        )

        assert result == {
            "task_id": "TASK-1",
            "prior_max_attempts": 3,
            "new_max_attempts": 4,
            "attempt": 3,
            "extended_by": "claude-lab-niko",
            "reason": "one more small fix",
        }
        assert row(db, "TASK-1") == ("CHANGES_REQUESTED", 3, 4)


def test_refuses_terminal_statuses() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        make_db(db)
        for status in ("APPROVED", "RELEASED", "RETIRED", "DONE"):
            task_id = f"TASK-{status}"
            insert_task(db, task_id, status=status, attempt=3, max_attempts=3)
            before = row(db, task_id)
            assert extend_task_attempts(
                task_id, "actor", 4, "reason", db_path=db
            ) is None, status
            assert row(db, task_id) == before, status


def test_refuses_lowering_below_current_attempt() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        make_db(db)
        insert_task(db, "TASK-2", status="CHANGES_REQUESTED", attempt=3, max_attempts=5)
        before = row(db, "TASK-2")

        assert extend_task_attempts("TASK-2", "actor", 2, "reason", db_path=db) is None
        assert row(db, "TASK-2") == before

        # Exactly at the current attempt count is not a *lowering* and must
        # be allowed, even though it grants no further claim on its own.
        result = extend_task_attempts("TASK-2", "actor", 3, "reason", db_path=db)
        assert result is not None
        assert row(db, "TASK-2") == ("CHANGES_REQUESTED", 3, 3)


def test_requires_a_reason() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        make_db(db)
        insert_task(db, "TASK-3", status="CHANGES_REQUESTED", attempt=3, max_attempts=3)
        for bad in ("", "   "):
            try:
                extend_task_attempts("TASK-3", "actor", 4, bad, db_path=db)
            except ValueError:
                pass
            else:
                raise AssertionError(f"empty reason {bad!r} must raise")
        assert row(db, "TASK-3") == ("CHANGES_REQUESTED", 3, 3)


def test_requires_an_actor() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        make_db(db)
        insert_task(db, "TASK-4", status="CHANGES_REQUESTED", attempt=3, max_attempts=3)
        for bad in ("", "   ", None):
            try:
                extend_task_attempts("TASK-4", bad, 4, "reason", db_path=db)
            except (ValueError, AttributeError, TypeError):
                pass
            else:
                raise AssertionError(f"actor {bad!r} must raise")
        assert row(db, "TASK-4") == ("CHANGES_REQUESTED", 3, 3)


def test_requires_a_positive_target() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        make_db(db)
        insert_task(db, "TASK-5", status="READY", attempt=0, max_attempts=3)
        for bad in (0, -1, None):
            try:
                extend_task_attempts("TASK-5", "actor", bad, "reason", db_path=db)
            except (ValueError, TypeError):
                pass
            else:
                raise AssertionError(f"target {bad!r} must raise")
        assert row(db, "TASK-5") == ("READY", 0, 3)


def test_unknown_task_returns_none() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        make_db(db)
        assert extend_task_attempts("TASK-NOPE", "actor", 4, "reason", db_path=db) is None


def test_cli_records_auditable_event_syncs_mirrors_and_supports_add() -> None:
    """CLI end-to-end: --add mode, event/mirror sync, like reassign-owner's CLI test."""
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
                     status, owner, attempt, max_attempts)
                VALUES
                    ('TASK-900','P','extend-attempts probe','probe','implementation',
                     'implementer','CHANGES_REQUESTED','owner',3,3)
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
                "extend-attempts",
                "TASK-900",
                "--actor",
                "  review-actor  ",
                "--add",
                "1",
                "--reason",
                "  one small mechanical finding left  ",
            ],
            capture_output=True,
            text=True,
        )
        assert proc.returncode == 0, proc.stderr
        result = json.loads(proc.stdout.strip().splitlines()[-1])
        assert result["prior_max_attempts"] == 3
        assert result["new_max_attempts"] == 4
        assert result["extended_by"] == "review-actor"

        with sqlite3.connect(db) as conn:
            task = conn.execute(
                "SELECT status, attempt, max_attempts FROM tasks WHERE task_id='TASK-900'"
            ).fetchone()
            event = conn.execute(
                "SELECT event_type, sender_id, summary FROM events"
            ).fetchone()
        assert task == ("CHANGES_REQUESTED", 3, 4)
        assert event[0:2] == ("PROGRESS", "review-actor")
        for fragment in ("3 -> 4", "review-actor", "one small mechanical finding left"):
            assert fragment in event[2]

        jsonl = [json.loads(line) for line in event_log.read_text().splitlines()]
        assert jsonl[0]["sender"] == "review-actor"
        assert "3 -> 4" in jsonl[0]["summary"]

        # The task JSON mirror does not carry attempt/max_attempts (neither
        # does any existing task file -- only SQLite tracks the claim-gate
        # counters), so the mirror-sync check here is that the re-export ran
        # and left the mirror consistent with the field it does carry.
        mirror = json.loads((output_dir / "tasks" / "TASK-900.json").read_text())
        assert mirror["status"] == "CHANGES_REQUESTED"


def test_cli_refuses_both_or_neither_of_max_attempts_and_add() -> None:
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
                     status, owner, attempt, max_attempts)
                VALUES
                    ('TASK-901','P','probe','probe','implementation',
                     'implementer','READY','owner',0,3)
                """
            )

        base = [
            sys.executable, str(script), "--db", str(db),
            "--output-dir", str(tmpd / "export"), "--event-log", str(tmpd / "events.jsonl"),
            "extend-attempts", "TASK-901", "--actor", "actor", "--reason", "reason",
        ]
        neither = subprocess.run(base, capture_output=True, text=True)
        assert neither.returncode != 0

        both = subprocess.run(base + ["--max-attempts", "5", "--add", "1"], capture_output=True, text=True)
        assert both.returncode != 0


def main() -> int:
    tests = [
        test_successful_extension,
        test_refuses_terminal_statuses,
        test_refuses_lowering_below_current_attempt,
        test_requires_a_reason,
        test_requires_an_actor,
        test_requires_a_positive_target,
        test_unknown_task_returns_none,
        test_cli_records_auditable_event_syncs_mirrors_and_supports_add,
        test_cli_refuses_both_or_neither_of_max_attempts_and_add,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"{len(tests)}/{len(tests)} extend-attempts tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
