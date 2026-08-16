from __future__ import annotations

import hashlib
import json
import re
from typing import Mapping, Sequence


class AcquisitionEvidenceError(ValueError):
    pass


_MANIFEST_KEYS = {"version", "release_id", "paths"}
_PATH_KEYS = {
    "path_id",
    "kind",
    "expected_ref",
    "operator_visible",
    "allow_not_applicable",
}
_OBSERVATION_KEYS = {
    "path_id",
    "acquisition_state",
    "observed_ref",
    "acquisition_evidence_ref",
    "usability_state",
    "usability_evidence_ref",
    "not_applicable_decision_ref",
}
_PATH_KINDS = {
    "DOWNLOAD",
    "INSTALL",
    "ARCHIVE",
    "OPERATOR_ARTIFACT",
    "SERVICE",
}
_ACQUISITION_STATES = {"OBSERVED", "UNREACHABLE", "UNKNOWN", "NOT_APPLICABLE"}
_USABILITY_STATES = {"VERIFIED", "FAILED", "UNKNOWN", "NOT_APPLICABLE"}
_REF_RE = re.compile(r"^(?:sha256:[0-9a-f]{64}|git:(?:[0-9a-f]{40}|[0-9a-f]{64}))$")
_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:@/-]{0,127}$")
_EVIDENCE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:@/#+=-]{0,255}$")


def _text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AcquisitionEvidenceError(f"{field} must be non-empty text")
    return value.strip()


def _id(value: object, field: str) -> str:
    text = _text(value, field)
    if not _ID_RE.fullmatch(text):
        raise AcquisitionEvidenceError(f"{field} is invalid")
    return text


def _immutable_ref(value: object, field: str) -> str:
    text = _text(value, field).lower()
    if not _REF_RE.fullmatch(text):
        raise AcquisitionEvidenceError(
            f"{field} must be sha256:<64hex> or git:<40/64hex>"
        )
    return text


def _optional_evidence_ref(value: object, field: str) -> str | None:
    if value is None:
        return None
    text = _text(value, field)
    if not _EVIDENCE_RE.fullmatch(text):
        raise AcquisitionEvidenceError(f"{field} is invalid")
    return text


def _hash(value: object) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _manifest(raw: Mapping[str, object]) -> dict[str, object]:
    if set(raw) != _MANIFEST_KEYS:
        raise AcquisitionEvidenceError("manifest fields are invalid")
    if raw.get("version") != "maps-acquisition-paths-v1":
        raise AcquisitionEvidenceError("unsupported acquisition manifest version")
    release_id = _id(raw.get("release_id"), "release_id")
    raw_paths = raw.get("paths")
    if not isinstance(raw_paths, list) or not raw_paths:
        raise AcquisitionEvidenceError("manifest paths must be a non-empty list")

    paths: list[dict[str, object]] = []
    seen: set[str] = set()
    for raw_path in raw_paths:
        if not isinstance(raw_path, Mapping) or set(raw_path) != _PATH_KEYS:
            raise AcquisitionEvidenceError("acquisition path fields are invalid")
        path_id = _id(raw_path.get("path_id"), "path_id")
        if path_id in seen:
            raise AcquisitionEvidenceError(f"duplicate path_id: {path_id}")
        seen.add(path_id)
        kind = _text(raw_path.get("kind"), f"{path_id}.kind").upper()
        if kind not in _PATH_KINDS:
            raise AcquisitionEvidenceError(f"{path_id}: unsupported path kind")
        operator_visible = raw_path.get("operator_visible")
        allow_na = raw_path.get("allow_not_applicable")
        if not isinstance(operator_visible, bool) or not isinstance(allow_na, bool):
            raise AcquisitionEvidenceError(
                f"{path_id}: operator_visible/allow_not_applicable must be boolean"
            )
        paths.append(
            {
                "path_id": path_id,
                "kind": kind,
                "expected_ref": _immutable_ref(
                    raw_path.get("expected_ref"), f"{path_id}.expected_ref"
                ),
                "operator_visible": operator_visible,
                "allow_not_applicable": allow_na,
            }
        )
    if not any(bool(item["operator_visible"]) for item in paths):
        raise AcquisitionEvidenceError(
            "manifest must identify at least one operator-visible acquisition path"
        )
    paths.sort(key=lambda item: str(item["path_id"]))
    return {
        "version": "maps-acquisition-paths-v1",
        "release_id": release_id,
        "paths": paths,
    }


