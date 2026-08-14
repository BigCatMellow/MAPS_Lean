#!/usr/bin/env python3
"""Focused tests for sanctioned task-owner reassignment (TASK-273)."""

from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from MAP_System.db.claims import reassign_task_owner  # noqa: E402


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
            attempt INTEGER NOT NULL DEFAULT 0,
            updated_at TEXT
        );
        INSERT INTO agents (agent_id, label, agent_type, status)
        VALUES ('old-owner', 'Old Owner', 'core', 'inactive');
        """
    )
    conn.commit()
    conn.close()


def insert_task(path: Path, task_id: str, status: str = "APPROVED") -> None:
    with sqlite3.connect(path) as conn:
        conn.execute(
            """
            INSERT INTO tasks
                (task_id, status, owner, claimed_by, lease_expires_at,
                 heartbeat_at, attempt, updated_at)
            VALUES (?, ?, 'old-owner', 'working-agent', '2099-01-01T00:00:00Z',
                    '2026-07-23T00:00:00Z', 2, '2026-07-23T00:00:00Z')
            """,
            (task_id, status),
        )


def row(path: Path, task_id: str):
    with sqlite3.connect(path) as conn:
        return conn.execute(
            """
            SELECT status, owner, claimed_by, lease_expires_at, heartbeat_at,
                   attempt, updated_at
            FROM tasks WHERE task_id=?
            """,
            (task_id,),
        ).fetchone()


def test_happy_path_registers_owner_and_changes_only_owner() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        make_db(db)
        insert_task(db, "TASK-1")
        before = row(db, "TASK-1")

        result = reassign_task_owner(
            "TASK-1",
            "  codex-lab-mubo  ",
            "  live-owner  ",
            "  prior session ended  ",
            db_path=db,
        )

        assert result == {
            "task_id": "TASK-1",
            "prior_owner": "old-owner",
            "new_owner": "live-owner",
            "reassigned_by": "codex-lab-mubo",
            "reason": "prior session ended",
        }
        after = row(db, "TASK-1")
        assert after[1] == "live-owner"
        assert after[:1] + after[2:] == before[:1] + before[2:]
        with sqlite3.connect(db) as conn:
            registered = conn.execute(
                "SELECT agent_type, status FROM agents WHERE agent_id='live-owner'"
            ).fetchone()
        assert registered == ("core", "available")


def test_refuses_terminal_tasks_without_mutation() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        make_db(db)
        for status in ("DONE", "RELEASED", "RETIRED"):
            task_id = f"TASK-{status}"
            insert_task(db, task_id, status)
            before = row(db, task_id)
            assert reassign_task_owner(
                task_id, "actor", "new-owner", "reason", db_path=db
            ) is None
            assert row(db, task_id) == before


def test_requires_actor_new_owner_and_reason() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        make_db(db)
        insert_task(db, "TASK-2", "READY")
        cases = [
            ("", "new-owner", "reason"),
            ("actor", "", "reason"),
            ("actor", "   ", "reason"),
            ("actor", None, "reason"),
            ("actor", "new-owner", ""),
            ("actor", "new-owner", "   "),
        ]
        before = row(db, "TASK-2")
        for actor, owner, reason in cases:
            try:
                reassign_task_owner(
                    "TASK-2", actor, owner, reason, db_path=db
                )
            except ValueError:
                pass
            else:
                raise AssertionError((actor, owner, reason))
            assert row(db, "TASK-2") == before


def test_unknown_task_returns_none_without_registering_owner() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        make_db(db)
        assert reassign_task_owner(
            "TASK-NOPE", "actor", "unused-owner", "reason", db_path=db
        ) is None
        with sqlite3.connect(db) as conn:
            assert conn.execute(
                "SELECT 1 FROM agents WHERE agent_id='unused-owner'"
            ).fetchone() is None


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
                " VALUES ('old-owner','Old Owner','core','inactive')"
            )
            conn.execute(
                """
                INSERT INTO tasks
                    (task_id, project_id, title, description, task_type, role,
                     status, owner, claimed_by, lease_expires_at, heartbeat_at,
                     attempt)
                VALUES
                    ('TASK-900','P','reassign probe','probe','implementation',
                     'implementer','IN_PROGRESS','old-owner',NULL,NULL,NULL,2)
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
                "reassign-owner",
                "TASK-900",
                "--actor",
                "  review-actor  ",
                "--new-owner",
                "  replacement-owner  ",
                "--reason",
                "  old session ended  ",
            ],
            capture_output=True,
            text=True,
        )
        assert proc.returncode == 0, proc.stderr
        result = json.loads(proc.stdout.strip().splitlines()[-1])
        assert result["prior_owner"] == "old-owner"
        assert result["new_owner"] == "replacement-owner"
        assert result["reassigned_by"] == "review-actor"

        with sqlite3.connect(db) as conn:
            task = conn.execute(
                "SELECT status, owner, claimed_by, attempt FROM tasks WHERE task_id='TASK-900'"
            ).fetchone()
            agent_ids = {
                value for (value,) in conn.execute("SELECT agent_id FROM agents")
            }
            event = conn.execute(
                "SELECT event_type, sender_id, summary FROM events"
            ).fetchone()
        assert task == ("IN_PROGRESS", "replacement-owner", None, 2)
        assert {"review-actor", "replacement-owner"} <= agent_ids
        assert event[0:2] == ("PROGRESS", "review-actor")
        for fragment in (
            "old-owner",
            "replacement-owner",
            "review-actor",
            "old session ended",
        ):
            assert fragment in event[2]

        jsonl = [json.loads(line) for line in event_log.read_text().splitlines()]
        assert jsonl[0]["sender"] == "review-actor"
        assert "old-owner -> replacement-owner" in jsonl[0]["summary"]
        mirror = json.loads((output_dir / "tasks" / "TASK-900.json").read_text())
        assert mirror["owner"] == "replacement-owner"


def main() -> int:
    tests = [
        test_happy_path_registers_owner_and_changes_only_owner,
        test_refuses_terminal_tasks_without_mutation,
        test_requires_actor_new_owner_and_reason,
        test_unknown_task_returns_none_without_registering_owner,
        test_cli_records_auditable_event_and_syncs_mirrors,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"{len(tests)}/{len(tests)} owner-reassignment tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
