from __future__ import annotations

from enum import Enum
import hashlib
import json
import re
from typing import Mapping, Sequence

from runtime.state.observability import redact_sensitive_text


class RegressionCaseError(ValueError):
    pass


class IncidentCategory(str, Enum):
    TOOL_FAILURE = "TOOL_FAILURE"
    CONTEXT_OMISSION = "CONTEXT_OMISSION"
    CONTEXT_POISONING = "CONTEXT_POISONING"
    ROUTING_ERROR = "ROUTING_ERROR"
    SKILL_ROUTING_ERROR = "SKILL_ROUTING_ERROR"
    HELPER_FAILURE = "HELPER_FAILURE"
    HELPER_NO_PROGRESS = "HELPER_NO_PROGRESS"
    RECOVERY_FAILURE = "RECOVERY_FAILURE"
    DUPLICATE_EXECUTION = "DUPLICATE_EXECUTION"
    ENVIRONMENT_DRIFT = "ENVIRONMENT_DRIFT"
    REVIEW_MISS = "REVIEW_MISS"
    STALE_REVIEW_EVIDENCE = "STALE_REVIEW_EVIDENCE"
    VALIDATOR_FALSE_POSITIVE = "VALIDATOR_FALSE_POSITIVE"
    VALIDATOR_FALSE_NEGATIVE = "VALIDATOR_FALSE_NEGATIVE"
    AUTHORITY_VIOLATION_ATTEMPT = "AUTHORITY_VIOLATION_ATTEMPT"
    ACI_AMBIGUITY = "ACI_AMBIGUITY"
    SUPPLY_CHAIN_DEFECT = "SUPPLY_CHAIN_DEFECT"
    OPERATOR_FRICTION_INTERVENTION = "OPERATOR_FRICTION_INTERVENTION"
    UNKNOWN = "UNKNOWN"


_PROPERTY_RE = re.compile(r"^[a-z][a-z0-9_.:-]{0,127}$")
_TAG_RE = re.compile(r"^[a-z0-9][a-z0-9_.:-]{0,63}$")
_MAX_FIXTURE_CHARS = 12_000


