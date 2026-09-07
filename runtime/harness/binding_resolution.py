"""Shared ExecutionBinding/SessionRef resolution from run/session lineage.

Factored verbatim out of ``RecoverySupervisor._resolve_harness_binding`` (rule
12: one lineage-resolution path, not two). The body referenced only
``self.task_reader``; here that becomes the first positional argument and
nothing else changes. Two call sites now share it:

* the recovery supervisor's harness-routed resume
  (``runtime/recovery/supervisor.py``);
* the ``maps run send-context`` context-delivery call site
  (``work/notes/2026-09-06-harness-send-callsite-design.md`` §2d).

It uses only the reader's existing read methods (``get_task``,
``compute_task_revision``, ``resolve_run_session``) -- no new state, no new
lineage-resolution semantics. Never raises: any lookup failure is reported as
a reason string.
"""

from __future__ import annotations

from typing import Any, Mapping

from .types import ExecutionBinding, SessionRef


def resolve_harness_binding(
    task_reader: Any,
    incident: Mapping[str, Any],
    session_name: str,
) -> tuple[ExecutionBinding | None, SessionRef | None, str]:
    """Construct the ExecutionBinding/SessionRef for a harness-routed operation.

    Reuses exactly the incident/session/run lineage relationship already used
    for recovery's advisory environment-evidence lookup -- no new
    lineage-resolution machinery. Returns ``(None, None, reason)`` whenever any
    part of that lineage is missing or ambiguous; callers must treat that as
    "the harness path cannot be constructed for this incident" and fail closed
    (never fall back to an unguarded direct send/resume).

    ``session_name`` is recorded verbatim as ``SessionRef.remote_ref`` and must
    be non-empty; callers with no display name should pass the adapter
    session_id (or the run_id) so the ref is still populated.
    """
    run_id = incident.get("run_id")
    if not run_id:
        return None, None, "no_run_id_bound"
    try:
        run_id = str(run_id)
        task_id = str(incident.get("task_id", ""))
        worker_id = str(incident.get("worker_id", ""))
        task = task_reader.get_task(task_id)
        if task is None:
            return None, None, "task_missing"
        project_id = str(task.get("project_id") or "").strip()
        compute_task_revision = getattr(task_reader, "compute_task_revision", None)
        task_revision = (
            str(compute_task_revision(task_id) or "").strip()
            if compute_task_revision is not None
            else ""
        )
        if not project_id or not task_revision:
            return None, None, "task_binding_incomplete"

        resolve_run_session = getattr(task_reader, "resolve_run_session", None)
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
    except Exception:  # noqa: BLE001 - binding construction must never break a caller
        return None, None, "binding_lookup_error"
