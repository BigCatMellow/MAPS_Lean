# Roadmap trajectory check #20 — arc: `8cf99c2..HEAD`

Twentieth pass. Predecessor: `work/notes/2026-09-02-roadmap-trajectory-check-19.md`
(PR #262, arc `03b6a34..HEAD` = 4 PRs #257–#260, action **CONTINUE** with a
sharpened security-cluster finding; scoreboard 16/13/6 — twelfth consecutive.
Substantive finding: the #18 lineage-bootstrap bottleneck was broken in one arc
— #257 scoped, #258 landed `maps run bind-session`, so a production non-adapter
writer of the first `run_session_links` ATTACH row now exists and a real
`resume_denied` is reachable. #19 named the #253 operator batch — item 5
especially — as the remaining lever.)

## Arc derivation — standard anchor

```
$ git log --oneline --grep='Roadmap trajectory check' main | head -1
8cf99c2 Roadmap trajectory check #19 (03b6a34..HEAD — PRs #257 #258 #259 #260) (#262)

$ git log --oneline 8cf99c2..HEAD
828d5e7 6.9 / S6 → DONE: operator §17.3 sign-off (decision batch item 4) (#268)
5a0f7c5 6.21 slice 3b: composite==BLOCKED hard-blocks OPERATOR_VISIBLE_RELEASE_CHECK approval (#249) (#267)
c6dc602 Record OPERATOR ANSWERED — decision batch 2026-09-02 (6 items) (#265)
3dfc922 Adopt merge-authority / merge-prep rule (decision batch item 2) (#266)
b6fc8da 6.9/S6 promotion-gate step RE-RUN (post-#260) — decision: NO FLIP (#264)
1a89015 Checklist evidence: H5 / 6.16 / 6.22 rows cite the lineage-bootstrap exercise (#261) — NO status flip (#263)
```

Arc = **6 PRs: #263, #264, #265, #266, #267, #268** — within the 3–6 window.
HEAD `828d5e7`. `git log --oneline 8cf99c2..HEAD` shows exactly these six; **no
PR beyond #268** on `origin/main`. (The clone carried a stray local `main`
tip `b52acd1` — the head of open PR #269, *not* on `origin/main`; the check was
re-run from a clean branch off `origin/main` `828d5e7`.)

Method (rule 14): every consequential claim re-checked against `git show`, a
read of the merged files, `/usr/bin/grep` over `runtime/`, targeted `unittest`
modules, and `python3 -m runtime.smoke`.

## 0. Situational awareness

- `python3 -m runtime.smoke` → **exit 0 at `828d5e7`**.
- `python3 -m unittest tests.test_exp_b_skill_routing` → **3 OK**, and the raw
  numbers reproduce DEC-002 / the checklist **exactly**: corpus sha256
  `2cff0e40…4565` (frozen), `selection_f1` 0.8667, `exact_cases` 19/25,
  `false_activation_cases` 0, per-category **DIRECT 1.0 / PARAPHRASE 1.0 /
  MULTI_SKILL 1.0 / NO_SKILL 1.0 / HARD_NEGATIVE 1.0 / VOCABULARY_SHIFT 0.0 /
  AMBIGUOUS 0.0**.
- `tests/test_flow_release_check.py` — the four 3b-gate tests
  (`test_unacked_blocked_composite_refuses_review_approval`,
  `test_no_release_check_row_refuses_review_approval`,
  `test_gate_does_not_fire_for_non_release_review_types`,
  `test_rerun_blocked_to_ready_unblocks_review_approval`) → **4 OK**.
- Each arc PR merged with an independent `work/reviews/pr-26N-review-evidence.md`
  (`independent: true`): #263 luve, #264 nava, #265/#266/#267/#268
  independent-review-agent (session 23). `gh pr merge` was operator-only on all
  six (squash-merges under the `BigCatMellow` account) — consistent with the
  #266 rule adopted mid-arc.
