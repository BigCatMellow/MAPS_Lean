reviewer: maps-320-review-bozo
head_sha: f2a2bde0f74e10f2bae7adca983a6a4b41dfacad
independent: true
verdict: APPROVE
summary: |
  Independent review of PR #320 — the 6.4 first-exposure exercise of the recovery
  HarnessService.stop() call site (direct analog of #303 for 6.16). No prior
  involvement with #320/#303/#306, author nazi, or any DEC-003 exercise.

  BOUNDARY (PASS): git diff --name-only origin/main...HEAD (merge-base 25c7729) =
  exactly the 3 expected files — work/notes/2026-09-09-6.4-destructive-action-
  first-exposure.md (new), work/regression-cases/CASE-3da6464c....json (new),
  work/roadmaps/CAPABILITY_CHECKLIST.md (+1/-1). No runtime/ touch, no test
  touch, no other checklist row. Single clean commit 48f84b9, attribution
  present. Branch is 2 commits behind origin/main (both docs/wiki-only:
  d042ab2, 18b064cd) — needs a rebase before merge but no CI/content risk.

  ROW 6.4 STATUS (PASS): still IN PROGRESS. Only a dated 2026-09-09 annotation
  line appended; prior 2026-09-03 / 2026-09-05 history preserved verbatim. The
  annotation explicitly states write/credential/scope guards + capability-
  declaration manifest remain unbuilt and does not claim them closed.

  GUARD FIRED — DENY + ALLOW lanes (PASS, with disclosed caveat): note §2
  captures the pass-3 armed action dict verbatim with
  harness_stop:{attempted:true,code:HOOK_DENIED} (ordinary task,
  destructive_action=false → fail-closed, incident terminal state unchanged) and
  the armed2 dict with harness_stop:{attempted:true,code:COMMAND_FAILED}
  (destructive-envelope + recorded operator approval → guard ALLOW → chain ran
  through SESSION_STOPPING to HcomHarnessAdapter.stop(), which no-op'd only
  because viru was already killed for the stall sim). §3 hook-chain trace
  (guard_code ACTION_OUTSIDE_TASK_ENVELOPE / ACTION_WITHIN_TASK_ENVELOPE /
  CANONICAL_RUN_VERIFIED, directives, gate order) is a post-hoc RECONSTRUCTION
  using the same build_canonical_harness_service composition root, same
  resolve_harness_binding resolver, and same DB/incident inputs — honestly
  disclosed as caveat 1 (ASSUMED→traced, not VERIFIED-from-tick); reconstructed
  OperationResult codes match the in-tick harness_stop codes exactly. This is
  the same evidence standard as #303's honest caveats. Sessions buno/miho/viru
  confirmed gone via hcom list --json / --stopped (note §2).

  CONTROL LANE / FAIL-CLOSED (PASS): note §2 shows the comparison actually
  computed, not asserted — armed minus {incident_id, harness_stop} == control
  minus {incident_id, harness_stop} → True; control harness_stop is null. Matches
  the #306 supervisor.py:668-682 contract (harness_stop key always present on the
  fail action dict, null when --terminate-denied-sessions omitted; verified
  against runtime/recovery/supervisor.py on the branch). Brief's phrasing "minus
  the harness_stop key" is looser than the real contract (key present, value
  null); the note is accurate to the code and discloses this.

  REGRESSION CASE (PASS): CASE-3da6464c... is MAPS_FROZEN_REGRESSION_CASE v1,
  incident_category RECOVERY_FAILURE, promotion.automatic=false with the standard
  reason string, three expected_properties (fires-before-destructive-action /
  fail-closed-outside-envelope / flag-off-byte-identical). Passes
  runtime.evaluation.regression_case.validate_regression_case, same as the two
  precedents (CASE-378fb326..., CASE-db2717314...). Same freeze shape as
  CASE-378fb326....

  CAVEAT HONESTY incl. §4c (PASS): 5 caveats in #303 style. The design caveat
  ("for an ordinary stalled task the recovery .stop() is always guard-DENY'd on
  the task envelope; the flag only terminates destructive-envelope tasks") is
  stated plainly in note §4 caveat 3, §5, the Resume prompt, and the commit
  body — not hidden. It is a real, correctly-disclosed observation flagged for
  the next 6.4 trajectory check. guard_code="LEASE_EXPIRED" on resume denials
  correctly labeled inferred (caveat 2), as in CASE-378fb326....

  CI (PASS): docs-only diff. Spot-checks run foreground on the clone:
  python3 -m unittest tests.test_recovery_supervisor → Ran 76 tests, OK (141s);
  python3 -m runtime.smoke → "ok": true, exit 0. Full CI cited by precedent
  (#303/#315/#318) for docs-only diffs.

  Real enforced pass NOT re-run (per dispatch) — captured evidence is internally
  consistent and sufficiently detailed; no specific reason to doubt it.

  VERDICT: APPROVE. Coordinator should rebase the branch onto current origin/main
  (docs-only, trivial) and rebind this evidence before merge.

  REVALIDATION 2026-09-09 (leto, coordinator; zero-diff tier): branch brought up
  to date by `git merge origin/main` (merge commit 0bb0311; NOT rebase+force-push,
  which is classifier-blocked in this env). origin/main added only two wiki-nav
  commits (d042ab2, 18b064c) since 25c7729. The 3 reviewed files
  (work/notes/2026-09-09-6.4-destructive-action-first-exposure.md,
  work/regression-cases/CASE-3da6464c….json, work/roadmaps/CAPABILITY_CHECKLIST.md)
  are byte-identical to bozo's reviewed head 48f84b9: `git diff 48f84b9 0bb0311 --
  <those 3 paths>` is empty. bozo's APPROVE stands. head_sha rebound 48f84b9 →
  0bb0311; reviewer unchanged; one value per key; this evidence commit is the
  branch tip.

  REVALIDATION 2026-09-09 #2 (liro, coordinator, session 40; zero-diff tier):
  origin/main advanced 18b064c → 54869f5 with only three "Refresh Development
  wiki status" commits (60c0dbf, 2377bf8, 54869f5). Branch brought up to date by
  `git merge origin/main` (merge commit f2a2bde; NOT rebase+force-push). The 3
  reviewed files (work/notes/2026-09-09-6.4-destructive-action-first-exposure.md,
  work/regression-cases/CASE-3da6464c….json, work/roadmaps/CAPABILITY_CHECKLIST.md)
  are byte-identical to bozo's reviewed head 48f84b9: `git diff 48f84b9 f2a2bde --
  <those 3 paths>` is empty. bozo's APPROVE stands. head_sha rebound
  0bb0311 → f2a2bde; reviewer unchanged; one value per key; this evidence commit
  is the branch tip.
