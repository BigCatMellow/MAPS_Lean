# Roadmap trajectory check #10 — arc: 6 merges since check #9 (PRs #185–#192)

Tenth pass. Predecessor: `work/notes/2026-09-01-roadmap-trajectory-check-9.md`
(covered PRs #177–#180 + the 42-commit governance batch, head `ee342c5`… no —
that pass ended at head after #180; this pass covers everything merged to
`origin/main` since, ending at head `ee342c5`).

Six merges this arc:

- **#185** (`5e92316`) — worktree binding enforced inside `CanonicalRunGuard` on
  continuing ops (6.16/E6(a) guard-layer seam). Checklist E6 + 6.16 evidence text
  updated. No status flipped.
- **#188** (`f620df4`) — FRICTION_LOG entry-1 rotation-10→11 end-to-end
  follow-up (docs) + review evidence.
- **#189** (`6d7a79e`) — design note: canonical-enforcement first-exposure
  (retry budget + expired-lease workflow). Note + review evidence only.
- **#190** (`03bb8a4`) — SEC4 Half 2 design addendum (authority wiring, Q4–Q8).
  Note + review evidence only.
- **#191** (`ee342c5`) — SEC3/6.4 guard impl-readiness design addendum
  (behavior Qs 1–6). Note + review evidence only.
- **#192** (`ae0d1ed`) — SEC4/6.10 Half 2 impl: durable Skill lifecycle store
  wired into real behavior. Checklist SEC4 + 6.10 evidence text updated. No
  status flipped.

Verification method (unchanged): no claim taken from a PR title, body, or
review-evidence summary; every consequential claim re-checked against
`git show --stat`, direct `grep` over `runtime/` excluding `tests/`, and a
targeted test run.

## 0. Situational awareness

- `python3 -m runtime.smoke` → exit 0 at `ee342c5`.
- `tests/test_skills_catalog.py` 14 passed; `tests/test_harness_canonical_guard.py`
  20 passed (+2 subtests).
- Scoreboard recounted from the master-inventory §7 table (parsed, 3rd column):
  **35 rows — DONE 16 / IN PROGRESS 13 / NOT STARTED 6.** Identical to pass #9
  and pass #8. No label moved this arc.
  - IN PROGRESS count includes 6.33 (`IN PROGRESS (evaluation-only, by design)`).
- Stray-branch resolution (dispatch item 4): coordinator `miga` parked
  `fix-context-builder-date-fixtures` WIP into `git stash@{0}` in the main
  worktree and switched it back to `main` on 2026-08-31. Recorded here as
  **resolved**; nothing done by this lane, stash untouched.

## 1. Re-verification of checklist claims against merged code (dispatch item 2)

Ten claims spot-checked. All accurate; no status materially false.

### 1a. E6 / 6.16 after #185 — worktree seam is in `CanonicalRunGuard`. Confirmed.

`git show 5e92316 --stat` + `/usr/bin/grep`:

- `runtime/policy/harness_guard.py:110` `_require_bound_worktree(manifest)`,
  called at `harness_guard.py:222` in the continuing-ops path; denies
  `RUN_WORKTREE_MISMATCH` (line 130) / `RUN_WORKTREE_UNAVAILABLE`.
- Injectable source: `harness_guard.py:43`
  `worktree_identity: WorktreeIdentitySource = collect_git_worktree_identity`,
  stored `:48`.
- `runtime/integrity/git_scope.py:106` `compare_worktree_identity(...)`, used by
  `verify_git_run()` at `git_scope.py:190` (single definition of sameness),
  exported `runtime/integrity/__init__.py:6,15`.
- Checklist E6 + 6.16 rows: `git show ae0d1ed`… — the #185 diff adds an
  "Updated 2026-08-31" paragraph to **both** the E6 sub-roadmap row and the 6.16
  master-inventory row (the asymmetric-miss twin that bit passes #8/#9 was NOT
  repeated this time — both twins updated together). Label stays `IN PROGRESS`
  in both; each row still explicitly says "Not `DONE`" / "E6(b) unchanged and
  still open".

