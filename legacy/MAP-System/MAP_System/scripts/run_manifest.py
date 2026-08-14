#!/usr/bin/env python3
"""TASK-281 bounded pilot: immutable run manifests.

Binds one immutable task revision to a unique run ID at dispatch time and
records the run's execution context by reference (path + sha256), never by
copying full source content. See
`MAP_System/artifacts/experiments/task281-run-manifest-pilot.md` for the
pilot comparison against EXP-0005 and the explicit non-production-rollout
scope.

Usage:
    python3 MAP_System/scripts/run_manifest.py create \\
        --task-id TASK-NNN --worker-id <agent> [--session-id <id>] \\
        [--skill <name> ...] [--context <repo-relative-path> ...] \\
        [--writable-path <repo-relative-path> ...] \\
        [--max-attempts N] [--max-tool-failures N] [--runtime-seconds N] \\
        [--base-revision <sha>]

    python3 MAP_System/scripts/run_manifest.py show <run_id>
    python3 MAP_System/scripts/run_manifest.py check-stale <run_id>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from MAP_System.scripts.validate_task_schema import load_role_registry, normalize_role  # noqa: E402
from MAP_System.scripts.verify_run_scope import validate_scope_contract  # noqa: E402

DEFAULT_DB = ROOT / "map.db"
SCHEMA = ROOT / "migration" / "run_manifest_schema.sql"


class UsageError(RuntimeError):
    pass


# TASK-283 added these two columns after some databases (including the
# canonical map.db) already had a run_manifests table from TASK-281.
# CREATE TABLE IF NOT EXISTS never adds columns to an existing table, so a
# guarded ALTER TABLE migration is required for those pre-existing rows.
_ADDITIVE_COLUMNS = (
    ("readable_scope", "TEXT NOT NULL DEFAULT '[]'"),
    ("forbidden_scope", "TEXT NOT NULL DEFAULT '[]'"),
)


def connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA.read_text(encoding="utf-8"))
    existing_columns = {row["name"] for row in conn.execute("PRAGMA table_info(run_manifests)")}
    for column, definition in _ADDITIVE_COLUMNS:
        if column not in existing_columns:
            conn.execute(f"ALTER TABLE run_manifests ADD COLUMN {column} {definition}")
    return conn


def _canonical_task_row(conn: sqlite3.Connection, task_id: str) -> dict[str, Any]:
    row = conn.execute(
        """
        SELECT task_id, title, description, task_type, role
        FROM tasks WHERE task_id = ?
        """,
        (task_id,),
    ).fetchone()
    if row is None:
        raise UsageError(f"unknown task: {task_id}")
    dependencies = sorted(
        r[0] for r in conn.execute(
            "SELECT depends_on FROM task_dependencies WHERE task_id = ?", (task_id,)
        )
    )
    output_paths = sorted(
        r[0] for r in conn.execute(
            "SELECT path FROM task_output_paths WHERE task_id = ?", (task_id,)
        )
    )
    acceptance_criteria = sorted(
        r[0] for r in conn.execute(
            "SELECT criterion FROM task_acceptance_criteria WHERE task_id = ?", (task_id,)
        )
    )
    return {
        "task_id": row["task_id"],
        "title": row["title"],
        "description": row["description"],
        "task_type": row["task_type"],
        "role": row["role"],
        "dependencies": dependencies,
        "output_paths": output_paths,
        "acceptance_criteria": acceptance_criteria,
    }


def compute_task_revision(conn: sqlite3.Connection, task_id: str) -> str:
    """Content hash of the task's stable definition fields.

    Deliberately excludes lifecycle fields (status, owner, claimed_by,
    lease, attempt, timestamps) so claim/heartbeat churn does not manufacture
    false staleness; a revision changes only when the task's actual
    definition changes.
    """
    canonical = _canonical_task_row(conn, task_id)
    blob = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def hash_file(path: Path) -> str:
    if not path.is_file():
        raise UsageError(f"context reference is not a file: {path}")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _next_run_id(conn: sqlite3.Connection, task_id: str) -> str:
    count = conn.execute(
        "SELECT count(*) FROM run_manifests WHERE task_id = ?", (task_id,)
    ).fetchone()[0]
    return f"RUN-{task_id}-{count + 1:02d}"


def create_manifest(
    *,
    task_id: str,
    worker_id: str,
    created_by: str,
    session_id: str | None = None,
    skills: list[str] | None = None,
    context_paths: list[str] | None = None,
    readable_paths: list[str] | None = None,
    writable_paths: list[str] | None = None,
    forbidden_paths: list[str] | None = None,
    max_attempts: int | None = None,
    max_tool_failures: int | None = None,
    runtime_seconds: int | None = None,
    base_revision: str | None = None,
    db_path: Path = DEFAULT_DB,
) -> dict[str, Any]:
    """Create one immutable run manifest and return its stored record."""
    with connect(db_path) as conn:
        task = _canonical_task_row(conn, task_id)
        if not conn.execute("SELECT 1 FROM agents WHERE agent_id = ?", (worker_id,)).fetchone():
            raise UsageError(f"unknown worker agent: {worker_id}")
        role_id, role_source = normalize_role(task["role"], load_role_registry())
        if role_id is None:
            raise UsageError(
                f"{task_id} has an unrecognized role {task['role']!r}; cannot "
                "bind a run manifest to an unnormalized role"
            )
        task_revision = compute_task_revision(conn, task_id)

        writable = sorted(set(writable_paths)) if writable_paths else task["output_paths"]
        readable = sorted(set(readable_paths)) if readable_paths else ["."]
        forbidden = sorted(set(forbidden_paths)) if forbidden_paths else []
        # Dispatch-preflight check (TASK-283): a self-inconsistent scope
        # contract must never be bound to a run, regardless of who the
        # worker is. This proves internal consistency only -- it cannot
        # prove the worker will honor the contract; see verify_run_scope.py.
        contract_issues = validate_scope_contract(
            readable=readable, writable=writable, forbidden=forbidden,
        )
        if contract_issues:
            raise UsageError(
                f"{task_id} scope contract is invalid: {'; '.join(contract_issues)}"
            )
        limits = {}
        if max_attempts is not None:
            limits["max_attempts"] = max_attempts
        if max_tool_failures is not None:
            limits["max_tool_failures"] = max_tool_failures
        if runtime_seconds is not None:
            limits["runtime_seconds"] = runtime_seconds

        context_refs = []
        for raw_path in context_paths or []:
            full = (REPO / raw_path).resolve()
            context_refs.append({"path": raw_path, "sha256": hash_file(full)})

        run_id = _next_run_id(conn, task_id)
        conn.execute(
            """
            INSERT INTO run_manifests
                (run_id, task_id, task_revision, worker_id, session_id,
                 role_id, role_source, readable_scope, writable_scope,
                 forbidden_scope, runtime_limits, base_revision, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id, task_id, task_revision, worker_id, session_id,
                role_id, role_source,
                json.dumps(readable, separators=(",", ":")),
                json.dumps(writable, separators=(",", ":")),
                json.dumps(forbidden, separators=(",", ":")),
                json.dumps(limits, sort_keys=True, separators=(",", ":")),
                base_revision, created_by,
            ),
        )
        for skill in sorted(set(skills or [])):
            conn.execute(
                "INSERT INTO run_manifest_skills (run_id, skill) VALUES (?, ?)",
                (run_id, skill),
            )
        for ref in context_refs:
            conn.execute(
                "INSERT INTO run_manifest_context_refs (run_id, path, sha256) VALUES (?, ?, ?)",
                (run_id, ref["path"], ref["sha256"]),
            )
        conn.commit()
        return get_manifest(run_id, db_path=db_path)


