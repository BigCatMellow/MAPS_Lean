from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any, Mapping, Sequence
from uuid import uuid4


_HELPER_RUN_ID = re.compile(r"^HELP-[0-9a-f]{12}$")


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
