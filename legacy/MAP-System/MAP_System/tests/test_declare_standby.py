#!/usr/bin/env python3
"""Focused tests for declare_standby.py, including --resume-at (operator-
scheduled RnS resume, distinct from an auto-detected rate-limit reset).

--resume-at fills a real gap: RnS's resume_after machinery previously only
ever got populated by limit_watcher's own transcript-limit detector, so
there was no sanctioned way for an operator to say "nudge this agent back
at this specific time" without impersonating a real rate-limit record.
"""

from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "MAP_System" / "scripts" / "declare_standby.py"
SCHEMA = ROOT / "MAP_System" / "migration" / "schema.sql"


def make_tree(tmp: Path) -> Path:
    """Build an isolated MAP_System-shaped root so ROOT-relative paths in the
    script (map.db, events/, migration/export_to_files.py) resolve safely."""
    map_root = tmp / "MAP_System"
    (map_root / "migration").mkdir(parents=True)
    (map_root / "events").mkdir(parents=True)
    (map_root / "scripts").mkdir(parents=True)
    (map_root / "migration" / "schema.sql").write_text(SCHEMA.read_text(), encoding="utf-8")
    exporter_src = ROOT / "MAP_System" / "migration" / "export_to_files.py"
    (map_root / "migration" / "export_to_files.py").write_text(
        exporter_src.read_text(encoding="utf-8"), encoding="utf-8"
    )
    (map_root / "scripts" / "declare_standby.py").write_text(
        SCRIPT.read_text(encoding="utf-8"), encoding="utf-8"
    )
    limit_watcher_src = ROOT / "MAP_System" / "scripts" / "limit_watcher.py"
    (map_root / "scripts" / "limit_watcher.py").write_text(
        limit_watcher_src.read_text(encoding="utf-8"), encoding="utf-8"
    )
    db = map_root / "map.db"
    conn = sqlite3.connect(db)
    conn.executescript((map_root / "migration" / "schema.sql").read_text())
    conn.execute(
        "INSERT INTO agents (agent_id, label, agent_type, status) "
        "VALUES ('test-agent', 'Test Agent', 'core', 'available')"
    )
    conn.commit()
    conn.close()
    return map_root


def run(map_root: Path, *args: str) -> subprocess.CompletedProcess:
    script = map_root / "scripts" / "declare_standby.py"
    return subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True, text=True, cwd=str(map_root.parent),
    )


def agent_row(map_root: Path) -> tuple:
    with sqlite3.connect(map_root / "map.db") as conn:
        return conn.execute(
            "SELECT status, reason, resume_after FROM agents WHERE agent_id='test-agent'"
        ).fetchone()


def future_iso(hours: int = 3) -> str:
    # No microseconds: declare_standby.py normalizes to second precision
    # (matching every other resume_after value in this codebase), so a
    # timestamp that already has none round-trips exactly.
    return (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat(timespec="seconds")


def test_plain_standby_unchanged() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        map_root = make_tree(Path(tmp))
        proc = run(map_root, "test-agent")
        assert proc.returncode == 0, proc.stderr
        assert agent_row(map_root) == ("standby", "awaiting_work", None)


def test_back_unchanged() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        map_root = make_tree(Path(tmp))
        run(map_root, "test-agent")
        proc = run(map_root, "test-agent", "--back")
        assert proc.returncode == 0, proc.stderr
        assert agent_row(map_root) == ("available", None, None)


def test_resume_at_accepts_a_future_timestamp() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        map_root = make_tree(Path(tmp))
        target = future_iso(3)
        proc = run(map_root, "test-agent", "--resume-at", target)
        assert proc.returncode == 0, proc.stderr
        status, reason, resume_after = agent_row(map_root)
        assert status == "standby"
        assert reason == "scheduled"
        assert resume_after is not None
        # round-trips to the same instant even if isoformat spelling differs
        assert datetime.fromisoformat(resume_after) == datetime.fromisoformat(target)


def test_resume_at_records_a_durable_event() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        map_root = make_tree(Path(tmp))
        target = future_iso(3)
        proc = run(map_root, "test-agent", "--resume-at", target)
        assert proc.returncode == 0, proc.stderr

        with sqlite3.connect(map_root / "map.db") as conn:
            event = conn.execute(
                "SELECT event_type, task_id, summary FROM events"
            ).fetchone()
        assert event[0] == "PROGRESS"
        assert event[1] == "TASK-083"
        assert "test-agent" in event[2]
        assert "scheduled resume" in event[2]

        jsonl_lines = (map_root / "events" / "events.jsonl").read_text().splitlines()
        assert len(jsonl_lines) == 1
        entry = json.loads(jsonl_lines[0])
        assert entry["sender"] == "declare_standby"
        assert entry["task_id"] == "TASK-083"


def test_resume_at_rejects_unparseable_timestamp() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        map_root = make_tree(Path(tmp))
        proc = run(map_root, "test-agent", "--resume-at", "not-a-timestamp")
        assert proc.returncode != 0
        assert "not a parseable" in proc.stderr
        # nothing written: agent stays at its pre-existing state
        assert agent_row(map_root) == ("available", None, None)


def test_resume_at_rejects_a_past_timestamp() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        map_root = make_tree(Path(tmp))
        past = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        proc = run(map_root, "test-agent", "--resume-at", past)
        assert proc.returncode != 0
        assert "not in the future" in proc.stderr
        assert agent_row(map_root) == ("available", None, None)


def test_resume_at_mutually_exclusive_with_back_and_terminal() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        map_root = make_tree(Path(tmp))
        proc = run(map_root, "test-agent", "--resume-at", future_iso(), "--back")
        assert proc.returncode != 0
        assert "not allowed with" in proc.stderr


def test_unknown_agent_rejected() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        map_root = make_tree(Path(tmp))
        proc = run(map_root, "no-such-agent", "--resume-at", future_iso())
        assert proc.returncode != 0
        assert "unknown agent" in proc.stderr


def main() -> int:
    tests = [
        test_plain_standby_unchanged,
        test_back_unchanged,
        test_resume_at_accepts_a_future_timestamp,
        test_resume_at_records_a_durable_event,
        test_resume_at_rejects_unparseable_timestamp,
        test_resume_at_rejects_a_past_timestamp,
        test_resume_at_mutually_exclusive_with_back_and_terminal,
        test_unknown_agent_rejected,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"{len(tests)}/{len(tests)} declare_standby tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
