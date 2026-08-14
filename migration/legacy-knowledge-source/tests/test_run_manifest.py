#!/usr/bin/env python3
"""Focused regressions for TASK-281 run manifests."""

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

from MAP_System.scripts.run_manifest import (
    UsageError,
    check_stale,
    compute_task_revision,
    connect,
    create_manifest,
    get_manifest,
)


def init_db(path: Path, *, task_id: str = "TASK-A", role: str = "implementer") -> None:
    with sqlite3.connect(path) as conn:
        conn.executescript(SCHEMA.read_text(encoding="utf-8"))
        conn.execute(
            "INSERT INTO agents (agent_id, label, agent_type, status) VALUES "
            "('worker-a', 'Worker A', 'core', 'available')"
        )
        conn.execute(
            """
            INSERT INTO tasks
              (task_id, project_id, title, description, task_type, role, status,
               owner, attempt, max_attempts)
            VALUES (?, 'TEST', 'Manifest fixture', 'fixture task', 'implementation',
                    ?, 'IN_PROGRESS', 'worker-a', 1, 3)
            """,
            (task_id, role),
        )
        conn.execute(
            "INSERT INTO task_output_paths (task_id, path) VALUES (?, 'out/example.txt')",
            (task_id,),
        )
        conn.execute(
            "INSERT INTO task_acceptance_criteria (task_id, criterion) VALUES (?, 'works')",
            (task_id,),
        )


def test_manifest_records_all_required_fields() -> None:
    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)
        db = temp / "map.db"
        init_db(db)
        manifest = create_manifest(
            task_id="TASK-A", worker_id="worker-a", created_by="worker-a",
            session_id="session-1", skills=["python", "sqlite"],
            context_paths=[], writable_paths=["out/example.txt"],
            max_attempts=3, max_tool_failures=5, runtime_seconds=600,
            base_revision=None, db_path=db,
        )
        assert manifest["run_id"] == "RUN-TASK-A-01"
        assert manifest["task_id"] == "TASK-A"
        assert manifest["worker_id"] == "worker-a"
        assert manifest["session_id"] == "session-1"
        assert manifest["role_id"] == "delivery-implementer"
        assert manifest["role_source"] in {"canonical", "compatibility"}
        assert manifest["skills"] == ["python", "sqlite"]
        assert manifest["writable_scope"] == ["out/example.txt"]
        assert manifest["runtime_limits"] == {
            "max_attempts": 3, "max_tool_failures": 5, "runtime_seconds": 600,
        }
        assert manifest["base_revision"] is None
        assert manifest["created_by"] == "worker-a"
        assert manifest["created_at"]


def test_context_stored_as_reference_and_hash_not_copy() -> None:
    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)
        db = temp / "map.db"
        init_db(db)
        # Use a real repo file as the context reference so the resolved path
        # is inside REPO, matching how create_manifest resolves paths.
        real_context = "MAP_System/tests/test_run_manifest.py"
        manifest = create_manifest(
            task_id="TASK-A", worker_id="worker-a", created_by="worker-a",
            context_paths=[real_context], db_path=db,
        )
        assert len(manifest["context_refs"]) == 1
        ref = manifest["context_refs"][0]
        assert ref["path"] == real_context
        assert len(ref["sha256"]) == 64
        assert "content" not in ref
        with sqlite3.connect(db) as conn:
            columns = {row[1] for row in conn.execute("PRAGMA table_info(run_manifest_context_refs)")}
        assert "content" not in columns
        assert {"path", "sha256"} <= columns


def test_document_only_task_does_not_require_base_revision() -> None:
    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)
        db = temp / "map.db"
        init_db(db, task_id="TASK-DOC")
        manifest = create_manifest(
            task_id="TASK-DOC", worker_id="worker-a", created_by="worker-a",
            base_revision=None, db_path=db,
        )
        assert manifest["base_revision"] is None


def test_git_backed_task_records_base_revision() -> None:
    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)
        db = temp / "map.db"
        init_db(db, task_id="TASK-GIT")
        manifest = create_manifest(
            task_id="TASK-GIT", worker_id="worker-a", created_by="worker-a",
            base_revision="abc123def456", db_path=db,
        )
        assert manifest["base_revision"] == "abc123def456"


