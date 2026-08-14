#!/usr/bin/env python3
"""Tests for orphaned-task recovery (TASK-266).

TASK-186 sat IN_PROGRESS for four days with claimed_by, lease_expires_at and
heartbeat_at all NULL. Nothing could move it: expire_leases filters on
`claimed_by IS NOT NULL`, release_task filters on `claimed_by = ?`, rework
requires CHANGES_REQUESTED, reject requires SUBMITTED, and AGENTS.md forbids
hand-editing SQLite. These tests pin the recovery path and, just as importantly,
its refusals -- a verb that can steal a live claim would be worse than the gap.
"""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from MAP_System.db.claims import (  # noqa: E402
    expire_leases,
    recover_orphan_task,
    release_task,
)


def make_db(path: Path) -> None:
    conn = sqlite3.connect(path)
    conn.executescript(
        """
        CREATE TABLE agents (agent_id TEXT PRIMARY KEY, label TEXT,
                             agent_type TEXT, status TEXT);
        CREATE TABLE tasks (
            task_id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL DEFAULT 'P',
            title TEXT NOT NULL DEFAULT 't',
            description TEXT NOT NULL DEFAULT '',
            task_type TEXT NOT NULL DEFAULT 'implementation',
            role TEXT NOT NULL DEFAULT 'implementer',
            status TEXT NOT NULL DEFAULT 'BACKLOG',
            owner TEXT,
            claimed_by TEXT,
            lease_expires_at TEXT,
            heartbeat_at TEXT,
            updated_at TEXT
        );
        """
    )
    conn.commit()
    conn.close()


def insert(db: Path, task_id: str, **cols) -> None:
    base = {"status": "IN_PROGRESS", "owner": "dead-agent", "claimed_by": None,
            "lease_expires_at": None, "heartbeat_at": None}
    base.update(cols)
    conn = sqlite3.connect(db)
    conn.execute(
        "INSERT INTO tasks (task_id, status, owner, claimed_by, lease_expires_at, heartbeat_at)"
        " VALUES (?,?,?,?,?,?)",
        (task_id, base["status"], base["owner"], base["claimed_by"],
         base["lease_expires_at"], base["heartbeat_at"]),
    )
    conn.commit()
    conn.close()


def status_of(db: Path, task_id: str) -> str:
    conn = sqlite3.connect(db)
    row = conn.execute("SELECT status FROM tasks WHERE task_id=?", (task_id,)).fetchone()
    conn.close()
    return row[0]


def test_recovers_the_task_186_shape() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        make_db(db)
        insert(db, "TASK-186")  # IN_PROGRESS, everything else NULL

        # First prove the existing paths genuinely cannot touch it.
        assert expire_leases(db_path=db) == [], "expire_leases must not see a lease-less orphan"
        assert release_task("TASK-186", "anyone", db_path=db) is False

        result = recover_orphan_task("TASK-186", "claude-lab-niko", "owner session is gone", db_path=db)
        assert result is not None
        assert result["prior_owner"] == "dead-agent"
        assert result["recovered_by"] == "claude-lab-niko"
        assert status_of(db, "TASK-186") == "READY"


def test_refuses_a_live_claimant() -> None:
    """The dangerous case: recovery must never yank work from a working agent."""
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        make_db(db)
        insert(db, "TASK-A", claimed_by="busy-agent")

        assert recover_orphan_task("TASK-A", "niko", "reason", db_path=db) is None
        assert status_of(db, "TASK-A") == "IN_PROGRESS"


def test_refuses_an_unexpired_lease() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        make_db(db)
        insert(db, "TASK-B", lease_expires_at="2099-01-01T00:00:00")

        assert recover_orphan_task("TASK-B", "niko", "reason", db_path=db) is None
        assert status_of(db, "TASK-B") == "IN_PROGRESS"


def test_recovers_when_lease_is_stale_but_claimant_already_cleared() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        make_db(db)
        insert(db, "TASK-C", lease_expires_at="2000-01-01T00:00:00")

        assert recover_orphan_task("TASK-C", "niko", "reason", db_path=db) is not None
        assert status_of(db, "TASK-C") == "READY"


def test_refuses_other_statuses() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        make_db(db)
        for status in ("READY", "SUBMITTED", "APPROVED", "CHANGES_REQUESTED", "RELEASED"):
            tid = f"TASK-{status}"
            insert(db, tid, status=status)
            assert recover_orphan_task(tid, "niko", "reason", db_path=db) is None, status
            assert status_of(db, tid) == status


