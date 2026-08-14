#!/usr/bin/env python3
"""Tests for review_routing.py (TASK-290: orchestrator auto-spawn eligibility)."""

from __future__ import annotations

from pathlib import Path
import sqlite3
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from MAP_System.db.review_authorship import record_submission_author  # noqa: E402
from MAP_System.scripts.review_routing import (  # noqa: E402
    disqualified_reviewers,
    eligible_reviewer,
    needs_reviewer,
    rotation_chain,
)

SCHEMA = ROOT / "migration" / "schema.sql"

CONTINUITY_TEMPLATE = """<!-- hpom: file: shared/context-continuity.md -->
# Context Continuity

<!-- context-rotation-state
{state}
-->
"""


def init_db(path: Path, *, submitted_by: str | None = "codex-lab-alfa") -> None:
    with sqlite3.connect(path) as conn:
        conn.executescript(SCHEMA.read_text(encoding="utf-8"))
        for agent in {"codex-lab-alfa", "codex-lab-beta", "codex-lab-gamma"}:
            conn.execute(
                "INSERT INTO agents (agent_id, label, agent_type, status) VALUES (?, ?, 'core', 'available')",
                (agent, agent),
            )
        conn.execute(
            """
            INSERT INTO tasks
              (task_id, project_id, title, description, task_type, role, status, owner, attempt, max_attempts)
            VALUES
              ('TASK-R', 'TEST', 'Reviewed task', 'desc', 'implementation', 'implementer', 'SUBMITTED', 'codex-lab-alfa', 1, 3)
            """
        )
        if submitted_by:
            record_submission_author(conn, "TASK-R", submitted_by)
            conn.commit()


def write_continuity(path: Path, state: dict) -> None:
    import json

    path.write_text(CONTINUITY_TEMPLATE.format(state=json.dumps(state)), encoding="utf-8")


def test_needs_reviewer_true_with_no_claim() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        init_db(db)
        conn = sqlite3.connect(db)
        conn.row_factory = sqlite3.Row
        assert needs_reviewer(conn, "TASK-R") is True


def test_needs_reviewer_false_with_live_claim() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        init_db(db)
        conn = sqlite3.connect(db)
        conn.row_factory = sqlite3.Row
        conn.execute(
            """
            INSERT INTO reviews (review_id, task_id, reviewer_id)
            VALUES ('REV-1', 'TASK-R', 'codex-lab-beta')
            """
        )
        conn.commit()
        assert needs_reviewer(conn, "TASK-R") is False


def test_disqualified_reviewers_includes_author_only_with_no_rotation_history() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        continuity = Path(tmp) / "context-continuity.md"
        init_db(db)
        write_continuity(continuity, {"schema_version": 1, "revision": 0, "rotations": {}, "history": []})
        conn = sqlite3.connect(db)
        conn.row_factory = sqlite3.Row
        assert disqualified_reviewers(conn, "TASK-R", master_path=continuity) == {"codex-lab-alfa"}


def test_disqualified_reviewers_includes_rotation_predecessor() -> None:
    """codex-lab-alfa (the submission author) was ack'd as the replacement
    for codex-lab-zed in a finalized rotation -- zed inherited alfa's full
    context and must be disqualified too, even though its agent_id differs."""
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        continuity = Path(tmp) / "context-continuity.md"
        init_db(db)
        write_continuity(
            continuity,
            {
                "schema_version": 1,
                "revision": 1,
                "history": [],
                "rotations": {
                    "codex-lab-zed": {
                        "old_agent": "codex-lab-zed",
                        "phase": "finalized",
                        "ack": {"replacement_agent": "codex-lab-alfa"},
                    }
                },
            },
        )
        conn = sqlite3.connect(db)
        conn.row_factory = sqlite3.Row
        result = disqualified_reviewers(conn, "TASK-R", master_path=continuity)
        assert result == {"codex-lab-alfa", "codex-lab-zed"}


def test_rotation_chain_walks_multiple_hops() -> None:
    """zed -> yod -> alfa: a two-hop lineage should disqualify all three."""
    with tempfile.TemporaryDirectory() as tmp:
        continuity = Path(tmp) / "context-continuity.md"
        write_continuity(
            continuity,
            {
                "schema_version": 1,
                "revision": 2,
                "history": [],
                "rotations": {
                    "codex-lab-zed": {
                        "old_agent": "codex-lab-zed",
                        "phase": "finalized",
                        "ack": {"replacement_agent": "codex-lab-yod"},
                    },
                    "codex-lab-yod": {
                        "old_agent": "codex-lab-yod",
                        "phase": "finalized",
                        "ack": {"replacement_agent": "codex-lab-alfa"},
                    },
                },
            },
        )
        chain = rotation_chain("codex-lab-alfa", master_path=continuity)
        assert chain == {"codex-lab-alfa", "codex-lab-yod", "codex-lab-zed"}


def test_eligible_reviewer_excludes_author_and_lineage() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        continuity = Path(tmp) / "context-continuity.md"
        init_db(db)
        write_continuity(
            continuity,
            {
                "schema_version": 1,
                "revision": 1,
                "history": [],
                "rotations": {
                    "codex-lab-zed": {
                        "old_agent": "codex-lab-zed",
                        "phase": "finalized",
                        "ack": {"replacement_agent": "codex-lab-alfa"},
                    }
                },
            },
        )
        conn = sqlite3.connect(db)
        conn.row_factory = sqlite3.Row
        chosen = eligible_reviewer(
            conn, "TASK-R", {"codex-lab-alfa", "codex-lab-zed", "codex-lab-beta"}, master_path=continuity
        )
        assert chosen == "codex-lab-beta"


def test_eligible_reviewer_returns_none_when_every_live_agent_disqualified() -> None:
    """This is the escalate-to-operator case: do not spawn a compromised reviewer."""
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "map.db"
        continuity = Path(tmp) / "context-continuity.md"
        init_db(db)
        write_continuity(continuity, {"schema_version": 1, "revision": 0, "rotations": {}, "history": []})
        conn = sqlite3.connect(db)
        conn.row_factory = sqlite3.Row
        chosen = eligible_reviewer(conn, "TASK-R", {"codex-lab-alfa"}, master_path=continuity)
        assert chosen is None


def main() -> int:
    tests = [
        test_needs_reviewer_true_with_no_claim,
        test_needs_reviewer_false_with_live_claim,
        test_disqualified_reviewers_includes_author_only_with_no_rotation_history,
        test_disqualified_reviewers_includes_rotation_predecessor,
        test_rotation_chain_walks_multiple_hops,
        test_eligible_reviewer_excludes_author_and_lineage,
        test_eligible_reviewer_returns_none_when_every_live_agent_disqualified,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
