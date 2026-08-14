#!/usr/bin/env python3
"""TASK-282: criterion-level submission claims and independent verification.

Extends a submission with a per-criterion claimed status and evidence
references linked to task revision and run ID (TASK-281), while keeping
reviewer-verified status in a separate append-only table so one criterion
can be rejected without mutating the implementer's original claim.

This module never reads or writes `tasks.status` and does not drive any
lifecycle transition; it records structured evidence alongside the existing
claim/submit/review/approve flow in `db/claims.py` and `scripts/map_task.py`.

Usage:
    python3 MAP_System/scripts/submission_records.py claim \\
        --task-id TASK-NNN --criterion-id ID --status complete|partial|blocked \\
        --author <agent> [--evidence <repo-relative-path> ...] \\
        [--task-revision <sha>] [--run-id <RUN-...>]

    python3 MAP_System/scripts/submission_records.py verdict \\
        --claim-id ID --status confirmed|rejected --reviewer <agent> [--notes TEXT]

    python3 MAP_System/scripts/submission_records.py show --task-id TASK-NNN \\
        [--submission-count N]
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

DEFAULT_DB = ROOT / "map.db"
SCHEMA = ROOT / "migration" / "submission_record_schema.sql"

VALID_CLAIMED_STATUSES = {"complete", "partial", "blocked"}
VALID_VERIFIED_STATUSES = {"confirmed", "rejected"}


class UsageError(RuntimeError):
    pass


def connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA.read_text(encoding="utf-8"))
    return conn


def _current_submission_count(conn: sqlite3.Connection, task_id: str) -> int:
    row = conn.execute(
        "SELECT submission_count FROM task_submission_authorship WHERE task_id = ?",
        (task_id,),
    ).fetchone()
    if row is None:
        raise UsageError(
            f"{task_id} has no canonical submission authorship record "
            "(task_submission_authorship); it must be submitted via "
            "db.claims.submit_task before criterion claims can be recorded"
        )
    return row["submission_count"]


def record_claim(
    *,
    task_id: str,
    criterion_id: int,
    claimed_status: str,
    author_id: str,
    evidence_refs: list[str] | None = None,
    task_revision: str | None = None,
    run_id: str | None = None,
    db_path: Path = DEFAULT_DB,
) -> dict[str, Any]:
    if claimed_status not in VALID_CLAIMED_STATUSES:
        raise UsageError(f"unknown claimed_status: {claimed_status!r}")
    evidence_refs = list(evidence_refs or [])

    with connect(db_path) as conn:
        criterion = conn.execute(
            "SELECT id, task_id, criterion FROM task_acceptance_criteria WHERE id = ?",
            (criterion_id,),
        ).fetchone()
        if criterion is None or criterion["task_id"] != task_id:
            raise UsageError(f"criterion {criterion_id} does not belong to {task_id}")
        if not conn.execute("SELECT 1 FROM agents WHERE agent_id = ?", (author_id,)).fetchone():
            raise UsageError(f"unknown author agent: {author_id}")
        canonical_author = conn.execute(
            "SELECT author_id FROM task_submission_authorship WHERE task_id = ?",
            (task_id,),
        ).fetchone()
        if canonical_author and canonical_author["author_id"].casefold() != author_id.casefold():
            raise UsageError(
                f"claim author '{author_id}' does not match the canonical "
                f"submission author '{canonical_author['author_id']}' for {task_id}; "
                "claims must be linked to the real submitter, not an artifact-supplied identity"
            )

        if claimed_status == "complete":
            missing = [ref for ref in evidence_refs if not (REPO / ref).is_file()]
            if not evidence_refs:
                raise UsageError(
                    f"criterion {criterion_id} cannot be claimed complete without "
                    "at least one evidence reference"
                )
            if missing:
                raise UsageError(
                    f"criterion {criterion_id} cannot be claimed complete: missing "
                    f"evidence file(s): {', '.join(missing)}"
                )

        submission_count = _current_submission_count(conn, task_id)
        cursor = conn.execute(
            """
            INSERT INTO submission_criterion_claims
                (task_id, submission_count, criterion_id, claimed_status,
                 evidence_refs, task_revision, run_id, author_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                task_id, submission_count, criterion_id, claimed_status,
                json.dumps(sorted(evidence_refs), separators=(",", ":")),
                task_revision, run_id, author_id,
            ),
        )
        conn.commit()
        return get_claim(cursor.lastrowid, db_path=db_path)


