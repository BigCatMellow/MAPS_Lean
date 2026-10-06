# Task: canonical task/history retention design

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `ARCHITECTURE`
- Owner: `orchestration-operator`
- Risk: `HIGH`
- Goal: Define one explicit database contract for canonical task deletion and `task_events` update/delete behavior before any schema hardening.
- Parent roadmap: operator-approved reviewed-gap sequence; source finding in [`../notes/2026-09-09-competitor-borrow-integration-log.md`](../notes/2026-09-09-competitor-borrow-integration-log.md), Slice 09.
- Related records: PR #330 task/event atomicity regression; [`../notes/2026-09-09-competitor-borrow-integration-log.md`](../notes/2026-09-09-competitor-borrow-integration-log.md).
- Autonomous continuation: `YES`

## Inputs and source of truth

- Inputs: `runtime/state/schema.sql`, `runtime/state/base.py`, current state/runtime callers, existing immutable lineage-table patterns, PR #330 atomicity evidence, Slice 09 integration finding.
- Authoritative sources: `AGENTS.md` > approved operator sequence > this task > accepted `main` runtime/schema > supporting notes.
- Evidence labels:
  - VERIFIED — `task_events` is written through `_append_event()` in normal runtime flows.
  - VERIFIED — `task_events.task_id` currently uses `ON DELETE CASCADE`.
  - VERIFIED — `task_events` has no database `BEFORE UPDATE`/`BEFORE DELETE` immutability triggers.
  - VERIFIED — many newer lineage/evidence tables do have database immutability triggers.
  - VERIFIED — no public `delete_task()` runtime API was found in accepted `main`.
  - VERIFIED — task creation and `TASK_CREATED` append share one transaction, so ordinary tasks immediately acquire semantic history.
  - VERIFIED — some immutable child rows can already make parent deletion semantically inconsistent with broad cascade expectations.
- Dependencies / preconditions: PR #330 review-complete/merged evidence establishing local state+event transaction atomicity; no dependency on #335/#336/#337 implementation.

## Change boundary

- MAY CHANGE: this task record; one bounded design note; PR metadata/review evidence.
- MUST NOT CHANGE: `runtime/`, `tests/`, `runtime/state/schema.sql`, task lifecycle status vocabulary, deletion APIs, archival subsystem, privacy policy, retention duration, capability status, provider behavior, merge authority.
- MAY CHANGE IF NECESSARY: supporting design wording only, after task amendment.
- HUMAN REAUTHORIZATION REQUIRED: any destructive migration or actual deletion of persisted user/operator state; any new privacy/legal retention requirement.

## Decision authority

- Inherited roadmap authority: resolve the reviewed semantic-history gap in the operator-approved order using the smallest coherent MAPS_L mechanism.
- Owner may decide: the default core runtime retention/immutability contract and the smallest future implementation proof, provided no destructive migration or new retention-duration promise is made.
- Resolve internally first: whether current cascades are active behavior or latent schema mechanics; whether a soft-delete/archive lifecycle is justified now; whether database enforcement is necessary.
- Human escalation only if: implementation would delete existing data, require a privacy/legal retention choice, or introduce a materially broader archival product/lifecycle.

## Decision proposed for review

Adopt the following Lean contract:

1. **Canonical tasks are not hard-deleted through normal MAPS_L operation.** Once created, the canonical task row remains part of the local audit/history record.
2. **`task_events` rows are immutable once committed.** Corrections are represented by later semantic events, not UPDATE/DELETE of prior history.
3. **Current `ON DELETE CASCADE` clauses are not authority for a supported delete workflow.** They are latent referential-cleanup mechanics and must not be treated as permission to erase canonical history.
4. **No new `ARCHIVED` lifecycle state is introduced now.** `DONE`/`BLOCKED` already provide terminal task states; filtering/derived views can hide old work without deleting it.
5. **No forever/privacy promise is made.** If storage pressure, legal/privacy obligations, or operator-directed data disposal later require removal/redaction, that becomes a separately authorized retention/export/redaction design with explicit recovery/evidence rules.

