# Task: provider-neutral HarnessService

- Status: `ACTIVE`
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

- [ ] `HarnessService` explicitly registers/selects adapters and reports unknown adapters structurally.
- [ ] Mutating session operations require exact project/worker/session agreement between `ExecutionBinding` and `SessionRef`; attach may accept an unbound run only for explicit attachment.
- [ ] `BEFORE_SEND`, `SESSION_STOPPING`, `RUN_STARTING`, and `RUN_STARTED` Hooks are integrated deterministically.
- [ ] `DENY` and `REQUIRE_APPROVAL` block adapter invocation before mutation where possible.
- [ ] A post-start Hook failure preserves evidence that provider mutation already happened rather than pretending the start did not occur.
- [ ] The service does not import `TaskStore`, infer task authority, or create durable session state.
- [ ] Focused tests and full Runtime stack CI pass.
- [ ] Independent review remains required before completion.

## Verification and evidence

- Verification: `tests.test_harness_service` plus full PR-triggered Runtime stack CI.
- Evidence to preserve: stacked PR diff, GitHub Actions run, review result.
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

- Completed: implementation in progress on `agent/harness-service-wave1`.
- Not completed: tests/CI/review.
- Current blocker: none.
- Next action if not DONE: commit and open stacked draft PR against `agent/hcom-hooks-wave1`.
