"""Fail-closed Hook guard over caller-declared write scope.

Implements the write half of roadmap 6.4 ("Before write" /
`work/roadmaps/agent-harness-capabilities/04-agentic-security.md` §6.1), per
the design note
`work/notes/2026-09-15-6.4-write-credential-guard-design.md`. Structural
mirror of the sibling caller-declared-action guard in
`runtime/policy/destructive_action_guard.py`: one callable guard, one
`register_*` composition helper, one enforcement role.

Classification is *caller-declared*, never inferred: the operation about to
write states `write_paths` explicitly on the Hook context. There is
deliberately no filesystem sniffing of what a caller is about to do -- an
honest self-declaration at the call site is the contract, same discipline as
the sibling destructive/external guard's booleans.

Scope authority is the task's own `output_paths` -- real, already-shipped
data (`readiness.py` requires it non-empty for `AGI READY`). Membership is
decided by the existing `runtime.helpers.common.path_in_scope` helper
(already used by the one-shot helper adapters); this module does not
reimplement path-scope math.

Deliberately NOT in this slice (design note §4a/§5):
* No firing call site. `HarnessService` mediates session-lifecycle
  operations only (start/send/resume/stop); none of those is "a file write
  happens." The actual write happens inside an agent's own tool loop, which
  this harness does not intercept today -- the same gap the memory
  provenance guard's own docstring names for its sibling event pair. Wiring
  that is a separate, larger architecture decision, not made here. This
  guard is composed but unwired, same starting shape the sibling
  caller-declared-action guard itself originally shipped in.
* No credential guard, no capability-declaration manifest -- see the design
  note §2/§3 for why neither is real, buildable work today.
* No registration on the write-completed event -- a deny-only guard gates
  nothing useful after the write already happened.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Sequence

from runtime.harness import (
    HookDirective,
    HookEvent,
    HookOutcome,
    HookRegistry,
    HookSideEffect,
    HookSpec,
)
from runtime.harness.hooks import HookEnforcement
from runtime.helpers.common import path_in_scope


class WriteScopeGuard:
    """Read-only Hook guard over caller-declared write scope.

    Decision table (fixed, deterministic):

    * `write_paths` missing from context -> DENY (`WRITE_PATHS_REQUIRED`).
    * `write_paths` present but not a non-empty list of non-blank strings ->
      DENY (`WRITE_PATHS_INVALID`).
    * no `context["binding"]` (or missing `task_id`/`run_id`) -> DENY
      (`WRITE_BINDING_REQUIRED`).
    * the bound task cannot be read -> DENY (`WRITE_POLICY_UNAVAILABLE`).
    * the task's `output_paths` is empty/missing -> DENY
      (`WRITE_SCOPE_UNDECLARED`). Expected unreachable via any normal
      `AGI READY` task (`output_paths` is a required field there) --
      fail-closed defense against malformed/legacy task state, same
      justification as the sibling guard's own similarly-unreachable
      branches.
    * any declared path resolves outside every entry of the task's
      `output_paths` -> DENY (`WRITE_OUTSIDE_TASK_SCOPE`).
    * every declared path is in scope -> ALLOW (`WRITE_WITHIN_TASK_SCOPE`)
      with `evidence_refs=(task:<id>, run:<id>, paths:<...>)`.

    ``source`` is the caller's existing `TaskStore`, duck-typed: only
    ``get_task(task_id) -> dict | None`` is used, same as the sibling guard.
    ``repo_root`` anchors relative `write_paths` and the task's
    `output_paths`, mirroring `path_in_scope`'s own contract.
    """

    def __init__(self, source: Any, *, repo_root: str | Path) -> None:
        self.source = source
        self.repo_root = Path(repo_root)

    @staticmethod
    def _deny(code: str, reason: str, **extra: Any) -> HookOutcome:
        return HookOutcome(
            HookDirective.DENY, reason, annotations={"guard_code": code, **extra}
        )

    @staticmethod
    def _binding_text(context: Mapping[str, Any], key: str) -> str:
        binding = context.get("binding")
        if not isinstance(binding, Mapping):
            return ""
        value = binding.get(key)
        return value.strip() if isinstance(value, str) else ""

    @staticmethod
    def _declared_paths(context: Mapping[str, Any]) -> tuple[Sequence[str] | None, bool]:
        """Return (paths, present). `paths` is None when the value is unusable."""

        if "write_paths" not in context:
            return None, False
        value = context["write_paths"]
        if (
            not isinstance(value, (list, tuple))
            or not value
            or not all(isinstance(item, str) and item.strip() for item in value)
        ):
            return None, True
        return tuple(value), True

    def __call__(self, context: Mapping[str, Any]) -> HookOutcome:
        write_paths, present = self._declared_paths(context)
        if not present:
            return self._deny(
                "WRITE_PATHS_REQUIRED",
                "Write scope guard requires explicit caller-declared write_paths.",
            )
        if write_paths is None:
            return self._deny(
                "WRITE_PATHS_INVALID",
                "write_paths must be a non-empty list of non-blank strings.",
            )

        task_id = self._binding_text(context, "task_id")
        run_id = self._binding_text(context, "run_id")
        if not task_id or not run_id:
            return self._deny(
                "WRITE_BINDING_REQUIRED",
                "Declared write requires an execution binding carrying "
                "task_id and run_id.",
            )

        try:
            task = self.source.get_task(task_id)
        except Exception as exc:  # noqa: BLE001 - fail closed, never leak
            return self._deny(
                "WRITE_POLICY_UNAVAILABLE",
                f"Task write scope could not be read ({type(exc).__name__}).",
            )
        if task is None:
            return self._deny(
                "WRITE_POLICY_UNAVAILABLE",
                "Bound task no longer exists; cannot verify write scope.",
            )

        allowed = task.get("output_paths")
        if not isinstance(allowed, (list, tuple)) or not allowed:
            return self._deny(
                "WRITE_SCOPE_UNDECLARED",
                "Bound task has no declared output_paths to write scope against.",
            )

        outside = [
            path
            for path in write_paths
            if not path_in_scope(path, allowed, self.repo_root)
        ]
        if outside:
            return self._deny(
                "WRITE_OUTSIDE_TASK_SCOPE",
                "Declared write path(s) are outside the task's output scope: "
                + ", ".join(outside),
                write_paths=",".join(write_paths),
            )

        return HookOutcome(
            HookDirective.ALLOW,
            reason="Declared write path(s) are within the task's output scope.",
            evidence_refs=(
                f"task:{task_id}",
                f"run:{run_id}",
                f"paths:{','.join(write_paths)}",
            ),
            annotations={
                "guard_code": "WRITE_WITHIN_TASK_SCOPE",
                "write_paths": ",".join(write_paths),
            },
        )


def register_write_scope_guards(
    registry: HookRegistry,
    guard: WriteScopeGuard,
    *,
    priority: int = 10,
) -> None:
    """Register the fail-closed write-scope guard on the pre-write event.

    Composition helper, mirroring the sibling caller-declared-action guard's
    own registration function. Not yet called from any operation --
    `build_canonical_harness_service` composes it (unwired) per the design
    note; there is no production firing call site yet (design note §4a).
    """

    if type(guard) is not WriteScopeGuard:
        raise TypeError("guard must be an exact WriteScopeGuard")

    registry._register_enforcement(
        HookSpec(
            hook_id=f"write-scope:{HookEvent.BEFORE_WRITE.value}",
            event=HookEvent.BEFORE_WRITE,
            callback=guard,
            priority=priority,
            side_effect=HookSideEffect.READ_ONLY,
        ),
        HookEnforcement.WRITE_SCOPE,
    )
