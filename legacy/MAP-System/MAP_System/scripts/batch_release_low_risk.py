#!/usr/bin/env python3
"""Batch-release APPROVED tasks that classify as low-risk (TASK-288/DEC-032).

Iterates every APPROVED task, runs the same classify_release() rule
scripts/release_task.py uses, and releases the ones that classify "low"
(no shared/templates/canonical output path, no SECURITY/STRUCTURAL/BLOCKING/
policy-tier signal) by auto-generating the minimal low-risk checklist. Tasks
that classify "full" are left untouched and reported for manual release with
a real, hand-written checklist -- this script never invents shared-file,
decisions, or follow-up claims it cannot verify.

Usage:
    MAP_System/.venv/bin/python3 MAP_System/scripts/batch_release_low_risk.py \
        --released-by lili-replacement-nisa [--dry-run]
"""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT.parent) not in sys.path:
    sys.path.insert(0, str(ROOT.parent))

from MAP_System.scripts.release_task import (  # noqa: E402
    DEFAULT_DB,
    EVENT_LOG,
    ReleaseError,
    classify_release,
    connect,
    ensure_schema,
    release_task,
)

CHECKLIST_DIR = ROOT / "artifacts" / "releases"

LOW_RISK_TEMPLATE = """\
# Release Checklist: {task_id}

## Header

```
task_id:      {task_id}
released_by:  {released_by}
release_date: {release_date}
```

## Checklist

- [x] Emergence capture considered

## Summary

Batch release under TASK-288/DEC-032 backlog clearance (release-tier
reconciliation, see CHANGE_CONTROL_SYSTEM.md's Release tier section).
Low-risk tier: {tier_reason}. No shared/templates/canonical output path is
touched by this task, so shared-file updates, decisions-recorded, and
follow-up-tasks-created do not apply. Emergence: no additional signal
identified beyond what the task's own independent review already covered;
this batch pass is administrative release paperwork, not a fresh review.

Original task: {title}
"""


def find_approved_tasks(db_path: Path) -> list[str]:
    with connect(db_path) as conn:
        ensure_schema(conn)
        rows = conn.execute(
            "SELECT task_id FROM tasks WHERE status = 'APPROVED' ORDER BY task_id"
        ).fetchall()
    return [row["task_id"] for row in rows]


def task_title(db_path: Path, task_id: str) -> str:
    with connect(db_path) as conn:
        row = conn.execute("SELECT title FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
    return row["title"] if row else ""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--released-by", required=True)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--event-log", type=Path, default=EVENT_LOG)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Release at most this many low-risk tasks this run, so a batch can be split "
             "into smaller, individually-confirmable chunks.",
    )
    args = parser.parse_args()

    released: list[str] = []
    needs_manual: list[tuple[str, str]] = []
    errors: list[tuple[str, str]] = []
    skipped_over_limit: list[str] = []

    for task_id in find_approved_tasks(args.db):
        with connect(args.db) as conn:
            ensure_schema(conn)
            tier, reason = classify_release(conn, task_id)

        if tier != "low":
            needs_manual.append((task_id, reason))
            continue

        if args.limit is not None and len(released) >= args.limit:
            skipped_over_limit.append(task_id)
            continue

        if args.dry_run:
            released.append(task_id)
            continue

        checklist_path = CHECKLIST_DIR / f"{task_id.lower()}-release-checklist.md"
        if checklist_path.exists():
            errors.append((task_id, f"checklist already exists: {checklist_path}"))
            continue
        title = task_title(args.db, task_id)
        checklist_path.parent.mkdir(parents=True, exist_ok=True)
        checklist_path.write_text(
            LOW_RISK_TEMPLATE.format(
                task_id=task_id,
                released_by=args.released_by,
                release_date=date.today().isoformat(),
                tier_reason=reason,
                title=title,
            ),
            encoding="utf-8",
        )
        try:
            release_task(
                task_id,
                args.released_by,
                checklist_path,
                db_path=args.db,
                event_log=args.event_log,
                output_dir=args.output_dir,
                summary=f"Batch-released low-risk task under TASK-288/DEC-032: {title}",
            )
            released.append(task_id)
        except ReleaseError as exc:
            errors.append((task_id, str(exc)))

    verb = "would release" if args.dry_run else "released"
    print(f"{verb}: {len(released)} -> {', '.join(released) if released else '(none)'}")
    if skipped_over_limit:
        print(f"skipped (over --limit, still low-risk, re-run to continue): {len(skipped_over_limit)} -> {', '.join(skipped_over_limit)}")
    print(f"needs manual full checklist: {len(needs_manual)}")
    for task_id, reason in needs_manual:
        print(f"  {task_id}: {reason}")
    if errors:
        print(f"errors: {len(errors)}")
        for task_id, message in errors:
            print(f"  {task_id}: {message}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