def _observation(raw: Mapping[str, object]) -> dict[str, object]:
    if set(raw) != _OBSERVATION_KEYS:
        raise AcquisitionEvidenceError("observation fields are invalid")
    path_id = _id(raw.get("path_id"), "observation.path_id")
    acquisition_state = _text(
        raw.get("acquisition_state"), f"{path_id}.acquisition_state"
    ).upper()
    if acquisition_state not in _ACQUISITION_STATES:
        raise AcquisitionEvidenceError(f"{path_id}: invalid acquisition_state")
    usability_state = _text(
        raw.get("usability_state"), f"{path_id}.usability_state"
    ).upper()
    if usability_state not in _USABILITY_STATES:
        raise AcquisitionEvidenceError(f"{path_id}: invalid usability_state")

    observed_raw = raw.get("observed_ref")
    observed_ref = (
        _immutable_ref(observed_raw, f"{path_id}.observed_ref")
        if observed_raw is not None
        else None
    )
    acquisition_ref = _optional_evidence_ref(
        raw.get("acquisition_evidence_ref"),
        f"{path_id}.acquisition_evidence_ref",
    )
    usability_ref = _optional_evidence_ref(
        raw.get("usability_evidence_ref"),
        f"{path_id}.usability_evidence_ref",
    )
    decision_ref = _optional_evidence_ref(
        raw.get("not_applicable_decision_ref"),
        f"{path_id}.not_applicable_decision_ref",
    )

    if acquisition_state == "OBSERVED":
        if observed_ref is None or acquisition_ref is None or decision_ref is not None:
            raise AcquisitionEvidenceError(
                f"{path_id}: OBSERVED requires observed_ref/acquisition evidence and no N/A decision"
            )
        if usability_state == "NOT_APPLICABLE":
            raise AcquisitionEvidenceError(
                f"{path_id}: observed acquisition cannot have NOT_APPLICABLE usability"
            )
    elif acquisition_state == "UNREACHABLE":
        if observed_ref is not None or acquisition_ref is None or decision_ref is not None:
            raise AcquisitionEvidenceError(
                f"{path_id}: UNREACHABLE requires failure evidence and no observed/N/A ref"
            )
        if usability_state not in {"FAILED", "UNKNOWN"}:
            raise AcquisitionEvidenceError(
                f"{path_id}: unreachable path usability must be FAILED or UNKNOWN"
            )
    elif acquisition_state == "UNKNOWN":
        if observed_ref is not None or acquisition_ref is not None or decision_ref is not None:
            raise AcquisitionEvidenceError(
                f"{path_id}: UNKNOWN cannot claim acquisition or decision evidence"
            )
        if usability_state != "UNKNOWN" or usability_ref is not None:
            raise AcquisitionEvidenceError(
                f"{path_id}: UNKNOWN acquisition requires UNKNOWN usability without evidence"
            )
    else:
        if (
            observed_ref is not None
            or acquisition_ref is not None
            or decision_ref is None
            or usability_state != "NOT_APPLICABLE"
            or usability_ref is not None
        ):
            raise AcquisitionEvidenceError(
                f"{path_id}: NOT_APPLICABLE requires only a decision ref and N/A usability"
            )

    if usability_state in {"VERIFIED", "FAILED"} and usability_ref is None:
        raise AcquisitionEvidenceError(
            f"{path_id}: VERIFIED/FAILED usability requires evidence"
        )
    if usability_state in {"UNKNOWN", "NOT_APPLICABLE"} and usability_ref is not None:
        raise AcquisitionEvidenceError(
            f"{path_id}: UNKNOWN/N/A usability cannot claim evidence"
        )

    return {
        "path_id": path_id,
        "acquisition_state": acquisition_state,
        "observed_ref": observed_ref,
        "acquisition_evidence_ref": acquisition_ref,
        "usability_state": usability_state,
        "usability_evidence_ref": usability_ref,
        "not_applicable_decision_ref": decision_ref,
    }


