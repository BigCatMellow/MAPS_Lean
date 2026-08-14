#!/usr/bin/env python3
"""Lifecycle and race regressions for TASK-278 review authorship."""

from __future__ import annotations

import concurrent.futures
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

if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from MAP_System.db.claims import claim_review, get_open_review_claim, submit_task
from MAP_System.db.review_authorship import (
    UnknownSubmissionAuthor,
    get_submission_author,
)
from MAP_System.scripts.validate_review import validate


def init_db(path: Path, *, task_id: str = "TASK-A", status: str = "IN_PROGRESS") -> None:
    with sqlite3.connect(path) as conn:
        conn.executescript(SCHEMA.read_text(encoding="utf-8"))
        conn.execute(
            """
            INSERT INTO agents (agent_id, label, agent_type, status) VALUES
              ('author-a', 'Author A', 'core', 'available'),
              ('author-b', 'Author B', 'core', 'available'),
              ('reviewer-a', 'Reviewer A', 'core', 'available'),
              ('reviewer-b', 'Reviewer B', 'core', 'available'),
              ('owner-a', 'Owner A', 'core', 'available'),
              ('owner-b', 'Owner B', 'core', 'available')
            """
        )
        conn.execute(
            """
            INSERT INTO tasks
              (task_id, project_id, title, description, task_type, role, status,
               owner, claimed_by, lease_expires_at, heartbeat_at, attempt, max_attempts)
            VALUES (?, 'TEST', 'Authorship fixture', 'fixture', 'implementation',
                    'implementer', ?, 'owner-a', ?, datetime('now', '+30 minutes'),
                    datetime('now'), 1, 4)
            """,
            (task_id, status, "author-a" if status == "IN_PROGRESS" else None),
        )
        conn.execute(
            "INSERT INTO task_output_paths (task_id, path) VALUES (?, 'out.txt')",
            (task_id,),
        )
        conn.execute(
            "INSERT INTO task_acceptance_criteria (task_id, criterion) "
            "VALUES (?, 'works')",
            (task_id,),
        )


def run_map_task(db: Path, out: Path, log: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            sys.executable,
            str(MAP_TASK),
            "--db",
            str(db),
            "--output-dir",
            str(out),
            "--event-log",
            str(log),
            *args,
        ],
        capture_output=True,
        text=True,
    )


def sync_out(db: Path, out: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(EXPORTER), "--db", str(db), "--output-dir", str(out)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_submission_identity_is_atomic_and_survives_owner_drift() -> None:
    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)
        db = temp / "map.db"
        init_db(db)
        assert submit_task("TASK-A", "author-a", db_path=db, event_log=temp / "events.jsonl")
        with sqlite3.connect(db) as conn:
            assert get_submission_author(conn, "TASK-A") == "author-a"
            conn.execute("UPDATE tasks SET owner='owner-b' WHERE task_id='TASK-A'")
            assert get_submission_author(conn, "TASK-A") == "author-a"

        assert claim_review("TASK-A", "author-a", db_path=db) is False
        assert claim_review("TASK-A", "reviewer-a", db_path=db) is True


def test_unknown_legacy_submission_fails_closed_at_both_gates() -> None:
    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)
        db = temp / "map.db"
        init_db(db, status="SUBMITTED")
        sync_out(db, temp / "out")
        try:
            claim_review("TASK-A", "reviewer-a", db_path=db)
        except UnknownSubmissionAuthor as exc:
            assert "UNKNOWN SUBMISSION AUTHOR" in str(exc)
        else:
            raise AssertionError("unknown legacy author must not be treated as independent")

        result = run_map_task(
            db,
            temp / "out",
            temp / "events.jsonl",
            "reject",
            "TASK-A",
            "--reviewer",
            "reviewer-a",
            "--reason",
            "probe",
        )
        assert result.returncode != 0
        assert "UNKNOWN SUBMISSION AUTHOR" in result.stderr
        with sqlite3.connect(db) as conn:
            assert conn.execute(
                "SELECT status FROM tasks WHERE task_id='TASK-A'"
            ).fetchone()[0] == "SUBMITTED"


def test_rejection_rework_and_resubmission_replace_only_current_author() -> None:
    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)
        db = temp / "map.db"
        out = temp / "out"
        log = temp / "events.jsonl"
        init_db(db)
        assert submit_task("TASK-A", "author-a", db_path=db, event_log=log)
        sync_out(db, out)

        rejected = run_map_task(
            db, out, log, "reject", "TASK-A",
            "--reviewer", "reviewer-a", "--reason", "needs repair",
        )
        assert rejected.returncode == 0, rejected.stderr
        reworked = run_map_task(
            db, out, log, "rework", "TASK-A",
            "--actor", "author-b", "--reason", "repairing",
        )
        assert reworked.returncode == 0, reworked.stderr
        with sqlite3.connect(db) as conn:
            # Rejection/rework preserve the last submission identity.
            assert get_submission_author(conn, "TASK-A") == "author-a"
            conn.execute(
                """
                UPDATE tasks SET status='IN_PROGRESS', claimed_by='author-b',
                  lease_expires_at=datetime('now', '+30 minutes'),
                  heartbeat_at=datetime('now')
                WHERE task_id='TASK-A' AND status='READY'
                """
            )
        assert submit_task("TASK-A", "author-b", db_path=db, event_log=log)
        with sqlite3.connect(db) as conn:
            row = conn.execute(
                """
                SELECT author_id, submission_count
                FROM task_submission_authorship WHERE task_id='TASK-A'
                """
            ).fetchone()
        assert row == ("author-b", 2)
        assert claim_review("TASK-A", "author-b", db_path=db) is False
        assert claim_review("TASK-A", "reviewer-b", db_path=db) is True


