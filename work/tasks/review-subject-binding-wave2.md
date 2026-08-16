# Task: immutable review subject / evidence binding

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `ChatGPT / implementation agent`
- Risk: `HIGH`
- Goal: make consequential review approval mechanically identify and validate the exact submission/task/run/artifact subject being approved, while preserving the existing review lifecycle and keeping ordinary low-risk review simple.

## Inputs and source of truth

- Inputs: `AGENTS.md`, merged `main`, `runtime/state/review.py`, `runtime/state/integrity.py`, `runtime/state/schema.sql`, Prime roadmap Phase 3.
- Authoritative sources: canonical SQLite task/submission/run/review state and immutable task/run revisions win; review-subject binding is additional audit/approval evidence, not a second review authority.
- Dependencies / preconditions: PR #19 merged baseline provides immutable task/run revisions, criterion evidence, review independence, and read-only trace.

## Change boundary

- MAY CHANGE: new `runtime/state/review_binding.py`, `runtime/state/review.py` narrow approval-hook/signature extension, `runtime/state/store.py`, `runtime/state/schema.sql`, focused tests, this task file.
- MUST NOT CHANGE: reviewer-claim authority/independence semantics, task claim/lease behavior, run-manifest immutability, criterion-verdict ownership rules, outcome semantics, external systems.
- MAY CHANGE IF NECESSARY: narrow review-subject schema/freshness validation inside this Phase 3 task.
- OPERATOR APPROVAL REQUIRED: new deployment/release behavior, weakening independent review, destructive/external behavior, or material scope expansion.

## Decision authority

- Owner may decide: consequential-review trigger using existing risk/policy/release-review flags, immutable subject fields, artifact-ref v1 syntax, freshness-mode validation, atomic approval hook, and focused tests consistent with Phase 3.
- Owner must escalate: any design that lets review bindings grant reviewer/operator authority, accepts mutable filenames/URLs as immutable identity, creates a second task/review lifecycle, or silently makes all low-risk work bureaucratic.

## Acceptance criteria

- [x] add immutable `review_subjects` record keyed one-to-one to an existing claimed review.
- [x] subject snapshots exact task ID, submission count, task revision, optional run ID, immutable artifact/evidence refs, freshness mode, binder, and timestamp.
- [x] supported freshness modes are `REVISION_BOUND`, `REDERIVED_AT_REVIEW`, and `NON_CONSEQUENTIAL`.
- [x] v1 artifact refs accept only `sha256:<64 hex>` or `git:<40/64 hex>`; mutable filenames/URLs/plain prose are rejected as identity.
- [x] review subject can be bound only by current review owner while task is READY_FOR_REVIEW and submission exists.
- [x] review subject is immutable and cannot be rebound/updated/deleted.
- [x] high-risk, operator-gated/destructive/external/security/broad-architecture, or operator-visible-release review requires bound freshness evidence before APPROVED.
- [x] low-risk/medium unflagged ordinary review remains approvable without a subject binding.
- [x] `NON_CONSEQUENTIAL` freshness cannot satisfy a consequential approval.
- [x] consequential `REVISION_BOUND` requires at least one immutable artifact/evidence ref identifying the reviewed output; run ID may be additional provenance but cannot substitute for output identity.
- [x] non-consequential `REVISION_BOUND` retains the narrower generic requirement of run ID or immutable artifact refs when explicitly bound.
- [x] `REDERIVED_AT_REVIEW` requires immutable refs at binding and exact matching rederived refs at approval.
- [x] approval validation runs inside the existing review transaction to avoid TOCTOU between subject validation and review completion.
- [x] existing criterion completeness validation preserves its established failure precedence before review-subject validation.
- [x] confirmed criterion run evidence alone cannot derive an approvable consequential review subject; explicit immutable reviewed-output identity remains required.
- [x] approval defensively rejects any consequential bound subject with empty immutable artifact/evidence refs.
- [x] approval rejects changed submission count, changed task revision, stale/missing bound run, and overall-vs-criterion revision/run mismatch.
- [x] read-only trace includes exact review subject under the owning review.
- [x] binding event does not dump artifact refs.
- [x] focused tests and full Runtime stack CI pass on the repaired pre-integration implementation.
- [ ] current-main synchronization, fresh exact-head full Runtime CI, and independent exact-head re-review remain required before completion.

