# PR #209 — Roadmap trajectory check #11 (arc PRs #194–#207) — independent review evidence

reviewer: maps-lean-laze
head_sha: fb252f556c536c2bd302d25dae98926ba91534cd
independent: true
verdict: APPROVE
summary: The note follows `playbook/ROADMAP_TRAJECTORY_CHECK.md` (5 steps + friction-log consumption). Its scope correction is right — the real uncovered arc since check #10 is PRs #194–#207 (14 commits `fbe88bc..c5461c9`), not the dispatch's hand-listed "#202–#207"; `#193` is verifiably the check-10 PR and `#194–#201` were never trajectory-checked. The scoreboard independently recounts to 16 DONE / 13 IN PROGRESS / 6 NOT STARTED from `CAPABILITY_CHECKLIST.md` §7 (35 rows), matching the note item-for-item. 7 of the note's 12 re-verified claims were independently re-checked against merged code at the arc HEAD with `/usr/bin/grep` + `git show`; all are substantively accurate. The KEY FINDING (6.4/6.5/6.16/6.22 enforcement code all merged, reachable only via opt-in `maps recovery-tick` flags, none with production exposure — "single-threaded through the first operator-gated enforced pass") is verified against the composition root. Friction-log consumption genuinely happened: 5 real entries, dispositions match `FRICTION_LOG.md`. Verdict `CONTINUE` is justified, not reassurance-drift — the note names the four-items-on-one-decision fragility explicitly and sets a concrete `#12` REPRIORITIZE trigger. Diff in-bounds: the note only (+387), no checklist status change. Author = pogo; reviewer not the author. 4 non-blocking observations, none blocks merge.

## Method

Detached worktree at PR #209 head `f500af7` (parent `c5461c9` = `origin/main` tip; the arc HEAD). `git fetch origin` first. Every claim re-derived with `/usr/bin/grep` over `runtime/` excluding `tests/` + `git show --stat` + `git log` range checks (rule 14). `python3 -m runtime.smoke` → exit 0 at the PR head. `python3 scripts/check_review_evidence.py 209` run first (reported the file missing, as expected — this commit creates it; the checker will bind to `f500af7` by walking past this evidence-only commit).

Sources of truth: the note in the PR, `playbook/ROADMAP_TRAJECTORY_CHECK.md`, `work/notes/2026-08-31-roadmap-trajectory-check-10.md`, `work/roadmaps/CAPABILITY_CHECKLIST.md` §7, `work/coordination/FRICTION_LOG.md`.

## 1. Arc scope — CONFIRMED

