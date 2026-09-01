# Roadmap trajectory check #16 — arc: `ff37c8a..HEAD`

Sixteenth pass. Predecessor: `work/notes/2026-09-01-roadmap-trajectory-check-15.md`
(arc `dbd786c..HEAD`, PRs #229/#230/#232/#231, action **CONTINUE**, scoreboard
16/13/6 — eighth consecutive; found §2 defect in `flow_handoff`'s
review-independence scope prose, fixed by #235).

## Arc derivation (commit range, per PR #212)

```
$ git log --oneline --grep='Roadmap trajectory check' main | head -1
ff37c8a Roadmap trajectory check #15 (dbd786c..HEAD — PRs #229, #230, #232, #231) (#233)

$ git log --oneline ff37c8a..HEAD
ccbd87e 6.9/S6 slice 2: execution-resource manifest + on-demand loader (#237)
7098ed2 Design note: SEC4 capability granularity (design only) (#238)
2bd9ce1 rule-20 safeguard: context-builder coverage-note drift (Part A + Part B) (#236)
89a8c60 flow_handoff: correct review-independence scope prose (trajectory #15 §2) (#235)
e96bd09 Design note: maps flow release-check (6.21, design only) (#234)
```

Arc = **5 PRs: #234, #235, #236, #238, #237** (within the 3–6 window). 2 impl
(#236 prose-drift safeguard, #237 6.9/S6 slice 2), 2 design notes (#234 release,
#238 capability granularity), 1 one-line prose fix (#235). HEAD `ccbd87e`.

Method (rule 14): every consequential claim re-checked against `git show`, a
read of the merged code, `/usr/bin/grep` over `runtime/` excluding `tests/`, and
`python3 -m runtime.smoke`.

## 0. Situational awareness

- `python3 -m runtime.smoke` → **exit 0 at `ccbd87e`** (`sqlite_task_lifecycle`
  ok, WAL / foreign_keys=1 / busy_timeout=5000).
- Full `tests/` suite is CI's job (machine test-contention — session-17
  targeted-modules protocol); each arc PR merged with green CI, and every arc
  PR carried an independent review-evidence file (`nava` on #234–#238).
- **Scoreboard recounted** from `work/roadmaps/CAPABILITY_CHECKLIST.md` §7 table
  (6.1–6.35 = 35 rows, Status column):
  - **DONE 16** — 6.1, 6.2, 6.3, 6.6, 6.7, 6.8, 6.13, 6.14, 6.15, 6.18, 6.23,
    6.26, 6.27, 6.28, 6.29, 6.30.
  - **IN PROGRESS 13** — 6.4, 6.5, 6.9, 6.10, 6.11, 6.16, 6.19, 6.20, 6.21,
    6.22, 6.24, 6.33, 6.35.
  - **NOT STARTED 6** — 6.12, 6.17, 6.25, 6.31, 6.32, 6.34.
  - **Identical to passes #8–#15. Ninth consecutive pass at 16/13/6.**
  - Arc cross-check: `git diff ff37c8a..HEAD -- CAPABILITY_CHECKLIST.md` touches
    exactly 4 rows (S6, 6.9, 6.11, 6.21) and **all 8 `-`/`+` status tokens read
    `IN PROGRESS`** — no PR in the arc flips a status. Recount agrees with
    16/13/6.

## 1. Carried checks (from the session-17 handoff / check #15 §5)

### Carried check 1 — check #15's "next 3 for #16" all delivered? **YES, all 3.**

| #15 §5 next-3 item | Delivered by | Verified |
|---|---|---|
| (a) 6.9/S6 slice-2 impl | **#237** (`ccbd87e`) | `runtime/skills/format.py::load_skill_resource` exists; `SkillDescriptor.resource_sizes` field; `context_builder.py::_execution_resource_manifest` builds `{"path","kind","size_bytes"}` in the `LOAD` branch after the body attach, **content-free** (no `.open()`/`read_bytes`/`read_text` anywhere in `_select_skills`, lines 355–520; the only `load_skill_resource` mentions in `context_builder.py` are docstring/comment, not a call). `pr-237-review-evidence.md` = APPROVE, 7/7 mutations killed. Follow-up commit `66e108d` (folded into `ccbd87e`) re-scoped `test_memory_trust_gate.py::NonGoalTests` for the slice — see carried check 5. |
| (a) prose-drift safeguard impl | **#236** (`2bd9ce1`) | `scripts/check_coverage_note_pins.py` (AST, `noqa` hatch) + `tests/test_check_coverage_note_pins.py` + `CoverageNoteConsistencyTests` in `test_context_builder.py`; wired as a `run:` step in `.github/workflows/review-evidence.yml:40`. #229's test generalized + removed, not duplicated. `pr-236-review-evidence.md` = APPROVE, 6/6 mutations killed (incl. one demonstrating the consistency test catches the exact #225 regression). |
| (b) §2 `flow_handoff` prose/scope 1-liner | **#235** (`89a8c60`) | `runtime/flow_handoff.py` docstring + `next_step.reason` + the 6.21 checklist clause now state the review-independence disqualification is `from_worker`-continuity-component-wide (global, `continuity_links` has no `task_id`), not task-scoped. No behaviour change. `pr-235-review-evidence.md` = APPROVE. |
| (c) 6.21 `release` design note | **#234** (`e96bd09`) | `work/notes/2026-09-01-6.21-release-design.md` — verdict **PARKED** on 4 §6 operator decisions (summary sink / schema; report persistence; advisory-vs-hard-block; who-may-run). Corrects #224 §1b's "closer to a new capability" — the two dormant evaluators (`evaluate_acquisition_evidence`, `evaluate_benchmark_results`) exist with zero prod callers. `pr-234-review-evidence.md` = APPROVE (the 4 decisions are genuine operator-only calls, not glossed). |

### Carried check 2 — scoreboard re-derived = 16/13/6 (9th consecutive). **CONFIRMED.** §0.

### Carried check 3 — `authorized_operators` (SEC4 B1). **STILL ABSENT.**

`/usr/bin/grep -rn "authorized_operators" runtime/` → no hits. The
`authorized_operators` table + opt-in trust-root check has not landed;
design-pending on the operator trust-root/bootstrap decision (its own
`OPERATOR DECISION REQUIRED` callout in
`work/notes/2026-08-31-sec4-operator-lifecycle-transitions-and-identity-design.md`,
batched with SEC4 Half 3). Unchanged since checks #13/#14/#15.

### Carried check 4 — zombie pid 3874. **STILL ALIVE.**

`ps -o pid,etime,cmd -p 3874` → `ELAPSED 1-17:17:11` (~41 h; ~34 h at #14, ~38 h
at #15 — steadily climbing). It is the session-8 orphan: an
`--permission-mode auto --model sonnet` orchestrator still running the
2026-08-30 session-8 prompt (reads `MAPS_Lean_Handoff_2026-08-30-session8.md`,
wants to triage PRs #173/#174/#178/#179 and wire a `harness_service` into
`RecoverySupervisor` — all long since done). Idle, harmless, but a stray
`auto`-mode agent on the repo. Recorded as **operator-ask #3** in the
operator-ask doc; not a trajectory action, do not act on it. Flagged again here
because it is now 4 consecutive passes and the operator has not killed it.

### Carried check 5 — friction entry 5 recurrence + `feedback_stale_slice_boundary_nongoal_test` judgment.

**Friction entry 5** ("orchestrator tool-use burned ~30–40k context on avoidable
dumps", `verified: n/a (behavioral)`, `countermeasure: none mechanical`): the
#234–#238 arc — 2 design notes, a prose fix, a safeguard, a slice-2 impl — shows
no large-dump behaviour (scoped `git show`, `/usr/bin/grep`, `sed -n` ranges,
`Read` offset/limit throughout; the PR bodies show scoped verification). **5th
consecutive no-recurrence arc; stays open** per its own "if it recurs" clause.
Follow-up line appended.

**`feedback_stale_slice_boundary_nongoal_test`** (2nd occurrence of the same
class: a `NonGoalTests` source-substring assertion — `assertNotIn("X",
context_builder_source)` — that correctly encodes "slice N does not do X" and
then breaks when slice N+1 legitimately introduces X; #221 `load_catalog_skill(`,
#237 `script_paths`/etc.):

- **Both times CI caught it** (the assertion failed on the impl commit; a
  follow-up commit re-scoped). Bounded friction, not an escaped defect.
- **A rule-20 CI safeguard is NOT the right countermeasure**, and PR #232's own
  design note already reasoned this through (§5, "out of scope"): a CI script
  cannot know "this assertion is correct today but the next planned slice will
  legitimately flip it" — that is forward-looking design knowledge, not a
  static property. #232 concluded the class is self-catching and the residual is
  a review-sweep / dispatch discipline.
- **Recommendation:** (i) a `FRICTION_LOG.md` entry (added in this PR) to make
  the 2-occurrence pattern durable and visible; (ii) a one-line **dispatch-time**
  discipline (AGI-standard shape, rule 19), not a CI check: *a dispatch for a
  scope-expanding slice must name the sibling NonGoal / boundary tests the slice
  will legitimately supersede, so the implementer updates them in the same PR
  rather than tripping CI.* The reviewer-side is already covered by memory
  `feedback_review_test_set_too_narrow` / `feedback_stale_slice_boundary_nongoal_test`.
  Not a new mechanical safeguard.

### Carried check 6 — operator-ask runway. **MATERIALLY DEPLETED — this drives the verdict (§3).**

Ask #1 (`maps recovery-tick --enforce-canonical-run` first production pass) is
now **6 consecutive sessions unanswered**. Check #15 §5 pre-registered: *"if ask
#1 is not answered before check #16 / #17, the next trajectory pass should treat
'no independent slices left AND ask #1 still open' as a genuine RESEARCH/STOP-level
signal."*

Inventory of what remains dispatchable **without** ask #1 (or any other operator
decision), after this arc:

| Candidate | Ask-#1-independent? | Ready? |
|---|---|---|
| **SEC4 capability granularity impl** (#238 §2/§6 — remove `network-read` from `_SATISFYING_TOKENS`; add `filesystem-write:<path>` token vocab+parsing) | Yes (#238 §5: no operator decision required) | **Yes — 1 clean impl slice, ready now** |
| **SEC4 `filesystem-write:<path>` → `task["output_paths"]` enforcement** (#238 §4 — the deferred second intersection axis) | Yes | Needs its own small design note, then impl (~1 design + 1 impl) |
| 6.9/S6 slice 3 — execution-level *content* loading via a real `load_skill_resource` consumer | Yes in principle | **No** — needs the provider-session-injection seam, which `flow_start` deliberately excludes (#237 design "out of scope"); a bigger design decision, not a clean slice |
| 6.9/S6 frozen selection eval (the actual 6.9 DONE gate) | Yes | **No** — a substantial, unscoped L4/EXP-B-adjacent effort (RESEARCH-shaped) |
| 6.21 `flow release-check` impl | **No** — PARKED on 4 operator decisions (#234 §6) | — |
| 6.21 `recover` | **No** — operator + `reviews`-schema decision (#224 §1a) | — |
| SEC4 B1 `authorized_operators` | **No** — operator trust-root decision | — |
| 6.22 `MemoryProvenanceGuard` first production exposure | Effectively no — needs a `HarnessService.send()` production caller, the same "compose + expose a guard" shape ask #1 gates | — |
| 6.11 `MAY_LOAD` tier | **No** — "still no data source" | — |
| 6.19 / 6.20 (helper health / NO_PROGRESS recovery action) | Yes but large — needs provider integration | **No** — not a slice |
| operator ask #2 (env-evidence-writer ratification), operator ask #3 (kill pid 3874) | **No** — operator | — |

**Net:** the ask-#1-independent dispatchable runway is down to **one ready impl
slice (#238 granularity) plus one small design→impl pair (#238 §4)**. That is
roughly one more arc. Everything else on the board is (a) an operator decision
(ask #1, the release-check batch, SEC4 B1 trust-root, asks #2/#3), or (b) a
substantial research/scoping effort with no current owner (6.9 frozen eval,
6.11 data source, provider integration for 6.19/6.20).

Check #15's pre-registered condition ("*no* independent slices left") is not yet
strictly met — but the trend is unambiguous and one arc from meeting it. Five
consecutive passes of a static 16/13/6 scoreboard, with the security cluster
(6.4/6.5/6.16/6.22 + H5/E4/L6 — **7 rows**) frozen behind one ungiven decision
across six sessions, is no longer plausibly "the designed shape". It is a
project waiting on an operator.

## 2. What changed (materially)

1. **The prose-drift pattern is now mechanically guarded** (#236) — Part A
   (consistency test, catches a known-bad claim reverting) + Part B
   (`check_coverage_note_pins.py`, forces a new `coverage` note to be
   test-pinned) + a CI step. The `_select_skills`/coverage-note drift that hit
   #225 (uncaught) and was found by check #14 cannot recur silently. First
   mechanical countermeasure for the "runtime prose describes an invariant the
   code no longer honours" class.

2. **6.9/S6 reached the "execution" level for listing** (#237) — a `LOAD` Skill's
   plan item now carries an `execution_resources` manifest (path/kind/size, no
   content); `load_skill_resource` is the deterministic single-file pull for a
   downstream consumer. 6.9 does **not** flip — the DONE gate (progressive-
   disclosure value shown in a frozen eval; content still pull-not-push; no real
   `load_skill_resource` consumer) is unmet. But the loading half of 6.9 is now
   substantially built across slices 1+2.

3. **The 6.21 verb set is design-complete for what can ship without the operator.**
   `start` / `review-start` / `review-record` / `handoff` are implemented;
   `release-check` is designed and PARKED (#234, 4 operator decisions); `recover`
   is PARKED (operator + schema). There is no more 6.21 code to write that does
   not first need an operator decision.

4. **The independent-work runway is one arc from empty** (§1 carried check 6).
   This is the material change this pass records.

## 3. Trajectory action: **REPRIORITIZE**

Not CONTINUE (checks #13–#15). Reasoning:

1. **The pre-registered trend condition is essentially met.** Check #15 named
   "no independent slices left AND ask #1 open" as a RESEARCH/STOP signal. We
   are at "≈1 arc of independent slices left AND ask #1 open for 6 sessions".
   Waiting for the condition to be *strictly* met wastes the one arc of runway.

2. **The bottleneck is no longer "find more small independent work" — it is
   "the operator must decide".** Continuing to dispatch guarded-default-off
   slices produced 5 static passes; the surface those rows need is *built*
   (checks #14/#15 established this). REPRIORITIZE the work order:

   ### Concrete reprioritization

   - **(3a) Dispatch the last ask-#1-independent slices now** — SEC4 capability
     granularity impl (#238 §6), then the #238 §4 `filesystem-write:<path>` →
     `output_paths` design + impl. These are real and should not sit idle.
   - **(3b) Escalate the operator decisions as a *blocking batch*, this session,
     not a 7th "re-surface".** The batch:
     - **Ask #1** — authorize (or decline) one `maps recovery-tick
       --enforce-canonical-run --repo-root <checkout>` pass against one named
       project. Unblocks 6.4 / 6.5 / 6.16 / 6.22 + H5 / E4 / L6 (7 rows). Expected
       first-run effect: some working resumes become `resume_denied`
       (`LEASE_EXPIRED` most likely), remediated per `docs/CONTROL_PLANE_SETUP.md`
       §5.
     - **The #234 `flow release-check` batch** — 4 decisions (summary sink /
       whether a new `release_checks` table; report persistence; advisory vs
       hard-block; who-may-run). Unblocks the last unshippable 6.21 verb.
     - **SEC4 B1 trust-root** — the `authorized_operators` opt-in/default-off
       decision. Unblocks SEC4 Half 3.
     - **Ask #2** (env-evidence-writer ratification) and **ask #3** (kill pid
       3874) — already open, low-stakes, batch them in.
   - **(3c) Scope the two research-shaped items** so that *if* the operator
     batch stalls further, check #17 has a RESEARCH lane to open rather than
     idling: (i) 6.9/S6 frozen selection eval (the 6.9 DONE gate); (ii) the
     provider-session-injection seam that 6.9 slice 3 and 6.19/6.20 both need.

3. **REPRIORITIZE stays inside the approved envelope.** It changes work order
   and escalates already-open asks; it does not change the objective, scope, or
   permission envelope, and needs no human reauthorization *to record*. It does
   need the operator to actually answer the §3b batch — that is the point.

**No CUT SCOPE / STOP / ADD.** The roadmap is still pointing at DONE; the route
now runs through an operator decision the project has deferred five times.

## 4. Tenth-Seat / §7 duty (`TENTH_SEAT_REVIEW.md` §2 Trigger 2, §7)

Trigger 2 is **armed** (passes #14 and #15 each found a substantive finding).

**It does not fire this pass.** §1 carried check 6 / §2 item 4 / §3 is a
substantive, foundational finding: the route to DONE for 7 roadmap rows now
depends on an operator decision, the independent-work buffer that masked this
for five passes is one arc from empty, and the trajectory action changes from
CONTINUE to REPRIORITIZE as a direct result. That is a "changed picture" in the
§7 sense (a foundational claim about the route to DONE), not "challenging
detail". Per the dispatch, `@soda` is flagged to confirm this read before any
Tenth-Seat sub-dispatch — this pass does **not** self-initiate one.

§7 "signs this has gone wrong", checked (no minority reports have ever
accumulated):

- *"same conclusion every pass regardless of evidence"* — the scoreboard number
  is identical for a 9th pass, but the **verdict moved**: CONTINUE (#13, #14,
  #15) → **REPRIORITIZE** (#16), driven by a fresh inventory of the remaining
  ask-independent runway, not inertia. This is exactly the evidence-driven
  move check #15 pre-registered.
- *"verdict drifting toward reassurance"* — the opposite: this is the least
  reassuring pass since #12's REPRIORITIZE. It says the roadmap cannot make
  security-cluster progress without the operator and the workaround is nearly
  exhausted.
- *"no one has run the full check"* — arc range-derived; all 5 PRs read at the
  code level (3 of them re-reviewed here beyond the review-evidence files);
  the runway inventory required walking every IN PROGRESS + NOT STARTED row's
  blocker, not re-reading the scoreboard.
- *"the seat challenges detail and never a foundational claim"* — §3 is
  foundational (the route to DONE), not "should a row say DONE".

No Tenth-Seat sub-agent dispatched — flagged to `@soda`; Trigger 2 negative in
this pass's judgment.

## 5. Friction-log consumption

Log walked in full (5 entries; **no new capture entries** since #14, but this
pass **adds one** — see carried check 5).

| # | Entry | `verified:` | Disposition |
|---|-------|-------------|-------------|
| 1 | self-clear resume prompt dropped | END-TO-END | **Closed.** This session (`nava`, session 18) started with the latest handoff injected as SessionStart context. 7th confirmation. |
| 2 | coordinate-via-helper-lanes preference | verified | **Closed.** `soda` (session 18) dispatching lanes; the whole #234–#238 arc ran this way. |
| 3 | context-rotation checkpoint too small | VERIFIED (per #14) | **Closed — no re-open.** |
| 4 | triage loop procedure-only | VERIFIED | **Closed.** Consumption duty discharged for a 7th consecutive pass (#10–#16). |
| 5 | orchestrator tool-use burned ~30–40k context | n/a (behavioral), `countermeasure: none yet` | **Consumed — 5th consecutive no-recurrence arc; stays open.** Follow-up line appended. |
| **6 (NEW)** | stale slice-boundary `NonGoalTests` assertions | `verified: END-TO-END (twice — CI caught both)` | **Added this pass** (carried check 5): 2nd occurrence of the class (#221, #237). `countermeasure:` a dispatch-time discipline (name the boundary tests a scope-expanding slice supersedes) — NOT a rule-20 CI script (#232 §5 established a CI check cannot see "correct now, stale next slice"). Reviewer-side already in memory. |

Nothing in the log needs escalation to trajectory work beyond the operator batch
already in §3b.

## 6. Recorded for the next pass (check #17)

- **Arc anchor for check #17:** the squash commit of *this* PR. `git log
  --oneline --grep='Roadmap trajectory check' main | head -1` then `<that>..HEAD`.
- `python3 -m runtime.smoke` exit 0 at `ccbd87e`.
- Scoreboard: 16 / 13 / 6 — **ninth** consecutive pass. Tenth-Seat Trigger 2
  armed, **did not fire** (§4 — substantive runway finding); re-arms for #17.
- **REPRIORITIZE not yet fully executed** — check #17 verifies: (a) the §3b
  operator batch was put to the operator and what came back; (b) #238 granularity
  impl + the §4 slice landed; (c) whether a RESEARCH lane (§3c) had to open.
  **If the §3b batch is still unanswered at #17 AND §3a is exhausted, that is a
  genuine STOP-condition on the security cluster** — check #17 should say so
  plainly, not REPRIORITIZE a third time.
- Cluster blocked on operator ask #1: **7 rows** (6.4 / 6.5 / 6.16 / 6.22 / H5 /
  E4 / L6). Verify all 7 hard before any flip if the ask lands.
- `authorized_operators`: still absent — re-check.
- Zombie pid 3874: still alive (~41 h). Operator-ask #3.
- Friction: entries 1–4 closed; entry 5 open (5th no-recurrence arc); entry 6
  new (dispatch-discipline countermeasure — check it was actually adopted).

## Resume prompt

You are running roadmap trajectory check #17 for MAPS_Lean. Follow
`playbook/ROADMAP_TRAJECTORY_CHECK.md` (5-step + friction-log consumption) and
`playbook/TENTH_SEAT_REVIEW.md` §7 (read it before recording any clean result).
Worktree off `origin/main`; `git fetch origin main` first.

Arc: anchor = `git log --oneline --grep='Roadmap trajectory check' main | head -1`
(the check-#16 squash commit), then `git log --oneline <anchor>..HEAD`. Do NOT
hand-list (standing rule, PR #212).

Method (rule 14): no claim from a PR title/body/review summary; re-verify against
`git show`, a read of the merged code, `/usr/bin/grep` over `runtime/` excluding
`tests/`, and a test run (targeted-modules per the coordinator's current
contention protocol; full suite is CI's). `python3 -m runtime.smoke` must exit 0.

Specifically check: (a) **Was the check-#16 §3b operator batch put to the
operator, and what came back?** — ask #1 (`--enforce-canonical-run` first pass),
the #234 `flow release-check` 4-decision batch, SEC4 B1 trust-root, asks #2/#3.
If ask #1 landed, verify 6.4/6.5/6.16/6.22 + H5/E4/L6 (7 rows) HARD before any
flip. (b) Did the check-#16 §3a slices land — SEC4 capability granularity impl
(#238 §6), the #238 §4 `filesystem-write:<path>`→`output_paths` design+impl?
(c) **If the §3b batch is STILL unanswered AND §3a is exhausted with no new
ask-independent slice identified → this is a STOP-condition on the security
cluster. Say so plainly; do not REPRIORITIZE a third time.** (d) Did a RESEARCH
lane (§3c: 6.9 frozen eval, or the provider-session-injection seam) get opened?
(e) Re-derive 16/13/6. **Trigger 2 re-armed** (#15, #16 both found something) —
a genuinely clean #17 fires it: flag the coordinator BEFORE dispatching a
Tenth-Seat sub-agent, then write `work/reviews/trajectory-17-minority-report.md`.
(f) Friction entry 5 (recurrence) + entry 6 (was the dispatch discipline
adopted?). (g) `authorized_operators`. (h) Zombie pid 3874.

Deliverable: `work/notes/2026-XX-XX-roadmap-trajectory-check-17.md` (+
friction-log follow-up lines, + minority report iff Trigger 2). Update
`CAPABILITY_CHECKLIST.md` ONLY if a status genuinely moved (hard evidence) or a
clause is provably wrong (prose fix — flag the coordinator before any status
flip).

Workflow: own worktree; PR into `main` (never push); verification-only review;
do NOT spawn your own reviewer — ping the coordinator; no self-merge; report the
PR number to the coordinator.

STOP + flag the coordinator if: the §3b batch is unanswered and §3a is exhausted
(a STOP-condition on the security cluster — record it, do not paper over it); a
status claim is wrong in a way that changes the route to DONE; the trajectory
action would be STOP or an envelope-leaving REPRIORITIZE; §7 signals the check
has gone shallow; or before dispatching the Tenth-Seat sub-agent.
