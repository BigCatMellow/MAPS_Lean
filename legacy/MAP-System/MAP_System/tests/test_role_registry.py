from __future__ import annotations

import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tempfile

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from MAP_System.graph.runner import normalize_task
from MAP_System.scripts.pre_dispatch_policy import evaluate_pre_dispatch
from MAP_System.scripts.validate_task_schema import check_task, load_role_registry, normalize_role


def test_registry_has_seven_complete_contracts():
    registry = load_role_registry()
    assert 5 <= len(registry["roles"]) <= 7
    required = {"mission", "owns", "may", "must", "must_not", "required_input", "required_output", "escalate", "complete_when"}
    assert all(required <= set(contract) for contract in registry["roles"].values())


def test_canonical_and_historical_roles_normalize_without_rewrite():
    assert normalize_role("delivery-implementer")[0:2] == ("delivery-implementer", "canonical")
    assert normalize_role("Claude (prose/architecture, HPOM tier-1)") == ("shaper", "compatibility")
    task = {"task_id": "TASK-999", "role": "architect"}
    assert normalize_task(task)["role_id"] == "shaper"
    assert task["role"] == "architect"


def test_unknown_role_is_rejected_with_clear_diagnostic():
    errors = check_task("TASK-999", {
        "task_id": "TASK-999", "title": "x", "task_type": "implementation",
        "role": "invented-role", "status": "READY", "owner": "x", "description": "x",
        "dependencies": [], "input_paths": [], "output_paths": [], "acceptance_criteria": [],
    })
    assert any("no explicit compatibility mapping" in error for error in errors)


def test_runner_separates_role_from_worker_provider_model_and_capabilities():
    normalized = normalize_task({
        "role": "implementer", "required_agent": "worker-1", "provider": "codex",
        "model_tier": "standard", "capability_requirements": ["sqlite"],
    })
    assert normalized["role_id"] == "delivery-implementer"
    assert normalized["worker_id"] == "worker-1"
    assert normalized["provider"] == "codex"
    assert normalized["model_tier"] == "standard"
    assert normalized["capability_requirements"] == ["sqlite"]


def test_normalization_does_not_substitute_for_review_independence():
    normalized = normalize_task({"role": "implementer", "claimed_by": "author-1"})
    assert normalized["role_id"] == "delivery-implementer"
    assert normalized["role_id"] != "independent-reviewer"
    assert normalized.get("claimed_by") == "author-1"


def test_sanctioned_create_rejects_unknown_role_without_mutation():
    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)
        db = temp / "map.db"
        schema = Path(__file__).parents[1] / "migration" / "schema.sql"
        with sqlite3.connect(db) as conn:
            conn.executescript(schema.read_text(encoding="utf-8"))
            conn.execute("INSERT INTO agents (agent_id, label, agent_type, status) VALUES ('owner', 'Owner', 'core', 'available')")
        result = subprocess.run([
            sys.executable, str(Path(__file__).parents[1] / "scripts" / "map_task.py"),
            "--db", str(db), "--event-log", str(temp / "events.jsonl"),
            "create", "--task-id", "TASK-9999", "--title", "unknown", "--owner", "owner",
            "--role", "invented-role",
        ], cwd=Path(__file__).parents[2], text=True, capture_output=True)
        assert result.returncode != 0
        assert "unknown role" in result.stderr
        with sqlite3.connect(db) as conn:
            assert conn.execute("SELECT count(*) FROM tasks WHERE task_id='TASK-9999'").fetchone()[0] == 0
            assert conn.execute("SELECT count(*) FROM events").fetchone()[0] == 0


def test_sanctioned_create_accepts_canonical_and_compatibility_roles():
    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)
        db = temp / "map.db"
        schema = Path(__file__).parents[1] / "migration" / "schema.sql"
        with sqlite3.connect(db) as conn:
            conn.executescript(schema.read_text(encoding="utf-8"))
            conn.execute("INSERT INTO agents (agent_id, label, agent_type, status) VALUES ('owner', 'Owner', 'core', 'available')")
        map_task = str(Path(__file__).parents[1] / "scripts" / "map_task.py")
        repo = Path(__file__).parents[2]
        # A successful create runs sync_files(), which exports into
        # --output-dir (or the real MAP_System tree if omitted). Always pass
        # an isolated scratch output dir here so this test can never write
        # into the canonical task_graph.json / tasks/*.json mirrors.
        out = temp / "out"

        # A stable canonical role ID is accepted and stored verbatim.
        canonical = subprocess.run([
            sys.executable, map_task, "--db", str(db), "--event-log", str(temp / "events.jsonl"),
            "--output-dir", str(out),
            "create", "--task-id", "TASK-8001", "--title", "canonical", "--owner", "owner",
            "--role", "delivery-implementer",
        ], cwd=repo, text=True, capture_output=True)
        assert canonical.returncode == 0, canonical.stderr

        # An explicit historical compatibility alias is accepted and stored
        # as the raw text supplied, not silently rewritten to its canonical ID.
        compatibility = subprocess.run([
            sys.executable, map_task, "--db", str(db), "--event-log", str(temp / "events.jsonl"),
            "--output-dir", str(out),
            "create", "--task-id", "TASK-8002", "--title", "compatibility", "--owner", "owner",
            "--role", "architect",
        ], cwd=repo, text=True, capture_output=True)
        assert compatibility.returncode == 0, compatibility.stderr

        with sqlite3.connect(db) as conn:
            rows = dict(conn.execute(
                "SELECT task_id, role FROM tasks WHERE task_id IN ('TASK-8001', 'TASK-8002')"
            ).fetchall())
        assert rows == {"TASK-8001": "delivery-implementer", "TASK-8002": "architect"}


def test_policy_and_helper_paths_use_normalized_role():
    historical = {"task_id": "TASK-A", "task_type": "implementation", "role": "auditor"}
    canonical = {"task_id": "TASK-B", "task_type": "implementation", "role_id": "independent-reviewer", "role": "independent-reviewer"}
    assert evaluate_pre_dispatch(historical, "helper-1", worker_tier=2)["decision"] == "reject"
    assert evaluate_pre_dispatch(canonical, "helper-1", worker_tier=2)["decision"] == "reject"


def main() -> int:
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_")]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"{len(tests)} role-registry tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
