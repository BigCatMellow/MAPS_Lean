"""Fail-closed Hook guard over caller-declared destructive/external actions.

Implements the SEC3 design note
`work/notes/2026-08-24-sec3-destructive-action-hook-guard-design.md`
("Decision" and "The second enforcement type").

Classification is *caller-declared*, never inferred: the operation about to be
performed states `destructive` / `external` as explicit booleans on the Hook
context. There is deliberately no regex sniffing, static analysis, or model
judgment here — an honest self-declaration at the call site is the contract.

This guard is intentionally NOT wired into any production call site. The first
real caller is a separate, bounded follow-up per the design note's Non-goals.
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


class DestructiveExternalActionGuard:
    """Read-only Hook guard over caller-declared destructive/external actions.

    Decision table (fixed, deterministic — no policy engine, no rules DSL):

    * `destructive` or `external` missing from the context -> DENY
      (`CLASSIFICATION_REQUIRED`). A forgotten declaration must never silently
      mean "not destructive"; this mirrors `CanonicalRunGuard`'s existing
      `BINDING_REQUIRED` fail-closed pattern.
    * either key present but not a real ``bool`` -> DENY
      (`CLASSIFICATION_INVALID`).
    * `destructive` or `external` is ``True`` -> DENY (`ACTION_AUTHORITY_ABSENT`).
      No explicit action-class authority signal exists on the task record, the
      execution binding, or the Hook context today, and this guard does not
      invent one. Until a real policy source exists, a declared
      destructive/external action is refused outright. `REQUIRE_APPROVAL` is
      deliberately not used: no operator-approval mechanism is confirmed to
      exist for this path yet, so it would be an escape hatch with nothing
      behind it.
    * both explicitly ``False`` -> ALLOW.
    """

    @staticmethod
    def _deny(code: str, reason: str) -> HookOutcome:
        return HookOutcome(HookDirective.DENY, reason, annotations={"guard_code": code})

    @staticmethod
    def _declared(context: Mapping[str, Any], key: str) -> tuple[bool | None, bool]:
        """Return (value, present). `value` is None when the key is unusable."""

        if key not in context:
            return None, False
        value = context[key]
        if not isinstance(value, bool):
            return None, True
        return value, True

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

        if destructive or external:
            classes = tuple(
                name
                for name, flag in (("destructive", destructive), ("external", external))
                if flag
            )
            return HookOutcome(
                HookDirective.DENY,
                reason=(
                    "Declared destructive/external action carries no explicit task "
                    "or binding authority for that action class."
                ),
                annotations={
                    "guard_code": "ACTION_AUTHORITY_ABSENT",
                    "action_classes": ",".join(classes),
                },
            )

        return HookOutcome(
            HookDirective.ALLOW,
            reason="Action is declared neither destructive nor external.",
            annotations={"guard_code": "ACTION_NOT_CONSEQUENTIAL"},
        )


def register_destructive_external_action_guards(
    registry: HookRegistry,
    guard: DestructiveExternalActionGuard,
    *,
    priority: int = 10,
) -> None:
    """Register the fail-closed destructive/external guard on both events.

    Composition helper only. No production code path calls this today; the
    first real call site is a separate follow-up per the design note.
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
