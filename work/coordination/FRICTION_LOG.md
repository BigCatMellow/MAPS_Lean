# Friction log

Append-only. One entry per friction signal: something that broke, stalled, was
clunky, or that the operator asked for. Each entry records the countermeasure
and whether it has been *verified live in the system* — not just written down.

This is the capture surface for the continuous-improvement ("triage") loop.
Consumption is a standing duty of every `playbook/ROADMAP_TRAJECTORY_CHECK.md`
pass (see that file): each pass skims this log for entries with
`verified: UNVERIFIED` or `countermeasure: none yet` and either closes them,
verifies them against real system state, or escalates.

Do not delete or rewrite past entries. To update status, append a dated
follow-up line under the entry. Related: `playbook/REPAIR_AND_LEARNING.md`
(severity triage + regression-case freezing), `runtime/operational_learning.py`
(operator-gated lessons).

Entry format:
```
## <YYYY-MM-DD> — <short title>
- class: operator-request | recurring-stall | tool-gap | drift | process-gap
- opened: <YYYY-MM-DD>   # machine-readable capture-date anchor (usually = the header date)
- signal: <what broke / was asked / was clunky — 1-3 lines, concrete>
- countermeasure: <the durable fix — file/mechanism — or "none yet">
- verified: <how + date it was confirmed live, or UNVERIFIED>
- follow-up: <open items, or "none">
```

`opened:` is the machine-readable date anchor read by
[`tools/triage_status.py`](../../tools/triage_status.py) (the advisory triage
backstop a trajectory pass runs). The **pass anchor** is the set of
`trajectory check #<n>` references a pass leaves in its dated follow-up lines
(each follow-up begins
`- <YYYY-MM-DD> follow-up (trajectory check #<n>...): ...`). Legacy entries
without an `opened:` line fall back to the header date; append the field only to
new entries, never backfill past ones.

## 2026-08-31 — self-clear resume prompt silently dropped
- class: recurring-stall
- signal: session 9 (`rosa`) self-cleared with a resume prompt; successor (`loki`)
  started, went to `listening`, and received NO prompt until the operator typed
  one ~5.5h later. `claude-selfclear` delivers the resume prompt via
  `tmux send-keys` after `/clear`, which lost it (timing / auto-mode-wizard
  race). Second known instance of resume context not reaching a fresh session.
- countermeasure: three layers — (a) [primary] `~/.local/bin/maps-handoff-context`
  (new SessionStart hook script — finds newest `~/MAPS_Lean_Handoff_*.md` by
  session-number+date, injects it as `additionalContext`), registered in
  `~/Projects/MAPS_Lean/.claude/settings.local.json` under `SessionStart`;
  (b) [secondary] `~/.local/bin/claude-selfclear` hardened this session with a
  verify-and-retry loop — after sending the resume prompt it captures the pane,
  checks a ~50-char probe of the prompt's first line is visible, retries up to
  4x if not, and on total failure prints a loud manual `tmux attach`
  instruction; (c) `claude-selfclear` also warns if the newest handoff is >2h
  old. Memory: `feedback_selfclear_resume_prompt_dropped.md`. NOTE: these are
  local-machine files, NOT in this repo — the paths are recorded here for
  visibility; the repo cannot contain them.
- verified: hook script tested manually 2026-08-31 (emitted the session-9
  handoff as valid JSON `additionalContext`); full end-to-end (does a real fresh
  session actually receive it) NOT yet confirmed — UNVERIFIED end-to-end.
- follow-up: confirm the next real session start actually receives the injected
  handoff; if the one-time hook-approval prompt blocks it, note that.