- **Scoreboard recounted** from `CAPABILITY_CHECKLIST.md` §7 (row-by-row):
  - **DONE 17** — 6.1, 6.2, 6.3, 6.6, 6.7, 6.8, **6.9**, 6.13, 6.14, 6.15,
    6.18, 6.23, 6.26, 6.27, 6.28, 6.29, 6.30.
  - **IN PROGRESS 12** — 6.4, 6.5, 6.10, 6.11, 6.16, 6.19, 6.20, 6.21, 6.22,
    6.24, 6.33, 6.35.
  - **NOT STARTED 6** — 6.12, 6.17, 6.25, 6.31, 6.32, 6.34.
  - Section 2 phases: **S1–S6 DONE**, **S7 NOT STARTED**.
  - **16/13/6 → 17/12/6.** First scoreboard move in twelve passes. The single
    delta is 6.9 IN PROGRESS→DONE (with S6 IN PROGRESS→DONE in section 2). This
    is the expected, pre-registered flip (#19 "Next 3" item 2b).

## 1. Per-PR verify column (rule 14 — re-confirmed against merged files)

| PR | What | Verified at `828d5e7` | Status impact |
|----|------|-----------------------|---------------|
| **#263** `1a89015` | Checklist evidence — H5 / 6.16 / 6.22 rows cite the #261 lineage-bootstrap exercise. Reviewer luve (APPROVE, independent of #263). | Diff = `CAPABILITY_CHECKLIST.md` only, 3 rows, every status token `IN PROGRESS`→`IN PROGRESS`. `work/notes/2026-09-02-lineage-bootstrap-exercise.md` present and matches: `maps run bind-session` wrote the first `run_session_links` ATTACH row on a fresh `.maps/`, `resolve_run_session → EXPLICIT`, reverse lookup resolves; the exercise **did not** run any `--enforce-*` pass. The prose is correctly hedged ("could", "reachable", "satisfiable"); 6.22 correctly marked **NOT advanced** (recovery-tick is `resume()`-only, `MemoryProvenanceGuard.BEFORE_SEND` unreachable). | none (evidence prose) |
| **#264** `b6fc8da` | 6.9/S6 promotion-gate RE-RUN post-#260 — **decision NO FLIP**. Reviewer nava (APPROVE, independent of author vame). | `work/notes/2026-09-02-6.9-s6-promotion-gate-rerun.md` present. §5: route (a) (further `_select_skills` work) **CLOSED/§6.33-blocked**; route (b) (§17.3 ruling) is the sole route. Checklist diff = prose only, no status cell change; `runtime/` + corpus byte-unmodified (confirmed: no `runtime/` path in `git show b6fc8da --stat`). L4 stale-pointer nit folded in-PR. | none (superseded by #268 three days later) |
| **#265** `c6dc602` | Record OPERATOR ANSWERED — decision batch (6 items). Reviewer independent-review-agent (APPROVE). | `work/notes/OPERATOR_DECISION_BATCH_2026-09-02.md` "OPERATOR ANSWERED" table present. Operator verbatim: *"Items 1–4: proceed with recommended answers. Item 5: target `~/Projects/MAPS_Lean` confirmed, go for the one enforced pass. Item 6: add the 3 scoped Bash rules."* Item 4 answer table entry resolves post-#264 to **YES-promote** (body's own fallback clause triggered by #264; audit note added). | none (decision record) |
| **#266** `3dfc922` | Adopt merge-authority / merge-prep rule (batch item 2). Reviewer independent-review-agent (APPROVE). | `AGENTS.md` gains `### Merge authority (operator-adopted 2026-09-02)` — `gh pr merge` operator-only; no coordinator seat → longest-running peer lane keeps PRs rebased/evidence-bound but does not merge; claim the rebase in-channel. `templates/handoff.md` gains a "Merge authority for this handoff" block. `AGENTS_BYTE_BUDGET` 10000→10400 with `tests/test_documentation_sprawl.py` updated in-PR; adjacent uncertainty-ladder reflowed to prose (byte-neutral intent). Consistent with how the arc's six merges actually operated. | none (process rule) |
| **#267** `5a0f7c5` | 6.21 slice 3b — `composite == BLOCKED` hard-blocks `record_review` APPROVED for `OPERATOR_VISIBLE_RELEASE_CHECK` (batch item 1, YES to both). Reviewer independent-review-agent (APPROVE, 5 own mutations). | `runtime/state/review_binding.py:596–616` — a terminal check in `_validate_review_approval_conn`, reached only for `OPERATOR_VISIBLE_RELEASE_CHECK` after the bound-subject / run / criterion / rederivation gates. On the latest `release_checks` row for `(task_id, review_id)`: no row → `RELEASE_CHECK_REQUIRED`; `composite_state == "BLOCKED"` and blank `operator_ack_ref` → `RELEASE_CHECK_COMPOSITE_BLOCKED`; non-empty ack ref = recorded override. Invoked from `runtime/state/review.py:193` on the APPROVED path (`conn.rollback()` + `MutationResult(False, code, msg)` on issue). No schema DDL, no CLI change. Post-review fix commit corrected the `flow_release_check` `next_step.reason` advisory string; review-evidence re-bound to new head `3f0c109`. | 6.21 evidence clause only — **stays IN PROGRESS** (correct: 3b is one slice; the composite has no verdict recording, `flow_release_check` still records none). |
| **#268** `828d5e7` | 6.9 / S6 → **DONE** — operator §17.3 sign-off (batch item 4). Reviewer independent-review-agent (APPROVE, EXP-B re-run + authorization-chain check). | See §2. `work/decisions/DEC-002-…md` (new) is the sign-off record. Checklist: S6 + 6.9 `IN PROGRESS`→`DONE`; S7 stale "S6 in progress but not done" clause fixed; L4 stale "sole route is a §17.3 ruling" pointer updated (no L4 status change). Master roadmap §6.9 + `02-procedural-knowledge-and-skills.md` S6: reduced to pointers to the checklist + DEC-002 (invariant 6, no restated status). No `runtime/` code, no corpus, no selector change (`git show 828d5e7 --stat` = docs only). | **6.9 + S6 → DONE** (only status flip in the arc) |

## 2. The 6.9 / S6 → DONE flip — is it genuinely true?

**Authorization chain — VALID.** Operator "proceed with recommended answers"
(batch, session 23, 2026-09-02) → the "OPERATOR ANSWERED" table records item 4
as an explicit **YES-promote** under §17.3, with the pre-#264 body recommendation
("(a)") superseded via the body's own fallback clause (triggered by #264's
finding that route (a) is §6.33-blocked). #265 (the answer record) and #264 (the
re-run) are both independently review-evidenced and merged *before* #268.
DEC-002 (`DECIDED`) is the sign-off artifact; §17.3 names "explicit operator
decision" as a valid status-evidence type, and the §6.9-vs-§6.33 scope-boundary
call is an authority decision, not a code question — correctly routed to the
operator, not a reviewer (rule 11 / rule 17).

