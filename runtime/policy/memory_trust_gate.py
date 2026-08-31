"""Fail-closed admission gate over `MemoryTrustClass` memory-like evidence.

Implements the design note
`work/notes/2026-08-25-memory-trust-enforcement-gate-design.md` (roadmap
6.22), which builds on the seam PR #148 already selected: Context Builder's
memory-like evidence buckets (`guidance` / `withheld_guidance` / `skills`).

Classification is *read* from the existing read-only correspondence mappings
in `runtime.trust`; this module derives nothing of its own. There is no
policy engine, no rules DSL, no configurable threshold, no persisted trust
store, and no inference over content — the admission table below is a fixed
dict literal, deliberately keyed by class rather than compared against
`Enum` declaration order (`SUPERSEDED`, `RETIRED`, and `QUARANTINED` are
declared *after* `CANONICAL_POLICY` yet must not load).

Fail-closed here means "this optional memory item does not enter the default
load set", never "the plan fails": canonical task context (`authority`,
`required`, `boundaries`, `dependencies`, `unresolved`) is entirely outside
this gate, and a malformed lesson or Skill record must never suppress it.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from runtime.trust import MemoryTrustClass


class MemoryAdmission(str, Enum):
    """The three outcomes the gate can return."""

    LOAD = "LOAD"
    WITHHOLD = "WITHHOLD"
    DENY = "DENY"


class MemoryTrustGateError(ValueError):
    """Raised when the gate is called with an unusable admission default."""


# Derived directly from PR #148's class/action table. No new vocabulary, no
# new semantics, and deliberately an explicit dict rather than a threshold
# comparison over `MemoryTrustClass` declaration order.
#
# `ACTIVE_INSTRUCTION` and `CANONICAL_POLICY` are effectively unreachable at
# this seam today: `_select_skills()` projects a Skill's lifecycle state via
# `skill_lifecycle_trust_class()`, but every entry's `lifecycle_state` is
# `None` (mapped to `OBSERVATION`) until a durable store is wired into
# `build_skill_catalog()`, and no memory-like producer emits
# `CANONICAL_POLICY` at all. #148 conditions
# `ACTIVE_INSTRUCTION`'s load on "a separate Skill loader task proves the
# source active"; that condition is carried forward as
# `_LOAD_REQUIRES_PROVEN_ACTIVE_SOURCE` below rather than silently widened.
_ADMISSION_TABLE: dict[MemoryTrustClass, MemoryAdmission] = {
    MemoryTrustClass.CANONICAL_POLICY: MemoryAdmission.LOAD,
    MemoryTrustClass.ACTIVE_INSTRUCTION: MemoryAdmission.LOAD,
    MemoryTrustClass.APPROVED_SKILL: MemoryAdmission.LOAD,
    MemoryTrustClass.REVIEWED_GUIDANCE: MemoryAdmission.LOAD,
    MemoryTrustClass.CANDIDATE_LESSON: MemoryAdmission.WITHHOLD,
    MemoryTrustClass.CLAIM: MemoryAdmission.WITHHOLD,
    MemoryTrustClass.OBSERVATION: MemoryAdmission.WITHHOLD,
    MemoryTrustClass.SUPERSEDED: MemoryAdmission.WITHHOLD,
    MemoryTrustClass.RETIRED: MemoryAdmission.WITHHOLD,
    MemoryTrustClass.UNTRUSTED_INPUT: MemoryAdmission.DENY,
    MemoryTrustClass.QUARANTINED: MemoryAdmission.DENY,
}

# #148 admits `ACTIVE_INSTRUCTION` only "if a separate Skill loader task
# proves the source active". No such prover exists, and no producer at this
# seam emits the class, so the row stays unreachable: reaching it without a
# prover withholds rather than loads.
_LOAD_REQUIRES_PROVEN_ACTIVE_SOURCE = frozenset({MemoryTrustClass.ACTIVE_INSTRUCTION})

ADMISSION_CODE_ADMITTED = "TRUST_CLASS_ADMITTED"
ADMISSION_CODE_NOT_DEFAULT_LOADABLE = "TRUST_CLASS_NOT_DEFAULT_LOADABLE"
ADMISSION_CODE_DENIED = "TRUST_CLASS_DENIED"
ADMISSION_CODE_STALE = "TRUST_METADATA_STALE"
ADMISSION_CODE_UNRESOLVED = "TRUST_CLASS_UNRESOLVED"
ADMISSION_CODE_ACTIVE_SOURCE_UNPROVEN = "TRUST_CLASS_ACTIVE_SOURCE_UNPROVEN"


@dataclass(frozen=True)
class MemoryAdmissionDecision:
    """One admission outcome plus the fixed code explaining it.

    Mirrors the `HookOutcome` + `guard_code` shape used by the SEC3 guard in
    `runtime/policy/destructive_action_guard.py`: a directive and a stable
    machine-readable reason, no free-form policy payload. (Named by path, not
    by class: that module's own tests assert its guard class name appears in
    no other `runtime/` source, since it must stay unwired.)
    """

    admission: MemoryAdmission
    code: str
    trust_class: MemoryTrustClass | None


def admit_memory_evidence(
    trust_class: object,
    *,
    stale: object,
    unknown_admission: MemoryAdmission,
) -> MemoryAdmissionDecision:
    """Decide whether one memory-like item may enter the default load set.

    Pure and deterministic. Arguments:

    * `trust_class` — a `MemoryTrustClass`, or its raw `str` value as stamped
      onto plan items. Anything else (``None``, an empty/blank string, an
      unrecognized name, a non-string object) is the *unknown* case.
    * `stale` — today's `stale_trust_metadata` flag. A true value demotes
      `LOAD` to `WITHHOLD`; it never promotes. A non-``bool`` value is itself
      unusable metadata and is treated as stale (fail-closed), never ignored.
    * `unknown_admission` — what the *calling producer* does with the unknown
      case. This is per-producer by design and settled in §2e of the note by
      whether that producer's withheld form carries content: lessons carry
      only `{lesson_id, reason}` so they `WITHHOLD`; Skill entries carry
      `name`/`description` text inline so they `DENY`. `LOAD` is rejected
      outright — missing or malformed trust metadata must never mean
      "trusted".
    """

    if not isinstance(unknown_admission, MemoryAdmission):
        raise MemoryTrustGateError(
            f"unknown_admission must be a MemoryAdmission: {unknown_admission!r}"
        )
    if unknown_admission is MemoryAdmission.LOAD:
        raise MemoryTrustGateError(
            "unknown_admission must never be LOAD: unresolved trust metadata "
            "cannot mean trusted"
        )

    resolved = _resolve(trust_class)
    if resolved is None:
        return MemoryAdmissionDecision(unknown_admission, ADMISSION_CODE_UNRESOLVED, None)

    admission = _ADMISSION_TABLE[resolved]

    if admission is MemoryAdmission.LOAD and resolved in _LOAD_REQUIRES_PROVEN_ACTIVE_SOURCE:
        return MemoryAdmissionDecision(
            MemoryAdmission.WITHHOLD, ADMISSION_CODE_ACTIVE_SOURCE_UNPROVEN, resolved
        )

    if admission is MemoryAdmission.LOAD and stale is not False:
        return MemoryAdmissionDecision(
            MemoryAdmission.WITHHOLD, ADMISSION_CODE_STALE, resolved
        )

    if admission is MemoryAdmission.LOAD:
        return MemoryAdmissionDecision(admission, ADMISSION_CODE_ADMITTED, resolved)
    if admission is MemoryAdmission.WITHHOLD:
        return MemoryAdmissionDecision(
            admission, ADMISSION_CODE_NOT_DEFAULT_LOADABLE, resolved
        )
    return MemoryAdmissionDecision(admission, ADMISSION_CODE_DENIED, resolved)


def _resolve(trust_class: object) -> MemoryTrustClass | None:
    """Coerce a stamped trust class to an enum member, or `None` if unusable."""

    if isinstance(trust_class, MemoryTrustClass):
        return trust_class
    if isinstance(trust_class, str) and trust_class.strip():
        try:
            return MemoryTrustClass(trust_class.strip())
        except ValueError:
            return None
    return None
