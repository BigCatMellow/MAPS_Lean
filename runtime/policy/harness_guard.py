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
from runtime.state.common import parse_time, utc_now


class CanonicalRunSource(Protocol):
    def get_task(self, task_id: str) -> dict[str, Any] | None: ...
    def get_run_manifest(self, run_id: str) -> dict[str, Any] | None: ...
    def compute_task_revision(self, task_id: str) -> str | None: ...
    def check_run_stale(
        self, run_id: str, *, repo_root: str | Path
    ) -> dict[str, Any]: ...


class CanonicalRunGuard:
    """Read-only Hook guard over canonical task/run evidence.

    The guard proves that a harness operation still points at the intended task,
    worker, run, and (when relevant) session. It does not grant policy or
    operator authority and it never mutates canonical state.
    """

    def __init__(
        self,
        source: CanonicalRunSource,
        *,
        repo_root: str | Path,
        now: Callable[[], datetime] = utc_now,
    ) -> None:
        self.source = source
        self.repo_root = Path(repo_root).resolve()
        self.now = now

    @staticmethod
    def _deny(code: str, reason: str) -> HookOutcome:
        return HookOutcome(
            HookDirective.DENY,
            reason,
            annotations={"guard_code": code},
        )

    @staticmethod
    def _text(mapping: Mapping[str, Any], key: str) -> str:
        value = mapping.get(key)
        return value.strip() if isinstance(value, str) else ""

    def _extract_binding(
        self, context: Mapping[str, Any]
    ) -> tuple[Mapping[str, Any] | None, HookOutcome | None]:
        binding = context.get("binding")
        if not isinstance(binding, Mapping):
            return None, self._deny(
                "BINDING_REQUIRED",
                "Canonical run guard requires an explicit execution binding.",
            )
        required = ("task_id", "run_id", "worker_id", "task_revision", "project_id")
        missing = [key for key in required if not self._text(binding, key)]
        if missing:
            return None, self._deny(
                "BINDING_INCOMPLETE",
                "Execution binding is missing required identity fields.",
            )
        return binding, None

    def _base_evidence(
        self,
        binding: Mapping[str, Any],
        *,
        require_current_revision: bool,
    ) -> tuple[dict[str, Any] | None, dict[str, Any] | None, HookOutcome | None]:
        task_id = self._text(binding, "task_id")
        run_id = self._text(binding, "run_id")
        worker_id = self._text(binding, "worker_id")
        task_revision = self._text(binding, "task_revision")
        project_id = self._text(binding, "project_id")

        task = self.source.get_task(task_id)
        if task is None:
            return None, None, self._deny(
                "TASK_NOT_FOUND",
                "Canonical task no longer exists.",
            )
        if str(task.get("project_id", "")).strip() != project_id:
            return None, None, self._deny(
                "PROJECT_MISMATCH",
                "Execution binding project does not match canonical task state.",
            )

        manifest = self.source.get_run_manifest(run_id)
        if manifest is None:
            return task, None, self._deny(
                "RUN_NOT_FOUND",
                "Canonical run manifest no longer exists.",
            )
        if str(manifest.get("task_id", "")).strip() != task_id:
            return task, manifest, self._deny(
                "RUN_TASK_MISMATCH",
                "Run manifest is bound to a different task.",
            )
        if str(manifest.get("worker_id", "")).strip() != worker_id:
            return task, manifest, self._deny(
                "RUN_WORKER_MISMATCH",
                "Run manifest is bound to a different worker.",
            )
        if str(manifest.get("task_revision", "")).strip() != task_revision:
            return task, manifest, self._deny(
                "RUN_REVISION_MISMATCH",
                "Execution binding does not match the immutable run revision.",
            )

        if require_current_revision:
            current_revision = self.source.compute_task_revision(task_id)
            if current_revision is None or current_revision != task_revision:
                return task, manifest, self._deny(
                    "TASK_REVISION_STALE",
                    "Canonical task definition changed after the run was created.",
                )
        return task, manifest, None

    def _require_live_claim(
        self,
        task: Mapping[str, Any],
        worker_id: str,
    ) -> HookOutcome | None:
        if str(task.get("status", "")).upper() != "ACTIVE":
            return self._deny(
                "TASK_NOT_ACTIVE",
                "Continuing execution requires an ACTIVE task.",
            )
        if str(task.get("claimed_by", "")).strip() != worker_id:
            return self._deny(
                "NOT_CLAIM_OWNER",
                "Continuing execution requires the active task claimant.",
            )
        lease = parse_time(task.get("lease_expires_at"))
        if lease is None or lease <= self.now():
            return self._deny(
                "LEASE_EXPIRED",
                "Continuing execution requires a live task lease.",
            )
        return None

    def _require_current_run(self, run_id: str) -> HookOutcome | None:
        state = self.source.check_run_stale(run_id, repo_root=self.repo_root)
        if bool(state.get("stale", True)):
            return self._deny(
                "RUN_STALE",
                "Run context or task definition is stale.",
            )
        return None

    def _require_durable_session(
        self,
        manifest: Mapping[str, Any],
        context: Mapping[str, Any],
    ) -> HookOutcome | None:
        session_ref = context.get("session_ref")
        if not isinstance(session_ref, Mapping):
            return self._deny(
                "SESSION_REF_REQUIRED",
                "Session-bound operation requires an explicit SessionRef.",
            )
        requested = self._text(session_ref, "session_id")
        recorded = str(manifest.get("session_id") or "").strip()
        if not requested:
            return self._deny(
                "SESSION_REF_INCOMPLETE",
                "SessionRef is missing session_id.",
            )
        if not recorded:
            return self._deny(
                "SESSION_NOT_DURABLY_BOUND",
                "Run manifest has no durable session binding for this operation.",
            )
        if recorded != requested:
            return self._deny(
                "SESSION_BINDING_MISMATCH",
                "SessionRef does not match the run manifest session binding.",
            )
        return None

    def __call__(self, context: Mapping[str, Any]) -> HookOutcome:
        binding, error = self._extract_binding(context)
        if error is not None:
            return error
        assert binding is not None

        operation = str(context.get("operation", "")).strip().lower()
        if operation not in {"start", "send", "stop"}:
            return self._deny(
                "UNSUPPORTED_OPERATION",
                "Canonical run guard received an unsupported harness operation.",
            )

        task, manifest, error = self._base_evidence(
            binding,
            require_current_revision=operation in {"start", "send"},
        )
        if error is not None:
            return error
        assert task is not None
        assert manifest is not None

        worker_id = self._text(binding, "worker_id")
        run_id = self._text(binding, "run_id")

        if operation in {"start", "send"}:
            error = self._require_live_claim(task, worker_id)
            if error is not None:
                return error
            error = self._require_current_run(run_id)
            if error is not None:
                return error

        if operation in {"send", "stop"}:
            error = self._require_durable_session(manifest, context)
            if error is not None:
                return error

        return HookOutcome(
            HookDirective.ANNOTATE,
            reason="Canonical run evidence is current for this operation.",
            evidence_refs=(
                f"task:{self._text(binding, 'task_id')}",
                f"run:{run_id}",
            ),
            annotations={"guard_code": "CANONICAL_RUN_VERIFIED"},
        )


def register_canonical_run_guards(
    registry: HookRegistry,
    guard: CanonicalRunGuard,
    *,
    priority: int = 10,
) -> None:
    """Register the guard at pre-mutation lifecycle points."""

    for event in (
        HookEvent.RUN_STARTING,
        HookEvent.BEFORE_SEND,
        HookEvent.SESSION_STOPPING,
    ):
        registry.register(
            HookSpec(
                hook_id=f"canonical-run:{event.value}",
                event=event,
                callback=guard,
                priority=priority,
                side_effect=HookSideEffect.READ_ONLY,
            )
        )