**S6 exit gate — "unrelated Skills demonstrably stay out of context" — MET.**
Re-verified here: EXP-B `false_activation_cases` **0**, HARD_NEGATIVE **1.00**,
NO_SKILL **1.00** at the frozen corpus; `tests/test_context_builder.py` (L117
`assertNotIn("unrelated.txt", serialized)`, L519+ `_catalog_with_matching_and_
unrelated_skill`, L610 "the unrelated Skill contributes nothing — S6 exit gate")
asserts the exclusion directly. `02-procedural-knowledge-and-skills.md` marks
the gate MET 2026-09-03 with the same evidence pointer.

**§17.3 sign-off soundness.** Route (a) genuinely dead: #260's scoring
simulation + #264's independent re-run both show VOCABULARY_SHIFT V01's
post-lemmatisation match is lexically identical to hard negatives H02/H03 (any
floor admitting V01 re-admits them → HARD_NEGATIVE regresses), and an AMBIGUOUS
margin loose enough to flag A01/A02 also flags the genuine MULTI_SKILL tie M01
→ MULTI_SKILL regresses. Both need query expansion / semantic similarity =
roadmap §6.33, which keeps its own `IN PROGRESS (evaluation-only, by design)`
status and its own promotion gate. DEC-002 does not touch §6.33. The selector
is explicitly **not** asserted correct on all routing — it is characterized as
blind on synonym-shift and fine-grained ambiguity, both deferred, with
containment (6.22 trust-gate + SEC4 quarantine sit downstream of selection).