def _canonical_hash(value: object) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _require_text(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RegressionCaseError(f"{field_name} must be non-empty text")
    return value.strip()


def _normalize_ids(
    values: Sequence[str],
    *,
    field_name: str,
    pattern: re.Pattern[str],
) -> tuple[str, ...]:
    normalized: list[str] = []
    for raw in values:
        value = _require_text(raw, field_name).lower()
        if not pattern.fullmatch(value):
            raise RegressionCaseError(f"invalid {field_name}: {raw!r}")
        normalized.append(value)
    if len(set(normalized)) != len(normalized):
        raise RegressionCaseError(f"{field_name} contains duplicates")
    return tuple(sorted(normalized))


def _validate_run_record(run_record: Mapping[str, object]) -> dict[str, object]:
    record = dict(run_record)
    if record.get("record_version") != 1:
        raise RegressionCaseError("only portable Run Record v1 can be frozen")
    content_sha = record.get("content_sha256")
    record_id = record.get("record_id")
    if not isinstance(content_sha, str) or not re.fullmatch(r"[0-9a-f]{64}", content_sha):
        raise RegressionCaseError("Run Record content_sha256 is invalid")
    if record_id != f"RR-{content_sha}":
        raise RegressionCaseError("Run Record record_id/content_sha256 mismatch")
    payload = {
        key: value
        for key, value in record.items()
        if key not in {"record_id", "content_sha256"}
    }
    if _canonical_hash(payload) != content_sha:
        raise RegressionCaseError("Run Record content hash does not match its payload")
    replay = record.get("replay")
    if not isinstance(replay, Mapping) or replay.get("complete") is not False:
        raise RegressionCaseError(
            "Run Record v1 regression cases must preserve explicit partial-replay semantics"
        )
    return record


def validate_regression_case(case: Mapping[str, object]) -> dict[str, object]:
    """Validate one exact frozen regression case without mutating any source state."""

    if not isinstance(case, Mapping):
        raise RegressionCaseError("regression case must be a mapping")
    record = dict(case)
    if record.get("case_version") != 1:
        raise RegressionCaseError("only frozen regression case v1 is supported")
    if record.get("case_kind") != "MAPS_FROZEN_REGRESSION_CASE":
        raise RegressionCaseError("regression case kind is invalid")

    content_sha = record.get("content_sha256")
    case_id = record.get("case_id")
    if not isinstance(content_sha, str) or not re.fullmatch(r"[0-9a-f]{64}", content_sha):
        raise RegressionCaseError("regression case content_sha256 is invalid")
    if case_id != f"CASE-{content_sha}":
        raise RegressionCaseError("regression case case_id/content_sha256 mismatch")
    payload = {
        key: value
        for key, value in record.items()
        if key not in {"case_id", "content_sha256"}
    }
    if _canonical_hash(payload) != content_sha:
        raise RegressionCaseError("regression case content hash does not match its payload")

    try:
        IncidentCategory(record.get("incident_category"))
    except (TypeError, ValueError) as exc:
        raise RegressionCaseError("regression case incident_category is invalid") from exc

    source = record.get("source_run_record")
    if not isinstance(source, Mapping):
        raise RegressionCaseError("regression case source_run_record is invalid")
    validated_source = _validate_run_record(source)
    if record.get("source_run_record_id") != validated_source["record_id"]:
        raise RegressionCaseError("regression case source Run Record ID mismatch")
    if record.get("source_run_record_sha256") != validated_source["content_sha256"]:
        raise RegressionCaseError("regression case source Run Record hash mismatch")

    fixture = _require_text(record.get("sanitized_fixture"), "sanitized_fixture")
    if fixture != record.get("sanitized_fixture"):
        raise RegressionCaseError("sanitized_fixture is not normalized")
    if len(fixture) > _MAX_FIXTURE_CHARS:
        raise RegressionCaseError(
            f"sanitized_fixture exceeds {_MAX_FIXTURE_CHARS} characters"
        )
    if redact_sensitive_text(fixture) != fixture:
        raise RegressionCaseError("sanitized_fixture contains text recognized as sensitive")

    actor = _require_text(record.get("frozen_by"), "frozen_by")
    if actor != record.get("frozen_by"):
        raise RegressionCaseError("frozen_by is not normalized")
    if redact_sensitive_text(actor) != actor:
        raise RegressionCaseError("frozen_by appears to contain sensitive text")

    raw_properties = record.get("expected_properties")
    if not isinstance(raw_properties, list):
        raise RegressionCaseError("expected_properties must be a list")
    properties = _normalize_ids(
        raw_properties,
        field_name="expected_properties",
        pattern=_PROPERTY_RE,
    )
    if not properties:
        raise RegressionCaseError("expected_properties cannot be empty")
    if list(properties) != raw_properties:
        raise RegressionCaseError("expected_properties are not normalized")

    raw_tags = record.get("tags")
    if not isinstance(raw_tags, list):
        raise RegressionCaseError("tags must be a list")
    tags = _normalize_ids(raw_tags, field_name="tags", pattern=_TAG_RE)
    if list(tags) != raw_tags:
        raise RegressionCaseError("tags are not normalized")

    promotion = record.get("promotion")
    if not isinstance(promotion, Mapping) or promotion.get("automatic") is not False:
        raise RegressionCaseError("regression case must explicitly disable automatic promotion")
    return record


def freeze_regression_case(
    run_record: Mapping[str, object],
    *,
    category: IncidentCategory | str,
    sanitized_fixture: str,
    expected_properties: Sequence[str],
    frozen_by: str,
    tags: Sequence[str] = (),
) -> dict[str, object]:
    """Create one deterministic frozen regression-case artifact.

    This function classifies nothing automatically and promotes nothing. The
    caller explicitly supplies the incident category, sanitized fixture, and
    expected property IDs after triage/review.
    """

    source = _validate_run_record(run_record)
    try:
        resolved_category = (
            category if isinstance(category, IncidentCategory) else IncidentCategory(category)
        )
    except ValueError as exc:
        raise RegressionCaseError(f"unknown incident category: {category}") from exc

    fixture = _require_text(sanitized_fixture, "sanitized_fixture")
    if len(fixture) > _MAX_FIXTURE_CHARS:
        raise RegressionCaseError(
            f"sanitized_fixture exceeds {_MAX_FIXTURE_CHARS} characters"
        )
    if redact_sensitive_text(fixture) != fixture:
        raise RegressionCaseError(
            "sanitized_fixture contains text recognized as sensitive; redact it before freezing"
        )
    actor = _require_text(frozen_by, "frozen_by")
    if redact_sensitive_text(actor) != actor:
        raise RegressionCaseError("frozen_by appears to contain sensitive text")

    properties = _normalize_ids(
        expected_properties,
        field_name="expected_properties",
        pattern=_PROPERTY_RE,
    )
    if not properties:
        raise RegressionCaseError("expected_properties cannot be empty")
    normalized_tags = _normalize_ids(tags, field_name="tags", pattern=_TAG_RE)

    payload: dict[str, object] = {
        "case_version": 1,
        "case_kind": "MAPS_FROZEN_REGRESSION_CASE",
        "incident_category": resolved_category.value,
        "source_run_record_id": source["record_id"],
        "source_run_record_sha256": source["content_sha256"],
        "source_run_record": source,
        "sanitized_fixture": fixture,
        "expected_properties": list(properties),
        "tags": list(normalized_tags),
        "frozen_by": actor,
        "promotion": {
            "automatic": False,
            "reason": (
                "frozen cases are evaluation evidence only; passing a case cannot "
                "self-authorize a harness/policy/routing change"
            ),
        },
    }
    digest = _canonical_hash(payload)
    return {
        "case_id": f"CASE-{digest}",
        "content_sha256": digest,
        **payload,
    }


def dumps_regression_case(case: Mapping[str, object]) -> str:
    return json.dumps(case, indent=2, sort_keys=True, ensure_ascii=False)
