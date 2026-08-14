#!/usr/bin/env python3
"""Focused tests for the sanctioned NEEDS_SHAPING -> READY promotion verb (TASK-317).

Before this verb, a task shaped incrementally (output_paths and
acceptance_criteria filled in, description left blank -- as happened to
TASK-316) had no route back to READY: `create_task` only reaches READY when
all three are supplied together at creation, and no other verb touches an
existing task's description. These tests pin the happy path (promotion only
when the READY gate now actually passes) and every refusal.
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

from MAP_System.db.claims import describe_task  # noqa: E402


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
            description TEXT NOT NULL DEFAULT '',
            owner TEXT REFERENCES agents(agent_id),
            claimed_by TEXT,
            lease_expires_at TEXT,
            heartbeat_at TEXT,
            updated_at TEXT
        );
        CREATE TABLE task_output_paths (
            task_id TEXT NOT NULL REFERENCES tasks(task_id),
            path TEXT NOT NULL,
            PRIMARY KEY (task_id, path)
        );
        CREATE TABLE task_acceptance_criteria (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id    TEXT NOT NULL REFERENCES tasks(task_id),
            criterion  TEXT NOT NULL,
            met        INTEGER NOT NULL DEFAULT 0,
            UNIQUE (task_id, criterion)
        );
        INSERT INTO agents (agent_id, label, agent_type, status)
        VALUES ('owner', 'Owner', 'core', 'available');
        """
    )
    conn.commit()
    conn.close()


def insert_task(path: Path, task_id: str, status: str = "NEEDS_SHAPING") -> None:
    with sqlite3.connect(path) as conn:
        conn.execute(
            "INSERT INTO tasks (task_id, status, owner) VALUES (?, ?, 'owner')",
            (task_id, status),
        )


def insert_output_path(path: Path, task_id: str, output_path: str) -> None:
    with sqlite3.connect(path) as conn:
        conn.execute(
            "INSERT INTO task_output_paths (task_id, path) VALUES (?, ?)",
            (task_id, output_path),
        )


def insert_criterion(path: Path, task_id: str, criterion: str) -> None:
    with sqlite3.connect(path) as conn:
        conn.execute(
            "INSERT INTO task_acceptance_criteria (task_id, criterion) VALUES (?, ?)",
            (task_id, criterion),
        )


def task_row(path: Path, task_id: str) -> sqlite3.Row:
    with sqlite3.connect(path) as conn:
        conn.row_factory = sqlite3.Row
        return conn.execute(
            "SELECT * FROM tasks WHERE task_id=?", (task_id,)
        ).fetchone()


def test_promotes_a_fully_shaped_task() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        make_db(db)
        insert_task(db, "TASK-1")
        insert_output_path(db, "TASK-1", "src/thing.py")
        insert_criterion(db, "TASK-1", "thing works")

        result = describe_task(
            "TASK-1", "  actor  ", "  fixes the thing  ", "  filling gap  ",
            db_path=db,
        )

        assert result == {
            "task_id": "TASK-1",
            "description": "fixes the thing",
            "promoted_to_ready": True,
            "described_by": "actor",
            "reason": "filling gap",
        }
        row = task_row(db, "TASK-1")
        assert row["status"] == "READY"
        assert row["description"] == "fixes the thing"


def test_does_not_promote_when_output_paths_still_missing() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        make_db(db)
        insert_task(db, "TASK-2")
        insert_criterion(db, "TASK-2", "thing works")

        result = describe_task("TASK-2", "actor", "a description", "reason", db_path=db)

        assert result["promoted_to_ready"] is False
        row = task_row(db, "TASK-2")
        assert row["status"] == "NEEDS_SHAPING"
        assert row["description"] == "a description"


def test_does_not_promote_when_criteria_still_missing() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        make_db(db)
        insert_task(db, "TASK-3")
        insert_output_path(db, "TASK-3", "src/thing.py")

        result = describe_task("TASK-3", "actor", "a description", "reason", db_path=db)

        assert result["promoted_to_ready"] is False
        row = task_row(db, "TASK-3")
        assert row["status"] == "NEEDS_SHAPING"


