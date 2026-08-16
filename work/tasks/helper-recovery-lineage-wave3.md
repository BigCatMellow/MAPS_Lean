# Task: helper/recovery lineage Wave 3

- Status: `IN_PROGRESS`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `agent/helper-recovery-lineage-wave3`
- Risk: `MEDIUM`
- Dependency: PR #48 / A1 exact base head `13b3293781a43980066f642edb79cf7f4528d4aa`

## Goal

Add explicit append-only run↔helper and predecessor-run↔replacement-run relationships while keeping existing helper/recovery stores authoritative for their own result/mutable state.

## Required boundaries

- Do not copy helper status, summary, output contents, or RecoveryIncident mutable fields into SQLite lineage.
- Do not turn recovery/session liveness into task truth.
- Do not create or imply review independence from recovery/helper identity.
- Do not add a permanent supervisor or new worker process.
- Do not modify A1/PR #48's branch.
- Existing helper and recovery APIs remain usable without a lineage-aware orchestrator.

## Helper lineage semantics

1. `helper_run_id` is stable and allocated before the helper's consequential subprocess/file side effect.
2. A caller may preallocate a helper ID and pass it into Aider/Ollama; the returned `HelperResult` must preserve it.
3. `run_helper_links` records only relationship evidence: helper ID, owning run, invoker worker, optional immediate parent session link OR parent helper, bounded evidence ref, actor/time.
4. Root/helper parent identity must resolve inside the same run.
5. The invoker worker must match the immutable run worker and current ACTIVE claimant with a live lease/current task revision when the invocation relationship is recorded.
6. Helper result JSON remains the source for helper status/summary/output paths. A link without a result is valid evidence of an invocation that may have failed/interrupted.

## Recovery lineage semantics

1. `run_recovery_links` records an explicit predecessor run -> replacement run relationship.
2. Both runs must exist, be different, and belong to the same task.
3. Replacement cannot predate its predecessor.
4. One predecessor has at most one direct replacement; one replacement has at most one predecessor, yielding an explicit linear recovery chain.
5. A bounded recovery/incident reference and evidence ref are required, but existing RecoveryStore remains authority for incident state/attempt/backoff/error.
6. Recovery lineage is distinct from `continuity_links`; it neither grants nor proves independent review.

## Acceptance criteria

- [ ] helper IDs can be preallocated and are preserved by Aider/Ollama results.
- [ ] helper ID is chosen before helper side effects.
- [ ] helper links are append-only and same-run parent relationships are mechanically enforced.
- [ ] helper link creation rejects wrong/stale claimant authority.
- [ ] helper result fields are not duplicated into SQLite lineage.
- [ ] recovery links are append-only, same-task, chronological, non-self, and linear.
- [ ] recovery linkage does not mutate either run manifest or RecoveryStore.
- [ ] trace exposes explicit helper/recovery relationships with incomplete legacy/external coverage.
- [ ] focused adversarial tests pass.
- [ ] full Runtime CI passes on the exact PR head.

## Verification

```text
python -m unittest tests.test_helper_recovery_lineage tests.test_bounded_helpers tests.test_recovery_supervisor -v
```

Review required: `INDEPENDENT_REVIEW` before merge/completion.

## Stop

Stop after A2 relationship storage, helper-ID preallocation, trace projection, and tests. Do not implement submission lineage (A3), communication task/run joins (A4c), or explainable waits (A4d) here.