**Residual "IN PROGRESS because X" left dangling?** Checked. The #268 review
caught the one instance — the 6.9 cell's pre-existing "Still IN PROGRESS —
content is pull-not-push, an optional body byte-budget ceiling (§4) is unmet" —
and the impl agent rewrote it to a resolved note (pull-not-push is
roadmap-conformant; the §4 ceiling is an optional future refinement, not a
promotion criterion). No other "still IN PROGRESS" / "not yet" phrasing survives
in the now-DONE 6.9 or S6 cells (grep-checked). S7 correctly re-gated to
"Harness/EnvironmentSpec stability" only. **The flip is sound.**

## 3. #267 release-check 3b gate — correct?

`_validate_review_approval_conn` **does** gate an un-acked BLOCKED composite for
`OPERATOR_VISIBLE_RELEASE_CHECK` — verified against the merged code (§1) and the
four gate tests (§0). The gate is correctly the *last* check (after bound-subject
/ run / criterion / rederivation), scoped by `task["review_required"]`, and the
override path (`operator_ack_ref`) is a recorded value, not a `--force`. **6.21
correctly stays IN PROGRESS** — the #267 diff adds one evidence clause and no
status flip; the independent review confirmed row 6.21 still reads `IN PROGRESS`.

## 4. #266 merge-authority rule — consistent with how the seat operated this arc?

Yes. All six arc merges were operator-account squash-merges (`gh pr merge`
operator-only — the rule's clause (b)). The #19 note already recorded mika
(session-20) draining the prior queue as merge-prep-only from the coordinator
checkout with cross-assigned evidence commits in each committer's own worktree —
the exact shape (a)/(c) prescribe, applied by convention before adoption. No
coordination-hygiene incident this arc (friction §5). The rule codifies existing
practice; nothing in the arc contradicts it.

## 5. #265 operator decision batch — item-by-item disposition

| # | Answer | This arc |
|---|--------|----------|
| 1 | YES to both | **Actioned** → #267 (3b gate merged). |
| 2 | Adopt (a)(b)(c) | **Actioned** → #266 (AGENTS.md + handoff template). |
| 3 | Keep fail-open + opt-in flag later | **No action by design** — the opt-in `--enforce-operator-identity` flag is a later slice; nothing to do now. |
| 4 | YES — promote 6.9/S6 | **Actioned** → #268 (DONE flip + DEC-002). |
| 5 | GO for the one enforced pass, target `~/Projects/MAPS_Lean` | **BLOCKED** — see §6. |
| 6 | Add 3 scoped Bash permission rules | **Applied** (local `.claude/settings` — not a repo artifact; confirmed via the batch "OPERATOR ANSWERED" record and #19's friction-log context, not re-verifiable from this clone). |

## 6. Named new evidence — item 5's enforced pass is BLOCKED

The one hard blocker on the security/harness cluster. When the enforced pass was
attempted (2026-09-03, per open **PR #269** `fix/hcom-stopped-json-defect` and
its `FRICTION_LOG` entry / `work/notes/2026-09-03-hcom-list-stopped-nonjson-repair.md`),
it aborted with `HcomProtocolError: hcom list --json returned invalid JSON`
(exit 2), nothing written:

- `HcomAdapter.list_sessions(include_stopped=True)` runs
  `hcom list --json --stopped --all`; hcom **0.7.25** ignores `--json` for
  `--stopped` and emits human text. `json.loads` explodes.
- `RecoverySupervisor.observe_silent_stops` / `tick` /
  `HcomSessionAdapter._session_records` call it unconditionally, so **all** of
  `maps recovery-tick` (not just `--enforce-canonical-run`) is dead against
  hcom 0.7.25. `hcom list --help` shows `--json` is intentionally absent from
  `--stopped`, so no hcom version fixes it.
- PR #269: Part A (folded) — `list_sessions` falls back to alive-only
  `hcom list --json` when `--stopped` output isn't JSON (detection preserved;
  `session_id`→`run_id` lineage degrades to unresolved, documented) + a frozen
  regression test. Part B (design-only, follow-up impl + review) — option C:
  rebuild stopped-session records from `hcom events --json`.

**Effect on the route to DONE.** The 7 rows item 5 was to advance — 6.4 / 6.5 /
6.16 / 6.22 + H5 / E4 / L6 — now have an inserted dependency the roadmap did
not show: **PR #269 must land, then the enforced pass must run.** It does not
change the destination and it is not a new operator decision. Two of those rows
(H5, 6.16) had checklist prose that still read the blocker as "operator-gated,
decision batch item 5 unanswered"; **corrected in this PR** to name the hcom
0.7.25 defect + PR #269 as the current blocker (evidence clause only, no status
flip — H5 / 6.16 stay IN PROGRESS). 6.22's blocker is orthogonal (a production
`send()` caller) and unaffected. 6.4 / 6.5 / E4 / L6 cite their own further
unmet conditions (capability-declaration manifest; the validation gate; a
manifest-writer wiring change) beyond the pass, so no per-row edit there.