def test_terminal_verdict_uses_author_not_owner() -> None:
    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)
        db = temp / "map.db"
        out = temp / "out"
        log = temp / "events.jsonl"
        init_db(db)
        assert submit_task("TASK-A", "author-a", db_path=db, event_log=log)
        sync_out(db, out)
        with sqlite3.connect(db) as conn:
            conn.execute("UPDATE tasks SET owner='owner-b' WHERE task_id='TASK-A'")
        sync_out(db, out)

        blocked = run_map_task(
            db, out, log, "reject", "TASK-A",
            "--reviewer", "author-a", "--reason", "self verdict",
        )
        assert blocked.returncode != 0
        assert "SELF_REVIEW" in blocked.stderr

        allowed = run_map_task(
            db, out, log, "reject", "TASK-A",
            "--reviewer", "reviewer-a", "--reason", "independent verdict",
        )
        assert allowed.returncode == 0, allowed.stderr


def test_terminal_verdict_race_only_one_transition_wins() -> None:
    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)
        db = temp / "map.db"
        out = temp / "out"
        log = temp / "events.jsonl"
        init_db(db)
        assert submit_task("TASK-A", "author-a", db_path=db, event_log=log)
        sync_out(db, out)

        def reject(reviewer: str) -> subprocess.CompletedProcess:
            return run_map_task(
                db, out, log, "reject", "TASK-A",
                "--reviewer", reviewer, "--reason", f"{reviewer} verdict",
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(reject, ("reviewer-a", "reviewer-b")))
        assert sum(result.returncode == 0 for result in results) == 1, [
            (result.returncode, result.stderr) for result in results
        ]
        with sqlite3.connect(db) as conn:
            assert conn.execute(
                "SELECT status FROM tasks WHERE task_id='TASK-A'"
            ).fetchone()[0] == "CHANGES_REQUESTED"


def test_duplicate_review_claim_race_still_has_one_winner() -> None:
    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)
        db = temp / "map.db"
        init_db(db)
        assert submit_task("TASK-A", "author-a", db_path=db, event_log=temp / "events.jsonl")

        def attempt(reviewer: str) -> bool:
            return claim_review("TASK-A", reviewer, db_path=db)

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(attempt, ("reviewer-a", "reviewer-b")))
        assert sorted(results) == [False, True], results
        claim = get_open_review_claim("TASK-A", db_path=db)
        assert claim and claim["reviewer_id"] in {"reviewer-a", "reviewer-b"}


def test_review_validator_uses_canonical_identity_not_artifact_owner_text() -> None:
    text = """task_id: TASK-A
reviewer: invented-reviewer
task_owner: unrelated-owner

## Verdict
APPROVED
## Acceptance Criteria Check
PASS
## Files Reviewed
- `out.txt`
## Forbidden Changes Check
PASS
"""
    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)
        db = temp / "map.db"
        init_db(db)
        assert submit_task("TASK-A", "author-a", db_path=db, event_log=temp / "events.jsonl")
        assert validate(
            text, "TASK-A", db_path=db, reviewer_id="reviewer-a"
        ) == []
        issues = validate(text, "TASK-A", db_path=db, reviewer_id="author-a")
        assert any("SELF_REVIEW" in issue for issue in issues)


def test_canonical_independence_overrides_artifact_owner_text_false_block() -> None:
    text = """task_id: TASK-A
reviewer: reviewer-a
task_owner: reviewer-a

## Verdict
APPROVED
## Acceptance Criteria Check
PASS
## Files Reviewed
- `out.txt`
## Forbidden Changes Check
PASS
"""
    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)
        db = temp / "map.db"
        init_db(db)
        assert submit_task("TASK-A", "author-a", db_path=db, event_log=temp / "events.jsonl")

        # Artifact task_owner text matches the reviewer, which the legacy
        # heuristic alone would flag as SELF_REVIEW. The canonical author is
        # a different agent, so an independent reviewer must not be blocked.
        assert validate(
            text, "TASK-A", db_path=db, reviewer_id="reviewer-a"
        ) == []

        # The canonical author remains blocked even though artifact text
        # never names them.
        issues = validate(text, "TASK-A", db_path=db, reviewer_id="author-a")
        assert any("SELF_REVIEW" in issue for issue in issues)

        # Without canonical inputs (legacy path), the artifact-text heuristic
        # is still the only signal available and must still catch the match.
        legacy_issues = validate(text, "TASK-A")
        assert any("SELF_REVIEW" in issue for issue in legacy_issues)


def main() -> int:
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_")]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"{len(tests)} review-authorship tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
