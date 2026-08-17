# Task: helper/recovery lineage Wave 3

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `agent/helper-recovery-lineage-wave3`
- Risk: `MEDIUM`
- Dependency: accepted A1 / PR #48 in `main@eccdddaa37e42c93982bedf20d19e4f5096dbcff`; rebuilt on current accepted `main@c4c93e52edd961802c7c203035f0bc272f196b59`

## Goal

Add explicit append-only run↔helper and predecessor-run↔replacement-run relationships while keeping existing helper/recovery stores authoritative for their own result/mutable state.

## Accepted A1 composition boundary

Accepted A1 defines durable provider session identity as `(project_id, adapter_id, session_id)`, with `project_id` derived from canonical task state and enforced at the SQLite boundary.

A2 does not add another project authority:

- a helper's optional `parent_session_link_id` must point to a session link belonging to the same immutable run, so accepted A1's canonical project context is inherited mechanically;
- a recovery predecessor and replacement must belong to the same canonical task, which likewise fixes project context;
- A2 stores only cross-source relationship evidence and does not duplicate `project_id` into helper/recovery rows.

The later accepted #45 hcom relationship layer is outside these twelve A2 paths and is preserved wholesale from current main.

## Required boundaries

- Do not copy helper status, summary, output contents, or RecoveryIncident mutable fields into SQLite lineage.
- Do not turn recovery/session liveness into task truth.
- Do not create or imply review independence from recovery/helper identity.
- Do not add a permanent supervisor or new worker process.
- Do not weaken or replace accepted A1 project-scoped session invariants.
- Existing helper and recovery APIs remain usable without a lineage-aware orchestrator.
- PR #50 / submission-attempt lineage remains downstream and out of scope.

## Helper lineage semantics

1. `helper_run_id` is stable and allocated before the helper's consequential subprocess/file side effect.
2. A caller may preallocate a helper ID and pass it into Aider/Ollama; the returned `HelperResult` preserves it.
3. `run_helper_links` records only relationship evidence: helper ID, owning run, invoker worker, optional immediate parent session link OR parent helper, bounded evidence ref, actor/time.
4. Parent session/helper identity resolves inside the same run.
5. The invoker worker matches the immutable run worker and current ACTIVE claimant with a live lease/current task revision when the invocation relationship is recorded.
6. Helper result JSON remains the source for helper status/summary/output paths. A link without a result is valid evidence of an invocation that may have failed/interrupted.

## Recovery lineage semantics

1. `run_recovery_links` records an explicit predecessor run -> replacement run relationship.
2. Both runs exist, differ, and belong to the same task.
3. Replacement cannot predate its predecessor.
4. One predecessor has at most one direct replacement; one replacement has at most one predecessor.
5. Application and SQLite boundaries reject cycles, including equal-timestamp cycles.
6. A bounded recovery/incident reference and evidence ref are required, while RecoveryStore remains authority for incident state/attempt/backoff/error.
7. Recovery lineage is distinct from `continuity_links`; it neither grants nor proves independent review.

## Acceptance criteria

- [x] helper IDs can be preallocated and are preserved by Aider/Ollama results.
- [x] helper ID is chosen before helper subprocess/file side effects.
- [x] helper links are append-only and same-run parent relationships are mechanically enforced.
- [x] helper link creation rejects wrong/stale claimant authority.
- [x] helper result fields are not duplicated into SQLite lineage.
- [x] accepted A1 project-scoped session identity remains authoritative; A2 helper parents cannot escape the owning run/project context.
- [x] recovery links are append-only, same-task, chronological, non-self, linear, and acyclic.
- [x] recovery linkage does not mutate either run manifest or RecoveryStore.
- [x] direct SQLite writes cannot bypass same-task, chronology, or cycle constraints.
- [x] trace exposes explicit helper/recovery relationships with UNKNOWN/incomplete legacy/external coverage.
- [x] rebuild composition is limited to the twelve declared A2 paths and preserves current-main accepted state outside them.
- [ ] fresh exact-head Runtime CI passes on the rebuilt current-main head.
- [ ] independent exact-head review is CLEAN before integration.

## Verification

Historical focused targets:

```text
python -m unittest tests.test_helper_recovery_lineage tests.test_helper_recovery_lineage_sql tests.test_bounded_helpers tests.test_recovery_supervisor -v
```

Historical Runtime CI #268 passed on `ed865be729cf2d15663258fd46c9296ea32d28e7`; it is stale after the accepted-A1/current-main rebuild.

Final rebuilt head requires fresh full Runtime CI and independent review. Review must verify the exact current-main delta, accepted A1 preservation, same-run/same-task composition, append-only invariants, bounded UNKNOWN coverage language, and absence of new authority.

Review required: `INDEPENDENT_REVIEW` before merge/completion.

## Rebuild / conflict resolution

A direct Git synchronization of historical #49 with accepted main conflicts at the two expected composition points in `runtime/state/schema.sql` and `runtime/state/store.py`.

The owner resolution is intentionally narrow:

- preserve current-main `run_session_links` schema/triggers and `RunSessionLineageMixin` wiring verbatim;
- add A2 `run_helper_links` / `run_recovery_links` schema and triggers after accepted A1 lineage;
- add `HelperRecoveryLineageMixin` to `TaskStore` without removing accepted mixins;
- carry the remaining historical A2 implementation/tests unchanged;
- refresh only task/note ancestry evidence.

## Stop

A2 implementation/rebuild scope stops after fresh exact-head CI and independent handoff.

Submission lineage (A3 / PR #50), communication task/run joins (A4c), and explainable waits (A4d) remain separate review units.
