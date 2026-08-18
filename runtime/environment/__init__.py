"""Declarative execution-environment contracts for MAPS Lean."""

from .fingerprint import (
    CommandResult,
    CompatibilityReport,
    CompatibilityState,
    EnvironmentFingerprint,
    EnvironmentKind,
    ObservationState,
    VersionObservation,
    evaluate_environment_compatibility,
    version_satisfies,
)
from .safety import inspect_local_environment
from .spec import (
    EnvironmentSpec,
    EnvironmentSpecError,
    NetworkMode,
    RepositoryEnvironment,
    ValidationTiers,
    load_environment_spec,
    parse_environment_spec,
)
from .validation import (
    CommandOutcome,
    ValidationTierError,
    ValidationTierResult,
    make_validation_hook,
    run_validation_tier,
)

__all__ = [
    "CommandOutcome",
    "CommandResult",
    "CompatibilityReport",
    "CompatibilityState",
    "EnvironmentFingerprint",
    "EnvironmentKind",
    "EnvironmentSpec",
    "EnvironmentSpecError",
    "NetworkMode",
    "ObservationState",
    "RepositoryEnvironment",
    "ValidationTierError",
    "ValidationTierResult",
    "ValidationTiers",
    "VersionObservation",
    "evaluate_environment_compatibility",
    "inspect_local_environment",
    "load_environment_spec",
    "make_validation_hook",
    "parse_environment_spec",
    "run_validation_tier",
    "version_satisfies",
]
