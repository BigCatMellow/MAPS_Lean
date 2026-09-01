# PR #226 review evidence — 6.21 increment (a): flow review-start → review-record coherence + hardening

reviewer: maps-lean-luve
head_sha: ae7d51f41953470d319dcbdbab60d4331f3ae9e2
independent: true
summary: Independent code review by maps-lean-luve (did not author — vame did). `runtime/flow_review.py` +33/-8: (1) `flow_review_record`'s success return now carries a `next_step: {state: "REVIEW_RECORDED", reason}` block matching the `flow_start` / `flow_review_start` deterministic-flow family convention (both verified `{state, reason}` on success); (2) the post-`record_review` closed-review lookup switches from `_review_by_id(list_reviews, int(review["id"]))` — which dereferences a `review` handle that is `None` on the non-owner/no-open-review path — to `_latest_completed_review_for(list_reviews, reviewer_id)`, a newest-first scan that never touches `review`. Happy-path behaviour unchanged: the review just closed by `record_review` is the newest completed review for that reviewer (append-only, `ORDER BY id`), so old and new code resolve the same row. `record_review` / `_validate_review_approval_conn` / `schema.sql` not in the diff; no review lease, no release primitive, no store mutation, no column, no verdict→status change. CAPABILITY_CHECKLIST 6.21 stays IN PROGRESS (evidence text only). `tests.test_flow_review` 28/28 green (foreground blocking), `tests.test_flow_start` + `tests.test_review_subject_binding` 28/28 green, `runtime.smoke` exit 0. New `FlowReviewSequenceTests` (4 tests) exercise start→record coherence incl. a 2-round CHANGES_REQUESTED→APPROVED test that validates "latest completed" semantics. Own min-5 mutation on the changed logic: 6 killed / 7, M2 (drop the `reviewer_id` filter) is a genuine equivalent mutant — the `closed` lookup is only reached after `record_review` succeeds for `reviewer_id`, making that reviewer's review the newest completed one. Confirms vame's 6/7 + 1-equivalent report. VERDICT: APPROVE. No non-blocking issues. NB: head_sha rebound by coordinator to the post-rebase commit (branch predated #225–#227; rebase clean).

## Verification (rule 14)

### (1) `next_step` block matches the deterministic-flow family — PASS
- `flow_start.py:181` — `"next_step": {"state": "STOPPED_BEFORE_PROVIDER_SESSION", "reason": "..."}`.
- `flow_review.py::flow_review_start` — `"next_step": {"state": "STOPPED_BEFORE_REVIEW_VERDICT", "reason": "..."}`.
- New `flow_review_record` success return — `"next_step": {"state": "REVIEW_RECORDED", "reason": f"the task is now {new_status}; flow review-record does not record real-world outcomes (maps outcome-record) or dispatch follow-on work"}`.
Same `{state, reason}` shape, string state, success path only (`_failed(...)` early returns carry no `next_step` — consistent with `flow_review_start`). Mutations M4 (state literal) and M5 (drop `new_status`) killed.

### (2) latent `int(review["id"])`-on-`None` path genuinely closed — PASS
Base: `closed = _review_by_id(store.list_reviews(task_id), int(review["id"]))`; `review = _open_review_for(list_reviews, reviewer_id)` is `None` whenever the caller does not hold the open review. On that path `record_review` returns `NO_OPEN_REVIEW`/`NOT_REVIEW_OWNER` and the function returns at `_failed("record", recorded)` before the deref — but a TOCTOU between the pre-call `list_reviews` read and `record_review`'s own transaction leaves `int(None["id"])` → `TypeError` reachable in principle. New: `_latest_completed_review_for(store.list_reviews(task_id), reviewer_id)` scans `reversed(reviews)` for `completed_at is not None and reviewer_id == reviewer_id`; never references `review`. No happy-path change (append-only rows, `ORDER BY id`; the row `record_review` just closed is the highest-id review owned by `reviewer_id`). `test_second_round_review_resolves_the_latest_completed_review` proves the multi-round case. M1 (`completed_at is not None` → `is None`) and M3 (`reversed` → forward) killed.

### (3) module-level start→record e2e present and real — PASS
New `FlowReviewSequenceTests`, 4 tests: `test_revision_bound_start_then_record_is_coherent` (same review row `recorded["review"]["id"] == started["review"]["id"]` → `DONE`, `next_step.state == "REVIEW_RECORDED"`); `test_rederived_start_then_record_matching_refs_is_coherent`; `test_second_round_review_resolves_the_latest_completed_review` (round-2 review reported, not round 1); `test_rederived_start_then_record_mismatched_refs_rejected_by_store`. The existing `test_revision_bound_subject_approved_goes_done` gains 3 `next_step` assertions. All real (drive the real store, assert task status + row identity).

### (4) MUST NOT — PASS
`git diff --name-only`: `runtime/flow_review.py`, `tests/test_flow_review.py`, `work/roadmaps/CAPABILITY_CHECKLIST.md`. No `runtime/state/review.py`, no `review_binding.py`, no `schema.sql`. Two module-level helpers + the return-dict shape — no review lease/heartbeat, no release primitive, no `store.*` write, no column, no verdict→status remapping, no `record_review` / `_validate_review_approval_conn` edit.

### (5) NO checklist status flip — PASS
6.21 row `| ... | IN PROGRESS |` on both sides; only the evidence prose gains the "Coherence/hardening increment (…§3)" sentence, which ends "6.21 stays IN PROGRESS".

### (6) tests green + smoke + own min-5 mutation — PASS
`python3 -m unittest tests.test_flow_review` → `Ran 28 tests OK`. `tests.test_flow_start tests.test_review_subject_binding` → `Ran 28 tests OK`. `runtime.smoke` exit 0.

| # | Mutation | Result |
|---|----------|--------|
| M1 | `_latest_completed_review_for`: `completed_at is not None` → `is None` | KILLED |
| M2 | drop `and review.get("reviewer_id") == reviewer_id` | SURVIVED — equivalent |
| M3 | `reversed(reviews)` → forward | KILLED |
| M4 | `next_step.state` `"REVIEW_RECORDED"` → `"RECORDED_REVIEW"` | KILLED |
| M5 | drop `new_status` interpolation from `next_step.reason` | KILLED |
| M6 | `new_status = recorded.task.get("status")` → `.get("state")` | KILLED |
| M7 | `"review": dict(closed) if closed is not None else None` → `"review": None` | KILLED |

6 killed / 7. M2 is a true equivalent mutant: the `closed` lookup is only reached after `store.record_review(...)` returned `ok` for `reviewer_id`, so that row is the newest completed review on the task; `reversed(reviews)` finds it first with or without the filter (`idx_reviews_one_open` guarantees no concurrently-closed newer row by another identity). Matches vame's 6/7 + 1-equivalent — confirmed.

## Verdict: APPROVE
