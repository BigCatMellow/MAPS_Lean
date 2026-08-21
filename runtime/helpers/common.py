from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import re
from typing import Any, Mapping, Sequence
from uuid import uuid4


_HELPER_RUN_ID = re.compile(r"^HELP-[0-9a-f]{12}$")
_HELPER_CONTINUITY_ID = re.compile(r"^HC-[0-9a-f]{12}$")


def now_z() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class HelperError(RuntimeError):
    pass


def new_helper_run_id() -> str:
    """Allocate a stable helper invocation ID before consequential side effects."""
    return f"HELP-{uuid4().hex[:12]}"


def validate_helper_run_id(value: str) -> str:
    normalized = value.strip() if isinstance(value, str) else ""
    if not _HELPER_RUN_ID.fullmatch(normalized):
        raise HelperError("helper_run_id must match HELP-<12 lowercase hex chars>")
    return normalized


@dataclass(frozen=True)
class HelperResult:
    helper_run_id: str
    task_id: str
    helper: str
    status: str
    summary: str
    output_paths: tuple[str, ...]
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["output_paths"] = list(self.output_paths)
        return payload


class HelperRunStore:
    """Durable helper invocation/results. This is evidence, not task authority."""

    def __init__(self, path: str | Path = ".maps/state/helper-runs.json"):
        self.path = Path(path)

    def append(self, result: HelperResult) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists():
            value = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(value, list):
                raise HelperError("helper run store must contain a JSON list")
        else:
            value = []
        if any(
            isinstance(item, Mapping)
            and item.get("helper_run_id") == result.helper_run_id
            for item in value
        ):
            raise HelperError("helper_run_id already exists in helper run store")
        value.append(result.to_dict())
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        tmp.replace(self.path)


