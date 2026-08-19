# Task: Memory trust class vocabulary (roadmap 6.22, MVP)

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `agent/memory-trust-class-vocabulary-wave19`
- Risk: `LOW`
- Goal: define the full 11-member `MemoryTrustClass` vocabulary that
  `work/roadmaps/00-MASTER-MAPS-CAPABILITY-ROADMAP.md` section "6.22 Memory
  trust classes" names as candidates, and add read-only cross-subsystem
  correspondence mappings from the existing, unrelated per-subsystem trust
  vocabularies onto it. `work/roadmaps/CAPABILITY_CHECKLIST.md`'s 6.22 row
  marks this `IN PROGRESS`, citing exactly this gap: a partial trust
  vocabulary exists (`SkillTrustState.UNASSESSED`,
  `operational_learning.py`'s `CANDIDATE`/`ACTIVE`/`RETIRED` and
  `GUIDANCE_ONLY` label) but not the full roadmap class list, and no unified
  cross-subsystem enum.

## Inputs and source of truth

- `work/roadmaps/00-MASTER-MAPS-CAPABILITY-ROADMAP.md` (lines ~1081-1111,
  section "6.22 Memory trust classes") -- the exact 11-member candidate
  vocabulary and its stated purpose ("Prevent 'remembered' content from
  becoming authority by repetition"). Not modified by this task.
- `runtime/skills/catalog.py` (`SkillTrustState`; unmodified, imported
  read-only) -- one member, `UNASSESSED`.
- `runtime/skills/lifecycle.py` (`SkillLifecycleState`; unmodified, imported
  read-only; merged via PR #113) -- seven members already overlapping
  heavily with the roadmap vocabulary (`QUARANTINED`, `SUPERSEDED`,
  `RETIRED` exact matches; `ACTIVE`/`APPROVED` conceptually close to
  `ACTIVE_INSTRUCTION`/`APPROVED_SKILL`). The strongest existing precedent
  for this vocabulary's shape.
- `runtime/operational_learning.py` (`_STATUSES`; unmodified, not imported --
  it is raw strings, not an importable enum) -- `CANDIDATE`, `ACTIVE`,
  `RETIRED`.
- `runtime/context_builder.py`'s `_lesson_guidance` (unmodified, not
  imported) -- the `GUIDANCE_ONLY` authority label attached to
  operator-promoted `ACTIVE` operational lessons; read only as evidence for
  the `ACTIVE` -> `MemoryTrustClass` mapping decision below.
- `playbook/INFORMATION_CLASSES.md` (merged via PR #111; unmodified) --
  prior-session precedent for naming a cross-cutting vocabulary as a durable
  reference, though docs-only; this task's vocabulary is real code because
  trust class is meant to eventually gate real behavior decisions.

## Change boundary

MAY CHANGE / ADD:
- `runtime/trust.py` (new module)
- `tests/test_trust.py` (new)
- `work/roadmaps/CAPABILITY_CHECKLIST.md` (6.22 row evidence text only)
- this task doc

MUST NOT CHANGE:
- `runtime/skills/catalog.py`'s `SkillTrustState` or any of its behavior --
  unmodified, only imported/read from.
- `runtime/skills/lifecycle.py`'s `SkillLifecycleState` or transition
  logic -- unmodified, only imported/read from.
- `runtime/operational_learning.py`'s `_STATUSES` or status-handling
  behavior -- unmodified, not imported from (raw strings only).
- `runtime/context_builder.py` -- unmodified, not imported from.
- No decision-gating code path anywhere is wired to `MemoryTrustClass` in
  this task.

## Required semantics

1. `MemoryTrustClass(str, Enum)` in `runtime/trust.py` has exactly the 11
   members the roadmap names, in roadmap order: `UNTRUSTED_INPUT`,
   `OBSERVATION`, `CLAIM`, `CANDIDATE_LESSON`, `REVIEWED_GUIDANCE`,
   `APPROVED_SKILL`, `ACTIVE_INSTRUCTION`, `CANONICAL_POLICY`, `SUPERSEDED`,
   `RETIRED`, `QUARANTINED`.
2. `skill_trust_class(state: SkillTrustState) -> MemoryTrustClass` maps the
   one real member, `UNASSESSED`, to `OBSERVATION` (an unassessed catalog
   entry is an observed fact, not yet a claim or reviewed guidance).
3. `skill_lifecycle_trust_class(state: SkillLifecycleState) -> MemoryTrustClass`
   covers all 7 `SkillLifecycleState` members:
   `DISCOVERED` -> `OBSERVATION`, `VALIDATED` -> `REVIEWED_GUIDANCE`,
   `QUARANTINED` -> `QUARANTINED`, `APPROVED` -> `APPROVED_SKILL`,
   `ACTIVE` -> `ACTIVE_INSTRUCTION`, `SUPERSEDED` -> `SUPERSEDED`,
   `RETIRED` -> `RETIRED`. See the module docstring for the reasoning behind
   `VALIDATED` -> `REVIEWED_GUIDANCE` (real automated gate-review evidence,
   not a bare `CLAIM`, but not yet operator-approved).
4. `operational_learning_trust_class(status: str) -> MemoryTrustClass`
   covers the 3 real status strings: `CANDIDATE` -> `CANDIDATE_LESSON`,
   `ACTIVE` -> `REVIEWED_GUIDANCE`, `RETIRED` -> `RETIRED`. See the module
   docstring for the reasoning behind `ACTIVE` -> `REVIEWED_GUIDANCE` rather
   than `ACTIVE_INSTRUCTION` (an ACTIVE operational lesson is surfaced under
   the `GUIDANCE_ONLY` label verbatim, never merged into
   instructions/boundaries -- `REVIEWED_GUIDANCE` is the more honest
   mapping). Raises `TrustClassError` (a `ValueError` subclass) for any
   unrecognized input string, since this mapping takes a raw string rather
   than an enum-typed value.
5. All three mapping functions are pure, read-only lookups: they persist
   nothing, change no subsystem's real behavior, and grant no authority.
   This is stated explicitly in the module docstring, matching the pattern
   in `runtime/skills/lifecycle.py`'s own docstring ("This module owns NO
   persistence, NO task/session authority...").

## Acceptance criteria

- [x] `MemoryTrustClass` has exactly the 11 specified members, verified by
      set-equality against the roadmap's own list (so the test fails if the
      roadmap-derived vocabulary is silently changed).
- [x] `skill_trust_class` covers every `SkillTrustState` member (exhaustive
      loop) and returns a `MemoryTrustClass` instance, not a string/`None`.
- [x] `skill_lifecycle_trust_class` covers every `SkillLifecycleState`
      member (exhaustive loop over all 7) and returns a `MemoryTrustClass`
      instance.
- [x] `operational_learning_trust_class` covers all 3 real status strings
      (exhaustive) and returns a `MemoryTrustClass` instance; raises
      `TrustClassError` for `"BOGUS"` and for non-string input.
- [x] `python3 -m unittest tests.test_trust -v` and the full suite
      (`python3 -m unittest discover -s tests -v`) pass.
- [ ] Independent review remains required before completion.

## Verification

```text
python3 -m unittest tests.test_trust -v
python3 -m unittest discover -s tests -v
```

Review required: `INDEPENDENT_REVIEW`. Self-authored; owner is not eligible
to supply that review (`work/reviews/pr-<N>-review-evidence.md` required
before merge per `scripts/check_review_evidence.py`).

## Stop / escalate

This task defines the vocabulary and cross-subsystem correspondence only.
It deliberately does NOT:

- Change `SkillTrustState`, `SkillLifecycleState`, or
  `operational_learning.py`'s real enums/status handling in any way. Those
  subsystems keep their own vocabularies and behavior exactly as they are;
  this module only adds a read-only view onto them.
- Wire `MemoryTrustClass` into any decision-gating code path (e.g. nothing
  in `context_builder.py`, `operational_learning.py`, or the Skill catalog
  actually consults this module to decide what content may influence a tool
  call or an instruction). Doing so is a separate, larger authority-design
  task -- exactly as SEC4 (`runtime/skills/lifecycle.py`) left persistence
  and real operator-authority wiring out of its own scope, and L6 left
  schema persistence out of scope for its identity/logic primitive.
- Force any existing subsystem to migrate onto `MemoryTrustClass` as its
  primary vocabulary. `SkillTrustState`/`SkillLifecycleState`/
  `operational_learning.py` remain the systems of record for their own
  domains; `MemoryTrustClass` is a cross-cutting correspondence layer, not a
  replacement.
- Claim 6.22 is `DONE` on the roadmap checklist. It remains `IN PROGRESS`:
  the full vocabulary and real cross-subsystem correspondence mappings now
  exist, but nothing actually gates real authority decisions on trust class
  yet -- that remains future work.
