"""Provider-neutral harness contracts for MAPS Lean.

This package defines execution-facing types and protocols only. It does not own
or infer task authority, policy, ownership, review, or completion state.
"""

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
    "NormalizedSessionState",
    "OperationResult",
    "RetryDisposition",
    "SessionRef",
    "SessionStatus",
    "new_operation_id",
]
