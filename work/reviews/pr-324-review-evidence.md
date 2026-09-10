reviewer: zuna
head_sha: e6628f4d3c9dcfc8cfec669f367b376ad3eda150
independent: true
verdict: APPROVE
summary: |
  Independent review of PR #324 — H4 enforced-validation-gate first-exposure exercise.
  No prior involvement with #324 / the H4 resume-validation-gate work / author meme /
  sub-sessions gine/laza/zelu / the sibling 6.4 exercise (nazi, #320) / any DEC-003 exercise.

  BOUNDARY: `git diff --name-only origin/main...HEAD` (merge-base 18b064c) = exactly the
  3 expected files — work/notes/2026-09-09-h4-validation-gate-first-exposure.md (new, 368L),
  work/regression-cases/CASE-559ff1df...json (new), work/roadmaps/CAPABILITY_CHECKLIST.md
  (1 line, row H4). No runtime/, no tests/, no other checklist row. `git diff origin/main...HEAD
  -- runtime/ tests/` is empty; the gate code is byte-identical to main. The throwaway
  h4-exercise-spec.json is absent from the diff and from `git ls-files` (confirmed untracked).

  ROW H4: Status still `IN PROGRESS` — dated annotation only, prior history intact. Annotation
  explicitly states normal/full tiers + the per-spec EnvironmentSpec.validation.enforcement
  field remain deferred and does NOT claim them done; it closes only the "no first production
  exposure of an enforced pass" clause. Discloses that E4/6.5 rows share the same clause and
  were deliberately left unedited for a trajectory check.

  LANE A (gate fired for real): note §3 verbatim tick-3 dict — action=resume_blocked_validation,
  reason=quick_validation_failed, harness_resume=null (no resume call), state=blocked_validation,
  attempt=0 (unchanged), resume_validation={attempted:true,passed:false,tier:quick} keyed on a
  genuine subprocess returncode:1 (real run_validation_tier exit-1, independently reproduced in
  §1, not mocked), next_attempt_at = last_attempt_at + 900s exactly (flat probe interval).
  Ticks 4–5: 2nd consecutive block (validation_blocks:2) then _MAX_CONSECUTIVE_VALIDATION_BLOCKS=3
  ceiling → action=fail / validation_block_persistent / state=failed, attempt still 0. All of
  this matches runtime/recovery/supervisor.py:556-589 semantics on the branch (verified).

  LANE B (control, flag off): byte-identical incident + same failing advisory resume_validation
  → action=resume_failed, attempt→1, state=probing. Note §4 shows the set-diff actually computed
  (resume_validation payload IDENTICAL between A and B; only differing input is the
  --enforce-validation flag), not asserted.

  LANE C (attempted:false): task with no environment block → no run_environment_evidence row →
  resume_validation={attempted:false,reason:no_spec_bound} → _quick_validation_failed returns
  False → NOT blocked even under --enforce-validation; proceeded to resume attempt (design Q6 /
  MUST-NOT 4). `passed` absent, not false. Present and correct.

  REGRESSION CASE: CASE-559ff1df... passes
  runtime.evaluation.regression_case.validate_regression_case (no exception; hash self-consistency,
  incident_category, embedded Run Record, sanitized_fixture normalization/redaction all pass).
  case_kind MAPS_FROZEN_REGRESSION_CASE, promotion.automatic=false, incident_category
  RECOVERY_FAILURE, 6 expected_properties covering all three lanes + ceiling + attempt-budget.
  Same shape as sibling CASE-378fb326... Frozen_by meme.

  CAVEAT HONESTY (#303/#320 style): note §6 discloses (1) the failing tier command is synthetic
  (sh -c 'exit 1') — real mechanism, constructed trigger, same shape as #303's worktree-mismatch;
  (2) no --enforce-canonical-run composed in this pass; (3) normal/full tiers + enforcement field
  deferred; (4) control/attempted-false killed sessions were revived by hcom r --go and killed
  again immediately — disclosed; (5) environment_evidence:null on lane-A dict explained
  (no environment_reader supplied). Honest and complete.

  CI: `test` (Runtime stack tests) SUCCESS on 6a8280b. `review-evidence` FAILURE is expected —
  it fails closed until this evidence file lands. Gate code unchanged from main (already green);
  local full run not repeated (docs-only diff, OOM precedent #303/#320).

  RE-RUN: the captured enforced pass was NOT re-run — no specific reason to doubt the verbatim
  evidence, which is internally consistent with the branch's supervisor.py.

  Verdict: APPROVE.

  REVALIDATION 2026-09-09 (liro, coordinator, session 40; zero-diff tier):
  operator authz #94781 (from=bigboss) names #324. After #320 (e133a16) and #319
  (69d6497) merged, branch brought up to date by `git merge origin/main` (merge
  commit e6628f4; NOT rebase+force-push). #324's actual reviewed content is
  byte-identical to zuna's reviewed head 6a8280b:
  `git diff 6a8280b e6628f4 -- work/notes/2026-09-09-h4-validation-gate-first-exposure.md
  work/regression-cases/CASE-559ff1df...json` is empty. The only
  CAPABILITY_CHECKLIST.md change 6a8280b..e6628f4 is #320's already-independently-
  reviewed row-6.4 addition (a disjoint checklist row; clean auto-merge); #324's
  H4 row is untouched. runtime/ and tests/ are byte-identical to main (gate code
  unchanged). zuna's APPROVE stands. head_sha rebound 6a8280b → e6628f4 (equal to
  the reviewed-code head — the walk-back stops at this merge commit); reviewer
  unchanged; one value per key; this evidence commit is the branch tip.
