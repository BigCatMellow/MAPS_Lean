reviewer: maps-lean-zaru
head_sha: f187dc93df093cc9d7b78ca2f257488ef7333a1e
independent: true
summary: Independent review of PR #321 (Reconcile Wiki with current MAPS_L behavior), 12 files under docs/wiki/, +1309/-408, branch docs/wiki-full-reconciliation-2026-09-09 at f187dc9. Independence: I (maps-lean-zaru) had zero prior involvement with this PR, its author (BigCatMellow), or the wiki; no commits, comments, or dispatches from me touch any docs/wiki/ file or this branch. Reviewed against origin/main HEAD b521536 and `git diff origin/main...HEAD`.

  CRITERION 1 (docs-only) — PASS. `git diff --name-only origin/main...HEAD` = exactly the 12 docs/wiki/* files (Capability-Status.md, Context-Memory-Skills-and-Capabilities.md, Development.md, Emergence-Triage-and-Learning.md, Execution-Recovery-and-Worktrees.md, First-Task-Walkthrough.md, Home.md, Operator-and-Developer-Tools.md, Review-Authority-and-Merge-Safety.md, Task-Run-and-Flow-Lifecycle.md, What-MAPS_L-Is.md, _Sidebar.md). No runtime/, tests/, playbook/, work/roadmaps/. Docs-only precedent for no full-suite run: this changes zero executable code.

  CRITERION 2 (no capability-status overclaim) — PASS. Every row in the wiki "Canonical capability scoreboard" (Capability-Status.md) checked against work/roadmaps/CAPABILITY_CHECKLIST.md on origin/main b521536, row by row 6.1–6.35: all 35 match exactly. Wiki 6.4=IN PROGRESS vs checklist 6.4 IN PROGRESS (checklist line 113, still IN PROGRESS after PR #320 merged — write/credential guards + capability-declaration manifest unbuilt). Wiki 6.16=DONE vs checklist DONE. Wiki 6.22=IN PROGRESS vs checklist IN PROGRESS. Wiki H4 references ("H4 remains IN PROGRESS", Execution-Recovery-and-Worktrees.md) vs checklist H4 IN PROGRESS (line 25, still IN PROGRESS after PR #324 merged). Wiki scoreboard "19 DONE / 10 IN PROGRESS / 6 NOT STARTED" = my independent row count of the checklist (DONE: 6.1,6.2,6.3,6.5,6.6,6.7,6.8,6.9,6.13,6.14,6.15,6.16,6.18,6.23,6.26,6.27,6.28,6.29,6.30 = 19; IN PROGRESS: 6.4,6.10,6.11,6.19,6.20,6.21,6.22,6.24,6.33,6.35 = 10; NOT STARTED: 6.12,6.17,6.25,6.31,6.32,6.34 = 6). No DONE-ish claim in the wiki exceeds its checklist row. The wiki explicitly frames itself as "Snapshot, not authority" and points to CAPABILITY_CHECKLIST.md as canonical.

  CRITERION 3 (no new authority / no rule invention) — PASS. Every reviewed page carries an explicit "not an authority store / snapshot not authority / repository main + AGENTS.md take precedence" disclaimer. The Review-Authority-and-Merge-Safety.md, Task-Run-and-Flow-Lifecycle.md, and Operator-and-Developer-Tools.md pages describe existing gates (opcmd_merge.py fail-closed checks, operator registry, release-check operator_ack_ref, review independence continuity component) in descriptive present tense matching AGENTS.md / docs/CHECKS_AND_BALANCES.md / playbook/EXECUTION_INTEGRITY.md. No sentence reads as a NEW rule or decision. The "12-hour batch merge-seat" figure is a description of existing opcmd behavior, not invention.

  CRITERION 4 (mechanism accuracy, >=10 spot-checks) — PASS. Each claim -> file:line on origin/main -> result:
   1. `--require-worktree-binding` alone fails with WORKTREE_BINDING_REQUIRES_BASE_REVISION (not silent no-op) -> runtime/state/integrity.py:209, runtime/cli.py:459 -> PASS
   2. Five `maps flow` verbs start/review-start/review-record/handoff/release-check -> runtime/cli.py:429,461,474,495,505 -> PASS
   3. No implemented `flow recover` verb -> grep of runtime/cli.py flow_sub: absent -> PASS
   4. `maps run send-context` dry-run by default; delivery needs --deliver-context + --enforce-canonical-run + --harness-project-id -> runtime/cli.py:182,191-194,216-225 -> PASS
   5. `recovery-tick --terminate-denied-sessions` requires canonical enforcement, default off -> runtime/cli.py:366,1018-1020 -> PASS
   6. `recovery-tick --enforce-validation` (H4 gate, default off, requires --repo-root) -> runtime/cli.py:349; checklist H4 line 25 -> PASS
   7. `maps freeze-case TASK_ID RUN_ID` produces MAPS_FROZEN_REGRESSION_CASE -> runtime/cli.py:232-255,939 -> PASS
   8. Operator registry: `maps init --operator-decision-ref` genesis via GENESIS authorizer; append-only -> runtime/cli.py:84,91,888-891 (runtime/state/authorized_operator_storage.GENESIS_AUTHORIZER) -> PASS
   9. Emergence incubation surfaced to operator after N=3 consecutive passes -> playbook/EMERGENCE.md:154 -> PASS
   10. Emergence lifecycle IMAGINE->CAPTURE->PROMOTE, promotion never automatic -> playbook/EMERGENCE.md (converge/decide; line 124) -> PASS
   11. HCOM_DIR precedence: explicit --hcom-dir > inherited HCOM_DIR > .hcom, warn once (PR #317) -> consistent with origin/main commit 52794e3 -> PASS
   12. Skill lifecycle VALIDATED/QUARANTINED->APPROVED->ACTIVE->SUPERSEDED, RETIRED terminal -> consistent with runtime/skills/ lifecycle (described, not contradicted) -> PASS
   13. Referenced tooling files all exist on origin/main: scripts/run_tests_sharded.py, scripts/check_spiderweb.py, scripts/coordination_housekeeping.py, scripts/opcmd_merge.py, docs/FRESH_INSTALL.md -> PASS

  CRITERION 5 (internal consistency) — PASS with one caveat. The 12 files + _Sidebar.md cross-link cleanly ([[Home]] hub, _Sidebar lists all new pages, First-Task-Walkthrough re-pointed to the new lifecycle pages). Capability-Status.md, Development.md, and Emergence-Triage-and-Learning.md agree with each other on the 19/10/6 scoreboard and on the (now-stale, see below) #319 framing — i.e. they are mutually consistent but jointly wrong on that point.

  CRITERION 6 (no secrets / no absolute home paths / attribution) — PASS pending commit. No secrets, no /home/ absolute paths, no credentials in the diff. Attribution line will be on the evidence commit.

  BLOCKING FINDING (defeats the PR's stated GOAL of accuracy vs CURRENT behavior):
  PR #319 ("Emergence may target established mechanisms for redesign/supersession") was MERGED to origin/main as commit 69d6497 on 2026-09-09 23:50Z — AFTER this branch was cut (2026-09-09 15:53Z) and BEFORE this review. playbook/EMERGENCE.md on origin/main now grants that authority in present tense (line 12: Emergence "may challenge, compare, redesign, or propose replacement of any established" mechanism; line 124: "Promotion may also authorize work whose purpose is to replace or supersede an established mechanism"). Three wiki files in this PR assert the OPPOSITE as current fact:
   - Capability-Status.md: "[PR #319] is not in `main`; established-mechanism supersession authority is not current behavior."
   - Development.md: "[PR #319] ... Its head is not in `main`." and "No open PR is counted in the scoreboard above." (#319 is no longer open.)
   - Emergence-Triage-and-Learning.md: entire section "Established-mechanism supersession is not current behavior" / "its head is **not merged into `main`**. It is therefore **IN REVIEW / NOT CURRENT**".
  Against origin/main HEAD (the dispatch's source of truth) these are factually false. This is not a capability overclaim (it is the reverse — the wiki understates current authority) and it does not touch the 19/10/6 scoreboard (no checklist row moved; 6.4/H4 remain IN PROGRESS), but it directly violates the PR's purpose. Fix (small, for a THIRD agent): update those three sections to describe #319 as merged/current, and refresh the two stale snapshot pointers ("Current Wiki-audit main: 18b064c", "Canonical main: 18b064c") to b521536. Also re-check that PR #320 (6.4) and PR #324 (H4) merges left both rows IN PROGRESS — they did (verified against checklist lines 25 and 113), so the scoreboard prose stays correct.

  NON-BLOCKING: Development.md "Recently shipped" omits #319/#320/#324 (same staleness root cause; folds into the fix above).

  VERDICT: REQUEST-CHANGES — docs-only and structurally sound (criteria 1,2,3,4,6 PASS; 5 PASS-with-caveat), but three files misstate PR #319 / mechanism-supersession authority as "not in main" when it merged to origin/main (69d6497) before this review. One targeted correction by a third agent clears it.
verdict: REQUEST-CHANGES
