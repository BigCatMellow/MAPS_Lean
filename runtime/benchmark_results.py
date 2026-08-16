from __future__ import annotations

import math
from typing import Mapping, Sequence


class BenchmarkResultError(ValueError):
    pass


_RESULT_KEYS = {
    "scenario_id",
    "evidence_class",
    "fixture_kind",
    "properties",
    "provenance",
    "measurements",
}
_PROPERTY_KEYS = {"state", "evidence_refs"}
_PROVENANCE_KEYS = {
    "task",
    "run",
    "outcome",
    "operator_visible_result",
    "external_authority",
    "operator_intervention",
}
_PROVENANCE_ITEM_KEYS = {"state", "ref"}
_PROVENANCE_STATES = {"VERIFIED", "UNKNOWN", "NOT_APPLICABLE"}
_FIXTURE_KINDS = {
    "CONTROLLED_SYNTHETIC",
    "CONTROLLED_REAL",
    "REAL_PRODUCTION",
}
_MEASUREMENTS = {
    "runtime_ms",
    "cost_usd",
    "tool_calls",
    "messages",
    "agent_count",
    "operator_intervention_count",
    "rework_count",
}
_COUNT_MEASUREMENTS = {
    "tool_calls",
    "messages",
    "agent_count",
    "operator_intervention_count",
    "rework_count",
}


def _text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise BenchmarkResultError(f"{field} must be non-empty text")
    return value.strip()


def _validate_protocol(protocol: Mapping[str, object]):
    if protocol.get("version") != "maps-end-to-end-benchmark-v1":
        raise BenchmarkResultError("unsupported benchmark protocol version")
    states = protocol.get("result_states")
    scenarios = protocol.get("scenarios")
    if not isinstance(states, list) or not states:
        raise BenchmarkResultError("result_states must be a non-empty list")
    if not isinstance(scenarios, list) or not scenarios:
        raise BenchmarkResultError("scenarios must be a non-empty list")
    allowed_states = {_text(x, "result_state") for x in states}

    indexed = {}
    for raw in scenarios:
        if not isinstance(raw, Mapping):
            raise BenchmarkResultError("scenario must be a mapping")
        scenario_id = _text(raw.get("id"), "scenario.id")
        if scenario_id in indexed:
            raise BenchmarkResultError(f"duplicate scenario: {scenario_id}")
        layer = _text(raw.get("layer"), f"{scenario_id}.layer")
        if layer not in {"LAYER_2_CONTROLLED", "LAYER_3_PRODUCTION_OUTCOME"}:
            raise BenchmarkResultError(f"{scenario_id}: unsupported layer")
        props = raw.get("properties")
        if not isinstance(props, list) or not props:
            raise BenchmarkResultError(f"{scenario_id}: properties are missing")
        normalized_props = {}
        for prop in props:
            if not isinstance(prop, Mapping):
                raise BenchmarkResultError(f"{scenario_id}: property must be a mapping")
            prop_id = _text(prop.get("id"), f"{scenario_id}.property.id")
            if prop_id in normalized_props:
                raise BenchmarkResultError(f"{scenario_id}: duplicate property {prop_id}")
            kind = _text(prop.get("kind"), f"{scenario_id}.{prop_id}.kind")
            if kind not in {"BLOCKER", "QUALITY"}:
                raise BenchmarkResultError(f"{scenario_id}.{prop_id}: invalid kind")
            normalized_props[prop_id] = {
                "kind": kind,
                "required": prop.get("required") is True,
            }
        eligibility = raw.get("eligibility")
        if eligibility is not None and not isinstance(eligibility, Mapping):
            raise BenchmarkResultError(f"{scenario_id}: eligibility must be a mapping")
        indexed[scenario_id] = {
            "id": scenario_id,
            "layer": layer,
            "required": raw.get("required") is True,
            "external_operator_visible": raw.get("external_operator_visible") is True,
            "synthetic_fixture": raw.get("synthetic_fixture"),
            "properties": normalized_props,
            "eligibility": dict(eligibility or {}),
        }
    return indexed, allowed_states


