"""Fail-closed Hook guard over caller-declared destructive/external actions.

Implements the SEC3 design notes
`work/notes/2026-08-24-sec3-destructive-action-hook-guard-design.md` and its
impl-readiness addendum
`work/notes/2026-08-31-sec3-guard-impl-readiness-design.md` (behavior Qs 1-6).

Classification is *caller-declared*, never inferred: the operation about to be
performed states `destructive` / `external` as explicit booleans on the Hook
context. There is deliberately no regex sniffing, static analysis, or model
judgment here -- an honest self-declaration at the call site is the contract.

Once an action is declared consequential the guard consults the task's existing
`task_policy` authority model (via a duck-typed `source`, exactly like
`CanonicalRunGuard`): a declared class must be inside the task's permission
envelope, and a task that explicitly crosses its inherited authority
(`requires_operator_approval`) needs a recorded human reauthorization.

Operator workflow when a stop/kill is denied `OPERATOR_REAUTHORIZATION_ABSENT`:

    maps approve <task_id> --approved-by <id> --note <why>

then re-run the operation. `maps approve` takes the task id *positionally*
(`runtime/routing/cli.py`). The guard re-reads `policy["approved_by"]` /
`policy["approved_at"]` on the retry and allows. `HookDirective.REQUIRE_APPROVAL`
is deliberately never returned: nothing catches `APPROVAL_REQUIRED` at any call
site and resumes the operation, so it would be a worse-labelled DENY with an
escape hatch that does not exist (addendum Q6).
"""

from __future__ import annotations

from typing import Any, Mapping

from runtime.harness import (
    HookDirective,
    HookEvent,
    HookOutcome,
    HookRegistry,
    HookSideEffect,
    HookSpec,
)
from runtime.harness.hooks import HookEnforcement

from .evaluator import _approved, task_needs_human_reauthorization


