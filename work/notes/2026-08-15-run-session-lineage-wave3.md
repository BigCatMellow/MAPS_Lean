# Run/session lineage Wave 3 — A1 implementation note

Date: 2026-08-15
Branch: `agent/run-session-lineage-wave3`
Historical stack dependency: PR #24 head `3be75c654051d27ad9beaf7d2620953f1e28d9ee`

## Purpose

Close the adapter-qualification hole deliberately left by merged PR #23 without mutating immutable run manifests or introducing task-level session truth.

Merged #23 established the correct fail-closed behavior:

- `run_manifests.session_id` is provider-local and therefore insufficient by itself;
- session-bound `send` / `resume` / `stop` must fail with `SESSION_ADAPTER_UNPROVEN` until durable adapter-qualified identity exists.

A1 supplies only that missing durable relationship.

## Project/provider-context repair

Independent review of the first A1 implementation found one foundational defect: it treated `(adapter_id, session_id)` as globally unique across every MAPS project. That was stronger than accepted Harness identity, where `SessionRef` includes `project_id` and project-scoped adapters/providers may legitimately reuse the same provider-local session ID.

The repaired identity is therefore:

`(project_id, adapter_id, session_id)`

`project_id` is not a new caller-controlled authority field. `record_run_session_link()` derives it from the canonical task owning the immutable run, and SQLite independently rejects direct inserts whose stored project does not match that run/task relationship.

## SQLite identity canonicalization repair

SENTINEL's re-review of the project-scoped repair found a second narrow but material boundary defect: SQLite uniqueness was still applied to raw stored strings while Python writer/resolver/guard code normalizes identity text. A direct SQL writer could therefore insert a trim-variant such as `project-a ` / `hcom ` / `sess-1 ` that SQLite considered distinct even though MAPS later treated it as the same logical provider identity.

The repaired SQLite boundary now:

- requires `run_session_links.project_id` to equal the owning task's canonical `project_id` **exactly**, not merely after `trim()`;
- constrains `adapter_id` and `session_id` to the same lexical identity class accepted by runtime `_lineage_id`: first character alphanumeric, only `[A-Za-z0-9_.:@-]`, and length 1–128;
- therefore rejects spaces, tabs, newlines, Unicode/other characters outside that identity alphabet, and any other raw-string variant that runtime normalization could collapse;
- retains raw `UNIQUE(project_id, adapter_id, session_id)` because the stored adapter/session keys are now canonical under the runtime identity contract and the project key must exactly match canonical task state.

Focused direct-SQL regression coverage attempts project trailing-space, adapter trailing-space/tab, and session trailing-space/newline variants against a second run after the canonical identity is already bound. All must fail at SQLite before the logical duplicate can exist.

No Python writer/resolver/guard semantic change was needed for this second repair.

## Storage model

Canonical cross-source relationship table:

`run_session_links`

Each row records:

- owning `run_id`;
- `ATTACH` or `REPLACE` relation;
- canonical task `project_id` copied as provider-namespace evidence;
- `adapter_id`;
- provider-local `session_id`;
- optional predecessor link for replacement;
- bounded `evidence_ref`;
- recording actor and timestamp.

The table is append-only. SQLite rejects UPDATE and DELETE.

Database constraints/triggers additionally enforce:

- one root `ATTACH` per run;
- at most one child replacement per link;
- replacement predecessor belongs to the same run;
- one durable run owner for a project-scoped `(project_id, adapter_id, session_id)` identity;
- two different projects may independently use the same adapter/session ID;
- stored `project_id` exactly matches the canonical task project for the owning run;
- adapter/session stored keys satisfy the runtime identity alphabet and cannot carry normalization whitespace variants;
- direct-SQL first attachment cannot contradict an immutable manifest's pre-existing bare `session_id`;
- bounded non-empty evidence/actor values.

No column is added to `tasks`. No `run_manifests` column is changed.

## Resolver semantics

`TaskStore.resolve_run_session(run_id)` returns one of:

- `UNBOUND` — no explicit lineage and no manifest session ID;
- `ADAPTER_UNPROVEN` — legacy/bare manifest session ID exists but has not been adapter-qualified;
- `EXPLICIT` — one valid append-only relationship chain exists; `current` is the terminal link;
- `INVALID` — stored rows do not form one linear, canonical-project-consistent chain.

The resolver exposes the canonical `project_id` at the lineage level and on explicit/current link evidence. The trace projection inherits this output unchanged.

The resolver does not inspect provider liveness and does not grant ownership, review, approval, policy, or readiness authority.

## Write semantics

`record_run_session_link(...)` requires:

- an existing immutable run;
- exact immutable run worker;
- canonical owning task with non-empty project identity;
- current ACTIVE claim by that worker;
- live lease;
- unchanged task revision;
- explicit adapter/session/evidence identity.

The caller does not provide a project argument. Project context is derived from the canonical task row inside the same `BEGIN IMMEDIATE` transaction.

First explicit link:

- must not name a predecessor;
- if the immutable manifest already contains a bare `session_id`, the first link must use that same session ID.

Replacement:

- must name the exact current link;
- creates a new immutable row;
- remains inside the same run/project context;
- never rewrites the prior link or run manifest.

A worker change remains a new-run concern and is outside A1.

## Canonical guard integration

`CanonicalRunGuard` consumes `resolve_run_session(run_id)` for session-bound operations.

Behavior remains fail-closed:

- `UNBOUND` -> `SESSION_NOT_DURABLY_BOUND`;
- `ADAPTER_UNPROVEN` -> `SESSION_ADAPTER_UNPROVEN`;
- `INVALID` -> `SESSION_LINEAGE_INVALID`;
- `EXPLICIT` -> requested `SessionRef.project_id`, `adapter`, and `session_id` must match canonical task/binding context and the terminal durable relationship exactly.

The guard performs the project check independently even though `HarnessService` already validates `ExecutionBinding.project_id == SessionRef.project_id`. This prevents a direct Hook invocation or malformed context from bypassing the durable identity boundary.

The guard still separately verifies task/run/worker/revision/lease/current-run evidence. Session lineage does not replace those checks.

## PR #24 enforcement boundary retained

A1 preserves the security boundary inherited from PR #24:

- Hook enforcement roles are recorded internally by `HookRegistry`, not inferred from caller-controlled callback attributes;
- `register_canonical_run_guards()` requires an exact `CanonicalRunGuard` rather than a lookalike callback;
- mandatory canonical hooks remain fail-closed and read-only;
- anti-spoof HarnessService regressions remain part of the A1 stack.

A1 changes only the durable session evidence source consumed by that guard; it does not weaken or replace enforcement composition.

## Trace integration

`TaskStore.trace_task()` is enriched through a narrow composition mixin. Each run gets its derived `session_lineage` projection, including project-scoped provider identity when explicit.

Coverage remains deliberately incomplete:

- explicit MAPS run/session relationships are included;
- absence of a MAPS relationship does not prove an external provider session never existed;
- communication and provider liveness remain separate evidence sources.

## Deliberate non-features

A1 does not add:

- mutable current-session state on tasks;
- helper/recovery lineage;
- submission-attempt lineage;
- communication-to-task/run joins;
- wait/pending inference;
- provider health/readiness checks;
- automatic session discovery;
- manifest rewriting/backfill heuristics.

Legacy rows are not guessed into adapter-qualified identity.

## Development / integration boundary

FOUNDRY owns only the returned #48 implementation defects because this continuity already modified the branch. After fresh exact-head CI, the branch must freeze for independent re-review. FOUNDRY is not eligible to provide that review.

SWITCHYARD owns eventual synchronization onto then-current accepted `main`, exact-delta verification, fresh integrated-head CI/review gating, and merge.

## Next tranche

After A1 is mechanically clean and accepted, A2 can be developed as a separate stack adding explicit helper/recovery run relationships without copying helper/recovery mutable result state into a second authority store.