def test_refuses_non_needs_shaping_status() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        make_db(db)
        for status in ("READY", "IN_PROGRESS", "CHANGES_REQUESTED", "RELEASED"):
            task_id = f"TASK-{status}"
            insert_task(db, task_id, status=status)
            insert_output_path(db, task_id, "src/thing.py")
            insert_criterion(db, task_id, "thing works")

            result = describe_task(task_id, "actor", "a description", "reason", db_path=db)

            assert result is None, status
            row = task_row(db, task_id)
            assert row["status"] == status
            assert row["description"] == ""


def test_unknown_task_returns_none() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        make_db(db)
        assert describe_task("TASK-MISSING", "actor", "a description", "reason", db_path=db) is None


def test_requires_a_description() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        make_db(db)
        insert_task(db, "TASK-4")
        try:
            describe_task("TASK-4", "actor", "   ", "reason", db_path=db)
        except ValueError as exc:
            assert "description" in str(exc)
        else:
            raise AssertionError("expected ValueError for blank description")


def test_requires_a_reason() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        make_db(db)
        insert_task(db, "TASK-5")
        try:
            describe_task("TASK-5", "actor", "a description", "  ", db_path=db)
        except ValueError as exc:
            assert "reason" in str(exc)
        else:
            raise AssertionError("expected ValueError for blank reason")


def test_requires_an_actor() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        make_db(db)
        insert_task(db, "TASK-6")
        try:
            describe_task("TASK-6", "  ", "a description", "reason", db_path=db)
        except ValueError as exc:
            assert "actor_id" in str(exc)
        else:
            raise AssertionError("expected ValueError for blank actor_id")


def test_cli_promotes_and_syncs_mirrors() -> None:
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
                    ('TASK-901','P','describe probe','','implementation',
                     'implementer','NEEDS_SHAPING','owner')
                """
            )
            conn.execute(
                "INSERT INTO task_output_paths (task_id, path) VALUES (?, ?)",
                ("TASK-901", "src/thing.py"),
            )
            conn.execute(
                "INSERT INTO task_acceptance_criteria (task_id, criterion) VALUES (?, ?)",
                ("TASK-901", "thing works"),
            )

        output_dir = tmpd / "export"
        event_log = tmpd / "events.jsonl"
        proc = subprocess.run(
            [
                sys.executable, str(script), "--db", str(db),
                "--output-dir", str(output_dir), "--event-log", str(event_log),
                "describe", "TASK-901",
                "--description", "now describes the probe",
                "--actor", "cli-actor", "--reason", "unblocking claim",
            ],
            capture_output=True,
            text=True,
        )
        assert proc.returncode == 0, proc.stderr
        payload = json.loads(proc.stdout.strip().splitlines()[-1])
        assert payload["status"] == "READY"
        assert payload["promoted_to_ready"] is True

        row = task_row(db, "TASK-901")
        assert row["status"] == "READY"
        assert row["description"] == "now describes the probe"

        event_lines = event_log.read_text().strip().splitlines()
        assert any("described by cli-actor" in line and "Promoted to READY" in line for line in event_lines)

        exported = json.loads((output_dir / "tasks" / "TASK-901.json").read_text())
        assert exported["status"] == "READY"
        assert exported["description"] == "now describes the probe"


def test_cli_refuses_ready_task_with_nonzero_exit() -> None:
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
                    ('TASK-902','P','describe probe','already shaped','implementation',
                     'implementer','READY','owner')
                """
            )

        proc = subprocess.run(
            [
                sys.executable, str(script), "--db", str(db),
                "describe", "TASK-902",
                "--description", "trying to re-describe",
                "--actor", "actor", "--reason", "reason",
            ],
            capture_output=True,
            text=True,
        )
        assert proc.returncode != 0
        assert "NEEDS_SHAPING" in proc.stderr

        row = task_row(db, "TASK-902")
        assert row["description"] == "already shaped"


def main() -> int:
    tests = [
        test_promotes_a_fully_shaped_task,
        test_does_not_promote_when_output_paths_still_missing,
        test_does_not_promote_when_criteria_still_missing,
        test_refuses_non_needs_shaping_status,
        test_unknown_task_returns_none,
        test_requires_a_description,
        test_requires_a_reason,
        test_requires_an_actor,
        test_cli_promotes_and_syncs_mirrors,
        test_cli_refuses_ready_task_with_nonzero_exit,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"{len(tests)}/{len(tests)} describe tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
