from __future__ import annotations

from contextlib import closing
from pathlib import Path
import re
import sqlite3
from typing import Iterable, Mapping, Sequence

from .common import MutationResult, iso_z, utc_now


class BaseStore:
    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        schema_path = Path(__file__).with_name("schema.sql")
        self._schema = schema_path.read_text(encoding="utf-8")
        with closing(self._connect()) as conn:
            conn.executescript(self._schema)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=5.0, isolation_level=None)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA busy_timeout = 5000")
        return conn

    @staticmethod
    def _clean(values: Iterable[str] | None) -> tuple[str, ...]:
        if not values:
            return ()
        return tuple(
            dict.fromkeys(
                value.strip()
                for value in values
                if isinstance(value, str) and value.strip()
            )
        )

    def _allocate_task_id(self, conn: sqlite3.Connection) -> str:
        row = conn.execute(
            "SELECT next_id FROM task_sequence WHERE singleton = 1"
        ).fetchone()
        next_id = int(row["next_id"])
        while conn.execute(
            "SELECT 1 FROM tasks WHERE task_id = ?", (f"TASK-{next_id:04d}",)
        ).fetchone():
            next_id += 1
        conn.execute(
            "UPDATE task_sequence SET next_id = ? WHERE singleton = 1",
            (next_id + 1,),
        )
        return f"TASK-{next_id:04d}"

    @staticmethod
    def _advance_sequence_past_explicit(
        conn: sqlite3.Connection,
        task_id: str,
    ) -> None:
        match = re.fullmatch(r"TASK-(\d+)", task_id)
        if not match:
            return
        explicit_number = int(match.group(1))
        row = conn.execute(
            "SELECT next_id FROM task_sequence WHERE singleton = 1"
        ).fetchone()
        if explicit_number >= int(row["next_id"]):
            conn.execute(
                "UPDATE task_sequence SET next_id = ? WHERE singleton = 1",
                (explicit_number + 1,),
            )

    def create_task(
        self,
        *,
        task_id: str | None = None,
        project_id: str = "default",
        title: str = "",
        outcome: str = "",
        task_type: str = "",
        owner: str = "",
        risk: str = "",
        max_attempts: int = 3,
    ) -> MutationResult:
        now = iso_z(utc_now())
        try:
            with closing(self._connect()) as conn:
                conn.execute("BEGIN IMMEDIATE")
                if task_id:
                    resolved_id = task_id.strip()
                    self._advance_sequence_past_explicit(conn, resolved_id)
                else:
                    resolved_id = self._allocate_task_id(conn)
                conn.execute(
                    """
                    INSERT INTO tasks(
                        task_id, project_id, title, outcome, task_type, owner, risk,
                        max_attempts, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        resolved_id,
                        project_id.strip() or "default",
                        title.strip(),
                        outcome.strip(),
                        task_type.strip().upper(),
                        owner.strip(),
                        risk.strip().upper(),
                        max_attempts,
                        now,
                        now,
                    ),
                )
                self._append_event(
                    conn,
                    resolved_id,
                    "TASK_CREATED",
                    owner or None,
                    "Task created in NEEDS_SHAPING",
                )
                conn.commit()
            return MutationResult(
                True,
                "CREATED",
                f"created {resolved_id}",
                self.get_task(resolved_id),
            )
        except sqlite3.IntegrityError as exc:
            return MutationResult(False, "CONFLICT", str(exc))

    def update_contract(
        self,
        task_id: str,
        contract: Mapping[str, object],
    ) -> MutationResult:
        scalar_fields = {
            "title",
            "outcome",
            "task_type",
            "owner",
            "risk",
            "decision_authority",
            "verification",
            "evidence_expected",
            "review_required",
            "escalation",
            "project_id",
        }
        list_tables = {
            "inputs": ("task_inputs", "value"),
            "sources": ("task_sources", "value"),
            "dependencies": ("task_dependencies", "depends_on"),
            "output_paths": ("task_output_paths", "path"),
            "non_goals": ("task_non_goals", "value"),
            "acceptance_criteria": ("task_acceptance_criteria", "criterion"),
            "stop_conditions": ("task_stop_conditions", "condition"),
        }
        with closing(self._connect()) as conn:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT * FROM tasks WHERE task_id = ?", (task_id,)
            ).fetchone()
            if row is None:
                conn.rollback()
                return MutationResult(False, "NOT_FOUND", f"{task_id} does not exist")
            if row["status"] not in {"NEEDS_SHAPING", "BLOCKED"}:
                conn.rollback()
                return MutationResult(
                    False,
                    "CONTRACT_FROZEN",
                    f"contract is frozen while status is {row['status']}",
                    dict(row),
                )

            updates: dict[str, object] = {}
            for key in scalar_fields:
                if key not in contract:
                    continue
                value = contract[key]
                if value is None:
                    value = ""
                if not isinstance(value, str):
                    conn.rollback()
                    return MutationResult(
                        False,
                        "INVALID_CONTRACT",
                        f"{key} must be a string",
                    )
                value = value.strip()
                if key in {"task_type", "risk", "review_required"}:
                    value = value.upper()
                updates[key] = value

            if updates:
                updates["updated_at"] = iso_z(utc_now())
                clause = ", ".join(f"{key} = ?" for key in updates)
                conn.execute(
                    f"UPDATE tasks SET {clause} WHERE task_id = ?",
                    (*updates.values(), task_id),
                )

            for key, (table, column) in list_tables.items():
                if key not in contract:
                    continue
                raw = contract[key]
                if raw is None:
                    cleaned = ()
                elif isinstance(raw, Sequence) and not isinstance(raw, (str, bytes)):
                    cleaned = self._clean(raw)  # type: ignore[arg-type]
                else:
                    conn.rollback()
                    return MutationResult(
                        False,
                        "INVALID_CONTRACT",
                        f"{key} must be a list of strings",
                    )
                conn.execute(f"DELETE FROM {table} WHERE task_id = ?", (task_id,))
                conn.executemany(
                    f"INSERT INTO {table}(task_id, {column}) VALUES (?, ?)",
                    ((task_id, item) for item in cleaned),
                )

            # Optional mixins can participate in the same shaping transaction.
            # PolicyStateMixin uses this hook so policy flags and approval reset
            # cannot drift from the task contract if a second write fails.
            policy_hook = getattr(self, "_apply_policy_contract_conn", None)
            if callable(policy_hook):
                policy_hook(conn, task_id, contract)

            conn.execute(
                "UPDATE tasks SET agi_status = 'UNCHECKED', updated_at = ? WHERE task_id = ?",
                (iso_z(utc_now()), task_id),
            )
            self._append_event(
                conn,
                task_id,
                "TASK_CONTRACT_UPDATED",
                row["owner"] or None,
                "Task contract updated; AGI status reset",
            )
            conn.commit()
        return MutationResult(True, "UPDATED", f"updated {task_id}", self.get_task(task_id))

    def get_task(self, task_id: str) -> dict | None:
        with closing(self._connect()) as conn:
            row = conn.execute(
                "SELECT * FROM tasks WHERE task_id = ?", (task_id,)
            ).fetchone()
            if row is None:
                return None
            task = dict(row)
            task["inputs"] = self._values(conn, "task_inputs", "value", task_id)
            task["sources"] = self._values(conn, "task_sources", "value", task_id)
            task["dependencies"] = self._values(
                conn, "task_dependencies", "depends_on", task_id
            )
            task["output_paths"] = self._values(
                conn, "task_output_paths", "path", task_id
            )
            task["non_goals"] = self._values(
                conn, "task_non_goals", "value", task_id
            )
            task["acceptance_criteria"] = self._values(
                conn, "task_acceptance_criteria", "criterion", task_id
            )
            task["stop_conditions"] = self._values(
                conn, "task_stop_conditions", "condition", task_id
            )
            return task

    def get_submission(self, task_id: str) -> dict | None:
        with closing(self._connect()) as conn:
            row = conn.execute(
                "SELECT * FROM task_submissions WHERE task_id = ?", (task_id,)
            ).fetchone()
            return dict(row) if row else None

    def list_reviews(self, task_id: str) -> list[dict]:
        with closing(self._connect()) as conn:
            return [
                dict(row)
                for row in conn.execute(
                    "SELECT * FROM reviews WHERE task_id = ? ORDER BY id",
                    (task_id,),
                ).fetchall()
            ]

    def list_events(self, task_id: str) -> list[dict]:
        with closing(self._connect()) as conn:
            return [
                dict(row)
                for row in conn.execute(
                    "SELECT * FROM task_events WHERE task_id = ? ORDER BY id",
                    (task_id,),
                ).fetchall()
            ]

    def connection_settings(self) -> dict[str, object]:
        with closing(self._connect()) as conn:
            return {
                "foreign_keys": conn.execute("PRAGMA foreign_keys").fetchone()[0],
                "journal_mode": conn.execute("PRAGMA journal_mode").fetchone()[0],
                "busy_timeout": conn.execute("PRAGMA busy_timeout").fetchone()[0],
            }

    @staticmethod
    def _values(
        conn: sqlite3.Connection,
        table: str,
        column: str,
        task_id: str,
    ) -> list[str]:
        return [
            row[column]
            for row in conn.execute(
                f"SELECT {column} FROM {table} WHERE task_id = ? ORDER BY rowid",
                (task_id,),
            ).fetchall()
        ]

    @staticmethod
    def _append_event(
        conn: sqlite3.Connection,
        task_id: str,
        event_type: str,
        actor: str | None,
        summary: str,
    ) -> None:
        conn.execute(
            """
            INSERT INTO task_events(task_id, event_type, actor, summary, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (task_id, event_type, actor, summary, iso_z(utc_now())),
        )
