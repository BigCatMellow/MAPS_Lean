from .base import BaseStore
from .common import MutationResult, ValidationResult
from .environment_contract import EnvironmentContractMixin
from .environment import EnvironmentEvidenceMixin
from .execution import ExecutionMixin
from .helper_recovery_lineage import HelperRecoveryLineageMixin
from .integrity import ExecutionIntegrityMixin
from .integrity_scope import ExecutionScopeHardeningMixin
from .observability import ObservabilityMixin
from .operational_learning_storage import OperationalLessonStorageMixin
from .outcomes import OutcomeMixin
from .policy import PolicyStateMixin
from .readiness import ReadinessMixin
from .review import ReviewMixin
from .review_binding import ReviewBindingMixin
from .run_lineage import RunSessionLineageMixin
from .run_lineage_trace import RunSessionTraceMixin
from .skill_lifecycle_storage import SkillLifecycleStorageMixin
from .submission_lineage import SubmissionRunLineageMixin


class TaskStore(
    RunSessionTraceMixin,
    ExecutionScopeHardeningMixin,
    SkillLifecycleStorageMixin,
    OperationalLessonStorageMixin,
    HelperRecoveryLineageMixin,
    SubmissionRunLineageMixin,
    RunSessionLineageMixin,
    ExecutionIntegrityMixin,
    EnvironmentContractMixin,
    EnvironmentEvidenceMixin,
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
