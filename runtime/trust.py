"""Cross-subsystem memory trust class vocabulary (roadmap 6.22, MVP).

Purpose, stated verbatim from
`work/roadmaps/00-MASTER-MAPS-CAPABILITY-ROADMAP.md` section "6.22 Memory
trust classes": "Prevent 'remembered' content from becoming authority by
repetition." Detailed roadmap pointer:
`work/roadmaps/agent-harness-capabilities/04-agentic-security.md`.

`MemoryTrustClass` is the full 11-member candidate vocabulary the roadmap
names, defined here as a single real enum for the first time. Before this
module, trust-adjacent vocabulary existed only per-subsystem and did not
overlap cleanly:

- `runtime.skills.catalog.SkillTrustState` -- one member, `UNASSESSED`.
- `runtime.skills.lifecycle.SkillLifecycleState` -- seven members
  (`DISCOVERED`, `VALIDATED`, `QUARANTINED`, `APPROVED`, `ACTIVE`,
  `SUPERSEDED`, `RETIRED`), which already overlaps heavily with the
  roadmap's candidate list.
- `runtime.operational_learning`'s `_STATUSES` (`CANDIDATE`, `ACTIVE`,
  `RETIRED`) plus the `GUIDANCE_ONLY` authority label used in
  `runtime.context_builder`'s `_lesson_guidance`.

This module defines the unified vocabulary and three READ-ONLY
correspondence mappings from each existing subsystem vocabulary onto it.
Exactly like `runtime.skills.lifecycle`'s own docstring says of itself: this
module owns NO persistence, NO task/session authority, and NO canonical
storage. The mapping functions below are pure lookups -- they do not
persist anything, do not change any subsystem's real behavior, and do not
grant authority. In particular, this module does NOT modify
`SkillTrustState`, `SkillLifecycleState`, or `operational_learning.py`'s
real enum/status handling.

This module itself still gates nothing: it defines vocabulary and lookups
only. One consumer now makes a real decision from it --
`runtime.policy.memory_trust_gate.admit_memory_evidence()`, the Context
Builder admission gate designed in
`work/notes/2026-08-25-memory-trust-enforcement-gate-design.md`, which
decides LOAD / WITHHOLD / DENY for memory-like plan evidence
(`guidance` / `withheld_guidance` / `skills`). Gating at the *action /
tool-call* level (e.g. "only ACTIVE_INSTRUCTION or CANONICAL_POLICY content
may influence a tool call") remains out of scope and left for a future task,
exactly as SEC4 (`runtime/skills/lifecycle.py`) left persistence and
authority wiring out of its own scope.
"""

from __future__ import annotations

from enum import Enum

from .skills.catalog import SkillTrustState
from .skills.lifecycle import SkillLifecycleState


class MemoryTrustClass(str, Enum):
    """The roadmap's 11 candidate memory trust classes, in roadmap order."""

    UNTRUSTED_INPUT = "UNTRUSTED_INPUT"
    OBSERVATION = "OBSERVATION"
    CLAIM = "CLAIM"
    CANDIDATE_LESSON = "CANDIDATE_LESSON"
    REVIEWED_GUIDANCE = "REVIEWED_GUIDANCE"
    APPROVED_SKILL = "APPROVED_SKILL"
    ACTIVE_INSTRUCTION = "ACTIVE_INSTRUCTION"
    CANONICAL_POLICY = "CANONICAL_POLICY"
    SUPERSEDED = "SUPERSEDED"
    RETIRED = "RETIRED"
    QUARANTINED = "QUARANTINED"


class TrustClassError(ValueError):
    """Raised when a raw status string has no known trust-class mapping."""


# --- runtime.skills.catalog.SkillTrustState ---------------------------------
#
# `SkillTrustState` currently has exactly one member, `UNASSESSED`, because
# catalog discovery itself can only ever say "unassessed" -- it has no gate
# evidence and no operator decision to draw on (see the comment on
# `SkillTrustState` itself). The most honest `MemoryTrustClass` mapping for
# that is `OBSERVATION`: an unassessed catalog entry is an observed fact
# ("a Skill exists on disk with this provenance"), not yet a `CLAIM` (no
# assessment has been made about it), and certainly not `CANDIDATE_LESSON`,
# `REVIEWED_GUIDANCE`, or anything further along the trust ladder.
_SKILL_TRUST_STATE_TO_MEMORY_TRUST_CLASS: dict[SkillTrustState, MemoryTrustClass] = {
    SkillTrustState.UNASSESSED: MemoryTrustClass.OBSERVATION,
}


def skill_trust_class(state: SkillTrustState) -> MemoryTrustClass:
    """Map a `runtime.skills.catalog.SkillTrustState` to its corresponding
    `MemoryTrustClass`. Read-only lookup; grants no authority.
    """

    if not isinstance(state, SkillTrustState):
        raise TrustClassError(f"not a SkillTrustState: {state!r}")
    return _SKILL_TRUST_STATE_TO_MEMORY_TRUST_CLASS[state]


