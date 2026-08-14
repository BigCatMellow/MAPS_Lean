#!/usr/bin/env python3
"""Focused regressions for TASK-282 criterion-level submission claims."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
SCHEMA = ROOT / "migration" / "schema.sql"

if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from MAP_System.db.claims import submit_task
from MAP_System.scripts.submission_records import (
    UsageError,
    get_claim,
    get_claims,
    record_claim,
    record_verdict,
)


def init_db(path: Path, *, task_id: str = "TASK-A") -> int:
    """Seed a fixture task with one acceptance criterion; returns its id."""
    with sqlite3.connect(path) as conn:
        conn.executescript(SCHEMA.read_text(encoding="utf-8"))
        conn.execute(
            "INSERT INTO agents (agent_id, label, agent_type, status) VALUES "
            "('author-a', 'Author A', 'core', 'available'), "
            "('reviewer-a', 'Reviewer A', 'core', 'available'), "
            "('owner-a', 'Owner A', 'core', 'available')"
        )
        conn.execute(
            """
            INSERT INTO tasks
              (task_id, project_id, title, description, task_type, role, status,
               owner, claimed_by, lease_expires_at, heartbeat_at, attempt, max_attempts)
            VALUES (?, 'TEST', 'Claims fixture', 'fixture', 'implementation',
                    'implementer', 'IN_PROGRESS', 'owner-a', 'author-a',
                    datetime('now', '+30 minutes'), datetime('now'), 1, 4)
            """,
            (task_id,),
        )
        cursor = conn.execute(
            "INSERT INTO task_acceptance_criteria (task_id, criterion) VALUES (?, 'works')",
            (task_id,),
        )
        return cursor.lastrowid


def test_claim_links_criterion_author_revision_and_run() -> None:
    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)
        db = temp / "map.db"
        criterion_id = init_db(db)
        assert submit_task("TASK-A", "author-a", db_path=db, event_log=temp / "events.jsonl")

        claim = record_claim(
            task_id="TASK-A", criterion_id=criterion_id, claimed_status="complete",
            author_id="author-a", evidence_refs=["MAP_System/tests/test_submission_records.py"],
            task_revision="abc123", run_id="RUN-TASK-A-01", db_path=db,
        )
        assert claim["task_id"] == "TASK-A"
        assert claim["criterion_id"] == criterion_id
        assert claim["claimed_status"] == "complete"
        assert claim["author_id"] == "author-a"
        assert claim["task_revision"] == "abc123"
        assert claim["run_id"] == "RUN-TASK-A-01"
        assert claim["submission_count"] == 1
        assert claim["evidence_refs"] == ["MAP_System/tests/test_submission_records.py"]
        assert claim["verdicts"] == []


def test_complete_claim_requires_existing_evidence() -> None:
    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)
        db = temp / "map.db"
        criterion_id = init_db(db)
        assert submit_task("TASK-A", "author-a", db_path=db, event_log=temp / "events.jsonl")

        try:
            record_claim(
                task_id="TASK-A", criterion_id=criterion_id, claimed_status="complete",
                author_id="author-a", evidence_refs=["MAP_System/does/not/exist.py"],
                db_path=db,
            )
        except UsageError as exc:
            assert "missing evidence" in str(exc)
        else:
            raise AssertionError("complete claim with missing evidence must be rejected")

        with sqlite3.connect(db) as conn:
            assert conn.execute("SELECT count(*) FROM submission_criterion_claims").fetchone()[0] == 0


def test_complete_claim_requires_at_least_one_evidence_ref() -> None:
    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)
        db = temp / "map.db"
        criterion_id = init_db(db)
        assert submit_task("TASK-A", "author-a", db_path=db, event_log=temp / "events.jsonl")

        try:
            record_claim(
                task_id="TASK-A", criterion_id=criterion_id, claimed_status="complete",
                author_id="author-a", evidence_refs=[], db_path=db,
            )
        except UsageError as exc:
            assert "without at least one evidence reference" in str(exc)
        else:
            raise AssertionError("complete claim with zero evidence must be rejected")


def test_partial_and_blocked_claims_do_not_require_evidence() -> None:
    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)
        db = temp / "map.db"
        criterion_id = init_db(db)
        assert submit_task("TASK-A", "author-a", db_path=db, event_log=temp / "events.jsonl")

        partial = record_claim(
            task_id="TASK-A", criterion_id=criterion_id, claimed_status="partial",
            author_id="author-a", db_path=db,
        )
        assert partial["claimed_status"] == "partial"
        assert partial["evidence_refs"] == []


def test_claim_author_must_match_canonical_submission_author() -> None:
    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)
        db = temp / "map.db"
        criterion_id = init_db(db)
        assert submit_task("TASK-A", "author-a", db_path=db, event_log=temp / "events.jsonl")

        try:
            record_claim(
                task_id="TASK-A", criterion_id=criterion_id, claimed_status="partial",
                author_id="reviewer-a", db_path=db,
            )
        except UsageError as exc:
            assert "does not match the canonical" in str(exc)
        else:
            raise AssertionError("a claim from a non-canonical author must be rejected")


def test_verdict_confirms_or_rejects_one_criterion_without_mutating_claim() -> None:
    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)
        db = temp / "map.db"
        criterion_id = init_db(db)
        assert submit_task("TASK-A", "author-a", db_path=db, event_log=temp / "events.jsonl")
        claim = record_claim(
            task_id="TASK-A", criterion_id=criterion_id, claimed_status="complete",
            author_id="author-a", evidence_refs=["MAP_System/tests/test_submission_records.py"],
            db_path=db,
        )

        rejected = record_verdict(
            claim_id=claim["id"], verified_status="rejected", reviewer_id="reviewer-a",
            notes="evidence does not cover the full criterion", db_path=db,
        )
        assert len(rejected["verdicts"]) == 1
        assert rejected["verdicts"][0]["verified_status"] == "rejected"
        assert rejected["verdicts"][0]["reviewer_id"] == "reviewer-a"
        # The original claim fields are untouched by the verdict.
        assert rejected["claimed_status"] == "complete"
        assert rejected["author_id"] == "author-a"
        assert rejected["evidence_refs"] == ["MAP_System/tests/test_submission_records.py"]


def test_verdict_rejects_self_review() -> None:
    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)
        db = temp / "map.db"
        criterion_id = init_db(db)
        assert submit_task("TASK-A", "author-a", db_path=db, event_log=temp / "events.jsonl")
        claim = record_claim(
            task_id="TASK-A", criterion_id=criterion_id, claimed_status="partial",
            author_id="author-a", db_path=db,
        )
        try:
            record_verdict(
                claim_id=claim["id"], verified_status="confirmed", reviewer_id="author-a",
                db_path=db,
            )
        except PermissionError as exc:
            assert "SELF_REVIEW" in str(exc)
        else:
            raise AssertionError("a reviewer must not verify their own claim")


def test_rework_and_resubmission_produce_new_claims_under_new_submission_count() -> None:
    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)
        db = temp / "map.db"
        criterion_id = init_db(db)
        assert submit_task("TASK-A", "author-a", db_path=db, event_log=temp / "events.jsonl")
        first = record_claim(
            task_id="TASK-A", criterion_id=criterion_id, claimed_status="partial",
            author_id="author-a", db_path=db,
        )
        assert first["submission_count"] == 1

        with sqlite3.connect(db) as conn:
            conn.execute(
                "UPDATE tasks SET status='IN_PROGRESS', claimed_by='author-a', "
                "lease_expires_at=datetime('now', '+30 minutes'), heartbeat_at=datetime('now') "
                "WHERE task_id='TASK-A'"
            )
        assert submit_task("TASK-A", "author-a", db_path=db, event_log=temp / "events.jsonl")
        second = record_claim(
            task_id="TASK-A", criterion_id=criterion_id, claimed_status="complete",
            author_id="author-a", evidence_refs=["MAP_System/tests/test_submission_records.py"],
            db_path=db,
        )
        assert second["submission_count"] == 2

        history = get_claims("TASK-A", db_path=db)
        assert [c["id"] for c in history] == [first["id"], second["id"]]
        # The prior claim is untouched, not overwritten.
        assert get_claim(first["id"], db_path=db)["claimed_status"] == "partial"


def test_unknown_criterion_is_rejected_without_mutation() -> None:
    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)
        db = temp / "map.db"
        init_db(db)
        assert submit_task("TASK-A", "author-a", db_path=db, event_log=temp / "events.jsonl")
        try:
            record_claim(
                task_id="TASK-A", criterion_id=999999, claimed_status="partial",
                author_id="author-a", db_path=db,
            )
        except UsageError as exc:
            assert "does not belong to" in str(exc)
        else:
            raise AssertionError("an unknown criterion id must be rejected")
        with sqlite3.connect(db) as conn:
            assert conn.execute("SELECT count(*) FROM submission_criterion_claims").fetchone()[0] == 0


def main() -> int:
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_")]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"{len(tests)} submission-record tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
