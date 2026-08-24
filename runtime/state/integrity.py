from __future__ import annotations

from contextlib import closing
import hashlib
import json
from pathlib import Path
import sqlite3
from typing import Any, Iterable, Mapping, Sequence
from uuid import uuid4

from runtime.integrity.git_scope import collect_git_worktree_identity

from .common import MutationResult, iso_z, utc_now


class ExecutionIntegrityMixin:
    """Run binding, continuity, and optional criterion-level evidence.

    These records constrain/prove execution. They do not replace the canonical
    task lifecycle in `tasks`.
    """

    # ---------- Stable task revision ----------

    def _task_definition_conn(
        self, conn: sqlite3.Connection, task_id: str
    ) -> dict[str, Any]:
        row = conn.execute(
            """
            SELECT task_id, project_id, title, outcome, task_type, owner, risk,
                   decision_authority, verification, evidence_expected,
                   review_required, escalation, max_attempts
            FROM tasks WHERE task_id = ?
            """,
            (task_id,),
        ).fetchone()
        if row is None:
            raise KeyError(task_id)

        definition = dict(row)
        for key, table, column in (
            ("inputs", "task_inputs", "value"),
            ("sources", "task_sources", "value"),
            ("dependencies", "task_dependencies", "depends_on"),
            ("output_paths", "task_output_paths", "path"),
            ("non_goals", "task_non_goals", "value"),
            ("acceptance_criteria", "task_acceptance_criteria", "criterion"),
            ("stop_conditions", "task_stop_conditions", "condition"),
        ):
            definition[key] = sorted(
                row[column]
                for row in conn.execute(
                    f"SELECT {column} FROM {table} WHERE task_id = ?",
                    (task_id,),
                ).fetchall()
            )

        policy = conn.execute(
            """
            SELECT requires_operator_approval, destructive_action,
                   external_side_effect, security_sensitive,
                   broad_architecture, paid_execution
            FROM task_policy WHERE task_id = ?
            """,
            (task_id,),
        ).fetchone()
        definition["policy"] = (
            {key: bool(value) for key, value in dict(policy).items()}
            if policy is not None
            else {
                "requires_operator_approval": False,
                "destructive_action": False,
                "external_side_effect": False,
                "security_sensitive": False,
                "broad_architecture": False,
                "paid_execution": True,
            }
        )
        environment = conn.execute(
            """
            SELECT spec_ref, max_age_seconds, required_for_routing,
                   allow_older_task_revision
            FROM task_environment WHERE task_id = ?
            """,
            (task_id,),
        ).fetchone()
        definition["environment"] = (
            None
            if environment is None
            else {
                "spec_ref": environment["spec_ref"],
                "max_age_seconds": environment["max_age_seconds"],
                "required_for_routing": bool(environment["required_for_routing"]),
                "allow_older_task_revision": bool(
                    environment["allow_older_task_revision"]
                ),
            }
        )
        return definition

    def _task_revision_conn(self, conn: sqlite3.Connection, task_id: str) -> str:
        canonical = self._task_definition_conn(conn, task_id)
        payload = json.dumps(
            canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    def compute_task_revision(self, task_id: str) -> str | None:
        with closing(self._connect()) as conn:
            try:
                return self._task_revision_conn(conn, task_id)
            except KeyError:
                return None

    # ---------- Path/scope helpers ----------

    @staticmethod
    def _repo_relative(path: str | Path, repo_root: str | Path) -> str:
        root = Path(repo_root).resolve()
        candidate = Path(path)
        if not candidate.is_absolute():
            candidate = root / candidate
        candidate = candidate.resolve()
        try:
            relative = candidate.relative_to(root)
        except ValueError as exc:
            raise ValueError(f"path escapes repo root: {path}") from exc
        text = relative.as_posix()
        return text if text else "."

    @staticmethod
    def _scope_contains(scope: str, path: str) -> bool:
        if scope in {"", "."}:
            return True
        scope_path = Path(scope)
        path_obj = Path(path)
        return path_obj == scope_path or scope_path in path_obj.parents

    @classmethod
    def _covered_by_any(cls, path: str, scopes: Sequence[str]) -> bool:
        return any(cls._scope_contains(scope, path) for scope in scopes)

    @classmethod
    def _normalize_scopes(
        cls, values: Iterable[str | Path], repo_root: str | Path
    ) -> tuple[str, ...]:
        return tuple(
            sorted(
                dict.fromkeys(
                    cls._repo_relative(value, repo_root) for value in values
                )
            )
        )

    @classmethod
    def _validate_scope_contract(
        cls,
        *,
        readable: Sequence[str],
        writable: Sequence[str],
        forbidden: Sequence[str],
    ) -> tuple[str, ...]:
        issues: list[str] = []
        if not readable:
            issues.append("readable scope cannot be empty")
        if not writable:
            issues.append("writable scope cannot be empty")
        for path in writable:
            if not cls._covered_by_any(path, readable):
                issues.append(f"writable path is not readable: {path}")
            if cls._covered_by_any(path, forbidden):
                issues.append(f"writable path is forbidden: {path}")
        return tuple(issues)

    # ---------- Run manifests ----------

    def create_run_manifest(
        self,
        task_id: str,
        worker_id: str,
        *,
        repo_root: str | Path,
        created_by: str,
        session_id: str | None = None,
        context_paths: Sequence[str | Path] = (),
        readable_paths: Sequence[str | Path] = (".",),
        writable_paths: Sequence[str | Path] | None = None,
        forbidden_paths: Sequence[str | Path] = (),
        runtime_limits: Mapping[str, int] | None = None,
        base_revision: str | None = None,
    ) -> MutationResult:
        if not worker_id.strip() or not created_by.strip():
            return MutationResult(
                False, "INVALID_RUN", "worker_id and created_by are required"
            )
        root = Path(repo_root).resolve()
        if not root.is_dir():
            return MutationResult(False, "INVALID_RUN", "repo_root must be a directory")

        worktree_identity: dict[str, str] | None = None
        if base_revision is not None:
            try:
                worktree_identity = collect_git_worktree_identity(root)
            except RuntimeError:
                worktree_identity = None

        try:
            readable = self._normalize_scopes(readable_paths, root)
            forbidden = self._normalize_scopes(forbidden_paths, root)
        except ValueError as exc:
            return MutationResult(False, "INVALID_SCOPE", str(exc))

        limits: dict[str, int] = {}
        for key, value in dict(runtime_limits or {}).items():
            if key not in {"max_attempts", "max_tool_failures", "runtime_seconds"}:
                return MutationResult(
                    False, "INVALID_RUN_LIMIT", f"unsupported runtime limit: {key}"
                )
            if not isinstance(value, int) or value <= 0:
                return MutationResult(
                    False, "INVALID_RUN_LIMIT", f"{key} must be a positive integer"
                )
            limits[key] = value

        with closing(self._connect()) as conn:
            conn.execute("BEGIN IMMEDIATE")
            task = conn.execute(
                "SELECT * FROM tasks WHERE task_id = ?", (task_id,)
            ).fetchone()
            if task is None:
                conn.rollback()
                return MutationResult(False, "NOT_FOUND", f"{task_id} does not exist")
            if task["status"] != "ACTIVE" or task["claimed_by"] != worker_id:
                conn.rollback()
                return MutationResult(
                    False,
                    "RUN_NOT_OWNED",
                    "run manifest requires the current ACTIVE claimant",
                    dict(task),
                )
            if task["agi_status"] != "AGI READY":
                conn.rollback()
                return MutationResult(False, "AGI_NOT_READY", "ACTIVE task is not AGI READY")

            parent_outputs = tuple(
                sorted(
                    row["path"]
                    for row in conn.execute(
                        "SELECT path FROM task_output_paths WHERE task_id = ?",
                        (task_id,),
                    ).fetchall()
                )
            )
            try:
                normalized_parent = self._normalize_scopes(parent_outputs, root)
                writable = self._normalize_scopes(
                    writable_paths if writable_paths is not None else parent_outputs,
                    root,
                )
            except ValueError as exc:
                conn.rollback()
                return MutationResult(False, "INVALID_SCOPE", str(exc))
            if not normalized_parent:
                conn.rollback()
                return MutationResult(False, "INVALID_SCOPE", "task has no output paths")
            escaped = [
                path
                for path in writable
                if not self._covered_by_any(path, normalized_parent)
            ]
            if escaped:
                conn.rollback()
                return MutationResult(
                    False,
                    "WRITE_SCOPE_EXCEEDS_TASK",
                    "run writable scope exceeds task output paths: " + ", ".join(escaped),
                )
            issues = self._validate_scope_contract(
                readable=readable, writable=writable, forbidden=forbidden
            )
            if issues:
                conn.rollback()
                return MutationResult(False, "INVALID_SCOPE", "; ".join(issues))

            context_refs: list[tuple[str, str]] = []
            for raw in context_paths:
                try:
                    relative = self._repo_relative(raw, root)
                except ValueError as exc:
                    conn.rollback()
                    return MutationResult(False, "INVALID_CONTEXT", str(exc))
                full = root / relative
                if not full.is_file():
                    conn.rollback()
                    return MutationResult(
                        False, "INVALID_CONTEXT", f"context is not a file: {relative}"
                    )
                if not self._covered_by_any(relative, readable):
                    conn.rollback()
                    return MutationResult(
                        False, "INVALID_CONTEXT", f"context is outside readable scope: {relative}"
                    )
                if self._covered_by_any(relative, forbidden):
                    conn.rollback()
                    return MutationResult(
                        False, "INVALID_CONTEXT", f"context is forbidden: {relative}"
                    )
                context_refs.append(
                    (relative, hashlib.sha256(full.read_bytes()).hexdigest())
                )

            run_id = f"RUN-{uuid4().hex}"
            task_revision = self._task_revision_conn(conn, task_id)
            created_at = iso_z(utc_now())
            conn.execute(
                """
                INSERT INTO run_manifests(
                    run_id, task_id, task_revision, worker_id, session_id,
                    readable_scope, writable_scope, forbidden_scope,
                    runtime_limits, base_revision, created_by, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    task_id,
                    task_revision,
                    worker_id,
                    session_id,
                    json.dumps(readable, separators=(",", ":")),
                    json.dumps(writable, separators=(",", ":")),
                    json.dumps(forbidden, separators=(",", ":")),
                    json.dumps(limits, sort_keys=True, separators=(",", ":")),
                    base_revision,
                    created_by.strip(),
                    created_at,
                ),
            )
            if worktree_identity is not None:
                conn.execute(
                    """
                    INSERT INTO run_worktree_bindings(
                        run_id, repo_root, git_common_dir, git_dir,
                        worktree_private_dir, head_revision, bound_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        run_id,
                        worktree_identity["repo_root"],
                        worktree_identity["git_common_dir"],
                        worktree_identity["git_dir"],
                        worktree_identity["worktree_private_dir"],
                        worktree_identity["head_revision"],
                        created_at,
                    ),
                )
            conn.executemany(
                "INSERT INTO run_context_refs(run_id, path, sha256) VALUES (?, ?, ?)",
                ((run_id, path, sha) for path, sha in sorted(context_refs)),
            )
            self._append_event(
                conn,
                task_id,
                "RUN_MANIFEST_CREATED",
                created_by.strip(),
                f"{run_id} bound to {worker_id}",
            )
            conn.commit()
        manifest = self.get_run_manifest(run_id)
        return MutationResult(True, "RUN_BOUND", f"created {run_id}", manifest)

    def get_run_manifest(self, run_id: str) -> dict[str, Any] | None:
        with closing(self._connect()) as conn:
            row = conn.execute(
                "SELECT * FROM run_manifests WHERE run_id = ?", (run_id,)
            ).fetchone()
            if row is None:
                return None
            record = dict(row)
            for field in ("readable_scope", "writable_scope", "forbidden_scope", "runtime_limits"):
                record[field] = json.loads(record[field])
            record["context_refs"] = [
                dict(item)
                for item in conn.execute(
                    "SELECT path, sha256 FROM run_context_refs WHERE run_id = ? ORDER BY path",
                    (run_id,),
                ).fetchall()
            ]
            worktree = conn.execute(
                "SELECT * FROM run_worktree_bindings WHERE run_id = ?",
                (run_id,),
            ).fetchone()
            record["worktree"] = dict(worktree) if worktree is not None else None
            return record

    def check_run_stale(
        self, run_id: str, *, repo_root: str | Path
    ) -> dict[str, Any]:
        manifest = self.get_run_manifest(run_id)
        if manifest is None:
            return {"run_id": run_id, "missing_run": True, "stale": True}
        root = Path(repo_root).resolve()
        current_revision = self.compute_task_revision(manifest["task_id"])
        stale_context: list[dict[str, Any]] = []
        for ref in manifest["context_refs"]:
            path = root / ref["path"]
            if not path.is_file():
                stale_context.append({"path": ref["path"], "reason": "missing"})
                continue
            current_hash = hashlib.sha256(path.read_bytes()).hexdigest()
            if current_hash != ref["sha256"]:
                stale_context.append(
                    {
                        "path": ref["path"],
                        "reason": "changed",
                        "recorded_sha256": ref["sha256"],
                        "current_sha256": current_hash,
                    }
                )
        task_missing = current_revision is None
        task_stale = not task_missing and current_revision != manifest["task_revision"]
        return {
            "run_id": run_id,
            "task_id": manifest["task_id"],
            "missing_run": False,
            "task_missing": task_missing,
            "task_stale": task_stale,
            "recorded_task_revision": manifest["task_revision"],
            "current_task_revision": current_revision,
            "stale_context": stale_context,
            "stale": task_missing or task_stale or bool(stale_context),
        }

    def verify_run_changes(
        self,
        run_id: str,
        changed_paths: Iterable[str | Path],
        *,
        repo_root: str | Path,
    ) -> dict[str, Any]:
        manifest = self.get_run_manifest(run_id)
        if manifest is None:
            return {
                "ok": False,
                "run_id": run_id,
                "reason": "run_not_found",
                "out_of_scope": [],
            }
        try:
            changed = self._normalize_scopes(changed_paths, repo_root)
        except ValueError as exc:
            return {
                "ok": False,
                "run_id": run_id,
                "reason": "path_outside_repo",
                "error": str(exc),
                "out_of_scope": [],
            }
        writable = tuple(manifest["writable_scope"])
        out_of_scope = [
            path for path in changed if not self._covered_by_any(path, writable)
        ]
        return {
            "ok": not out_of_scope,
            "run_id": run_id,
            "changed_paths": list(changed),
            "writable_scope": list(writable),
            "out_of_scope": out_of_scope,
        }

    # ---------- Continuity lineage ----------

    def record_continuity_link(
        self, predecessor_id: str, replacement_id: str, *, reason: str
    ) -> MutationResult:
        predecessor_id = predecessor_id.strip()
        replacement_id = replacement_id.strip()
        if not predecessor_id or not replacement_id or not reason.strip():
            return MutationResult(
                False,
                "INVALID_CONTINUITY_LINK",
                "predecessor, replacement, and reason are required",
            )
        if predecessor_id == replacement_id:
            return MutationResult(
                False, "INVALID_CONTINUITY_LINK", "identity cannot continue itself"
            )
        try:
            with closing(self._connect()) as conn:
                conn.execute("BEGIN IMMEDIATE")
                conn.execute(
                    """
                    INSERT INTO continuity_links(
                        predecessor_id, replacement_id, reason, created_at
                    ) VALUES (?, ?, ?, ?)
                    """,
                    (
                        predecessor_id,
                        replacement_id,
                        reason.strip(),
                        iso_z(utc_now()),
                    ),
                )
                conn.commit()
        except sqlite3.IntegrityError as exc:
            return MutationResult(False, "CONTINUITY_CONFLICT", str(exc))
        return MutationResult(
            True,
            "CONTINUITY_LINKED",
            f"{predecessor_id} -> {replacement_id}",
        )

    @staticmethod
    def _continuity_component_conn(
        conn: sqlite3.Connection, identity: str
    ) -> set[str]:
        if not identity:
            return set()
        component = {identity}
        changed = True
        while changed:
            changed = False
            rows = conn.execute(
                "SELECT predecessor_id, replacement_id FROM continuity_links"
            ).fetchall()
            for row in rows:
                left = row["predecessor_id"]
                right = row["replacement_id"]
                if left in component or right in component:
                    before = len(component)
                    component.update((left, right))
                    changed = changed or len(component) != before
        return component

    def continuity_component(self, identity: str) -> set[str]:
        with closing(self._connect()) as conn:
            return self._continuity_component_conn(conn, identity)

    def same_continuity_lineage(self, left: str, right: str) -> bool:
        if not left or not right:
            return False
        with closing(self._connect()) as conn:
            return right in self._continuity_component_conn(conn, left)

    # ---------- Criterion-level evidence ----------

    def list_acceptance_criteria(self, task_id: str) -> list[dict[str, Any]]:
        with closing(self._connect()) as conn:
            return [
                dict(row)
                for row in conn.execute(
                    """
                    SELECT id, task_id, criterion
                    FROM task_acceptance_criteria
                    WHERE task_id = ? ORDER BY id
                    """,
                    (task_id,),
                ).fetchall()
            ]

    def record_criterion_claim(
        self,
        task_id: str,
        criterion_id: int,
        claimed_status: str,
        *,
        author_id: str,
        evidence_refs: Sequence[str | Path] = (),
        repo_root: str | Path,
        run_id: str | None = None,
    ) -> MutationResult:
        claimed_status = claimed_status.strip().lower()
        if claimed_status not in {"complete", "partial", "blocked"}:
            return MutationResult(
                False,
                "INVALID_CRITERION_STATUS",
                "claimed_status must be complete, partial, or blocked",
            )
        root = Path(repo_root).resolve()
        normalized_evidence: list[str] = []
        for raw in evidence_refs:
            try:
                relative = self._repo_relative(raw, root)
            except ValueError as exc:
                return MutationResult(False, "INVALID_EVIDENCE", str(exc))
            if not (root / relative).is_file():
                return MutationResult(
                    False, "INVALID_EVIDENCE", f"evidence file missing: {relative}"
                )
            normalized_evidence.append(relative)
        if claimed_status == "complete" and not normalized_evidence:
            return MutationResult(
                False,
                "MISSING_CRITERION_EVIDENCE",
                "complete criterion claim requires at least one evidence file",
            )

        with closing(self._connect()) as conn:
            conn.execute("BEGIN IMMEDIATE")
            task = conn.execute(
                "SELECT status FROM tasks WHERE task_id = ?", (task_id,)
            ).fetchone()
            if task is None:
                conn.rollback()
                return MutationResult(False, "NOT_FOUND", f"{task_id} does not exist")
            if task["status"] != "READY_FOR_REVIEW":
                conn.rollback()
                return MutationResult(
                    False, "NOT_REVIEWABLE", "criterion claims require READY_FOR_REVIEW"
                )
            criterion = conn.execute(
                """
                SELECT id FROM task_acceptance_criteria
                WHERE id = ? AND task_id = ?
                """,
                (criterion_id, task_id),
            ).fetchone()
            if criterion is None:
                conn.rollback()
                return MutationResult(
                    False, "INVALID_CRITERION", "criterion does not belong to task"
                )
            submission = conn.execute(
                "SELECT * FROM task_submissions WHERE task_id = ?", (task_id,)
            ).fetchone()
            if submission is None:
                conn.rollback()
                return MutationResult(
                    False, "MISSING_SUBMISSION", "criterion claim requires submission"
                )
            if submission["author_id"] != author_id:
                conn.rollback()
                return MutationResult(
                    False,
                    "CLAIM_AUTHOR_MISMATCH",
                    "criterion claim author must be current submission author",
                )
            current_revision = self._task_revision_conn(conn, task_id)
            if run_id:
                run = conn.execute(
                    "SELECT * FROM run_manifests WHERE run_id = ?", (run_id,)
                ).fetchone()
                if run is None or run["task_id"] != task_id:
                    conn.rollback()
                    return MutationResult(False, "INVALID_RUN", "run does not belong to task")
                if run["worker_id"] != author_id:
                    conn.rollback()
                    return MutationResult(
                        False, "RUN_AUTHOR_MISMATCH", "run worker is not submission author"
                    )
                if run["task_revision"] != current_revision:
                    conn.rollback()
                    return MutationResult(False, "STALE_RUN", "run task revision is stale")

            cursor = conn.execute(
                """
                INSERT INTO submission_criterion_claims(
                    task_id, submission_count, criterion_id, claimed_status,
                    evidence_refs, task_revision, run_id, author_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    task_id,
                    submission["submission_count"],
                    criterion_id,
                    claimed_status,
                    json.dumps(sorted(set(normalized_evidence)), separators=(",", ":")),
                    current_revision,
                    run_id,
                    author_id,
                    iso_z(utc_now()),
                ),
            )
            conn.commit()
        return MutationResult(
            True,
            "CRITERION_CLAIM_RECORDED",
            f"criterion claim {cursor.lastrowid} recorded",
            {"claim_id": cursor.lastrowid},
        )

    def get_criterion_claims(
        self, task_id: str, *, current_submission_only: bool = True
    ) -> list[dict[str, Any]]:
        with closing(self._connect()) as conn:
            params: list[Any] = [task_id]
            where = "task_id = ?"
            if current_submission_only:
                submission = conn.execute(
                    "SELECT submission_count FROM task_submissions WHERE task_id = ?",
                    (task_id,),
                ).fetchone()
                if submission is None:
                    return []
                where += " AND submission_count = ?"
                params.append(submission["submission_count"])
            rows = conn.execute(
                f"SELECT * FROM submission_criterion_claims WHERE {where} ORDER BY id",
                params,
            ).fetchall()
            records: list[dict[str, Any]] = []
            for row in rows:
                record = dict(row)
                record["evidence_refs"] = json.loads(record["evidence_refs"])
                record["verdicts"] = [
                    dict(verdict)
                    for verdict in conn.execute(
                        """
                        SELECT * FROM submission_criterion_verdicts
                        WHERE claim_id = ? ORDER BY id
                        """,
                        (row["id"],),
                    ).fetchall()
                ]
                records.append(record)
            return records

    def record_criterion_verdict(
        self,
        claim_id: int,
        verified_status: str,
        *,
        reviewer_id: str,
        notes: str = "",
    ) -> MutationResult:
        verified_status = verified_status.strip().lower()
        if verified_status not in {"confirmed", "rejected"}:
            return MutationResult(
                False,
                "INVALID_CRITERION_VERDICT",
                "verified_status must be confirmed or rejected",
            )
        with closing(self._connect()) as conn:
            conn.execute("BEGIN IMMEDIATE")
            claim = conn.execute(
                "SELECT * FROM submission_criterion_claims WHERE id = ?", (claim_id,)
            ).fetchone()
            if claim is None:
                conn.rollback()
                return MutationResult(False, "NOT_FOUND", f"criterion claim {claim_id} missing")
            review = conn.execute(
                """
                SELECT * FROM reviews
                WHERE task_id = ? AND completed_at IS NULL
                """,
                (claim["task_id"],),
            ).fetchone()
            if review is None or review["reviewer_id"] != reviewer_id:
                conn.rollback()
                return MutationResult(
                    False,
                    "NOT_REVIEW_OWNER",
                    "criterion verdict requires the current review owner",
                )
            if reviewer_id in self._continuity_component_conn(conn, claim["author_id"]):
                conn.rollback()
                return MutationResult(
                    False,
                    "CONTINUITY_REVIEW_FORBIDDEN",
                    "reviewer shares submission-author continuity lineage",
                )
            conn.execute(
                """
                INSERT INTO submission_criterion_verdicts(
                    claim_id, verified_status, reviewer_id, notes, created_at
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    claim_id,
                    verified_status,
                    reviewer_id,
                    notes.strip(),
                    iso_z(utc_now()),
                ),
            )
            conn.commit()
        return MutationResult(
            True,
            "CRITERION_VERDICT_RECORDED",
            f"criterion claim {claim_id} -> {verified_status}",
        )

    def _criterion_approval_issues_conn(
        self, conn: sqlite3.Connection, task_id: str
    ) -> tuple[str, ...]:
        submission = conn.execute(
            "SELECT submission_count FROM task_submissions WHERE task_id = ?",
            (task_id,),
        ).fetchone()
        if submission is None:
            return ()
        submission_count = submission["submission_count"]
        count = conn.execute(
            """
            SELECT count(*) FROM submission_criterion_claims
            WHERE task_id = ? AND submission_count = ?
            """,
            (task_id, submission_count),
        ).fetchone()[0]
        if count == 0:
            return ()

        issues: list[str] = []
        criteria = conn.execute(
            "SELECT id, criterion FROM task_acceptance_criteria WHERE task_id = ? ORDER BY id",
            (task_id,),
        ).fetchall()
        for criterion in criteria:
            claim = conn.execute(
                """
                SELECT * FROM submission_criterion_claims
                WHERE task_id = ? AND submission_count = ? AND criterion_id = ?
                ORDER BY id DESC LIMIT 1
                """,
                (task_id, submission_count, criterion["id"]),
            ).fetchone()
            if claim is None:
                issues.append(f"criterion {criterion['id']} has no current claim")
                continue
            if claim["claimed_status"] != "complete":
                issues.append(
                    f"criterion {criterion['id']} claimed {claim['claimed_status']}, not complete"
                )
                continue
            verdict = conn.execute(
                """
                SELECT verified_status FROM submission_criterion_verdicts
                WHERE claim_id = ? ORDER BY id DESC LIMIT 1
                """,
                (claim["id"],),
            ).fetchone()
            if verdict is None or verdict["verified_status"] != "confirmed":
                status = verdict["verified_status"] if verdict else "unverified"
                issues.append(
                    f"criterion {criterion['id']} latest verification is {status}, not confirmed"
                )
        return tuple(issues)
