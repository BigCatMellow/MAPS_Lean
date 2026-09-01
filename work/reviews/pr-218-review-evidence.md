# PR #218 review evidence — 6.21 slice 1: `maps flow review-record`

reviewer: maps-lean-luve
head_sha: 4ac45d6bdec77dbd7eb9e093251071228520a3bb
independent: true
summary: Independent code review by maps-lean-luve (did not author — vame did). `flow_review_record` is a pure composition over `store.record_review` plus exactly one added piece: an early deterministic `REVIEW_REDERIVATION_REQUIRED` preflight for `APPROVED` + `REDERIVED_AT_REVIEW`-bound subject + no re-derived refs, mirroring the deep `_validate_review_approval_conn` hook. No semantic change to `record_review` / `_validate_review_approval_conn` (neither file is in the diff). No new store primitive, no review lease, no schema change, verdict→status mapping untouched (owned by `record_review`). CAPABILITY_CHECKLIST.md 6.21 row stays IN PROGRESS — evidence text only, no status flip. `tests.test_flow_review` 23/23 green (foreground blocking); `tests.test_review_subject_binding` + `tests.test_runtime_review_hardening` 30/30 green; `runtime.smoke` exit 0. Own min-5 mutation: 8 mutations, 7 killed, 1 survivor (on the pre-existing `_open_review_for` helper, not PR-new code). VERDICT: APPROVE. 1 non-blocking observation. NB: head_sha rebound by coordinator to the post-rebase code commit (branch predated #217).

## Reviewed diff (against merge-base 0056640)

| File | Change |
|---|---|
| `runtime/flow_review.py` | +99 — new `flow_review_record` + `_review_by_id` helper |
| `runtime/cli.py` | +31 — `flow review-record` subparser + one dispatch block |
| `tests/test_flow_review.py` | +298 — `FlowReviewRecordTests` (13 methods) |
| `work/roadmaps/CAPABILITY_CHECKLIST.md` | +1/-1 — 6.21 evidence text, status unchanged (IN PROGRESS) |

`git diff 0056640..HEAD --name-only` contains no `runtime/state/review.py`, `runtime/state/review_binding.py`, or `runtime/state/schema.sql`.

## Dispatch criteria (verified)

### 1. Pure composition over `record_review`; NO semantic change — PASS
`record_review` (`review.py:107`) and `_validate_review_approval_conn` (`review_binding.py:496`) byte-identical to `origin/main` (not in diff). `flow_review_record` resolves the open review via pre-existing `_open_review_for`, runs the preflight, calls `store.record_review(..., rederived_artifact_refs=tuple(...) or None)`, surfaces `recorded.task["status"]` as `new_status`. Every real check (ownership, `READY_FOR_REVIEW`, submission, independence, criterion verification, approval hook, verdict→status) remains in the store primitive.

### 2. Early `REDERIVED_AT_REVIEW` preflight deterministic, not a raw hook error — PASS
Returned before any `record_review` call as a structured `MutationResult` with `failed_step="rederivation_preflight"`. Condition set exactly mirrors the hook (`review_binding.py:580-588`). `CHANGES_REQUESTED`/`BLOCKED` and `REVISION_BOUND`/`NON_CONSEQUENTIAL` subjects never hit it. Narrower hook errors (`REVIEW_REDERIVATION_MISMATCH`, `INVALID_REDERIVED_ARTIFACT_REF`) deliberately not duplicated, still flow through to the store.

### 3. No lease / store-primitive / schema — PASS
No lease/heartbeat/expiry code in the diff; `_review_by_id` is a pure list scan; no new `TaskStore` method; `schema.sql` untouched.

### 4. Verdict→status unchanged — PASS
Map lives in `record_review`, not in the diff. `flow_review_record` only reads back `recorded.task["status"]`.

### 5. NO checklist status flip — PASS
`| 6.21 | ... | IN PROGRESS |` on both sides; only evidence prose gains a sentence which itself states "6.21 stays IN PROGRESS".

### 6. Foreground unittest green — PASS
`python3 -m unittest tests.test_flow_review` → `Ran 23 tests OK` (blocking foreground). `tests.test_review_subject_binding tests.test_runtime_review_hardening` → `Ran 30 tests OK`.

### 7. `runtime.smoke` exit 0 — PASS
`{"ok": true}` / `0`.

### 8. Min-5 mutation (own) — PASS (7 killed / 8)

| # | Mutation | Result |
|---|----------|--------|
| M1 | preflight `verdict == "APPROVED"` guard removed | KILLED |
| M2 | `and not rederived_artifact_refs` inverted | KILLED |
| M3 | preflight matches `"REVISION_BOUND"` not `"REDERIVED_AT_REVIEW"` | KILLED |
| M4 | drop `rederived_artifact_refs=` passthrough | KILLED |
| M5 | preflight code → `"WRONG_CODE"` | KILLED |
| M6 | remove early `return` in preflight | KILLED |
| M8 | `_review_by_id`: `==` → `!=` | KILLED |
| M7 | `_open_review_for`: drop the `reviewer_id ==` filter | SURVIVED |

M7 survivor (non-blocking): `_open_review_for` is pre-existing code, not added by this PR. `idx_reviews_one_open` guarantees ≤1 open review per task and `record_review` re-checks ownership inside its own transaction, so correctness holds.

## Non-blocking observation
The preflight's failure payload embeds `dict(subject)` even on the fallback branch where the resolved open review is owned by a different reviewer — a non-owner sees the subject binding before `record_review` rejects with `NOT_REVIEW_OWNER`. Binding is low-sensitivity, path is narrow; purely a message-ordering nicety.

## Verdict: APPROVE
