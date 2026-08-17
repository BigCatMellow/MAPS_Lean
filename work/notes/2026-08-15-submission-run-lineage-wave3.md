# Submission-attempt run lineage Wave 3 — A3 implementation note

Date: 2026-08-15
Branch: `agent/submission-run-lineage-wave3`
Stack base: A2 / PR #49 head `ed865be729cf2d15663258fd46c9296ea32d28e7`

## Purpose

Preserve exact run attribution for each task submission attempt without turning the existing mutable `task_submissions` row into a lossy current-run pointer.

A3 adds one narrow relationship:

`(task_id, submission_count) -> run_id`

Only an explicitly supplied run may create the relationship. Missing attribution remains `UNKNOWN`.

## Why a separate table

`task_submissions` intentionally stores the current submission and cumulative `submission_count`. Adding a mutable `run_id` column there would overwrite the run identity of earlier attempts after `CHANGES_REQUESTED` and resubmission.

`submission_run_links` is therefore append-only and keyed by the immutable attempt identity `(task_id, submission_count)`.

It stores only:

- task ID;
- submission count;
- run ID;
- link timestamp.

Submission evidence, current author, current evidence text, and submission timestamps remain owned by `task_submissions`.

## Submission API

`submit_task()` now accepts:

```text
run_id: str | None = None
```

### Omitted run

Omitting `run_id` preserves legacy behavior:

- submission remains valid;
- no relationship row is created;
- trace reports that attempt's run attribution as `UNKNOWN`;
- no timestamp, single-run, worker, session, or prose inference is attempted.

### Explicit run

When `run_id` is supplied, validation occurs under the existing `BEGIN IMMEDIATE` submission transaction.

The run must:

- exist;
- belong to the same task;
- belong to the submitting worker;
- carry the current canonical task revision.

The next exact `submission_count` is computed from the current submission row. The submission row update/insert and `submission_run_links` insert occur in the same transaction.

If relationship insertion fails, the entire submission mutation rolls back: task remains ACTIVE/claimed, submission count is unchanged, and no partial submission row survives.

## SQLite boundary

`submission_run_links` has:

- primary key `(task_id, submission_count)`;
- task/run foreign keys;
- same-task trigger;
- existing-attempt trigger;
- immutable UPDATE/DELETE triggers.

The existing-attempt rule permits an explicit historical link only for a submission count known to have existed (`count <= current submission_count`). It does not create or infer such links automatically.

## Retry semantics

A single immutable run may be explicitly associated with multiple submission counts. This is intentional: a worker can submit, receive changes requested, continue the same still-valid run, and explicitly submit it again.

The attempt identities remain distinct:

```text
(TASK-1, 1) -> RUN-1
(TASK-1, 2) -> RUN-1
```

No prior relationship is rewritten.

## Derived trace semantics

`submission_run_attribution(task_id)` derives one row for every known submission count:

- `EXPLICIT` + run ID when a relationship exists;
- `UNKNOWN` + null run ID when it does not.

`trace_task()` exposes this under `submission_run_lineage`.

Coverage is complete only if every known submission attempt has an explicit relationship. This is a derived completeness statement over MAPS-attributed attempts, not proof that external execution history is globally complete.

## Deliberate non-features

A3 does not:

- infer run identity from timestamps;
- infer from there being one run;
- infer from worker/session/helper/message identity;
- require run attribution for legacy callers;
- mutate immutable run manifests;
- change review authority;
- attach criterion claims automatically;
- join communication to task/run identity;
- infer wait/pending state.

## Verification focus

Tests cover:

- exact first attempt attribution;
- second attempt append without rewriting attempt 1;
- same run explicitly reused across attempts;
- omitted-run legacy submission -> `UNKNOWN`;
- missing run rejection with zero submission mutation;
- wrong-task run rejection;
- old-worker run rejection after claim recovery;
- stale run revision rejection;
- forced SQLite link failure rolling the whole submission transaction back;
- direct-SQL cross-task/future-attempt rejection;
- immutable link rows;
- no one-run/timestamp inference;
- trace completeness/UNKNOWN semantics.

## Next tranche

After A3 is mechanically clean, execution-lineage storage has the minimum run/session/helper/recovery/submission relationships needed for A4c: joining body-free provider communication evidence from PRs #44/#45 to explicit task/run/request identity.

A4c must still avoid inferring task/run attribution from names, timestamps, same-thread membership, or message prose.
