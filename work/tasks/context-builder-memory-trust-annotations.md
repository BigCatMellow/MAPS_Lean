# Task: Context Builder memory trust annotations

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `/root`
- Risk: `MEDIUM`
- Goal: wire `MemoryTrustClass` into Context Builder's existing memory-like
  evidence (`guidance`, `withheld_guidance`, and `skills`) without loading new
  content or granting authority.

## Inputs and source of truth

- Inputs:
  - `work/notes/2026-08-21-memory-trust-enforcement-design.md`.
  - `runtime/context_builder.py`.
  - `runtime/trust.py`.
  - `runtime/operational_learning.py`.
  - `runtime/skills/catalog.py`.
  - `tests/test_context_builder.py`, `tests/test_trust.py`.
- Authoritative sources: current runtime code and the 2026-08-21 design note.
- Evidence labels:
  - VERIFIED: operational lessons are projected as `GUIDANCE_ONLY`.
  - VERIFIED: Skill selection exposes descriptor/provenance metadata only and
    does not load Skill bodies.
  - VERIFIED: `MemoryTrustClass` mappings are pure/read-only.
- Dependencies / preconditions: PR #148's design note is merged.

## Change boundary

- MAY CHANGE:
  - `runtime/context_builder.py`
  - `tests/test_context_builder.py`
  - `work/roadmaps/CAPABILITY_CHECKLIST.md` row `6.22` evidence text only
  - this task file
- MUST NOT CHANGE:
  - Skill body loading behavior
  - task authority, policy, routing, or tool-call authorization
  - operational-learning storage/promotion/retirement semantics
  - Skill lifecycle persistence or operator approval workflows
- MAY CHANGE IF NECESSARY: none.
- OPERATOR APPROVAL REQUIRED: none for this bounded metadata implementation.

## Decision authority

- Owner may decide:
  - exact field names for trust annotations if they are explicit and tested;
  - fail-closed handling for optional memory-like evidence mapping failures;
  - coverage metadata wording.
- Owner must escalate:
  - loading Skill bodies;
  - treating operational lessons or Skill metadata as authority;
  - adding persistence/migrations or new approval workflows;
  - changing action/tool-call gates.

## Acceptance criteria

- [x] Active operational-learning guidance remains `GUIDANCE_ONLY` and carries
      `trust_class: REVIEWED_GUIDANCE`.
- [x] Withheld operational-learning guidance carries trust metadata while
      remaining withheld.
- [x] `EXPIRED` and `REVIEW_DUE` operational lessons stay in
      `withheld_guidance` with stale metadata marked.
- [x] Matched unassessed Skills carry `trust_class: OBSERVATION` and Skill
      bodies are still not loaded.
- [x] Malformed optional memory-like evidence fails closed without suppressing
      canonical authority or required task context.
- [x] Context Builder coverage reports whether memory-like evidence carries
      trust-class metadata.
- [x] 6.22 remains `IN PROGRESS`; this is metadata/invariant wiring, not full
      security enforcement.

## Verification and evidence

- Verification:
  - `git diff --check`
  - `python3 -m unittest tests.test_context_builder tests.test_trust -v`
- Evidence to preserve: test output and review evidence.
- Review required: `INDEPENDENT_REVIEW`.

## Conditional execution rules

- Environment / target: Python unittest in local repo.
- Ordered procedure: implement metadata only, run focused tests, request review.
- Failure branches: if adding trust metadata would require changing authority
  or loading behavior, stop and reshape.
- Rollback / recovery: revert commit/PR.
- Security / privacy controls: no new content is loaded; malformed optional
  memory evidence must fail closed.
- External side effects: GitHub PR publication/merge only after review.
- Effort limit: no broader 6.22 enforcement in this task.
- Approved reference:
  `work/notes/2026-08-21-memory-trust-enforcement-design.md`.

## Stop / escalate

Stop rather than guess if:

- a trust class cannot be derived without inventing a new subsystem authority;
- tests require changing operational-learning or Skill lifecycle semantics;
- the implementation would make remembered content authoritative.

Escalate to: operator or a new architecture task.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- `trust_class` is metadata on evidence. It is not authority.
- `memory_trust_classification_present` is a coverage signal for memory-like
  evidence in the context plan.

## Completion / handoff

- Completed: implementation and focused tests.
- Not completed: action/tool-call gating, Skill body loading, persistence, or
  unified subsystem migration.
- Current blocker: independent review.
- Next action if not DONE: review this implementation.
