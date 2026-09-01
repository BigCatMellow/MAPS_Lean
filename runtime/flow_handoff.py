from __future__ import annotations

from typing import Any

from runtime.flow_review import _failed, _mutation_payload
from runtime.state import MutationResult, TaskStore


def flow_handoff(
    store: TaskStore,
    task_id: str,
    *,
    from_worker: str,
    to_worker: str,
    reason: str,
) -> dict[str, Any]:
    """Record a same-task worker handoff as a pure composition over
    ``record_continuity_link``.

    ``flow handoff`` declares that ``to_worker`` continues ``from_worker``'s
    work on task ``task_id``: it records exactly one ``continuity_links`` row
    and stops. The identity->identity link is the whole state change — the
    review-independence consequence falls out automatically from the existing
    ``_continuity_component_conn`` walk on every ``claim_review`` /
    ``record_review`` / review-binding / policy call. The flow touches no
    review table and pre-disqualifies nothing (the component walk is the single
    source of truth).

    **Scope of the consequence.** ``continuity_links`` has no ``task_id`` and
    ``_continuity_component_conn`` is undirected and global, so the effect is
    *not* limited to ``task_id``: after this handoff, ``to_worker`` — and anyone
    already in ``from_worker``'s continuity component — can no longer claim
    independent review of **any** task whose submission author is in that
    component. This is the conservative direction (it only ever removes review
    eligibility) and is exactly how ``record_continuity_link`` behaves for every
    other caller; ``flow handoff`` adds no new semantic.

    Stop boundary — **before the incoming worker claims.** ``flow handoff`` does
    not release ``from_worker``'s claim (there is no claim-release primitive and
    this must not add one), bind a replacement run manifest, create a
    replacement task, select the incoming worker, or launch a session. The
    incoming worker takes over via the unchanged ``claim_task`` recovery path
    once ``from_worker``'s lease expires.

    Guard: ``from_worker`` must be the task's current claimant
    (``status == "ACTIVE"`` and ``claimed_by == from_worker``), else
    ``HANDOFF_NOT_CLAIMANT``. ``from_worker`` is a *declaration the flow checks
    against* ``store.get_task``, not a lookup of whoever holds the claim. The
    guard deliberately does **not** check lease liveness — a handoff normally
    happens *because* ``from_worker``'s session died and its lease is lapsing,
    so an expired-but-still-recorded claim by ``from_worker`` is the common case
    and is accepted.

    The outgoing run id is intentionally *not* returned: there is no lightweight
    task->runs accessor (only ``trace_task``), adding one is outside this
    slice's no-store-mutation scope, and the incoming worker resolves the
    handoff point from ``maps status`` / the trace anyway. Nothing is "frozen"
    by this verb — the outgoing run manifest is already immutable and the task
    revision is content-addressed.
    """

    task = store.get_task(task_id)
    if task is None:
        return _failed(
            "preflight",
            MutationResult(False, "NOT_FOUND", f"{task_id} does not exist"),
        )
    if task.get("status") != "ACTIVE" or task.get("claimed_by") != from_worker:
        return _failed(
            "preflight",
            MutationResult(
                False,
                "HANDOFF_NOT_CLAIMANT",
                (
                    f"flow handoff requires {task_id} ACTIVE and claimed by "
                    f"{from_worker!r} (status={task.get('status')!r}, "
                    f"claimed_by={task.get('claimed_by')!r})"
                ),
                task,
            ),
        )

    link = store.record_continuity_link(from_worker, to_worker, reason=reason)
    if not link.ok:
        # Surfaces INVALID_CONTINUITY_LINK (empty/self) and CONTINUITY_CONFLICT
        # (duplicate) verbatim from the primitive.
        return _failed("continuity_link", link)

    return {
        "ok": True,
        "code": "FLOW_HANDOFF_RECORDED",
        "task_id": task_id,
        "from_worker": from_worker,
        "to_worker": to_worker,
        "continuity_link": _mutation_payload(link),
        "next_step": {
            "state": "STOPPED_BEFORE_REPLACEMENT_CLAIM",
            "reason": (
                f"{to_worker} is now recorded as a continuation of {from_worker} "
                f"(via {task_id}) and — because a continuity link is a global "
                "identity relationship — cannot claim independent review of any "
                f"task authored within {from_worker}'s continuity component; the "
                "incoming worker must still claim-recover the task after the "
                "outgoing lease expires (maps claim / maps flow start) and bind "
                "its own run manifest — flow handoff selects no worker and "
                "launches no session"
            ),
        },
    }