### 1b. E6(b) still default-off. Confirmed — #185 did not change reachability.

`build_canonical_harness_service` remains the only production composition root
and is reached only via the opt-in `harness_project_id` keyword /
`maps recovery-tick --enforce-canonical-run`. #185 touched the guard body, not
the composition path. The checklist E6/6.16 text says exactly this.

### 1c. SEC4 / 6.10 after #192 — store is wired, but has no production caller. Confirmed; checklist text is honest about it.

`/usr/bin/grep -rn` over `runtime/` (excl. tests):

- `runtime/skills/catalog.py:221` `register_skill_catalog(...)` →
  `catalog.py:249` `store.record_skill_lifecycle_subject(entry, report, now=now)`
  — the production caller of the Half 1 store's writer, as claimed.
- `runtime/skills/catalog.py:201` `build_skill_catalog(..., store=...)` reads
  `store.get_skill_lifecycle_state(catalog_key)` one-directionally into
  `SkillProvenance.lifecycle_state`.
- `runtime/skills/catalog.py:284` `load_catalog_skill` reads composed state (the
  "first real refusal").
- `runtime/trust.py:115` `skill_lifecycle_trust_class(state)` — sole projection
  to `MemoryTrustClass`; consumed at `runtime/context_builder.py:22,40` via a
  local `None → OBSERVATION` helper. `SkillTrustState` collapse: `grep` finds no
  `SkillTrustState` symbol in `runtime/trust.py` (rule-12 collapse done).
- **But**: `grep -rn register_skill_catalog --include=*.py .` → only
  `tests/test_skills_catalog.py` + defn/export. `grep -rn build_skill_catalog`
  production callers: `runtime/context_builder.py` calls it with **no `store=`**
  (line 533 `_select_skills(skill_catalog, task)`; catalog constructed
  elsewhere without a store). No `cli.py` / `flow_start.py` entrypoint passes a
  `skill_catalog` at all.
- Verdict: the SEC4 and 6.10 checklist rows say verbatim "the Skills subsystem
  still has no runtime entrypoint that constructs a catalog … so the refusal is
  real, tested code with no production caller yet". **Accurate.** `register_skill_catalog`
  is a production *caller of the store* but is itself not yet called from any
  production entrypoint. Label correctly stays `IN PROGRESS`. Pass #9's
  observation that "SEC4 store has zero non-test writers" is now superseded in a
  narrow sense (a `runtime/` function calls the writer) but the effective
  situation — no Skill gets a persisted state in a real run — is unchanged, and
  the checklist does not overclaim.

### 1d. Design notes #189 / #190 / #191 flipped no status. Confirmed.

`git show --stat` for all three: each touches exactly one
`work/notes/2026-08-31-*.md` + one `work/reviews/pr-<N>-review-evidence.md`.
**Zero** runtime code, zero `CAPABILITY_CHECKLIST.md`, zero master roadmap,
zero `ROADMAP_TRAJECTORY_CHECK.md`. No NO/`NOT STARTED`/`IN PROGRESS` status
touched. They are pure design-readiness artifacts for the next impl slices
(canonical-enforcement first exposure; SEC4 Half 2 authority wiring; SEC3 guard
impl readiness).

### 1e. #185 / #192 checklist diffs — no status token changed.

`git show <sha> -- work/roadmaps/CAPABILITY_CHECKLIST.md | grep '^[+-].*\(DONE\|IN PROGRESS\|NOT STARTED\)'`:
every changed row line keeps its existing `| IN PROGRESS |` cell; the only
additions are evidence-text paragraphs. Confirmed against dispatch MUST-NOT.

### 1f. E4 / H5 / 6.5 — unchanged this arc, re-spot-checked.

- No PR this arc touched `runtime/environment/validation.py`,
  `runtime/recovery/production.py`, or the validation hook path. E4/6.5's
  "advisory-only, opt-in, `quick`-tier, no branch consults `resume_validation`"
  clauses still hold (no code delta).
