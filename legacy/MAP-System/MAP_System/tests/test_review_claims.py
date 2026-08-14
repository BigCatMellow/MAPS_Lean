#!/usr/bin/env python3
"""Tests for atomic review claiming (TASK-199 / IDEA-0017)."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "migration" / "schema.sql"

if str(ROOT.parent) not in sys.path:
    sys.path.insert(0, str(ROOT.parent))

from MAP_System.db.claims import claim_review, get_open_review_claim, release_review_claim


def init_db(path: Path, *, status: str = "SUBMITTED", owner: str = "owner-agent") -> None:
    with sqlite3.connect(path) as conn:
        conn.executescript(SCHEMA.read_text(encoding="utf-8"))
        conn.execute(
            "INSERT INTO agents (agent_id, label, agent_type, status) VALUES "
            "(?, 'Owner', 'core', 'available')",
            (owner,),
        )
        conn.execute(
            "INSERT INTO agents (agent_id, label, agent_type, status) VALUES "
            "('reviewer-a', 'Reviewer A', 'core', 'available'), "
            "('reviewer-b', 'Reviewer B', 'core', 'available')"
        )
        conn.execute(
            """
            INSERT INTO tasks
              (task_id, project_id, title, description, task_type, role, status,
               owner, attempt, max_attempts)
            VALUES
              ('TASK-R', 'TEST', 'Reviewable task', 'desc', 'implementation',
               'worker', ?, ?, 0, 3)
            """,
            (status, owner),
        )
        if status == "SUBMITTED":
            # TASK-278: a submitted fixture must declare its canonical author.
            # This keeps the legacy arbitration tests about their intended
            # invariant; unknown-author behavior has dedicated fail-closed
            # coverage in test_review_authorship.py.
            conn.execute(
                """
                INSERT INTO task_submission_authorship (task_id, author_id)
                VALUES ('TASK-R', ?)
                """,
                (owner,),
            )


def test_claim_review_succeeds_on_submitted_task():
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        init_db(db)
        assert claim_review("TASK-R", "reviewer-a", db_path=db) is True
        claim = get_open_review_claim("TASK-R", db_path=db)
        assert claim is not None
        assert claim["reviewer_id"] == "reviewer-a"


def test_concurrent_claim_race_only_one_wins():
    """The core guarantee: two reviewers racing for the same SUBMITTED task
    can never both hold an open claim -- the unique index arbitrates."""
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        init_db(db)
        first = claim_review("TASK-R", "reviewer-a", db_path=db)
        second = claim_review("TASK-R", "reviewer-b", db_path=db)
        assert first is True
        assert second is False
        claim = get_open_review_claim("TASK-R", db_path=db)
        assert claim["reviewer_id"] == "reviewer-a"


def test_self_review_blocked():
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        init_db(db, owner="owner-agent")
        assert claim_review("TASK-R", "owner-agent", db_path=db) is False
        assert get_open_review_claim("TASK-R", db_path=db) is None


def test_claim_requires_submitted_status():
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        init_db(db, status="IN_PROGRESS")
        assert claim_review("TASK-R", "reviewer-a", db_path=db) is False


def test_claim_unknown_task_returns_false():
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        init_db(db)
        assert claim_review("TASK-GHOST", "reviewer-a", db_path=db) is False


def test_release_by_holder_succeeds_and_frees_the_slot():
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        init_db(db)
        assert claim_review("TASK-R", "reviewer-a", db_path=db) is True
        assert release_review_claim(
            "TASK-R", "reviewer-a", verdict="APPROVED", summary="looks good",
            db_path=db,
        ) is True
        assert get_open_review_claim("TASK-R", db_path=db) is None
        # slot is free again: a new reviewer can claim
        assert claim_review("TASK-R", "reviewer-b", db_path=db) is True


def test_release_by_non_holder_rejected():
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        init_db(db)
        assert claim_review("TASK-R", "reviewer-a", db_path=db) is True
        assert release_review_claim("TASK-R", "reviewer-b", db_path=db) is False
        # original claim is untouched
        claim = get_open_review_claim("TASK-R", db_path=db)
        assert claim["reviewer_id"] == "reviewer-a"


def test_release_with_no_open_claim_returns_false():
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        init_db(db)
        assert release_review_claim("TASK-R", "reviewer-a", db_path=db) is False


def test_unregistered_reviewer_can_claim_an_open_review() -> None:
    """TASK-270 regression, the exact live failure of 2026-07-22.

    reviews.reviewer_id is a foreign key to agents(agent_id). A reviewer that
    was never registered used to hit a FOREIGN KEY violation that claim_review
    flattened into a bare False -- indistinguishable from "already claimed",
    which review-guide.md told the reviewer to read as "stand down". A real
    reviewer self-ejected from an open queue and the submission stalled."""
    with tempfile.TemporaryDirectory() as td:
        db = Path(td) / "map.db"
        init_db(db)
        assert claim_review("TASK-R", "never-registered-agent", db_path=db) is True
        claim = get_open_review_claim("TASK-R", db_path=db)
        assert claim is not None and claim["reviewer_id"] == "never-registered-agent"
        with sqlite3.connect(db) as conn:
            row = conn.execute(
                "SELECT agent_type, status FROM agents WHERE agent_id = ?",
                ("never-registered-agent",),
            ).fetchone()
        assert row == ("core", "available"), row


def test_second_claimant_is_still_refused_after_auto_registration() -> None:
    """Auto-registering the reviewer must not weaken the one-open-claim rule:
    a genuine second claimant still gets False, not an exception."""
    with tempfile.TemporaryDirectory() as td:
        db = Path(td) / "map.db"
        init_db(db)
        assert claim_review("TASK-R", "fresh-reviewer-one", db_path=db) is True
        assert claim_review("TASK-R", "fresh-reviewer-two", db_path=db) is False


def test_non_uniqueness_integrity_error_is_not_swallowed() -> None:
    """The other half of TASK-270: claim_review used to flatten EVERY
    IntegrityError into False, so any unexpected constraint failure silently
    told a reviewer to stand down. Only the open-claim uniqueness violation may
    mean already-claimed; anything else must stay loud."""
    with tempfile.TemporaryDirectory() as td:
        db = Path(td) / "map.db"
        init_db(db)
        # force a non-uniqueness integrity failure on the reviews insert
        with sqlite3.connect(db) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute(
                "CREATE TRIGGER reviews_force_check BEFORE INSERT ON reviews "
                "BEGIN SELECT RAISE(ABORT, 'CHECK constraint failed: synthetic'); END"
            )
        raised = False
        try:
            claim_review("TASK-R", "reviewer-a", db_path=db)
        except sqlite3.IntegrityError:
            raised = True
        assert raised, "a non-uniqueness IntegrityError must propagate, not return False"


def test_review_id_primary_key_collision_raises_not_false() -> None:
    """TASK-270 re-review (codex-lab-lime): the first fix classified an
    already-claimed slot by matching 'unique' in the error text. A collision on
    the reviews.review_id PRIMARY KEY also raises 'UNIQUE constraint failed' but
    has nothing to do with the claim slot -- there is NO open claim -- yet it was
    swallowed into False, re-creating the same silent stand-down for a different
    error. The classifier now re-checks the open-claim invariant instead, so this
    must raise.

    Forced deterministically: seed a COMPLETED review whose review_id is exactly
    the id claim_review will generate, by monkeypatching uuid4 to a fixed hex.
    A completed row does not occupy the open-claim partial index, so the only
    failure the insert can hit is the primary-key collision."""
    import MAP_System.db.claims as claims_mod

    with tempfile.TemporaryDirectory() as td:
        db = Path(td) / "map.db"
        init_db(db)
        fixed_hex = "deadbeefdeadbeefdeadbeefdeadbeef"
        colliding_id = f"REV-TASK-R-reviewer-a-{fixed_hex[:8]}"
        with sqlite3.connect(db) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            # a COMPLETED review with the id the next claim will generate:
            # occupies the PK but NOT the WHERE completed_at IS NULL index.
            conn.execute(
                "INSERT INTO reviews (review_id, task_id, reviewer_id, completed_at) "
                "VALUES (?, 'TASK-R', 'reviewer-b', '2026-07-22T00:00:00Z')",
                (colliding_id,),
            )
        assert get_open_review_claim("TASK-R", db_path=db) is None  # queue is open

        class _FixedUUID:
            hex = fixed_hex

        real_uuid4 = claims_mod.uuid.uuid4
        claims_mod.uuid.uuid4 = lambda: _FixedUUID()
        try:
            raised = False
            try:
                claim_review("TASK-R", "reviewer-a", db_path=db)
            except sqlite3.IntegrityError:
                raised = True
        finally:
            claims_mod.uuid.uuid4 = real_uuid4
        assert raised, (
            "a review_id PRIMARY KEY collision with no open claim must raise, "
            "not be flattened into False")


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"{len(tests)} review-claim tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