## Verification and evidence

- Initial PR CI run `31898581152` exposed an integration-order regression: an existing high-risk criterion test expected `CRITERION_VERIFICATION_INCOMPLETE`, while the first implementation returned `REVIEW_SUBJECT_REQUIRED` earlier.
- The first correction preserved criterion-check precedence but automatically derived an overall subject from same-run criterion evidence.
- Independent review on head `489a2524b513d6d9ab5eb186874cbc04e6e4ba4a` found that run identity is execution provenance, not immutable reviewed-output identity; both manual run-only binding and automatic same-run criterion derivation could therefore approve stale output bytes.
- The narrow repair requires immutable artifact/evidence refs for consequential `REVISION_BOUND`, removes automatic run-only criterion derivation from approval, and adds defense-in-depth approval rejection for empty refs.
- Focused regressions now require run-only consequential binding to fail and confirmed criterion run evidence alone to leave approval blocked until an explicit immutable output ref is bound.
- Evidence to preserve: schema diff, historical CI, blocking independent review, repaired exact-head CI, repaired tests, PR #32 diff, and fresh independent review result.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: existing canonical SQLite review/task state.
- Ordered procedure: immutable schema → binding mixin → atomic ReviewMixin approval hook → preserve criterion-check precedence → exact reviewed-output identity gate → trace projection → behavioral tests → current-main synchronization → full CI → independent review.
- Failure branches: IF exact artifact identity cannot be represented by an immutable ref THEN consequential approval must remain blocked; do not substitute run identity, mutable criterion paths, filenames, URLs, or prose. IF a low-risk task has no consequential trigger THEN retain existing simple review behavior.
- Rollback / recovery: revert isolated independent commit/PR; additive table and optional method parameter only.
- Security / privacy controls: artifact refs are hashes/commit IDs, event summary omits them, no raw evidence/source text copied into subject table.
- External side effects: Git branch/PR publication only.
- Effort limit: Phase 3 review-subject binding v1; no artifact registry, release publisher, or acquisition-path system.
- Approved reference: Prime Agent capability roadmap Phase 3.

## Stop / escalate

Stop rather than guess if:

- approval needs a mutable artifact name treated as identity;
- a review subject would need to alter task/reviewer authority;
- atomic validation cannot be kept inside the existing review transaction;
- the change would require reopening every low-risk review path.

Escalate to: operator / roadmap re-shaping as appropriate.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- This task started independently from merged `main`; it does not depend on the unmerged Harness, Skills, or Environment stacks.
- Consequential-review requirement is derived only from existing canonical risk/policy/review flags. It does not create a new policy authority.
- Review binding happens after review claim and before approval. Binding does not grant the reviewer anything they did not already have.
- The existing `ReviewMixin.record_review()` receives one optional `rederived_artifact_refs` keyword and invokes an optional approval hook while holding the same SQLite transaction.
- The new mixin supplies that hook and extends trace through MRO composition, avoiding a second review engine.
- Criterion confirmation remains criterion evidence. Even unanimous same-run criterion evidence does not mechanically identify the exact final output bytes and therefore cannot manufacture consequential overall review freshness.
- Run identity remains useful provenance but is not artifact identity.
- Artifact identity syntax is intentionally narrow in v1. Extend only when a real immutable artifact-ID class exists and can be validated mechanically.

## Completion / handoff

- Completed in the repair layer: immutable review subjects, consequential approval gating, rederivation checks, exact-output identity requirement, trace projection, and focused adversarial regressions.
- Not completed: synchronization with then-current accepted main, fresh exact-head Runtime CI, and independent re-review of the repaired head.
- Current blocker: independent exact-head review is required after synchronization because the agent implementing this repair cannot review its own fix.
- Next action if not DONE: synchronize the repaired six-file layer onto accepted main without dropping accepted state, run full Runtime CI, and hand the immutable base/head/CI packet to an independent reviewer.
