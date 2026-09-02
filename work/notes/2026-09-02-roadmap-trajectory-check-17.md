# Roadmap trajectory check #17 — arc: `6ea81b2..HEAD`

Seventeenth pass. Predecessor: `work/notes/2026-09-01-roadmap-trajectory-check-16.md`
(arc `ff37c8a..HEAD`, PRs #234/#235/#236/#238/#237, action **REPRIORITIZE**,
scoreboard 16/13/6 — ninth consecutive; substantive finding: the independent-work
runway was ~1 arc from empty and 7 security-cluster rows were frozen behind an
unanswered operator batch. Tenth-Seat Trigger 2 armed, did not fire.)

## Arc derivation (commit range, per PR #212 — never hand-listed)

```
$ git log --oneline --grep='Roadmap trajectory check' main | head -1
6ea81b2 Roadmap trajectory check #16 (ff37c8a..HEAD — PRs #234-#238) (#240)

$ git log --oneline 6ea81b2..origin/main
070dc65 6.9/S6: EXP-B expanded frozen Skill-selection evaluation (25-case corpus) (#246)
7a466eb 6.21: maps flow release-check — compose artifact-identity + release-smoke evidence (#244)
ffbf71c Operator answered the trajectory-#16 decision batch (session 17) (#243)
891045e Design note: 6.9/S6 frozen Skill-selection evaluation — scoping (#241)
5d4a9f2 SEC4 capability granularity: network-read split + filesystem-write:<path> token (#242)
```

