from __future__ import annotations

from datetime import datetime
import hashlib
import json
import re
from typing import Any, Mapping, Protocol

from runtime.operational_learning import (
    OperationalLearningError,
    validate_lesson_record,
)


class OutcomeLessonCandidateError(ValueError):
    pass


_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class OutcomeLessonSource(Protocol):
    def get_outcome(self, outcome_id: int) -> dict[str, Any] | None: ...

    def list_outcomes(self, task_id: str) -> list[dict[str, Any]]: ...

    def get_task(self, task_id: str) -> dict[str, Any] | None: ...

    def get_run_manifest(self, run_id: str) -> dict[str, Any] | None: ...


def _instant(value: object, field: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise OutcomeLessonCandidateError(f"{field} must be a non-empty ISO-8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError as exc:
        raise OutcomeLessonCandidateError(f"{field} must be ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise OutcomeLessonCandidateError(f"{field} must include a UTC offset")
    return parsed


def _candidate_id(
    *,
    claim: str,
    source_refs: list[str],
    applicability: Mapping[str, object],
) -> str:
    payload = json.dumps(
        {
            "lesson_version": 1,
            "source_kind": "TASK_OUTCOME",
            "source_refs": source_refs,
            "claim": claim,
            "applicability": applicability,
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return f"LESSON-CAND-{hashlib.sha256(payload).hexdigest()}"


def build_outcome_lesson_candidate(
    source: OutcomeLessonSource,
    outcome_id: int,
    *,
    claim: str,
    applicability: Mapping[str, object],
    created_by: str,
    created_at: str,
) -> dict[str, object]:
    """Build a validated CANDIDATE lesson from exact canonical outcome evidence.

    The caller supplies the lesson claim and applicability explicitly. Outcome
    notes/source prose are never converted into lesson instructions here.
    """

    if isinstance(outcome_id, bool) or not isinstance(outcome_id, int) or outcome_id <= 0:
        raise OutcomeLessonCandidateError("outcome_id must be a positive integer")

    outcome = source.get_outcome(outcome_id)
    if not isinstance(outcome, Mapping):
        raise OutcomeLessonCandidateError(f"outcome {outcome_id} does not exist")

    task_id = outcome.get("task_id")
    if not isinstance(task_id, str) or not task_id.strip():
        raise OutcomeLessonCandidateError("outcome has no valid task_id")
    task_id = task_id.strip()

    task = source.get_task(task_id)
    if not isinstance(task, Mapping):
        raise OutcomeLessonCandidateError(f"outcome task {task_id} does not exist")
    if str(task.get("status", "")).upper() != "DONE":
        raise OutcomeLessonCandidateError(f"outcome task {task_id} is not DONE")

    task_revision = outcome.get("task_revision")
    if not isinstance(task_revision, str) or not _SHA256_RE.fullmatch(task_revision):
        raise OutcomeLessonCandidateError(
            "outcome does not carry a valid task revision SHA-256"
        )

    outcome_created_at = outcome.get("created_at")
    outcome_created = _instant(outcome_created_at, "outcome.created_at")
    candidate_created = _instant(created_at, "created_at")
    if candidate_created < outcome_created:
        raise OutcomeLessonCandidateError(
            "lesson candidate cannot be created before its source outcome"
        )

    all_outcomes = source.list_outcomes(task_id)
    if not isinstance(all_outcomes, list) or any(
        not isinstance(item, Mapping) for item in all_outcomes
    ):
        raise OutcomeLessonCandidateError("canonical outcome history is invalid")
    superseding_ids = sorted(
        int(item["id"])
        for item in all_outcomes
        if item.get("supersedes_outcome_id") == outcome_id
        and isinstance(item.get("id"), int)
        and not isinstance(item.get("id"), bool)
    )
    if superseding_ids:
        raise OutcomeLessonCandidateError(
            "outcome is superseded by later canonical observation(s): "
            + ", ".join(str(value) for value in superseding_ids)
        )

    source_refs = [
        f"outcome:{outcome_id}",
        f"task:{task_id}",
        f"task-revision-sha256:{task_revision}",
    ]

    run_id = outcome.get("run_id")
    if run_id is not None:
        if not isinstance(run_id, str) or not run_id.strip():
            raise OutcomeLessonCandidateError("outcome run_id is invalid")
        run_id = run_id.strip()
        run = source.get_run_manifest(run_id)
        if not isinstance(run, Mapping):
            raise OutcomeLessonCandidateError(f"outcome run {run_id} does not exist")
        if str(run.get("task_id", "")).strip() != task_id:
            raise OutcomeLessonCandidateError(
                f"outcome run {run_id} belongs to a different task"
            )
        source_refs.append(f"run:{run_id}")

    provisional = {
        "lesson_version": 1,
        "lesson_id": "LESSON-CAND-PROVISIONAL",
        "status": "CANDIDATE",
        "claim": claim,
        "source_kind": "TASK_OUTCOME",
        "source_refs": source_refs,
        "applicability": dict(applicability),
        "created_by": created_by,
        "created_at": created_at,
        "promotion": None,
        "superseded_by": None,
        "retirement": None,
    }
    try:
        normalized = validate_lesson_record(provisional)
    except OperationalLearningError as exc:
        raise OutcomeLessonCandidateError(str(exc)) from exc

    semantic_id = _candidate_id(
        claim=str(normalized["claim"]),
        source_refs=list(normalized["source_refs"]),
        applicability=normalized["applicability"],
    )
    final_record = dict(provisional)
    final_record["lesson_id"] = semantic_id
    try:
        return validate_lesson_record(final_record)
    except OperationalLearningError as exc:
        raise OutcomeLessonCandidateError(str(exc)) from exc
