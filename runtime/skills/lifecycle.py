"""Pure Skill trust-lifecycle transition logic (SEC4 quarantine lifecycle primitive).

This module is a validated in-memory state machine over
`SkillLifecycleState`. It owns no persistence, no task/session authority, and
no canonical storage -- exactly parallel in spirit to how
`runtime.harness.hooks`'s `HookDirective`/`HookOutcome` are pure logic with no
storage. Actually recording a Skill's current lifecycle state durably, and
wiring operator approval through a real authority path, is out of scope here
and left for a future task (see `work/tasks/skill-trust-lifecycle-wave11.md`).

`runtime.skills.catalog.SkillTrustState` currently has exactly one member,
`UNASSESSED`, because catalog discovery itself can only ever say
"unassessed" -- it has no gate evidence and no operator decision to draw on.
This module is the "future reviewed trust lifecycle" that comment predicted:
a 7-state sequence (`DISCOVERED` -> `VALIDATED`/`QUARANTINED` ->
`APPROVED` -> `ACTIVE` -> `SUPERSEDED`/`RETIRED`) with a pure, statically
checkable transition graph. It is deliberately *not* wired into
`SkillCatalog`/`SkillTrustState` in this task -- that wiring implies a
persistence decision (where does the current state of a given Skill live
across process restarts?) that is explicitly deferred.

Design notes on the transition graph:

- `DISCOVERED` is the only legal starting state: every Skill begins life as
  merely "found on disk", before any gate assessment has run.
- From `DISCOVERED`, only `assess_skill()`'s verdict may move the state
  forward, via `initial_transition_from_gate_report`. A `BLOCK`-severity
  finding forces `SkillGateDisposition.QUARANTINE`, which this module maps
  to `QUARANTINED` -- never `VALIDATED`, never `APPROVED`. Anything else
  (`CLEAR` or `REVIEW_REQUIRED`) maps to `VALIDATED`. This mirrors
  `assess_skill`'s own severity-to-disposition mapping in
  `runtime/skills/gate.py` exactly; this module does not re-derive or
  second-guess that mapping, only translates its result into a lifecycle
  state.
- `VALIDATED -> APPROVED` and `QUARANTINED -> APPROVED` both require an
  explicit, non-empty `actor` (an operator identity). This is a structural
  reminder -- not an authority check -- that approval is never implicit or
  automatic. It mirrors `runtime/state/operational_learning_storage.py`'s
  pattern of state transitions carrying an explicit actor, though this
  module implements none of that subsystem's persistence or authority
  machinery.
- `APPROVED -> ACTIVE` requires no additional actor: by the time a Skill is
  `APPROVED`, the operator decision has already been recorded by the
  `VALIDATED -> APPROVED` or `QUARANTINED -> APPROVED` transition that
  produced it. `ACTIVE` only means "an already-approved Skill has been
  deployed/loaded" -- it is a deployment fact, not a second trust decision,
  so it needs no actor of its own.
- `QUARANTINED` may also move to `RETIRED` (an operator rejects it outright
  instead of approving it).
- `ACTIVE` may move to `SUPERSEDED` (a newer revision replaces it) or
  `RETIRED` (withdrawn).
- `SUPERSEDED` and `RETIRED` are terminal: no outgoing transitions from
  either state are ever legal.
- No transition may skip quarantine review once a gate assessment produced
  `QUARANTINE`: because `DISCOVERED` only ever routes to `VALIDATED` or
  `QUARANTINED` (never directly to `APPROVED` or `ACTIVE`), and the graph
  below has no `DISCOVERED -> APPROVED` or `DISCOVERED -> ACTIVE` edge,
  quarantined content can only reach `APPROVED` through the explicit
  `QUARANTINED -> APPROVED` operator-actor transition.
"""

from __future__ import annotations

from enum import Enum

from .gate import SkillGateDisposition, SkillGateReport