def _property_result(raw: object, allowed_states: set[str], field: str):
    if not isinstance(raw, Mapping) or set(raw) != _PROPERTY_KEYS:
        raise BenchmarkResultError(f"{field} must contain exactly state/evidence_refs")
    state = _text(raw.get("state"), f"{field}.state")
    if state not in allowed_states:
        raise BenchmarkResultError(f"{field}: unsupported state {state}")
    refs = raw.get("evidence_refs")
    if not isinstance(refs, list) or not all(
        isinstance(x, str) and x.strip() for x in refs
    ):
        raise BenchmarkResultError(f"{field}.evidence_refs must be a text list")
    refs = [x.strip() for x in refs]
    if len(refs) != len(set(refs)):
        raise BenchmarkResultError(f"{field}.evidence_refs contains duplicates")
    if state in {"PASS", "FAIL"} and not refs:
        raise BenchmarkResultError(f"{field}: PASS/FAIL requires observable evidence refs")
    if state in {"UNKNOWN", "NOT_RUN"} and refs:
        raise BenchmarkResultError(f"{field}: UNKNOWN/NOT_RUN cannot claim evidence refs")
    return {"state": state, "evidence_refs": refs}


def _provenance_item(raw: object, field: str):
    if not isinstance(raw, Mapping) or set(raw) != _PROVENANCE_ITEM_KEYS:
        raise BenchmarkResultError(f"{field} must contain exactly state/ref")
    state = _text(raw.get("state"), f"{field}.state")
    if state not in _PROVENANCE_STATES:
        raise BenchmarkResultError(f"{field}: invalid provenance state")
    ref = raw.get("ref")
    if state == "VERIFIED":
        ref = _text(ref, f"{field}.ref")
    elif ref is not None:
        raise BenchmarkResultError(f"{field}: non-VERIFIED provenance must use ref=null")
    return {"state": state, "ref": ref}


def _provenance(raw: object, field: str):
    if raw is None:
        return {
            key: {"state": "NOT_APPLICABLE", "ref": None}
            for key in _PROVENANCE_KEYS
        }
    if not isinstance(raw, Mapping) or set(raw) != _PROVENANCE_KEYS:
        raise BenchmarkResultError(f"{field} must contain the complete provenance key set")
    return {
        key: _provenance_item(raw[key], f"{field}.{key}")
        for key in sorted(_PROVENANCE_KEYS)
    }


def _measurements(raw: object, field: str):
    if raw is None:
        return {}
    if not isinstance(raw, Mapping) or set(raw) - _MEASUREMENTS:
        raise BenchmarkResultError(f"{field}: unknown measurement fields")
    output = {}
    for key, value in raw.items():
        if key in _COUNT_MEASUREMENTS:
            if isinstance(value, bool) or not isinstance(value, int):
                raise BenchmarkResultError(
                    f"{field}.{key} must be a non-negative integer count"
                )
        elif isinstance(value, bool) or not isinstance(value, (int, float)):
            raise BenchmarkResultError(f"{field}.{key} must be numeric")
        if not math.isfinite(value) or value < 0:
            raise BenchmarkResultError(
                f"{field}.{key} must be finite and non-negative"
            )
        output[key] = value
    return output


def _result(raw: Mapping[str, object], allowed_states: set[str]):
    if set(raw) - _RESULT_KEYS:
        raise BenchmarkResultError("scenario result has unknown fields")
    scenario_id = _text(raw.get("scenario_id"), "scenario_id")
    evidence_class = _text(raw.get("evidence_class"), f"{scenario_id}.evidence_class")
    fixture_kind = _text(raw.get("fixture_kind"), f"{scenario_id}.fixture_kind")
    if fixture_kind not in _FIXTURE_KINDS:
        raise BenchmarkResultError(f"{scenario_id}: invalid fixture_kind")
    props = raw.get("properties")
    if not isinstance(props, Mapping):
        raise BenchmarkResultError(f"{scenario_id}.properties must be a mapping")
    properties = {
        _text(prop_id, f"{scenario_id}.property_id"): _property_result(
            value, allowed_states, f"{scenario_id}.{prop_id}"
        )
        for prop_id, value in props.items()
    }
    return {
        "scenario_id": scenario_id,
        "evidence_class": evidence_class,
        "fixture_kind": fixture_kind,
        "properties": properties,
        "provenance": _provenance(raw.get("provenance"), f"{scenario_id}.provenance"),
        "measurements": _measurements(
            raw.get("measurements"), f"{scenario_id}.measurements"
        ),
    }


