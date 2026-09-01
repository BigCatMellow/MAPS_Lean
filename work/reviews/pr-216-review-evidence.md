# PR #216 review evidence — Scoping + design pass on trajectory-#12 next-3 items #2 (6.21) and #3 (L6)

reviewer: maps-lean-nava
head_sha: 6f5da71b3b8172e2af3a925491de3f32d59292dc
independent: true
summary: APPROVE — verification-review of 2 design/scoping notes. The L6-BLOCKED verdict is correct against merged code (`HarnessService` constructed only at `runtime/recovery/production.py:419` inside the ask-#1 `--enforce-canonical-run` opt-in; neither `create_run_manifest` caller — `flow_start.py:139`, `integrity/cli.py:117` — has a service in scope, zero harness refs). The trajectory-#12 §5 "L6 independent" error is explicitly recorded as a correction and flagged for check-#13 (original #214 note correctly left unedited as historical record). The 6.21 `REDERIVED_AT_REVIEW` CLI gap is a real deterministic-composition gap (store primitive complete, CLI surface missing — `maps review-record APPROVED` deterministically fails `REVIEW_REDERIVATION_REQUIRED` on such a task). The slice needs no new authority/schema and is ask-#1-independent. Deferral rationale for recover/release/handoff is sound (no review lease exists; release = new operator-visible surface; handoff = provider launch, which `flow start` deliberately excludes). Diff is work/notes/ only; `runtime.smoke` exit 0. Two non-blocking citation nits.

## Criteria

| # | Criterion | Result |
|---|-----------|--------|
| 1 | L6-BLOCKED verdict: `HarnessService` constructed in exactly ONE production place, reachable only via `--enforce-canonical-run`; neither `create_run_manifest` caller has one in scope | PASS. `/usr/bin/grep -rn "HarnessService(" runtime/` (excl. tests) → one real constructor, `production.py:419` `return HarnessService([adapter], hooks=registry)`. `build_canonical_harness_service` invoked only at `production.py:513` inside `if harness_project_id is not None:` (`:498` `harness_service = None`). `harness_project_id` surfaces only as `maps recovery-tick --enforce-canonical-run --harness-project-id`. `create_run_manifest` production callers `flow_start.py:139` and `integrity/cli.py:117` — `/usr/bin/grep -ni harness` in both → zero hits. `harness_config_ref` (`config_ref.py:72`) needs a live instance, zero non-test callers. Verdict correct. |
| 2 | Trajectory-#12 §5 "L6 is independent" corrected in this PR — it was NOT independent | PASS. `traj12-next3-scoping.md`: "This corrects trajectory-check-#12 §5, which listed L6 as independent of ask #1. It is not." + "Trajectory-check-#13 should record that next-3 #3 was retracted here". Original #214 note left unedited (historical trajectory record). |
| 3 | 6.21: "a REDERIVED_AT_REVIEW consequential task cannot be approved via CLI today" is an accurate real gap | PASS. `record_review` (`review.py:107`) accepts `rederived_artifact_refs` (`:114`). `_validate_review_approval_conn` (`review_binding.py:496`, branch `:580`) → `REDERIVED_AT_REVIEW` subject + empty refs → `REVIEW_REDERIVATION_REQUIRED`. CLI `review-record` (`cli.py:247-251`, dispatch `:615`) passes only `task_id, reviewer_id, verdict, --summary` — no `--rederived-artifact-ref` anywhere in `cli.py`. `maps review-record APPROVED` on such a task deterministically fails. |
| 4 | Slice needs no new authority/schema, independent of ask #1 | PASS. `flow_review_record` is pure composition over `record_review` + one early preflight mirror; all enforcement stays in the unchanged store primitive. `get_review_subject` already exposes `freshness_mode` for the preflight. §2d MUST-NOT list explicit (no `record_review` / `_validate_review_approval_conn` change, no lease, no store primitive, no schema, no verdict→status change, no RnS/harness). Touches no `--enforce-*` path. |
| 5 | recover/release/handoff deferral rationale sound | PASS. `/usr/bin/grep -rn "lease\|expire\|heartbeat" runtime/state/review*.py` → none, so "recover a stale review" = force-closing another identity's open row behind `idx_reviews_one_open` = new authority + likely schema. `release` → `OPERATOR_VISIBLE_RELEASE_CHECK` with no primitive for release-path smoke / artifact identity validation = new capability surface. `handoff`'s final step = "attach/start replacement session" = provider launch, which `flow start` deliberately excludes. Each deferral names its blocking decision. |
| 6 | Every code citation file:line-accurate, re-verified (rule 14) | PASS with 2 non-blocking nits. Spot-checked 10: `review.py:12/107`, `review_binding.py:496`, `production.py:419/350`, `config_ref.py:72`, `flow_start.py:139`, `integrity/cli.py:117` all ✓. **Nit A:** `flow_review.py:44` cited for `flow_review_start` — `def` is at line 45. **Nit B:** `cli.py:285` variable is named `flow`, not `flow_sub`. Neither changes a conclusion. |
| 7 | Diff = work/notes/ only, no runtime/roadmap change | PASS. `git diff --stat origin/main...HEAD` = `2026-09-01-6.21-review-lifecycle-verbs-design.md` (+222), `2026-09-01-traj12-next3-scoping.md` (+184). No runtime/, no CAPABILITY_CHECKLIST.md, no schema. |
| 8 | runtime.smoke exit 0 | PASS. `python3 -m runtime.smoke` → `"ok": true`, exit=0. |

## Non-blocking

- Citation nits A/B (one off-by-one line ref, one variable-name slip). The 6.21-impl task should reference `def flow_review_start` / the `flow` subparser by name rather than line numbers.
- No mutation testing — correct per dispatch (design/scoping notes).
- 6.21 note §2b leaves implementer discretion between a new `flow review-record` verb and adding `--rederived-artifact-ref` to `maps review-record`; both within stated scope.

## Verdict

APPROVE.
