# Task: Skill trust-lifecycle transition primitive (SEC4, partial)

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `agent/skill-trust-lifecycle-wave11`
- Risk: `LOW`
- Goal: build the pure, tested quarantine-lifecycle state-machine primitive
  that `work/roadmaps/agent-harness-capabilities/04-agentic-security.md`
  phase **SEC4** calls for ("Quarantine, provenance, capability declaration,
  behavioral tests. Exit gate: unreviewed executable Skill/tool content
  cannot become active silently"). `work/roadmaps/CAPABILITY_CHECKLIST.md`
  marks SEC4 `IN PROGRESS`, citing exactly this gap: static content linting
  (`runtime/skills/gate.py`) and provenance/trust metadata
  (`runtime/skills/catalog.py`) exist, but "there is no quarantine
  *lifecycle* state machine (discovered→validated→quarantined→approved→
  active→superseded→retired)".

## Inputs and source of truth

- `runtime/skills/gate.py` (`assess_skill`, `SkillGateReport`,
  `SkillGateDisposition`; unmodified) -- the per-assessment classification
  (`CLEAR` / `REVIEW_REQUIRED` / `QUARANTINE`) this task reads, once, in
  `initial_transition_from_gate_report`. This task does not touch scanning
  logic.
- `runtime/skills/catalog.py` (`SkillTrustState`; unmodified) -- currently
  exactly one member, `UNASSESSED`, with a comment predicting "a future
  reviewed trust lifecycle may add states." This task builds that lifecycle
  as a standalone module; it deliberately does **not** wire it into
  `SkillCatalog`/`SkillTrustState` or `SkillCatalogEntry.provenance` -- doing
  so implies a persistence decision (where does a given Skill's current
  lifecycle state live durably, across process restarts?) that is out of
  scope here.
- `runtime/state/operational_learning_storage.py` / `operational_learning.py`
  (read-only reference, unmodified, not imported) -- a different subsystem's
  candidate/promote/retire lifecycle, useful only as precedent for "state
  transitions are validated pure logic; persistence/authority is a separate
  concern." Not the same state machine.
- `runtime/harness/hooks.py` (`HookDirective`/`HookOutcome`; read-only
  reference) -- the "pure logic, no storage" shape this module mirrors.

## Change boundary

MAY CHANGE / ADD:
- `runtime/skills/lifecycle.py` (new module)
- `runtime/skills/__init__.py` (additive export only: `SkillLifecycleState`,
  `SkillLifecycleError`, `transition`, `initial_transition_from_gate_report`)
- `tests/test_skill_lifecycle.py` (new)
- this task doc

MUST NOT CHANGE:
- `runtime/state/schema.sql` -- no new canonical persistence. This task is
  the transition-validation primitive only; actually recording a Skill's
  current lifecycle state durably is separate, larger, schema-risk work.
- `runtime/skills/gate.py` scanning logic, `runtime/skills/catalog.py`
  `SkillCatalog`/discovery code -- unmodified, only imported/read from.
- `runtime/context_builder.py` -- a different concurrent PR is actively
  editing this file; not touched, not imported from.

## Required semantics

1. `SkillLifecycleState(str, Enum)` has exactly 7 members: `DISCOVERED`,
   `VALIDATED`, `QUARANTINED`, `APPROVED`, `ACTIVE`, `SUPERSEDED`, `RETIRED`.
2. `DISCOVERED` is the only legal starting state (no edges point into it).
3. `DISCOVERED` routes forward only via gate-assessment result: `VALIDATED`
   on `CLEAR`/`REVIEW_REQUIRED`, `QUARANTINED` on `QUARANTINE`. There is no
   `DISCOVERED -> APPROVED` or `DISCOVERED -> ACTIVE` edge -- quarantine
   review can never be skipped.
4. `VALIDATED -> APPROVED` and `QUARANTINED -> APPROVED` both require an
   explicit, non-empty `actor` (operator identity); `transition()` raises
   `SkillLifecycleError` if `actor` is `None` or blank on these two edges.
   This is a structural reminder that approval is never implicit -- it
   performs no real authority/identity check, since no persistence layer
   exists yet to check against.
5. `APPROVED -> ACTIVE` requires no additional actor (the operator decision
   already happened to reach `APPROVED`; `ACTIVE` is a deployment fact, not
   a second trust decision).
6. `QUARANTINED -> RETIRED` (operator rejects instead of approving) needs no
   actor either, by the same reasoning as (5) -- it is documented in the
   module docstring, not independently justified per-edge in code.
7. `ACTIVE -> SUPERSEDED` and `ACTIVE -> RETIRED` are legal; `SUPERSEDED` and
   `RETIRED` are terminal (zero outgoing edges from either).
8. `transition(current, target, *, actor=None)` raises `SkillLifecycleError`
   (a `ValueError` subclass) for any `(current, target)` pair not in the
   allowed graph, in addition to the actor checks in (4).
9. `initial_transition_from_gate_report(report: SkillGateReport)` is a thin
   mapping over a real `SkillGateReport` imported from `runtime/skills/gate.py`
   -- no new scanning, no re-derivation of `disposition` from `findings`.

This module owns no persistence, no task/session authority, and no canonical
storage: it is pure validated state-transition logic over an in-memory enum.

## Acceptance criteria

- [x] `SkillLifecycleState` has exactly the 7 specified members.
- [x] `DISCOVERED -> VALIDATED`, `DISCOVERED -> QUARANTINED`,
      `VALIDATED -> APPROVED` (actor required), `QUARANTINED -> APPROVED`
      (actor required), `QUARANTINED -> RETIRED`, `APPROVED -> ACTIVE`,
      `ACTIVE -> SUPERSEDED`, `ACTIVE -> RETIRED` all succeed via
      `transition()`.
- [x] Every other `(source, target)` pair raises `SkillLifecycleError`,
      including explicitly `DISCOVERED -> APPROVED` and
      `DISCOVERED -> ACTIVE` (quarantine-skip attempts).
- [x] `VALIDATED -> APPROVED` and `QUARANTINED -> APPROVED` reject
      `actor=None`, `actor=""`, and whitespace-only `actor`.
- [x] `SUPERSEDED` and `RETIRED` have zero outgoing transitions, tested
      exhaustively against all 7 states as target.
- [x] `initial_transition_from_gate_report` correctly maps real `CLEAR`,
      `REVIEW_REQUIRED`, and `QUARANTINE` `SkillGateReport` instances
      (constructed via `discover_skills`/`assess_skill`, not stubbed) to
      `VALIDATED`, `VALIDATED`, and `QUARANTINED` respectively.
- [x] `python3 -m unittest tests.test_skill_lifecycle
      tests.test_skills_quality_gate tests.test_skills_quality_gate_metadata
      tests.test_skills_catalog -v` and the full suite pass.
- [ ] Independent review remains required before completion.

## Verification

```text
python3 -m unittest tests.test_skill_lifecycle tests.test_skills_quality_gate tests.test_skills_quality_gate_metadata tests.test_skills_catalog -v
python3 -m unittest discover -s tests -v
```

Review required: `INDEPENDENT_REVIEW`. Self-authored; owner is not eligible
to supply that review (`work/reviews/pr-<N>-review-evidence.md` required
before merge per `scripts/check_review_evidence.py`).

## Stop / escalate

Persistence is explicitly out of scope and left for a future task, exactly
as L6 left schema persistence out of scope for its identity/logic primitive:

- Actually storing a Skill's current lifecycle state durably (which table,
  how it's keyed against `SkillCatalogEntry.catalog_key` or
  `content_sha256`, how it survives catalog rebuilds/content changes) is a
  real schema design decision, not a mechanical addition to
  `runtime/state/schema.sql`.
- Wiring operator approval through a real authority path (who is allowed to
  supply `actor`, how that identity is verified, how the approval event
  itself is persisted/audited) is a separate authority-design task, parallel
  to how `work/tasks/operational-learning-authority-design-wave4.md` and
  `recovery-equivalence-authority-design-wave4.md` were split out from their
  respective storage tasks.
- SEC4 remains only *partially* complete after this task -- the
  "capability-declaration manifest for third-party Skills/tools" half of
  SEC4's stated scope is untouched and still `NOT STARTED`.
  `work/roadmaps/CAPABILITY_CHECKLIST.md` is left unchanged by this task;
  updating it to reflect this partial progress is left to a fast-follow
  docs-only PR, consistent with how PR #105 handled H5.
