# Memory trust enforcement design — first bounded seam

Date: 2026-08-21
Owner: `/root`
Status: design complete; no runtime behavior changed

## Finding

Roadmap 6.22 is correctly still `IN PROGRESS`.

VERIFIED current state:

- `runtime/trust.py` defines the 11-member `MemoryTrustClass` vocabulary and
  read-only mappings from Skill trust, Skill lifecycle, and operational-learning
  status values.
- `runtime/context_builder.py::_lesson_guidance()` projects operator-promoted
  operational lessons as `GUIDANCE_ONLY` and explicitly does not merge them into
  instructions or boundaries.
- `runtime/context_builder.py::_select_skills()` emits matched Skill descriptor
  metadata only. It does not call `load_skill()` or load Skill bodies.
- No runtime decision-gating path currently consults `MemoryTrustClass`.

The broad enforcement task is not implementation-ready because the missing
choices are material: canonical trust authority, per-class influence rules,
first enforcement seam, persistence/lineage, and malformed metadata behavior.

## Decision: first seam is Context Builder evidence annotation and validation

The first implementation should wire `MemoryTrustClass` into
`runtime/context_builder.py` as metadata on memory-like evidence that Context
Builder already emits:

- operational-learning `guidance` / `withheld_guidance`;
- Skill selection metadata under `skills`.

This seam is intentionally narrow:

- It does not load Skill bodies.
- It does not promote guidance into authority, instructions, or boundaries.
- It does not replace `SkillTrustState`, `SkillLifecycleState`, or
  operational-learning statuses as systems of record.
- It creates a mechanically testable invariant that downstream consumers can
  inspect before any future stronger gate exists.

This is the smallest useful step because Context Builder is already the place
where remembered lessons and Skill metadata become visible to a worker. Adding
trust-class metadata there reduces ambiguity without changing execution
authority.

## Class/action table for the first seam

| `MemoryTrustClass` | May appear in Context Builder as | Must not influence |
|---|---|---|
| `UNTRUSTED_INPUT` | omitted or withheld evidence only | authority, required context, task boundaries, tool calls |
| `OBSERVATION` | attributed metadata/evidence | authority, required context, loaded instructions |
| `CLAIM` | attributed claim evidence only | authority, required context, loaded instructions |
| `CANDIDATE_LESSON` | withheld guidance | authority, required context, loaded instructions |
| `REVIEWED_GUIDANCE` | `guidance` with `GUIDANCE_ONLY` authority | authority, boundaries, policy, task status |
| `APPROVED_SKILL` | Skill metadata eligible for future loading | automatic body loading or authority |
| `ACTIVE_INSTRUCTION` | active Skill/instruction metadata only if a separate Skill loader task proves the source active | task authority unless already present in canonical authority files |
| `CANONICAL_POLICY` | only canonical policy/authority sources such as `AGENTS.md` or explicit task contract fields | replacement by memory, lesson, or Skill metadata |
| `SUPERSEDED` | omitted or withheld with reason | current guidance/authority |
| `RETIRED` | omitted or withheld with reason | current guidance/authority |
| `QUARANTINED` | omitted or withheld with reason | loaded instructions, tool calls, authority |

## Canonical authority boundary

For this seam:

- `AGENTS.md`, explicit task contracts, policy records, and current task state
  remain canonical authority.
- `MemoryTrustClass` is a classification on evidence, not authority itself.
- Operational lessons remain `GUIDANCE_ONLY`.
- Skill catalog matches remain descriptor/provenance evidence until a separate
  Skill-loading task supplies lifecycle authority and loading rules.

## Fail-closed rules

The first implementation must fail closed as follows:

- Missing trust class on memory-like evidence: mark item withheld, or omit it if
  no safe withheld bucket exists.
- Unknown trust class string: withheld with reason `unknown_trust_class`.
- Malformed trust metadata type: withheld with reason `malformed_trust_class`.
- Mapping failure from subsystem status: withheld with reason
  `trust_mapping_failed`.
- Stale operational-learning metadata: preserve the existing
  `project_applicable_lessons()` behavior. Lessons withheld as `EXPIRED` or
  `REVIEW_DUE` are stale for this seam and must stay in `withheld_guidance`;
  they must not be promoted to active `guidance` merely because they also map
  to a non-terminal trust class.
- Stale Skill metadata: until durable Skill lifecycle state exists, an
  unassessed catalog entry is only `OBSERVATION`. If a future Skill source
  supplies lifecycle/provenance timestamps or state and that evidence is
  expired, superseded, retired, quarantined, or otherwise review-due, the item
  must be omitted or withheld with reason `stale_trust_metadata`; it must not
  be treated as loadable or authoritative.
- Candidate, quarantined, retired, or superseded content must not appear in
  active `guidance` or loaded Skill output.

Fail-closed here means "do not surface as active guidance/skills." It does not
mean failing the whole context plan, because Context Builder must still produce
canonical authority and required task context when optional memory evidence is
bad.

## Bounded follow-up implementation

Recommended next task: `Context Builder memory trust annotations`.

Allowed implementation scope:

- Add `trust_class` to operational-learning `guidance` and
  `withheld_guidance` items using
  `operational_learning_trust_class(status)`.
- Add `trust_class` to Skill selection metadata using
  `skill_trust_class(entry.provenance.trust_state)`.
- If a mapping raises `TrustClassError`, withhold or omit that optional item
  according to the fail-closed rules above.
- Add tests proving:
  - ACTIVE operational lessons remain `GUIDANCE_ONLY` and carry
    `REVIEWED_GUIDANCE`;
  - candidate/retired/superseded/quarantined memory-like evidence cannot become
    active guidance;
  - matched unassessed Skills carry `OBSERVATION` and are still not loaded;
  - malformed/unknown trust metadata does not break required authority context;
  - `coverage` reports trust classification presence for memory-like evidence.
- Keep 6.22 `IN PROGRESS`; this is observability/invariant wiring, not full
  security enforcement.

Must not do in that follow-up:

- Load Skill bodies.
- Make operational lessons authority.
- Add persistence, migrations, or operator-approval workflows.
- Change task-state policy, routing, or tool-call authorization.

## Roadmap impact

This design does not complete 6.22. It narrows the next implementation step to
a verifiable invariant at the first place where memory-like evidence enters the
worker context. Full 6.22 completion still requires later enforcement at action
or instruction-loading boundaries.
