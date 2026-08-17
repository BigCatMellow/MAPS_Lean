# Helper/recovery lineage Wave 3 — A2 rebuild note

Date: 2026-08-16
Branch: `agent/helper-recovery-lineage-wave3`
Historical A2 head: `ed865be729cf2d15663258fd46c9296ea32d28e7`
Accepted A1: PR #48 / `main@eccdddaa37e42c93982bedf20d19e4f5096dbcff`
Current rebuild baseline: `main@c4c93e52edd961802c7c203035f0bc272f196b59`

## Purpose

Extend explicit execution lineage into two relationships the existing subsystems do not own:

1. immutable run -> helper invocation identity;
2. immutable predecessor run -> replacement run after recovery.

The design deliberately does not copy helper result state or RecoveryStore incident state into SQLite.

## Accepted A1 composition

Accepted A1 defines session identity as `(project_id, adapter_id, session_id)`, derives project context from canonical task state, and mechanically enforces canonical project identity in SQLite.

A2 composes with that accepted model without adding another project column or authority:

- `parent_session_link_id` is valid only when the referenced A1 session link belongs to the same immutable run as the helper invocation. The run owns one canonical task/project context, so helper ancestry cannot cross that boundary.
- helper-parent links likewise require the parent helper to belong to the same run.
- recovery links require predecessor and replacement runs to belong to the same canonical task. Same-task identity preserves the canonical project boundary while RecoveryStore remains authority for incident state.

The later accepted PR #45 hcom message-relationship projection is preserved wholesale from current main and is not part of A2.

## Existing source ownership preserved

### HelperResult / HelperRunStore

Existing helper JSON remains authoritative for helper implementation/model label, completion status, summary, output paths, and result timestamp.

A `run_helper_links` row records only that a stable helper invocation identity belongs to a run and, when known, its immediate invocation parent. A relationship may exist without a HelperResult if invocation begins but result persistence does not complete.

### RecoveryStore

Existing RecoveryStore JSON remains authoritative for incident state, attempts/backoff, next/last attempt times, last error, terminal-session evidence, and last-live observations.

A `run_recovery_links` row stores only an explicit predecessor/replacement run relationship plus bounded evidence references.

## Stable helper identity before side effects

A2 provides `new_helper_run_id()`, `validate_helper_run_id()`, optional `helper_run_id=` on `new_result()`, and optional `helper_run_id=` on Aider/Ollama `.run()`.

When no ID is supplied, wrappers allocate one after pure validation and before the helper subprocess/file side effect. A lineage-aware caller may preallocate, record the relationship, invoke the helper with that exact ID, and receive a `HelperResult` carrying the same identity.

## Helper lineage mechanics

`run_helper_links` stores only helper ID, run ID, invoker worker, optional immediate parent session/helper, evidence reference, and actor/time.

Application and SQLite checks require same-run parent relationships. Recording revalidates immutable run worker, current ACTIVE claimant, live lease, and current task revision. Rows are immutable.

## Recovery lineage mechanics

`run_recovery_links` stores predecessor/replacement run identity plus recovery/evidence references and actor/time.

Mechanical invariants remain:

- predecessor != replacement;
- both runs exist and belong to the same task;
- replacement does not predate predecessor;
- one direct replacement per predecessor and one predecessor per replacement;
- application and SQLite boundaries reject cycles, including equal-timestamp cycles;
- rows are immutable.

## Rebuild conflict resolution

A real synchronization attempt showed conflicts at exactly the two expected composition paths: `runtime/state/schema.sql` and `runtime/state/store.py`.

The owner rebuild treats current accepted main as authoritative:

- current-main A1 `run_session_links`, project checks, normalization constraints, environment evidence, review/outcome state, and all other accepted schema remain unchanged;
- A2 adds only `run_helper_links`, `run_recovery_links`, their indexes/triggers, and corresponding `HelperRecoveryLineageMixin` wiring;
- historical A2 helper wrappers, lineage implementation, trace extension, and tests carry forward unchanged;
- task/note text alone is refreshed for accepted ancestry and project-scope evidence;
- current-main PR #45 hcom files remain untouched.

PR #50 submission lineage is deliberately not included.

## Trace behavior

Each run trace includes `session_lineage` from accepted A1 plus A2 `helper_lineage` and `recovery_lineage`. Coverage remains explicitly UNKNOWN/incomplete for legacy/external activity: absence of a helper link does not prove no external helper ran, and recovery relationship rows do not replace RecoveryStore incident evidence.

## Authority boundary

A2 does not run helpers automatically, create replacement runs automatically, change RecoverySupervisor behavior, convert liveness into task truth, duplicate helper/incident state, merge recovery with review continuity, implement submission lineage, join communication to task/run identity, or infer pending/wait states.

## Verification / handoff

Historical A2 Runtime CI #268 passed on `ed865be729cf2d15663258fd46c9296ea32d28e7`, but that evidence is stale after rebuilding on accepted A1/current main.

The final rebuilt head must have:

1. real ancestry from current accepted main;
2. exactly the twelve declared A2 paths in `main -> head`;
3. fresh full Runtime CI on the exact rebuilt head;
4. independent exact-head review confirming accepted A1 preservation and A2-only authority boundaries.

FOUNDRY owns the rebuild but cannot provide the required independent review or merge it.
