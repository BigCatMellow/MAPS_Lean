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
- signal: <what broke / was asked / was clunky — 1-3 lines, concrete>
- countermeasure: <the durable fix — file/mechanism — or "none yet">
- verified: <how + date it was confirmed live, or UNVERIFIED>
- follow-up: <open items, or "none">
```

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
