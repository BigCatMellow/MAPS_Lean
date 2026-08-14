from .base import BaseStore
from .common import MutationResult, ValidationResult
from .execution import ExecutionMixin
from .integrity import ExecutionIntegrityMixin
from .integrity_scope import ExecutionScopeHardeningMixin
from .policy import PolicyStateMixin
from .readiness import ReadinessMixin
from .review import ReviewMixin


class TaskStore(
    ExecutionScopeHardeningMixin,
    ExecutionIntegrityMixin,
    PolicyStateMixin,
    ReadinessMixin,
    ExecutionMixin,
    ReviewMixin,
    BaseStore,
):
    """Canonical SQLite task store for MAPS Lean."""
    pass


__all__ = ["MutationResult", "TaskStore", "ValidationResult"]
