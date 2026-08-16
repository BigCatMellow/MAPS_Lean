from __future__ import annotations

from enum import Enum
import hashlib
import json
import math
import re
from typing import Mapping, Sequence

from .regression_case import RegressionCaseError, validate_regression_case


class EvaluationError(ValueError):
    pass


class PropertyResultState(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"
    NOT_RUN = "NOT_RUN"


class ComparisonOutcome(str, Enum):
    IMPROVED = "IMPROVED"
    REGRESSED = "REGRESSED"
    UNCHANGED = "UNCHANGED"
    INCOMPLETE = "INCOMPLETE"


_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_IMMUTABLE_REF_RE = re.compile(
    r"^(?:sha256:[0-9a-f]{64}|git:(?:[0-9a-f]{40}|[0-9a-f]{64}))$"
)
_ALLOWED_RESULT_KEYS = {"case_id", "case_sha256", "properties", "measurements"}
_ALLOWED_MEASUREMENT_KEYS = {"cost_usd", "latency_ms"}
_PROMOTION = {
    "automatic": False,
    "path": [
        "frozen cases",
        "candidate results",
        "comparative report",
        "proposal",
        "independent review/operator gate where required",
        "promotion",
    ],
    "rule": "a better evaluation score cannot authorize an automatic production change",
}


def _canonical_hash(value: object) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _require_label(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise EvaluationError(f"{field_name} must be non-empty text")
    return value.strip()


def _require_immutable_ref(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not _IMMUTABLE_REF_RE.fullmatch(value):
        raise EvaluationError(
            f"{field_name} must be an immutable sha256:<64hex> or git:<40/64hex> reference"
        )
    return value


def _validate_cases(cases: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    validated: list[dict[str, object]] = []
    seen: set[str] = set()
    for raw in cases:
        try:
            case = validate_regression_case(raw)
        except RegressionCaseError as exc:
            raise EvaluationError(str(exc)) from exc
        case_id = str(case["case_id"])
        if case_id in seen:
            raise EvaluationError(f"duplicate frozen case: {case_id}")
        seen.add(case_id)
        validated.append(case)
    if not validated:
        raise EvaluationError("at least one frozen regression case is required")
    return sorted(validated, key=lambda item: str(item["case_id"]))


def _validate_measurements(raw: object) -> dict[str, int | float]:
    if raw is None:
        return {}
    if not isinstance(raw, Mapping):
        raise EvaluationError("measurements must be a mapping")
    unknown = set(raw) - _ALLOWED_MEASUREMENT_KEYS
    if unknown:
        raise EvaluationError(f"unknown measurement fields: {sorted(unknown)}")
    output: dict[str, int | float] = {}
    for key, value in raw.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise EvaluationError(f"measurement {key} must be numeric")
        if not math.isfinite(value) or value < 0:
            raise EvaluationError(f"measurement {key} must be finite and non-negative")
        output[key] = value
    return output


def _index_results(
    cases: Sequence[Mapping[str, object]],
    results: Sequence[Mapping[str, object]],
) -> dict[str, dict[str, object]]:
    by_case = {str(case["case_id"]): case for case in cases}
    indexed: dict[str, dict[str, object]] = {}
    for raw in results:
        if not isinstance(raw, Mapping):
            raise EvaluationError("case result must be a mapping")
        unknown_keys = set(raw) - _ALLOWED_RESULT_KEYS
        if unknown_keys:
            raise EvaluationError(f"unknown case result fields: {sorted(unknown_keys)}")
        case_id = _require_label(raw.get("case_id"), "case_id")
        if case_id in indexed:
            raise EvaluationError(f"duplicate result for case: {case_id}")
        case = by_case.get(case_id)
        if case is None:
            raise EvaluationError(f"result references unknown case: {case_id}")
        case_sha = raw.get("case_sha256")
        if not isinstance(case_sha, str) or not _SHA256_RE.fullmatch(case_sha):
            raise EvaluationError(f"result case hash is invalid for {case_id}")
        if case_sha != case["content_sha256"]:
            raise EvaluationError(f"result case hash mismatch for {case_id}")
        properties = raw.get("properties")
        if not isinstance(properties, Mapping):
            raise EvaluationError(f"properties must be a mapping for {case_id}")
        expected = set(case["expected_properties"])
        supplied = set(properties)
        extra = supplied - expected
        if extra:
            raise EvaluationError(f"unknown properties for {case_id}: {sorted(extra)}")
        normalized: dict[str, str] = {}
        for property_id, state in properties.items():
            if not isinstance(property_id, str):
                raise EvaluationError(f"property ID must be text for {case_id}")
            try:
                resolved = state if isinstance(state, PropertyResultState) else PropertyResultState(state)
            except (TypeError, ValueError) as exc:
                raise EvaluationError(
                    f"invalid property result for {case_id}/{property_id}: {state!r}"
                ) from exc
            normalized[property_id] = resolved.value
        indexed[case_id] = {
            "case_id": case_id,
            "case_sha256": case_sha,
            "properties": normalized,
            "measurements": _validate_measurements(raw.get("measurements")),
        }
    return indexed


def _fraction(numerator: int, denominator: int) -> dict[str, int]:
    return {"numerator": numerator, "denominator": denominator}


def _measurement_summary(case_reports: Sequence[Mapping[str, object]]) -> dict[str, object]:
    costs: list[int | float] = []
    latencies: list[int | float] = []
    for case in case_reports:
        measurements = case.get("measurements")
        if not isinstance(measurements, Mapping):
            continue
        if "cost_usd" in measurements:
            costs.append(measurements["cost_usd"])
        if "latency_ms" in measurements:
            latencies.append(measurements["latency_ms"])
    output: dict[str, object] = {}
    if costs:
        output["cost_usd"] = {"measured_cases": len(costs), "total": sum(costs)}
    if latencies:
        output["latency_ms"] = {
            "measured_cases": len(latencies),
            "total": sum(latencies),
            "min": min(latencies),
            "max": max(latencies),
        }
    return output


def evaluate_regression_cases(
    cases: Sequence[Mapping[str, object]],
    results: Sequence[Mapping[str, object]],
    *,
    label: str,
    configuration_ref: str,
) -> dict[str, object]:
    """Build a deterministic read-only report from externally produced results."""

    resolved_label = _require_label(label, "label")
    resolved_configuration_ref = _require_immutable_ref(
        configuration_ref, "configuration_ref"
    )
    validated_cases = _validate_cases(cases)
    indexed_results = _index_results(validated_cases, results)

    corpus_identity = [
        {
            "case_id": case["case_id"],
            "content_sha256": case["content_sha256"],
            "expected_properties": case["expected_properties"],
        }
        for case in validated_cases
    ]
    corpus_sha = _canonical_hash(corpus_identity)

    case_reports: list[dict[str, object]] = []
    property_counts = {
        "expected": 0,
        "reported": 0,
        "complete": 0,
        "pass": 0,
        "fail": 0,
        "unknown": 0,
        "not_run": 0,
        "missing": 0,
    }
    case_counts = {
        "total": len(validated_cases),
        "complete": 0,
        "pass": 0,
        "fail": 0,
        "incomplete": 0,
    }

    for case in validated_cases:
        case_id = str(case["case_id"])
        supplied = indexed_results.get(case_id)
        supplied_properties = supplied["properties"] if supplied else {}
        rows: list[dict[str, object]] = []
        local = {
            "expected": len(case["expected_properties"]),
            "reported": 0,
            "pass": 0,
            "fail": 0,
            "unknown": 0,
            "not_run": 0,
            "missing": 0,
        }
        for property_id in case["expected_properties"]:
            property_counts["expected"] += 1
            if property_id not in supplied_properties:
                local["missing"] += 1
                property_counts["missing"] += 1
                rows.append(
                    {"property_id": property_id, "reported": False, "status": None}
                )
                continue
            status = supplied_properties[property_id]
            local["reported"] += 1
            property_counts["reported"] += 1
            key = status.lower()
            local[key] += 1
            property_counts[key] += 1
            if status in {PropertyResultState.PASS.value, PropertyResultState.FAIL.value}:
                property_counts["complete"] += 1
            rows.append(
                {"property_id": property_id, "reported": True, "status": status}
            )

        incomplete = bool(local["missing"] or local["unknown"] or local["not_run"])
        if incomplete:
            case_status = "INCOMPLETE"
            case_counts["incomplete"] += 1
        elif local["fail"]:
            case_status = "FAIL"
            case_counts["complete"] += 1
            case_counts["fail"] += 1
        else:
            case_status = "PASS"
            case_counts["complete"] += 1
            case_counts["pass"] += 1

        case_report: dict[str, object] = {
            "case_id": case_id,
            "case_sha256": case["content_sha256"],
            "incident_category": case["incident_category"],
            "tags": list(case["tags"]),
            "status": case_status,
            "properties": rows,
            "metrics": local,
        }
        if supplied and supplied["measurements"]:
            case_report["measurements"] = dict(supplied["measurements"])
        case_reports.append(case_report)

    metrics: dict[str, object] = {
        "cases": case_counts,
        "properties": property_counts,
        "case_pass_fraction_all": _fraction(
            case_counts["pass"], case_counts["total"]
        ),
        "property_pass_fraction_completed": _fraction(
            property_counts["pass"], property_counts["complete"]
        ),
    }
    measurements = _measurement_summary(case_reports)
    if measurements:
        metrics["measurements"] = measurements

    payload: dict[str, object] = {
        "report_version": 1,
        "report_kind": "MAPS_REGRESSION_EVALUATION_REPORT",
        "label": resolved_label,
        "configuration_ref": resolved_configuration_ref,
        "corpus_id": f"CORPUS-{corpus_sha}",
        "corpus_sha256": corpus_sha,
        "cases": case_reports,
        "metrics": metrics,
        "promotion": _PROMOTION,
    }
    digest = _canonical_hash(payload)
    return {"report_id": f"EVAL-{digest}", "content_sha256": digest, **payload}


def _property_outcome(baseline: object, candidate: object) -> str:
    concrete = {PropertyResultState.PASS.value, PropertyResultState.FAIL.value}
    if baseline not in concrete or candidate not in concrete:
        return ComparisonOutcome.INCOMPLETE.value
    if (
        baseline == PropertyResultState.FAIL.value
        and candidate == PropertyResultState.PASS.value
    ):
        return ComparisonOutcome.IMPROVED.value
    if (
        baseline == PropertyResultState.PASS.value
        and candidate == PropertyResultState.FAIL.value
    ):
        return ComparisonOutcome.REGRESSED.value
    return ComparisonOutcome.UNCHANGED.value


def _case_outcome(counts: Mapping[str, int]) -> str:
    if counts[ComparisonOutcome.INCOMPLETE.value] > 0:
        return ComparisonOutcome.INCOMPLETE.value
    if counts[ComparisonOutcome.REGRESSED.value] > 0:
        return ComparisonOutcome.REGRESSED.value
    if counts[ComparisonOutcome.IMPROVED.value] > 0:
        return ComparisonOutcome.IMPROVED.value
    return ComparisonOutcome.UNCHANGED.value


def _paired_measurements(
    baseline_cases: Mapping[str, Mapping[str, object]],
    candidate_cases: Mapping[str, Mapping[str, object]],
) -> dict[str, object]:
    output: dict[str, object] = {}
    for field in ("cost_usd", "latency_ms"):
        pairs: list[tuple[int | float, int | float]] = []
        for case_id in sorted(baseline_cases):
            b = baseline_cases[case_id].get("measurements")
            c = candidate_cases[case_id].get("measurements")
            if (
                isinstance(b, Mapping)
                and isinstance(c, Mapping)
                and field in b
                and field in c
            ):
                pairs.append((b[field], c[field]))
        if pairs:
            baseline_total = sum(item[0] for item in pairs)
            candidate_total = sum(item[1] for item in pairs)
            output[field] = {
                "paired_cases": len(pairs),
                "baseline_total": baseline_total,
                "candidate_total": candidate_total,
                "candidate_minus_baseline": candidate_total - baseline_total,
            }
    return output


def compare_regression_cases(
    cases: Sequence[Mapping[str, object]],
    baseline_results: Sequence[Mapping[str, object]],
    candidate_results: Sequence[Mapping[str, object]],
    *,
    baseline_ref: str,
    candidate_ref: str,
    baseline_label: str = "baseline",
    candidate_label: str = "candidate",
) -> dict[str, object]:
    """Compare baseline and candidate on the same exact frozen corpus."""

    baseline = evaluate_regression_cases(
        cases,
        baseline_results,
        label=baseline_label,
        configuration_ref=baseline_ref,
    )
    candidate = evaluate_regression_cases(
        cases,
        candidate_results,
        label=candidate_label,
        configuration_ref=candidate_ref,
    )
    if baseline["corpus_id"] != candidate["corpus_id"]:
        raise EvaluationError("baseline and candidate corpus identity mismatch")

    baseline_cases = {
        str(item["case_id"]): item for item in baseline["cases"]
    }
    candidate_cases = {
        str(item["case_id"]): item for item in candidate["cases"]
    }
    case_rows: list[dict[str, object]] = []
    property_counts = {item.value: 0 for item in ComparisonOutcome}
    case_counts = {item.value: 0 for item in ComparisonOutcome}

    for case_id in sorted(baseline_cases):
        bcase = baseline_cases[case_id]
        ccase = candidate_cases[case_id]
        bprops = {
            row["property_id"]: row["status"] for row in bcase["properties"]
        }
        cprops = {
            row["property_id"]: row["status"] for row in ccase["properties"]
        }
        local_counts = {item.value: 0 for item in ComparisonOutcome}
        properties: list[dict[str, object]] = []
        for property_id in sorted(bprops):
            outcome = _property_outcome(
                bprops[property_id], cprops[property_id]
            )
            property_counts[outcome] += 1
            local_counts[outcome] += 1
            properties.append(
                {
                    "property_id": property_id,
                    "baseline": bprops[property_id],
                    "candidate": cprops[property_id],
                    "outcome": outcome,
                }
            )
        outcome = _case_outcome(local_counts)
        case_counts[outcome] += 1
        case_rows.append(
            {
                "case_id": case_id,
                "case_sha256": bcase["case_sha256"],
                "incident_category": bcase["incident_category"],
                "tags": list(bcase["tags"]),
                "outcome": outcome,
                "has_improvement": local_counts[ComparisonOutcome.IMPROVED.value] > 0,
                "has_regression": local_counts[ComparisonOutcome.REGRESSED.value] > 0,
                "properties": properties,
                "metrics": local_counts,
            }
        )

    payload: dict[str, object] = {
        "comparison_version": 1,
        "comparison_kind": "MAPS_REGRESSION_COMPARATIVE_REPORT",
        "corpus_id": baseline["corpus_id"],
        "corpus_sha256": baseline["corpus_sha256"],
        "baseline": {
            "label": baseline["label"],
            "configuration_ref": baseline["configuration_ref"],
            "report_id": baseline["report_id"],
            "content_sha256": baseline["content_sha256"],
            "metrics": baseline["metrics"],
        },
        "candidate": {
            "label": candidate["label"],
            "configuration_ref": candidate["configuration_ref"],
            "report_id": candidate["report_id"],
            "content_sha256": candidate["content_sha256"],
            "metrics": candidate["metrics"],
        },
        "cases": case_rows,
        "metrics": {"cases": case_counts, "properties": property_counts},
        "promotion": _PROMOTION,
    }
    paired = _paired_measurements(baseline_cases, candidate_cases)
    if paired:
        payload["measurement_comparison"] = paired
    digest = _canonical_hash(payload)
    return {
        "comparison_id": f"CMP-{digest}",
        "content_sha256": digest,
        **payload,
    }


def dumps_evaluation_report(report: Mapping[str, object]) -> str:
    return json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False)