**Upside also recorded (verify at #21).** The `.maps/` control plane at
`~/Projects/MAPS_Lean` now carries real routable state (`LBW-EXERCISE-1`,
lease-expired, EXPLICIT lineage from #261's exercise) — so once PR #269 lands
the enforced pass **can** produce a real `LEASE_EXPIRED` `resume_denied`, not
the near-no-op the #255 runbook feared. The lineage-bootstrap half is done; the
blocker is now purely the hcom adapter defect.

## 7. Trajectory action: **CONTINUE**

Not REPRIORITIZE: the item-5 dependency chain lengthened by exactly one PR
(#269), and that PR is *already* the correctly-prioritised top of the runway —
dispatched 2026-09-03, Part A folded in, in review. Nothing about the roadmap's
item ordering is wrong; the next work is already the right work. Not STOP: the
#19 STOP-condition ("#253 still unanswered AND nava's exercise stalled AND no
new ask-independent slice") is **not met** — the batch is answered (5 of 6 items
actioned this arc), the exercise landed (#261), and PR #269 + its Part B impl
are live ask-independent work.

Reasoning:

1. **The arc shipped cleanly.** 5 of 6 batch items actioned in one arc, each
   with independent review; the 6.9/S6 DONE flip — the first scoreboard move in
   twelve passes — rests on a valid §17.3 operator sign-off and an S6 exit gate
   that is genuinely MET (EXP-B numbers reproduced here).

2. **The single blocker is well-contained.** Item 5's enforced pass is blocked
   by one adapter defect with a fix in flight (PR #269 Part A folded, Part B
   scoped). The lineage-bootstrap deadlock #18/#19 tracked is *done*; the
   control plane has real routable state; the remaining gap is a 2-part PR, not
   an unowned code change or an operator decision.

3. **The runway is healthy:** PR #269 Part A review + Part B (option C) impl +
   review; then the enforced pass (operator GO already given) + the 7-row HARD
   verification; 6.21 further slices; 6.4/6.5/E4 each have a named next step
   independent of the pass.

**No CUT SCOPE / ADD.** The roadmap points at DONE; the route now runs
PR #269 → enforced pass → per-row verification. The correction applied this PR
(H5 / 6.16 blocker prose) is the status-truth fix the pass surfaced.

## 8. Tenth-Seat / §7 duty (`TENTH_SEAT_REVIEW.md` §2 Trigger 2, §7)

Trigger 2 is **armed** (passes #17, #18, #19 each found a substantive finding).

**It does not fire this pass.** §6 is a substantive finding: item 5's enforced
pass — named by #19 as "the remaining lever" — is blocked by a newly-surfaced
hcom 0.7.25 adapter defect, and the roadmap's H5 / 6.16 prose was stale on the
blocker (corrected here). This pass is **not trending clean**, so no @mika
pre-flag for a Tenth-Seat sub-dispatch is required, and none is initiated.

§7 "signs this has gone wrong", checked:

- *"same conclusion every pass regardless of evidence"* — the scoreboard
  **moved** this pass (16/13/6 → 17/12/6) for the first time in twelve, and the
  picture keeps moving: #18 "unscoped code change" → #19 "code merged, exercise
  in flight" → **#20 "exercise landed, batch answered, one adapter defect (PR
  #269) between here and the enforced pass."** Evidence-driven.
- *"verdict drifting toward reassurance"* — this pass records a *new* blocker
  (§6) and a stale-prose correction, and downgrades the H5 / 6.16 blocker
  framing from "just waiting on the operator" to "waiting on a code fix". Not
  glossing.
- *"no one has run the full check"* — arc range-derived (6 PRs, clean-branch
  re-derivation after catching the stray local `main` tip); all six read at the
  file level; EXP-B + the 3b gate tests re-run here; scoreboard walked
  row-by-row; the hcom defect traced to `HcomAdapter.list_sessions` + PR #269.
- *"challenges detail, never a foundational claim"* — §6 is foundational (the
  route to DONE for a 7-row cluster), not a row-label quibble.

No Tenth-Seat sub-agent dispatched — Trigger 2 negative in this pass's judgment,
substantive finding present.

## 9. Friction-log consumption

Log walked in full (8 entries). Entries 1–4 already closed (`verified:`
END-TO-END / VERIFIED) — no re-open. Open items:

| # | Entry | `verified:` | Disposition this pass |
|---|-------|-------------|-----------------------|
| 5 | orchestrator tool-use burned context | n/a (behavioral), `countermeasure: none yet` | **Consumed — 9th consecutive no-recurrence arc.** The #263–#268 lanes + this trajectory lane used scoped `git show` / `git show --stat` / `/usr/bin/grep` / `awk`/`sed -n` line ranges / `Read` offset+limit; no 100KB+ dumps, no whole-doc re-reads (the one large `sed -n` on `CAPABILITY_CHECKLIST.md` was redirected to a saved file by the harness, not re-read into context). Follow-up line appended. Stays open (behavioral). |
| 6 | stale slice-boundary `NonGoalTests` asserts | END-TO-END (×4) | **Consumed — no clean test case this arc.** None of #263–#268 was a scope-expanding `_select_skills` / `context_builder` slice; #267 (`review_binding.py`) added no `NonGoalTests` substring risk and updated its own `flow_release_check` advisory string + test in-PR. No CI-red boundary trip. Follow-up line appended. Stays open. |
| 7 | agent edited the shared coordinator checkout | confirmed 2026-09-02; countermeasure not yet adopted | **CLOSED — countermeasure now adopted.** #266 landed the merge-authority rule into `AGENTS.md` (`gh pr merge` operator-only; coordinator checkout is merge-prep-only) — the operator-adoption this entry was folded into (#253 item 2 → batch item 2 → answered → #266). (b) No coordination-hygiene incident this arc. The mechanical backstop (dirty-tree merge-prep refusal) stays a "if a 5th lands" item, not needed now. Follow-up line appended marking the entry closed. |
| 8 | hcom 0.7.25 `list --stopped` ignores `--json` | reproduced 2026-09-03, Part A test green; Part B open | **Escalated as in-scope trajectory work (§6).** The entry itself is on the PR #269 branch, not `origin/main` — it is the record for the open fix PR. Verified the defect is real (the entry documents a fresh-clone repro against installed `hcom 0.7.25`). This is the item-5 blocker; the route-to-DONE consequence + the H5 / 6.16 prose correction are in §6 / this PR. Follow-up: check #21 confirms PR #269 (Parts A + B) landed and the enforced pass ran. |

**New friction this arc (captured — two entries appended to `FRICTION_LOG.md`):**

- **`fix commit lands on top of review-evidence, evidence re-bound to new head`
  — 2 occurrences (#267 `3f0c109`, #268 `261636a`).** Both contained (the
  review-evidence file was updated to the new head and the delta re-reviewed
  in-PR), no escaped defect. Recorded so a 3rd occurrence triggers a
  dispatch-discipline fix (a review dispatch for a doc/prose PR should expect
  and bundle the "reviewer's own nits applied by the impl agent" round-trip
  before evidence is bound).
- **dispatched worker stalls on its own full `unittest` suite.** Several test
  modules (`test_flow_release_check`, `test_context_builder`,
  `test_exp_b_skill_routing` batteries) run ~7–8 s per test — a full module is
  3+ min, the whole suite well over a short foreground cap. Recorded per rule 20
  (this pattern has produced repeated "run tests" stalls); the standing
  countermeasure is the AGI-standard dispatch clause "full suite is CI's; run
  named modules as blocking foreground" — this pass ran named modules foreground
  and delegated the full suite (below).

## 10. Full suite

`python3 -m unittest discover -s tests` was started foreground from the branch
off `origin/main` `828d5e7` + the doc edits, but is heavily I/O-bound in this
environment (~9 min wall for ~13 s CPU, still running well past a reasonable
foreground cap — the "dispatched worker stalls on its own full suite" friction
this pass captured, in action). **Full suite delegated to CI**
(`runtime-stack-tests.yml`, `python -m unittest discover -s tests -v`, 15-min
budget) on the PR. Foreground evidence run here and green: `runtime.smoke`
exit 0; `tests.test_exp_b_skill_routing` 3 OK (f1 0.867, numbers reproduce
DEC-002); the four `tests.test_flow_release_check` 3b-gate tests 4 OK;
`tests.test_documentation_sprawl` 22 OK. The arc changes under test are
docs/prose only (this PR touches no `runtime/` or `tests/` code); the six arc
PRs each merged green.

## 11. Recorded for the next pass (check #21)

- **Arc anchor for #21:** the squash commit of *this* PR (#20). Standard rule.
- `python3 -m runtime.smoke` exit 0 at `828d5e7`; EXP-B 3 OK, f1 0.867.
- Scoreboard **17 / 12 / 6** — first move in twelve passes (6.9/S6 → DONE).
  Tenth-Seat Trigger 2 armed, **did not fire** (§8). Re-arms for #21: a
  genuinely clean #21 fires it — flag @mika BEFORE dispatching a Tenth-Seat
  sub-agent, then write `work/reviews/trajectory-21-minority-report.md`.
- **Next 3 (verify at #21):**
  1. **Did PR #269 land** (Part A tolerate + Part B option C impl + independent
     review)? If yes → is `maps recovery-tick` reachable against the installed
     hcom again?
  2. **Did the enforced `--enforce-canonical-run` pass run** (operator GO given
     in batch item 5, target `~/Projects/MAPS_Lean`, real routable state
     `LBW-EXERCISE-1` present)? If yes → the **7-row** verification (6.4 / 6.5 /
     6.16 / 6.22 / H5 / E4 / L6), HARD, per `work/notes/2026-09-02-ask1-control-plane-runbook.md`
     §6 per-row unmet conditions, before any flip. Confirm no impl/review agent
     ran an `--enforce-*` pass autonomously.
  3. **6.21** — any slice past 3b (composite verdict recording)? Still IN
     PROGRESS is correct until then.
- STOP-condition watch for #21: if PR #269 stalled AND the enforced pass has not
  run AND no new ask-independent security-cluster slice is identified — that is
  a genuine STOP-condition on the security cluster; #21 says so plainly.
- Friction: entries 1–4 closed; **7 now closed** (#266 adopted the
  countermeasure); 5 open (9th no-recurrence arc); 6 open (no test case this
  arc); 8 = the PR #269 record (verify landed at #21); 2 new entries appended
  (review-evidence re-bind ×2; full-suite stall).

## Resume prompt

You are running roadmap trajectory check #21 for MAPS_Lean. Follow
`playbook/ROADMAP_TRAJECTORY_CHECK.md` (5-step + friction-log consumption) and
`playbook/TENTH_SEAT_REVIEW.md` §7 (read it before recording any clean result).
Fresh clone off `origin/main`; `git fetch origin main` first and work from a
clean branch off `origin/main` (check #20 was tripped by a stray local `main`
tip — verify `git rev-parse origin/main` matches your base).

Anchor: `git log --oneline --grep='Roadmap trajectory check' main | head -1` →
the check-#20 squash; then `git log --oneline <that>..HEAD`, check every line.

Method (rule 14): no claim from a PR title/body/review summary; re-verify against
`git show`, merged code, `/usr/bin/grep` over `runtime/`, targeted `unittest`
modules (named modules foreground — the full suite is CI's; ~7–8 s/test).
`python3 -m runtime.smoke` must exit 0. `python3 -m unittest
tests.test_exp_b_skill_routing` must stay 3 OK at f1 0.867 (6.9/S6 are now DONE
— a regression there is a status-truth emergency).

Specifically check: (a) **Did PR #269** (`fix/hcom-stopped-json-defect` — the
hcom 0.7.25 `list --stopped --json` defect blocking `maps recovery-tick`) land,
Parts A **and** B, with independent review? (b) **Did the enforced
`--enforce-canonical-run` pass run** (operator GO already given, batch item 5;
target `~/Projects/MAPS_Lean`; real routable state `LBW-EXERCISE-1` present)? If
yes → verify 6.4 / 6.5 / 6.16 / 6.22 / H5 / E4 / L6 (7 rows) HARD against
`work/notes/2026-09-02-ask1-control-plane-runbook.md` §6 before any flip; confirm
no impl/review agent ran an `--enforce-*` pass autonomously. (c) Re-derive the
scoreboard — it should be 17/12/6 unless the enforced pass advanced a row.
(d) **Trigger 2 re-armed** (#17–#20 all found something) — a genuinely clean #21
fires it: flag @mika BEFORE dispatching a Tenth-Seat sub-agent. (e) Friction
entries 5, 6, and the 2 new ones (review-evidence re-bind; full-suite stall);
entry 8 (PR #269) — confirm landed.

Deliverable: `work/notes/2026-XX-XX-roadmap-trajectory-check-21.md` (+ friction
follow-up lines, + minority report iff Trigger 2). Update `CAPABILITY_CHECKLIST.md`
ONLY if a status genuinely moved (hard evidence) or a clause is provably wrong —
flag @mika before any status flip.

Workflow: own branch; PR into `main` (never push to main, never merge);
verification-only; do NOT write your own review-evidence; do NOT spawn your own
reviewer — ping @mika; report the PR number to @mika. Do NOT touch
`~/Projects/MAPS_Lean` or `.maps/`, do NOT run `maps recovery-tick`.

STOP + flag @mika if: PR #269 stalled AND the enforced pass has not run AND no
new ask-independent security-cluster slice is identified (STOP-condition —
record it plainly); a status claim is wrong in a way that changes the route to
DONE; the trajectory action would be STOP or an envelope-leaving REPRIORITIZE;
§7 signals the check has gone shallow; or before dispatching the Tenth-Seat
sub-agent.
