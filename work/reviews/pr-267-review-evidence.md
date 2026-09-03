reviewer: independent-review-agent (session 23, PR #267)
head_sha: 3f0c109005f2299c8904fb92305442e1aa64bf46
independent: true
summary: Independent review of 6.21 slice 3b (composite==BLOCKED hard-blocks OPERATOR_VISIBLE_RELEASE_CHECK approval) — diff, spec conformance, 5 own mutations, adversarial fail-closed analysis. APPROVE. No blocking findings. The one non-blocking finding (stale next_step.reason string, Finding 10) was fixed by the impl agent in 3f0c109 and re-reviewed (Finding 12).

## Findings

1. **Files changed match the spec boundary exactly.** `git diff --stat origin/main...HEAD` shows only: `runtime/state/review_binding.py` (+22), `runtime/flow_release_check.py` (docstring, +7/-1), `runtime/state/schema.sql` (comment, +7/-3), `tests/test_flow_release_check.py` (+147), `work/roadmaps/CAPABILITY_CHECKLIST.md` (+1/-1). No stray files. PASS.

2. **schema.sql — no DDL change.** `git diff origin/main...HEAD -- runtime/state/schema.sql` touches only the block comment above `CREATE TABLE ... release_checks` (L845-854); the DDL, triggers and index are untouched. Sub-decision (c) confirmed NOT implemented — no `task_revision` / `submission_count` columns added. PASS.

3. **CAPABILITY_CHECKLIST.md — no status flip.** Row 6.21 still reads `IN PROGRESS`; the change is an appended evidence clause describing the 3b gate. No DONE flip anywhere in the diff. PASS.

4. **Gate placement (`runtime/state/review_binding.py:596-616`).** New block is the last check in `_validate_review_approval_conn`, after the bound-subject / run-manifest / criterion-claim / rederivation checks and immediately before `return None` (L617). Guarded by `str(task["review_required"]).upper() == "OPERATOR_VISIBLE_RELEASE_CHECK"` so it is reached only for that review type. It uses the passed `conn` with raw SQL and never calls `self.` store methods — consistent with the rest of the hook. PASS.

5. **SQL matches spec §3 verbatim** (`review_binding.py:600-604`): `SELECT composite_state, operator_ack_ref FROM release_checks WHERE task_id = ? AND review_id = ? ORDER BY id DESC LIMIT 1`, params `(task["task_id"], review["id"])`. `review` is the single open review row selected by `record_review` (`review.py:132-139`, `WHERE task_id = ? AND completed_at IS NULL`, one-row fetch; `reviews` has a unique constraint on the open review — `claim_review` catches `sqlite3.IntegrityError`). `flow_release_check` writes `release_checks.review_id` from the same open-review resolution (`flow_release_check.py:89-100`, `_open_release_review`), so `review["id"]` here is the same id. `latest_release_check` (`release_check.py:188-203`) uses the identical `ORDER BY id DESC LIMIT 1`. Ordering agreement confirmed. PASS.

6. **Two refusal codes exactly per §3** (`review_binding.py:605-616`): `RELEASE_CHECK_REQUIRED` when `row is None`; `RELEASE_CHECK_COMPOSITE_BLOCKED` when `row["composite_state"] == "BLOCKED" and not (row["operator_ack_ref"] or "").strip()`. Empty/whitespace check is the exact §3 form. PASS.

7. **Sub-decisions resolved per §3′ recommendations, no route-back needed.** (a) no row → refuse (`RELEASE_CHECK_REQUIRED`), implemented as refuse — matches recommendation. (b) non-empty `operator_ack_ref` on the latest row overrides the block — implemented. (c) stale-check DEFERRED — not implemented, no schema columns added. None resolved in the directions (§5) that would require an operator question. PASS.

8. **Tests (`tests/test_flow_release_check.py`).** The advisory test `test_blocked_composite_does_not_prevent_review_approval` is INVERTED (renamed to `test_unacked_blocked_composite_refuses_review_approval`, L269), not deleted; it now asserts `RELEASE_CHECK_COMPOSITE_BLOCKED` and task still `READY_FOR_REVIEW`. New tests read in full and each exercises its named behaviour:
   - `test_acked_blocked_composite_allows_review_approval` (L297): BLOCKED row recorded with `operator_ack_ref="operator-note:..."`, APPROVED succeeds → `DONE`, release row unchanged.
   - `test_no_release_check_row_refuses_review_approval` (L331): no release check recorded → `RELEASE_CHECK_REQUIRED`, task stays `READY_FOR_REVIEW`.
   - `test_ready_release_check_allows_review_approval` (L347): `READY_FOR_OPERATOR_VERDICT` composite → APPROVED → `DONE`.
   - `test_rerun_blocked_to_ready_unblocks_review_approval` (L368): first run BLOCKED → APPROVED refused; second run READY (latest by id) → APPROVED → `DONE`.
   - `test_gate_does_not_fire_for_non_release_review_types` (L414): `INDEPENDENT_REVIEW` and `OWNER_CHECK` tasks with no release_checks row → APPROVED → `DONE`.
   PASS.

9. **No other fixtures affected.** `grep -rn OPERATOR_VISIBLE_RELEASE_CHECK tests/` → hits only in `tests/test_flow_release_check.py`. No pre-existing `record_review(APPROVED)` fixture elsewhere uses that review type, so nothing needed a "record a READY check first" fix. PASS.

10. **NON-BLOCKING — stale operator-facing string.** `runtime/flow_release_check.py:222` still emits, in `next_step.reason`, `"composite={composite_state} (BLOCKED is advisory this slice — it does not gate record_review)"`, and `tests/test_flow_release_check.py:267` still asserts `"BLOCKED is advisory"` on that string. After this PR the statement is false for an un-acked BLOCKED row. Spec §3 scoped `flow_release_check.py` to "docstring clause only", so this is within the stated file boundary, but it leaves misleading guidance in the live flow output. Recommend a follow-up one-line correction. Not blocking — the gate itself is correct and lives in the store hook, not the flow.

12. **Finding 10 string fix reviewed (delta `1c216cb..3f0c109`, trailing commit `3f0c109`).** 2-line change: `runtime/flow_release_check.py` `next_step.reason` now reads `"composite={composite_state} (an un-acknowledged BLOCKED composite hard-blocks record_review APPROVED — a non-empty operator_ack_ref on the latest release check is the override)"`, and `tests/test_flow_release_check.py:268` (`test_mismatched_artifact_ref_blocks`) now asserts `"hard-blocks record_review APPROVED"` instead of `"BLOCKED is advisory"`. The new string is accurate for the shipped gate and the test asserts the new string. Verified: `python3 -m unittest tests.test_flow_release_check.FlowReleaseCheckTests.{test_mismatched_artifact_ref_blocks,test_unacked_blocked_composite_refuses_review_approval,test_acked_blocked_composite_allows_review_approval}` → 3 passed; CI `test` on `3f0c109` GREEN (run 33700071016). Finding 10 resolved; no new issue. This evidence file re-pointed to `head_sha 3f0c109`.

11. **OBSERVATION (pre-existing, not introduced here).** The `operator_ack_ref` override carries no operator-identity enforcement — any caller of `maps flow release-check --operator-ack-ref <ref>` sets it. This is a property of #244 that spec §3′(b) explicitly accepts as the recorded, append-only, auditable escape hatch ("no `--force`, no config flag"). Noted for completeness; nothing for this PR to change.

## Own mutation testing (gate in `runtime/state/review_binding.py`, distinct from §3 M1–M6)

Baseline: the 6 gate tests green in 48s; `python3 -m runtime.smoke` → exit 0.

| # | Mutation | Expected | Result |
|---|----------|----------|--------|
| M-A | composite literal case: `== "BLOCKED"` → `== "blocked"` (stored value is upper-case) | un-acked BLOCKED no longer refused | FAIL caught (`test_unacked_blocked...`, `test_rerun_blocked...`) — 2 failures |
| M-B | invert composite equality: `== "BLOCKED"` → `!= "BLOCKED"` | READY rows wrongly blocked | FAIL caught |
| M-C | `and` → `or` in the block condition (ack no longer able to override; READY also blocked) | acked-BLOCKED / READY approvals wrongly refused | FAIL caught |
| M-D | wrong code on the BLOCKED path: return `RELEASE_CHECK_REQUIRED` instead of `RELEASE_CHECK_COMPOSITE_BLOCKED` | code assertion mismatch | FAIL caught |
| M-E | `review_id` param → constant `-1` (latest-row lookup never matches) | every OPERATOR_VISIBLE_RELEASE_CHECK approval refused as REQUIRED | FAIL caught |

Observed failure counts across the 6 gate tests: M-A 2, M-B 3, M-C 3, M-D 2, M-E 4. Every mutation produced ≥1 test failure; all reverted (`git checkout -- runtime/state/review_binding.py`), tree confirmed clean before commit.

## Adversarial — can an un-acked BLOCKED latest row still reach APPROVED?

- **Fail-closed for the review type.** For `OPERATOR_VISIBLE_RELEASE_CHECK`, `_requires_bound_subject_conn` is `True` (`review_binding.py:68`), so a missing review subject returns `REVIEW_SUBJECT_REQUIRED` earlier. The only pre-gate `return None` (subject absent AND not required) is unreachable for this type, so the gate is always evaluated once execution reaches the tail of the hook. No earlier `return None` short-circuits it.
- **Stale / cross-review rows.** The gate keys on the current open review's id. Rows written under a prior, now-completed review are not matched → `RELEASE_CHECK_REQUIRED` (fail closed), not a silent pass.
- **A newer READY row.** Unblocks by design (§3′(c) DEFER) — it requires a real re-run of `flow_release_check` with passing caller-supplied evidence and is the intended clear path, not a bypass.
- **Direct store call.** The gate is inside `record_review` → `_validate_review_approval_conn`, so `store.record_review(APPROVED)` is gated even without going through `flow_review_record`.
- **Whitespace ack.** `.strip()` on `(operator_ack_ref or "")` defeats a `"   "` ack.
- No path found for an un-acknowledged BLOCKED latest row to reach APPROVED.

## Verification runs (fresh, at HEAD 1c216cb)

- Targeted gate tests (`tests.test_flow_release_check` 6 gate methods): 6 passed.
- Earlier full-module run of `tests.test_flow_release_check`: 24 passed (`OK`).
- `tests.test_flow_review` + `tests.test_review_subject_binding` + `tests.test_runtime_review_hardening`: 58 passed (`OK`). (Note: the task's named modules `tests.test_review_binding` / `tests.test_flow_review_record` do not exist in the tree; the review-binding hook and review-record flow are covered by these modules and `tests.test_flow_release_check`.)
- `python3 -m runtime.smoke`: exit 0 (`"ok": true`, task lifecycle `DONE`).
- Full suite: CI `test` check on PR #267 (= `python3 -m unittest discover -s tests`) is GREEN — GitHub Actions run 33698500188, pass, 1m25s. Cited as the authoritative full-suite result.

## Disposition

**APPROVE.** The gate is the exact ~8-line check scoped in §3, positioned and wired as specified, with the two refusal codes, correct sub-decision resolution (a=refuse, b=ack-overrides, c=deferred), an inverted advisory test plus five new tests that each exercise their named behaviour, comment/docstring/checklist updates only, no DDL, no CLI change, no status flip. All five independent mutations are caught; adversarial analysis finds no path for an un-acked BLOCKED release check to reach APPROVED. The one non-blocking finding (stale `next_step.reason` string) was fixed by the impl agent in `3f0c109` and re-reviewed (Finding 12); this evidence file is pointed at that head. CI `test` on PR #267 is green at `3f0c109`.
