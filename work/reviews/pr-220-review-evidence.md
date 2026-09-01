# PR #220 review evidence — flow_review_record: preflight resolves only the caller's own open review

reviewer: maps-lean-gela
head_sha: df3c96e2318c075462a2523049703ae0b8afdaad
independent: true
summary: Independent review by maps-lean-gela (did not author — vame did; gela authored the #218 design note but not this follow-up impl). #218 review follow-up (non-blocking, luve). 3 files: runtime/flow_review.py, tests/test_flow_review.py, work/roadmaps/CAPABILITY_CHECKLIST.md. The change: flow_review_record's rederivation preflight previously fell back to resolving ANY open review on the task when the caller did not hold one, so a non-owner's failure payload embedded dict(subject) — leaking the bound review subject, freshness_mode, artifact_refs — before record_review would reject with NOT_REVIEW_OWNER. After: `_open_review_for(store.list_reviews(task_id), reviewer_id)` resolves ONLY the caller's own open review; the preflight runs only inside `if review is not None:`; a non-owner falls straight through to record_review (NO_OPEN_REVIEW / NOT_REVIEW_OWNER, failed_step "record"). All 5 verification points PASS. No record_review / _validate_review_approval_conn change (not in diff). REDERIVED_AT_REVIEW deterministic preflight byte-identical for the legit owner path, regression-covered. verdict→status unchanged. No checklist status flip — 6.21 stays IN PROGRESS. Foreground `unittest tests.test_flow_review tests.test_review_subject_binding tests.test_flow_start` → Ran 52 tests, OK. `runtime.smoke` → {"ok": true} exit 0. Own mutation pass: 7 mutations, 7 killed (one equivalent mutant identified + replaced). VERDICT: APPROVE. 2 non-blocking observations, neither gates merge. NB: head_sha rebound by coordinator to the post-rebase code commit (branch predated #217–#219).

## Verification

### V1 — no record_review / _validate_review_approval_conn semantic change — PASS
Diff = runtime/flow_review.py, tests/test_flow_review.py, work/roadmaps/CAPABILITY_CHECKLIST.md only. runtime/state/review.py and review_binding.py not in the diff. All enforcement (ownership, reviewability, independence, criterion verification, review-binding approval hook, verdict→status) unchanged in the store primitive.

### V2 — REDERIVED_AT_REVIEW deterministic preflight still fires for the legit owner (regression vs #218) — PASS
Preflight condition after the change is the identical 4-clause test as #218 (`verdict APPROVED` and `subject is not None` and `freshness_mode == "REDERIVED_AT_REVIEW"` and `not rederived_artifact_refs` → `_failed("rederivation_preflight", MutationResult(False, "REVIEW_REDERIVATION_REQUIRED", …, dict(subject)))`). Only structural change: now nested under `if review is not None:` where `review` is resolved with the caller's own `reviewer_id`. For the owner, `_open_review_for` returns their review, branch entered as before. Covered by test_rederived_subject_approved_without_refs_fails_early, test_rederived_subject_approved_with_matching_refs_goes_done, test_blocked_on_rederived_subject_needs_no_refs, test_cli_flow_review_record_end_to_end.

### V3 — verdict→status unchanged — PASS
Not touched. record_review maps APPROVED→DONE, CHANGES_REQUESTED→CHANGES_REQUESTED, BLOCKED→BLOCKED (not in diff).

### V4 — no checklist status flip (6.21 stays IN PROGRESS) — PASS
6.21 cell unchanged both sides; the change appends one "Follow-up (#218 review, non-blocking)" sentence accurately describing the code. No other row touched.

### V5 — foreground unittest green; smoke 0 — PASS
`python3 -m unittest tests.test_flow_review tests.test_review_subject_binding tests.test_flow_start` → Ran 52 tests OK. `python3 -m runtime.smoke` → {"ok": true}, exit 0.

### Behavioural delta (the security intent)
Old: a non-owner calling flow_review_record against a task with someone else's open REDERIVED_AT_REVIEW review + APPROVED + no refs got `rederivation_preflight` / `REVIEW_REDERIVATION_REQUIRED` with `dict(subject)` embedded (leak of run_id, artifact_refs, freshness_mode, task_revision). New: non-owner always falls to record_review → NO_OPEN_REVIEW / NOT_REVIEW_OWNER, failed_step "record", no subject data. Strictly an information-disclosure fix + code simplification (any-open-review fallback removed; store.list_reviews called once). New test test_non_owner_of_rederived_review_sees_no_subject asserts the freshness mode + artifact SHA are absent from the serialized result.

## Mutation testing (min-5) — 7 mutations, 7 killed

| # | Mutation | Result |
|---|---|---|
| M1 | `if review is not None:` → `if review is None:` | KILLED |
| M2 | resolve preflight review via the removed any-open-review fallback | KILLED (test_non_owner_of_rederived_review_sees_no_subject) |
| M3 | `verdict … == "APPROVED"` → `!=` | KILLED |
| M4 | `freshness_mode == "REDERIVED_AT_REVIEW"` → `!=` | KILLED |
| M5 | `and not rederived_artifact_refs` → `and rederived_artifact_refs` | KILLED |
| M6 | `and subject is not None` → `and subject is None` | KILLED |
| M7 | `_failed("rederivation_preflight", …)` → `_failed("record", …)` | KILLED |

Equivalent-mutant note: `_open_review_for(…, reviewer_id)` → `_open_review_for(…, "")` SURVIVES but is a true equivalent mutant — no reviews row can have `reviewer_id == ""` (claim_review rejects empty reviewer_id), so it is always None and the or-chain collapses to the original. Replaced with M2, which restores the actual pre-#220 behaviour and is killed.

## Non-blocking observations
1. `_open_review_for` is now the single resolver for both flow_review_start and flow_review_record — load-bearing for two flows now.
2. The "caller holds no review, nothing open" failure now returns record_review's message `"no open review exists"` rather than the flow's former task-id-specific message. Tests assert `code`, not message.

## Verdict: APPROVE
