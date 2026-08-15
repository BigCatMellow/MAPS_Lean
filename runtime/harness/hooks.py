from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Callable, Mapping

from .types import _require_text


class HookEvent(str, Enum):
    RUN_STARTING = "run_starting"
    RUN_STARTED = "run_started"
    BEFORE_TOOL = "before_tool"
    AFTER_TOOL = "after_tool"
    BEFORE_WRITE = "before_write"
    AFTER_WRITE = "after_write"
    BEFORE_EXTERNAL_ACTION = "before_external_action"
    BEFORE_DESTRUCTIVE_ACTION = "before_destructive_action"
    BEFORE_SEND = "before_send"
    SUBMISSION_CREATED = "submission_created"
    REVIEW_STARTING = "review_starting"
    REVIEW_COMPLETING = "review_completing"
    SESSION_STOPPING = "session_stopping"
    RUN_FAILED = "run_failed"


class HookDirective(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    ANNOTATE = "ANNOTATE"


class HookSideEffect(str, Enum):
    READ_ONLY = "READ_ONLY"
    EVIDENCE_WRITE = "EVIDENCE_WRITE"
    GUARDED_MUTATION = "GUARDED_MUTATION"


class HookFailurePolicy(str, Enum):
    FAIL_CLOSED = "FAIL_CLOSED"
    CONTINUE = "CONTINUE"
    RAISE = "RAISE"


HookCallback = Callable[[Mapping[str, Any]], "HookOutcome"]


def _freeze_hook_value(value: Any) -> Any:
    """Recursively freeze hook context so hooks cannot rewrite later guard input."""

    if isinstance(value, Mapping):
        return MappingProxyType(
            {key: _freeze_hook_value(item) for key, item in value.items()}
        )
    if isinstance(value, (list, tuple)):
        return tuple(_freeze_hook_value(item) for item in value)
    if isinstance(value, (set, frozenset)):
        return frozenset(_freeze_hook_value(item) for item in value)
    return value


@dataclass(frozen=True, slots=True)
class HookOutcome:
    directive: HookDirective
    reason: str | None = None
    evidence_refs: tuple[str, ...] = ()
    annotations: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.directive in {HookDirective.DENY, HookDirective.REQUIRE_APPROVAL}:
            if self.reason is None or not self.reason.strip():
                raise ValueError(f"{self.directive.value} requires a reason")
        if self.reason is not None:
            object.__setattr__(self, "reason", _require_text(self.reason, "reason"))
        object.__setattr__(
            self,
            "evidence_refs",
            tuple(_require_text(ref, "evidence reference") for ref in self.evidence_refs),
        )
        object.__setattr__(self, "annotations", MappingProxyType(dict(self.annotations)))


@dataclass(frozen=True, slots=True)
class HookSpec:
    hook_id: str
    event: HookEvent
    callback: HookCallback
    priority: int = 100
    side_effect: HookSideEffect = HookSideEffect.READ_ONLY
    failure_policy: HookFailurePolicy = HookFailurePolicy.FAIL_CLOSED

    def __post_init__(self) -> None:
        object.__setattr__(self, "hook_id", _require_text(self.hook_id, "hook_id"))
        if not callable(self.callback):
            raise TypeError("callback must be callable")


@dataclass(frozen=True, slots=True)
class HookInvocation:
    hook_id: str
    outcome: HookOutcome


@dataclass(frozen=True, slots=True)
class HookRunResult:
    event: HookEvent
    invocations: tuple[HookInvocation, ...]

    @property
    def denied(self) -> bool:
        return any(
            item.outcome.directive == HookDirective.DENY for item in self.invocations
        )

    @property
    def requires_approval(self) -> bool:
        return any(
            item.outcome.directive == HookDirective.REQUIRE_APPROVAL
            for item in self.invocations
        )

    @property
    def permitted(self) -> bool:
        return not self.denied and not self.requires_approval

    @property
    def blocking_reasons(self) -> tuple[str, ...]:
        return tuple(
            item.outcome.reason
            for item in self.invocations
            if item.outcome.directive
            in {HookDirective.DENY, HookDirective.REQUIRE_APPROVAL}
            and item.outcome.reason is not None
        )

    @property
    def evidence_refs(self) -> tuple[str, ...]:
        return tuple(
            ref for item in self.invocations for ref in item.outcome.evidence_refs
        )


class HookRegistry:
    """Small deterministic in-process hook registry.

    Hooks may deny, require existing approval, or annotate evidence. Running this
    registry does not grant task ownership, scope, policy authority, or operator
    approval.
    """

    def __init__(self) -> None:
        self._specs: list[tuple[int, HookSpec]] = []
        self._ids: set[str] = set()
        self._sequence = 0

    def register(self, spec: HookSpec) -> None:
        if spec.hook_id in self._ids:
            raise ValueError(f"duplicate hook_id: {spec.hook_id}")
        self._ids.add(spec.hook_id)
        self._specs.append((self._sequence, spec))
        self._sequence += 1

    def list_for(self, event: HookEvent) -> tuple[HookSpec, ...]:
        matching = [
            (sequence, spec)
            for sequence, spec in self._specs
            if spec.event == event
        ]
        matching.sort(key=lambda item: (item[1].priority, item[0]))
        return tuple(spec for _, spec in matching)

    def run(
        self,
        event: HookEvent,
        context: Mapping[str, Any] | None = None,
    ) -> HookRunResult:
        frozen_context = _freeze_hook_value(dict(context or {}))
        invocations: list[HookInvocation] = []

        for spec in self.list_for(event):
            try:
                outcome = spec.callback(frozen_context)
                if not isinstance(outcome, HookOutcome):
                    raise TypeError("hook callback must return HookOutcome")
            except Exception as exc:
                if spec.failure_policy == HookFailurePolicy.RAISE:
                    raise
                if spec.failure_policy == HookFailurePolicy.FAIL_CLOSED:
                    outcome = HookOutcome(
                        HookDirective.DENY,
                        reason=f"Hook {spec.hook_id} failed closed.",
                        annotations={"error_type": type(exc).__name__},
                    )
                else:
                    outcome = HookOutcome(
                        HookDirective.ANNOTATE,
                        reason=f"Hook {spec.hook_id} failed and was ignored.",
                        annotations={"error_type": type(exc).__name__},
                    )

            invocations.append(HookInvocation(spec.hook_id, outcome))

        return HookRunResult(event=event, invocations=tuple(invocations))