- 2026-08-31 follow-up (session 10 -> 11 rotation, `loki` -> `gobi`, observer
  `meda`): VERIFIED END-TO-END, delivered cleanly with no manual operator nudge.
  (a) primary layer: session 11 received `MAPS_Lean_Handoff_2026-08-31-session10.md`
  as SessionStart `additionalContext` on the first start — no hook-approval block.
  (b) secondary layer: `/tmp/claude-rotate-worker.log` shows the tmux resume
  prompt failed to land on attempt 1 ("resume prompt not visible in pane %0;
  retrying") and succeeded on attempt 2 ("rotation delivered ... on attempt 2") —
  the built-in verify-and-retry loop absorbed the failure automatically. Net: the
  send-keys race that caused this entry still occurs, but the retry loop + the
  hook now make it non-blocking. Entry 1 can move to verified; send-keys single
  point of failure is retired.
- 2026-08-31 follow-up (trajectory check #10, `lola`): **CLOSED — verified.**
  Recorded in PR #188 (`f620df4`) and re-confirmed a third time independently:
  this trajectory-check session itself started with
  `MAPS_Lean_Handoff_2026-08-31-session11.md` injected as SessionStart
  `additionalContext` by the `maps-handoff-context` hook, no operator nudge,
  no hook-approval block. `verified:` is now END-TO-END across three real
  rotations. follow-up bullet 1 ("confirm the next real session start actually
  receives the injected handoff") is discharged.

## 2026-08-31 — coordinate-via-helper-lanes is a standing operator preference
- class: operator-request
- signal: operator wants the orchestrator to keep 2-3 dispatched helper lanes
  running and look ahead while they run — not implement directly, and not idle
  waiting for prompts.
- countermeasure: encoded in every session handoff's "Standing operating mode"
  section + memory `feedback_orchestrator_mode.md`,
  `feedback_never_ask_keep_working.md`.
- verified: in active use session 10 (3 lanes dispatched: #174 rescue, #185
  worktree guard, trajectory #9) — 2026-08-31.
- follow-up: none.

## 2026-08-31 — context-rotation checkpoint too small for the coordinator role
- class: tool-gap
- signal: operator observed the coordinator session hit 130k tokens "almost
  right away" and rotation risks disrupting more than helping. Threshold is
  `legacy/MAP-System/MAP_System/scripts/context_rotation.py`
  `DEFAULT_THRESHOLD_TOKENS = 150_000` (soft = 80% = 120k), capped
  `min(150k, window·0.75)` / `min(120k, window·0.60)` so 150k/120k always bind
  regardless of window. Fine for a single-task implementer; too tight for a
  coordinator holding N in-flight lanes + roadmap state across round-trips.
- countermeasure: Part 2 of this PR — raise the default + fractions
  (`DEFAULT_THRESHOLD_TOKENS` 150k→185k, `SOFT_FRACTION` 0.60→0.78,
  `HARD_FRACTION` 0.75→0.90). Also lossless handoffs via the SessionStart hook
  (entry 1) so a rotation costs ~5k re-orientation not ~40k.
- verified: PARTIAL — countermeasure confirmed live in code (trajectory check
  #10, `lola`): `legacy/MAP-System/MAP_System/scripts/context_rotation.py:72-74`
  reads `DEFAULT_THRESHOLD_TOKENS = 185_000`, `SOFT_FRACTION = 0.78`,
  `HARD_FRACTION = 0.90` exactly per spec, merged PR #187 (`84cc3f7`). The
  full-arc behavioral bar (a coordinator running coordinate→dispatch→review→merge
  under 185k without a disruptive mid-arc rotation) is NOT yet explicitly logged;
  sessions 11→12 handoffs have been clean but no arc recorded "no disruptive
  rotation under the new threshold". Coordinator call whether that suffices.
- follow-up: if `limit_watcher` (hcom-side) has its own separate threshold
  config, that may also need raising — check `hcom config` next session.
  (Per memory `feedback_limit_watcher_hcom`: unverified hcom-side self-rotation
  demands are not a real MAPS_Lean mechanism — this is a check-if-it-recurs
  item, not an escalation.)
- 2026-09-01 follow-up (trajectory check #13, `vame`): both open sub-items
  resolved to non-issues. (a) `hcom config` has **no** rotation/token/threshold
  key; the running `limit_watcher.py` is a legacy non-MAPS_Lean script
  (`…/MultiAgentProject/Source/MAP_System/scripts/limit_watcher.py --interval
  300`) whose demands memory `feedback_limit_watcher_hcom` says to ignore — ~8
  such messages correctly ignored across session 16. Not a MAPS_Lean mechanism;
  nothing to raise. (b) Behavioral bar **met**: session 16 (`rozo`) ran a full
  multi-lane arc — trajectory-#12 consumption → dispatch #219 (SEC4 manifest) →
  #218 (6.21) → 6.9/S6 → #220 (#218 follow-up) → this check — with no disruptive
  mid-arc rotation. Recommend `verified: PARTIAL` → `verified: VERIFIED`
  (coordinator call). Both follow-up bullets discharged.
- 2026-09-01 follow-up (trajectory check #14, `gela`): **`verified: PARTIAL` →
  `verified: VERIFIED`.** Session 16 has since run an even longer arc (#221 6.9/S6
  → #223/#224/#227 design notes → #225 SEC4 slice 2 → #226 6.21 increment-a →
  checks #13, #14) with no disruptive mid-arc rotation. Behavioral bar met twice
  over; both #13 follow-up sub-items already resolved to non-issues. Entry closed.

## 2026-08-31 — "triage" continuous-improvement loop was procedure-only, nothing ran it
- class: process-gap
- signal: operator: "I don't know if it does anything." Audit found
  `playbook/REPAIR_AND_LEARNING.md` + `work/coordination/README.md`
  §stalled-work-triage + `freeze-case` CLI + `runtime/operational_learning.py`
  (~zero writers) — all procedure or unused. No capture surface for
  operator-friction/requests; the retrospective loop has no owner/trigger;
  nothing verifies a countermeasure stays live.
- countermeasure: this PR — `FRICTION_LOG.md` (this file) + capture wired into
  `REPAIR_AND_LEARNING.md` and the session-handoff checklist + consumption wired
  as a standing duty into every `ROADMAP_TRAJECTORY_CHECK.md` pass.
- verified: VERIFIED (trajectory check #10, `lola`, 2026-08-31) — pass #10
  skimmed all 5 entries in this log and recorded an explicit disposition for
  each in `work/notes/2026-08-31-roadmap-trajectory-check-10.md` §2. Entries 1
  and 4 (this one) moved to verified; entry 3 downgraded to a precise partial;
  entries 2 and 5 already closed. The consumption half of the triage loop is now
  demonstrably real.
- follow-up: none — but every future trajectory-check pass carries the same
  standing duty; if a pass skips it, the loop has regressed.

## 2026-08-31 — orchestrator tool-use burned ~30-40k context on avoidable dumps
- class: tool-gap
- signal: session 10 coordinator ran a 151KB `find` dump, a `git ls-tree | grep`
  returning ~250 release-checklist filenames, and re-read whole 37KB/57KB docs —
  ~30-40k tokens of avoidable context spend that contributed to hitting the
  rotation threshold fast.
- countermeasure: none mechanical — model-side discipline (targeted greps,
  `git show` of specific line ranges, `Read` with offset/limit). Recorded so the
  pattern is visible if it recurs.
- verified: n/a (behavioral).
- follow-up: if this recurs in a later coordinator session, consider a durable
  countermeasure (e.g. a scratchpad orientation script that produces a compact
  status digest instead of ad-hoc exploration).
- 2026-09-01 follow-up (trajectory check #14, `gela`): **no recurrence — 3rd
  consecutive arc.** The #221–#227 implementer lanes (this trajectory lane
  included) used targeted `/usr/bin/grep`, `git show --stat` / path-scoped
  `git show`, `sed -n` line ranges, and `Read` with offset/limit — no 100KB+
  dumps, no whole-doc re-reads. Stays open (behavioral, "if it recurs").
- 2026-09-01 follow-up (trajectory check #15, `gela`): **no recurrence — 4th
  consecutive arc.** The #229–#232 lanes (#229 a ~25-line prose fix; #230/#232
  design notes from this lane; #231 the flow-handoff impl) used the same scoped
  tooling. Stays open.
- 2026-09-01 follow-up (trajectory check #16, `nava`): **no recurrence — 5th
  consecutive arc.** The #234–#238 lanes (2 design notes, a 1-line prose fix, the
  #236 safeguard, the #237 slice-2 impl) used scoped `git show` / `/usr/bin/grep`
  / `sed -n` / `Read` offset+limit throughout. Stays open.
- 2026-09-02 follow-up (trajectory check #17, `vame`): **no recurrence — 6th
  consecutive arc.** The #241–#246 lanes (a scoping design note, the #243
  operator-answers record, #242 policy-token impl, #244 `flow release-check`,
  #246 frozen corpus + test) + this trajectory lane used scoped `git show` /
  `/usr/bin/grep` / `sed -n` ranges / `Read` offset+limit throughout. Stays open
  (behavioral, "if it recurs").
- 2026-09-02 follow-up (trajectory check #18, `vame`): **no recurrence — 7th
  consecutive arc.** The 13-PR `6ea81b2..d8568a3` window (#241–#255: design
  notes, scoping notes, the #255 Ask-#1 runbook, #242/#244 impl, two review
  lanes) + this trajectory lane used scoped tooling throughout; the #255
  deadlock trace followed specific call sites via `/usr/bin/grep` + `sed -n`,
  not a dump. Stays open.
- 2026-09-02 follow-up (trajectory check #19, `vame`): **no recurrence — 8th
  consecutive arc.** The `03b6a34..3a4b3a4` window (#257–#260: a scoping note,
  two code impl PRs I reviewed pre-merge, the selector-quality impl) + this
  trajectory lane used scoped tooling throughout. Stays open.
- 2026-09-03 follow-up (trajectory check #20): **no recurrence — 9th consecutive
  arc.** The #263–#268 lanes (5 doc/status PRs + the #267 `review_binding.py`
  slice) + this trajectory lane used scoped `git show` / `git show --stat` /
  `/usr/bin/grep` / `awk` / `sed -n` line ranges / `Read` offset+limit; the one
  large `CAPABILITY_CHECKLIST.md` dump was redirected to a saved file by the
  harness, not re-read into context. Stays open (behavioral).
- 2026-09-03 follow-up (trajectory check #21): **CLOSED — 10th consecutive
  no-recurrence arc.** The #269–#276 lanes + this trajectory lane used scoped
  `git show` / `git show --stat` / `/usr/bin/grep` / `sed -n` line ranges /
  `Read` offset+limit throughout — no 100KB+ dumps, no whole-doc re-reads. Per
  `playbook/ROADMAP_TRAJECTORY_CHECK.md` (a behavioral watch-if-it-recurs entry
  with 3 clean arcs is CLOSED, not carried further), this is closed 7 arcs past
  that threshold. A future recurrence is a fresh entry (with the
  scratchpad-orientation-digest countermeasure this entry sketches), not a
  re-open.

## 2026-09-01 — stale slice-boundary NonGoalTests assertions
- class: recurring-stall
- signal: a `NonGoalTests` source-substring assertion (`assertNotIn("<symbol>",
  runtime/context_builder.py source)`) that correctly encodes "slice N does not
  do X" breaks when slice N+1 legitimately introduces X. Occurrence 1: PR #221
  added `load_catalog_skill(` (a call slice-1's own test banned by substring),
  CI caught it, follow-up commit renamed+rewrote the test. Occurrence 2: PR #237
  added `script_paths` / `reference_paths` / `example_paths` / `asset_paths`
  references to `_select_skills` as legitimate execution-resource *manifest*
  vocabulary; `tests/test_memory_trust_gate.py::NonGoalTests` still banned those
  names by `assertNotIn`; CI caught it; follow-up commit `66e108d` flipped them
  to `assertIn` and added `assertNotIn("load_skill_resource(", text)` as the real
  slice-2 non-goal.
- countermeasure: NOT a rule-20 CI script. PR #232's own design note §5 ("out of
  scope") already reasoned this through: a CI check cannot distinguish "this
  assertion is correct today" from "the next planned slice will legitimately
  flip it" — that is forward-looking design knowledge, not a static property, and
  the class is already self-catching (CI red on the impl commit). The fitting
  countermeasure is a **dispatch-time discipline** (AGI-standard shape, rule 19):
  *a dispatch for a scope-expanding slice must name the sibling NonGoal /
  boundary tests the slice will legitimately supersede, so the implementer
  updates them in the same PR rather than tripping CI.* Reviewer-side is covered
  by memory `feedback_stale_slice_boundary_nongoal_test` /
  `feedback_review_test_set_too_narrow`.
- verified: END-TO-END (twice) — CI caught both occurrences; each was fixed by a
  same-branch follow-up commit before merge. No escaped defect either time.
- follow-up: check #17 verifies the dispatch discipline above was actually
  adopted (a scope-expanding-slice dispatch that names its superseded boundary
  tests). If a 3rd occurrence lands *and* the dispatch discipline was in place,
  re-open for a mechanical safeguard discussion.
- 2026-09-02 follow-up (trajectory check #17, `vame`): **no clean test case this
  arc** — none of #241–#246 was a scope-expanding `_select_skills` /
  `context_builder` slice with `NonGoalTests` substring-assert risk. The
  discipline IS being applied prospectively: the #251 SEC4 Half 3 slice-2 scoping
  note's §3 Stop-conditions explicitly name the boundary the slice supersedes
  ("If any existing test asserts an unauthorized actor can
  activate/retire/supersede against a seeded registry → update it"). Check #18
  gets the first real test — the #251 slice-2 impl PR. Stays open.
- 2026-09-02 follow-up (trajectory check #18, `vame`): the #251 slice-2a impl
  has **not landed yet** (dispatched to `luve`, no PR) — carries to #19. A
  *second* scope-expanding `_select_skills` slice is now also queued: the #254
  selector-quality impl (path a — HARD_NEGATIVE score + AMBIGUOUS margin + V01
  lemmatiser), whose dispatch (#254 resume prompt) explicitly names the boundary
  it supersedes ("the per-category structural asserts … change intentionally";
  "`test_exp_a` v1 pins may shift — update alongside, note it"). Both impl PRs
  are #19's test of the dispatch discipline. Stays open.
- 2026-09-02 follow-up (trajectory check #19, `vame`): **the discipline HELD on
  both real tests.** #259 (SEC4 slice 2a — a scope-expanding CLI change) rewrote
  `test_seeded_registry_does_not_gate_activate` into 4 tests in the same PR, per
  the #251 §3 Stop-condition it named. #260 (selector match-strength gate)
  flipped `test_exp_b_skill_routing`'s HARD_NEGATIVE structural asserts + updated
  `test_exp_a` v1 pins alongside the selector change, in-PR. Neither tripped a
  CI-red boundary assert. `verified:` upgraded to **END-TO-END (×4 — CI caught 2
  pre-discipline; discipline held on #259 + #260)**. Stays open (a 3rd
  post-discipline occurrence with a CI-red trip would re-open the mechanical
  safeguard discussion).
- 2026-09-03 follow-up (trajectory check #20): **no clean test case this arc.**
  None of #263–#268 was a scope-expanding `_select_skills` / `context_builder`
  slice; #267 (`runtime/state/review_binding.py`) added no `NonGoalTests`
  substring risk and updated its own `flow_release_check` advisory string + the
  matching test assertion in-PR. No CI-red boundary trip. Stays open.
- 2026-09-03 follow-up (trajectory check #21): **no clean test case this arc.**
  None of #269–#276 was a scope-expanding `_select_skills` / `context_builder`
  slice. #276 loosened its *own* option-D `test_list_sessions_include_stopped_
  survives_nonjson_stopped_output` call-sequence assertion in the same PR
  (tail-pinned → index-ordered; a justified contract change — an `events` call
  now follows the alive fallback; behavioural asserts unchanged). No CI-red
  boundary trip. Discipline holding (2nd post-discipline arc with no trip).
  Stays open (close: 3 clean post-discipline arcs, or a 3rd CI-red trip
  re-opens the mechanical-safeguard discussion).

## 2026-09-03 — coordinator merge marks treated as merge authorization (recurrence)
- class: recurring-stall
- signal: 2nd occurrence of the same pattern — a coordinator/peer lane's own
  "APPROVED / ready to merge" marks being acted on as merge authorization without
  an explicit operator line. Occurrence 1 (session 24, #270): the OPCMD merge
  retry loop merged #270 one turn *before* an operator HOLD landed — the retry
  raced an authority-ambiguous merge (memory
  `feedback_opcmd_hold_lost_to_retry_race`). Occurrence 2 (session 25): the
  merge-authority rule (invariant / `AGENTS.md` §"Merge authority", PR #266) was
  in place and still did not stop a coordinator-mark-only merge being queued —
  the rule says "operator-only or a designated coordinator seat" but nothing
  mechanically checks that a specific operator authorization exists for the
  specific PR before the merge runs.
- countermeasure: **mechanical safeguard (invariant 13 / rule 20).** The
  merge-runner seat (`gule`) independently requires an explicit operator line
  naming it as the merge seat *or* naming a specific PR number to merge;
  coordinator marks ("APPROVED", "ready", "merge it") alone are insufficient and
  the merge-runner enforces this by refusing to run `gh pr merge` until it can
  quote the operator authorization (message id + PR number) in-channel. This is
  an actor-side gate on the runner, not another line in `AGENTS.md`.
  Why the 1st fix did not hold: PR #266 added a *prose rule* ("`gh pr merge` is
  operator-only, or an explicitly designated coordinator seat") — an instruction.
  Invariant 13 is explicit that the 2nd occurrence of a pattern does not get a
  second instruction; the retry loop and the coordinator seat both read the prose
  as already satisfied by their own role and merged anyway. The enforced version
  moves the check into the runner's pre-merge step where it blocks mechanically.
- verified: UNVERIFIED — the runner-side gate is described here and in the
  session-25 handoff; not yet observed refusing a real coordinator-mark-only
  merge. Observation condition: next merge cycle, `gule` blocks or quotes the
  operator authorization before `gh pr merge`. Checked at the next trajectory
  pass.
- follow-up: trajectory check verifies (a) the runner-side gate was actually
  adopted by `gule`, (b) no 3rd occurrence of a coordinator-mark-only merge. A
  3rd occurrence with the gate in place is an operator escalation, not a 4th fix.
- 2026-09-03 follow-up (trajectory check #21): **UNVERIFIED — pass 1 of ≤3; no
  3rd occurrence.** All five arc merges (#269/#272/#274/#275/#276) ran through
  the `gule` merge-runner seat under Mode A (session-26 handoff: `gule` merges
  only on an explicit operator PR-number instruction; coordinator marks alone
  insufficient). No coordinator-mark-only merge occurred this arc. The gate's
  *refusal* behaviour cannot be verified from a clone — needs a live observation
  of `gule` blocking or quoting an operator authorization. Stays UNVERIFIED,
  pass 1 of the N=3 ladder; not an escalation this pass. #22/#23 close it or it
  auto-escalates at #24.
- 2026-09-04 follow-up (trajectory check #23): **N=3 reached — automatic
  operator-escalation, per `ROADMAP_TRAJECTORY_CHECK.md`'s ladder (pass 2 was
  recorded in check #22's own note §3.1 but never appended here as a dated
  line — corrected now).** (i) No 3rd occurrence of a coordinator-mark-only
  merge this arc (#286/#287/#288 all ordinary `BigCatMellow`-account squash
  merges). (ii) `gule` was NOT observed enforcing the gate — structurally
  cannot be: the gate itself (`scripts/opcmd_merge.py`) shipped **dormant**
  in this same arc's PR #287 (411 lines, 18/18 tests, re-run here). "Built and
  tested" is not "adopted and live" — 4 operator decisions are still pending
  per `work/notes/2026-09-04-merge-auth-mechanical-backstop-design.md` §6
  (mandatory-path adoption, identity allowlist, `AGENTS.md` reword,
  ledger-vs-in-channel). Disposition: does NOT close on "built + dormant"
  alone — that would let the entry close without ever answering its own
  verification question. Named as an operator-escalation item in
  `work/notes/2026-09-04-roadmap-trajectory-check-23.md` §7 item 1. Next pass
  looks for a live gate-refusal/enforcement observation post-adoption.
- 2026-09-05 follow-up (trajectory check #24): **Still UNVERIFIED — status
  update, not a new escalation.** No 3rd occurrence of a coordinator-mark-only
  merge this arc (#291/#292/#293/#295 all ordinary `BigCatMellow`-account
  squash merges); `gule` still not observed enforcing the gate — no PR in
  this arc adopted `scripts/opcmd_merge.py` as a required path. New fact this
  pass: per the session-31 handoff, the operator has answered 2 of the 4
  pending adoption decisions (mandatory-path = YES, ledger = persistent)
  directly to the session-31 coordinator, outside hcom — not yet a
  quotable/mechanical record, and not yet landed here or in `AGENTS.md`
  (`#294`, the PR meant to land it, is still DRAFT as of this pass —
  `gh pr view 294` confirms). Next pass checks whether `#294` merged and
  whether a live gate-refusal observation is now possible.

## 2026-09-02 — agent edited the shared coordinator checkout instead of its own worktree
- class: process-gap
- signal: 4th coordination-hygiene signal in the `6ea81b2..d8568a3` arc (after
  the 5h+ merge-queue stall / no coordinator seat; the concurrent #245 rebase
  race; and now this). `soda` found an uncommitted modification to the
  `CAPABILITY_CHECKLIST.md` 6.10 row ("…covers all `maps skill` lifecycle verbs
  (approve/activate/retire/supersede, Half 3 slice 2 increment 2a)…") sitting in
  the **coordinator checkout** `~/Projects/MAPS_Lean` working tree — NOT a
  worktree. It was `luve`'s SEC4 Half 3 slice-2a checklist evidence, written to
  the wrong checkout. `soda` stashed it, confirmed with `luve` that the clause
  belongs on the slice-2a branch, then dropped the stash. No harm done (caught
  before it contaminated a merge), but a stray edit in the shared checkout can
  be picked up by the next `git add -A` during merge-prep and land in an
  unrelated PR.
- countermeasure (rule-20, proposed — pending operator adoption via #253 item 2,
  which this extends): **agents NEVER edit files in the coordinator checkout
  (`~/Projects/MAPS_Lean`), only in their own `.claude/worktrees/<name>/`
  worktree. The coordinator's working tree is merge-prep-only** (rebase, evidence
  binding, `gh pr merge`) — never an authoring surface. Add to `AGENTS.md` +
  the session-handoff template alongside the #252 §1.5 merge-prep rule. This is
  a process rule, no machinery (rule 13). A mechanical backstop worth
  considering if it recurs: a pre-merge `git status --porcelain` check in the
  coordinator checkout that refuses merge-prep while the tree is dirty.
- verified: the specific incident is confirmed (soda observed + stashed + dropped
  the edit 2026-09-02). The countermeasure is NOT yet adopted — it is folded
  into #253 item 2's operator decision.
- follow-up: check #19 verifies (a) #253 item 2 (incl. this extension) was
  answered, (b) no 5th coordination-hygiene incident in the #18→#19 arc. If a
  5th lands, the mechanical backstop (dirty-tree merge-prep refusal) gets scoped.
- 2026-09-02 follow-up (trajectory check #19, `vame`): (a) #253 item 2 **still
  unanswered** (the whole operator batch is). (b) **No 5th incident.** mika
  (session-20 coordinator) drained the 3-PR merge queue running merge-prep from
  the coordinator checkout as merge-prep-only (rebase + evidence commit), and
  the 3 cross-assigned review-evidence commits (committer ≠ author ≠ reviewer)
  were each done in the committer's own worktree — the exact shape the
  countermeasure prescribes, applied by convention before adoption. Countermeasure
  stays folded into #253 item 2 (pending the operator). Stays open.
- 2026-09-03 follow-up (trajectory check #20): **CLOSED — countermeasure adopted.**
  #266 (`3dfc922`; decision batch item 2, operator-answered via #265) landed the
  merge-authority rule into `AGENTS.md` (`### Merge authority (operator-adopted
  2026-09-02)` — `gh pr merge` operator-only; no coordinator seat → longest-running
  peer lane keeps every APPROVED PR rebased + evidence-bound but does not merge;
  claim the rebase in-channel) + a "Merge authority for this handoff" block in
  `templates/handoff.md`. This is the operator adoption the entry was folded into.
  No coordination-hygiene incident in the #19→#20 arc — all six arc merges were
  operator-account squash-merges. The mechanical backstop (dirty-tree merge-prep
  refusal) stays a "if a 5th lands" item.

## 2026-09-03 — fix commit lands on top of review-evidence; evidence re-bound to new head
- class: process-gap
- signal: trajectory check #20 arc — twice, an independent reviewer's non-blocking
  nit was applied by the impl agent *after* the review-evidence file was
  committed, forcing a re-bind. #267 (`5a0f7c5`): the `flow_release_check`
  `next_step.reason` advisory string was fixed in `3f0c109` and the evidence
  updated to that head. #268 (`828d5e7`): a stale IN-PROGRESS sentence was
  dropped + status blocks reduced to pointers in `261636a`, evidence re-bound.
  Both contained (delta re-reviewed in-PR, no escaped defect), but the round-trip
  is now a recurring shape on doc/prose PRs.
- countermeasure: dispatch discipline (rule 19 shape) — a review dispatch for a
  prose/status PR should expect and bundle the "reviewer's own nits applied by
  the impl agent, then evidence re-bound to the new head" round-trip as part of
  the review lane, not treat the first evidence commit as final. Not machinery
  (rule 13). A 3rd occurrence with an *escaped* stale bind (evidence not updated
  to the fixed head) re-opens for a mechanical check (`review-evidence.yml`
  head_sha match).
- verified: both occurrences confirmed 2026-09-03 — `git show 5a0f7c5 -s` /
  `git show 828d5e7 -s` show the fix commit + the evidence re-bind commit; the
  `pr-267` / `pr-268` review-evidence `head_sha:` fields match the final heads.
- follow-up: check #21 notes whether a 3rd occurrence lands and whether the
  evidence stayed bound to the correct head.

## 2026-09-03 — dispatched worker stalls on its own full `unittest` suite
- class: recurring-stall
- signal: several test modules run ~7–8 s per test (`test_flow_release_check`,
  `test_context_builder`, the `test_exp_b_skill_routing` batteries) — a single
  module is 3+ min and `python3 -m unittest discover -s tests` is well over a
  short foreground cap. A dispatched worker that runs the full suite foreground
  without a raised timeout stalls; running it backgrounded then reading a
  buffered-empty output file looks like a hang. Multiple "run tests" stalls
  across recent arcs trace to this.
- countermeasure: dispatch discipline (rule 19 / rule 20) — every test dispatch
  states "run the named modules as a blocking foreground call; the full suite is
  CI's (`runtime-stack-tests.yml`, 15-min budget) — if you must run it locally,
  raise the timeout and expect buffered output". Trajectory check #20 applied
  this (named modules foreground, full suite delegated). A mechanical option if
  it recurs: a `scripts/` wrapper that shards the suite and streams per-module
  timing.
- verified: n/a (behavioral) — the per-test cost is real (observed 2026-09-03:
  4 gate tests in `test_flow_release_check` took 30 s).
- follow-up: if a worker stalls on the full suite again after this discipline is
  in the dispatch, scope the sharding wrapper.
- 2026-09-04 follow-up (trajectory check #22): **recurred 2× in session 27,
  discipline already in place → rule-20 mechanical-safeguard now scoped-needed.**
  Implementers `rovu` and `buro` both backgrounded the local `unittest` suite
  and sat on a Monitor/wait-loop instead of finishing; coordinator `mimi`
  intervened both times. Every impl brief already forbids this. This converges
  with `work/notes/2026-08-18-stalled-dispatched-worker-repair.md` Prevention §1
  (deferred "mechanical timeout/heartbeat for dispatched background workers"),
  which `tools/triage_status.py` also flags as a Drift+ record missing a
  countermeasure. Per rule 20 the fix is now an actual safeguard — a
  sharding/streaming test wrapper (`scripts/`) keeping per-module runs under a
  foreground cap, and/or a dispatched-worker heartbeat check — not another
  instruction. Named in `work/notes/2026-09-04-roadmap-trajectory-check-22.md`
  §7 item 2 as a countermeasure-needed operator/coordinator item.
  `countermeasure:` is now "scoped-needed (rule 20)", not just dispatch
  discipline.
- 2026-09-04 follow-up (trajectory check #23): **countermeasure SHIPPED —
  PR #288.** `scripts/run_tests_sharded.py` (per-module subprocess shards,
  streamed heartbeat output, self-bounding, exit codes trustworthy) +
  `scripts/hooks/block-monitor-on-tests.example.json` (dormant Monitor-block
  hook template) merged this arc, independently reviewed (`pr-288-review-
  evidence.md`, sana, 6/6 focus areas verified empirically). Re-ran
  `tests.test_run_tests_sharded` here: 10/10 OK. `countermeasure:` moves from
  "scoped-needed (rule 20)" to **"shipped (PR #288), adoption pending"** — the
  hook template is not yet wired into a live hook config and no dispatched
  worker has used the runner under real stall pressure yet. Not a full CLOSE.
  #24 checks for a first real observed use.

## 2026-09-03 — hcom 0.7.25 `list --stopped` ignores `--json`, blocking `maps recovery-tick`
- class: tool-gap
- signal: enforced canonical-run pass (operator decision batch item 5) aborted with
  `{"ok": false, "error": "HcomProtocolError: hcom list --json returned invalid JSON", ...}`
  (exit 2), nothing written. `HcomAdapter.list_sessions(include_stopped=True)` runs
  `hcom list --json --stopped --all`; hcom 0.7.25 ignores `--json` for `--stopped` and
  always emits human text (`No recently stopped agents (last 60m)` / `Stopped agents
  (all, showing N): ...`). `json.loads` explodes. Because `RecoverySupervisor.observe_silent_stops`
  and `tick` (and `HcomSessionAdapter._session_records`) call it unconditionally, ALL of
  `maps recovery-tick` — not just `--enforce-canonical-run` — is dead against hcom 0.7.25.
  `hcom list --help` shows `--json` is intentionally absent from the `--stopped` subcommand,
  so no hcom version fixes this.
- countermeasure: repair record `work/notes/2026-09-03-hcom-list-stopped-nonjson-repair.md`
  (severity BLOCKING) + this PR. Part A (folded in): `list_sessions` falls back to
  alive-only `hcom list --json` when the `--stopped` output is not JSON — detection preserved
  (absent == not-live), `session_id`→`run_id` lineage degrades to unresolved (documented).
  Frozen regression test `tests/test_hcom_adapter.py::...::test_list_sessions_include_stopped_survives_nonjson_stopped_output`
  feeds hcom's real `--stopped` text (empty + non-empty) and asserts it no longer raises.
  Part B (design-only, follow-up impl + review): option C — rebuild stopped-session records
  from `hcom events --json` to restore lineage without depending on `--stopped --json`.
- verified: defect reproduced 2026-09-03 in a fresh clone against installed `hcom 0.7.25`
  (`/home/home/.local/bin/hcom`): `hcom list --json --stopped --all` → human text (exit 0);
  `hcom list --json` → `[]` (exit 0). Part A regression test + `tests/test_hcom_adapter.py`
  `tests/test_recovery_supervisor.py` `tests/test_harness_hcom_adapter.py` green (87 passed).
  Full suite: see PR. `recovery-tick` / `--enforce-*` NOT re-run (stop condition).
- follow-up: Part B impl PR (option C) + independent review. Also open: hcom upstream
  changelog unreachable from this env (compiled binary) — confirm no `--stopped --json`
  support lands that would let Part B simplify.
- 2026-09-03 update (item 5 / option C impl, `impl/item5-optionC-events-stopped-records`):
  **Part B landed.** `HcomAdapter._stopped_records_from_events()` rebuilds stopped-session
  records from `hcom events` (JSONL; `--json` is the default, not a flag — Step-0 finding)
  and merges them under the alive list in the non-JSON `--stopped` fallback. `name → session_id`
  comes from the most recent `status` event for that name carrying non-null `data.session`;
  stop signal from a `life action:stopped` or `status new_status:inactive`. Lookback
  `_STOPPED_EVENTS_LOOKBACK = 2000` events (~6h at observed rate, < read_events cap 5000).
  Frozen regression test `tests/test_hcom_adapter.py::...::test_list_sessions_include_stopped_reconstructs_from_events`.
  Residual gap: a session that started+stopped entirely outside the lookback window still
  yields an unresolved `run_id` (same as Part A, smaller exposure). See
  `work/notes/2026-09-03-item5-optionC-impl.md`.
- 2026-09-03 follow-up (trajectory check #21): **CLOSED.** Part A merged (PR #269,
  `a6ad820`) + Part B / option C merged (PR #276, `9a884c2`), both with
  independent review (`work/reviews/pr-269-review-evidence.md` /
  `pr-276-review-evidence.md`, `independent: true`). `maps recovery-tick` abort
  cleared; `tests.test_hcom_adapter` + `tests.test_recovery_supervisor` +
  `tests.test_harness_hcom_adapter` = 90 OK re-run at `f2e57b9`. Residual
  (session started+stopped outside the 2000-event lookback → unresolved
  `run_id`) documented and accepted. The remaining item-5 step — the enforced
  `--enforce-canonical-run` pass — is tracked on `CAPABILITY_CHECKLIST.md`
  H5/6.16, not this entry.

## 2026-09-03 — cross-agent scratchpad / fresh-clone contamination
- class: process-gap
- signal: session 24 — 3 concurrently-dispatched agents reported fresh clones
  landing dirty on branch `impl/roadmap-trajectory-check-20` with foreign staged
  files and a stray `main` tip (= #269's head `b52acd1`); the #269 reviewer's
  clone was clean. All deliverables were CI-verified via clean re-derivation, so
  no bad artifact shipped. Root cause UNKNOWN — likely a shared `mktemp` /
  scratchpad path collision or a `git worktree` / `git clone --reference` leak
  between concurrent agents.
- countermeasure: dispatch discipline — every impl/review brief tells the agent
  to `git clone` (or worktree) into a unique `/tmp/<tag>-$$/MAPS_Lean` path and
  never touch `~/Projects/MAPS_Lean`; keep ≤2 parallel impl agents until the root
  cause is found. Session 25 ran hiro/hola/lozo under this discipline with no
  contamination observed. Not yet a mechanical safeguard (rule 20) — a 3rd
  occurrence under the discipline scopes an investigation into the clone/worktree
  path allocation.
- verified: n/a (behavioral, root cause unresolved).
- follow-up: if contamination recurs with unique-path discipline in place,
  investigate `mktemp` / worktree path allocation for concurrent agents.
- 2026-09-03 follow-up (trajectory check #21): **pass 1; no recurrence.** First
  trajectory pass since this landed (#275). This trajectory lane cloned to a
  unique `/tmp/traj21-$$/MAPS_Lean` path per the dispatch discipline and the
  clone landed clean — `git rev-parse origin/main` matched HEAD, no foreign
  staged files, no stray `main` tip. Positive data point vs. the session-24
  observation. Stays open (behavioral, root cause unresolved).
- 2026-09-04 follow-up (trajectory check #23): **CLOSED — 3rd consecutive
  clean pass (pass 2 was recorded in check #22's own note §3.3 prose but
  never appended here as a dated line — corrected now).** This lane's clone
  (`/tmp/traj23-$$/MAPS_Lean`) landed clean: `git rev-parse origin/main` ==
  `HEAD` == `2bcf251`, `git status --porcelain` empty, no foreign staged
  files, no stray `main` tip. 3 clean arcs in a row (#21, #22, #23) per the
  method's "3 clean arcs = closed, not carried a 4th time." A future
  recurrence is a fresh entry, not a re-open.

## 2026-09-03 — coordinator hcom env leaks into `maps recovery-tick`
- class: tool-gap
- signal: running `maps recovery-tick` from the coordinator's own hcom session
  inherits `HCOM_RELAY` / `HCOM_INSTANCE_NAME` / etc. from the coordinator's
  environment, so the tick observes the coordinator's hcom context instead of the
  target routable state.
- countermeasure: the item-5 run recipe (session-24 handoff §"Item 5 run recipe")
  invokes the tick under `env -i` with only the explicitly-needed vars, isolating
  it from the caller's hcom environment.
- verified: n/a (behavioral) — recipe updated 2026-09-03.
- follow-up: if a future `maps` subcommand needs the same isolation, consider a
  `scripts/` wrapper that scrubs `HCOM_*` before exec.
- 2026-09-03 follow-up (trajectory check #21): **pass 1; no recurrence.** First
  trajectory pass since this landed (#275). Countermeasure = `env -i` in the
  item-5 run recipe. Per the #21 dispatch brief the session-26 enforced pass ran
  with "0 incidents" — consistent with the recipe isolating the tick from the
  caller's `HCOM_*` env — but no direct in-repo evidence (the enforced-pass
  results PR was not open at check #21). Stays open (behavioral). #22 confirms
  against the results PR that the tick observed the target routable state.
  (Note: the "2026-09-03 update … Part B landed" paragraph below is a
  copy-paste artefact from the hcom-`list --stopped` entry — it does not
  describe this env-leak entry; left as-is under the append-only rule.)
- 2026-09-03 update (item 5 / option C impl, `impl/item5-optionC-events-stopped-records`):
  **Part B landed.** `HcomAdapter._stopped_records_from_events()` rebuilds stopped-session
  records from `hcom events` (JSONL; `--json` is the default, not a flag — Step-0 finding)
  and merges them under the alive list in the non-JSON `--stopped` fallback. `name → session_id`
  comes from the most recent `status` event for that name carrying non-null `data.session`;
  stop signal from a `life action:stopped` or `status new_status:inactive`. Lookback
  `_STOPPED_EVENTS_LOOKBACK = 2000` events (~6h at observed rate, < read_events cap 5000).
  Frozen regression test `tests/test_hcom_adapter.py::...::test_list_sessions_include_stopped_reconstructs_from_events`.
  Residual gap: a session that started+stopped entirely outside the lookback window still
  yields an unresolved `run_id` (same as Part A, smaller exposure). See
  `work/notes/2026-09-03-item5-optionC-impl.md`.
- 2026-09-04 follow-up (trajectory check #23): **CLOSED — "no exposure" close,
  3rd pass with zero triggering condition (pass 2 recorded in check #22's own
  note prose, never appended here — corrected now).** No `maps recovery-tick`
  / enforced pass ran in any of #21, #22, or #23's arcs, so the leak condition
  never had an opportunity to fire or not-fire this window — this is a "no
  exposure" close per the method's 3-clean-arcs rule, not a "verified fixed
  under load" close. Flagged explicitly so it isn't misread as stronger
  evidence than it is. If a `recovery-tick` run happens before the next
  trajectory pass, take the opportunity to get one real positive-exposure
  verification of the `env -i` recipe.

## 2026-09-03 — coordination_housekeeping.py fully non-functional (gh GraphQL node-budget)
- class: tool-gap
- opened: 2026-09-03
- signal: `python3 scripts/coordination_housekeeping.py BigCatMellow/MAPS_Lean`
  raised `CalledProcessError` on its very first `gh pr list` call — the bulk
  `--json` set included `comments,commits`, and those sub-connections × `--limit
  200` exceed gh's GraphQL node budget ("exceeds maximum limit of 500,000"). The
  script has been dead since it was written; no trajectory pass or coordinator
  caught it, so a "mechanical safety net that runs without an agent tab" was in
  fact never running. A safety net that always crashes is worse than none —
  it looks present.
- countermeasure: PR "coordination tooling fixes" (branch `fix/coordination-tooling`)
  drops `comments`/`commits` from the bulk query (`BULK_PR_FIELDS`) and fetches
  them per-PR via `_attach_pr_details` (`gh pr view <n> --json comments,commits`).
  Regression test `tests/test_coordination_housekeeping.py::OpenPrsQueryTests`
  asserts the bulk field set never re-adds those two connections.
- verified: `python3 scripts/coordination_housekeeping.py BigCatMellow/MAPS_Lean`
  exits 0 and prints a report, 2026-09-03 (against the live repo, 1 open PR).
- follow-up: none. The per-PR enrichment is O(open PRs) extra `gh` calls; if the
  open-PR count ever gets large enough for that to matter, batch it — not a
  concern at current volume.

## 2026-09-04 — circular import runtime/environment <-> runtime/state/environment
- class: drift
- opened: 2026-09-04
- signal: while implementing `scripts/run_tests_sharded.py` (the dispatched-worker
  full-suite stall safeguard, `work/notes/2026-09-04-monitor-stall-mechanical-safeguard-design.md`),
  running each test module in its own subprocess made the four `test_environment_*`
  modules (`fingerprint`, `fingerprint_safety`, `spec`, `validation`) ERROR with
  `ImportError: cannot import name 'EnvironmentFingerprint' from partially
  initialized module 'runtime.environment' (circular import)`. Chain:
  `runtime/environment/__init__.py` -> `.fingerprint` -> `.spec` ->
  `runtime.state.observability` -> `runtime/state/__init__.py` -> `.store` ->
  `.environment` -> back to `runtime.environment`. Full `unittest discover -s
  tests` masks it: an earlier alphabetical module imports `runtime.state` fully
  first, so the cycle resolves. Even `discover -s tests -p "test_environment_*"`
  fails — only the full 96-module run saves it. CI `semantic-eval-tests.yml`
  already runs single modules via `python -m unittest tests.<mod>`, so isolated
  runs are a supported mode that this latent cycle can break.
- countermeasure: `run_tests_sharded.py` imports `WARMUP_IMPORTS =
  ("runtime.state",)` in every shard subprocess before loading the module
  (unconditional, `ImportError` swallowed). Documented as a module constant with
  a pointer here + to the design note "Known limitation" section.
- verified: reproduced 2026-09-04 via per-module `python -m unittest tests.test_environment_spec`
  (ERROR) vs. the same module through the runner with the warmup (PASS); all four
  modules PASS through the runner, 8+2 tests in `tests/test_run_tests_sharded.py`
  green.
- follow-up: **the warmup is a workaround, not the fix.** A separate PR should
  break the cycle (deferred import in `runtime/state/environment.py` or a shared
  lower-level module) and then `WARMUP_IMPORTS` can shrink to `()`. Not done here
  — the impl brief's MUST-NOT list forbids touching existing source.
- 2026-09-04 (fix, PR TBD on open): root cause fixed. `redact_sensitive_text`
  (and its regexes) moved out of `runtime/state/observability.py` into a new
  dependency-free leaf module `runtime/text_redaction.py` (stdlib-only, no
  import from either `runtime.state` or `runtime.environment`).
  `runtime/environment/spec.py` now imports it from there instead of from
  `runtime.state.observability`, so importing `runtime.environment.spec` no
  longer forces `runtime/state/__init__.py`'s full import chain.
  `runtime/state/observability.py` re-exports `redact_sensitive_text` from the
  new module so every existing caller (`runtime/environment/validation.py`,
  `runtime/evaluation/regression_case.py`, `runtime/operational_learning.py`,
  `runtime/recovery/production.py`, `runtime/skills/gate.py`,
  `runtime/state/environment.py`, `runtime/state/outcomes.py`) keeps working
  unchanged, and `redact_sensitive_text` itself is byte-for-byte identical.
  New regression test `tests/test_environment_state_import_isolation.py`
  imports `runtime.environment.spec` (and runs
  `tests.test_environment_spec`) in a fresh subprocess with no warmup import,
  and would have failed before this fix (verified by temporarily reverting
  the source change and re-running it). `scripts/run_tests_sharded.py`'s
  `WARMUP_IMPORTS` shrunk back to `()`; its docstring/comment updated to say
  the cycle is fixed rather than pointing at this entry as an open follow-up.
