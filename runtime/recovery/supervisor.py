from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Mapping

from runtime.communication import HcomAdapter, HcomError
from runtime.harness import ExecutionBinding, SessionRef
from .store import RecoveryStore, parse_time

LIVE_STATUSES = {"active", "listening", "waiting", "blocked"}
DEFAULT_BACKOFF_SECONDS = (300, 900, 1800, 3600, 7200)

# Codes that mean an installed CANONICAL_RUN Hook actively evaluated this
# resume and found a concrete mismatch (HOOK_DENIED) or withheld automatic
# approval (APPROVAL_REQUIRED). This is the only outcome tick() treats as an
# explicit canonical-run denial -- the one case where routing through the
# harness changes observable behavior versus the pre-existing direct hcom
# resume call. CANONICAL_GUARD_REQUIRED (no CANONICAL_RUN Hook installed at
# all -- a configuration gap, not a concrete mismatch) and every other
# failure code are deliberately NOT included here: per the design note's
# "does not silently suppress a resume the direct path would have attempted
# unless the canonical-run guard has a concrete mismatch," those fall back to
# the pre-existing direct-resume call instead (see tick()).
_CANONICAL_DENIAL_CODES = {"HOOK_DENIED", "APPROVAL_REQUIRED"}


def session_is_live(session: Mapping[str, Any], *, stale_after_seconds: int = 1800) -> bool:
    if str(session.get("status", "")).lower() not in LIVE_STATUSES:
        return False
    process_bound = session.get("process_bound")
    if process_bound is not None:
        return bool(process_bound)
    age = session.get("status_age_seconds")
    if isinstance(age, (int, float)) and age > stale_after_seconds:
        return False
    return True


