from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol

from runtime.harness import (
    HookDirective,
    HookEvent,
    HookOutcome,
    HookRegistry,
    HookSideEffect,
    HookSpec,
)
from runtime.harness.hooks import HookEnforcement
from runtime.integrity.git_scope import (
    collect_git_worktree_identity,
    compare_worktree_identity,
)
from runtime.state.common import parse_time, utc_now


WorktreeIdentitySource = Callable[[str], Mapping[str, Any]]


class CanonicalRunSource(Protocol):
    def get_task(self, task_id: str) -> dict[str, Any] | None: ...
    def get_run_manifest(self, run_id: str) -> dict[str, Any] | None: ...
    def compute_task_revision(self, task_id: str) -> str | None: ...
    def check_run_stale(self, run_id: str, *, repo_root: str | Path) -> dict[str, Any]: ...
    def resolve_run_session(self, run_id: str) -> dict[str, Any] | None: ...


class CanonicalRunGuard:
    """Read-only Hook guard over canonical task/run evidence."""

    def __init__(
        self,
        source: CanonicalRunSource,
        *,
        repo_root: str | Path,
        now: Callable[[], datetime] = utc_now,
        worktree_identity: WorktreeIdentitySource = collect_git_worktree_identity,
    ) -> None:
        self.source = source
        self.repo_root = Path(repo_root).resolve()
        self.now = now
        self.worktree_identity = worktree_identity

    @staticmethod
    def _deny(code: str, reason: str) -> HookOutcome:
        return HookOutcome(HookDirective.DENY, reason, annotations={"guard_code": code})

    @staticmethod
    def _text(mapping: Mapping[str, Any], key: str) -> str:
        value = mapping.get(key)
        return value.strip() if isinstance(value, str) else ""

    def _extract_binding(self, context: Mapping[str, Any]) -> tuple[Mapping[str, Any] | None, HookOutcome | None]:
        binding = context.get("binding")
        if not isinstance(binding, Mapping):
            return None, self._deny("BINDING_REQUIRED", "Canonical run guard requires an explicit execution binding.")
        required = ("task_id", "run_id", "worker_id", "task_revision", "project_id")
        if any(not self._text(binding, key) for key in required):
            return None, self._deny("BINDING_INCOMPLETE", "Execution binding is missing required identity fields.")
        return binding, None

    def _base_evidence(self, binding: Mapping[str, Any], *, require_current_revision: bool) -> tuple[dict[str, Any] | None, dict[str, Any] | None, HookOutcome | None]:
        task_id = self._text(binding, "task_id")
        run_id = self._text(binding, "run_id")
        worker_id = self._text(binding, "worker_id")
        task_revision = self._text(binding, "task_revision")
        project_id = self._text(binding, "project_id")
        task = self.source.get_task(task_id)
        if task is None:
            return None, None, self._deny("TASK_NOT_FOUND", "Canonical task no longer exists.")
        if str(task.get("project_id", "")).strip() != project_id:
            return None, None, self._deny("PROJECT_MISMATCH", "Execution binding project does not match canonical task state.")
        manifest = self.source.get_run_manifest(run_id)
        if manifest is None:
            return task, None, self._deny("RUN_NOT_FOUND", "Canonical run manifest no longer exists.")
        if str(manifest.get("task_id", "")).strip() != task_id:
            return task, manifest, self._deny("RUN_TASK_MISMATCH", "Run manifest is bound to a different task.")
        if str(manifest.get("worker_id", "")).strip() != worker_id:
            return task, manifest, self._deny("RUN_WORKER_MISMATCH", "Run manifest is bound to a different worker.")
        if str(manifest.get("task_revision", "")).strip() != task_revision:
            return task, manifest, self._deny("RUN_REVISION_MISMATCH", "Execution binding does not match the immutable run revision.")
        if require_current_revision:
            current_revision = self.source.compute_task_revision(task_id)
            if current_revision is None or current_revision != task_revision:
                return task, manifest, self._deny("TASK_REVISION_STALE", "Canonical task definition changed after the run was created.")
        return task, manifest, None

    def _require_live_claim(self, task: Mapping[str, Any], worker_id: str) -> HookOutcome | None:
        if str(task.get("status", "")).upper() != "ACTIVE":
            return self._deny("TASK_NOT_ACTIVE", "Continuing execution requires an ACTIVE task.")
        if str(task.get("claimed_by", "")).strip() != worker_id:
            return self._deny("NOT_CLAIM_OWNER", "Continuing execution requires the active task claimant.")
        lease = parse_time(task.get("lease_expires_at"))
        if lease is None or lease <= self.now():
            return self._deny("LEASE_EXPIRED", "Continuing execution requires a live task lease.")
        return None

    def _require_current_run(self, run_id: str) -> HookOutcome | None:
        state = self.source.check_run_stale(run_id, repo_root=self.repo_root)
        if bool(state.get("stale", True)):
            return self._deny("RUN_STALE", "Run context or task definition is stale.")
        return None

    def _require_bound_worktree(self, manifest: Mapping[str, Any]) -> HookOutcome | None:
        """Fail closed only for runs bound to a specific Git worktree.

        Unbound runs (non-Git, placeholder ``base_revision``) carry no
        ``worktree`` mapping and are always allowed -- absence of a binding is a
        coverage gap, not a failure. When identity cannot be read for a bound
        run we deny rather than fall back to the process current directory.
        """
        expected = manifest.get("worktree")
        if not isinstance(expected, Mapping):
            return None
        try:
            actual = self.worktree_identity(str(self.repo_root))
        except RuntimeError:
            return self._deny(
                "RUN_WORKTREE_UNAVAILABLE",
                "Current Git worktree identity could not be read for a worktree-bound run.",
            )
        if compare_worktree_identity(dict(expected), dict(actual))["status"] == "mismatch":
            return self._deny(
                "RUN_WORKTREE_MISMATCH",
                "Run is bound to a different Git worktree than the one continuing it.",
            )
        return None

    def _require_durable_session(
        self,
        run_id: str,
        project_id: str,
        context: Mapping[str, Any],
    ) -> HookOutcome | None:
        session_ref = context.get("session_ref")
        if not isinstance(session_ref, Mapping):
            return self._deny("SESSION_REF_REQUIRED", "Session-bound operation requires an explicit SessionRef.")
        requested_session = self._text(session_ref, "session_id")
        requested_adapter = self._text(session_ref, "adapter")
        requested_project = self._text(session_ref, "project_id")
        routed_adapter = self._text(context, "adapter_id")
        if not requested_session or not requested_adapter or not requested_project or not routed_adapter:
            return self._deny(
                "SESSION_REF_INCOMPLETE",
                "Session-bound operation requires explicit project, adapter, and session identity.",
            )
        if requested_project != project_id:
            return self._deny(
                "SESSION_PROJECT_MISMATCH",
                "SessionRef project does not match the canonical run/task project context.",
            )
        if requested_adapter != routed_adapter:
            return self._deny("SESSION_ADAPTER_MISMATCH", "SessionRef adapter does not match the adapter selected for this operation.")

        lineage = self.source.resolve_run_session(run_id)
        if lineage is None:
            return self._deny("SESSION_NOT_DURABLY_BOUND", "Run has no durable session lineage for this operation.")
        state = str(lineage.get("state", "")).upper()
        if state == "UNBOUND":
            return self._deny("SESSION_NOT_DURABLY_BOUND", "Run has no durable session binding for this operation.")
        if state == "ADAPTER_UNPROVEN":
            return self._deny("SESSION_ADAPTER_UNPROVEN", "Canonical run evidence does not prove adapter-qualified session identity.")
        if state == "INVALID":
            return self._deny("SESSION_LINEAGE_INVALID", "Canonical run/session lineage is not a valid linear chain.")
        if state != "EXPLICIT":
            return self._deny("SESSION_LINEAGE_UNPROVEN", "Canonical run/session lineage state is not sufficient for this operation.")

        lineage_project = self._text(lineage, "project_id")
        if lineage_project != project_id:
            return self._deny(
                "SESSION_PROJECT_MISMATCH",
                "Durable run/session lineage does not match the canonical project context.",
            )

        current = lineage.get("current")
        if not isinstance(current, Mapping):
            return self._deny("SESSION_LINEAGE_INVALID", "Canonical run/session lineage has no current relationship.")
        recorded_project = self._text(current, "project_id")
        recorded_session = self._text(current, "session_id")
        recorded_adapter = self._text(current, "adapter_id")
        if recorded_project != requested_project:
            return self._deny(
                "SESSION_PROJECT_MISMATCH",
                "SessionRef project does not match the current durable run/session relationship.",
            )
        if recorded_session != requested_session:
            return self._deny("SESSION_BINDING_MISMATCH", "SessionRef does not match the current durable run/session relationship.")
        if recorded_adapter != requested_adapter:
            return self._deny("SESSION_ADAPTER_MISMATCH", "SessionRef adapter does not match the current durable run/session relationship.")
        return None

    def __call__(self, context: Mapping[str, Any]) -> HookOutcome:
        binding, error = self._extract_binding(context)
        if error is not None:
            return error
        assert binding is not None
        operation = str(context.get("operation", "")).strip().lower()
        if operation not in {"start", "send", "resume", "stop"}:
            return self._deny("UNSUPPORTED_OPERATION", "Canonical run guard received an unsupported harness operation.")
        continuing = operation in {"start", "send", "resume"}
        session_bound = operation in {"send", "resume", "stop"}
        task, manifest, error = self._base_evidence(binding, require_current_revision=continuing)
        if error is not None:
            return error
        assert task is not None and manifest is not None
        worker_id = self._text(binding, "worker_id")
        run_id = self._text(binding, "run_id")
        project_id = self._text(binding, "project_id")
        if continuing:
            error = self._require_live_claim(task, worker_id)
            if error is not None:
                return error
            error = self._require_current_run(run_id)
            if error is not None:
                return error
            error = self._require_bound_worktree(manifest)
            if error is not None:
                return error
        if session_bound:
            error = self._require_durable_session(run_id, project_id, context)
            if error is not None:
                return error
        return HookOutcome(
            HookDirective.ANNOTATE,
            reason="Canonical run evidence is current for this operation.",
            evidence_refs=(f"task:{self._text(binding, 'task_id')}", f"run:{run_id}"),
            annotations={"guard_code": "CANONICAL_RUN_VERIFIED"},
        )


def register_canonical_run_guards(registry: HookRegistry, guard: CanonicalRunGuard, *, priority: int = 10) -> None:
    """Register mandatory fail-closed guards at consequential lifecycle points."""

    if type(guard) is not CanonicalRunGuard:
        raise TypeError("guard must be an exact CanonicalRunGuard")

    for event in (HookEvent.RUN_STARTING, HookEvent.BEFORE_SEND, HookEvent.BEFORE_RESUME, HookEvent.SESSION_STOPPING):
        registry._register_enforcement(
            HookSpec(
                hook_id=f"canonical-run:{event.value}",
                event=event,
                callback=guard,
                priority=priority,
                side_effect=HookSideEffect.READ_ONLY,
            ),
            HookEnforcement.CANONICAL_RUN,
        )
