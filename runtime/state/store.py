from .base import BaseStore
from .common import MutationResult, ValidationResult
from .execution import ExecutionMixin
from .policy import PolicyStateMixin
from .readiness import ReadinessMixin
from .review import ReviewMixin


class TaskStore(PolicyStateMixin, ReadinessMixin, ExecutionMixin, ReviewMixin, BaseStore):
    """Canonical SQLite task store for MAPS Lean."""
    pass


__all__ = ["MutationResult", "TaskStore", "ValidationResult"]
