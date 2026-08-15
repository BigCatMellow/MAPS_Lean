# Task: immutable review subject / evidence binding

- Status: `ACTIVE`
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

- [ ] add immutable `review_subjects` record keyed one-to-one to an existing claimed review.
- [ ] subject snapshots exact task ID, submission count, task revision, optional run ID, immutable artifact/evidence refs, freshness mode, binder, and timestamp.
- [ ] supported freshness modes are `REVISION_BOUND`, `REDERIVED_AT_REVIEW`, and `NON_CONSEQUENTIAL`.
- [ ] v1 artifact refs accept only `sha256:<64 hex>` or `git:<40/64 hex>`; mutable filenames/URLs/plain prose are rejected as identity.
- [ ] review subject can be bound only by current review owner while task is READY_FOR_REVIEW and submission exists.
- [ ] review subject is immutable and cannot be rebound/updated/deleted.
- [ ] high-risk, operator-gated/destructive/external/security/broad-architecture, or operator-visible-release review requires bound freshness evidence before APPROVED.
- [ ] low-risk/medium unflagged ordinary review remains approvable without a subject binding.
- [ ] `NON_CONSEQUENTIAL` freshness cannot satisfy a consequential approval.
- [ ] `REVISION_BOUND` requires at least run ID or immutable artifact refs.
- [ ] `REDERIVED_AT_REVIEW` requires immutable refs at binding and exact matching rederived refs at approval.
- [ ] approval validation runs inside the existing review transaction to avoid TOCTOU between subject validation and review completion.
- [ ] approval rejects changed submission count, changed task revision, stale/missing bound run, and overall-vs-criterion revision/run mismatch.
- [ ] existing criterion approval checks still run after subject validation.
- [ ] read-only trace includes exact review subject under the owning review.
- [ ] binding event does not dump artifact refs.
- [ ] focused tests and full Runtime stack CI pass.
- [ ] independent review remains required before completion.

## Verification and evidence

- Verification: `python -m unittest tests.test_review_subject_binding -v` plus full PR-triggered Runtime stack CI.
- Evidence to preserve: schema diff, review atomicity tests, stale-subject tests, PR diff, CI run, independent review result.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: existing canonical SQLite review/task state.
- Ordered procedure: immutable schema → binding mixin → atomic ReviewMixin approval hook → trace projection → behavioral tests → independent draft PR → full CI → review.
- Failure branches: IF exact artifact identity cannot be represented by an immutable ref THEN do not pretend the review is revision-bound; use a later artifact registry/rederivation mechanism. IF a low-risk task has no consequential trigger THEN retain existing simple review behavior.
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

- This task starts independently from merged `main`; it does not depend on the unmerged Harness, Skills, or Environment stacks.
- Consequential-review requirement is derived only from existing canonical risk/policy/review flags. It does not create a new policy authority.
- Review binding happens after review claim and before approval. Binding does not grant the reviewer anything they did not already have.
- The existing `ReviewMixin.record_review()` receives one optional `rederived_artifact_refs` keyword and invokes an optional approval hook while holding the same SQLite transaction.
- The new mixin supplies that hook and extends trace through MRO composition, avoiding a second review engine.
- Artifact identity syntax is intentionally narrow in v1. Extend only when a real immutable artifact-ID class exists and can be validated mechanically.

## Completion / handoff

- Completed: implementation prepared on `agent/review-subject-binding-wave2`.
- Not completed: commit/PR/CI/review.
- Current blocker: none.
- Next action if not DONE: commit isolated Phase 3 implementation, open a draft PR against `main`, and run full Runtime stack CI.
