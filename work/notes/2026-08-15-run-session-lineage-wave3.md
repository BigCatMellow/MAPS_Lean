# Run/session lineage Wave 3 — A1 implementation note

Date: 2026-08-15
Branch: `agent/run-session-lineage-wave3`
Stack base: PR #24 exact head `4ec42de3398258ebde0e0645516caef953a6a0ed`

## Purpose

Close the adapter-qualification hole deliberately left by merged PR #23 without mutating immutable run manifests or introducing task-level session truth.

Merged #23 established the correct fail-closed behavior:

- `run_manifests.session_id` is provider-local and therefore insufficient by itself;
- session-bound `send` / `resume` / `stop` must fail with `SESSION_ADAPTER_UNPROVEN` until durable adapter-qualified identity exists.

A1 supplies only that missing durable relationship.

## Storage model

New canonical cross-source relationship table:

`run_session_links`

Each row records:

- owning `run_id`;
- `ATTACH` or `REPLACE` relation;
- `adapter_id`;
- provider-local `session_id`;
- optional predecessor link for replacement;
- bounded `evidence_ref`;
- recording actor and timestamp.

The table is append-only. SQLite rejects UPDATE and DELETE.

Database constraints additionally enforce:

- one root `ATTACH` per run;
- at most one child replacement per link;
- one durable run owner for an adapter-qualified `(adapter_id, session_id)` identity.

No column is added to `tasks`. No `run_manifests` column is changed.

## Resolver semantics

`TaskStore.resolve_run_session(run_id)` returns one of:

- `UNBOUND` — no explicit lineage and no manifest session ID;
- `ADAPTER_UNPROVEN` — legacy/bare manifest session ID exists but has not been adapter-qualified;
- `EXPLICIT` — one valid append-only relationship chain exists; `current` is the terminal link;
- `INVALID` — stored rows do not form one linear chain.

The resolver does not inspect provider liveness and does not grant ownership, review, approval, policy, or readiness authority.

## Write semantics

`record_run_session_link(...)` requires:

- an existing immutable run;
- exact immutable run worker;
- current ACTIVE claim by that worker;
- live lease;
- unchanged task revision;
- explicit adapter/session/evidence identity.

First explicit link:

- must not name a predecessor;
- if the immutable manifest already contains a bare `session_id`, the first link must use that same session ID.

Replacement:

- must name the exact current link;
- creates a new immutable row;
- never rewrites the prior link or run manifest.

A worker change remains a new-run concern and is outside A1.

## Canonical guard integration

`CanonicalRunGuard` now consumes `resolve_run_session(run_id)` for session-bound operations.

Behavior remains fail-closed:

- `UNBOUND` -> `SESSION_NOT_DURABLY_BOUND`;
- `ADAPTER_UNPROVEN` -> `SESSION_ADAPTER_UNPROVEN`;
- `INVALID` -> `SESSION_LINEAGE_INVALID`;
- `EXPLICIT` -> requested `SessionRef.adapter` and `session_id` must match the terminal relationship exactly.

The guard still separately verifies task/run/worker/revision/lease/current-run evidence. Session lineage does not replace those checks.

## Trace integration

`TaskStore.trace_task()` is enriched through a narrow composition mixin. Each run gets its derived `session_lineage` projection.

Coverage remains deliberately incomplete:

- explicit MAPS relationships are included;
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

## Stack dependency

This branch is intentionally stacked on open PR #24 rather than waiting for its review/merge.

Before A1 merges:

1. re-check #24 exact accepted head;
2. synchronize this branch if #24 changed;
3. rerun full Runtime CI;
4. obtain independent review on the integrated A1 state.

## Next tranche

After A1 is accepted:

A2 should add explicit helper/recovery run relationships, without copying helper/recovery mutable result state into a second authority store.
