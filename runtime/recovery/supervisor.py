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

# A canonical-run denial is deterministic w.r.t. an identical re-run, so it must
# not consume a transient `backoff_seconds` retry attempt (that would launder the
# real cause through `retry_budget_exhausted`). Instead the incident is parked in
# a distinct `denied` state, rescheduled on a flat interval, and given its own
# small ceiling: this many consecutive denials with no intervening non-denied
# outcome promotes the incident to `failed` / `canonical_denial_persistent`, so a
# genuinely un-remediable run does not probe forever. Independent of the
# transient retry budget. See
# work/notes/2026-08-31-canonical-enforcement-first-exposure-design.md §2b.
_MAX_CONSECUTIVE_CANONICAL_DENIALS = 3

# Incident states tick() and _open_incident_for treat as still in play. A
# blocked_validation incident (see tick()) is re-processed on the next due
# pass exactly like a probing one -- the block is a parked, recoverable state,
# not a terminal one. "denied" is the equivalent parked state for a
# canonical-run denial (PR #195); it is listed here so the two features
# compose regardless of merge order -- an incident only ever reaches it once
# that PR's tick() branch exists.
_REPROCESSABLE_STATES = {"scheduled", "probing", "blocked_validation", "denied"}

# Consecutive-block ceiling for the opt-in resume-validation gate. Mirrors the
# canonical-denial ceiling pattern: a failed quick tier is deterministic
# w.r.t. an identical re-run, so a validation block never consumes the
# transient `attempt` retry budget; instead N consecutive blocks with no
# intervening non-block outcome promote the incident to a distinct terminal
# failure (`validation_block_persistent`), separate from
# `retry_budget_exhausted`.
_MAX_CONSECUTIVE_VALIDATION_BLOCKS = 3


