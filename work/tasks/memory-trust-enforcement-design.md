# Task: Memory trust enforcement design

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `ARCHITECTURE`
- Owner: `/root`
- Risk: `MEDIUM`
- Goal: choose the first bounded enforcement seam for roadmap 6.22, define what
  each `MemoryTrustClass` may influence, define stale/malformed trust-metadata
  handling, and leave an implementation-ready follow-up that prevents
  remembered content from becoming authority by repetition.

## Inputs and source of truth

- Inputs:
  - `work/roadmaps/CAPABILITY_CHECKLIST.md` row `6.22`.
  - `runtime/trust.py` and `tests/test_trust.py`.
  - `work/tasks/memory-trust-class-vocabulary-wave19.md`.
  - `runtime/context_builder.py`, especially `_lesson_guidance()` and
    `_select_skills()`.
  - `runtime/skills/catalog.py`, `runtime/skills/lifecycle.py`,
    `runtime/operational_learning.py`.
- Authoritative sources: current runtime code wins over stale roadmap prose.
- Evidence labels:
  - VERIFIED: `MemoryTrustClass` exists as a read-only vocabulary/mapping layer.
  - VERIFIED: Context Builder surfaces operational lessons as `GUIDANCE_ONLY`
    and does not load Skill bodies.
  - VERIFIED: no decision-gating code path currently consults
    `MemoryTrustClass`.
  - UNKNOWN: durable Skill lifecycle state and operator authority wiring; not
    decided by this task.
- Dependencies / preconditions: none for this docs/design task.

## Change boundary

- MAY CHANGE:
  - `work/notes/2026-08-21-memory-trust-enforcement-design.md`
  - this task file
  - `work/roadmaps/CAPABILITY_CHECKLIST.md` row `6.22` evidence text only
- MUST NOT CHANGE:
  - `runtime/*.py`
  - `tests/*.py`
  - Skill lifecycle persistence, operator approval behavior, or any production
    gating behavior
- MAY CHANGE IF NECESSARY: none.
- OPERATOR APPROVAL REQUIRED: none for the design; future operator-authority
  wiring requires its own task boundary.

## Decision authority

- Owner may decide:
  - the first implementation seam if it is bounded to current code and does not
    grant new authority;
  - a trust-class action table for the existing 11-class vocabulary;
  - fail-closed rules for missing/malformed trust metadata at that seam.
- Owner must escalate:
  - changing which subsystem owns canonical authority;
  - making remembered guidance, unassessed Skills, or candidate lessons
    authoritative;
  - adding persistence/migrations or operator-approval workflows;
  - loading Skill bodies into context.

## Acceptance criteria

- [x] Design note states why 6.22 is not implementation-ready as a broad
      enforcement task.
- [x] Design note selects exactly one first enforcement seam.
- [x] Design note gives a class/action table for all 11 `MemoryTrustClass`
      members.
- [x] Design note states canonical authority boundaries and what remains
      outside the selected seam.
- [x] Design note defines fail-closed behavior for missing, malformed, stale, or
      unknown trust metadata at the selected seam, including `EXPIRED` /
      `REVIEW_DUE` operational lessons and future stale Skill lifecycle or
      provenance evidence.
- [x] Design note leaves a bounded implementation follow-up with concrete
      acceptance criteria.
- [x] No runtime or test file is changed.

## Verification and evidence

- Verification:
  - `git diff --check`
  - direct read of changed docs
- Evidence to preserve: committed design note and task file.
- Review required: `INDEPENDENT_REVIEW`.

## Conditional execution rules

- Environment / target: local repository docs only.
- Ordered procedure: inspect current code, write design, verify diff.
- Failure branches: if code already contains trust-class gating, update the
  design to reflect it rather than claiming absence.
- Rollback / recovery: revert this docs-only commit.
- Security / privacy controls: do not introduce new authority from remembered
  content.
- External side effects: GitHub PR publication/merge only after review.
- Effort limit: no code implementation in this task.
- Approved reference: `runtime/trust.py` is the current vocabulary reference.

## Stop / escalate

Stop rather than guess if:

- the chosen seam would load Skill bodies or make guidance authoritative;
- the implementation would need durable lifecycle storage or migrations;
- a future worker cannot verify the behavior without inventing acceptance
  criteria.

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

- This task deliberately chooses a narrow first seam: annotate and validate
  Context Builder memory-like evidence by trust class, without changing what
  content is loaded or treated as authority.

## Completion / handoff

- Completed: design note and implementation-ready follow-up.
- Not completed: implementation of the selected seam.
- Current blocker: independent review.
- Next action if not DONE: review this docs-only architecture task.
