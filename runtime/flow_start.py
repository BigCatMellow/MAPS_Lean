from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any, Mapping, Sequence

from runtime.context_builder import build_context_plan
from runtime.state import MutationResult, TaskStore


def _mutation_payload(result: MutationResult) -> dict[str, Any]:
    return asdict(result)


def _failed(step: str, result: MutationResult | Mapping[str, Any]) -> dict[str, Any]:
    payload = _mutation_payload(result) if isinstance(result, MutationResult) else dict(result)
    return {
        "ok": False,
        "code": "FLOW_STEP_FAILED",
        "failed_step": step,
        "step_result": payload,
    }


def _parse_runtime_limits(items: Sequence[str]) -> dict[str, int] | MutationResult:
    limits: dict[str, int] = {}
    for item in items:
        if "=" not in item:
            return MutationResult(
                False,
                "INVALID_RUNTIME_LIMIT",
                "runtime limits must use KEY=INT",
            )
        key, raw_value = item.split("=", 1)
        key = key.strip()
        try:
            value = int(raw_value)
        except ValueError:
            return MutationResult(
                False,
                "INVALID_RUNTIME_LIMIT",
                f"{key} must be an integer",
            )
        limits[key] = value
    return limits


def flow_start(
    store: TaskStore,
    task_id: str,
    *,
    worker_id: str,
    repo_root: str | Path = ".",
    created_by: str = "maps-flow-start",
    lease_seconds: int = 900,
    context_paths: Sequence[str | Path] = (),
    readable_paths: Sequence[str | Path] = (".",),
    writable_paths: Sequence[str | Path] | None = None,
    forbidden_paths: Sequence[str | Path] = (),
    runtime_limits: Mapping[str, int] | None = None,
    base_revision: str | None = None,
) -> dict[str, Any]:
    """Start a deterministic local execution flow without provider launch.

    The flow composes existing guarded operations in order:

    1. claim the task for an explicit worker;
    2. build a read-only context plan;
    3. bind an immutable run manifest.

    It intentionally stops before choosing or launching a provider session.
    """

    claim = store.claim_task(task_id, worker_id, lease_seconds=lease_seconds)
    if not claim.ok:
        return _failed("claim", claim)

    try:
        context_plan = build_context_plan(store, task_id, repo_root=repo_root)
    except ValueError as exc:
        return _failed(
            "context",
            MutationResult(False, "INVALID_REPO_ROOT", str(exc)),
        )
    if context_plan is None:
        return _failed(
            "context",
            MutationResult(False, "NOT_FOUND", f"{task_id} does not exist"),
        )

    run = store.create_run_manifest(
        task_id,
        worker_id,
        repo_root=repo_root,
        created_by=created_by,
        context_paths=context_paths,
        readable_paths=readable_paths,
        writable_paths=writable_paths,
        forbidden_paths=forbidden_paths,
        runtime_limits=runtime_limits,
        base_revision=base_revision,
    )
    if not run.ok:
        return _failed("run_manifest", run)

    return {
        "ok": True,
        "code": "FLOW_STARTED",
        "task_id": task_id,
        "worker_id": worker_id,
        "claim": _mutation_payload(claim),
        "context_plan": context_plan,
        "run_manifest": run.task,
        "next_step": {
            "state": "STOPPED_BEFORE_PROVIDER_SESSION",
            "reason": (
                "flow start does not select workers, launch providers, attach "
                "sessions, or send messages"
            ),
        },
    }


def flow_start_from_runtime_limit_args(
    store: TaskStore,
    task_id: str,
    *,
    worker_id: str,
    repo_root: str | Path = ".",
    created_by: str = "maps-flow-start",
    lease_seconds: int = 900,
    context_paths: Sequence[str | Path] = (),
    readable_paths: Sequence[str | Path] = (".",),
    writable_paths: Sequence[str | Path] | None = None,
    forbidden_paths: Sequence[str | Path] = (),
    runtime_limit_args: Sequence[str] = (),
    base_revision: str | None = None,
) -> dict[str, Any]:
    limits = _parse_runtime_limits(runtime_limit_args)
    if isinstance(limits, MutationResult):
        return _failed("options", limits)
    return flow_start(
        store,
        task_id,
        worker_id=worker_id,
        repo_root=repo_root,
        created_by=created_by,
        lease_seconds=lease_seconds,
        context_paths=context_paths,
        readable_paths=readable_paths,
        writable_paths=writable_paths,
        forbidden_paths=forbidden_paths,
        runtime_limits=limits or None,
        base_revision=base_revision,
    )
