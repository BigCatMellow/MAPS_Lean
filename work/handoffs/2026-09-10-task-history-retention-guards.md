# Handoff: canonical task/history retention guards

- From: ChatGPT orchestration/operator lane that authored PR #339
- To: fresh independent reviewer / next orchestration chat
- Task: [`../tasks/task-history-retention-guards.md`](../tasks/task-history-retention-guards.md)
- Status: implementation complete; exact-head Runtime green; fresh independent implementation review still required
- Active implementation PR: #339 — `Enforce canonical task history retention`
- Parent design PR: #338 — `Design canonical task/history retention`

## What is true now

- VERIFIED: PR #338 design was independently APPROVED against exact design head `3a3d46d0da6f8a8c4b98b6da6bc97ef5f5d86484`.
- VERIFIED: independent design evidence is `work/reviews/pr-338-review-evidence.md`, evidence-only commit `bedb6533f3ba5390d91e615fb1c56452496cab74`; its `review-evidence` run #789 passed.
- VERIFIED: PR #338 remains open and unmerged; current tip is the evidence-only commit `bedb6533f3ba5390d91e615fb1c56452496cab74`.
- VERIFIED: PR #339 is stacked directly on that #338 evidence tip.
- VERIFIED: the final review-candidate implementation head for #339 is `9689cefbfadea403a5418c95336a3e64bd3be470`.
- VERIFIED: Runtime stack tests #1654 completed successfully on exact head `9689cefbfadea403a5418c95336a3e64bd3be470`.
- VERIFIED: PR #339 is open, unmerged, non-draft, and currently mergeable.
- VERIFIED: the `review-evidence` run on #339 currently fails because no independent implementation review-evidence file has been added yet; this is the expected next gate, not evidence of a runtime failure.
- UNKNOWN / NOT YET PROVEN: whether the implementation passes fresh independent review. The authoring lane must not self-certify this.

## Work completed

The independently approved first enforcement tranche was implemented and no broader retention architecture was added.

### Runtime/schema change

`runtime/state/schema.sql` adds exactly three SQLite triggers, +23/-0:

1. `BEFORE UPDATE ON task_events` → abort `task events are immutable`;
2. `BEFORE DELETE ON task_events` → abort `task events are immutable`;
3. `BEFORE DELETE ON tasks` → abort `canonical tasks cannot be hard-deleted`.

Existing `ON DELETE CASCADE` declarations are untouched. The explicit parent-task no-delete trigger owns the normal canonical-task retention rule; event triggers own committed event-row integrity.

### Regression proof

`tests/test_task_history_retention.py` proves:

- fresh task creation produces `TASK_CREATED`;
- direct SQL UPDATE of a committed `task_events` row is rejected;
- direct SQL DELETE of a committed `task_events` row is rejected;
- direct SQL DELETE of the canonical task is rejected;
- rejected mutations leave task/history intact;
- normal shaping → READY → claim still appends the existing canonical event sequence, including `TASK_POLICY_UPDATED`, `TASK_CONTRACT_UPDATED`, `TASK_PROMOTED_READY`, and `TASK_CLAIMED`.

### CI-caught assumption repair

An earlier test expectation omitted the existing `TASK_POLICY_UPDATED` event. Runtime #1650 caught that expectation error; the three retention-guard assertions themselves passed. The correction changed only the expected normal event sequence, not runtime behavior. Runtime #1651 passed after that correction.

Per `AGENTS.md` / Repair and Learning, the wrong assumption was captured durably as DRIFT:

- [`../coordination/FRICTION_LOG.md`](../coordination/FRICTION_LOG.md) — append-only entry;
- [`../notes/2026-09-10-task-history-event-sequence-assumption-repair.md`](../notes/2026-09-10-task-history-event-sequence-assumption-repair.md) — repair record.

The final exact-head Runtime proof is #1654 on `9689cefbfadea403a5418c95336a3e64bd3be470`.

## Work not completed

- Fresh independent implementation review of PR #339.
- Independent review-evidence file for #339 bound to the exact reviewed implementation head.
- Passing #339 `review-evidence` workflow after that independent evidence commit.
- Merge of #338 or #339.
- Any archive/tombstone/purge/redaction/privacy/legal retention design or implementation.

## Decisions and constraints

The approved contract is intentionally narrow:

```text
create canonical task
→ TASK_CREATED commits atomically
→ committed task_events cannot UPDATE/DELETE
→ canonical task cannot hard-delete
→ ordinary lifecycle writes continue by appending later events
```

Do not widen this tranche into:

