#!/usr/bin/env python3
"""Reviewer-eligibility helper for orchestrator auto-spawn routing (TASK-290).

Extends TASK-286's "a lane opens only when live state genuinely needs it"
rule to independent review: when graph/runner.py reports next_route=review,
the orchestrator should spawn a reviewer only for a submitted task with no
live review claim, and only for a candidate that is neither the submission
author nor a same-lineage predecessor/replacement identity of that author.

The DB-level no-self-review check (db/review_authorship.py) only compares
literal agent_id strings. TASK-288's review this session found that a
context-rotation replacement session inherits its predecessor's full
context, so it is not an independent check in spirit even when the two
agent_id strings differ. disqualified_reviewers() closes that gap by
walking shared/context-continuity.md's rotation ledger.
"""

from __future__ import annotations

from pathlib import Path
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT.parent) not in sys.path:
    sys.path.insert(0, str(ROOT.parent))

from MAP_System.db.claims import get_open_review_claim  # noqa: E402
from MAP_System.db.review_authorship import get_submission_author  # noqa: E402
from MAP_System.scripts.context_rotation import parse_master  # noqa: E402

DEFAULT_CONTINUITY_MD = ROOT / "shared" / "context-continuity.md"


def rotation_chain(agent_id: str, master_path: Path = DEFAULT_CONTINUITY_MD) -> set[str]:
    """Return agent_id plus every ancestor identity in its rotation lineage.

    Walks shared/context-continuity.md's rotations: for each entry whose
    ack.replacement_agent equals a name already in the chain, that entry's
    old_agent (the predecessor) is added too, repeated until no new
    ancestor is found. History entries (abandoned/superseded-by-a-different-
    rotation) are included the same way -- a lineage link is a lineage
    link regardless of the rotation's current phase.
    """
    chain = {agent_id}
    state = parse_master(master_path)
    all_entries = list(state.get("rotations", {}).items())
    all_entries += [(entry.get("old_agent"), entry) for entry in state.get("history", [])]

    changed = True
    while changed:
        changed = False
        for old_agent, entry in all_entries:
            if not old_agent or not entry:
                continue
            ack = entry.get("ack") or {}
            replacement = ack.get("replacement_agent")
            if replacement in chain and old_agent not in chain:
                chain.add(old_agent)
                changed = True
    return chain


def disqualified_reviewers(
    conn: sqlite3.Connection,
    task_id: str,
    *,
    master_path: Path = DEFAULT_CONTINUITY_MD,
) -> set[str]:
    """Agent identities that must not review task_id: the submission author
    and every identity in that author's rotation lineage (predecessors and
    replacements alike)."""
    author = get_submission_author(conn, task_id)
    if not author:
        return set()
    return rotation_chain(author, master_path=master_path)


def needs_reviewer(conn: sqlite3.Connection, task_id: str) -> bool:
    """True if task_id has no live, unexpired review claim."""
    db_path = _db_path_of(conn)
    return get_open_review_claim(task_id, db_path=db_path) is None


def _db_path_of(conn: sqlite3.Connection) -> str:
    """SQLite has no public API for a connection's source path; extract it
    from PRAGMA database_list, which every sqlite3.Connection supports."""
    row = conn.execute("PRAGMA database_list").fetchone()
    return row[2]


def eligible_reviewer(
    conn: sqlite3.Connection,
    task_id: str,
    live_agents: set[str],
    *,
    master_path: Path = DEFAULT_CONTINUITY_MD,
) -> str | None:
    """Return one live agent eligible to review task_id, or None if every
    live agent is disqualified (author or author's lineage) -- the caller
    should escalate to the operator in that case rather than spawn a
    compromised reviewer."""
    disqualified = disqualified_reviewers(conn, task_id, master_path=master_path)
    candidates = sorted(live_agents - disqualified)
    return candidates[0] if candidates else None


def main() -> int:
    import argparse
    import json

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task_id")
    parser.add_argument("--db", type=Path, default=ROOT / "map.db")
    parser.add_argument("--continuity-md", type=Path, default=DEFAULT_CONTINUITY_MD)
    parser.add_argument("--live-agent", action="append", default=[], dest="live_agents")
    args = parser.parse_args()

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row
    result = {
        "task_id": args.task_id,
        "needs_reviewer": needs_reviewer(conn, args.task_id),
        "disqualified": sorted(disqualified_reviewers(conn, args.task_id, master_path=args.continuity_md)),
    }
    if args.live_agents:
        result["eligible_reviewer"] = eligible_reviewer(
            conn, args.task_id, set(args.live_agents), master_path=args.continuity_md
        )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