- H5's "`build_canonical_harness_service` is the production composition root,
  default-off, closes only after first real production exposure" — unchanged;
  #185 added to the guard it composes but not to its reachability.

### 1g. Bonus finding — pass #9's two open housekeeping items:

1. **ROADMAP_TRAJECTORY_CHECK ↔ TENTH_SEAT_REVIEW xref: NOW RESOLVED.**
   `/usr/bin/grep -c 'TENTH_SEAT\|Tenth Seat\|Trigger 2' playbook/ROADMAP_TRAJECTORY_CHECK.md`
   → 1 (was 0 at pass #9). The method file now ends with a paragraph directing
   the reader to `TENTH_SEAT_REVIEW.md` Trigger 2 + §7 before recording a clean
   result. PR #169's two-passes-old follow-up is closed. (Landed in the
   playbook-consolidation work, not a PR this arc — noted for the record.)
2. The §3c process finding from pass #9 (42-commit governance batch pushed
   direct to `main`, no PR/review) — no new direct-to-main governance batch this
   arc; all 6 merges are real PRs with `work/reviews/pr-<N>-review-evidence.md`.
   The standing concern remains recorded in pass #9; nothing new to add.

## 2. Friction-log consumption (dispatch item 3 — MANDATORY)

Full skim of `work/coordination/FRICTION_LOG.md` (5 entries). Disposition for
each:

| # | Entry | Prior state | Disposition this pass |
|---|---|---|---|
| 1 | self-clear resume prompt silently dropped | `verified: UNVERIFIED end-to-end` | **CLOSED → verified.** PR #188 (`f620df4`) appended the rotation-10→11 end-to-end confirmation: session 11 received `MAPS_Lean_Handoff_2026-08-31-session10.md` as SessionStart `additionalContext` first-try, no hook-approval block; `/tmp/claude-rotate-worker.log` shows the send-keys miss on attempt 1 absorbed by the retry loop on attempt 2. Both countermeasure layers exercised live. This session ALSO started with the session-11 handoff injected by the same hook (`maps-handoff-context`) — a third independent live confirmation. `verified:` line updated + follow-up bullet 1 marked done. |
| 2 | coordinate-via-helper-lanes standing preference | `verified: in active use, follow-up: none` | **Already closed.** Re-confirmed still in force: this very dispatch is one of `miga`'s (session 12) parallel lanes. No action. |
| 3 | context-rotation checkpoint too small for coordinator | `verified: UNVERIFIED` | **Countermeasure verified live in code; behavioral bar still pending.** `legacy/MAP-System/MAP_System/scripts/context_rotation.py:72-74` now reads `DEFAULT_THRESHOLD_TOKENS = 185_000`, `SOFT_FRACTION = 0.78`, `HARD_FRACTION = 0.90` — exactly the entry's spec, merged in PR #187 (`84cc3f7`). The `verified:` condition ("a coordinator session runs a full coordinate→dispatch→review→merge cycle under the new threshold without a disruptive mid-arc rotation") is behavioral and not yet formally recorded; sessions 11→12 coordinator handoffs have been clean but no arc has explicitly logged "no disruptive rotation under 185k". Downgraded to `verified: countermeasure live (code), full-arc behavioral confirmation still open`. limit_watcher follow-up: per memory `feedback_limit_watcher_hcom`, unverified hcom-side self-rotation demands are not a real MAPS_Lean mechanism — left as a check-if-it-recurs item, not escalated. |
| 4 | "triage" loop was procedure-only, nothing ran it | `verified: UNVERIFIED — first real consumption at trajectory check #10` | **CLOSED by this pass.** This is trajectory check #10 and it consumed the log: every entry above has an explicit disposition, and this section is recorded in the note. The consumption half of the loop is now demonstrably real. Follow-up bullet ("if it doesn't, the loop still isn't real") is discharged. `verified:` updated. |
| 5 | orchestrator tool-use burned ~30-40k context on avoidable dumps | `verified: n/a (behavioral)`, conditional follow-up | **No action needed.** No mechanical countermeasure was ever owed (explicitly `n/a`). Did not recur in a way visible this arc. Left open as a watch item exactly as written. |