def test_requires_an_actor() -> None:
    """Regression for codex-lab-lime's TASK-266 review: a blank actor previously
    recovered the task and was recorded as `recovered_by`, which defeats the
    attribution the verb exists to provide."""
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        make_db(db)
        insert(db, "TASK-E")
        for bad in ("", "   ", None):
            try:
                recover_orphan_task("TASK-E", bad, "a real reason", db_path=db)
            except (ValueError, AttributeError, TypeError):
                pass
            else:
                raise AssertionError(f"actor {bad!r} must raise")
            assert status_of(db, "TASK-E") == "IN_PROGRESS", f"actor {bad!r} mutated state"


def test_actor_is_stored_stripped() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        make_db(db)
        insert(db, "TASK-F")
        result = recover_orphan_task("TASK-F", "  claude-lab-niko  ", "reason", db_path=db)
        assert result is not None
        assert result["recovered_by"] == "claude-lab-niko"


def test_requires_a_reason() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        make_db(db)
        insert(db, "TASK-D")
        for bad in ("", "   "):
            try:
                recover_orphan_task("TASK-D", "niko", bad, db_path=db)
            except ValueError:
                pass
            else:
                raise AssertionError(f"empty reason {bad!r} must raise")
        assert status_of(db, "TASK-D") == "IN_PROGRESS"


def test_cli_normalizes_actor_across_every_record() -> None:
    """Regression for codex-lab-lime's TASK-266 re-review.

    recover_orphan_task() strips the actor, but the CLI previously kept using the
    raw argument for ensure_agent(), the event sender, and the summary -- so the
    agent row, the JSONL event, the SQLite event and the printed result all
    disagreed about who acted. Whitespace-padded input must produce exactly one
    identity everywhere.
    """
    import json
    import subprocess

    script = ROOT / "MAP_System" / "scripts" / "map_task.py"
    with tempfile.TemporaryDirectory() as tmp:
        tmpd = Path(tmp)
        db = tmpd / "map.db"
        # The CLI path runs the real exporter, so this fixture needs the real
        # schema rather than the minimal one the function tests use.
        schema = (ROOT / "MAP_System" / "migration" / "schema.sql").read_text()
        conn = sqlite3.connect(db)
        conn.executescript(schema)
        conn.execute(
            "INSERT INTO agents (agent_id, label, agent_type, status)"
            " VALUES ('dead-agent','Dead Agent','core','available')"
        )
        conn.execute(
            "INSERT INTO tasks (task_id, project_id, title, description, task_type,"
            " role, status, owner) VALUES"
            " ('TASK-900','P','orphan probe','probe','implementation','implementer',"
            "  'IN_PROGRESS','dead-agent')"
        )
        conn.commit()
        conn.close()

        out_dir = tmpd / "tasks"
        out_dir.mkdir()
        event_log = tmpd / "events.jsonl"

        proc = subprocess.run(
            [sys.executable, str(script), "--db", str(db),
             "--output-dir", str(out_dir), "--event-log", str(event_log),
             "recover-orphan", "TASK-900",
             "--actor", "  review-probe  ", "--reason", "padded actor probe"],
            capture_output=True, text=True,
        )
        assert proc.returncode == 0, proc.stderr

        assert '"recovered_by":"review-probe"' in proc.stdout.replace(" ", ""), proc.stdout

        conn = sqlite3.connect(db)
        agent_ids = [r[0] for r in conn.execute("SELECT agent_id FROM agents")]
        senders = [r[0] for r in conn.execute("SELECT sender_id FROM events")]
        summaries = [r[0] for r in conn.execute("SELECT summary FROM events")]
        conn.close()

        assert "review-probe" in agent_ids, f"normalized actor not registered: {agent_ids!r}"
        assert not any(a != a.strip() for a in agent_ids), (
            f"a padded identity was registered: {agent_ids!r}"
        )
        assert all(s == "review-probe" for s in senders), f"event sender not normalized: {senders!r}"
        for summary in summaries:
            assert "  review-probe" not in summary, f"double-spaced attribution: {summary!r}"

        if event_log.exists():
            for line in event_log.read_text().splitlines():
                payload = json.loads(line)
                for field in ("sender", "actor"):
                    if field in payload:
                        assert payload[field] == "review-probe", (field, payload[field])


def test_unknown_task_returns_none() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        make_db(db)
        assert recover_orphan_task("TASK-NOPE", "niko", "reason", db_path=db) is None


def main() -> int:
    for test in [
        test_recovers_the_task_186_shape,
        test_refuses_a_live_claimant,
        test_refuses_an_unexpired_lease,
        test_recovers_when_lease_is_stale_but_claimant_already_cleared,
        test_refuses_other_statuses,
        test_requires_an_actor,
        test_actor_is_stored_stripped,
        test_requires_a_reason,
        test_cli_normalizes_actor_across_every_record,
        test_unknown_task_returns_none,
    ]:
        test()
        print(f"PASS {test.__name__}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