def test_run_id_unique_and_increments_per_task() -> None:
    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)
        db = temp / "map.db"
        init_db(db)
        first = create_manifest(task_id="TASK-A", worker_id="worker-a", created_by="worker-a", db_path=db)
        second = create_manifest(task_id="TASK-A", worker_id="worker-a", created_by="worker-a", db_path=db)
        assert first["run_id"] == "RUN-TASK-A-01"
        assert second["run_id"] == "RUN-TASK-A-02"
        assert first["run_id"] != second["run_id"]


def test_reviewer_can_reproduce_exact_revision_from_run_id() -> None:
    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)
        db = temp / "map.db"
        init_db(db)
        real_context = "MAP_System/tests/test_run_manifest.py"
        manifest = create_manifest(
            task_id="TASK-A", worker_id="worker-a", created_by="worker-a",
            context_paths=[real_context], db_path=db,
        )
        fetched = get_manifest(manifest["run_id"], db_path=db)
        assert fetched == manifest
        with connect(db) as conn:
            recomputed = compute_task_revision(conn, "TASK-A")
        assert recomputed == manifest["task_revision"]


def test_check_stale_detects_task_definition_change() -> None:
    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)
        db = temp / "map.db"
        init_db(db)
        manifest = create_manifest(task_id="TASK-A", worker_id="worker-a", created_by="worker-a", db_path=db)
        result = check_stale(manifest["run_id"], db_path=db)
        assert result["task_stale"] is False
        assert result["stale_context"] == []

        with sqlite3.connect(db) as conn:
            conn.execute("UPDATE tasks SET description='changed after dispatch' WHERE task_id='TASK-A'")

        result = check_stale(manifest["run_id"], db_path=db)
        assert result["task_stale"] is True
        assert result["current_task_revision"] != result["recorded_task_revision"]


def test_check_stale_ignores_lifecycle_field_churn() -> None:
    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)
        db = temp / "map.db"
        init_db(db)
        manifest = create_manifest(task_id="TASK-A", worker_id="worker-a", created_by="worker-a", db_path=db)
        with sqlite3.connect(db) as conn:
            conn.execute(
                "UPDATE tasks SET status='SUBMITTED', attempt=2, heartbeat_at=datetime('now') "
                "WHERE task_id='TASK-A'"
            )
        result = check_stale(manifest["run_id"], db_path=db)
        assert result["task_stale"] is False


def test_check_stale_detects_context_file_change() -> None:
    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)
        db = temp / "map.db"
        init_db(db)
        scratch_context = REPO / "MAP_System" / "artifacts" / "experiments" / "._task281_stale_probe.txt"
        scratch_context.write_text("original", encoding="utf-8")
        try:
            rel = str(scratch_context.relative_to(REPO))
            manifest = create_manifest(
                task_id="TASK-A", worker_id="worker-a", created_by="worker-a",
                context_paths=[rel], db_path=db,
            )
            result = check_stale(manifest["run_id"], db_path=db)
            assert result["stale_context"] == []

            scratch_context.write_text("mutated", encoding="utf-8")
            result = check_stale(manifest["run_id"], db_path=db)
            assert len(result["stale_context"]) == 1
            assert result["stale_context"][0]["path"] == rel
            assert result["stale_context"][0]["reason"] == "changed"
        finally:
            scratch_context.unlink(missing_ok=True)


def test_unknown_worker_is_rejected_without_mutation() -> None:
    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)
        db = temp / "map.db"
        init_db(db)
        try:
            create_manifest(task_id="TASK-A", worker_id="ghost-worker", created_by="worker-a", db_path=db)
        except UsageError as exc:
            assert "unknown worker" in str(exc)
        else:
            raise AssertionError("unknown worker must be rejected")
        with sqlite3.connect(db) as conn:
            assert conn.execute("SELECT count(*) FROM run_manifests").fetchone()[0] == 0


def main() -> int:
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_")]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"{len(tests)} run-manifest tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
