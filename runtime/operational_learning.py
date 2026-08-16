from __future__ import annotations

from datetime import datetime
from pathlib import PurePosixPath
from typing import Mapping, Sequence

from runtime.state.observability import redact_sensitive_text


class OperationalLearningError(ValueError):
    pass


_STATUSES = {"CANDIDATE", "ACTIVE", "RETIRED"}
_SOURCE_KINDS = {
    "TASK_OUTCOME",
    "INCIDENT",
    "OPERATOR_OBSERVATION",
    "NON_TASK_OBSERVATION",
    "RESEARCH",
}
_APPLICABILITY_KEYS = {
    "global",
    "project_ids",
    "task_types",
    "risk_levels",
    "path_prefixes",
}
_PROMOTION_KEYS = {
    "decision_ref",
    "promoted_by",
    "starts_at",
    "review_at",
    "expires_at",
}
_RETIREMENT_KEYS = {"decision_ref", "retired_by", "retired_at"}


def _text(value: object, field: str, *, max_chars: int = 4000) -> str:
    if not isinstance(value, str) or not value.strip():
        raise OperationalLearningError(f"{field} must be non-empty text")
    value = value.strip()
    if len(value) > max_chars:
        raise OperationalLearningError(f"{field} exceeds {max_chars} characters")
    return value


def _safe_text(value: object, field: str, *, max_chars: int = 4000) -> str:
    text = _text(value, field, max_chars=max_chars)
    if redact_sensitive_text(text) != text:
        raise OperationalLearningError(f"{field} contains text recognized as sensitive")
    return text