def get_claim(claim_id: int, *, db_path: Path = DEFAULT_DB) -> dict[str, Any]:
    with connect(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM submission_criterion_claims WHERE id = ?", (claim_id,)
        ).fetchone()
        if row is None:
            raise UsageError(f"unknown claim: {claim_id}")
        record = dict(row)
        record["evidence_refs"] = json.loads(record["evidence_refs"])
        record["verdicts"] = [
            dict(v) for v in conn.execute(
                "SELECT * FROM submission_criterion_verdicts WHERE claim_id = ? ORDER BY created_at",
                (claim_id,),
            )
        ]
        return record


def record_verdict(
    *,
    claim_id: int,
    verified_status: str,
    reviewer_id: str,
    notes: str | None = None,
    db_path: Path = DEFAULT_DB,
) -> dict[str, Any]:
    if verified_status not in VALID_VERIFIED_STATUSES:
        raise UsageError(f"unknown verified_status: {verified_status!r}")
    with connect(db_path) as conn:
        claim = conn.execute(
            "SELECT id, task_id, author_id FROM submission_criterion_claims WHERE id = ?",
            (claim_id,),
        ).fetchone()
        if claim is None:
            raise UsageError(f"unknown claim: {claim_id}")
        if not conn.execute("SELECT 1 FROM agents WHERE agent_id = ?", (reviewer_id,)).fetchone():
            raise UsageError(f"unknown reviewer agent: {reviewer_id}")
        if reviewer_id.casefold() == claim["author_id"].casefold():
            raise PermissionError(
                f"SELF_REVIEW: reviewer '{reviewer_id}' is the claim author for "
                f"claim {claim_id}"
            )
        conn.execute(
            """
            INSERT INTO submission_criterion_verdicts
                (claim_id, verified_status, reviewer_id, notes)
            VALUES (?, ?, ?, ?)
            """,
            (claim_id, verified_status, reviewer_id, notes),
        )
        conn.commit()
        return get_claim(claim_id, db_path=db_path)


def get_claims(
    task_id: str, *, submission_count: int | None = None, db_path: Path = DEFAULT_DB
) -> list[dict[str, Any]]:
    with connect(db_path) as conn:
        if submission_count is None:
            rows = conn.execute(
                "SELECT id FROM submission_criterion_claims WHERE task_id = ? ORDER BY id",
                (task_id,),
            )
        else:
            rows = conn.execute(
                "SELECT id FROM submission_criterion_claims WHERE task_id = ? "
                "AND submission_count = ? ORDER BY id",
                (task_id, submission_count),
            )
        claim_ids = [row["id"] for row in rows]
    return [get_claim(claim_id, db_path=db_path) for claim_id in claim_ids]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    subparsers = parser.add_subparsers(dest="command", required=True)

    claim = subparsers.add_parser("claim")
    claim.add_argument("--task-id", required=True)
    claim.add_argument("--criterion-id", type=int, required=True)
    claim.add_argument("--status", required=True, dest="claimed_status")
    claim.add_argument("--author", required=True, dest="author_id")
    claim.add_argument("--evidence", action="append", default=[], dest="evidence_refs")
    claim.add_argument("--task-revision")
    claim.add_argument("--run-id")

    verdict = subparsers.add_parser("verdict")
    verdict.add_argument("--claim-id", type=int, required=True)
    verdict.add_argument("--status", required=True, dest="verified_status")
    verdict.add_argument("--reviewer", required=True, dest="reviewer_id")
    verdict.add_argument("--notes")

    show = subparsers.add_parser("show")
    show.add_argument("--task-id", required=True)
    show.add_argument("--submission-count", type=int)

    args = parser.parse_args(argv)

    try:
        if args.command == "claim":
            record = record_claim(
                task_id=args.task_id, criterion_id=args.criterion_id,
                claimed_status=args.claimed_status, author_id=args.author_id,
                evidence_refs=args.evidence_refs, task_revision=args.task_revision,
                run_id=args.run_id, db_path=args.db,
            )
            print(json.dumps(record, separators=(",", ":")))
        elif args.command == "verdict":
            record = record_verdict(
                claim_id=args.claim_id, verified_status=args.verified_status,
                reviewer_id=args.reviewer_id, notes=args.notes, db_path=args.db,
            )
            print(json.dumps(record, separators=(",", ":")))
        elif args.command == "show":
            records = get_claims(args.task_id, submission_count=args.submission_count, db_path=args.db)
            print(json.dumps(records, separators=(",", ":")))
        return 0
    except (UsageError, PermissionError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