def _aggregate(states: Sequence[str]) -> str:
    if any(state == "FAIL" for state in states):
        return "FAIL"
    if any(state == "UNKNOWN" for state in states):
        return "UNKNOWN"
    return "PASS"


def _property_fragment(state: str, report_ref: str) -> dict[str, object]:
    if state in {"PASS", "FAIL"}:
        refs = [report_ref]
    else:
        refs = []
    return {"state": state, "evidence_refs": refs}


def evaluate_acquisition_evidence(
    manifest: Mapping[str, object],
    observations: Sequence[Mapping[str, object]],
    *,
    label: str,
) -> dict[str, object]:
    """Validate externally observed acquisition evidence; performs no acquisition itself."""

    resolved_label = _text(label, "label")
    normalized_manifest = _manifest(manifest)
    path_index = {
        str(item["path_id"]): item for item in normalized_manifest["paths"]
    }

    observed_index: dict[str, dict[str, object]] = {}
    for raw in observations:
        if not isinstance(raw, Mapping):
            raise AcquisitionEvidenceError("observation must be a mapping")
        item = _observation(raw)
        path_id = str(item["path_id"])
        if path_id not in path_index:
            raise AcquisitionEvidenceError(f"observation references unknown path: {path_id}")
        if path_id in observed_index:
            raise AcquisitionEvidenceError(f"duplicate observation: {path_id}")
        observed_index[path_id] = item

    normalized_observations = [
        observed_index[path_id] for path_id in sorted(observed_index)
    ]
    # The evidence identity is content-derived. `label` is descriptive metadata
    # and must not create two identities for the same manifest/observations.
    report_id = _hash(
        {
            "manifest": normalized_manifest,
            "observations": normalized_observations,
        }
    )
    report_ref = f"acquisition-report:{report_id}"

    path_reports: list[dict[str, object]] = []
    acquisition_states: list[str] = []
    visible_stale_states: list[str] = []
    visible_usability_states: list[str] = []
    mismatch_count = 0
    missing_count = 0

    for path in normalized_manifest["paths"]:
        path_id = str(path["path_id"])
        observation = observed_index.get(path_id)
        if observation is None:
            missing_count += 1
            acquisition_status = "UNKNOWN"
            usability_status = "UNKNOWN"
            stale_status = "UNKNOWN" if path["operator_visible"] else "NOT_APPLICABLE"
            reason = "observation_missing"
            acquisition_evidence_ref = None
            usability_evidence_ref = None
            decision_ref = None
            observed_ref = None
        else:
            state = str(observation["acquisition_state"])
            acquisition_evidence_ref = observation["acquisition_evidence_ref"]
            usability_evidence_ref = observation["usability_evidence_ref"]
            decision_ref = observation["not_applicable_decision_ref"]
            observed_ref = observation["observed_ref"]

            if state == "NOT_APPLICABLE":
                if not bool(path["allow_not_applicable"]):
                    acquisition_status = "FAIL"
                    # An invalid N/A claim proves incomplete/invalid coverage,
                    # not that the underlying artifact itself is unusable.
                    usability_status = "UNKNOWN" if path["operator_visible"] else "NOT_APPLICABLE"
                    stale_status = "UNKNOWN" if path["operator_visible"] else "NOT_APPLICABLE"
                    reason = "not_applicable_not_allowed"
                else:
                    acquisition_status = "PASS"
                    usability_status = "NOT_APPLICABLE"
                    stale_status = "PASS" if path["operator_visible"] else "NOT_APPLICABLE"
                    reason = "explicit_not_applicable"
            elif state == "UNKNOWN":
                acquisition_status = "UNKNOWN"
                usability_status = "UNKNOWN"
                stale_status = "UNKNOWN" if path["operator_visible"] else "NOT_APPLICABLE"
                reason = "acquisition_unknown"
            elif state == "UNREACHABLE":
                acquisition_status = "FAIL"
                usability_status = (
                    "FAIL"
                    if observation["usability_state"] == "FAILED"
                    else "UNKNOWN"
                )
                stale_status = "UNKNOWN" if path["operator_visible"] else "NOT_APPLICABLE"
                reason = "path_unreachable"
            else:
                content_match = observed_ref == path["expected_ref"]
                acquisition_status = "PASS" if content_match else "FAIL"
                if not content_match:
                    mismatch_count += 1
                    reason = "immutable_ref_mismatch"
                else:
                    reason = "verified_exact_ref"
                usability_status = {
                    "VERIFIED": "PASS",
                    "FAILED": "FAIL",
                    "UNKNOWN": "UNKNOWN",
                }[str(observation["usability_state"])]
                if path["operator_visible"]:
                    stale_status = "PASS" if content_match else "FAIL"
                else:
                    stale_status = "NOT_APPLICABLE"

        acquisition_states.append(acquisition_status)
        if path["operator_visible"]:
            visible_stale_states.append(stale_status)
            if usability_status != "NOT_APPLICABLE":
                visible_usability_states.append(usability_status)

        path_reports.append(
            {
                "path_id": path_id,
                "kind": path["kind"],
                "operator_visible": path["operator_visible"],
                "expected_ref": path["expected_ref"],
                "observed_ref": observed_ref,
                "acquisition_status": acquisition_status,
                "stale_visible_status": stale_status,
                "usability_status": usability_status,
                "reason": reason,
                "evidence": {
                    "acquisition_ref": acquisition_evidence_ref,
                    "usability_ref": usability_evidence_ref,
                    "not_applicable_decision_ref": decision_ref,
                },
            }
        )

    acquisition_property = _aggregate(acquisition_states)
    stale_property = (
        _aggregate(visible_stale_states) if visible_stale_states else "UNKNOWN"
    )
    usability_property = (
        _aggregate(visible_usability_states) if visible_usability_states else "UNKNOWN"
    )

    return {
        "report_version": 1,
        "report_kind": "MAPS_ACQUISITION_PATH_EVIDENCE_REPORT",
        "report_id": report_id,
        "label": resolved_label,
        "manifest_version": normalized_manifest["version"],
        "release_id": normalized_manifest["release_id"],
        "manifest_sha256": _hash(normalized_manifest),
        "path_count": len(path_reports),
        "missing_observation_count": missing_count,
        "immutable_ref_mismatch_count": mismatch_count,
        "paths": path_reports,
        "benchmark_property_fragments": {
            "release.acquisition_paths_verified": _property_fragment(
                acquisition_property, report_ref
            ),
            "release.no_stale_visible_artifact": _property_fragment(
                stale_property, report_ref
            ),
            "operator.result_usable": _property_fragment(
                usability_property, report_ref
            ),
        },
        "coverage": {
            "acquisition_performed_by_this_report": False,
            "network_or_install_execution": False,
            "real_world_provenance_verified_by_this_report": False,
            "rule": (
                "the report validates supplied observations and immutable-ref/usability "
                "evidence shape; benchmark provenance must separately prove that the "
                "observations came from the real authorized acquisition path"
            ),
        },
        "authority": {
            "external_action_authorized": False,
            "publication_authorized": False,
            "automatic_benchmark_pass": False,
        },
    }
