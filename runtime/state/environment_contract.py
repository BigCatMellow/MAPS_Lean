from __future__ import annotations

from contextlib import closing
from pathlib import PurePosixPath
import sqlite3
from typing import Mapping

from .common import MutationResult


ENVIRONMENT_FIELDS = (
    "spec_ref",
    "max_age_seconds",
    "required_for_routing",
    "allow_older_task_revision",
)


def _normalize_spec_ref(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("spec_ref must be a string")
    text = value.strip()
    if not text:
        raise ValueError("spec_ref is required")
    if "\\" in text:
        raise ValueError("spec_ref must use repository-style '/' separators")
    path = PurePosixPath(text)
    if path.is_absolute() or ".." in path.parts or path == PurePosixPath("."):
        raise ValueError("spec_ref must name a repository-relative file")
    return path.as_posix()


def validate_environment_contract(value: object) -> MutationResult | None:
    if not isinstance(value, Mapping):
        return MutationResult(False, "INVALID_CONTRACT", "environment must be an object")
    unknown = sorted(set(value) - set(ENVIRONMENT_FIELDS))
    if unknown:
        return MutationResult(
            False,
            "INVALID_CONTRACT",
            "unknown environment fields: " + ", ".join(unknown),
        )
    for field in ("spec_ref", "max_age_seconds"):
        if field not in value:
            return MutationResult(
                False,
                "INVALID_CONTRACT",
                f"environment.{field} is required",
            )
    try:
        _normalize_spec_ref(value["spec_ref"])
    except ValueError as exc:
        return MutationResult(False, "INVALID_CONTRACT", f"environment.{exc}")
    max_age_seconds = value["max_age_seconds"]
    if (
        not isinstance(max_age_seconds, int)
        or isinstance(max_age_seconds, bool)
        or max_age_seconds <= 0
    ):
        return MutationResult(
            False,
            "INVALID_CONTRACT",
            "environment.max_age_seconds must be a positive integer",
        )
    for field in ("required_for_routing", "allow_older_task_revision"):
        if field in value and not isinstance(value[field], bool):
            return MutationResult(
                False,
                "INVALID_CONTRACT",
                f"environment.{field} must be boolean",
            )
    return None


def validate_persisted_environment_contract(value: Mapping[str, object]) -> MutationResult | None:
    """Validate SQLite's integer-backed representation of the contract."""

    normalized = dict(value)
    for field in ("required_for_routing", "allow_older_task_revision"):
        raw_flag = normalized.get(field)
        if raw_flag not in (0, 1):
            return MutationResult(
                False,
                "INVALID_CONTRACT",
                f"environment.{field} must be stored as 0 or 1",
            )
        normalized[field] = bool(raw_flag)
    return validate_environment_contract(normalized)


class EnvironmentContractMixin:
    """Optional task-level environment requirements.

    This records only a task's expected specification and evidence freshness
    policy. It does not source reports. Routing consumes it read-only: a
    ``required_for_routing`` task with no fresh projected report is held at the
    policy gate (``runtime/routing/router.py``); the default (0) leaves routing
    unchanged.
    """

    def update_contract(self, task_id: str, contract: Mapping[str, object]) -> MutationResult:
        if "environment" in contract and contract["environment"] is not None:
            validation = validate_environment_contract(contract["environment"])
            if validation is not None:
                return validation
        return super().update_contract(task_id, contract)

    def _contract_shaping_hooks(self):
        return (*super()._contract_shaping_hooks(), self._apply_environment_contract_conn)

    def _apply_environment_contract_conn(
        self,
        conn: sqlite3.Connection,
        task_id: str,
        contract: Mapping[str, object],
    ) -> None:
        if "environment" not in contract:
            return
        raw_environment = contract["environment"]
        if raw_environment is None:
            conn.execute("DELETE FROM task_environment WHERE task_id = ?", (task_id,))
            return

        environment = raw_environment
        assert isinstance(environment, Mapping)
        spec_ref = _normalize_spec_ref(environment["spec_ref"])
        max_age_seconds = environment["max_age_seconds"]
        assert isinstance(max_age_seconds, int) and not isinstance(max_age_seconds, bool)
        conn.execute(
            """
            INSERT INTO task_environment(
                task_id, spec_ref, max_age_seconds, required_for_routing,
                allow_older_task_revision
            ) VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(task_id) DO UPDATE SET
                spec_ref = excluded.spec_ref,
                max_age_seconds = excluded.max_age_seconds,
                required_for_routing = excluded.required_for_routing,
                allow_older_task_revision = excluded.allow_older_task_revision
            """,
            (
                task_id,
                spec_ref,
                max_age_seconds,
                1 if environment.get("required_for_routing", False) else 0,
                1 if environment.get("allow_older_task_revision", False) else 0,
            ),
        )

    def get_task(self, task_id: str) -> dict | None:
        task = super().get_task(task_id)
        if task is None:
            return None
        with closing(self._connect()) as conn:
            row = conn.execute(
                """
                SELECT spec_ref, max_age_seconds, required_for_routing,
                       allow_older_task_revision
                FROM task_environment WHERE task_id = ?
                """,
                (task_id,),
            ).fetchone()
        task["environment"] = (
            None
            if row is None
            else {
                "spec_ref": row["spec_ref"],
                "max_age_seconds": row["max_age_seconds"],
                "required_for_routing": bool(row["required_for_routing"]),
                "allow_older_task_revision": bool(row["allow_older_task_revision"]),
            }
        )
        return task
