#!/usr/bin/env python3
"""Focused regressions for TASK-283 scope contracts and retry budgets."""

from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
SCHEMA = ROOT / "migration" / "schema.sql"

if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from MAP_System.scripts.pre_dispatch_policy import evaluate_pre_dispatch, scope_contract_issues
from MAP_System.scripts.run_manifest import UsageError, connect, create_manifest
from MAP_System.scripts.verify_run_scope import (
    check_budget,
    load_scope_policy,
    validate_scope_contract,
    verify_post_run_diff,
    write_escalation_artifact,
)


# --- validate_scope_contract -------------------------------------------------


def test_valid_contract_has_no_issues() -> None:
    issues = validate_scope_contract(
        readable=["."], writable=["MAP_System/scripts/example.py"], forbidden=[".git"],
    )
    assert issues == []


def test_overlapping_writable_and_forbidden_is_rejected() -> None:
    issues = validate_scope_contract(
        readable=["."], writable=["MAP_System/map.db"], forbidden=["MAP_System/map.db"],
    )
    assert any("overlaps forbidden" in issue for issue in issues)


def test_writable_inside_a_forbidden_directory_is_rejected() -> None:
    issues = validate_scope_contract(
        readable=["."], writable=["MAP_System/.venv/lib/thing.py"], forbidden=["MAP_System/.venv"],
    )
    assert any("overlaps forbidden" in issue for issue in issues)


def test_forbidden_directory_containing_writable_is_also_rejected() -> None:
    # Overlap is symmetric: a forbidden path that is a *parent* of a
    # writable path is exactly as invalid as the reverse.
    issues = validate_scope_contract(
        readable=["."], writable=["MAP_System"], forbidden=["MAP_System/map.db"],
    )
    assert any("overlaps forbidden" in issue for issue in issues)


def test_path_escaping_repo_is_rejected() -> None:
    issues = validate_scope_contract(readable=["."], writable=["../outside-repo.txt"], forbidden=[])
    assert any("escapes the repository" in issue for issue in issues)


def test_empty_path_is_rejected() -> None:
    issues = validate_scope_contract(readable=["."], writable=[""], forbidden=[])
    assert any("empty" in issue for issue in issues)


def test_writable_not_covered_by_readable_is_rejected() -> None:
    issues = validate_scope_contract(
        readable=["MAP_System/notes"], writable=["MAP_System/scripts/example.py"], forbidden=[],
    )
    assert any("not covered by any declared readable path" in issue for issue in issues)


def test_no_declared_contract_fields_is_trivially_valid() -> None:
    assert validate_scope_contract() == []


# --- pre_dispatch_policy.py integration --------------------------------------


def test_task_without_scope_contract_is_unaffected() -> None:
    task = {"task_id": "TASK-A", "task_type": "implementation", "role": "implementer"}
    assert scope_contract_issues(task) == []
    result = evaluate_pre_dispatch(task, "core-agent", worker_tier=1)
    assert "REJECT_INVALID_SCOPE_CONTRACT" not in result["reasons"]


def test_task_with_valid_scope_contract_passes_through_normally() -> None:
    task = {
        "task_id": "TASK-A", "task_type": "implementation", "role": "implementer",
        "scope_contract": {
            "readable": ["."], "writable": ["MAP_System/scripts/example.py"], "forbidden": [".git"],
        },
    }
    result = evaluate_pre_dispatch(task, "core-agent", worker_tier=1)
    assert "REJECT_INVALID_SCOPE_CONTRACT" not in result["reasons"]
    assert result["decision"] == "allow"


def test_task_with_invalid_scope_contract_is_rejected_regardless_of_tier() -> None:
    task = {
        "task_id": "TASK-A", "task_type": "implementation", "role": "implementer",
        "scope_contract": {
            "readable": ["."], "writable": ["MAP_System/map.db"], "forbidden": ["MAP_System/map.db"],
        },
    }
    for worker, tier in (("core-agent", 1), ("helper-review-01", 2), ("local-model", 3)):
        result = evaluate_pre_dispatch(task, worker, worker_tier=tier)
        assert result["decision"] == "reject", (worker, tier, result)
        assert "REJECT_INVALID_SCOPE_CONTRACT" in result["reasons"]


def test_command_center_tier_bypasses_scope_contract_check() -> None:
    # Tier 0 (command-center/the human operator) is allowed unconditionally,
    # same as every other pre-existing check in this file -- an invalid
    # contract on a task the operator is directly running is not this
    # module's business to block.
    task = {
        "task_id": "TASK-A", "task_type": "implementation", "role": "implementer",
        "scope_contract": {"writable": ["MAP_System/map.db"], "forbidden": ["MAP_System/map.db"]},
    }
    result = evaluate_pre_dispatch(task, "command-center", worker_tier=0)
    assert result["decision"] == "allow"