class SkillLifecycleState(str, Enum):
    DISCOVERED = "DISCOVERED"
    VALIDATED = "VALIDATED"
    QUARANTINED = "QUARANTINED"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"
    RETIRED = "RETIRED"


class SkillLifecycleError(ValueError):
    """Raised for any transition not present in the allowed lifecycle graph."""


# Transitions that require an explicit, non-empty operator `actor` identity.
_ACTOR_REQUIRED_TRANSITIONS: frozenset[tuple[SkillLifecycleState, SkillLifecycleState]] = frozenset(
    {
        (SkillLifecycleState.VALIDATED, SkillLifecycleState.APPROVED),
        (SkillLifecycleState.QUARANTINED, SkillLifecycleState.APPROVED),
    }
)

# The complete allowed transition graph. Every edge not listed here is illegal.
_ALLOWED_TRANSITIONS: dict[SkillLifecycleState, frozenset[SkillLifecycleState]] = {
    SkillLifecycleState.DISCOVERED: frozenset(
        {SkillLifecycleState.VALIDATED, SkillLifecycleState.QUARANTINED}
    ),
    SkillLifecycleState.VALIDATED: frozenset({SkillLifecycleState.APPROVED}),
    SkillLifecycleState.QUARANTINED: frozenset(
        {SkillLifecycleState.APPROVED, SkillLifecycleState.RETIRED}
    ),
    SkillLifecycleState.APPROVED: frozenset({SkillLifecycleState.ACTIVE}),
    SkillLifecycleState.ACTIVE: frozenset(
        {SkillLifecycleState.SUPERSEDED, SkillLifecycleState.RETIRED}
    ),
    SkillLifecycleState.SUPERSEDED: frozenset(),
    SkillLifecycleState.RETIRED: frozenset(),
}


def transition(
    current: SkillLifecycleState,
    target: SkillLifecycleState,
    *,
    actor: str | None = None,
) -> SkillLifecycleState:
    """Validate and perform a single Skill lifecycle transition.

    Returns `target` if the transition is legal. Raises `SkillLifecycleError`
    for any transition not present in the allowed graph, and for the two
    operator-approval transitions (`VALIDATED -> APPROVED`,
    `QUARANTINED -> APPROVED`) when `actor` is missing or empty/whitespace.

    This function performs no persistence and no authority check beyond the
    structural non-empty-actor requirement -- verifying that `actor` is a
    real, authorized operator identity is a separate concern for a future
    persistence/authority task.
    """

    if not isinstance(current, SkillLifecycleState):
        raise SkillLifecycleError(f"not a SkillLifecycleState: {current!r}")
    if not isinstance(target, SkillLifecycleState):
        raise SkillLifecycleError(f"not a SkillLifecycleState: {target!r}")

    allowed = _ALLOWED_TRANSITIONS.get(current, frozenset())
    if target not in allowed:
        raise SkillLifecycleError(
            f"illegal Skill lifecycle transition: {current.value} -> {target.value}"
        )

    if (current, target) in _ACTOR_REQUIRED_TRANSITIONS:
        if actor is None or not actor.strip():
            raise SkillLifecycleError(
                f"transition {current.value} -> {target.value} requires a non-empty actor"
            )

    return target


def initial_transition_from_gate_report(report: SkillGateReport) -> SkillLifecycleState:
    """Map a real `SkillGateReport` (`runtime/skills/gate.py`) to the state a
    freshly `DISCOVERED` Skill should move to.

    A `QUARANTINE` disposition (i.e. at least one `BLOCK`-severity finding)
    maps to `QUARANTINED`. Any other disposition (`CLEAR` or
    `REVIEW_REQUIRED`) maps to `VALIDATED`. This is a thin, obviously-correct
    reading of `report.disposition` -- it performs no scanning of its own and
    does not re-derive the disposition from `report.findings`.
    """

    if report.disposition == SkillGateDisposition.QUARANTINE:
        return SkillLifecycleState.QUARANTINED
    return SkillLifecycleState.VALIDATED