@dataclass(frozen=True)
class HelperContinuityRecord:
    continuity_id: str
    task_id: str
    project_id: str
    helper: str
    purpose: str
    context_key: str
    session_ref: str
    status: str
    created_at: str
    expires_at: str
    invalidated_at: str | None = None
    invalidation_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _utc_from_iso_z(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(
            timezone.utc
        )
    except ValueError as exc:
        raise HelperError(f"invalid timestamp: {value}") from exc


def _continuity_text(value: str, field: str, *, max_len: int = 256) -> str:
    normalized = value.strip() if isinstance(value, str) else ""
    if not normalized or len(normalized) > max_len or any(ord(ch) < 32 for ch in normalized):
        raise HelperError(f"{field} must be non-empty text without control characters")
    return normalized


class HelperContinuityStore:
    """Durable helper session continuity metadata.

    Continuity records are reuse evidence only. They do not claim task
    authority, prove provider liveness, or resume a helper process.
    """

    def __init__(self, path: str | Path = ".maps/state/helper-continuity.json"):
        self.path = Path(path)

    def _validate_record(self, item: Mapping[str, Any], *, index: int) -> dict[str, Any]:
        required = {
            "continuity_id",
            "task_id",
            "project_id",
            "helper",
            "purpose",
            "context_key",
            "session_ref",
            "status",
            "created_at",
            "expires_at",
        }
        missing = sorted(required - set(item))
        if missing:
            raise HelperError(
                f"malformed helper continuity record {index}: missing "
                + ", ".join(missing)
            )
        record = dict(item)
        for field in required:
            if not isinstance(record[field], str):
                raise HelperError(
                    f"malformed helper continuity record {index}: "
                    f"{field} must be text"
                )
        continuity_id = _continuity_text(
            record["continuity_id"], "continuity_id", max_len=128
        )
        if not _HELPER_CONTINUITY_ID.fullmatch(continuity_id):
            raise HelperError(f"malformed helper continuity record {index}: invalid id")
        record["continuity_id"] = continuity_id
        for field in (
            "task_id",
            "project_id",
            "helper",
            "purpose",
            "context_key",
            "session_ref",
        ):
            record[field] = _continuity_text(record[field], field)
        status = _continuity_text(record["status"], "status", max_len=32)
        if status not in {"active", "invalidated"}:
            raise HelperError(
                f"malformed helper continuity record {index}: invalid status"
            )
        record["status"] = status
        _utc_from_iso_z(record["created_at"])
        _utc_from_iso_z(record["expires_at"])
        if status == "invalidated":
            if not isinstance(record.get("invalidated_at"), str) or not isinstance(
                record.get("invalidation_reason"), str
            ):
                raise HelperError(
                    f"malformed helper continuity record {index}: "
                    "invalidated records require invalidation metadata"
                )
            _utc_from_iso_z(record["invalidated_at"])
            record["invalidation_reason"] = _continuity_text(
                record["invalidation_reason"], "invalidation_reason"
            )
        return record

    def _read(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        value = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(value, list):
            raise HelperError("helper continuity store must contain a JSON list")
        records: list[dict[str, Any]] = []
        for index, item in enumerate(value):
            if not isinstance(item, Mapping):
                raise HelperError(
                    f"malformed helper continuity record {index}: expected object"
                )
            records.append(self._validate_record(item, index=index))
        return records

    def _write(self, value: Sequence[Mapping[str, Any]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(
            json.dumps(list(value), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        tmp.replace(self.path)

    def register(
        self,
        *,
        task_id: str,
        project_id: str,
        helper: str,
        purpose: str,
        context_key: str,
        session_ref: str,
        ttl_seconds: int,
        now: datetime | None = None,
    ) -> HelperContinuityRecord:
        if ttl_seconds <= 0:
            raise HelperError("ttl_seconds must be > 0")
        current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
        record = HelperContinuityRecord(
            continuity_id=f"HC-{uuid4().hex[:12]}",
            task_id=_continuity_text(task_id, "task_id", max_len=128),
            project_id=_continuity_text(project_id, "project_id", max_len=128),
            helper=_continuity_text(helper, "helper", max_len=128),
            purpose=_continuity_text(purpose, "purpose"),
            context_key=_continuity_text(context_key, "context_key"),
            session_ref=_continuity_text(session_ref, "session_ref"),
            status="active",
            created_at=current.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            expires_at=(current + timedelta(seconds=ttl_seconds))
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z"),
        )
        value = self._read()
        value.append(record.to_dict())
        self._write(value)
        return record

    def resolve(
        self,
        *,
        task_id: str,
        project_id: str,
        helper: str,
        purpose: str,
        context_key: str,
        now: datetime | None = None,
    ) -> dict[str, Any]:
        query = {
            "task_id": _continuity_text(task_id, "task_id", max_len=128),
            "project_id": _continuity_text(project_id, "project_id", max_len=128),
            "helper": _continuity_text(helper, "helper", max_len=128),
            "purpose": _continuity_text(purpose, "purpose"),
            "context_key": _continuity_text(context_key, "context_key"),
        }
        current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
        try:
            records = self._read()
        except (HelperError, json.JSONDecodeError) as exc:
            return {
                "reusable": False,
                "reason": "MALFORMED_STORE",
                "record": None,
                "error": str(exc),
            }
        candidates = [
            item
            for item in records
            if all(item.get(key) == value for key, value in query.items())
        ]
        if not candidates:
            return {"reusable": False, "reason": "NO_MATCH", "record": None}
        latest = sorted(candidates, key=lambda item: str(item.get("created_at", "")))[-1]
        if latest.get("status") != "active":
            return {"reusable": False, "reason": "INVALIDATED", "record": latest}
        if _utc_from_iso_z(str(latest.get("expires_at", ""))) <= current:
            return {"reusable": False, "reason": "EXPIRED", "record": latest}
        return {"reusable": True, "reason": "REUSABLE", "record": latest}

    def invalidate(
        self,
        continuity_id: str,
        *,
        reason: str,
        now: datetime | None = None,
    ) -> dict[str, Any]:
        continuity_id = _continuity_text(continuity_id, "continuity_id", max_len=128)
        reason = _continuity_text(reason, "reason")
        current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
        value = self._read()
        for item in value:
            if item.get("continuity_id") != continuity_id:
                continue
            item["status"] = "invalidated"
            item["invalidated_at"] = (
                current.replace(microsecond=0).isoformat().replace("+00:00", "Z")
            )
            item["invalidation_reason"] = reason
            self._write(value)
            return {"ok": True, "record": item}
        return {"ok": False, "reason": "NOT_FOUND"}


def new_result(
    *,
    task_id: str,
    helper: str,
    status: str,
    summary: str,
    output_paths: Sequence[str],
    helper_run_id: str | None = None,
) -> HelperResult:
    resolved_id = (
        validate_helper_run_id(helper_run_id)
        if helper_run_id is not None
        else new_helper_run_id()
    )
    return HelperResult(
        helper_run_id=resolved_id,
        task_id=task_id,
        helper=helper,
        status=status,
        summary=summary,
        output_paths=tuple(output_paths),
        created_at=now_z(),
    )


def _norm(path: str | Path, repo: Path) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = repo / candidate
    resolved = candidate.resolve()
    try:
        resolved.relative_to(repo)
    except ValueError as exc:
        raise HelperError(f"helper path escapes repository: {path}") from exc
    return resolved


def path_in_scope(path: str | Path, allowed: Sequence[str], repo: str | Path) -> bool:
    repo_path = Path(repo).resolve()
    target = _norm(path, repo_path)
    for raw in allowed:
        scope = _norm(raw, repo_path)
        if target == scope or scope in target.parents:
            return True
    return False


def validate_active_scope(
    task: Mapping[str, Any], paths: Sequence[str | Path], *, repo: str | Path
) -> None:
    if str(task.get("status", "")).upper() != "ACTIVE":
        raise HelperError("helper work requires an ACTIVE parent task")
    task_id = str(task.get("task_id", "")).strip()
    if not task_id:
        raise HelperError("task_id is required")
    allowed = task.get("output_paths", [])
    if not isinstance(allowed, Sequence) or isinstance(allowed, (str, bytes)) or not allowed:
        raise HelperError(f"{task_id} has no output_paths")
    outside = [str(path) for path in paths if not path_in_scope(path, allowed, repo)]
    if outside:
        raise HelperError("helper path outside task output scope: " + ", ".join(outside))