This selects Slice 09 option 3 in practical terms: task deletion is forbidden once semantic history exists. Since normal task creation atomically appends `TASK_CREATED`, the common-case result is that canonical tasks are never hard-deleted.

## Why not the alternatives

- `events immutable only while task exists; task delete cascades them` — lets one parent delete erase the very audit history whose immutability is being protected.
- `events survive task deletion via tombstone/archive now` — requires a new identity/lifecycle/archive mechanism without a demonstrated need.
- `best-effort application append-only` — leaves direct SQL able to rewrite/delete history while other evidence tables are database-enforced immutable.

## Acceptance criteria

- [x] Current `task_events` write/update/delete behavior is described from accepted code/schema rather than assumed.
- [x] Parent-task deletion semantics are separated from event-row immutability.
- [x] One explicit default contract is chosen rather than leaving four incompatible interpretations active.
- [x] The choice avoids a new archive/tombstone lifecycle absent evidence.
- [x] Privacy/legal/data-disposal needs remain an explicit future authority boundary rather than being silently overruled by "retain forever" language.
- [x] Future implementation proof is bounded and mechanically discriminating.
- [x] No runtime/schema/test behavior changes in this design task.

## Verification and evidence

- Verification: direct inspection of accepted `runtime/state/schema.sql` and `runtime/state/base.py`; repository search for a public task-deletion API; compare with existing immutable lineage-table trigger patterns and PR #330 transaction evidence.
- Evidence to preserve: this task, companion design note, independent review evidence exact-head-bound to this design PR.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: accepted MAPS_L SQLite task state.
- Ordered procedure: design review first; only then shape a separate schema/test implementation.
- Failure branches: if review finds an existing supported hard-delete/retention contract, stop and reconcile rather than imposing this decision.
- Rollback / recovery: design-only; no persistent runtime mutation.
- Security / privacy controls: do not claim indefinite retention satisfies privacy/legal obligations; actual data disposal requires separate authority and design.
- External side effects: GitHub design records only.
- Effort limit: no archive service, retention scheduler, data migration, or generic event-sourcing framework.
- Approved reference: Slice 09 of the competitor borrow-integration log plus current accepted runtime/schema.
- Operational independence: `N/A — one-time architecture decision; any repeatable implementation receives its own task/test package.`
- Reproduction package: direct file inspection steps recorded in companion note.

## First future implementation proof, if design is approved

A separate implementation task should add only the minimum database guards and regressions needed to prove:

```text
create task
→ TASK_CREATED exists
→ direct UPDATE task_events rejected
→ direct DELETE task_events rejected
→ direct DELETE canonical task rejected
→ ordinary lifecycle transitions still append events successfully
```

Preferred minimum schema shape for that future task:

- `BEFORE UPDATE ON task_events` → reject;
- `BEFORE DELETE ON task_events` → reject;
- explicit `BEFORE DELETE ON tasks` → reject normal hard deletion.

Do not redesign all existing `ON DELETE CASCADE` foreign keys in the same tranche. The explicit task-delete guard should make their normal-operation deletion path unreachable; changing every FK would be a broader migration with little added proof.

## Stop / escalate

Stop if accepted runtime evidence reveals a real supported task hard-delete flow or if implementation requires deleting/migrating existing state. Do not infer a privacy/legal retention period.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- The key distinction is `append-only application API != database-enforced immutable history`.
- `ON DELETE CASCADE` is referential behavior, not by itself product/authority intent.
- A future explicit data-disposal mechanism should be designed from a real privacy/storage requirement, not prebuilt speculatively.

## Completion / handoff

- Completed: bounded retention/immutability contract shaped for independent review.
- Not completed: schema/test enforcement.
- Triage capture: no new product failure discovered; task resolves previously routed Slice 09 ambiguity.
- Reproduction package: inspect `task_events` definition and `_append_event()` in accepted `main`, verify absence of `delete_task()`, compare immutable trigger patterns.
- Current blocker: independent design review.
- Next eligible roadmap task: if approved, bounded task/event immutability implementation; afterward continue to remaining reviewed-gap sequence item(s).
- Human action required: none unless future work crosses destructive/privacy/legal authority.