- `git show -s fbe88bc` → `Roadmap trajectory check #10 (PRs #185-#192) (#193)`. So `fbe88bc` **is** PR #193, the check-10 PR. ✓
- `git log --oneline fbe88bc..c5461c9` → exactly 14 commits, `d810509` (#194) … `c5461c9` (#206), plus `bb74c00` (#207). Matches the note's PR table row-for-row (14 rows, #194–#207). ✓
- Check #10's note title + body: "arc: 6 merges since check #9 (PRs #185–#192)". So `#194–#201` were never trajectory-checked. ✓
- **The dispatch's "6 PRs since check #10: #202–#207" was wrong; the note's scope correction (flagged to niko) is correct.** #209 covers #194–#207.

## 2. Scoreboard — INDEPENDENTLY RECOUNTED, MATCHES 16 / 13 / 6

`/usr/bin/grep -nE '^\| 6\.[0-9]+ ' work/roadmaps/CAPABILITY_CHECKLIST.md`, 3rd column, 35 rows (6.1–6.35):

- **DONE = 16:** 6.1, 6.2, 6.3, 6.6, 6.7, 6.8, 6.13, 6.14, 6.15, 6.18, 6.23, 6.26, 6.27, 6.28, 6.29, 6.30.
- **IN PROGRESS = 13:** 6.4, 6.5, 6.9, 6.10, 6.11, 6.16, 6.19, 6.20, 6.21, 6.22, 6.24, 6.33 (`IN PROGRESS (evaluation-only, by design)`), 6.35.
- **NOT STARTED = 6:** 6.12, 6.17, 6.25, 6.31, 6.32, 6.34.

Every per-item list in the note's §0 matches exactly. The "master-inventory §7 table" is `CAPABILITY_CHECKLIST.md`'s own §7 ("Master roadmap capability inventory"); the note parsed the right table. (The dispatch's pointer to `MAPS_Lean_Committee_Review_2026-08-19.md §7` is a mis-reference — that §7 is the non-goals section — but the note is not at fault.)

## 3. Spot-checked claims (7 of 12; dispatch asked for ≥4) — ALL SUBSTANTIVELY ACCURATE

| Claim | Independent check at `f500af7` | Result |
|---|---|---|
| **1a** #194 — `_require_destructive_enforcement` runs before the canonical check in `stop()`; both-events registration; fail-closed | `runtime/harness/service.py`: `def stop` :335 → `_require_destructive_enforcement(BEFORE_DESTRUCTIVE_ACTION, "stop")` :354 → `_require_canonical_enforcement` :375 (destructive first ✓). `destructive_action_guard.py:228` `for event in (BEFORE_DESTRUCTIVE_ACTION, BEFORE_EXTERNAL_ACTION)`. | ACCURATE |
| **1b** #195 — `denied` is a re-processable parked state; `canonical_denial_persistent` ceiling | `supervisor.py:44` `_REPROCESSABLE_STATES = {"scheduled","probing","blocked_validation","denied"}`; `canonical_denial_persistent` present; disjoint from `blocked_validation` (:503). | ACCURATE (line refs exact) |
| **1c** #199 — `--enforce-validation` opt-in, requires `--repo-root` | `runtime/cli.py:592` `if args.enforce_validation and not args.repo_root:` → refuses. `production.py` `validation_blocks_resume=enforce_validation` (default False). | ACCURATE |
| **1d** #200 — `build_project_skill_catalog(repo_root, store)` inside `flow_start()` | `runtime/flow_start.py` — call present, passed to `build_context_plan(..., skill_catalog=...)`. **BUT the note cites `:84`; the call is at `:117`** at the arc HEAD. | SUBSTANCE ACCURATE; line ref STALE — see obs. 1 |
| **1e** #202 — `MemoryProvenanceGuard` composed in `build_canonical_harness_service` | `production.py:414` `register_memory_provenance_guards(registry, MemoryProvenanceGuard())`, inside the `build_canonical_harness_service` body (def :346, `return HarnessService` ~:415). | ACCURATE |
| **1f** #204 — `select_recorded_environment_reports`; `--environment-reports-from-recorded` default-off; JSON wins | `environment_reports.py:206` def; `routing/cli.py:83` flag (`store_true`), `:131` JSON-wins branch; `router.py:151` `environment_report_required` reason. | ACCURATE |
| **1g** #206/#207 — `RunBoundValidator` unchanged: no `recorded_by` filter, `quick`-tier only | `production.py:291` `self.environment_reader.list_run_environment_evidence(str(run_id))` (no filter); `:154` `VALIDATION_TIER = "quick"`; `:317` `spec_hash_mismatch` gate. | ACCURATE |
| **1h** #205 — `maps skill` CLI is the first production caller of `record_skill_lifecycle_transition()` | `/usr/bin/grep -rn record_skill_lifecycle_transition runtime/ ex-tests` → `runtime/cli.py:469` (caller) + `skill_lifecycle_storage.py:284` (def). | ACCURATE — but see obs. 2 |

No claim was taken from a PR title/body rather than code.

## 4. KEY FINDING — VERIFIED

`build_canonical_harness_service` (`runtime/recovery/production.py:346`) body registers, in order:
`register_canonical_run_guards(registry, CanonicalRunGuard(task_reader, repo_root=...))` (:59 rel), `register_destructive_external_action_guards(registry, DestructiveExternalActionGuard(task_reader))` (:62 rel), `register_memory_provenance_guards(registry, MemoryProvenanceGuard())` (:414 abs) → `return HarnessService([adapter], hooks=registry)`.

- **Single production caller**: `/usr/bin/grep -rn build_canonical_harness_service runtime/` → one call site, `production.py:509`, guarded `if harness_project_id is not None:`. `harness_service = None` default (`:494`); `validation_blocks_resume=enforce_validation` default False.
- `--enforce-validation` requires `--repo-root`; `harness_project_id` requires `validation_repo_root`. Both opt-in flags on `maps recovery-tick`. The `maps claim` piggyback and `maps flow start` construct no `HarnessService`.
- So 6.4 (destructive), 6.16 (canonical/worktree), 6.22 (memory-provenance) share `build_canonical_harness_service`; 6.5 (`validation_blocks_resume` / `RunBoundValidator`) is wired on the same `RecoverySupervisor` that consumes that service, gated by the sibling `--enforce-validation` flag. **"Single-threaded through the first operator-gated `--enforce-canonical-run` / `--enforce-validation` production pass" is accurate. None has production exposure today.**
- Minor: §2.1 says all four are "composed into the *same* production composition root (`build_canonical_harness_service`)". Precisely, 6.5's gate is not inside that function — it is the `validation_blocks_resume` wiring in `build_canonical_recovery_supervisor` / `RecoverySupervisor`. §5 states the shared blocker correctly. See obs. 3.

## 5. Friction-log consumption — HAPPENED, DISPOSITIONS MATCH

`FRICTION_LOG.md` has 5 entries. The note's §3 table names all 5 and its dispositions match the file:

| Entry | File state | Note's disposition | Match |
|---|---|---|---|
| self-clear resume prompt | `verified: END-TO-END across three real [rotations]` | Closed (pass #10), re-confirmed 4th time | ✓ |
| coordinate-via-helper-lanes | `verified: in active use session 10` | Closed | ✓ |
| context-rotation checkpoint | `verified: PARTIAL` | Consumed; follow-up discharged; stays PARTIAL on the behavioral bar | ✓ |
| triage loop procedure-only | `verified: VERIFIED (trajectory check #10)` | Closed; this pass performs the consumption duty (2nd consecutive) | ✓ |
| orchestrator tool-use burned context | `verified: n/a (behavioral)`, `countermeasure: none mechanical` | Consumed; no recurrence this arc; stays open | ✓ |

Cross-checks: the note's claim that `limit_watcher` hcom messages report `soft=120000 rotate=150000` (pre-#187 values) matches the `limit_watcher` messages observed in this review session verbatim. `#187` = `84cc3f7` "Friction-log triage loop + raise coordinator context-rotation threshold" — the note's citation is correct. Per memory `feedback_limit_watcher_hcom`, treating that divergence as cosmetic (not a live gap) is the right call.

## 6. Verdict CONTINUE vs REPRIORITIZE — CONTINUE is justified

`playbook` REPRIORITIZE is for a stale roadmap *ordering*. Here the highest-leverage next action (the operator enforcement decision) is correctly identified, is "not more code", and is already in motion (niko is surfacing it). No unblocked in-scope work is being wrongly deprioritized. The note does **not** smooth over the risk: §2.4 and §5 name "four IN PROGRESS items single-threaded through one operator decision" as a fragility and set an explicit REPRIORITIZE trigger for pass #12 ("if that decision does not land soon … consider whether any of the four has an independent partial-exposure path"). This is the tenth-seat discipline applied, not reassurance-drift. A REPRIORITIZE-now verdict would be defensible too, but CONTINUE-with-a-named-trigger is within reasonable judgment and is honestly reasoned.

## 7. Diff in-bounds — CONFIRMED

`git show f500af7 --stat` → 1 file, `work/notes/2026-08-31-roadmap-trajectory-check-11.md` +387. No `runtime/`, no `schema.sql`, no `CAPABILITY_CHECKLIST.md` change. §6 of the note correctly says "None. No status moved." ✓

## 8. Non-blocking observations (recommend; none blocks merge)

1. **§1d line citation is stale.** The note cites `runtime/flow_start.py:84` for `build_project_skill_catalog(repo_root, store)`; at the arc HEAD the call is at `:117` (moved because #204 — *in this same arc* — added `_record_environment_evidence` + step 4 to that file). The substantive claim is correct; only that one line number was not re-derived at `c5461c9`. Trivial to fix in a follow-up or ignore.

2. **Uncaught prose drift, `runtime/state/skill_lifecycle_storage.py:12`.** Its module docstring still reads: "`record_skill_lifecycle_transition()` still has no production caller; operator-driven transitions are a later task." #205 (`410d60c`) added that caller (`runtime/cli.py:469` via `maps skill approve|activate|retire|supersede`). Same class of drift as the `runtime/recovery/production.py:194` claim that #206 fixed. The note's §1h verified the code correctly but did not flag the now-stale docstring in the same file. Recommend a one-line follow-up (fold into the next SEC4/6.10 PR or a trivial docs PR).

3. **§2.1 wording** overstates slightly — "all four … composed into the same production composition root (`build_canonical_harness_service`)". 6.5's gate is the `validation_blocks_resume` / `RunBoundValidator` wiring on `RecoverySupervisor`, not inside `build_canonical_harness_service`. §5's phrasing ("`--enforce-canonical-run` / `--enforce-validation` production pass") is accurate; recommend aligning §2.1 to it. Cosmetic.

4. **For niko (not a note defect):** the dispatch's scoreboard-source pointer to `MAPS_Lean_Committee_Review_2026-08-19.md §7` is a mis-reference; the master-inventory table lives in `CAPABILITY_CHECKLIST.md` §7. The note used the right one.

## Conclusion

**APPROVE.** Scope correction sound, scoreboard independently confirmed, all spot-checked claims accurate, KEY FINDING verified, friction-log consumption real, CONTINUE justified and honestly reasoned, diff in-bounds. The 4 observations are cosmetic / follow-up-grade and do not affect the note's conclusions.
