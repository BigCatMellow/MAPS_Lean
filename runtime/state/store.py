from .base import BaseStore
from .common import MutationResult, ValidationResult
from .execution import ExecutionMixin
from .integrity import ExecutionIntegrityMixin
from .integrity_scope import ExecutionScopeHardeningMixin
from .observability import ObservabilityMixin
from .outcomes import OutcomeMixin
from .policy import PolicyStateMixin
from .readiness import ReadinessMixin
from .review import ReviewMixin
from .review_binding import ReviewBindingMixin


class TaskStore(
    ExecutionScopeHardeningMixin,
    ExecutionIntegrityMixin,
    PolicyStateMixin,
    ReadinessMixin,
    ExecutionMixin,
    ReviewBindingMixin,
    ReviewMixin,
    OutcomeMixin,
    ObservabilityMixin,
    BaseStore,
):
    """Canonical SQLite task store for MAPS Lean."""
    pass


__all__ = ["MutationResult", "TaskStore", "ValidationResult"]