Arc = **5 PRs: #242, #241, #243, #244, #246** (within the 3–6 window). 2 impl
(#242 capability-granularity, #244 `flow release-check`), 2 design notes (#241
6.9 frozen-eval scoping, #246 is impl not design — corrects to: #246 the 25-case
frozen corpus + test, #241 the scoping note), 1 operator-decision record (#243).
Re-tally: **#242 impl, #241 design note, #243 operator-answers record, #244 impl,
#246 impl (corpus + frozen test).** HEAD `070dc65`.

**#245 (SEC4 Half 3 slice 1) is NOT in this arc** — luve APPROVE, rebased to tip
`d86c6f2`, MERGEABLE, awaiting `gh pr merge`. In-flight, counts toward #18's arc.
Also in-flight for #18's horizon: **#249** (release-check 3b scoping), **#250**
(6.9/S6 NO-FLIP decision), **#251** (SEC4 Half 3 slice 2 scoping).

Method (rule 14): every consequential claim re-checked against `git show`, a read
of the merged code, `/usr/bin/grep` over `runtime/` excluding `tests/`, targeted
`unittest` modules (session-17 contention protocol — full `tests/` is CI's job),
and `python3 -m runtime.smoke`.

## 0. Situational awareness

- `python3 -m runtime.smoke` → **exit 0 at `070dc65`** (`sqlite_task_lifecycle`
  ok, WAL / foreign_keys=1 / busy_timeout=5000).
- Each arc PR merged with green CI + an independent review-evidence file
  (`nava` on #243; `vame` on #242; `luve` on #246; #244 carries
  `pr-244-review-evidence.md`).
- **Scoreboard recounted** from `work/roadmaps/CAPABILITY_CHECKLIST.md` §7
  (6.1–6.35, Status column, parsed `awk -F'|' '{print $2, $4}'`):
  - **DONE 16** — 6.1, 6.2, 6.3, 6.6, 6.7, 6.8, 6.13, 6.14, 6.15, 6.18, 6.23,
    6.26, 6.27, 6.28, 6.29, 6.30.
  - **IN PROGRESS 13** — 6.4, 6.5, 6.9, 6.10, 6.11, 6.16, 6.19, 6.20, 6.21,
    6.22, 6.24, 6.33, 6.35.
  - **NOT STARTED 6** — 6.12, 6.17, 6.25, 6.31, 6.32, 6.34.
  - **Identical to passes #8–#16. Tenth consecutive pass at 16/13/6.**
  - Arc cross-check: `git diff 6ea81b2..HEAD -- CAPABILITY_CHECKLIST.md` touches
    the **6.9** and **6.21** evidence-text cells only; every status token on both
    the `-` and `+` side reads `IN PROGRESS`. The `DONE` / `BLOCKED` substrings in
    that diff are all inside prose ("flipping 6.9/S6 to DONE … **no status flip
    here**"; "`policy_gate` … BLOCKED"). **No PR in the arc flips a status.**

## 1. Carried checks (from the @soda dispatch #81390)

### Carried check 1 — the operator answered the whole #16 §3b blocking batch (#243). **CONFIRMED — and each answered item is being acted on correctly.**

`git show ffbf71c` → `work/notes/OPERATOR_ASK_2026-08-31-session13.md` gains a
"SESSION 17 (`luve`) — OPERATOR ANSWERED" block. Operator instruction: *"Go
ahead and do all those things"* against the enumerated batch with a recommended
answer per item. Per-item disposition:

| Batch item | Operator answer | Acted on? |
|---|---|---|
| **Ask #1** — first `--enforce-canonical-run` pass | **AUTHORIZED**, one pass; target/timing pinned by coordinator; **`.maps/` does not exist in this checkout** → control-plane DB + `--harness-project-id` setup is a coordinator prerequisite *before* any enforced pass; no impl/review agent runs it autonomously | **Not yet — correctly.** `ls .maps` → absent. `git log --all --grep='enforce-canonical-run\|recovery-tick' 6ea81b2..` → **no arc commit ran an enforced pass.** The prerequisite (control-plane setup) has **no owner assigned yet** — see §2.3. |
| **`flow release-check` batch** (#234 §6) | new append-only `release_checks` table; persist evaluator `report_ref`s; `composite==BLOCKED` **advisory**; any party may run | **DONE — #244.** `runtime/state/release_check.py` mixin + `release_checks` table (schema.sql, `id`-keyed, `(task_id, review_id, id)` index, no-update/no-delete triggers) + `runtime/flow_release_check.py` + `maps flow release-check`. `composite = BLOCKED` iff an aggregate is `FAIL`, records no verdict, does not gate `record_review`. Matches the answer exactly. 6.21 stays IN PROGRESS. |
| **SEC4 B1** `authorized_operators` | opt-in real check, one site, **default off**; no rows → disabled (fail-open); genesis at `maps init`; separate `maps operator add` for later rows | **In-flight — #245** (luve APPROVE, merge pending). `authorized_operators` + `authorized_operator_revocations` tables, `AuthorizedOperatorStorageMixin`, `maps operator add|revoke|list`, genesis via `maps init --operator`, opt-in-by-data check on `maps skill approve`. Matches the answer. |
| **Ask #2** — env-evidence-writer authority ratification | **YES**; no Q4 fallback slice | **DONE — no runtime change needed** (RESOLVED per PR #207; see memory `project_env_evidence_writer_authority_redecision`). |
| **Ask #3** — kill zombie pid 3874 | **AUTHORIZED**; operator runs `kill 3874` | **DONE.** `ps -o pid,etime,cmd -p 3874` → **"NOT RUNNING"** (dead; was ~41 h at #16). |
| Infra #2 / #3 — worktree + stale-branch cleanup | **not in the answered batch** — still pending operator | still open (44 classifier-blocked `git worktree remove` / `git branch -D` + 5 stale remote branches). |

The #16 REPRIORITIZE's central demand — put the batch to the operator as a
blocking decision, not a 7th re-surface — **succeeded**. This is the material
change this pass records.

### Carried check 2 — scoreboard re-derived. **CONFIRMED 16/13/6 (10th consecutive).** §0.

- **#250 (6.9/S6) is a NO-FLIP decision** — 6.9 stays IN PROGRESS. Verified: the
  merged #246 checklist diff keeps `6.9 | … | IN PROGRESS` and the evidence text
  itself says "flipping 6.9/S6 to DONE … is a separate reviewer gate step —
  **no status flip here**". #250 (in-flight PR) formalises the NO-FLIP; nothing
  to verify beyond "6.9 did not move", which holds.
- **#244 / #245 / #246 all claim no status flip** — verified: only 6.9 and 6.21
  *evidence text* changed in the arc; both stay IN PROGRESS.

### Carried check 3 — runway re-assessment. **THE ROADMAP IS HEALTHY AGAIN; the bottleneck moved from "operator decision" to "one coordinator prerequisite task (Ask #1 control-plane setup)".**

The #16 finding was "≈1 arc of ask-independent slices left AND the operator
batch open 6 sessions". The batch is now answered. Re-inventory of dispatchable
work:

| Candidate | Blocked on? | Ready? |
|---|---|---|
| **SEC4 Half 3 slice 1** (`authorized_operators`) | nothing — operator answered | **#245, done, merge-pending** |
| **SEC4 Half 3 slice 2** (widen the operator gate to `activate`/`retire`/`supersede`) | nothing — no schema, no operator decision | **#251 scoping done; 1 clean impl slice next** |
| **`flow release-check` 3b** (composite==BLOCKED → hard approval gate) | authority-model change → needs the operator's nod on the gate itself | **#249 scoping in-flight** — surfaces the operator decision |
| **SEC4 `filesystem-write:<path>` → `output_paths` enforcement** (#238 §4) | nothing | needs a small design note, then impl |
| **Ask #1 first enforced pass** — unblocks 6.4/6.5/6.16/6.22 + H5/E4/L6 (**7 rows**) | **the control-plane-setup prerequisite** (`.maps/` DB + `--harness-project-id` per `docs/CONTROL_PLANE_SETUP.md`) — a coordinator task, plus a final operator timing nod | **not started; no owner assigned** |
| 6.9/S6 → DONE | the frozen eval now EXISTS (#246) + covers 6 categories, but scores 0.00 on VOCABULARY_SHIFT / HARD_NEGATIVE / AMBIGUOUS — the selector fails half the categories §6.9 requires | **#250 = NO FLIP.** Remaining: a better selector, or an operator-signed lower bar. RESEARCH-shaped, no owner. |
| 6.11 `MAY_LOAD` tier | still no data source | no |
| 6.19 / 6.20 recovery actions | provider integration | large, no |

**Net:** the ask-independent runway is **restored to several arcs** (SEC4 Half 3
slice 2, the #238 §4 slice, release-check 3b once #249 surfaces the decision).
The one hard dependency for the biggest prize — the 7-row security cluster —
is now a **single concrete coordinator task** (`.maps/` control-plane setup),
not an open-ended operator decision. That is a qualitatively better position
than #16.

### Carried check 4 — the standing "`/usr/bin/grep -rn authorized_operators runtime/` → NOTHING" check. **STILL NOTHING on `main` — but only because #245 is not merged yet.**

`/usr/bin/grep -rn "authorized_operators" runtime/` on `origin/main` `070dc65`
→ **0 hits** (unchanged since #13/#14/#15/#16). The table + mixin exist on the
**#245 branch** (`origin/worktree-sec4-half3` `d86c6f2`:
`runtime/state/authorized_operator_storage.py` + `schema.sql`). **Check #18
MUST re-run this on `main`** — once #245 merges it flips to "finds the storage
module + schema + the `maps operator` CLI dispatch"; the standing check text
should be updated then, not now.

### Carried check 5 — merge-authority stall (memory `project_merge_authority_stall_session19`). **RECURRING. Recommend a rule-20 durable countermeasure.**

- Session 18→19: PRs #243/#244/#245/#246 sat reviewed+APPROVED with `main`
  frozen at `891045e` for **5h+** with no coordinator/merge-authority seat
  (soda/mepo/rozo all dropped mid-session-17). Peer agents (nava/luve/vame/gela)
  can author + review + commit evidence but **`gh pr merge` is in no peer's
  authority**. The queue drained only when the operator merged + `soda`'s seat
  returned.
- This is the **third** coordination-gap incident in the session-17→19 arc
  (see also the concurrent #245-rebase race this session — two agents
  force-pushed the same branch because merge-prep ownership was ambiguous during
  the gap; recorded in memory `feedback_concurrent_rebase_race_pr245`).
- Per rule 20 (a failure that repeats gets a *mechanical* safeguard, not another
  instruction): **RECOMMEND** a standing written rule — *"merge authority and
  merge-prep ownership when the coordinator seat lapses"* — added to
  `AGENTS.md` or the session-handoff template. Concretely: (a) a named
  fallback-authority order (e.g. the longest-running peer lane holds
  merge-prep — rebasing, evidence-binding — but NOT `gh pr merge`); (b)
  `gh pr merge` stays operator-only, and the fallback lane's job is to keep every
  PR *merge-ready and non-conflicting* so the operator's merge is one command;
  (c) "claim the rebase in-channel before force-pushing a shared PR branch" as an
  explicit line. This is an **operator decision to adopt** (it touches the
  authority model) → flag it in the next decision batch, do not self-adopt.

### Carried check 6 — friction entry 5 recurrence + entry 6 (`feedback_stale_slice_boundary_nongoal_test`).

**Friction entry 5** ("orchestrator tool-use burned ~30–40k context on avoidable
dumps", `verified: n/a (behavioral)`, `countermeasure: none mechanical`): the
#241–#246 arc — a design note, an operator-answers record, two impl PRs, a corpus
— shows no large-dump behaviour (this trajectory lane and the arc PR bodies all
use scoped `git show` / `/usr/bin/grep` / `sed -n` ranges / `Read` offset+limit).
**6th consecutive no-recurrence arc; stays open** per its own "if it recurs"
clause. Follow-up line appended.

**Friction entry 6** (`feedback_stale_slice_boundary_nongoal_test`, 2nd
occurrence at #16): the check-#16 follow-up asked #17 to verify the **dispatch
discipline** ("a scope-expanding-slice dispatch names the sibling NonGoal /
boundary tests it will supersede") was adopted.

- **No clean test case this arc** — none of #241–#246 was a scope-expanding
  `_select_skills` / `context_builder` slice with `NonGoalTests` substring-assert
  risk (design notes + an operator record + a corpus + a policy-token impl that
  touched `gate.py` / `capability_policy.py`, not the banned-substring tests).
- **The discipline IS being applied prospectively:** the #251 SEC4 Half 3
  slice-2 scoping note's §3 Stop-conditions explicitly names the boundary this
  slice supersedes — *"If any existing test asserts an unauthorized actor can
  `activate`/`retire`/`supersede` against a seeded registry → that is the old
  narrow contract; update it (this slice deliberately changes it)."* That is
  exactly the dispatch-time shape the countermeasure calls for.
- **Disposition:** entry 6 stays open; check #18 gets the first real test —
  the #251 slice-2 impl PR. If it lands without a CI-red boundary-test trip,
  the discipline held. If a 3rd occurrence lands *with* the discipline in place,
  re-open for a mechanical-safeguard discussion (per the entry's own clause).

## 2. What changed (materially)

1. **The #16 operator batch is answered (#243)** — the single largest positive
   change since #12. Ask #1 AUTHORIZED, the release-check 4-decision batch
   ACCEPTED, SEC4 B1 ACCEPTED, Ask #2 YES, Ask #3 DONE. The five-pass frozen
   16/13/6 scoreboard was, as #16 argued, "a project waiting on an operator" —
   and the operator has now answered.

2. **Two of the answered decisions are already implemented** — #244 (`flow
   release-check` + `release_checks` table, exactly per the accepted answer) and
   #245 (SEC4 B1 `authorized_operators`, opt-in default-off, in-flight). The
   answer-to-impl latency was one session.

3. **The security-cluster blocker changed shape** — from "an open-ended operator
   decision" to "one concrete coordinator prerequisite task": establish the
   `.maps/` control-plane DB + `--harness-project-id` in a real checkout, then
   run one `maps recovery-tick --enforce-canonical-run` pass. This is
   dispatchable coordinator work, not a waiting game. **It has no owner yet** —
   that is the one gap this pass surfaces.

4. **The frozen selection eval exists (#246)** — the 6.9 DONE-gate artifact the
   roadmap has wanted since S4. It does its job: it measures the token selector
   as **weak** (f1 0.722, 0.00 on 3 of 6 categories) and pins that, rather than
   letting 6.9 flip on a document. #250 correctly records NO FLIP.

5. **Merge-authority gaps are now a 3-incident pattern** (§1 carried check 5) —
   worth a durable rule, flagged as an operator decision.

## 3. Trajectory action: **CONTINUE**

Not REPRIORITIZE (that was #16, and it is now substantially executed — batch
answered, §3a slices landed/in-flight). Not STOP (the #16 resume prompt named a
STOP-condition only *"if the §3b batch is STILL unanswered AND §3a is
exhausted"* — the batch is answered; that condition is not met). Reasoning:

1. **The #16 REPRIORITIZE worked.** The work order it set — dispatch the last
   ask-independent slices, escalate the operator batch as blocking — produced
   #242 (granularity impl), a merged operator-answers record, #244, and the
   in-flight #245/#249/#250/#251. The roadmap is executing again.

2. **The dispatchable runway is restored** (§1 carried check 3): SEC4 Half 3
   slice 2 (#251 → impl), the #238 §4 `filesystem-write:<path>`→`output_paths`
   slice, release-check 3b once #249 surfaces its decision. Several arcs of
   ask-independent work, not one.

3. **The one new bottleneck is small and concrete** — the Ask #1 control-plane
   prerequisite (§2.3). It needs a coordinator to (a) stand up `.maps/` +
   register a `--harness-project-id` per `docs/CONTROL_PLANE_SETUP.md`, (b)
   confirm timing with the operator, (c) run one enforced pass, (d) hand #18 the
   result for a 7-row (6.4/6.5/6.16/6.22 + H5/E4/L6) verification. **Recommend
   @soda assign this as its own lane now** — it is the highest-leverage single
   task on the board (7 rows) and it is not blocked on anything but someone
   picking it up.

4. **No CUT SCOPE / ADD.** The roadmap still points at DONE; the route runs
   through (a) merging #245, (b) the Ask #1 control-plane lane, (c) the SEC4
   Half 3 slice-2 + release-check-3b + #238-§4 slices in parallel.

### Recommended dispatch (for @soda)

- **Lane 1 — Ask #1 control-plane prerequisite** (highest leverage, 7 rows,
  unowned). Coordinator-run per the #243 answer's explicit "coordinator runs the
  operator workflow" clause.
- **Lane 2 — SEC4 Half 3 slice 2 impl** (per #251, after #245 merges).
- **Lane 3 — #238 §4 `filesystem-write:<path>` → `output_paths` design note**,
  then impl.
- Merge queue: land #245, then #249/#250/#251 as they clear review.

## 4. Tenth-Seat / §7 duty (`TENTH_SEAT_REVIEW.md` §2 Trigger 2, §7)

Trigger 2 is **armed** (passes #15 and #16 each found a substantive finding).

**It does not fire this pass.** This pass has substantive findings — the
operator batch is answered (a "changed picture" in the §7 sense: it resolves the
foundational claim #16 made about the route to DONE), the security-cluster
blocker changed shape and gained a concrete owner-less prerequisite (§2.3), and
merge-authority gaps are now a durable-countermeasure-worthy 3-incident pattern
(§1.5). The verdict moves CONTINUE, but not from inertia — from the #16
REPRIORITIZE having executed. **Per the dispatch, this pass is NOT "trending
clean", so no @soda pre-flag for a Tenth-Seat sub-dispatch is required, and none
is initiated.**

§7 "signs this has gone wrong", checked (no minority reports have ever
accumulated):

- *"same conclusion every pass regardless of evidence"* — scoreboard number
  identical for a 10th pass, but the **picture moved decisively**: the operator
  answered, two decisions shipped, the blocker became a concrete task. The
  verdict is CONTINUE because REPRIORITIZE already happened and worked — the
  opposite of inertia.
- *"verdict drifting toward reassurance"* — this pass IS more reassuring than
  #16, and that is warranted: the thing #16 was alarmed about (a project frozen
  behind an unanswered operator) is resolved. It is not glossing — §2.3 names an
  unowned prerequisite and §1.5 escalates a recurring authority gap.
- *"no one has run the full check"* — arc range-derived; all 5 PRs read at code
  level (#242 token diff, #244 schema + mixin, #243 operator-answers doc, #246
  corpus + frozen test run); the runway inventory walked every IN PROGRESS +
  NOT STARTED row's blocker.
- *"the seat challenges detail and never a foundational claim"* — §2.1 / §2.3
  are foundational (the route to DONE for the security cluster), not "should a
  row say DONE".

No Tenth-Seat sub-agent dispatched — Trigger 2 negative in this pass's judgment,
substantive findings present.

## 5. Friction-log consumption

Log walked in full (6 entries; no new capture entries this pass).

| # | Entry | `verified:` | Disposition |
|---|-------|-------------|-------------|
| 1 | self-clear resume prompt dropped | END-TO-END (×3) | **Closed.** This session started with `MAPS_Lean_Handoff_2026-09-01-session18.md` injected as SessionStart context — 8th confirmation. |
| 2 | coordinate-via-helper-lanes preference | verified | **Closed.** `soda` (seat back) + nava/luve/gela/vame lanes; the whole #241–#246 arc + the coordination-gap self-organization ran this way. |
| 3 | context-rotation checkpoint too small | VERIFIED (#14) | **Closed — no re-open.** (`limit_watcher` "context_rotation.py" messages this session correctly ignored per memory `feedback_limit_watcher_hcom`.) |
| 4 | triage loop procedure-only | VERIFIED | **Closed.** Consumption duty discharged for an 8th consecutive pass (#10–#17). |
| 5 | orchestrator tool-use burned ~30–40k context | n/a (behavioral), `countermeasure: none yet` | **Consumed — 6th consecutive no-recurrence arc; stays open.** Follow-up line appended. |
| 6 | stale slice-boundary `NonGoalTests` assertions | `END-TO-END (twice — CI caught both)` | **Consumed — no clean test case this arc; the dispatch discipline IS being applied prospectively (#251 §3 Stop-conditions name the superseded boundary).** Check #18 gets the first real test (the #251 slice-2 impl PR). Follow-up line appended. |

**Escalated to trajectory work / operator decision:** the merge-authority-gap
rule-20 recommendation (§1.5) — surface in the next decision batch as an
operator decision (it touches the authority model).

## 6. Recorded for the next pass (check #18)

- **Arc anchor for #18:** the squash commit of *this* PR. `git log --oneline
  --grep='Roadmap trajectory check' main | head -1` then `<that>..HEAD`.
- `python3 -m runtime.smoke` exit 0 at `070dc65`.
- Scoreboard: 16 / 13 / 6 — **tenth** consecutive pass. Tenth-Seat Trigger 2
  armed, **did not fire** (§4 — substantive findings). Re-arms for #18: a
  genuinely clean #18 fires it — flag @soda BEFORE dispatching a Tenth-Seat
  sub-agent, then write `work/reviews/trajectory-18-minority-report.md`.
- **Next 3 (verify at #18):**
  1. **Did #245 merge?** — then re-run `/usr/bin/grep -rn "authorized_operators"
     runtime/` on `main` (the standing check flips from NOTHING to
     module+schema+CLI). Update the standing check text.
  2. **Ask #1 control-plane lane** — did a coordinator stand up `.maps/` +
     `--harness-project-id` and run one `maps recovery-tick
     --enforce-canonical-run` pass? If yes: verify **6.4 / 6.5 / 6.16 / 6.22 +
     H5 / E4 / L6 (7 rows)** HARD against real evidence before any status flip.
     If still unowned/unstarted: say so plainly — it is now the single
     highest-leverage unblocked task.
  3. **Did #249 / #250 / #251 land, and #251's slice-2 impl?** — #250 must keep
     6.9 IN PROGRESS (NO FLIP); #249 surfaces the release-check-3b operator
     decision; #251 impl is friction-entry-6's first real test (no CI-red
     boundary-test trip).
- Merge-authority rule-20 rec (§1.5): check whether it was added to the next
  decision batch and answered.
- Zombie pid 3874: **dead** (Ask #3 done). Its 4 worktree locks are now safe to
  release under Infra #2 (still operator-pending).
- Friction: entries 1–4 closed; entry 5 open (6th no-recurrence arc); entry 6
  open (first real test at #18).

## Resume prompt

You are running roadmap trajectory check #18 for MAPS_Lean. Follow
`playbook/ROADMAP_TRAJECTORY_CHECK.md` (5-step + friction-log consumption) and
`playbook/TENTH_SEAT_REVIEW.md` §7 (read it before recording any clean result).
Worktree off `origin/main`; `git fetch origin main` first.

Arc: anchor = `git log --oneline --grep='Roadmap trajectory check' main | head -1`
(the check-#17 squash commit), then `git log --oneline <anchor>..HEAD`. Do NOT
hand-list (standing rule, PR #212).

Method (rule 14): no claim from a PR title/body/review summary; re-verify against
`git show`, a read of the merged code, `/usr/bin/grep` over `runtime/` excluding
`tests/`, targeted `unittest` modules (session-17 contention protocol — full
suite is CI's). `python3 -m runtime.smoke` must exit 0.

Specifically check: (a) **#245 merged?** → re-run `/usr/bin/grep -rn
"authorized_operators" runtime/` on `main`; it should now find the storage
module + schema + `maps operator` CLI. Update the standing "→ NOTHING" check
text. (b) **Ask #1 control-plane lane** — did a coordinator establish `.maps/` +
`--harness-project-id` and run ONE `maps recovery-tick --enforce-canonical-run`
pass? If yes → verify 6.4/6.5/6.16/6.22 + H5/E4/L6 (7 rows) HARD before any flip.
If still unowned → say so plainly (highest-leverage unblocked task). Confirm no
impl/review agent ran an enforced pass autonomously. (c) Did #249 (release-check
3b scoping), #250 (6.9/S6 NO-FLIP), #251 (SEC4 Half 3 slice 2 scoping + impl)
land? #250 must keep 6.9 IN PROGRESS. #251's slice-2 impl PR is friction-entry-6's
first real test — did it trip a CI-red `NonGoalTests` boundary assertion, or was
the superseded boundary updated in the same PR? (d) Re-derive 16/13/6.
**Trigger 2 re-armed** (#16 found something, #17 found something) — a genuinely
clean #18 fires it: flag @soda BEFORE dispatching a Tenth-Seat sub-agent, then
write `work/reviews/trajectory-18-minority-report.md`. (e) Friction entry 5
(recurrence) + entry 6 (the #251 slice-2 impl test). (f) Was the
merge-authority-gap rule-20 recommendation (check #17 §1.5) added to a decision
batch + answered?

Deliverable: `work/notes/2026-XX-XX-roadmap-trajectory-check-18.md` (+
friction-log follow-up lines, + minority report iff Trigger 2). Update
`CAPABILITY_CHECKLIST.md` ONLY if a status genuinely moved (hard evidence) or a
clause is provably wrong — flag @soda before any status flip.

Workflow: own worktree; PR into `main` (never push); verification-only review;
do NOT spawn your own reviewer — ping @soda; no self-merge; report the PR number
to @soda. Do NOT commit your own review evidence.

STOP + flag @soda if: a status claim is wrong in a way that changes the route to
DONE; the Ask #1 enforced pass ran and a 7-row verification does not hold; the
trajectory action would be STOP or an envelope-leaving REPRIORITIZE; §7 signals
the check has gone shallow; or before dispatching the Tenth-Seat sub-agent.