**Nothing open requires escalation. No live regression surfaced.** Entries 1 and
4 move to verified this pass; entry 3's countermeasure is confirmed in code with
one behavioral bar still open; entries 2 and 5 were already closed / not-owed.

## 3. What changed the picture

Nothing structural. This arc is **one small guard-layer impl (#185), one store-
wiring impl (#192), and three design-readiness notes (#189/#190/#191) plus a
docs follow-up (#188)** — all four design/impl items trace directly to pass #9
§5a's ranked horizon:

- pass #9 §5a item 2 (worktree-binding guard, "track the in-flight PR to merge")
  → **#185 merged.**
- pass #9 §5a item 3 (SEC4 Half 2, "first real writer + `decided_by`") → **#190
  design addendum + #192 impl merged.** Note: #192 delivered the store-wiring +
  first-refusal slice but explicitly deferred the operator-identity registry
  ("Half 3") and any runtime catalog entrypoint — so 6.10/SEC4 advanced but the
  remaining gap is now "no production entrypoint constructs a catalog" rather
  than "no writer exists".
- pass #9 §5a item 1 (design note answering #177 §5 Q4/Q5 — enforced
  `HOOK_DENIED` vs. RnS retry budget; expired-lease operator workflow) → **#189
  merged.** This unblocks the first enforced `--enforce-canonical-run` pass at
  the design level.
- pass #9 §5a item 4 (SEC3 guard first call site) → **#191 design addendum
  merged** (behavior Qs 1–6), the design-readiness half of that item.

The route to DONE is unchanged and the last arc advanced it exactly as pass #9
predicted. The three design notes convert three of the four §5a items from
"needs design" to "ready to implement".

## 4. Decision: CONTINUE

Per method step 3, one action: **`CONTINUE`.**

Reasoning: every merge this arc traces to a pass #9 ranked item (§3). No status
label moved, no exit gate was met, no discovered blocker changes multiple items,
the checklist is not "mostly conditional/blocked" beyond what prior passes
recorded, and no checklist claim is materially false. The design notes
(#189/#190/#191) are the expected precursors to the next impl slices, not a
scope change. Friction-log triage surfaced no regression and closed two stale
entries. The plan is still pointing at DONE.

Not `REPRIORITIZE`: the horizon order from pass #9 §5a still holds, now with
three of four items design-ready.

Not `ADD IN-SCOPE WORK`: the xref resolution (§1g) is already done; nothing new
is owed.

## 5. Horizon report — refreshed ranked next-work list

### 5a. Immediately next

1. **First enforced `--enforce-canonical-run` pass** (serves 6.4, 6.5, 6.16, H5
   — all `P1`). #189 answered the two design questions (retry-budget interaction,
   expired-lease operator workflow) that pass #9 said gated this. The
   composition root exists (#180), the worktree seam is now in the guard (#185).
   This is now an **impl/enablement** task, not a design task: turn enforcement
   on for one real project pass and record what the first exposure does
   (expected: some working resumes convert to `resume_denied` / `LEASE_EXPIRED`
   until leases are refreshed). **Ranked #1 — it is the single gate in front of
   moving four `IN PROGRESS` rows, and every prerequisite now exists in code.**
2. **SEC3 guard first call site** (6.4, `P1`). #191 resolved behavior Qs 1–6.
   `BEFORE_EXTERNAL_ACTION` / `BEFORE_DESTRUCTIVE_ACTION` still have zero
   registered guards in production — verified: `runtime/policy/destructive_action_guard.py`
   has both `DestructiveExternalActionGuard` and
   `register_destructive_external_action_guards()`, but the only callers are
   tests, and `tests/test_recovery_composition_root.py:127` explicitly asserts
   `build_canonical_harness_service` does NOT register it. The next slice is
   composing it into `build_canonical_harness_service` alongside the
   canonical-run guard. Design-ready after #191.
3. **SEC4 Half 2 completion — a runtime catalog entrypoint** (6.10, `P1/P2`).
   #192 wired the store and the first refusal but left the Skills subsystem with
   no production path that builds a catalog with a `store=`. A first
   `cli.py` / `flow_start.py` call that constructs `build_skill_catalog(..., store=...)`
   would make the refusal reachable in a real run. Smaller than it was — the
   wiring and collapse are done.
4. **Turn advisory validation into a gate** (6.5 / H4 / E4). Unchanged from pass
   #9 §5b.1. `resume_validation` is still consulted by nothing; who may let a
   failed `quick` tier block a resume is a real open question. Short design
   first. Rises in priority once item 1 lands (enforced canonical-run is the
   natural place to also consult validation outcome).

### 5b. Next tier (unchanged from pass #9)

1. **6.24** — production environment-report source/cache (`P1/P2`).
2. **6.22** — memory-trust enforcement past the Context Builder plan to a
   tool-call gate (`P1`).
3. **6.9 / S6** — progressive loading of matched Skill bodies (the one
   Skill-routing slice that is still metadata-only).
4. **`record_skill_lifecycle_transition()` production caller** (SEC4) — operator-
   driven transitions; deferred by #192 as a later task.

### 5c. Correctly gated/blocked — do not re-investigate

Unchanged, re-spot-checked: **6.35/D3** (operator target decision),
**6.25/SEC6** (`TRIGGERED`, no recorded trigger), **6.17/E7** (gated on 6.16),
**6.31/6.32/6.34** (`NOT STARTED` by current roadmap decision), **6.12/S7**
(gated on S6), **6.33** (`EVIDENCE-GATED`, evaluation-only by design).

## 6. Tenth Seat check (`playbook/TENTH_SEAT_REVIEW.md`)

**Trigger 2 — evaluated, does not fire.** Pass #9's tripwire stayed armed for
pass #10 ("if pass #10 also finds nothing substantive, produce the minority
report"). This pass DID find substantive things:

- (a) confirmed the E6/6.16 asymmetric-twin miss was NOT repeated by #185 — both
  rows updated together (a positive finding, but a real verification result);
- (b) the SEC4/6.10 gap moved category — from "no writer exists" to "no
  production entrypoint constructs a catalog" (§1c) — which re-shapes §5a item 3;
- (c) pass #9's ROADMAP_TRAJECTORY_CHECK↔TENTH_SEAT xref open item is now
  resolved (§1g) — a state change worth recording;
- (d) two friction-log entries moved to verified and one had its `verified:`
  condition downgraded to a precise partial (§2);
- (e) a refreshed §5a with item 1 recategorised from "design" to
  "impl/enablement" now that #189 landed.

Trigger 2's precondition (no substantive finding) is unmet — **no minority
report is produced.** Recording the evaluation, not just the conclusion.

**Tripwire state for pass #11:** pass #9 found something, pass #10 found
something → tripwire **stays armed** for pass #11 under the same rule. If pass
#11 finds nothing substantive, that is the two-consecutive condition — produce
the minority report then.

**Trigger 1 — not applicable.** No PR this arc flipped a status row to `DONE`,
so the "zero-finding status-flipping PR" conjunction cannot arise.

**§7 warning-sign duty (this pass's standing check).**
`ls work/reviews/ | grep -iE 'minorit|tenth|dissent'` → empty. No
minority/dissent reports have accumulated since the convention landed (PR #169).
Warning signs ("all GREEN forever", "same agent always draws the role",
"reports accumulate, nothing reopens") remain vacuously not-yet-observable. The
check is discharged; first real evaluation is still a future pass's. Note: this
is the second consecutive pass (with #9) where ordinary verification discipline
surfaced the substantive findings and no dedicated dissent pass was needed —
consistent with the seat being a backstop, not a routine gate.

## 7. Honesty check on drift

Does every merge this arc trace to something a prior pass ranked
next-to-dispatch?

- **#185** — pass #9 §5a item 2, verbatim ("track the in-flight PR to merge").
  Clean.
- **#189, #190, #191** — pass #9 §5a items 1, 3, 4 respectively (their design
  halves). Clean — these are the "short design note, not an impl" precursors
  those items explicitly called for.
- **#192** — pass #9 §5a item 3's impl half. Clean, with a documented
  scope-narrowing (deferred Half 3 / no runtime entrypoint) that this note
  carries forward into §5a item 3.
- **#188** — docs follow-up closing FRICTION_LOG entry 1's end-to-end gap. Not
  roadmap-capability work; it is the continuous-improvement loop doing its job.
  Defensible.

No speculative capability additions. No `runtime/` code landed that is not
traceable to a ranked item.

**Evidence weakening this pass's own conclusions, recorded per standing
practice:**

1. §1c's "no production entrypoint constructs a catalog" rests on `grep` for
   `build_skill_catalog` / `register_skill_catalog` callers plus reading
   `context_builder.py:533`'s call shape. I did not trace every frame that could
   reach `_select_skills` to prove a `store` is never threaded through some
   other path — but the checklist itself makes the same claim, so this is
   corroboration, not a lone assertion.
2. §2 entry 3's downgrade ("full-arc behavioral confirmation still open") is a
   judgement that clean sessions-11→12 handoffs do not by themselves satisfy the
   entry's written bar. If `miga` considers the coordinator arc since #187
   sufficient evidence, entry 3 can close fully — that is a coordinator call,
   flagged for `miga`.
3. §5a item 1's "#1, every prerequisite exists" assumes the operator intends
   `--enforce-canonical-run` to be run on a real project soon. #177's design
   left that timing as an operator call; if enforcement is not going to be
   enabled, items 2 (SEC3 guard) and 3 (SEC4 entrypoint) are the real next work
   and item 1 is premature. Same caveat pass #9 §7.3 raised — still open.

## Resume prompt

Trajectory check #10 is merged. Scoreboard holds at 35 rows — 16 DONE / 13 IN
PROGRESS / 6 NOT STARTED — unchanged for the third consecutive pass; no label
moved this arc and no PR met an exit gate. Ten checklist claims were
spot-checked against merged code at `ee342c5`: all accurate, none materially
false. #185 put the worktree-binding seam inside `CanonicalRunGuard`
(`runtime/policy/harness_guard.py:110,222`) and updated BOTH the E6 and 6.16
rows together (the asymmetric-twin miss from passes #8/#9 was not repeated).
#192 wired the SEC4 Half 1 store into `runtime/skills/catalog.py::register_skill_catalog`
+ collapsed `SkillTrustState` into `SkillLifecycleState` — but no
`cli.py`/`flow_start.py` path builds a catalog with a `store=`, so the SEC4/6.10
gap moved from "no writer" to "no production entrypoint" (checklist text is
honest about this). Design notes #189/#190/#191 touched only `work/notes/` +
review evidence — zero status flips, zero runtime code. Friction-log fully
consumed: entries 1 and 4 moved to `verified:`, entry 3's countermeasure
confirmed live in `legacy/MAP-System/MAP_System/scripts/context_rotation.py:72-74`
(185k/0.78/0.90, PR #187) with only a full-arc behavioral confirmation still
open, entries 2 and 5 already closed. No regression surfaced. Pass #9's
ROADMAP_TRAJECTORY_CHECK↔TENTH_SEAT xref open item is now resolved. Stray branch
`fix-context-builder-date-fixtures` was parked to `git stash@{0}` by `miga` —
resolved, stash untouched. Trajectory action: **CONTINUE**. Pick up §5a item 1:
run the first enforced `--enforce-canonical-run` pass on a real project (all
prerequisites now exist in code — #180 composition root, #185 worktree seam,
#189 first-exposure design) and record what the first exposure does; if the
operator is not ready to enable enforcement, §5a item 2 (register
`DestructiveExternalActionGuard` into `build_canonical_harness_service`,
design-ready after #191) or item 3 (a runtime catalog entrypoint that threads
`store=` into `build_skill_catalog`) are the independent fresh dispatches. Tenth
Seat tripwire stays ARMED for pass #11 — if pass #11 finds nothing substantive,
produce the minority report. Run pass #11 after the next 3–6 merges.
