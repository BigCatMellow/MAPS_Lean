"""Provider-neutral harness contracts for MAPS Lean.

This package defines execution-facing types, protocols, and deterministic hook
mechanics. It does not own or infer task authority, policy, ownership, review,
or completion state.
"""

from .hooks import (
    HookDirective,
    HookEvent,
    HookFailurePolicy,
    HookOutcome,
    HookRegistry,
    HookRunResult,
    HookSideEffect,
    HookSpec,
)
from .protocol import HarnessAdapter
from .types import (
    ExecutionBinding,
    NormalizedSessionState,
    OperationResult,
    RetryDisposition,
    SessionRef,
    SessionStatus,
    new_operation_id,
)

__all__ = [
    "ExecutionBinding",
    "HarnessAdapter",
    "HookDirective",
    "HookEvent",
    "HookFailurePolicy",
    "HookOutcome",
    "HookRegistry",
    "HookRunResult",
    "HookSideEffect",
    "HookSpec",
    "NormalizedSessionState",
    "OperationResult",
    "RetryDisposition",
    "SessionRef",
    "SessionStatus",
    "new_operation_id",
]