- `ARCHIVED` or another lifecycle state;
- tombstones;
- archive service;
- purge/redaction machinery;
- retention scheduler/duration;
- broad FK rewrites;
- legal/privacy/forever-retention policy;
- provider/harness/recovery changes;
- capability or authority changes.

PR #330 proves same-transaction task-state/event atomicity only. It does **not** prove permanent task-event immutability or retention; do not collapse those claims.

## Merge authority for this handoff

- Coordinator/merge seat: none granted by this handoff.
- PR #338: independently APPROVED but still open/unmerged.
- PR #339: **not yet independently reviewed**, therefore not approved for merge.
- Any merge to `main` must obey current `AGENTS.md`, including mandatory `scripts/opcmd_merge.py` operator-authorization gate. This handoff grants no merge authority.

## Current blocker / risk

- Only current gate: fresh independent review of #339.
- Reviewer must verify that direct canonical-task deletion fails because of `trg_tasks_no_delete`, not merely because a child cascade reaches `trg_task_events_no_delete`.
- Reviewer must verify the CI repair changed only the test expectation/process evidence, not runtime behavior.
- Reviewer must verify existing `ON DELETE CASCADE` clauses remain unchanged and no broader retention mechanism entered the implementation.

## Working state

- #339 substantive/final review candidate: `9689cefbfadea403a5418c95336a3e64bd3be470`.
- #339 base: #338 evidence tip `bedb6533f3ba5390d91e615fb1c56452496cab74`.
- Delta from that base at the review candidate: 5 files, 258 additions, 0 deletions.
- Schema delta: +23/-0 only.
- Last verification: Runtime stack tests #1654 — SUCCESS on exact head `9689cefbfadea403a5418c95336a3e64bd3be470`.
- Known runtime failures: none on final review candidate.
- Expected non-runtime check state: #339 `review-evidence` is red until a valid independent evidence file exists.

## Next action

1. In a **fresh independent chat/lane**, read repository root `AGENTS.md`, this handoff, PR #338 review evidence, the implementation task, and PR #339 exact delta at `9689cefbfadea403a5418c95336a3e64bd3be470`; perform only the bounded implementation review.
2. If APPROVED, create the required independent `work/reviews/pr-339-review-evidence.md` bound to the exact reviewed code head and let `review-evidence` verify it.
3. Do not merge unless separately authorized by the human operator under `scripts/opcmd_merge.py`. If/when merge authority is granted, integrate #338 before #339 or otherwise preserve the stacked dependency exactly.

## Do not redo / do not assume

- Do not redo the #338 design decision; it already passed fresh independent review.
- Do not re-investigate whether normal event writes are application-append-only or whether task creation atomically creates `TASK_CREATED`; those were established by the approved design review.
- Do not treat PR #330 as permanent immutability evidence.
- Do not treat the current red #339 `review-evidence` check as a runtime regression; it is missing-review evidence by design.
- Do not self-review #339 from the authoring lane.
- Do not add more retention architecture merely because hard deletion is now blocked. Future disposal/archival/privacy requirements require separately authorized design.
- Do not alter the exact implementation head before review unless a real defect is found. Any substantive change invalidates exact-head review assumptions and needs fresh Runtime verification/review.

## Evidence / paths

- PR #338 — design: `https://github.com/BigCatMellow/MAPS_Lean/pull/338`
- PR #339 — implementation: `https://github.com/BigCatMellow/MAPS_Lean/pull/339`
- Design task: [`../tasks/task-history-retention-design.md`](../tasks/task-history-retention-design.md)
- Implementation task: [`../tasks/task-history-retention-guards.md`](../tasks/task-history-retention-guards.md)
- Design review evidence: [`../reviews/pr-338-review-evidence.md`](../reviews/pr-338-review-evidence.md)
- Design note: [`../notes/2026-09-10-task-history-retention-design.md`](../notes/2026-09-10-task-history-retention-design.md)
- CI repair note: [`../notes/2026-09-10-task-history-event-sequence-assumption-repair.md`](../notes/2026-09-10-task-history-event-sequence-assumption-repair.md)
- Runtime/schema: `runtime/state/schema.sql`
- Regression: `tests/test_task_history_retention.py`

## Fresh-chat resume instruction

Use this as the compact continuation prompt:

> Read and follow `BigCatMellow/MAPS_Lean` root `AGENTS.md`, then read `work/handoffs/2026-09-10-task-history-retention-guards.md` from branch `handoff/task-history-retention-guards-2026-09-10`. Recover live GitHub state and continue from the exact next gate only. Do not redo completed design/implementation work, widen scope, self-certify independent review, or merge without explicit operator authorization.
