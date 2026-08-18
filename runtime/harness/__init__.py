"""Provider-neutral harness contracts for MAPS Lean.

This package defines execution-facing types, protocols, deterministic hook
mechanics, and the provider-neutral service that composes them. It does not own
or infer task authority, policy, ownership, review, or completion state.
"""

from .contract import AdapterContractMixin
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
from .service import HarnessService
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
    "AdapterContractMixin",
    "ExecutionBinding",
    "HarnessAdapter",
    "HarnessService",
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
