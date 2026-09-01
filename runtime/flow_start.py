from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any, Mapping, Sequence

from runtime.context_builder import build_context_plan
from runtime.skills import SkillCatalogError, SkillParseError, build_project_skill_catalog
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


def _record_environment_evidence(
    store: TaskStore,
    run_id: str,
    contract: Mapping[str, Any],
    repo_root: str | Path,
) -> MutationResult:
    """Wire E2 inspection + E3 recording for a contracted task's run.

    Uses ``runtime.environment.safety.inspect_local_environment`` -- the
    containment-checked wrapper that will not follow dependency inputs outside
    the repo -- NOT the raw ``runtime.environment.fingerprint`` inspector. This
    adds no new probing capability: it composes two functions that already ship.
    """

    from runtime.environment.safety import inspect_local_environment
    from runtime.environment.spec import EnvironmentSpecError, load_environment_spec

    spec_ref = str(contract["spec_ref"])
    root = Path(repo_root)
    try:
        spec = load_environment_spec(root / spec_ref)
        fingerprint = inspect_local_environment(spec, repo_root=root)
    except (EnvironmentSpecError, OSError, ValueError, RuntimeError) as exc:
        return MutationResult(False, "ENVIRONMENT_INSPECTION_FAILED", str(exc))
    return store.record_run_environment_evidence(
        run_id,
        spec=spec,
        fingerprint=fingerprint,
        spec_ref=spec_ref,
        recorded_by="maps-flow-start",
    )


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
    require_worktree_binding: bool = False,
) -> dict[str, Any]:
    """Start a deterministic local execution flow without provider launch.

    The flow composes existing guarded operations in order:

    1. claim the task for an explicit worker;
    2. discover the project's bundled Skills into a durable catalog, then build
       a read-only context plan including the Skills matched to this task,
       gated by their recorded lifecycle state (a QUARANTINED Skill is dropped);
    3. bind an immutable run manifest.

    It intentionally stops before choosing or launching a provider session.
    Per roadmap 6.9 / S6, a matched Skill whose trust-gate decision is `LOAD`
    has its hash-verified SKILL.md body attached to the plan
    (`plan["skills"][i]["body"]`, slice 1) plus an `execution_resources`
    manifest -- path / kind / size of its scripts/references/examples/assets,
    NEVER content (slice 2). WITHHELD / ON_DEMAND / DENIED Skills get neither,
    and resource *content* is only ever pulled on demand by a downstream
    consumer via `runtime.skills.load_skill_resource`.
    """

    claim = store.claim_task(task_id, worker_id, lease_seconds=lease_seconds)
    if not claim.ok:
        return _failed("claim", claim)

    try:
        skill_catalog = build_project_skill_catalog(repo_root, store)
    except (SkillCatalogError, SkillParseError) as exc:
        return _failed(
            "skills",
            MutationResult(False, "SKILL_CATALOG_FAILED", str(exc)),
        )

    try:
        context_plan = build_context_plan(
            store, task_id, repo_root=repo_root, skill_catalog=skill_catalog
        )
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
        require_worktree_binding=require_worktree_binding,
    )
    if not run.ok:
        return _failed("run_manifest", run)

    # 4. when the task carries an environment contract, record production
    #    environment evidence for this run (the task_environment row is itself
    #    the opt-in -- a task with no contract records nothing and routes
    #    exactly as before).
    task_record = store.get_task(task_id)
    environment_contract = (
        task_record.get("environment") if task_record is not None else None
    )
    if environment_contract is not None:
        evidence = _record_environment_evidence(
            store, run.task["run_id"], environment_contract, repo_root
        )
        if not evidence.ok:
            return _failed("environment_evidence", evidence)

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
    require_worktree_binding: bool = False,
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
        require_worktree_binding=require_worktree_binding,
    )