class DestructiveExternalActionGuard:
    """Read-only Hook guard over caller-declared destructive/external actions.

    Decision table (fixed, deterministic -- no policy engine, no rules DSL):

    * `destructive` or `external` missing from the context -> DENY
      (`CLASSIFICATION_REQUIRED`). A forgotten declaration must never silently
      mean "not destructive"; this mirrors `CanonicalRunGuard`'s existing
      `BINDING_REQUIRED` fail-closed pattern.
    * either key present but not a real ``bool`` -> DENY
      (`CLASSIFICATION_INVALID`).
    * both explicitly ``False`` -> ALLOW (`ACTION_NOT_CONSEQUENTIAL`).
    * a consequential action with no `context["binding"]` (or one missing
      `task_id` / `run_id`) -> DENY (`CLASSIFICATION_BINDING_REQUIRED`).
    * the bound task cannot be read -> DENY (`ACTION_POLICY_UNAVAILABLE`).
    * a declared class outside the task's policy envelope
      (`destructive` vs `policy["destructive_action"]`, `external` vs
      `policy["external_side_effect"]`) -> DENY (`ACTION_OUTSIDE_TASK_ENVELOPE`).
    * inside the envelope but the task explicitly crosses its inherited
      authority (`requires_operator_approval`) with no recorded human
      reauthorization -> DENY (`OPERATOR_REAUTHORIZATION_ABSENT`).
    * inside the envelope, approval satisfied or not required -> ALLOW
      (`ACTION_WITHIN_TASK_ENVELOPE`) with
      ``evidence_refs=(task:<id>, run:<id>, action_classes:<...>)``.

    ``source`` is the caller's existing `TaskStore`, duck-typed: only
    ``get_task(task_id) -> dict | None`` is used. Both the envelope booleans and
    the approval state are read from the live task record. (The impl-readiness
    addendum proposed reading the envelope from a run-manifest policy snapshot;
    re-verified at HEAD, `get_run_manifest` carries no `policy` key -- that
    snapshot does not exist, so the live task is the single source. No schema
    change; see the addendum's "Implementation correction" section.)
    """

    def __init__(self, source: Any) -> None:
        self.source = source

    @staticmethod
    def _deny(code: str, reason: str, **extra: Any) -> HookOutcome:
        return HookOutcome(
            HookDirective.DENY, reason, annotations={"guard_code": code, **extra}
        )

    @staticmethod
    def _declared(context: Mapping[str, Any], key: str) -> tuple[bool | None, bool]:
        """Return (value, present). `value` is None when the key is unusable."""

        if key not in context:
            return None, False
        value = context[key]
        if not isinstance(value, bool):
            return None, True
        return value, True

    @staticmethod
    def _binding_text(context: Mapping[str, Any], key: str) -> str:
        binding = context.get("binding")
        if not isinstance(binding, Mapping):
            return ""
        value = binding.get(key)
        return value.strip() if isinstance(value, str) else ""

    def __call__(self, context: Mapping[str, Any]) -> HookOutcome:
        destructive, destructive_present = self._declared(context, "destructive")
        external, external_present = self._declared(context, "external")

        missing = [
            key
            for key, present in (("destructive", destructive_present), ("external", external_present))
            if not present
        ]
        if missing:
            return self._deny(
                "CLASSIFICATION_REQUIRED",
                "Destructive/external action guard requires explicit "
                f"caller-declared classification ({', '.join(missing)}).",
            )
        if destructive is None or external is None:
            return self._deny(
                "CLASSIFICATION_INVALID",
                "Destructive/external action classification must be explicit booleans.",
            )

        if not destructive and not external:
            return HookOutcome(
                HookDirective.ALLOW,
                reason="Action is declared neither destructive nor external.",
                annotations={"guard_code": "ACTION_NOT_CONSEQUENTIAL"},
            )

        classes = tuple(
            name
            for name, flag in (("destructive", destructive), ("external", external))
            if flag
        )
        class_text = ",".join(classes)

        task_id = self._binding_text(context, "task_id")
        run_id = self._binding_text(context, "run_id")
        if not task_id or not run_id:
            return self._deny(
                "CLASSIFICATION_BINDING_REQUIRED",
                "Declared destructive/external action requires an execution "
                "binding carrying task_id and run_id.",
                action_classes=class_text,
            )

        try:
            task = self.source.get_task(task_id)
        except Exception as exc:  # noqa: BLE001 - fail closed, never leak
            return self._deny(
                "ACTION_POLICY_UNAVAILABLE",
                f"Task policy could not be read ({type(exc).__name__}).",
                action_classes=class_text,
            )
        if task is None:
            return self._deny(
                "ACTION_POLICY_UNAVAILABLE",
                "Bound task no longer exists; cannot verify action authority.",
                action_classes=class_text,
            )
        policy = task.get("policy")
        policy = policy if isinstance(policy, Mapping) else {}

        if destructive and not bool(policy.get("destructive_action")):
            return self._deny(
                "ACTION_OUTSIDE_TASK_ENVELOPE",
                "Declared destructive action is outside the task's policy envelope.",
                action_classes=class_text,
            )
        if external and not bool(policy.get("external_side_effect")):
            return self._deny(
                "ACTION_OUTSIDE_TASK_ENVELOPE",
                "Declared external action is outside the task's policy envelope.",
                action_classes=class_text,
            )

        needs_reauthorization, _ = task_needs_human_reauthorization(task)
        if needs_reauthorization and not _approved(task):
            return self._deny(
                "OPERATOR_REAUTHORIZATION_ABSENT",
                "Task explicitly crosses its inherited authority and has no "
                "recorded human reauthorization for this action.",
                action_classes=class_text,
            )

        return HookOutcome(
            HookDirective.ALLOW,
            reason="Declared action is within the task's policy envelope.",
            evidence_refs=(
                f"task:{task_id}",
                f"run:{run_id}",
                f"action_classes:{class_text}",
            ),
            annotations={
                "guard_code": "ACTION_WITHIN_TASK_ENVELOPE",
                "action_classes": class_text,
            },
        )


def register_destructive_external_action_guards(
    registry: HookRegistry,
    guard: DestructiveExternalActionGuard,
    *,
    priority: int = 10,
) -> None:
    """Register the fail-closed destructive/external guard on both events.

    Composition helper. `build_canonical_harness_service`
    (`runtime/recovery/production.py`) is the one production caller;
    `HarnessService.stop()` is the first operation that fires
    `BEFORE_DESTRUCTIVE_ACTION`. `BEFORE_EXTERNAL_ACTION` still has no firing
    call site -- the enum member and this both-events registration stay so the
    external event is ready, but nothing fires it yet (addendum Q2).
    """

    if type(guard) is not DestructiveExternalActionGuard:
        raise TypeError("guard must be an exact DestructiveExternalActionGuard")

    for event in (HookEvent.BEFORE_DESTRUCTIVE_ACTION, HookEvent.BEFORE_EXTERNAL_ACTION):
        registry._register_enforcement(
            HookSpec(
                hook_id=f"destructive-external-action:{event.value}",
                event=event,
                callback=guard,
                priority=priority,
                side_effect=HookSideEffect.READ_ONLY,
            ),
            HookEnforcement.DESTRUCTIVE_EXTERNAL_ACTION,
        )