def get_manifest(run_id: str, *, db_path: Path = DEFAULT_DB) -> dict[str, Any]:
    with connect(db_path) as conn:
        row = conn.execute("SELECT * FROM run_manifests WHERE run_id = ?", (run_id,)).fetchone()
        if row is None:
            raise UsageError(f"unknown run: {run_id}")
        skills = sorted(
            r[0] for r in conn.execute(
                "SELECT skill FROM run_manifest_skills WHERE run_id = ?", (run_id,)
            )
        )
        context_refs = [
            {"path": r["path"], "sha256": r["sha256"]}
            for r in conn.execute(
                "SELECT path, sha256 FROM run_manifest_context_refs WHERE run_id = ? ORDER BY path",
                (run_id,),
            )
        ]
        record = dict(row)
        record["readable_scope"] = json.loads(record["readable_scope"])
        record["writable_scope"] = json.loads(record["writable_scope"])
        record["forbidden_scope"] = json.loads(record["forbidden_scope"])
        record["runtime_limits"] = json.loads(record["runtime_limits"])
        record["skills"] = skills
        record["context_refs"] = context_refs
        return record


def check_stale(run_id: str, *, db_path: Path = DEFAULT_DB) -> dict[str, Any]:
    """Compare a stored manifest against live task/context state.

    Returns which parts of the run's recorded context have since changed --
    the reproducibility check acceptance criterion 3 requires.
    """
    manifest = get_manifest(run_id, db_path=db_path)
    with connect(db_path) as conn:
        try:
            current_task_revision = compute_task_revision(conn, manifest["task_id"])
            task_missing = False
        except UsageError:
            current_task_revision = None
            task_missing = True

    stale_context = []
    for ref in manifest["context_refs"]:
        full = (REPO / ref["path"]).resolve()
        if not full.is_file():
            stale_context.append({"path": ref["path"], "reason": "missing"})
            continue
        current_hash = hash_file(full)
        if current_hash != ref["sha256"]:
            stale_context.append({
                "path": ref["path"], "reason": "changed",
                "recorded_sha256": ref["sha256"], "current_sha256": current_hash,
            })

    return {
        "run_id": run_id,
        "task_id": manifest["task_id"],
        "task_missing": task_missing,
        "task_stale": (not task_missing) and current_task_revision != manifest["task_revision"],
        "recorded_task_revision": manifest["task_revision"],
        "current_task_revision": current_task_revision,
        "stale_context": stale_context,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create")
    create.add_argument("--task-id", required=True)
    create.add_argument("--worker-id", required=True)
    create.add_argument("--created-by")
    create.add_argument("--session-id")
    create.add_argument("--skill", action="append", default=[], dest="skills")
    create.add_argument("--context", action="append", default=[], dest="context_paths")
    create.add_argument("--readable-path", action="append", default=[], dest="readable_paths")
    create.add_argument("--writable-path", action="append", default=[], dest="writable_paths")
    create.add_argument("--forbidden-path", action="append", default=[], dest="forbidden_paths")
    create.add_argument("--max-attempts", type=int)
    create.add_argument("--max-tool-failures", type=int)
    create.add_argument("--runtime-seconds", type=int)
    create.add_argument("--base-revision")

    show = subparsers.add_parser("show")
    show.add_argument("run_id")

    stale = subparsers.add_parser("check-stale")
    stale.add_argument("run_id")

    args = parser.parse_args(argv)

    try:
        if args.command == "create":
            record = create_manifest(
                task_id=args.task_id,
                worker_id=args.worker_id,
                created_by=args.created_by or args.worker_id,
                session_id=args.session_id,
                skills=args.skills,
                context_paths=args.context_paths,
                readable_paths=args.readable_paths or None,
                writable_paths=args.writable_paths or None,
                forbidden_paths=args.forbidden_paths or None,
                max_attempts=args.max_attempts,
                max_tool_failures=args.max_tool_failures,
                runtime_seconds=args.runtime_seconds,
                base_revision=args.base_revision,
                db_path=args.db,
            )
            print(json.dumps(record, separators=(",", ":")))
        elif args.command == "show":
            print(json.dumps(get_manifest(args.run_id, db_path=args.db), separators=(",", ":")))
        elif args.command == "check-stale":
            result = check_stale(args.run_id, db_path=args.db)
            print(json.dumps(result, separators=(",", ":")))
            if result["task_stale"] or result["task_missing"] or result["stale_context"]:
                return 1
        return 0
    except UsageError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