# --- verify_post_run_diff ----------------------------------------------------


def test_post_run_diff_detects_out_of_scope_write() -> None:
    result = verify_post_run_diff(
        writable=["MAP_System/scripts/example.py"], forbidden=[],
        changed_paths=["MAP_System/scripts/example.py", "MAP_System/notes/unexpected.md"],
    )
    assert result["ok"] is False
    assert result["out_of_scope_writes"] == ["MAP_System/notes/unexpected.md"]
    assert result["forbidden_writes"] == []


def test_post_run_diff_detects_forbidden_write() -> None:
    result = verify_post_run_diff(
        writable=["MAP_System"], forbidden=["MAP_System/map.db"],
        changed_paths=["MAP_System/scripts/example.py", "MAP_System/map.db"],
    )
    assert result["ok"] is False
    assert result["forbidden_writes"] == ["MAP_System/map.db"]


def test_post_run_diff_clean_when_all_changes_are_writable() -> None:
    result = verify_post_run_diff(
        writable=["MAP_System/scripts"], forbidden=[".git"],
        changed_paths=["MAP_System/scripts/a.py", "MAP_System/scripts/b.py"],
    )
    assert result == {
        "ok": True, "out_of_scope_writes": [], "forbidden_writes": [], "checked_paths": 2,
    }


# --- check_budget / write_escalation_artifact --------------------------------


def test_check_budget_returns_none_when_within_limits() -> None:
    limits = {"max_attempts": 3, "max_tool_failures": 20, "runtime_seconds": 7200}
    assert check_budget(
        runtime_limits=limits, actual_attempts=1, actual_tool_failures=2, actual_runtime_seconds=60,
    ) is None


def test_check_budget_detects_exhaustion() -> None:
    limits = {"max_attempts": 3}
    record = check_budget(runtime_limits=limits, actual_attempts=3)
    assert record is not None
    assert record["kind"] == "budget_exhaustion"
    assert record["exceeded"][0]["metric"] == "max_attempts"
    assert record["exceeded"][0]["actual"] == 3


def test_check_budget_ignores_undeclared_limits() -> None:
    # A limit never declared in runtime_limits is not enforced -- mirrors
    # run_manifest.py's own convention of only recording explicitly
    # supplied limits.
    assert check_budget(runtime_limits={}, actual_attempts=999) is None


def test_write_escalation_artifact_is_durable_and_self_describing() -> None:
    with tempfile.TemporaryDirectory() as td:
        out_dir = Path(td) / "escalations"
        record = {"kind": "budget_exhaustion", "exceeded": [{"metric": "max_attempts", "limit": 3, "actual": 3}]}
        path = write_escalation_artifact(record, task_id="TASK-A", run_id="RUN-TASK-A-01", out_dir=out_dir)
        assert path.is_file()
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["task_id"] == "TASK-A"
        assert payload["run_id"] == "RUN-TASK-A-01"
        assert payload["kind"] == "budget_exhaustion"
        assert payload["created_at"]


# --- load_scope_policy --------------------------------------------------------


def test_load_scope_policy_reads_the_real_runtime_policy_yaml() -> None:
    policy = load_scope_policy()
    assert policy.get("version") == 1
    assert "." in policy.get("default_readable_paths", [])
    assert ".git" in policy.get("default_forbidden_paths", [])
    assert "tier1_core_agent" in policy.get("retry_budgets", {})
    assert policy.get("containment_level") != "harness_enforced"


def test_load_scope_policy_returns_empty_for_missing_file() -> None:
    assert load_scope_policy(Path("/nonexistent/runtime_policy.yaml")) == {}


# --- run_manifest.py integration (readable/writable/forbidden + migration) --


def _seed_task(conn: sqlite3.Connection, task_id: str = "TASK-A") -> None:
    conn.execute(
        "INSERT INTO agents (agent_id, label, agent_type, status) VALUES ('worker-a', 'W', 'core', 'available')"
    )
    conn.execute(
        """
        INSERT INTO tasks
          (task_id, project_id, title, description, task_type, role, status,
           owner, attempt, max_attempts)
        VALUES (?, 'TEST', 'Scope fixture', 'fixture', 'implementation',
                'implementer', 'IN_PROGRESS', 'worker-a', 1, 3)
        """,
        (task_id,),
    )
    conn.execute(
        "INSERT INTO task_output_paths (task_id, path) VALUES (?, 'out/example.txt')", (task_id,)
    )
    conn.execute(
        "INSERT INTO task_acceptance_criteria (task_id, criterion) VALUES (?, 'works')", (task_id,)
    )


