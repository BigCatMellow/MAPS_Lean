# Task: provider-neutral HarnessService

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `ChatGPT / implementation agent`
- Risk: `MEDIUM`
- Goal: compose the typed harness contract, explicit session correlation, registered adapters, and deterministic Hooks into one provider-neutral execution surface without creating task authority or a second session store.

## Inputs and source of truth

- Inputs: `AGENTS.md`, PR #20 typed harness foundation, PR #21 hcom normalization/Hook registry, existing run-manifest/session evidence, master roadmap, Harness Mechanics roadmap.
- Authoritative sources: active repository instructions and canonical runtime state win; stacked PRs provide the implementation dependencies.
- Dependencies / preconditions: PR #20 and PR #21 implementation heads; rebase/reshape if either changes materially during review.

## Change boundary

- MAY CHANGE: `runtime/harness/**`, focused harness-service tests, this task file.
- MUST NOT CHANGE: SQLite schema/task authority, existing hcom/helper/RnS behavior, routing/review semantics, deployment/external systems.
- MAY CHANGE IF NECESSARY: none without re-shaping.
- OPERATOR APPROVAL REQUIRED: destructive/external behavior or material scope expansion.

## Decision authority

- Owner may decide: service method shapes, adapter registry behavior, correlation checks, Hook invocation points, structured block/failure results.
- Owner must escalate: any design requiring inference of missing session identity, new mutable authority state, or task-policy decisions inside the harness.

## Acceptance criteria

- [x] `HarnessService` explicitly registers/selects adapters and reports unknown adapters structurally.
- [x] Mutating session operations require exact project/worker/session agreement between `ExecutionBinding` and `SessionRef`; attach may accept an unbound run only for explicit attachment.
- [x] `BEFORE_SEND`, `SESSION_STOPPING`, `RUN_STARTING`, and `RUN_STARTED` Hooks are integrated deterministically.
- [x] `DENY` and `REQUIRE_APPROVAL` block adapter invocation before mutation where possible.
- [x] A post-start Hook failure preserves evidence that provider mutation already happened rather than pretending the start did not occur.
- [x] The service does not import `TaskStore`, infer task authority, or create durable session state.
- [x] Focused tests and full Runtime stack CI pass.
- [ ] Independent review remains required before completion.

## Verification and evidence

- Verification: PR-triggered full Runtime stack CI run `31895128908` passed on implementation commit `96c614846314ea604be95df9feed5c7e3b477b62`.
- Evidence to preserve: GitHub Actions run `31895128908`, PR #22 diff, independent review result.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: existing MAPS Lean Python runtime.
- Ordered procedure: service/correlation layer → tests → stacked PR → CI → independent review.
- Failure branches: IF exact session correlation is absent THEN return structured failure; never choose “the only active session.”
- Rollback / recovery: revert isolated stacked commit/PR; no schema/data migration.
- Security / privacy controls: Hooks can only narrow/block; raw provider errors are not added here; no secret persistence.
- External side effects: Git branch/PR publication only; tests use dummy adapters.
- Effort limit: one narrow service-integration tranche.
- Approved reference: master roadmap + Harness Mechanics roadmap.

## Stop / escalate

Stop rather than guess if implementation requires a durable run/session join, policy authority inside the harness, or provider-specific assumptions not represented by an adapter.

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

- This is stacked on PR #21 rather than blocked on its review.
- Durable run/session lineage is still separate future work; this tranche enforces explicit correlation at call time only.

## Completion / handoff

- Completed: provider-neutral HarnessService, explicit correlation checks, Hook integration, focused tests, and full Runtime stack CI.
- Not completed: independent review / merge.
- Current blocker: independent review required for completion, but downstream stacked work may continue against this verified head.
- Next action if not DONE: independent review of PR #22; downstream work may stack on the verified implementation head.