# --- runtime.skills.lifecycle.SkillLifecycleState ---------------------------
#
# This is close to 1:1 given the overlap already noted in the roadmap
# checklist and in `lifecycle.py`'s own docstring:
#
# - `DISCOVERED` -> `OBSERVATION`: a freshly discovered Skill is merely
#   "found on disk", before any gate assessment has run -- an observed fact,
#   nothing claimed or reviewed yet.
# - `VALIDATED` -> `REVIEWED_GUIDANCE`, not `CLAIM`: `VALIDATED` is reached
#   only after `assess_skill()`'s gate has run and produced a `CLEAR` or
#   `REVIEW_REQUIRED` verdict (see `initial_transition_from_gate_report`).
#   That is real automated review evidence, not a bare unverified assertion
#   (`CLAIM`) and not yet operator-approved (`APPROVED_SKILL`) -- so
#   `REVIEWED_GUIDANCE` ("has been reviewed, not yet authoritative") is the
#   more honest fit than either neighbor.
# - `QUARANTINED` -> `QUARANTINED` (exact name match; a `BLOCK`-severity gate
#   finding).
# - `APPROVED` -> `APPROVED_SKILL` (an operator has explicitly approved it
#   via a non-empty `actor`, per `transition()`'s actor-required edges).
# - `ACTIVE` -> `ACTIVE_INSTRUCTION` (deployed/loaded; the operator trust
#   decision already happened at `APPROVED`, so `ACTIVE` is the deployment
#   fact that makes it live instruction).
# - `SUPERSEDED` -> `SUPERSEDED`, `RETIRED` -> `RETIRED` (exact name
#   matches; both terminal in `lifecycle.py`'s transition graph too).
_SKILL_LIFECYCLE_STATE_TO_MEMORY_TRUST_CLASS: dict[SkillLifecycleState, MemoryTrustClass] = {
    SkillLifecycleState.DISCOVERED: MemoryTrustClass.OBSERVATION,
    SkillLifecycleState.VALIDATED: MemoryTrustClass.REVIEWED_GUIDANCE,
    SkillLifecycleState.QUARANTINED: MemoryTrustClass.QUARANTINED,
    SkillLifecycleState.APPROVED: MemoryTrustClass.APPROVED_SKILL,
    SkillLifecycleState.ACTIVE: MemoryTrustClass.ACTIVE_INSTRUCTION,
    SkillLifecycleState.SUPERSEDED: MemoryTrustClass.SUPERSEDED,
    SkillLifecycleState.RETIRED: MemoryTrustClass.RETIRED,
}


def skill_lifecycle_trust_class(state: SkillLifecycleState) -> MemoryTrustClass:
    """Map a `runtime.skills.lifecycle.SkillLifecycleState` to its
    corresponding `MemoryTrustClass`. Read-only lookup; grants no authority.
    """

    if not isinstance(state, SkillLifecycleState):
        raise TrustClassError(f"not a SkillLifecycleState: {state!r}")
    return _SKILL_LIFECYCLE_STATE_TO_MEMORY_TRUST_CLASS[state]


# --- runtime.operational_learning status strings ----------------------------
#
# `operational_learning.py`'s `_STATUSES` (`CANDIDATE`, `ACTIVE`, `RETIRED`)
# are raw strings, not an enum, so this mapping takes a raw string and
# raises `TrustClassError` for anything unrecognized.
#
# - `CANDIDATE` -> `CANDIDATE_LESSON`: exact conceptual match -- a candidate
#   lesson has not been operator-promoted and "cannot carry promotion
#   authority" per `operational_learning.py`'s own validation.
# - `ACTIVE` -> `REVIEWED_GUIDANCE`, not `ACTIVE_INSTRUCTION`: an ACTIVE
#   operational lesson is surfaced to the Context Builder under the
#   `GUIDANCE_ONLY` authority label verbatim (see
#   `runtime.context_builder._lesson_guidance`'s docstring, "Attributed
#   GUIDANCE_ONLY evidence from operator-promoted ACTIVE lessons") and is
#   explicitly "never merged into instructions/boundaries". That is a
#   stronger claim than `CANDIDATE_LESSON` -- an operator did promote it --
#   but it is not `ACTIVE_INSTRUCTION`, which the roadmap vocabulary reserves
#   for content actually driving behavior as instruction. `REVIEWED_GUIDANCE`
#   ("operator-reviewed, offered as guidance, not authoritative
#   instruction") is the more honest mapping, matching the subsystem's own
#   `GUIDANCE_ONLY` label in spirit.
# - `RETIRED` -> `RETIRED`: exact name match.
_OPERATIONAL_LEARNING_STATUS_TO_MEMORY_TRUST_CLASS: dict[str, MemoryTrustClass] = {
    "CANDIDATE": MemoryTrustClass.CANDIDATE_LESSON,
    "ACTIVE": MemoryTrustClass.REVIEWED_GUIDANCE,
    "RETIRED": MemoryTrustClass.RETIRED,
}


def operational_learning_trust_class(status: str) -> MemoryTrustClass:
    """Map a `runtime.operational_learning` status string (`CANDIDATE`,
    `ACTIVE`, `RETIRED`) to its corresponding `MemoryTrustClass`. Read-only
    lookup; grants no authority. Raises `TrustClassError` for any
    unrecognized string.
    """

    if not isinstance(status, str):
        raise TrustClassError(f"not a status string: {status!r}")
    try:
        return _OPERATIONAL_LEARNING_STATUS_TO_MEMORY_TRUST_CLASS[status]
    except KeyError as exc:
        raise TrustClassError(
            f"unrecognized operational_learning status: {status!r}"
        ) from exc