def _verified(provenance, key: str) -> bool:
    return provenance[key]["state"] == "VERIFIED"


def _eligibility(scenario, result):
    layer = scenario["layer"]
    fixture_kind = result["fixture_kind"]
    provenance = result["provenance"]
    measurements = result["measurements"]

    if result["evidence_class"] != layer:
        return "FAIL", ["evidence_class_mismatch"]

    reasons = []
    incomplete = []
    if layer == "LAYER_2_CONTROLLED":
        if fixture_kind not in {"CONTROLLED_SYNTHETIC", "CONTROLLED_REAL"}:
            reasons.append("layer2_invalid_fixture_kind")
        return ("FAIL", reasons) if reasons else ("PASS", [])

    if fixture_kind != "REAL_PRODUCTION":
        reasons.append("layer3_synthetic_or_controlled_fixture_forbidden")
        return "FAIL", reasons

    required_verified = {"task", "run", "outcome"}
    eligibility = scenario["eligibility"]
    if eligibility.get("requires_operator_or_user_visible_result") is True:
        required_verified.add("operator_visible_result")
    if eligibility.get("requires_existing_task_authority_for_external_effect") is True:
        required_verified.add("external_authority")
    if eligibility.get("requires_real_outcome_observation") is True:
        required_verified.add("outcome")

    for key in sorted(required_verified):
        state = provenance[key]["state"]
        if state != "VERIFIED":
            incomplete.append(f"{key}_provenance_{state.lower()}")

    interventions = measurements.get("operator_intervention_count", 0)
    if (
        eligibility.get("requires_operator_intervention_provenance_if_counted") is True
        and interventions > 0
        and not _verified(provenance, "operator_intervention")
    ):
        incomplete.append("operator_intervention_provenance_unverified")

    return ("INCOMPLETE", incomplete) if incomplete else ("PASS", [])


def _score_scenario(scenario, result):
    expected_props = scenario["properties"]
    if result is None:
        return {
            "scenario_id": scenario["id"],
            "layer": scenario["layer"],
            "status": "INCOMPLETE",
            "eligibility_status": "INCOMPLETE",
            "eligibility_reasons": ["scenario_result_missing"],
            "properties": [
                {
                    "property_id": prop_id,
                    "kind": meta["kind"],
                    "required": meta["required"],
                    "state": "NOT_RUN",
                    "evidence_ref_count": 0,
                }
                for prop_id, meta in expected_props.items()
            ],
            "blocker_failures": [],
            "measurements": {},
        }

    extra = set(result["properties"]) - set(expected_props)
    if extra:
        raise BenchmarkResultError(
            f"{scenario['id']}: unknown properties {sorted(extra)}"
        )

    rows = []
    blocker_failures = []
    any_fail = False
    any_incomplete = False
    for prop_id, meta in expected_props.items():
        supplied = result["properties"].get(prop_id)
        state = supplied["state"] if supplied else "NOT_RUN"
        refs = supplied["evidence_refs"] if supplied else []
        if meta["required"]:
            if state == "FAIL":
                any_fail = True
                if meta["kind"] == "BLOCKER":
                    blocker_failures.append(prop_id)
            elif state in {"UNKNOWN", "NOT_RUN"}:
                any_incomplete = True
        rows.append(
            {
                "property_id": prop_id,
                "kind": meta["kind"],
                "required": meta["required"],
                "state": state,
                "evidence_ref_count": len(refs),
            }
        )

    eligibility_status, reasons = _eligibility(scenario, result)
    if eligibility_status == "FAIL" or any_fail:
        status = "FAIL"
    elif eligibility_status == "INCOMPLETE" or any_incomplete:
        status = "INCOMPLETE"
    else:
        status = "PASS"

    return {
        "scenario_id": scenario["id"],
        "layer": scenario["layer"],
        "status": status,
        "eligibility_status": eligibility_status,
        "eligibility_reasons": reasons,
        "properties": rows,
        "blocker_failures": blocker_failures,
        "measurements": dict(result["measurements"]),
    }