def _instant(value: object, field: str) -> datetime:
    text = _text(value, field, max_chars=64)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise OperationalLearningError(f"{field} must be ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise OperationalLearningError(f"{field} must include a UTC offset")
    return parsed


def _string_list(value: object, field: str) -> list[str]:
    if not isinstance(value, list):
        raise OperationalLearningError(f"{field} must be a list")
    output = [_safe_text(item, field, max_chars=256) for item in value]
    if len(output) != len(set(output)):
        raise OperationalLearningError(f"{field} contains duplicates")
    return sorted(output)


def _path_prefix(value: str, field: str) -> str:
    if "\\" in value or value.startswith("/"):
        raise OperationalLearningError(f"{field} must be a repository-relative POSIX path")
    path = PurePosixPath(value)
    if not path.parts or any(part in {"", ".", ".."} for part in path.parts):
        raise OperationalLearningError(f"{field} contains an unsafe path component")
    return path.as_posix().rstrip("/")


def _applicability(raw: object) -> dict[str, object]:
    if not isinstance(raw, Mapping) or set(raw) != _APPLICABILITY_KEYS:
        raise OperationalLearningError(
            "applicability must contain global/project_ids/task_types/risk_levels/path_prefixes"
        )
    global_scope = raw.get("global")
    if not isinstance(global_scope, bool):
        raise OperationalLearningError("applicability.global must be boolean")
    project_ids = _string_list(raw.get("project_ids"), "applicability.project_ids")
    task_types = _string_list(raw.get("task_types"), "applicability.task_types")
    risk_levels = _string_list(raw.get("risk_levels"), "applicability.risk_levels")
    raw_paths = _string_list(raw.get("path_prefixes"), "applicability.path_prefixes")
    paths = sorted(
        _path_prefix(item, "applicability.path_prefixes") for item in raw_paths
    )
    populated = bool(project_ids or task_types or risk_levels or paths)
    if global_scope and populated:
        raise OperationalLearningError(
            "global applicability cannot be combined with scoped matchers"
        )
    if not global_scope and not populated:
        raise OperationalLearningError(
            "non-global applicability requires at least one explicit matcher"
        )
    return {
        "global": global_scope,
        "project_ids": project_ids,
        "task_types": task_types,
        "risk_levels": risk_levels,
        "path_prefixes": paths,
    }


def _promotion(raw: object, lesson_id: str) -> dict[str, object]:
    if not isinstance(raw, Mapping) or set(raw) != _PROMOTION_KEYS:
        raise OperationalLearningError(
            f"{lesson_id}.promotion must contain the complete promotion contract"
        )
    starts_text = _text(
        raw.get("starts_at"), f"{lesson_id}.promotion.starts_at", max_chars=64
    )
    review_text = _text(
        raw.get("review_at"), f"{lesson_id}.promotion.review_at", max_chars=64
    )
    starts = _instant(starts_text, f"{lesson_id}.promotion.starts_at")
    review = _instant(review_text, f"{lesson_id}.promotion.review_at")
    if review <= starts:
        raise OperationalLearningError(f"{lesson_id}: review_at must be after starts_at")
    expires_raw = raw.get("expires_at")
    expires_text = None
    if expires_raw is not None:
        expires_text = _text(
            expires_raw, f"{lesson_id}.promotion.expires_at", max_chars=64
        )
        expires = _instant(expires_text, f"{lesson_id}.promotion.expires_at")
        if expires <= starts:
            raise OperationalLearningError(
                f"{lesson_id}: expires_at must be after starts_at"
            )
    return {
        "decision_ref": _safe_text(
            raw.get("decision_ref"),
            f"{lesson_id}.promotion.decision_ref",
            max_chars=512,
        ),
        "promoted_by": _safe_text(
            raw.get("promoted_by"),
            f"{lesson_id}.promotion.promoted_by",
            max_chars=128,
        ),
        "starts_at": starts_text,
        "review_at": review_text,
        "expires_at": expires_text,
    }


def _retirement(raw: object, lesson_id: str) -> dict[str, object]:
    if not isinstance(raw, Mapping) or set(raw) != _RETIREMENT_KEYS:
        raise OperationalLearningError(
            f"{lesson_id}.retirement must contain decision_ref/retired_by/retired_at"
        )
    retired_at = _text(
        raw.get("retired_at"), f"{lesson_id}.retirement.retired_at", max_chars=64
    )
    _instant(retired_at, f"{lesson_id}.retirement.retired_at")
    return {
        "decision_ref": _safe_text(
            raw.get("decision_ref"),
            f"{lesson_id}.retirement.decision_ref",
            max_chars=512,
        ),
        "retired_by": _safe_text(
            raw.get("retired_by"),
            f"{lesson_id}.retirement.retired_by",
            max_chars=128,
        ),
        "retired_at": retired_at,
    }


def validate_lesson_record(record: Mapping[str, object]) -> dict[str, object]:
    """Validate one lesson snapshot without granting it authority or persisting it."""

    lesson_id = _safe_text(record.get("lesson_id"), "lesson_id", max_chars=128)
    if record.get("lesson_version") != 1:
        raise OperationalLearningError(f"{lesson_id}: unsupported lesson_version")
    status = _text(record.get("status"), f"{lesson_id}.status", max_chars=32).upper()
    if status not in _STATUSES:
        raise OperationalLearningError(f"{lesson_id}: invalid status {status}")
    source_kind = _text(
        record.get("source_kind"), f"{lesson_id}.source_kind", max_chars=64
    ).upper()
    if source_kind not in _SOURCE_KINDS:
        raise OperationalLearningError(f"{lesson_id}: invalid source_kind")
    source_refs = _string_list(record.get("source_refs"), f"{lesson_id}.source_refs")
    if not source_refs:
        raise OperationalLearningError(f"{lesson_id}: source_refs cannot be empty")

    created_at = _text(record.get("created_at"), f"{lesson_id}.created_at", max_chars=64)
    created_instant = _instant(created_at, f"{lesson_id}.created_at")
    promotion_raw = record.get("promotion")
    retirement_raw = record.get("retirement")

    if status == "ACTIVE":
        promotion = _promotion(promotion_raw, lesson_id)
        if retirement_raw is not None:
            raise OperationalLearningError(f"{lesson_id}: ACTIVE lesson cannot be retired")
    elif status == "CANDIDATE":
        if promotion_raw is not None:
            raise OperationalLearningError(
                f"{lesson_id}: CANDIDATE lesson cannot carry promotion authority"
            )
        if retirement_raw is not None:
            raise OperationalLearningError(
                f"{lesson_id}: retired candidate must use RETIRED status"
            )
        promotion = None
    else:
        promotion = _promotion(promotion_raw, lesson_id) if promotion_raw is not None else None

    retirement = None
    if status == "RETIRED":
        retirement = _retirement(retirement_raw, lesson_id)
    elif retirement_raw is not None:
        raise OperationalLearningError(
            f"{lesson_id}: retirement is valid only for RETIRED"
        )

    if promotion is not None:
        starts = _instant(promotion["starts_at"], f"{lesson_id}.promotion.starts_at")
        if starts < created_instant:
            raise OperationalLearningError(
                f"{lesson_id}: promotion cannot start before lesson creation"
            )
    if retirement is not None:
        retired = _instant(
            retirement["retired_at"], f"{lesson_id}.retirement.retired_at"
        )
        if retired < created_instant:
            raise OperationalLearningError(
                f"{lesson_id}: retirement cannot precede lesson creation"
            )
        if promotion is not None:
            starts = _instant(
                promotion["starts_at"], f"{lesson_id}.promotion.starts_at"
            )
            if retired < starts:
                raise OperationalLearningError(
                    f"{lesson_id}: retirement cannot precede promotion start"
                )

    superseded_by = record.get("superseded_by")
    if superseded_by is not None:
        superseded_by = _safe_text(
            superseded_by, f"{lesson_id}.superseded_by", max_chars=128
        )
        if superseded_by == lesson_id:
            raise OperationalLearningError(
                f"{lesson_id}: lesson cannot supersede itself"
            )

    return {
        "lesson_version": 1,
        "lesson_id": lesson_id,
        "status": status,
        "claim": _safe_text(record.get("claim"), f"{lesson_id}.claim"),
        "source_kind": source_kind,
        "source_refs": source_refs,
        "applicability": _applicability(record.get("applicability")),
        "created_by": _safe_text(
            record.get("created_by"), f"{lesson_id}.created_by", max_chars=128
        ),
        "created_at": created_at,
        "promotion": promotion,
        "superseded_by": superseded_by,
        "retirement": retirement,
    }


def _context_value(context: Mapping[str, object], key: str) -> str | None:
    value = context.get(key)
    if value is None:
        return None
    return _text(value, f"context.{key}", max_chars=256)


def _context_paths(context: Mapping[str, object]) -> list[str] | None:
    value = context.get("paths")
    if value is None:
        return None
    if not isinstance(value, list):
        raise OperationalLearningError("context.paths must be a list")
    return sorted(
        _path_prefix(
            _text(item, "context.paths", max_chars=512), "context.paths"
        )
        for item in value
    )


def _match_applicability(
    app: Mapping[str, object], context: Mapping[str, object]
) -> str:
    if app["global"]:
        return "MATCH"

    unknown = False
    checks = (
        ("project_ids", _context_value(context, "project_id")),
        ("task_types", _context_value(context, "task_type")),
        ("risk_levels", _context_value(context, "risk")),
    )
    for field, observed in checks:
        expected = app[field]
        if not expected:
            continue
        if observed is None:
            unknown = True
        elif observed not in expected:
            return "NO_MATCH"

    prefixes = app["path_prefixes"]
    if prefixes:
        paths = _context_paths(context)
        if paths is None or not paths:
            unknown = True
        elif not any(
            path == prefix or path.startswith(prefix + "/")
            for path in paths
            for prefix in prefixes
        ):
            return "NO_MATCH"

    return "UNKNOWN" if unknown else "MATCH"


def project_applicable_lessons(
    records: Sequence[Mapping[str, object]],
    context: Mapping[str, object],
    *,
    at: str,
) -> dict[str, object]:
    """Return a deterministic guidance-only projection of already-promoted lessons."""

    now = _instant(at, "at")
    normalized = [validate_lesson_record(record) for record in records]
    lesson_ids = [record["lesson_id"] for record in normalized]
    if len(lesson_ids) != len(set(lesson_ids)):
        raise OperationalLearningError("duplicate lesson_id in projection input")

    projected = []
    withheld = []
    for record in sorted(normalized, key=lambda item: item["lesson_id"]):
        reason = None
        if record["status"] == "RETIRED":
            reason = "RETIRED"
        elif record["status"] == "CANDIDATE":
            reason = "CANDIDATE_NOT_PROMOTED"
        elif record["superseded_by"] is not None:
            reason = "SUPERSEDED"
        else:
            promotion = record["promotion"]
            starts = _instant(promotion["starts_at"], "promotion.starts_at")
            review = _instant(promotion["review_at"], "promotion.review_at")
            expires = (
                _instant(promotion["expires_at"], "promotion.expires_at")
                if promotion["expires_at"] is not None
                else None
            )
            if now < starts:
                reason = "NOT_STARTED"
            elif expires is not None and now >= expires:
                reason = "EXPIRED"
            elif now >= review:
                reason = "REVIEW_DUE"
            else:
                match = _match_applicability(record["applicability"], context)
                if match == "NO_MATCH":
                    reason = "NOT_APPLICABLE"
                elif match == "UNKNOWN":
                    reason = "APPLICABILITY_UNKNOWN"

        if reason is not None:
            withheld.append({"lesson_id": record["lesson_id"], "reason": reason})
            continue

        projected.append(
            {
                "lesson_id": record["lesson_id"],
                "claim": record["claim"],
                "source_kind": record["source_kind"],
                "source_refs": list(record["source_refs"]),
                "promotion_decision_ref": record["promotion"]["decision_ref"],
                "authority": "GUIDANCE_ONLY",
            }
        )

    return {
        "projection_version": 1,
        "projection_kind": "MAPS_OPERATIONAL_LEARNING_GUIDANCE",
        "at": at,
        "projected": projected,
        "withheld": withheld,
        "coverage": {
            "records_considered": len(normalized),
            "projected": len(projected),
            "withheld": len(withheld),
            "unknown_applicability": sum(
                item["reason"] == "APPLICABILITY_UNKNOWN" for item in withheld
            ),
        },
        "authority": {
            "kind": "DERIVED_GUIDANCE",
            "can_grant_task_authority": False,
            "can_grant_policy_authority": False,
            "can_promote_candidates": False,
        },
    }
