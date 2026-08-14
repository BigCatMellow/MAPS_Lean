#!/usr/bin/env python3
"""Focused tests for the sanctioned criterion-amendment verb (TASK-297).

Amending an acceptance criterion is the single most abusable lifecycle
mutation in MAP: it is exactly how an agent would retroactively lower a bar
it failed to clear, leaving a task looking cleanly APPROVED against criteria
that were rewritten to fit the delivery. These tests pin the verb's happy
path and every refusal: it must be harder to misuse than the raw-SQL/
hand-edit route it replaces, not merely more convenient.
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

from MAP_System.db.claims import amend_task_criterion  # noqa: E402


def make_root(tmp: Path, *, decisions: list[str] | None = None, repairs: list[str] | None = None) -> Path:
    """Build an isolated MAP_System-shaped root with a fake decisions.md/repairs/."""
    map_root = tmp / "MAP_System"
    (map_root / "shared").mkdir(parents=True)
    (map_root / "repairs").mkdir(parents=True)
    lines = ["# Decisions\n"]
    for dec in decisions or []:
        lines.append(f"## {dec}: A test decision\n\nStatus: approved\n")
    (map_root / "shared" / "decisions.md").write_text("\n".join(lines), encoding="utf-8")
    for repair in repairs or []:
        (map_root / "repairs" / f"{repair}-a-test-repair.md").write_text("# test repair\n", encoding="utf-8")
    return map_root


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


def insert_task(path: Path, task_id: str, status: str = "READY") -> None:
    with sqlite3.connect(path) as conn:
        conn.execute(
            "INSERT INTO tasks (task_id, status, owner) VALUES (?, ?, 'owner')",
            (task_id, status),
        )


def insert_criteria(path: Path, task_id: str, criteria: list[str]) -> None:
    with sqlite3.connect(path) as conn:
        for criterion in criteria:
            conn.execute(
                "INSERT INTO task_acceptance_criteria (task_id, criterion) VALUES (?, ?)",
                (task_id, criterion),
            )


def criteria_rows(path: Path, task_id: str) -> list[str]:
    with sqlite3.connect(path) as conn:
        return [
            row[0]
            for row in conn.execute(
                "SELECT criterion FROM task_acceptance_criteria WHERE task_id=? ORDER BY id",
                (task_id,),
            )
        ]


def test_successful_amendment() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmpd = Path(tmp)
        db = tmpd / "map.db"
        make_db(db)
        insert_task(db, "TASK-1", status="READY")
        insert_criteria(db, "TASK-1", ["criterion one", "criterion two", "criterion three"])
        map_root = make_root(tmpd, decisions=["DEC-034"])

        result = amend_task_criterion(
            "TASK-1", 2, "  criterion two, corrected  ", "  actor  ", "  fixed a typo  ", "  DEC-034  ",
            db_path=db, map_root=map_root,
        )

        assert result == {
            "task_id": "TASK-1",
            "criterion_index": 2,
            "old_text": "criterion two",
            "new_text": "criterion two, corrected",
            "amended_by": "actor",
            "reason": "fixed a typo",
            "authority": "DEC-034",
        }
        assert criteria_rows(db, "TASK-1") == ["criterion one", "criterion two, corrected", "criterion three"]


def test_successful_amendment_citing_repair() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmpd = Path(tmp)
        db = tmpd / "map.db"
        make_db(db)
        insert_task(db, "TASK-1", status="IN_PROGRESS")
        insert_criteria(db, "TASK-1", ["only criterion"])
        map_root = make_root(tmpd, repairs=["REPAIR-0009"])

        result = amend_task_criterion(
            "TASK-1", 1, "corrected criterion", "actor", "reason", "REPAIR-0009",
            db_path=db, map_root=map_root,
        )
        assert result is not None
        assert result["authority"] == "REPAIR-0009"
        assert criteria_rows(db, "TASK-1") == ["corrected criterion"]


def test_refuses_terminal_statuses() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmpd = Path(tmp)
        db = tmpd / "map.db"
        make_db(db)
        map_root = make_root(tmpd, decisions=["DEC-001"])
        for status in ("APPROVED", "RELEASED", "RETIRED", "DONE"):
            task_id = f"TASK-{status}"
            insert_task(db, task_id, status=status)
            insert_criteria(db, task_id, ["a criterion"])
            result = amend_task_criterion(
                task_id, 1, "new text", "actor", "reason", "DEC-001", db_path=db, map_root=map_root,
            )
            assert result is None, status
            assert criteria_rows(db, task_id) == ["a criterion"], status


def test_refuses_nonexistent_authority() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmpd = Path(tmp)
        db = tmpd / "map.db"
        make_db(db)
        insert_task(db, "TASK-1", status="READY")
        insert_criteria(db, "TASK-1", ["a criterion"])
        map_root = make_root(tmpd, decisions=["DEC-001"], repairs=["REPAIR-0001"])

        for bad_authority in ("DEC-999", "REPAIR-9999", "TASK-1", "because I said so", "", "   "):
            try:
                amend_task_criterion(
                    "TASK-1", 1, "new text", "actor", "reason", bad_authority,
                    db_path=db, map_root=map_root,
                )
            except ValueError:
                pass
            else:
                raise AssertionError(f"authority {bad_authority!r} must raise")
        assert criteria_rows(db, "TASK-1") == ["a criterion"]


def test_refuses_out_of_range_criterion_id() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmpd = Path(tmp)
        db = tmpd / "map.db"
        make_db(db)
        insert_task(db, "TASK-1", status="READY")
        insert_criteria(db, "TASK-1", ["only one"])
        map_root = make_root(tmpd, decisions=["DEC-001"])

        for bad_index in (0, -1, 2, 99):
            result = amend_task_criterion(
                "TASK-1", bad_index, "new text", "actor", "reason", "DEC-001",
                db_path=db, map_root=map_root,
            )
            assert result is None, bad_index
        assert criteria_rows(db, "TASK-1") == ["only one"]


def test_requires_a_reason() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmpd = Path(tmp)
        db = tmpd / "map.db"
        make_db(db)
        insert_task(db, "TASK-1", status="READY")
        insert_criteria(db, "TASK-1", ["only one"])
        map_root = make_root(tmpd, decisions=["DEC-001"])
        for bad in ("", "   "):
            try:
                amend_task_criterion(
                    "TASK-1", 1, "new text", "actor", bad, "DEC-001", db_path=db, map_root=map_root,
                )
            except ValueError:
                pass
            else:
                raise AssertionError(f"empty reason {bad!r} must raise")
        assert criteria_rows(db, "TASK-1") == ["only one"]


def test_requires_new_text() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmpd = Path(tmp)
        db = tmpd / "map.db"
        make_db(db)
        insert_task(db, "TASK-1", status="READY")
        insert_criteria(db, "TASK-1", ["only one"])
        map_root = make_root(tmpd, decisions=["DEC-001"])
        for bad in ("", "   "):
            try:
                amend_task_criterion(
                    "TASK-1", 1, bad, "actor", "reason", "DEC-001", db_path=db, map_root=map_root,
                )
            except ValueError:
                pass
            else:
                raise AssertionError(f"empty new_text {bad!r} must raise")
        assert criteria_rows(db, "TASK-1") == ["only one"]


def test_unknown_task_returns_none() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmpd = Path(tmp)
        db = tmpd / "map.db"
        make_db(db)
        map_root = make_root(tmpd, decisions=["DEC-001"])
        assert amend_task_criterion(
            "TASK-NOPE", 1, "new text", "actor", "reason", "DEC-001", db_path=db, map_root=map_root,
        ) is None


def test_old_text_survives_in_full_in_the_event() -> None:
    """The durable event must preserve the complete prior criterion text so a
    reader can always reconstruct what the task originally promised."""
    script = ROOT / "MAP_System" / "scripts" / "map_task.py"
    schema = ROOT / "MAP_System" / "migration" / "schema.sql"
    long_old_text = (
        "The system MUST verify every single one of the seventeen distinct "
        "conditions before proceeding, in the exact order specified in the "
        "design document, with no exceptions permitted under any circumstances."
    )
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
                    ('TASK-900','P','amend probe','probe','implementation',
                     'implementer','READY','owner')
                """
            )
            conn.execute(
                "INSERT INTO task_acceptance_criteria (task_id, criterion) VALUES (?, ?)",
                ("TASK-900", long_old_text),
            )

        output_dir = tmpd / "export"
        event_log = tmpd / "events.jsonl"
        proc = subprocess.run(
            [
                sys.executable, str(script), "--db", str(db),
                "--output-dir", str(output_dir), "--event-log", str(event_log),
                "amend-criteria", "TASK-900",
                "--criterion-id", "1",
                "--new-text", "The system verifies the conditions.",
                "--actor", "  review-actor  ",
                "--reason", "  original text was unreadable and factually wrong  ",
                "--authority", "REPAIR-0009",
            ],
            capture_output=True,
            text=True,
        )
        assert proc.returncode == 0, proc.stderr
        result = json.loads(proc.stdout.strip().splitlines()[-1])
        assert result["old_text"] == long_old_text
        assert result["new_text"] == "The system verifies the conditions."
        assert result["authority"] == "REPAIR-0009"

        with sqlite3.connect(db) as conn:
            criterion = conn.execute(
                "SELECT criterion FROM task_acceptance_criteria WHERE task_id='TASK-900'"
            ).fetchone()[0]
            event = conn.execute(
                "SELECT event_type, sender_id, summary FROM events"
            ).fetchone()
        assert criterion == "The system verifies the conditions."
        assert event[0:2] == ("PROGRESS", "review-actor")
        assert long_old_text in event[2]
        assert "The system verifies the conditions." in event[2]
        assert "REPAIR-0009" in event[2]

        jsonl = [json.loads(line) for line in event_log.read_text().splitlines()]
        assert long_old_text in jsonl[0]["summary"]

        mirror = json.loads((output_dir / "tasks" / "TASK-900.json").read_text())
        assert mirror["acceptance_criteria"] == ["The system verifies the conditions."]


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
            conn.execute(
                "INSERT INTO task_acceptance_criteria (task_id, criterion) VALUES ('TASK-901', 'a criterion')"
            )

        proc = subprocess.run(
            [
                sys.executable, str(script), "--db", str(db),
                "--output-dir", str(tmpd / "export"), "--event-log", str(tmpd / "events.jsonl"),
                "amend-criteria", "TASK-901",
                "--criterion-id", "1", "--new-text", "new text",
                "--actor", "actor", "--reason", "reason", "--authority", "REPAIR-0009",
            ],
            capture_output=True,
            text=True,
        )
        assert proc.returncode != 0
        assert "RELEASED" in proc.stderr

        with sqlite3.connect(db) as conn:
            criterion = conn.execute(
                "SELECT criterion FROM task_acceptance_criteria WHERE task_id='TASK-901'"
            ).fetchone()[0]
        assert criterion == "a criterion"


