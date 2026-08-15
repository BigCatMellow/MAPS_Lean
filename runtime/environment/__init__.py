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

__all__ = [
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
    "ValidationTiers",
    "VersionObservation",
    "evaluate_environment_compatibility",
    "inspect_local_environment",
    "load_environment_spec",
    "parse_environment_spec",
    "version_satisfies",
]
