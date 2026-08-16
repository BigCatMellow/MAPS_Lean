"""Evaluation artifacts and frozen regression evidence for MAPS Lean."""

from .evaluator import (
    ComparisonOutcome,
    EvaluationError,
    PropertyResultState,
    compare_regression_cases,
    dumps_evaluation_report,
    evaluate_regression_cases,
)
from .regression_case import (
    IncidentCategory,
    RegressionCaseError,
    dumps_regression_case,
    freeze_regression_case,
    validate_regression_case,
)

__all__ = [
    "ComparisonOutcome",
    "EvaluationError",
    "IncidentCategory",
    "PropertyResultState",
    "RegressionCaseError",
    "compare_regression_cases",
    "dumps_evaluation_report",
    "dumps_regression_case",
    "evaluate_regression_cases",
    "freeze_regression_case",
    "validate_regression_case",
]
