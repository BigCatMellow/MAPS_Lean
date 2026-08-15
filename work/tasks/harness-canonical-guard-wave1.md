# Task: canonical harness run guard

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `ChatGPT / implementation agent`
- Risk: `MEDIUM`
- Goal: add a read-only canonical-state Hook guard so harness continuation operations cannot rely on session liveness or stale run identity instead of current MAPS task/run evidence.

## Inputs and source of truth

- Inputs: `AGENTS.md`, PRs #20–#22, `runtime/state/execution.py`, `runtime/state/integrity.py`, `runtime/state/schema.sql`, master roadmap, Prime roadmap Phase 2, Harness Mechanics roadmap.
- Authoritative sources: canonical SQLite task/run state and active repository instructions win; stacked PRs provide implementation dependencies.
- Dependencies / preconditions: verified PR #22 head `4d4eeb1bd42ada3582aec1efcceeb5e63fb6af0a`; existing immutable run manifests and task leases.

## Change boundary

- MAY CHANGE: `runtime/policy/harness_guard.py`, `runtime/policy/__init__.py`, focused tests, this task file.
- MUST NOT CHANGE: SQLite schema, task lifecycle/claim mutation behavior, run-manifest immutability, hcom/helper/RnS behavior, review semantics, external systems.
- MAY CHANGE IF NECESSARY: none without re-shaping.
- OPERATOR APPROVAL REQUIRED: any new durable authority/join state or destructive/external behavior.

## Decision authority

- Owner may decide: read-only guard checks, Hook registration points, denial codes/messages, and operation-specific freshness requirements consistent with existing canonical state.
- Owner must escalate: any need to mutate leases/task state, create a second session authority store, or weaken the ability to stop an explicitly known stale session safely.

## Acceptance criteria

- [x] Guard verifies explicit task/run/worker/project identity against canonical task and immutable run manifest.
- [x] `start`/`send` require current task revision, ACTIVE claimant, live lease, and non-stale run/context evidence.
- [x] `send` also requires exact durable run-manifest session binding.
- [x] `stop` requires exact task/run/session identity but does not require a live lease/current task revision, so stale known sessions remain stoppable by an otherwise authorized caller.
- [x] Guard fails closed when canonical evidence is missing, mismatched, stale, or unsupported.
- [x] Guard is read-only and grants no policy/operator authority.
- [x] Registration covers pre-mutation lifecycle events only.
- [x] Focused tests and full Runtime stack CI pass.
- [ ] Independent review remains required before completion.

## Verification and evidence

- Verification: PR-triggered full Runtime stack CI run `31895412303` passed on implementation commit `6c6eeeb050a3bc102250bafba9a849bab1e82b04`.
- Evidence to preserve: GitHub Actions run `31895412303`, PR #23 diff, independent review result.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: existing MAPS Lean Python runtime.
- Ordered procedure: read-only canonical guard → focused tests → stacked PR → CI → independent review.
- Failure branches: IF session binding is absent for `send`/`stop` THEN deny rather than infer from live hcom state; IF stale task/run state is found for continuation THEN deny and require recovery/rebinding.
- Rollback / recovery: revert isolated stacked commit/PR; no schema/data migration.
- Security / privacy controls: no raw provider transcript/logging; concise reason codes only; source reads are canonical and read-only.
- External side effects: Git branch/PR publication only; tests use fakes.
- Effort limit: one narrow guard tranche; durable late session attachment remains separate design work.
- Approved reference: master roadmap + Prime Phase 2 + Harness Mechanics roadmap.

## Stop / escalate

Stop rather than guess if:

- durable late session attachment becomes necessary to satisfy this task;
- stopping stale sessions would require reviving expired authority;
- canonical evidence cannot distinguish current continuation from historical cleanup.

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

- This is stacked on PR #22 rather than blocked on review.
- Session liveness is intentionally not used to renew or prove task authority.
- Historical stop targeting is identity verification, not permission grant; the caller must still possess authority outside this guard.
- Late session attachment is not solved here because immutable `run_manifests.session_id` requires a separate lineage design rather than a hidden mutable copy.

## Completion / handoff

- Completed: read-only canonical run guard, operation-specific continuation/cleanup semantics, focused tests, and full Runtime stack CI.
- Not completed: independent review / merge.
- Current blocker: independent review required for completion, but downstream stacked work may continue against this verified head.
- Next action if not DONE: independent review of PR #23; downstream security baseline work may stack on the verified implementation head.