def _time_z(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class RecoverySupervisor:
    """Resume known sessions for already-active work; never mutate task truth."""

    def __init__(
        self,
        *,
        task_reader: Any,
        hcom: HcomAdapter,
        recovery_store: RecoveryStore | None = None,
        backoff_seconds: tuple[int, ...] = DEFAULT_BACKOFF_SECONDS,
        silent_stop_probe_delay_seconds: int = 900,
        environment_reader: Any | None = None,
        harness_service: Any | None = None,
        resume_validator: Any | None = None,
    ):
        self.task_reader = task_reader
        self.hcom = hcom
        self.store = recovery_store or RecoveryStore()
        self.backoff_seconds = backoff_seconds
        self.silent_stop_probe_delay_seconds = silent_stop_probe_delay_seconds
        # Optional, advisory-only. When set, must expose
        # list_run_environment_evidence(run_id) -> list[dict]. Never consulted
        # to make or change any recovery decision -- see _advisory_environment_evidence.
        self.environment_reader = environment_reader
        # Optional. When set, must duck-type HarnessService (a
        # resume(binding, session_ref) -> OperationResult method). This is
        # the real production resume path (see tick()): when the incident's
        # existing session/run lineage lets _resolve_harness_binding build an
        # ExecutionBinding/SessionRef, resume is routed through this service
        # instead of the direct self.hcom.resume(...) call. When unset, or
        # when that lineage can't be resolved for a given incident, tick()
        # preserves the pre-existing direct-resume behavior unchanged.
        self.harness_service = harness_service
        # Optional, advisory-only. When set, must expose
        # validate_for_run(run_id) -> dict | None, returning either
        # {"attempted": False, "reason": <closed-vocabulary reason>, ...} or
        # {"attempted": True, "passed": bool, ...}. It is invoked exactly once
        # per incident that is about to be resumed (see tick()), purely so its
        # result can be recorded on that incident's action dict under the
        # "resume_validation" key. No branch in tick() reads it: a failing or
        # missing check never denies, delays, reschedules, suppresses or fails
        # a resume, never changes the retry budget, and never implies
        # environment incompatibility. When left None the "resume_validation"
        # key is None on every action dict and behavior is byte-identical to
        # having no validator at all.
        #
        # Deliberately specified by interface only. This module must stay free
        # of the declared-environment type names that
        # tests/test_recovery_supervisor.py::
        # test_no_validation_tier_commands_or_task_mutation_in_source scans
        # for -- that guard is a lowercased substring scan over this whole
        # file's source text, comments and docstrings included, not an import
        # check, so merely naming those types here (even in prose) would turn
        # it red. Composition of a concrete validator, and every import it
        # needs, belongs in runtime/recovery/production.py.
        self.resume_validator = resume_validator
        if not backoff_seconds or any(value <= 0 for value in backoff_seconds):
            raise ValueError("backoff_seconds must contain positive values")

    def _resolve_run_id(
        self, task: Mapping[str, Any], session: Mapping[str, Any]
    ) -> str | None:
        """Best-available, non-heuristic run_id binding for a detected silent stop.

        Uses the exact, schema-enforced reverse lookup
        (project_id, adapter_id, session_id) -> run_id on `run_session_links`
        (see `RunSessionLineageMixin.resolve_session_run`), never a
        "most recent run for this task" guess. `session` is the raw hcom
        session record (keyed by hcom's own `session_id` field, which is a
        distinct identifier from the display `name` used elsewhere in this
        module for session_name bookkeeping). Returns None whenever any part
        of the lookup is unavailable -- missing project_id, missing hcom
        session_id, no resolver on task_reader, or no matching row -- which is
        exactly today's existing behavior (no advisory evidence).
        """
        resolver = getattr(self.task_reader, "resolve_session_run", None)
        if resolver is None:
            return None
        project_id = str(task.get("project_id") or "").strip()
        session_id = str(session.get("session_id") or "").strip()
        if not project_id or not session_id:
            return None
        try:
            return resolver(project_id, "hcom", session_id)
        except Exception:  # noqa: BLE001 - advisory lookup must never break detection
            return None

    def _advisory_environment_evidence(self, run_id: str | None) -> list[dict[str, Any]] | None:
        """Read-only environment-compatibility evidence for an incident's bound run.

        Stage 2 Option A per work/notes/2026-08-17-recovery-equivalence-authority-design.md:
        purely advisory context, never consulted by any branch in tick() to make
        or change a recovery decision. Returns None (not an empty list) when no
        run is bound or no reader is configured, so absence of evidence is never
        confused with "checked and found nothing" -- both this function's
        failure to look anything up and a genuinely empty result are distinct
        from an actual list of evidence records.
        """
        if not run_id or self.environment_reader is None:
            return None
        try:
            return self.environment_reader.list_run_environment_evidence(run_id)
        except Exception:  # noqa: BLE001 - advisory lookup must never break recovery
            return None

    def _resolve_harness_binding(
        self, incident: Mapping[str, Any], session_name: str
    ) -> tuple[ExecutionBinding | None, SessionRef | None, str]:
        """Construct the ExecutionBinding/SessionRef for a harness-routed resume.

        Reuses exactly the incident/session/run lineage relationship already
        used for _advisory_environment_evidence -- no new lineage-resolution
        machinery. Returns (None, None, reason) whenever any part of that
        lineage is missing or ambiguous; callers must treat that as "the
        harness path cannot be constructed for this incident" and fall back
        to the pre-existing direct hcom resume behavior (see tick()). Never
        raises: any lookup failure is reported as a reason string.
        """
        run_id = incident.get("run_id")
        if not run_id:
            return None, None, "no_run_id_bound"
        try:
            run_id = str(run_id)
            task_id = str(incident.get("task_id", ""))
            worker_id = str(incident.get("worker_id", ""))
            task = self.task_reader.get_task(task_id)
            if task is None:
                return None, None, "task_missing"
            project_id = str(task.get("project_id") or "").strip()
            compute_task_revision = getattr(self.task_reader, "compute_task_revision", None)
            task_revision = (
                str(compute_task_revision(task_id) or "").strip()
                if compute_task_revision is not None
                else ""
            )
            if not project_id or not task_revision:
                return None, None, "task_binding_incomplete"

            resolve_run_session = getattr(self.task_reader, "resolve_run_session", None)
            if resolve_run_session is None:
                return None, None, "no_lineage_resolver"
            lineage = resolve_run_session(run_id)
            if not isinstance(lineage, Mapping) or lineage.get("state") != "EXPLICIT":
                return None, None, "session_not_durably_bound"
            current = lineage.get("current")
            if not isinstance(current, Mapping):
                return None, None, "session_not_durably_bound"
            adapter_session_id = str(current.get("session_id") or "").strip()
            adapter_id = str(current.get("adapter_id") or "").strip()
            if not adapter_session_id or adapter_id != "hcom":
                return None, None, "session_not_durably_bound"

            binding = ExecutionBinding(
                task_id=task_id,
                run_id=run_id,
                worker_id=worker_id,
                task_revision=task_revision,
                project_id=project_id,
                session_id=adapter_session_id,
            )
            session_ref = SessionRef(
                session_id=adapter_session_id,
                worker_id=worker_id,
                adapter="hcom",
                project_id=project_id,
                remote_ref=session_name,
            )
            return binding, session_ref, ""
        except Exception:  # noqa: BLE001 - binding construction must never break recovery
            return None, None, "binding_lookup_error"

    @staticmethod
    def _open_incident_for(state: dict[str, Any], task_id: str, session_name: str) -> bool:
        return any(
            item.get("task_id") == task_id
            and item.get("session_name") == session_name
            and item.get("state") in {"scheduled", "probing"}
            for item in state.get("incidents", {}).values()
        )

    def observe_silent_stops(
        self,
        bindings: Mapping[str, str],
        *,
        now: datetime | None = None,
    ) -> list[str]:
        """Open incidents only for prior-live sessions tied to current ACTIVE claims.

        A worker with multiple ACTIVE tasks is ambiguous because the binding is
        worker -> session, not task -> session. RnS records that ambiguity and
        refuses to guess which task the stopped session represented.
        """
        now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
        sessions = {
            item.get("name"): item
            for item in self.hcom.list_sessions(include_stopped=True)
        }
        state = self.store.load()
        detected: list[tuple[str, str, str, dict[str, Any]]] = []

        tasks_by_worker: dict[str, list[dict[str, Any]]] = {}
        for task in self.task_reader.list_tasks(statuses=("ACTIVE",)):
            worker_id = str(task.get("claimed_by") or "").strip()
            if worker_id:
                tasks_by_worker.setdefault(worker_id, []).append(task)

        state["ambiguous_workers"] = {
            worker_id: sorted(str(task["task_id"]) for task in tasks)
            for worker_id, tasks in tasks_by_worker.items()
            if len(tasks) != 1
        }
        active_by_worker = {
            worker_id: tasks[0]
            for worker_id, tasks in tasks_by_worker.items()
            if len(tasks) == 1
        }

        for worker_id, session_name in sorted(bindings.items()):
            task = active_by_worker.get(worker_id)
            if not task:
                continue
            if session_name in state["terminal_sessions"]:
                continue
            current = session_is_live(sessions.get(session_name, {}))
            previous = bool(state["last_live"].get(session_name, False))
            state["last_live"][session_name] = current
            if previous and not current and not self._open_incident_for(
                state, str(task["task_id"]), session_name
            ):
                detected.append((str(task["task_id"]), worker_id, session_name, task))

        self.store.save(state)
        opened: list[str] = []
        for task_id, worker_id, session_name, task in detected:
            run_id = self._resolve_run_id(task, sessions.get(session_name, {}))
            incident = self.store.schedule(
                task_id=task_id,
                worker_id=worker_id,
                session_name=session_name,
                reason="silent_stop",
                resume_after=_time_z(
                    now + timedelta(seconds=self.silent_stop_probe_delay_seconds)
                ),
                run_id=run_id,
            )
            opened.append(incident.incident_id)
        return opened

    def tick(self, *, now: datetime | None = None) -> list[dict[str, Any]]:
        """Process due incidents and return an audit-friendly action list."""
        now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
        sessions = {
            item.get("name"): item
            for item in self.hcom.list_sessions(include_stopped=True)
        }
        state = self.store.load()
        actions: list[dict[str, Any]] = []

        for incident_id, incident in sorted(state["incidents"].items()):
            if incident.get("state") not in {"scheduled", "probing"}:
                continue
            session_name = str(incident["session_name"])
            task_id = str(incident["task_id"])
            worker_id = str(incident["worker_id"])
            # Advisory only -- never read by any branch below to make or
            # change a decision. See _advisory_environment_evidence docstring.
            evidence = self._advisory_environment_evidence(incident.get("run_id"))
            # harness_resume is populated only once an actual resume attempt
            # is made below (this incident wasn't suppressed/resolved/failed
            # first); no lineage lookup or harness call happens for those
            # other outcomes.
            harness_resume: dict[str, Any] | None = None
            # Same contract as harness_resume: stays None unless this incident
            # actually reaches a resume attempt below, so suppressed/resolved/
            # failed/not-yet-due incidents run no validation at all.
            resume_validation: dict[str, Any] | None = None

            if session_name in state["terminal_sessions"]:
                incident["state"] = "suppressed"
                incident["last_error"] = "terminal_session"
                incident["updated_at"] = _time_z(now)
                actions.append(
                    {
                        "incident_id": incident_id,
                        "action": "suppress",
                        "reason": "terminal_session",
                        "environment_evidence": evidence,
                        "harness_resume": harness_resume,
                        "resume_validation": resume_validation,
                    }
                )
                continue

            task = self.task_reader.get_task(task_id)
            if task is None:
                reason = "task_missing"
            elif str(task.get("status", "")).upper() != "ACTIVE":
                reason = "task_not_active"
            elif task.get("claimed_by") != worker_id:
                reason = "claim_changed"
            else:
                reason = ""
            if reason:
                incident["state"] = "suppressed"
                incident["last_error"] = reason
                incident["updated_at"] = _time_z(now)
                actions.append(
                    {
                        "incident_id": incident_id,
                        "action": "suppress",
                        "reason": reason,
                        "environment_evidence": evidence,
                        "harness_resume": harness_resume,
                        "resume_validation": resume_validation,
                    }
                )
                continue

            if session_is_live(sessions.get(session_name, {})):
                incident["state"] = "resolved"
                incident["last_error"] = ""
                incident["updated_at"] = _time_z(now)
                actions.append(
                    {
                        "incident_id": incident_id,
                        "action": "resolve",
                        "reason": "session_live",
                        "environment_evidence": evidence,
                        "harness_resume": harness_resume,
                        "resume_validation": resume_validation,
                    }
                )
                continue

            due_at = parse_time(str(incident["resume_after"]))
            if incident.get("next_attempt_at"):
                due_at = max(due_at, parse_time(str(incident["next_attempt_at"])))
            if now < due_at:
                continue

            attempt = int(incident.get("attempt", 0))
            if attempt >= len(self.backoff_seconds):
                incident["state"] = "failed"
                incident["last_error"] = "retry_budget_exhausted"
                incident["updated_at"] = _time_z(now)
                actions.append(
                    {
                        "incident_id": incident_id,
                        "action": "fail",
                        "reason": "retry_budget_exhausted",
                        "environment_evidence": evidence,
                        "harness_resume": harness_resume,
                        "resume_validation": resume_validation,
                    }
                )
                continue

            # Advisory pre-resume observation. Placed here deliberately: this
            # is the first point at which the incident is committed to a
            # resume attempt (every earlier outcome -- suppress, resolve, fail,
            # not-yet-due -- has already continue'd out), and it is still
            # strictly *before* the resume, so the observation is not
            # confounded by whatever the resumed session then does. The result
            # is recorded on the action dict below and read by nothing.
            if self.resume_validator is not None:
                try:
                    resume_validation = self.resume_validator.validate_for_run(
                        incident.get("run_id")
                    )
                except Exception:  # noqa: BLE001 - advisory check must never break recovery
                    # Deliberately carries no exception text: the validator is
                    # a caller-supplied object whose messages have not passed
                    # through any redaction boundary this module controls.
                    resume_validation = {
                        "attempted": False,
                        "reason": "validation_error",
                    }

            resolved = False
            if self.harness_service is not None:
                binding, session_ref, binding_reason = self._resolve_harness_binding(
                    incident, session_name
                )
                if binding is not None and session_ref is not None:
                    try:
                        result = self.harness_service.resume(binding, session_ref)
                    except Exception as exc:  # noqa: BLE001 - service failure must not crash the tick
                        harness_resume = {
                            "attempted": True,
                            "ok": False,
                            "code": "HARNESS_CALL_ERROR",
                            "summary": str(exc),
                        }
                    else:
                        harness_resume = {
                            "attempted": True,
                            "ok": bool(result.ok),
                            "code": str(result.code),
                            "summary": str(result.summary),
                        }
                        if result.ok:
                            error = ""
                            action = "resume"
                            resolved = True
                        elif str(result.code) in _CANONICAL_DENIAL_CODES:
                            # A concrete canonical-run mismatch -- an
                            # installed CANONICAL_RUN Hook actively denied
                            # (or required approval for) this resume. This
                            # is the one outcome allowed to change behavior
                            # versus the pre-existing direct-resume call: no
                            # fallback, the denial is observable via
                            # harness_resume above, and no task truth is
                            # touched.
                            error = str(result.summary)
                            action = "resume_denied"
                            resolved = True
                        # else: harness attempt failed for a non-canonical
                        # reason (e.g. no CANONICAL_RUN Hook installed at
                        # all, an adapter/provider failure) -- fall through
                        # below and preserve current direct-resume behavior
                        # for this incident so a resume is never silently
                        # suppressed by anything short of an explicit
                        # canonical-run denial.
                else:
                    harness_resume = {"attempted": False, "reason": binding_reason}

            if not resolved:
                try:
                    self.hcom.resume(session_name, headless=True, go=True)
                    error = ""
                    action = "resume"
                except HcomError as exc:
                    error = str(exc)
                    action = "resume_failed"

            attempt += 1
            incident["attempt"] = attempt
            incident["state"] = "probing"
            incident["last_attempt_at"] = _time_z(now)
            incident["last_error"] = error
            incident["next_attempt_at"] = _time_z(
                now
                + timedelta(
                    seconds=self.backoff_seconds[
                        min(attempt - 1, len(self.backoff_seconds) - 1)
                    ]
                )
            )
            incident["updated_at"] = _time_z(now)
            actions.append(
                {
                    "incident_id": incident_id,
                    "action": action,
                    "attempt": attempt,
                    "error": error,
                    "environment_evidence": evidence,
                    "harness_resume": harness_resume,
                    "resume_validation": resume_validation,
                }
            )

        self.store.save(state)
        return actions