def evaluate_benchmark_results(
    protocol: Mapping[str, object],
    results: Sequence[Mapping[str, object]],
    *,
    label: str,
) -> dict[str, object]:
    """Validate externally produced benchmark evidence without executing a scenario."""

    resolved_label = _text(label, "label")
    scenarios, allowed_states = _validate_protocol(protocol)
    indexed = {}
    for raw in results:
        if not isinstance(raw, Mapping):
            raise BenchmarkResultError("scenario result must be a mapping")
        item = _result(raw, allowed_states)
        scenario_id = item["scenario_id"]
        if scenario_id not in scenarios:
            raise BenchmarkResultError(f"unknown scenario: {scenario_id}")
        if scenario_id in indexed:
            raise BenchmarkResultError(f"duplicate scenario result: {scenario_id}")
        indexed[scenario_id] = item

    reports = [
        _score_scenario(scenario, indexed.get(scenario_id))
        for scenario_id, scenario in scenarios.items()
    ]
    blocker_failures = [
        {"scenario_id": report["scenario_id"], "property_id": prop_id}
        for report in reports
        for prop_id in report["blocker_failures"]
    ]
    if any(report["status"] == "FAIL" for report in reports):
        benchmark_status = "FAIL"
    elif any(report["status"] == "INCOMPLETE" for report in reports):
        benchmark_status = "INCOMPLETE"
    else:
        benchmark_status = "COMPLETE"

    completion = protocol.get("benchmark_completion")
    if not isinstance(completion, Mapping):
        raise BenchmarkResultError("benchmark_completion is missing")
    external_id = completion.get("real_external_or_operator_visible_scenario")
    external_report = next(
        (x for x in reports if x["scenario_id"] == external_id),
        None,
    )
    if external_report is None:
        raise BenchmarkResultError("external/operator-visible scenario is missing")

    return {
        "report_version": 1,
        "report_kind": "MAPS_END_TO_END_BENCHMARK_REPORT",
        "label": resolved_label,
        "protocol_version": protocol["version"],
        "benchmark_status": benchmark_status,
        "cases": {
            "total": len(reports),
            "pass": sum(x["status"] == "PASS" for x in reports),
            "fail": sum(x["status"] == "FAIL" for x in reports),
            "incomplete": sum(x["status"] == "INCOMPLETE" for x in reports),
        },
        "layer_counts": {
            layer: {
                "pass": sum(
                    x["layer"] == layer and x["status"] == "PASS" for x in reports
                ),
                "fail": sum(
                    x["layer"] == layer and x["status"] == "FAIL" for x in reports
                ),
                "incomplete": sum(
                    x["layer"] == layer and x["status"] == "INCOMPLETE"
                    for x in reports
                ),
            }
            for layer in ("LAYER_2_CONTROLLED", "LAYER_3_PRODUCTION_OUTCOME")
        },
        "external_operator_visible_case_passed": external_report["status"] == "PASS",
        "blocker_failures": blocker_failures,
        "scenarios": reports,
        "candidate_advancement_gate": (
            "BLOCKED"
            if blocker_failures or benchmark_status == "FAIL"
            else "INCOMPLETE"
            if benchmark_status == "INCOMPLETE"
            else "EVALUATION_COMPLETE_NOT_AUTHORIZED"
        ),
        "promotion": {
            "automatic": False,
            "rule": completion.get("promotion_rule"),
        },
    }
