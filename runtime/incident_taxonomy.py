"""Outcome-linked incident-class vocabulary (roadmap 6.27, expansion).

Purpose, stated verbatim from
`work/roadmaps/00-MASTER-MAPS-CAPABILITY-ROADMAP.md` section "6.27
Outcome-linked incident taxonomy": "Current append-only outcomes create the
base," and the roadmap then lists a "Future incident classes include" block.
`work/roadmaps/CAPABILITY_CHECKLIST.md`'s 6.27 row marks this
`DONE (foundation)`, citing exactly this gap: `runtime/state/outcomes.py`'s
append-only `record_outcome` accepts a free-text `failure_class: str`, but
the roadmap's own expanded incident-class vocabulary was not encoded as a
distinct type anywhere.

`IncidentClass` is that full 19-member vocabulary, defined here as a real
enum for the first time, exactly matching `runtime.trust.MemoryTrustClass`
(roadmap 6.22, wave19) in style and level of ambition:

- A single `str, Enum` subclass, member values equal to member names.
- Pure/read-only: this module owns NO persistence, NO task/session
  authority, and NO canonical storage.
- NOT wired into any decision-gating code path. In particular, it does NOT
  modify `runtime.state.outcomes.OutcomeMixin.record_outcome`'s signature or
  validation in any way -- `failure_class` there remains free-text and
  fully backward compatible, including for values outside this enum.
  Actually validating/gating `record_outcome` against this taxonomy is
  deliberately out of scope and left for a future task, exactly as 6.22's
  wave19 `MemoryTrustClass` left decision-gating wiring out of its own
  scope.

One roadmap rule this module preserves explicitly: "Classification must
preserve uncertainty; do not force every incident into a confident story."
That is why `UNKNOWN` is a first-class member of the vocabulary, not an
error case or a fallback bolted on afterward -- it is one of the 19 roadmap
members, and `classify_failure_text` below returns it (rather than raising)
whenever no exact match is found.
"""

from __future__ import annotations

from enum import Enum


class IncidentClass(str, Enum):
    """The roadmap's 19 expanded incident classes, in roadmap order."""

    TOOL_FAILURE = "TOOL_FAILURE"
    CONTEXT_OMISSION = "CONTEXT_OMISSION"
    CONTEXT_POISONING = "CONTEXT_POISONING"
    ROUTING_ERROR = "ROUTING_ERROR"
    SKILL_ROUTING_ERROR = "SKILL_ROUTING_ERROR"
    HELPER_FAILURE = "HELPER_FAILURE"
    HELPER_NO_PROGRESS = "HELPER_NO_PROGRESS"
    RECOVERY_FAILURE = "RECOVERY_FAILURE"
    DUPLICATE_EXECUTION = "DUPLICATE_EXECUTION"
    ENVIRONMENT_DRIFT = "ENVIRONMENT_DRIFT"
    REVIEW_MISS = "REVIEW_MISS"
    STALE_REVIEW_EVIDENCE = "STALE_REVIEW_EVIDENCE"
    VALIDATOR_FALSE_POSITIVE = "VALIDATOR_FALSE_POSITIVE"
    VALIDATOR_FALSE_NEGATIVE = "VALIDATOR_FALSE_NEGATIVE"
    AUTHORITY_VIOLATION_ATTEMPT = "AUTHORITY_VIOLATION_ATTEMPT"
    ACI_AMBIGUITY = "ACI_AMBIGUITY"
    SUPPLY_CHAIN_DEFECT = "SUPPLY_CHAIN_DEFECT"
    OPERATOR_FRICTION_INTERVENTION = "OPERATOR_FRICTION_INTERVENTION"
    UNKNOWN = "UNKNOWN"


def classify_failure_text(text: str) -> IncidentClass:
    """Map an exact-match uppercase string to its `IncidentClass`.

    Pure, read-only convenience lookup. Never called from
    `runtime.state.outcomes.OutcomeMixin.record_outcome` -- that method's
    free-text `failure_class` parameter is unmodified and unvalidated by
    this function. Returns `IncidentClass.UNKNOWN` for any non-exact-match
    input rather than raising, matching the roadmap's explicit rule to
    preserve uncertainty instead of forcing a confident classification.
    """

    if not isinstance(text, str):
        return IncidentClass.UNKNOWN
    try:
        return IncidentClass(text.strip().upper())
    except ValueError:
        return IncidentClass.UNKNOWN