def test_manifest_records_readable_writable_and_forbidden_scope() -> None:
    with tempfile.TemporaryDirectory() as td:
        db = Path(td) / "map.db"
        with sqlite3.connect(db) as conn:
            conn.executescript(SCHEMA.read_text(encoding="utf-8"))
            _seed_task(conn)
        manifest = create_manifest(
            task_id="TASK-A", worker_id="worker-a", created_by="worker-a",
            readable_paths=["."], writable_paths=["out/example.txt"],
            forbidden_paths=[".git"], db_path=db,
        )
        assert manifest["readable_scope"] == ["."]
        assert manifest["writable_scope"] == ["out/example.txt"]
        assert manifest["forbidden_scope"] == [".git"]


def test_manifest_creation_rejects_invalid_scope_contract() -> None:
    with tempfile.TemporaryDirectory() as td:
        db = Path(td) / "map.db"
        with sqlite3.connect(db) as conn:
            conn.executescript(SCHEMA.read_text(encoding="utf-8"))
            _seed_task(conn)
        try:
            create_manifest(
                task_id="TASK-A", worker_id="worker-a", created_by="worker-a",
                writable_paths=["out/example.txt"], forbidden_paths=["out/example.txt"],
                db_path=db,
            )
        except UsageError as exc:
            assert "scope contract is invalid" in str(exc)
        else:
            raise AssertionError("an overlapping writable/forbidden contract must be rejected")
        with sqlite3.connect(db) as conn:
            assert conn.execute("SELECT count(*) FROM run_manifests").fetchone()[0] == 0


def test_manifest_scope_defaults_when_not_supplied() -> None:
    with tempfile.TemporaryDirectory() as td:
        db = Path(td) / "map.db"
        with sqlite3.connect(db) as conn:
            conn.executescript(SCHEMA.read_text(encoding="utf-8"))
            _seed_task(conn)
        manifest = create_manifest(task_id="TASK-A", worker_id="worker-a", created_by="worker-a", db_path=db)
        assert manifest["readable_scope"] == ["."]
        assert manifest["forbidden_scope"] == []
        # writable defaults to the task's own registered output paths (TASK-281 behavior, unchanged).
        assert manifest["writable_scope"] == ["out/example.txt"]


def test_pre_existing_run_manifests_table_migrates_additive_columns() -> None:
    """A database with TASK-281's original (pre-TASK-283) schema must gain
    the two new columns via ALTER TABLE, without losing existing rows."""
    with tempfile.TemporaryDirectory() as td:
        db = Path(td) / "map.db"
        with sqlite3.connect(db) as conn:
            conn.executescript(SCHEMA.read_text(encoding="utf-8"))
            _seed_task(conn)
            # Simulate the original TASK-281 schema: no readable_scope/forbidden_scope.
            conn.execute(
                """
                CREATE TABLE run_manifests (
                    run_id TEXT PRIMARY KEY, task_id TEXT NOT NULL, task_revision TEXT NOT NULL,
                    worker_id TEXT NOT NULL, session_id TEXT, role_id TEXT NOT NULL,
                    role_source TEXT NOT NULL, writable_scope TEXT NOT NULL DEFAULT '[]',
                    runtime_limits TEXT NOT NULL DEFAULT '{}', base_revision TEXT,
                    created_by TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
                )
                """
            )
            conn.execute(
                """
                INSERT INTO run_manifests
                    (run_id, task_id, task_revision, worker_id, role_id, role_source,
                     writable_scope, created_by, created_at)
                VALUES ('RUN-TASK-A-01', 'TASK-A', 'abc', 'worker-a', 'delivery-implementer',
                        'canonical', '["out/example.txt"]', 'worker-a', '2026-07-26T00:00:00Z')
                """
            )
            conn.commit()

        # connect() must migrate this pre-existing table without error.
        with connect(db) as conn:
            columns = {row["name"] for row in conn.execute("PRAGMA table_info(run_manifests)")}
        assert {"readable_scope", "forbidden_scope"} <= columns

        # The pre-existing row survives with sane defaults for the new columns.
        from MAP_System.scripts.run_manifest import get_manifest
        migrated = get_manifest("RUN-TASK-A-01", db_path=db)
        assert migrated["writable_scope"] == ["out/example.txt"]
        assert migrated["readable_scope"] == []
        assert migrated["forbidden_scope"] == []

        # And a fresh manifest can still be created against the migrated table.
        second = create_manifest(task_id="TASK-A", worker_id="worker-a", created_by="worker-a", db_path=db)
        assert second["run_id"] == "RUN-TASK-A-02"
        assert second["readable_scope"] == ["."]


def main() -> int:
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_")]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"{len(tests)} run-scope tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
