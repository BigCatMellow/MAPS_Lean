reviewer: maps-lean-nava
head_sha: 592d1f9b7d8cfb78597fa8feab7a549695f4bfd8
independent: true
summary: APPROVE — schema (append-only release_checks with correct triggers/FKs/CHECKs), ReleaseCheckMixin, and the flow_release_check composition are all correct (every evaluator return-key reference verified against acquisition_evidence.py / benchmark_results.py; advisory-only semantics proven; no MUST-NOT violated; 6.21 stays IN PROGRESS); round-1 REQUEST_CHANGES found two non-equivalent mutation survivors (M3 untested FAIL-smoke -> BLOCKED path, M6 untested RELEASE_CHECK_TASK_MISMATCH branch), both closed by the delta with dedicated tests and re-verified KILLED; test_flow_release_check 19/19, test_state_store 15/15, smoke 0.

# PR #244 review evidence — 6.21 `maps flow release-check` impl

## Verified correct (round 1, unchanged by the delta)

| Area | Result |
|---|---|
| **Schema (`release_checks`)** | Append-only (`trg_release_checks_no_update` / `_no_delete`), `id` AUTOINCREMENT PK, FK `task_id -> tasks` / `review_id -> reviews` (ON DELETE CASCADE), CHECK on all three state enums, `input_evidence_refs` JSON default `[]`, `summary_snapshot` NOT NULL, index `(task_id, review_id, id)`. `test_state_store` 15/15 with the mixin in the MRO. |
| **`ReleaseCheckMixin`** | `record_release_check` validates then does FK/cross-task checks in one `BEGIN IMMEDIATE` txn (`TASK_NOT_FOUND` / `REVIEW_NOT_FOUND` / `RELEASE_CHECK_TASK_MISMATCH`), appends, fires `RELEASE_CHECK_RECORDED`. `get_/latest_/list_release_check(s)`. `_decode_release_check` JSON-decodes the two JSON columns. |
| **`flow_release_check` composition** | design §3 steps 1-4. Every evaluator return-key reference verified: `acq_report["benchmark_property_fragments"]["release.acquisition_paths_verified"]["state"]` (PASS/FAIL/UNKNOWN via `_property_fragment`), `report_id`, `manifest_sha256`; `smoke_report["benchmark_status"]` (COMPLETE/FAIL/INCOMPLETE), `result_evidence_ref`. `composite = "BLOCKED" if artifact_identity_state == "FAIL" or release_smoke_state == "FAIL" else "READY_FOR_OPERATOR_VERDICT"`. `next_step.state == "STOPPED_BEFORE_RELEASE_VERDICT"`. `AcquisitionEvidenceError` / `BenchmarkResultError` caught -> `INVALID_ACQUISITION_EVIDENCE` / `INVALID_BENCHMARK_EVIDENCE`. |
| **Advisory-only** | `test_blocked_composite_does_not_prevent_review_approval` — a `BLOCKED` release check does not block a later `APPROVED` verdict; the row is unchanged. No `record_review` / `_validate_review_approval_conn` call or modification (grep -> docstring/comment/checklist prose only). |
| **MUST-NOT** | No acquisition/download/install; no benchmark execution; no verdict recorded; no `recover` impl; no approval gate. Follows the operator-answered §6 batch (#243). |
| **CLI** | `maps flow release-check TASK --recorded-by R [--evidence-json PATH] [--operator-ack-ref REF]`; `INVALID_EVIDENCE_JSON` on a bad bundle. `test_cli_flow_release_check_*` cover happy + bad path. |
| **Checklist** | 6.21 stays `IN PROGRESS`; one evidence clause added; "Recover flow remains unimplemented" retained. Delta corrected the "keyed `(task_id, review_id)`" wording to "`id`-keyed with a `(task_id, review_id, id)` index". |

## Mutation testing — round 1: 5/8 killed + 2 survivors + 1 borderline; delta: both survivors closed

Round-1 survivors and their delta fixes (each re-verified KILLED by this reviewer on the delta):

| # | Mutation | Round 1 | Delta fix | Re-run |
|---|----------|---------|-----------|--------|
| M3 | drop `or release_smoke_state == "FAIL"` from the composite | SURVIVED | `test_failing_release_smoke_blocks_with_passing_artifact_identity` — passing `acquisition` + a benchmark bundle with a forced BLOCKER `FAIL` (`benchmark_status == "FAIL"`), asserts `release_smoke.state == "FAIL"` and `composite == "BLOCKED"` with `artifact_identity.state == "PASS"` | **KILLED** (`FAILED (failures=1)`) |
| M6 | drop the `review["task_id"] != task_id` guard in `record_release_check` | SURVIVED | `test_store_record_release_check_rejects_cross_task_review` — `record_release_check(task_B, review_of_task_A)` -> `RELEASE_CHECK_TASK_MISMATCH`, nothing written | **KILLED** (`FAILED (failures=1)`) |
| M7 | drop the `_COMPOSITE_STATES` re-validation | SURVIVED (near-equivalent w/ schema CHECK) | `test_store_record_release_check_rejects_bad_composite_state` added (bonus) | KILLED |

M1 (or->and), M2 (never BLOCKED), M4 (invert review-type guard), M5 (drop bound-subject guard) — all KILLED in round 1.

Round-1 killed set also stands on the delta (delta is test-only, no `runtime/` change).

## Merge-prep

**No rebase needed** — corrected from the round-1 note: `891045e` (#241) is the current `origin/main` HEAD; `5d4a9f2` (#242) is the commit below it, an ancestor. The branch is clean on the main tip. `_ready_for_review` was also given distinct per-task output paths in the delta (needed once the M6 test creates a 2nd task; an output-scope-conflict fix, not a behaviour change).

## Verdict

APPROVE.