def test_cli_refuses_nonexistent_authority_with_nonzero_exit() -> None:
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
                    ('TASK-902','P','probe','probe','implementation',
                     'implementer','READY','owner')
                """
            )
            conn.execute(
                "INSERT INTO task_acceptance_criteria (task_id, criterion) VALUES ('TASK-902', 'a criterion')"
            )

        proc = subprocess.run(
            [
                sys.executable, str(script), "--db", str(db),
                "--output-dir", str(tmpd / "export"), "--event-log", str(tmpd / "events.jsonl"),
                "amend-criteria", "TASK-902",
                "--criterion-id", "1", "--new-text", "new text",
                "--actor", "actor", "--reason", "reason", "--authority", "DEC-99999-DOES-NOT-EXIST",
            ],
            capture_output=True,
            text=True,
        )
        assert proc.returncode != 0
        assert "does not exist" in proc.stderr

        with sqlite3.connect(db) as conn:
            criterion = conn.execute(
                "SELECT criterion FROM task_acceptance_criteria WHERE task_id='TASK-902'"
            ).fetchone()[0]
        assert criterion == "a criterion"


def main() -> int:
    tests = [
        test_successful_amendment,
        test_successful_amendment_citing_repair,
        test_refuses_terminal_statuses,
        test_refuses_nonexistent_authority,
        test_refuses_out_of_range_criterion_id,
        test_requires_a_reason,
        test_requires_new_text,
        test_unknown_task_returns_none,
        test_old_text_survives_in_full_in_the_event,
        test_cli_refuses_terminal_status_with_nonzero_exit,
        test_cli_refuses_nonexistent_authority_with_nonzero_exit,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"{len(tests)}/{len(tests)} amend-criteria tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
