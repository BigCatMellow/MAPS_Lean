# Task: Deterministic review-start flow

- Status: `ACTIVE`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `/root`
- Risk: `MEDIUM`
- Goal: add a bounded `maps flow review-start` lifecycle flow that claims
  review work and, when provided, binds the immutable review subject before any
  reviewer verdict is recorded.

## Inputs and source of truth

- Inputs:
  - `work/roadmaps/CAPABILITY_CHECKLIST.md` row `6.21`
  - `work/roadmaps/prime-agent-capability-roadmap.md` section `12`
  - `runtime/flow_start.py`
  - `runtime/cli.py`
  - `runtime/state/review.py`
  - `runtime/state/review_binding.py`
  - `tests/test_flow_start.py`
  - `tests/test_review_subject_binding.py`
- Authoritative sources: existing task/review/review-subject state methods.
- Evidence labels:
  - VERIFIED: `maps flow start` exists and stops before provider/session launch.
  - VERIFIED: `claim_review()` enforces current review eligibility and
    independence.
  - VERIFIED: `bind_review_subject()` already enforces immutable review-subject
    freshness, artifact refs, and consequential review requirements.
- Dependencies / preconditions: current `origin/main` at PR #154 merge.

## Change boundary

- MAY CHANGE:
  - `runtime/flow_review.py`
  - `runtime/cli.py`
  - focused flow/review tests
  - `work/roadmaps/CAPABILITY_CHECKLIST.md` row `6.21`
  - this task file
- MUST NOT CHANGE:
  - review verdict semantics
  - reviewer independence rules
  - task approval / DONE transitions
  - RnS/recovery/harness behavior
  - Skill loading/trust behavior
  - external project / portable deployment behavior
- MAY CHANGE IF NECESSARY:
  - a small read-only helper on the review-subject store surface if needed to
    avoid duplicating consequential-review logic.
- OPERATOR APPROVAL REQUIRED: any flow that records a verdict, approves work,
  selects an external reviewer, or weakens review-subject requirements.

## Decision authority

- Owner may decide:
  - CLI option names for the review-start flow;
  - the returned flow payload shape;
  - whether missing required subject evidence fails preflight before claiming.
- Owner must escalate:
  - automatic review verdicts;
  - reviewer assignment/selection;
  - external/GitHub review actions;
  - changing review independence or consequential-review policy.

## Acceptance criteria

- [x] `flow_review_start()` composes existing review claim and review-subject
      binding operations without recording a verdict.
- [x] Consequential work that requires a review subject fails preflight when no
      subject evidence is supplied, without claiming the review.
- [x] Low-risk/simple review work can be claimed without a subject binding.
- [x] When subject evidence is supplied, the flow binds the immutable subject
      through the existing store API and returns it.
- [x] Invalid subject evidence fails before a durable review claim is left open.
- [x] CLI exposes `maps flow review-start` and emits JSON like other commands.
- [x] 6.21 checklist is updated while remaining `IN PROGRESS`.

## Verification and evidence

- Verification:
  - `git diff --check`
  - `python3 -m py_compile runtime/flow_review.py runtime/cli.py`
  - focused unit tests for review-start flow and review binding
- Evidence to preserve: test output, diff, independent review evidence.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: local deterministic runtime only.
- Ordered procedure: add flow module, wire CLI, add tests, update checklist,
  verify.
- Failure branches: if review-subject requirement cannot be checked without
  duplicating policy, add a small read-only store helper rather than guessing.
- Rollback / recovery: revert this branch.
- Security / privacy controls: do not include artifact ref values in event
  summaries beyond existing store behavior.
- External side effects: GitHub PR publication/merge only after review.
- Effort limit: no review-record flow in this task.
- Approved reference: existing `flow_start` composition pattern.

## Stop / escalate

Stop rather than guess if:

- claiming review before subject preflight would create ambiguous partial state;
- subject binding would need to weaken immutable review evidence rules;
- reviewer selection or verdict recording becomes necessary.

Escalate to: operator or separate implementation task.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- This is an agent-OS improvement under 6.21. It is intentionally unrelated to
  RnS and external pilot work.

## Completion / handoff

- Completed: implementation and focused verification.
- Not completed: independent review and merge.
- Current blocker: independent review.
- Next action if not DONE: review this implementation.
