# Roadmap trajectory check #18 — arc: `6ea81b2..HEAD`

Eighteenth pass. Predecessor: `work/notes/2026-09-02-roadmap-trajectory-check-17.md`
(PR #252, arc `6ea81b2..HEAD` at that time = #242/#241/#243/#244/#246 + folded
#245/#251, action **CONTINUE**, scoreboard 16/13/6 — tenth consecutive;
substantive finding: the #16 operator batch was answered (#243), the
security-cluster blocker changed shape to "one coordinator prerequisite task").

## Arc derivation (commit range — deliberate over-anchor, per PR #252 §6)

```
$ git log --oneline --grep='Roadmap trajectory check' main | head -1
1b9fe1d Roadmap trajectory check #17 (6ea81b2..HEAD — PRs #242, #241, #243, #244, #246) (#252)
```

**Anchor = `6ea81b2` (the check-#16 squash), NOT `1b9fe1d` (#252's squash).**
Per PR #252 §6's "READ THIS FIRST" table: #245/#251 merged *after* the #252
branch was cut and #252 folded them in as an over-anchor; #252 §6 also
instructed #18 to anchor at `6ea81b2` and cover every PR since.

```
$ git log --oneline 6ea81b2..origin/main
d8568a3 Runbook: Ask #1 control-plane setup + first --enforce-canonical-run pass (#255)
6548cbb Operator decision batch doc — 2026-09-02 (6 items) (#253)
709471e Design note: 6.9/S6 _select_skills selector-quality scoping (path to DONE) (#254)
1b9fe1d Roadmap trajectory check #17 (…) (#252)
e1e4467 6.9/S6 promotion gate step — decision: NO FLIP (#250)
6cfa416 Design note: 6.21 release-check 3b — composite==BLOCKED approval gate (scoping) (#249)
5447700 SEC4 Half 3 slice 1: authorized-operator registry (#245)
6b8e703 Design note: SEC4 Half 3 slice 2 scoping — widen operator gate to all skill verbs (#251)
070dc65 6.9/S6: EXP-B expanded frozen Skill-selection evaluation (25-case corpus) (#246)
7a466eb 6.21: maps flow release-check — compose artifact-identity + release-smoke evidence (#244)
ffbf71c Operator answered the trajectory-#16 decision batch (session 17) (#243)
891045e Design note: 6.9/S6 frozen Skill-selection evaluation — scoping (#241)
5d4a9f2 SEC4 capability granularity: network-read split + filesystem-write:<path> token (#242)
```

Arc = **13 PRs** (#241 #242 #243 #244 #245 #246 #249 #250 #251 #252 #253 #254
#255) — **far over the 3–6 window; acknowledged.** The window slipped because
the coordinator seat lapsed mid-session-17 (a 5h+ queue stall, memory
`project_merge_authority_stall_session19`) and a large catch-up batch then
landed at once. The anchor accounting — every PR since `6ea81b2` reviewed
exactly once, no gap — is what matters, not the count.

**Verification split:** #252 §6 carries a per-PR verify column for
#241/#242/#243/#244/#246 (and folded #245/#251). Those are trusted with a
spot-check. #18 fully verifies the rest: **#245, #249, #250, #251, #252 (the
check-#17 note), #253, #254, #255** — the last four are new since #252.

Method (rule 14): every consequential claim re-checked against `git show`, a
read of the merged code, `/usr/bin/grep` over `runtime/` excluding `tests/`, and
`python3 -m runtime.smoke`.

## 0. Situational awareness

- `python3 -m runtime.smoke` → **exit 0 at `d8568a3`**.
- **Scoreboard recounted** from `CAPABILITY_CHECKLIST.md` §7 (6.1–6.35, Status
  column, `awk -F'|' '{print $2,$4}'`):
  - **DONE 16** — 6.1, 6.2, 6.3, 6.6, 6.7, 6.8, 6.13, 6.14, 6.15, 6.18, 6.23,
    6.26, 6.27, 6.28, 6.29, 6.30.
  - **IN PROGRESS 13** — 6.4, 6.5, 6.9, 6.10, 6.11, 6.16, 6.19, 6.20, 6.21,
    6.22, 6.24, 6.33, 6.35.
  - **NOT STARTED 6** — 6.12, 6.17, 6.25, 6.31, 6.32, 6.34.
  - **Identical to passes #8–#17. Eleventh consecutive pass at 16/13/6.**
  - Arc cross-check: `git diff 6ea81b2..HEAD -- CAPABILITY_CHECKLIST.md` touches
    **6.9, 6.10, 6.21** (main table) + **S6, L4** (sub-roadmap) — evidence text
    only; every `-`/`+` status token on all five reads `IN PROGRESS`. **No PR in
    the 13 flips a status.**
- Spot-checks of #252-trusted PRs held: `_SATISFYING_TOKENS` (#242) =
  `{"network-general": {"network-general"}}` only — no `network-read` alias;
  `release_checks` table (#244) present (7 schema refs); `authorized_operators`
  (#245) → `runtime/cli.py`, `runtime/state/authorized_operator_storage.py`,
  `runtime/state/schema.sql`.

## 1. Carried checks (from the @soda dispatch #81900)

### Carried check 1 — everything #253's operator batch unblocks, + the #255 finding. **MATERIAL CHANGE: the security cluster is now blocked on a CODE change, not an operator go.**

**#253 status:** the 6-item batch is **merged as a doc** (`6548cbb`,
`work/notes/OPERATOR_DECISION_BATCH_2026-09-02.md`) but **not yet answered by
the operator** — `soda` is surfacing it. Items: (1) release-check 3b approval
gate, (2) merge-authority rule-20 adoption, (3) SEC4 Half 3 2c empty-registry
semantics, (4) 6.9/S6 DONE path, (5) Ask #1 target/timing, (6) infra permission
carry-overs.

**#255 (`d8568a3`) re-frames item 5.** The Ask #1 control-plane runbook (nava
APPROVE after one REQUEST_CHANGES round; the load-bearing finding traced
end-to-end) establishes:

- A freshly-created `.maps/` + the current (empty) incident set makes the first
  `--enforce-canonical-run` pass a **near no-op**: it *instantiates* the
  production guard composition (`build_canonical_harness_service` — the "first
  production exposure of the composition root" the checklist rows want) but
  **`CanonicalRunGuard.__call__` is never invoked**, because
  `RecoverySupervisor._resolve_harness_binding` pre-checks
  `store.resolve_run_session(run_id)["state"] == "EXPLICIT"` before routing a
  resume through the guarded `HarnessService`, and **no production code path
  writes that first `run_session_links` row.** `flow_start` explicitly stops
  before a provider session; no `maps` CLI verb records a session link; the
  adapter that *would* bootstrap it (`HcomHarnessAdapter.record_run_session_link`)
  is only ever reached *after* the supervisor's `EXPLICIT` pre-check passes.
  Deadlock. **Zero `resume_denied` on the first pass.**
- Ask #1 was authorised (#243) for a *pictured outcome* — currently-working
  resumes becoming `resume_denied`, exposing the enforcement layer for real.
  That outcome is **not reachable without a code change** (#255 §8): a
  lineage-bootstrap wiring change so a production path records the first
  `run_session_links` row.
- #255 §6: **none of the 7 rows (6.4 / 6.5 / 6.16 / 6.22 / H5 / E4 / L6) reach
  DONE from the pass alone** even absent the deadlock — 6.4 needs
  write/credential guards; 6.5 + E4 need the validation-*outcome* gate (a
  different enforcement layer, `--enforce-validation`); L6 needs manifest-writer
  wiring (`create_run_manifest` callers have no `HarnessService` in scope);
  6.16 + H5 + 6.22 share the "guard instantiated in the composition but its
  callback never fires for lack of a reachable operation" shape — exactly what
  the lineage-bootstrap change would unblock.

**So the #16/#17 model — "operator answers Ask #1 → run the pass → verify 7 rows"
— is now known to be wrong.** The real route for the 3 lineage-gated rows
(6.16 / H5 / 6.22): operator answers item 5 → run the documented 0-denial
instantiation pass (option A, within the granted scope) → **scope + implement
the lineage-bootstrap wiring (option B)** → engineer a routable denial → then
each row still needs its own remaining work. 6.4 / 6.5 / E4 / L6 have
independent unmet conditions on top.

This is the substantive finding this pass records (see §2, §3).

### Carried check 2 — scoreboard re-derived. **CONFIRMED 16/13/6 (11th consecutive).** §0.

Every arc PR's no-status-flip claim verified: only 6.9 / 6.10 / 6.21 / S6 / L4
*evidence text* changed across the 13 PRs; all stayed `IN PROGRESS`. #250 is the
explicit NO-FLIP decision on 6.9/S6 (verified — 6.9 and S6 both still
`IN PROGRESS`, the note itself says "No status cell changes value"). #245 / #255
/ #254 / #253 / #252 touch no status cell (#245 edits 6.10 evidence text only;
#255 / #254 / #253 add notes + one review-evidence file each; #252 adds the
check-17 note + friction lines).

### Carried check 3 — `authorized_operators` / SEC4 Half 3. **CONFIRMED as described.**

- The standing "`/usr/bin/grep -rn authorized_operators runtime/` → NOTHING"
  check is **RETIRED** (per #252 carried check 4). It now returns
  `runtime/cli.py`, `runtime/state/authorized_operator_storage.py`,
  `runtime/state/schema.sql`.
- **Slice 1 (#245)** — `authorized_operators` + `authorized_operator_revocations`
  tables (append-only triggers), `AuthorizedOperatorStorageMixin`,
  `maps operator add|revoke|list`, genesis via `maps init --operator` (`GENESIS`
  sentinel), opt-in-by-data `is_authorized_operator` gate on `maps skill
  approve` (`cli.py:570`). Re-verified: `test_authorized_operator_storage`
  18/18 OK (check #17).
- **Slice 2 scoping (#251)** — recommends increment 2a (widen the gate to
  `activate`/`retire`/`supersede`); defers 2b/2d/2e; flags 2c (empty-registry
  fail-closed cutover) as an operator decision — now #253 item 3.
- **Slice 2a impl** — dispatched to `luve` (per the @soda dispatch); **no PR
  open or merged yet** at `d8568a3`. It is friction-entry-6's first real test (a
  scope-expanding change that will legitimately supersede a boundary assertion —
  the #251 §3 Stop-conditions already name it).

### Carried check 4 — merge-authority. **Rule-20 rec is now #253 item 2 (pending an answer). One new incident this window.**

- The rule-20 recommendation from #252 §1.5 (named fallback merge-prep order
  when the coordinator seat lapses; `gh pr merge` stays operator-only; claim the
  rebase in-channel before force-pushing a shared branch) is now **#253 item 2**,
  awaiting the operator batch answer.
- **New incident this window:** the concurrent #245-rebase race — `luve` (as
  reviewer) asked `vame` (author) to rebase #245 while the returning coordinator
  `soda` had *also* rebased and force-pushed the same branch; `vame`'s push
  landed second and overwrote `soda`'s (`cb775bb…d86c6f2 forced update`).
  Harmless only because both resolved the same additive conflicts identically.
  Recorded in memory `feedback_concurrent_rebase_race_pr245`. This is the third
  coordination-gap incident in the session-17→19 arc and it is exactly what
  #253 item 2(c) ("claim the rebase in-channel first") addresses.
- **Also reported by @soda (not independently verified here):** a stray
  `CAPABILITY_CHECKLIST.md` edit appeared in the coordinator checkout this
  session. If real, that is a fourth coordination-hygiene signal and should get
  its own `FRICTION_LOG.md` entry — flagged to @soda to confirm + capture.

### Carried check 5 — friction entries 5 / 6 + `feedback_stale_slice_boundary_nongoal_test`.

**Entry 5** ("orchestrator tool-use burned ~30–40k context on avoidable dumps",
`countermeasure: none mechanical`): the #241–#255 arc (mostly design notes,
scoping notes, a runbook, two impl PRs, two review lanes) shows no large-dump
behaviour — scoped `git show` / `/usr/bin/grep` / `sed -n` ranges / `Read`
offset+limit throughout, in both the impl lanes and this trajectory lane.
**7th consecutive no-recurrence arc; stays open.** Follow-up line appended.

**Entry 6** (`feedback_stale_slice_boundary_nongoal_test`, 2 occurrences): the
#251 slice-2a impl (the first real test — does a scope-expanding `_select_skills`
/ CLI change trip a CI-red `NonGoalTests` boundary assert, or update it in-PR?)
**has not landed yet** — carries to #19. Meanwhile the **#254 selector-quality
scoping note's resume prompt** (path a: HARD_NEGATIVE score + AMBIGUOUS margin +
V01 lemmatiser) is a second scope-expanding `_select_skills` slice, and its
dispatch *does* name the boundary it supersedes ("the per-category structural
asserts … change intentionally"; "`test_exp_a` v1 pins may shift — update
alongside, note it"). The dispatch discipline is being applied. Both impl PRs
are #19's test. Follow-up line appended.

## 2. What changed (materially)

1. **The Ask #1 → 7-row path is longer than #16/#17 modelled (#255).** Not
   "operator go → run pass → verify"; a lineage-bootstrap **code change** sits
   between "run the pass" and "any of 6.16 / H5 / 6.22 becomes verifiable". The
   runbook removes the guesswork (the exact command sequence, the reversibility
   answer, the deny-code order) and traces the deadlock end-to-end. The pass
   *itself* is still worth running (option A — instantiation evidence, within
   the granted scope) but it is not the milestone the rows' evidence text
   implies.

2. **The operator batch (#253) is drafted and merged but unanswered.** Six
   decisions are queued; four (items 1–4) are accept-as-block; two (5 Ask #1
   A/B + timing, 6 infra permissions) need per-item responses. Until it is
   answered, release-check 3b impl and the Ask #1 pass are both parked.

3. **The 6.9/S6 path is fully scoped (#254, APPROVE'd).** HARD_NEGATIVE +
   AMBIGUOUS are explicit-first and dispatchable now; VOCABULARY_SHIFT V02–V04
   are correctly parked as roadmap §6.33 (semantic retrieval / query expansion,
   EVIDENCE-GATED); only the V01 morphological miss + a §17.3 ruling on the
   residual gap stand between the impl and a DONE decision.

4. **No scoreboard movement for an 11th pass** — but this is no longer the
   "waiting on an operator" freeze #16 described. Three of the four
   design-note-heavy passes (#15–#18) have been *scoping the security cluster's
   real route*, and #255 is the deepest cut yet: the route is now concrete
   (lineage-bootstrap wiring) rather than "first exposure, somehow".

## 3. Trajectory action: **CONTINUE** (with a sharpened security-cluster finding)

Not STOP: the route to DONE still exists and #255 makes its next step concrete
(the lineage-bootstrap wiring). Not REPRIORITIZE: the work order is already
right — dispatch what is ready, surface the operator batch. Not CUT SCOPE: none
of the 7 rows is discretionary. Reasoning:

1. **The dispatchable runway is healthy — 3–4 ready lanes:**
   - **SEC4 Half 3 slice 2a impl** — dispatched to `luve`, in flight (widen the
     operator gate to `activate`/`retire`/`supersede`; #251-scoped, no schema,
     no operator decision).
   - **6.9/S6 selector-quality impl** — #254 path a, APPROVE'd, ready to
     dispatch now (HARD_NEGATIVE distinctiveness score + AMBIGUOUS margin + V01
     lemmatiser; EXP-B is the acceptance test).
   - **Lineage-bootstrap wiring scoping note** — #255 §8 option B. **NEW, not
     yet dispatched, and it is the true bottleneck for 6.16 / H5 / 6.22.**
     **Recommend @soda dispatch this as the top-priority new design lane** — it
     does not need an operator decision to *scope* (only to implement), and
     three roadmap rows are waiting behind it.
   - **SEC4 Half 3 slice 2b** — #238 §4 `filesystem-write:<path>` →
     `output_paths` enforcement; needs a small design note then impl.

2. **Blocked on the operator batch (#253):** release-check 3b impl (item 1); the
   Ask #1 pass + its A/B decision (item 5 + #255 §8); the infra permission rules
   (item 6). These are genuinely waiting — do not dispatch around them.

3. **The security cluster is not yet a STOP-condition — but it is trending
   toward one.** Seven rows have been `IN PROGRESS` behind "first enforced
   exposure" for six-plus sessions; #255 now shows that exposure needs a code
   change nobody has scoped. **If check #19 finds (a) the #253 batch still
   unanswered AND (b) no lineage-bootstrap scoping note dispatched, that is a
   genuine STOP-condition on 6.16 / H5 / 6.22** — #19 should say so plainly and
   not CONTINUE a fourth time on the security cluster. This pass pre-registers
   that condition (mirroring #15→#16).

### Recommended dispatch (for @soda)

- **Lane 1 (NEW, top priority) — lineage-bootstrap wiring scoping note** (#255
  §8 B). Design only; the real path to 6.16 / H5 / 6.22.
- **Lane 2 — 6.9/S6 selector-quality impl** (#254 path a, ready).
- **Lane 3 — SEC4 Half 3 slice 2a impl** (luve, already in flight) → then 2b
  design.
- **Surface #253 to the operator** — items 1–4 as a block; items 5 (with the
  #255 A/B framing) and 6 per-item.

## 4. Tenth-Seat / §7 duty (`TENTH_SEAT_REVIEW.md` §2 Trigger 2, §7)

Trigger 2 is **armed** (passes #16 and #17 each found a substantive finding).

**It does not fire this pass.** §1 carried check 1 / §2 item 1 is a substantive,
foundational finding — the route to DONE for 3 (and, with their own conditions,
7) roadmap rows now provably requires a code change that the roadmap did not
account for, discovered by tracing the enforced-pass path end-to-end (#255).
That is a "changed picture" in the §7 sense, not "challenging detail". Per the
dispatch, this pass is **not trending clean**, so no @soda pre-flag for a
Tenth-Seat sub-dispatch is required, and none is initiated.

§7 "signs this has gone wrong", checked (no minority reports have ever
accumulated):

- *"same conclusion every pass regardless of evidence"* — scoreboard number
  identical for an 11th pass, but the **picture keeps sharpening**: #16 "waiting
  on an operator" → #17 "operator answered, one coordinator prerequisite" → #18
  "the prerequisite's pass is a near-no-op, a code change is needed". Each pass
  cuts deeper into the *same* cluster with *new* evidence. This is
  evidence-driven, not inertia.
- *"verdict drifting toward reassurance"* — the opposite: this pass says the
  security cluster's route is longer than believed and pre-registers a
  STOP-condition for #19.
- *"no one has run the full check"* — arc range-derived (13 PRs); #255 read in
  full and its deadlock trace independently followed through
  `_resolve_harness_binding` / `resolve_run_session` / `record_run_session_link`;
  #245/#249/#250/#251/#252/#253/#254 verified; scoreboard walked row-by-row.
- *"challenges detail, never a foundational claim"* — §2 item 1 is foundational
  (the route to DONE for the security cluster), not "should a row say DONE".

No Tenth-Seat sub-agent dispatched — Trigger 2 negative in this pass's judgment,
substantive finding present.

## 5. Friction-log consumption

Log walked in full (6 entries; no new capture entries this pass — but see
carried check 4 on the possible stray-checklist-edit entry, flagged to @soda).

| # | Entry | `verified:` | Disposition |
|---|-------|-------------|-------------|
| 1 | self-clear resume prompt dropped | END-TO-END (×3) | **Closed.** This session's lane started with the session-18 handoff injected — 9th confirmation. |
| 2 | coordinate-via-helper-lanes preference | verified | **Closed.** `soda` coordinating; nava/luve/vame/gela lanes across the whole 13-PR arc. |
| 3 | context-rotation checkpoint too small | VERIFIED (#14) | **Closed — no re-open.** `limit_watcher` "context_rotation.py" messages this session correctly ignored (memory `feedback_limit_watcher_hcom`). |
| 4 | triage loop procedure-only | VERIFIED | **Closed.** Consumption duty discharged for a 9th consecutive pass (#10–#18). |
| 5 | orchestrator tool-use burned ~30–40k context | n/a (behavioral), `countermeasure: none yet` | **Consumed — 7th consecutive no-recurrence arc; stays open.** Follow-up line appended. |
| 6 | stale slice-boundary `NonGoalTests` assertions | `END-TO-END (twice — CI caught both)` | **Consumed — the #251 slice-2a impl (first real test) has not landed yet; carries to #19. The #254 selector-quality dispatch applies the discipline (names the superseded boundary).** Follow-up line appended. |

**Escalated:** the possible stray `CAPABILITY_CHECKLIST.md` edit in the
coordinator checkout (carried check 4) — @soda to confirm and, if real, add a
`FRICTION_LOG.md` entry (coordination-hygiene, 4th signal in the arc).

## 6. Recorded for the next pass (check #19)

- **Arc anchor for #19 — the slippage ENDS here.** #18 fully caught up: its arc
  covers every PR from `6ea81b2` through `d8568a3` (HEAD). #19 **returns to the
  standard rule**: anchor = the squash commit of *this* PR (#18), found via
  `git log --oneline --grep='Roadmap trajectory check' main | head -1`, then
  `<that>..HEAD`. **Belt-and-braces for #19 only:** also run `git log --oneline
  1b9fe1d..<#18-squash>` and confirm every line there is in this note's arc
  list (it should be — nothing merged between the #252 squash and #18's branch
  cut that #18 does not enumerate). If that check is clean, the over-anchor is
  retired and #20 onward uses the plain rule with no special note.
- `python3 -m runtime.smoke` exit 0 at `d8568a3`.
- Scoreboard: 16 / 13 / 6 — **eleventh** consecutive. Tenth-Seat Trigger 2
  armed, **did not fire** (§4). Re-arms for #19: a genuinely clean #19 fires it
  — flag @soda BEFORE dispatching a Tenth-Seat sub-agent, then write
  `work/reviews/trajectory-19-minority-report.md`.
- **STOP-condition pre-registered (§3.3):** if #19 finds the #253 operator batch
  still unanswered AND no lineage-bootstrap wiring scoping note dispatched →
  that is a STOP-condition on 6.16 / H5 / 6.22. #19 says so plainly; does not
  CONTINUE a fourth time on the security cluster.
- **Next 3 (verify at #19):**
  1. **Did the operator answer #253?** — items 1–4 as a block; item 5 (the
     #255 A/B lineage-bootstrap decision + Ask #1 timing); item 6 (infra
     permissions). If answered → which lanes dispatched.
  2. **Did the lineage-bootstrap wiring scoping note (#255 §8 B) get
     dispatched + landed?** It is the true bottleneck for 6.16 / H5 / 6.22 —
     the "guard instantiated but callback never fires" trio.
  3. **SEC4 Half 3 slice 2a impl (luve) + 6.9/S6 selector-quality impl (#254
     path a)** — did they land? Both are friction-entry-6's real test (a
     scope-expanding `_select_skills` / CLI change — did it trip a CI-red
     `NonGoalTests` assert or update the boundary in-PR?). #254 impl must not
     regress DIRECT/PARAPHRASE/MULTI_SKILL/NO_SKILL from 1.00; no 6.9/S6/L4
     status flip (a separate gate step decides DONE).
- Merge-authority (#253 item 2): check whether the operator adopted it +
  whether the stray-checklist-edit friction entry was captured.
- `authorized_operators`: present (standing grep check retired). Verify slice 2a
  landed and 6.10 evidence text updated (s/`approve`-only/all lifecycle verbs/),
  no status flip.
- Zombie pid 3874: **dead** (confirmed again — `ps -p 3874` → dead). Its 4
  worktree locks remain releasable under Infra #2 (operator-pending, #253 item 6).

## Resume prompt

You are running roadmap trajectory check #19 for MAPS_Lean. Follow
`playbook/ROADMAP_TRAJECTORY_CHECK.md` (5-step + friction-log consumption) and
`playbook/TENTH_SEAT_REVIEW.md` §7 (read it before recording any clean result).
Worktree off `origin/main`; `git fetch origin main` first.

**Anchor: the standard rule is back.** `git log --oneline --grep='Roadmap
trajectory check' main | head -1` → the check-#18 squash; then `git log
--oneline <that>..HEAD` and check every line. **Belt-and-braces once:** also run
`git log --oneline 1b9fe1d..<#18-squash>` and confirm every PR there is listed
in check #18's arc (it should be). If clean, note "over-anchor retired" and #20+
uses the plain rule.

Method (rule 14): no claim from a PR title/body/review summary; re-verify
against `git show`, merged code, `/usr/bin/grep` over `runtime/` excluding
`tests/`, targeted `unittest` modules (contention protocol — full suite is
CI's). `python3 -m runtime.smoke` must exit 0.

Specifically check: (a) **Was #253 answered by the operator?** — items 1–4
block; item 5 = the #255 A/B lineage-bootstrap decision + Ask #1 timing; item 6
= infra permissions. (b) **Did the lineage-bootstrap wiring scoping note
(#255 §8 B) get dispatched + landed?** — the true bottleneck for 6.16 / H5 /
6.22. (c) **SEC4 slice 2a impl (luve) + 6.9/S6 selector-quality impl (#254 path
a)** — landed? Both are the friction-entry-6 test. #254 impl must hold
DIRECT/PARAPHRASE/MULTI_SKILL/NO_SKILL at 1.00 and flip **no** status cell. (d)
Re-derive 16/13/6. **Trigger 2 re-armed** (#17, #18 both found something) — a
genuinely clean #19 fires it: flag @soda BEFORE dispatching a Tenth-Seat
sub-agent. (e) **STOP-condition (check #18 §3.3):** if #253 is still unanswered
AND no lineage-bootstrap scoping note was dispatched → STOP-condition on 6.16 /
H5 / 6.22; say so plainly, do not CONTINUE a fourth time on the security
cluster. (f) Friction entries 5 (recurrence) + 6 (the two impl PRs) + whether
the stray-checklist-edit entry was captured.

Deliverable: `work/notes/2026-XX-XX-roadmap-trajectory-check-19.md` (+
friction-log follow-up lines, + minority report iff Trigger 2). Update
`CAPABILITY_CHECKLIST.md` ONLY if a status genuinely moved (hard evidence) or a
clause is provably wrong — flag @soda before any status flip.

Workflow: own worktree; PR into `main` (never push); verification-only review;
do NOT spawn your own reviewer — ping @soda; no self-merge; report the PR number
to @soda. Do NOT commit your own review evidence.

STOP + flag @soda if: the §3.3 STOP-condition is met; a status claim is wrong in
a way that changes the route to DONE; the trajectory action would be STOP or an
envelope-leaving REPRIORITIZE; §7 signals the check has gone shallow; or before
dispatching the Tenth-Seat sub-agent.
