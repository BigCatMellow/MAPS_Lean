# Helper/recovery lineage Wave 3 — A2 implementation note

Date: 2026-08-15
Branch: `agent/helper-recovery-lineage-wave3`
Stack base: A1 / PR #48 head `13b3293781a43980066f642edb79cf7f4528d4aa`

## Purpose

Extend explicit execution lineage into two relationships the existing subsystems do not own:

1. immutable run -> helper invocation identity;
2. immutable predecessor run -> replacement run after recovery.

The design deliberately does not copy helper result state or RecoveryStore incident state into SQLite.

## Existing source ownership preserved

### HelperResult / HelperRunStore

Existing helper JSON remains authoritative for:

- helper implementation/model label;
- completion status;
- summary;
- output paths;
- result timestamp.

A `run_helper_links` row records only that a specific stable helper invocation identity belongs to a run and, when known, its immediate invocation parent.

A relationship may exist without a HelperResult. This is intentional: if a helper starts and fails/interruption occurs before result persistence, the invocation identity can still be represented honestly.

### RecoveryStore

Existing RecoveryStore JSON remains authoritative for:

- incident state;
- attempts/backoff;
- next/last attempt times;
- last error;
- terminal-session and last-live observations.

A `run_recovery_links` row stores only an explicit predecessor/replacement run relationship plus references back to recovery/evidence sources.

## Stable helper identity before side effects

Before A2, both bounded helper wrappers allocated `helper_run_id` only when constructing the final HelperResult, after their external work had already happened.

A2 adds:

- `new_helper_run_id()`;
- `validate_helper_run_id()`;
- optional `helper_run_id=` on `new_result()`;
- optional `helper_run_id=` on Aider/Ollama `.run()`.

When the caller does not supply an ID, each wrapper allocates one after pure input/scope validation but before any helper subprocess begins. When orchestration needs durable lineage before invocation, it can:

1. preallocate a helper ID;
2. record `run_helper_links`;
3. invoke the wrapper with that exact ID;
4. receive a HelperResult carrying the same ID.

This is backward compatible with existing helper calls.

## run_helper_links

Relationship fields only:

- `helper_run_id`;
- `run_id`;
- `invoker_worker_id`;
- optional `parent_session_link_id`;
- optional `parent_helper_run_id`;
- `evidence_ref`;
- `created_by` / `created_at`.

The helper may have at most one immediate parent dimension: session or helper.

SQLite and application validation require parent session/helper relationships to belong to the same run. Rows are immutable.

Recording also revalidates:

- immutable run worker;
- current ACTIVE claimant;
- live lease;
- current task revision.

This prevents a stale or different worker from attaching new helper invocation evidence to a run it no longer owns.

## run_recovery_links

Relationship fields only:

- predecessor run;
- replacement run;
- recovery/incident reference;
- evidence reference;
- recording actor/time.

Mechanical invariants:

- predecessor != replacement;
- both runs exist;
- both belong to the same task;
- replacement creation is not earlier than predecessor creation;
- one direct replacement per predecessor;
- one direct predecessor per replacement;
- rows are immutable.

These constraints produce a linear explicit recovery chain without interpreting provider liveness or incident state.

## continuity_links remain different

`continuity_links` answer an identity/reviewer-independence question: whether two identities share inherited execution context.

`run_recovery_links` answer a run-history question: whether one immutable run explicitly replaced another.

A recovery link does not grant task ownership and does not prove independent review. A future recovery orchestrator may need both facts, but they remain separate authorities.

## Trace behavior

Each run trace now includes:

- `session_lineage` from A1;
- `helper_lineage` from A2;
- `recovery_lineage` from A2.

Coverage is explicitly incomplete for all three. In particular:

- absence of a helper link does not prove no legacy/external helper ran;
- recovery relationship rows do not include or replace RecoveryStore incident state.

## Deliberate non-features

A2 does not:

- run helpers automatically;
- create recovery replacement runs automatically;
- change RecoverySupervisor behavior;
- convert worker/session liveness into task truth;
- duplicate helper status/output information into SQLite;
- duplicate incident state/backoff/error into SQLite;
- merge recovery with review continuity;
- implement submission-attempt lineage;
- join communication messages to task/run identity;
- infer pending/wait states.

## Verification focus

Tests cover:

- helper ID allocation occurs before Aider/Ollama subprocesses;
- explicit preallocated ID is preserved;
- helper link rows contain no result fields;
- helper rows are immutable;
- session/helper parents must belong to same run;
- two simultaneous immediate parents are rejected;
- worker/lease/task-revision rechecks;
- duplicate helper identity rejection;
- same-task linear recovery;
- no RecoveryStore mutation during relationship recording;
- branch/duplicate predecessor/replacement rejection;
- cross-task/self recovery rejection;
- direct-SQL same-task and chronology enforcement;
- trace projections remain explicitly incomplete.

## Next tranche

After A2 is mechanically clean, A3 should add exact `(task_id, submission_count) -> run_id` relationships atomically at submission time when an explicit run is supplied. It must not infer run identity from timestamps or from there being only one run.