def _quick_validation_failed(result: Any) -> bool:
    """True only for a concrete failed quick-tier check.

    A result of `{"attempted": False, ...}` -- a missing / ambiguous /
    unparseable spec, a budget-skipped incident, or an errored validator --
    is NOT a failure and must never block a resume (design note Q6.4). Only an
    explicit `{"attempted": True, "passed": False}` blocks.
    """
    return (
        isinstance(result, Mapping)
        and result.get("attempted") is True
        and result.get("passed") is False
    )


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
        validation_blocks_resume: bool = False,
        terminate_on_canonical_denial: bool = False,
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
        # Opt-in resume-validation gate. Default False: when False the
        # `resume_validator` result stays strictly advisory (byte-identical to
        # before this flag existed -- the result is recorded on the action
        # dict and read by nothing). When True, an incident whose pre-resume
        # check returns a concrete `{"attempted": True, "passed": False}` is
        # parked in a distinct `blocked_validation` state *before* the resume
        # attempt: no harness/hcom resume call is made, the transient `attempt`
        # retry budget is untouched, and the incident is rescheduled on the
        # flat `silent_stop_probe_delay_seconds` probe interval. This is
        # disjoint from -- and composes ahead of -- any canonical-run denial
        # handling on the harness path. Composed only via
        # runtime/recovery/production.py from an explicit
        # `maps recovery-tick --enforce-validation` (which itself requires
        # `--repo-root`, since no validator is constructed without it).
        self._validation_blocks_resume = bool(validation_blocks_resume)
        # Opt-in destructive-termination of a session whose resume an installed
        # CANONICAL_RUN Hook has denied `_MAX_CONSECUTIVE_CANONICAL_DENIALS`
        # times in a row. Default False: when False, tick() never calls
        # `harness_service.stop()` and the `canonical_denial_persistent`
        # promotion is byte-identical to before this flag existed (the incident
        # still ends `failed` / `canonical_denial_persistent`; only the new
        # audit-only `harness_stop` action key -- always None when the flag is
        # off -- is added). When True, and only on that terminal promotion, a
        # single bounded `HarnessService.stop(binding, session_ref, reason)` is
        # routed for the binding this tick already resolved for the resume
        # attempt, firing BEFORE_DESTRUCTIVE_ACTION -> DestructiveExternalAction
        # Guard -> SESSION_STOPPING -> adapter.stop(). Fail-closed
        # (_maybe_terminate_denied_session): a session that cannot be positively
        # and canonically identified is never terminated, and any stop failure
        # (guard veto, binding-integrity mismatch, raised exception) is recorded
        # but never changes the incident outcome. Arming it is a strictly larger
        # authority grant than arming a resume-denial, so it stays a separate
        # opt-in from `validation_blocks_resume` / canonical-run enforcement.
        # Composed only via runtime/recovery/production.py from an explicit
        # `maps recovery-tick --terminate-denied-sessions` (which itself
        # requires `--enforce-canonical-run`, since there is no HarnessService
        # to route a stop through otherwise). See
        # work/notes/2026-09-06-harness-stop-callsite-design.md §3.
        self._terminate_on_canonical_denial = bool(terminate_on_canonical_denial)
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

    def _maybe_terminate_denied_session(
        self,
        binding: ExecutionBinding | None,
        session_ref: SessionRef | None,
        binding_reason: str,
    ) -> dict[str, Any] | None:
        """Route one bounded, opt-in `HarnessService.stop()` for a persistently
        canonical-denied session. Audit-only: the return value is recorded on
        the terminal action dict under `harness_stop` and read by nothing.

        Returns None when `terminate_on_canonical_denial` is False -- the flag's
        "byte-identical when off" contract: no call is made and the caller
        records `harness_stop=None`.

        Fail-closed (design note §3c): never terminate a session that cannot be
        positively and canonically identified, and never let an inability-to-
        stop change the incident outcome (the caller has already set
        state="failed" / "canonical_denial_persistent" regardless of what this
        returns):

        - no HarnessService                 -> {"attempted": False, "reason": "no_harness_service"}
        - binding / session_ref unresolved  -> {"attempted": False, "reason": <binding_reason>}
          (cannot happen on the canonical-denial branch today -- that branch is
          only reachable when both were built -- but asserted defensively; no
          direct `hcom stop` path is invented here)
        - stop() returns a non-ok result    -> the result recorded verbatim, no
          retry within the tick, incident state untouched. A guard veto of the
          stop is itself a fail-closed outcome (session left parked, matching
          today's behavior).
        - stop() raises                     -> caught, recorded as HARNESS_CALL_ERROR
        """
        if not self._terminate_on_canonical_denial:
            return None
        if self.harness_service is None:
            return {"attempted": False, "reason": "no_harness_service"}
        if binding is None or session_ref is None:
            return {
                "attempted": False,
                "reason": binding_reason or "binding_unresolved",
            }
        # Fixed, closed-vocabulary provenance string constructed at this code
        # path -- never inferred from the denial. Passed straight through
        # HarnessService.stop() to adapter.stop(binding, reason).
        reason = "recovery:canonical_denial_persistent"
        try:
            result = self.harness_service.stop(binding, session_ref, reason)
        except Exception as exc:  # noqa: BLE001 - service failure must not crash the tick
            return {
                "attempted": True,
                "ok": False,
                "code": "HARNESS_CALL_ERROR",
                "summary": str(exc),
            }
        return {
            "attempted": True,
            "ok": bool(result.ok),
            "code": str(result.code),
            "summary": str(result.summary),
        }

    @staticmethod
    def _open_incident_for(state: dict[str, Any], task_id: str, session_name: str) -> bool:
        return any(
            item.get("task_id") == task_id
            and item.get("session_name") == session_name
            and item.get("state") in _REPROCESSABLE_STATES
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
            if incident.get("state") not in _REPROCESSABLE_STATES:
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

            # Opt-in resume-validation gate. Runs here deliberately: after the
            # advisory observation above (so the same result is still recorded
            # on the action dict) and strictly *before* any harness/hcom
            # resume call, so a broken environment never triggers a
            # canonical-guarded resume attempt. Disjoint from the canonical
            # denial path below: this parks the incident in `blocked_validation`
            # and `continue`s before `attempt` is ever incremented, so it
            # composes cleanly with -- and cannot collide with -- that path's
            # own state handling.
            if self._validation_blocks_resume and _quick_validation_failed(
                resume_validation
            ):
                blocks = int(incident.get("validation_blocks", 0)) + 1
                incident["validation_blocks"] = blocks
                incident["last_attempt_at"] = _time_z(now)
                incident["updated_at"] = _time_z(now)
                if blocks >= _MAX_CONSECUTIVE_VALIDATION_BLOCKS:
                    incident["state"] = "failed"
                    incident["last_error"] = "validation_block_persistent"
                    block_action = "fail"
                    block_reason = "validation_block_persistent"
                else:
                    incident["state"] = "blocked_validation"
                    incident["last_error"] = "quick validation tier failed"
                    incident["next_attempt_at"] = _time_z(
                        now
                        + timedelta(seconds=self.silent_stop_probe_delay_seconds)
                    )
                    block_action = "resume_blocked_validation"
                    block_reason = "quick_validation_failed"
                actions.append(
                    {
                        "incident_id": incident_id,
                        "action": block_action,
                        "reason": block_reason,
                        "validation_blocks": blocks,
                        "environment_evidence": evidence,
                        "harness_resume": harness_resume,
                        "resume_validation": resume_validation,
                    }
                )
                continue

            # Any non-block outcome for an incident that had accumulated a
            # validation-block streak resets it -- the ceiling is for
            # *consecutive* blocks only.
            if incident.get("validation_blocks"):
                incident["validation_blocks"] = 0

            resolved = False
            canonically_denied = False
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
                            canonically_denied = True
                        # else: harness attempt failed for a non-canonical
                        # reason (e.g. no CANONICAL_RUN Hook installed at
                        # all, an adapter/provider failure) -- fall through
                        # below and preserve current direct-resume behavior
                        # for this incident so a resume is never silently
                        # suppressed by anything short of an explicit
                        # canonical-run denial.
                else:
                    harness_resume = {"attempted": False, "reason": binding_reason}

            if canonically_denied:
                # A canonical-run Hook denied this resume. The denial is
                # deterministic w.r.t. an identical re-run, so it does NOT
                # consume a transient retry `attempt` and is NOT laundered
                # through `retry_budget_exhausted`. Park the incident in a
                # distinct `denied` state carrying the deny code, reschedule on
                # a flat interval, and only give up after its own separate
                # consecutive-denial ceiling. `attempt` is left untouched.
                denials = int(incident.get("canonical_denials", 0)) + 1
                incident["canonical_denials"] = denials
                incident["last_attempt_at"] = _time_z(now)
                incident["last_error"] = error
                incident["updated_at"] = _time_z(now)
                if denials >= _MAX_CONSECUTIVE_CANONICAL_DENIALS:
                    incident["state"] = "failed"
                    incident["last_error"] = "canonical_denial_persistent"
                    # Opt-in, default-off. `binding` / `session_ref` /
                    # `binding_reason` are the pair this tick already resolved
                    # for the resume attempt above -- this branch is only
                    # reachable when that resolution succeeded, so no second
                    # `_resolve_harness_binding` call is made. The incident
                    # state is already terminal above; this never changes it.
                    harness_stop = self._maybe_terminate_denied_session(
                        binding, session_ref, binding_reason
                    )
                    actions.append(
                        {
                            "incident_id": incident_id,
                            "action": "fail",
                            "reason": "canonical_denial_persistent",
                            "attempt": attempt,
                            "error": "canonical_denial_persistent",
                            "environment_evidence": evidence,
                            "harness_resume": harness_resume,
                            "harness_stop": harness_stop,
                            "resume_validation": resume_validation,
                        }
                    )
                else:
                    incident["state"] = "denied"
                    incident["next_attempt_at"] = _time_z(
                        now
                        + timedelta(seconds=self.silent_stop_probe_delay_seconds)
                    )
                    actions.append(
                        {
                            "incident_id": incident_id,
                            "action": "resume_denied",
                            "attempt": attempt,
                            "error": error,
                            "environment_evidence": evidence,
                            "harness_resume": harness_resume,
                            "resume_validation": resume_validation,
                        }
                    )
                continue

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
            # Any non-denied outcome breaks a canonical-denial streak.
            incident["canonical_denials"] = 0
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
