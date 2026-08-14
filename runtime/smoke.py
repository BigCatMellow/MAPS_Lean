from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile
from typing import Any

from runtime.state import TaskStore


def smoke_contract() -> dict[str, Any]:
    return {
        "title": "Smoke lifecycle",
        "outcome": "Disposable task reaches DONE through guarded lifecycle",
        "task_type": "IMPLEMENTATION",
        "owner": "smoke-owner",
        "risk": "MEDIUM",
        "decision_authority": "disposable smoke state only",
        "verification": "this smoke lifecycle",
        "evidence_expected": "smoke evidence string",
        "review_required": "INDEPENDENT_REVIEW",
        "escalation": "stop on any failed guarded transition",
        "inputs": ["disposable smoke input"],
        "sources": ["active runtime"],
        "dependencies": [],
        "output_paths": ["scratch/smoke-output.txt"],
        "non_goals": ["no live project mutation"],
        "acceptance_criteria": ["task reaches DONE"],
        "stop_conditions": ["any guard rejects expected valid transition"],
        "policy": {
            "requires_operator_approval": False,
            "destructive_action": False,
            "external_side_effect": False,
            "security_sensitive": False,
            "broad_architecture": False,
            "paid_execution": False,
        },
    }


def require(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def run_smoke(*, with_langgraph: bool = False, with_hcom: bool = False) -> dict[str, Any]:
    result: dict[str, Any] = {}
    with tempfile.TemporaryDirectory(prefix="maps-smoke-") as td:
        root = Path(td)
        task_db = root / "maps.db"
        store = TaskStore(task_db)
        settings = store.connection_settings()
        require(settings["foreign_keys"] == 1, "SQLite foreign keys are not enabled")
        require(str(settings["journal_mode"]).lower() == "wal", "SQLite WAL is not enabled")
        require(settings["busy_timeout"] == 5000, "SQLite busy timeout is not 5000ms")

        created = store.create_task(title="Smoke lifecycle")
        require(created.ok, created.message)
        require(created.task is not None, "create_task returned no task payload")
        task_id = created.task["task_id"]
        shaped = store.update_contract(task_id, smoke_contract())
        require(shaped.ok, shaped.message)
        validated = store.validate_ready(task_id)
        require(validated.ok, "; ".join(validated.reasons))
        promoted = store.promote_ready(task_id, actor="smoke-shaper")
        require(promoted.ok, promoted.message)
        claimed = store.claim_task(task_id, "smoke-worker", lease_seconds=60)
        require(claimed.ok, claimed.message)
        submitted = store.submit_task(task_id, "smoke-worker", "smoke evidence")
        require(submitted.ok, submitted.message)
        review_claim = store.claim_review(task_id, "smoke-reviewer")
        require(review_claim.ok, review_claim.message)
        reviewed = store.record_review(
            task_id,
            "smoke-reviewer",
            "APPROVED",
            "independent smoke criteria verified",
        )
        require(reviewed.ok, reviewed.message)
        final = store.get_task(task_id)
        require(final is not None and final["status"] == "DONE", "smoke task did not reach DONE")
        result["sqlite_task_lifecycle"] = {
            "ok": True,
            "task_id": task_id,
            "status": final["status"],
            "settings": settings,
        }

        if with_langgraph:
            from runtime.policy import HaltRecord, WorkerProfile
            from runtime.routing.langgraph_runtime import run_checkpointed_route

            checkpoint_db = root / "langgraph-checkpoints.db"
            route = run_checkpointed_route(
                tasks=[],
                workers=[WorkerProfile("smoke-worker", "core")],
                halt=HaltRecord(),
                checkpoint_path=checkpoint_db,
                task_db_path=task_db,
                thread_id="maps-smoke",
            )
            require(route["route"] == "wait_or_reconcile", "unexpected idle LangGraph route")
            require(checkpoint_db.exists(), "LangGraph checkpoint DB was not created")
            require(checkpoint_db.resolve() != task_db.resolve(), "checkpoint DB equals task DB")
            result["langgraph"] = {"ok": True, "route": route["route"]}

        if with_hcom:
            from runtime.communication import HcomAdapter

            adapter = HcomAdapter(hcom_dir=root / ".hcom")
            version = adapter.version()
            require(version.ok, "hcom --version failed")
            result["hcom"] = {"ok": True, "version": version.stdout.strip()}

    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run disposable MAPS Lean smoke checks")
    parser.add_argument("--with-langgraph", action="store_true")
    parser.add_argument("--with-hcom", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = run_smoke(with_langgraph=args.with_langgraph, with_hcom=args.with_hcom)
    except Exception as exc:
        print(json.dumps({"ok": False, "error": type(exc).__name__, "message": str(exc)}, indent=2))
        return 1
    print(json.dumps({"ok": True, "checks": result}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
