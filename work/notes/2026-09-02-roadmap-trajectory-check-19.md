# Roadmap trajectory check #19 — arc: `03b6a34..HEAD`

Nineteenth pass. Predecessor: `work/notes/2026-09-02-roadmap-trajectory-check-18.md`
(PR #256, arc `6ea81b2..HEAD` = 13 PRs #241–#255, deliberate over-anchor, action
**CONTINUE** with a sharpened security-cluster finding, scoreboard 16/13/6 —
eleventh consecutive; substantive finding: the #255 runbook proved the first
`--enforce-canonical-run` pass is a near-no-op — `CanonicalRunGuard` never fires
because no production path writes the `EXPLICIT` `run_session_links` lineage the
supervisor pre-checks — so 6.16 / H5 / 6.22 were blocked on an unscoped **code
change**. #18 pre-registered a STOP-condition for #19: *"if #253 still unanswered
AND no lineage-bootstrap scoping dispatched → STOP on 6.16 / H5 / 6.22."*)

## Arc derivation — standard anchor rule resumes

```
$ git log --oneline --grep='Roadmap trajectory check' main | head -1
03b6a34 Roadmap trajectory check #18 (6ea81b2..HEAD — 13 PRs #241-#255) (#256)

$ git log --oneline 03b6a34..origin/main
3a4b3a4 6.9/S6: _select_skills match-strength gate (closes EXP-B HARD_NEGATIVE) (#260)
5f2e459 SEC4 Half 3 slice 2 (2a): widen opt-in operator gate to all `maps skill` verbs (#259)
f009249 Lineage-bootstrap wiring: maps run bind-session verb (#255 §8 B) (#258)
3e0b8d4 Design note: lineage-bootstrap wiring scoping (#255 §8 B) (#257)
```

Arc = **4 PRs: #257, #258, #259, #260** — within the 3–6 window. HEAD `3a4b3a4`.

**Over-anchor retired — confirmed.** #18 §6 required one belt-and-braces check:
`git log --oneline 1b9fe1d..03b6a34` → `#256, #255, #253, #254` — every one of
#253/#254/#255 is in #18's arc list (#18 covered #241–#255), and #256 is the
check-18 note itself. **No gap.** #19 uses the plain "previous-trajectory-squash"
anchor; #20 onward needs no special note.

Method (rule 14): every consequential claim re-checked against `git show`, a
read of the merged code, `/usr/bin/grep` over `runtime/` excluding `tests/`,
`python3 -m runtime.smoke`, and the frozen-eval test.

## 0. Situational awareness

- `python3 -m runtime.smoke` → **exit 0 at `3a4b3a4`**.
- Each arc PR merged with green CI + an independent review-evidence file
  (vame on #258 and #259; luve on #260; nava on #257). mika (session-20
  coordinator) drained the 3-deep merge queue that had been stalled since soda
  dropped.
- **Scoreboard recounted** from `CAPABILITY_CHECKLIST.md` §7 (`awk -F'|' '{print
  $2,$4}'`):
  - **DONE 16** — 6.1, 6.2, 6.3, 6.6, 6.7, 6.8, 6.13, 6.14, 6.15, 6.18, 6.23,
    6.26, 6.27, 6.28, 6.29, 6.30.
  - **IN PROGRESS 13** — 6.4, 6.5, 6.9, 6.10, 6.11, 6.16, 6.19, 6.20, 6.21,
    6.22, 6.24, 6.33, 6.35.
  - **NOT STARTED 6** — 6.12, 6.17, 6.25, 6.31, 6.32, 6.34.
  - **Identical to passes #8–#18. Twelfth consecutive pass at 16/13/6.**
  - Arc cross-check: `git diff 03b6a34..HEAD -- CAPABILITY_CHECKLIST.md` touches
    **6.9, 6.10, S6** — evidence text only; every `-`/`+` status token reads
    `IN PROGRESS`. `git diff 03b6a34..HEAD -- 'runtime/state/*.sql'
    'runtime/state/store.py'` → **empty** (no schema / no store-MRO change in
    the arc). **No PR in the 4 flips a status.**

## 1. Per-PR verify column (rule 14 — re-confirmed against merged code)

| PR | What | Verified at `3a4b3a4` | Status impact |
|----|------|-----------------------|---------------|
| **#257** `3e0b8d4` | Design note — lineage-bootstrap wiring scoping (#255 §8 B). Verdict SCOPE-FOR-IMPL; recommends a new `maps run bind-session` verb, thin over `store.record_run_session_link`, no operator decision. | `work/notes/2026-09-02-lineage-bootstrap-wiring-scoping.md` present. Design-only — no `runtime/` change in the commit. Its §2 precondition table + §3 minimal-change spec are what #258 implements. | none (design note) |
| **#258** `f009249` | `maps run bind-session` impl — the lineage-bootstrap wiring. Reviewed by vame (APPROVE, 6/7 own mutations killed) at `20d7161`. | `runtime/cli.py:584 _dispatch_run` — thin `_emit(store.record_run_session_link(run_id, worker_id, adapter_id=…, session_id=…, evidence_ref=…, created_by=…))`, mirrors `_dispatch_operator`/`_dispatch_skill`, **no `HarnessService` import**. `run` subparser + `bind-session` at cli.py:125–173. **`/usr/bin/grep -rln record_run_session_link runtime/` now returns `runtime/cli.py`** — i.e. a production **non-adapter** writer of `run_session_links` exists. Before #258 the only production writer was `runtime/harness/adapters/hcom.py`, reachable only *inside* `HarnessService` (the #18 / #255 §3 deadlock). **The deadlock is broken.** No schema change; `git diff` = exactly `runtime/cli.py` + `tests/test_cli_run.py` (the 2 MAY-touch files). | none (correct — #257 MAY-touch defers the H5/6.16 checklist text to the follow-up "exercise" PR nava is doing now) |
| **#259** `5f2e459` | SEC4 Half 3 slice 2a — widen the opt-in operator gate from `approve`-only to all four `maps skill` lifecycle verbs. Reviewed by vame (APPROVE, 5/5 own mutations) at `48d8f48` (rebased). | `runtime/cli.py:644` → gate is now `if store.has_authorized_operator_registry():` (was `… and args.skill_command == 'approve'`); reached only for approve/activate/retire/supersede. `--actor` arg at cli.py:498 → `required=(verb == 'approve')` (optional at argparse for the other three, enforced in dispatch only when the registry is seeded). `test_seeded_registry_does_not_gate_activate` (the #251 §3 Stop-condition boundary test) correctly replaced in-PR by 4 tests — friction-log entry 6's dispatch discipline honoured. | 6.10 evidence text only (`s/opt-in \`maps skill approve\` check/covers every \`maps skill\` lifecycle verb/`) — **no status flip** |
| **#260** `3a4b3a4` | 6.9/S6 `_select_skills` match-strength gate — path (a) of #254 §5. Reviewed by luve (APPROVE, 9/9 mutations after a test-only delta); evidence committed by vame (independent of gela-author + luve-reviewer). | `runtime/context_builder.py:320` `_SKILL_MATCH_STRENGTH_FLOOR = 2.0`, `:322` `_SKILL_ANCHOR_MAX_SKILL_COUNT = 2`, `:329` `_SKILL_ROUTING_STOPWORDS = frozenset(…)`; the gate at `:522–531` — `1/df` token weighting (`Counter` over name+description tokens, stdlib only), stopwords weight 0 and cannot anchor, a Skill surfaced only with an anchor (≥1 non-stopword token in ≤2 Skills) AND (`match_strength ≥ 2.0` OR `match_coverage ≥ 0.5`). `python3 -m unittest tests.test_exp_b_skill_routing` → **3 OK** (`test_corpus_is_frozen` passes — the v2 corpus + its pinned sha are untouched). EXP-B: HARD_NEGATIVE 0.00→1.00, `false_activation_cases` 4→0, `selection_f1` 0.72→0.87; DIRECT/PARAPHRASE/MULTI_SKILL/NO_SKILL held at 1.00; recall unchanged. The SEC4 `capabilities_within_envelope` DENY still fires for every token-matched Skill *before* the strength gate. **Scope: only HARD_NEGATIVE (1 of the 3 gaps #254 §4 listed) is closed** — AMBIGUOUS + VOCABULARY_SHIFT V01 are argued lexically-indistinguishable-from-hard-negatives / would-regress-MULTI_SKILL and routed to the existing path-(b) §17.3 ruling (no new decision surface). | 6.9 + S6 evidence text only — **no status flip** (path-(b) §17.3 ruling, #253 item 4, still pending) |

## 2. What changed (materially)

1. **The #18 lineage-bootstrap bottleneck is BROKEN (#257 scoped → #258
   implemented, one arc).** #18 pre-registered a STOP-condition — *"if #253
   still unanswered AND no lineage-bootstrap scoping dispatched → STOP on
   6.16 / H5 / 6.22."* Both halves are now resolved: #257 dispatched the
   scoping, #258 landed the code. `runtime/cli.py` is a production non-adapter
   writer of the first `run_session_links` ATTACH row, so a `RecoverySupervisor`
   resume can now become routable and `CanonicalRunGuard.__call__` can actually
   fire on a real incident. The 3 lineage-gated rows move from "blocked on an
   unscoped code change" to "wiring landed, needs the enforced pass exercised" —
   nava is running exactly that exercise now (mika dispatch #82729, note-first
   PR, **no `--enforce-*` pass** — that stays operator-gated per #253 item 5).

2. **6.9 selector materially improved (#260).** The safety-relevant failure —
   HARD_NEGATIVE false activation, a wrong Skill surfaced as trust-gated
   evidence — is eliminated (4→0), f1 0.72→0.87, with zero regression on the
   four already-perfect categories and recall unchanged. 6.9/S6 stay IN PROGRESS
   because 2 of the 3 gaps #254 targeted (AMBIGUOUS, VOCABULARY_SHIFT V01) are
   §6.33-class (semantic / query-expansion) and route to the path-(b) §17.3
   ruling — the ruling itself is #253 item 4, still unanswered.

3. **SEC4 Half 3 slice 2a landed (#259).** The opt-in authorized-operator gate
   now covers every `maps skill` lifecycle-transition verb, not just `approve`.

4. **The merge-queue stall was resolved by a coordinator seat (mika, session
   20).** Three APPROVED PRs sat behind the missing `review-evidence` CI check
   for ~1 session; mika took the seat, cross-assigned the evidence commits
   (committer ≠ author ≠ reviewer — vame committed pr-260, luve pr-258, nava
   pr-259), rebased between merges, and drained the queue to `3a4b3a4`. The
   #253 item 2 rule-20 rec (fallback merge-prep ownership) + friction entry 7
   (coordinator-checkout-is-merge-prep-only) are the durable countermeasures,
   still pending the operator batch answer.

## 3. Trajectory action: **CONTINUE**

Not STOP: the #18 STOP-condition is **not met** (lineage-bootstrap scoping was
dispatched *and* implemented). Not REPRIORITIZE: the #18 work order is being
executed cleanly — #258 landed the exact code #18 named as the bottleneck.
Reasoning:

1. **The security-cluster picture genuinely advanced** for the first time in
   ~6 passes of a static scoreboard. 6.16 / H5 / 6.22's blocker was "an unscoped
   code change nobody owns" at #18; it is now "wiring merged, enforced-pass
   exercise in flight." That is real movement even though no row flipped.

2. **The dispatchable runway is healthy:**
   - nava's lineage-bootstrap exercise (in flight) — documents a working
     `maps run bind-session` pass on a fresh `.maps/`, then a checklist-evidence
     PR for H5 / 6.16.
   - The **enforced pass itself** (option A of #255 §8) — within Ask #1's
     *granted* scope (a pass, not a code change), and option B (#258) is now
     done. It needs only the operator's timing "go" + the A/B acknowledgement
     (#253 item 5).
   - 6.9/S6 path-(b) §17.3 ruling (#253 item 4) — a reviewer/operator decision,
     now well-supported by #260's measured result (HARD_NEGATIVE closed, the
     two residuals principled).
   - release-check 3b impl (#253 item 1) — scoped in #249, waiting on the YES.

3. **The single biggest lever is now the #253 operator batch** (still
   UNANSWERED, all 6 items). #258 removed the one blocker that was *not* an
   operator decision. **Recommend @mika escalate #253 — item 5 especially — now
   that option B is complete**: the framing to the operator is simpler than at
   #18 ("the code change is done; we need your go on the timing of one pass,
   and your A/B acknowledgement that it will produce instantiation evidence
   now that a real denial is reachable").

**No CUT SCOPE / ADD.** The roadmap points at DONE; the route runs through
nava's exercise → the operator answering #253 item 5 → one enforced pass →
per-row verification.

## 4. Tenth-Seat / §7 duty (`TENTH_SEAT_REVIEW.md` §2 Trigger 2, §7)

Trigger 2 is **armed** (passes #17 and #18 each found a substantive finding).

**It does not fire this pass.** §2 item 1 is a substantive, foundational finding:
the blocker #18 identified for 3 roadmap rows — "a lineage-bootstrap code change
nobody has scoped" — is now *implemented and merged* (#258), a "changed picture"
in the §7 sense (the route to DONE for 6.16 / H5 / 6.22 moved from blocked to
unblocked-pending-exercise). Per the dispatch, this pass is **not trending
clean**, so no @mika pre-flag for a Tenth-Seat sub-dispatch is required, and
none is initiated.

§7 "signs this has gone wrong", checked (no minority reports have ever
accumulated):

- *"same conclusion every pass regardless of evidence"* — scoreboard number
  identical for a 12th pass, but the picture keeps moving: #16 "waiting on an
  operator" → #17 "answered, one coordinator prerequisite" → #18 "the
  prerequisite is a near-no-op, needs unscoped code" → **#19 "that code is
  merged; the enforced-pass exercise is in flight."** Evidence-driven, not
  inertia.
- *"verdict drifting toward reassurance"* — this pass IS more positive than #18,
  and it is warranted: the thing #18 flagged as the risk (an unowned code
  dependency) was closed in one arc. It is not glossing — §3 names the #253
  batch as the remaining lever and recommends escalation.
- *"no one has run the full check"* — arc range-derived (4 PRs); all 4 read at
  the code level (#258 / #259 I reviewed pre-merge and re-verified on main;
  #260's gate constants + EXP-B run checked; #257 design note read);
  scoreboard walked row-by-row; the `record_run_session_link` writer-set grep
  re-run to confirm the deadlock break.
- *"challenges detail, never a foundational claim"* — §2 item 1 is foundational
  (the route to DONE for the security cluster), not "should a row say DONE".

No Tenth-Seat sub-agent dispatched — Trigger 2 negative in this pass's judgment,
substantive finding present.

## 5. Friction-log consumption

Log walked in full (7 entries).

| # | Entry | `verified:` | Disposition |
|---|-------|-------------|-------------|
| 1 | self-clear resume prompt dropped | END-TO-END (×3) | **Closed.** 10th confirmation. |
| 2 | coordinate-via-helper-lanes preference | verified | **Closed.** mika coordinating; nava/luve/vame lanes across the 4-PR arc. |
| 3 | context-rotation checkpoint too small | VERIFIED (#14) | **Closed — no re-open.** (`limit_watcher` messages this session correctly ignored per memory `feedback_limit_watcher_hcom`.) |
| 4 | triage loop procedure-only | VERIFIED | **Closed.** 10th consecutive discharge (#10–#19). |
| 5 | orchestrator tool-use burned ~30–40k context | n/a (behavioral), `countermeasure: none yet` | **Consumed — 8th consecutive no-recurrence arc; stays open.** The #257–#260 lanes + this trajectory lane used scoped `git show` / `/usr/bin/grep` / `sed -n` / `Read` offset+limit. Follow-up line appended. |
| 6 | stale slice-boundary `NonGoalTests` assertions | END-TO-END (twice) | **Consumed — no CI-red trip this arc.** #259 (slice 2a, a scope-expanding CLI change) rewrote `test_seeded_registry_does_not_gate_activate` in the same PR, exactly the dispatch discipline; #260 flipped `test_exp_b_skill_routing`'s HARD_NEGATIVE structural asserts + `test_exp_a` pins alongside the selector change, also in-PR. **The discipline held on both — first two real tests since the entry.** Follow-up line appended; consider moving to `verified: END-TO-END (×4, discipline held on #259 + #260)`. |
| 7 | agent edited the shared coordinator checkout | confirmed 2026-09-02; countermeasure not yet adopted | **Consumed — no recurrence this arc.** mika ran merge-prep from the coordinator checkout as merge-prep-only (rebase + evidence commit), and the cross-assigned evidence commits were each done in the committer's own worktree. Countermeasure still folded into #253 item 2 (pending the operator). Follow-up line appended. |

**Escalated:** none new. The #253 item 2 / item 4 / item 5 operator decisions
remain the escalation, restated in §3.

## 6. Recorded for the next pass (check #20)

- **Arc anchor for #20:** the squash commit of *this* PR (#19). Standard rule —
  `git log --oneline --grep='Roadmap trajectory check' main | head -1` then
  `<that>..HEAD`. **The over-anchor is fully retired** (confirmed this pass via
  the `1b9fe1d..03b6a34` belt-brace); no special note needed for #20+.
- `python3 -m runtime.smoke` exit 0 at `3a4b3a4`.
- Scoreboard: 16 / 13 / 6 — **twelfth** consecutive. Tenth-Seat Trigger 2
  armed, **did not fire** (§4). Re-arms for #20: a genuinely clean #20 fires it
  — flag @mika BEFORE dispatching a Tenth-Seat sub-agent, then write
  `work/reviews/trajectory-20-minority-report.md`.
- **Next 3 (verify at #20):**
  1. **Did nava's lineage-bootstrap exercise land?** — a documented working
     `maps run bind-session` pass on a fresh `.maps/` (the ATTACH row written,
     reverse-lookup + EXPLICIT lineage both resolve), plus its checklist-evidence
     follow-up PR. Which of **H5 / 6.16 E6(b) / 6.22** did the exercise actually
     advance, and what does each still need (runbook §6 lists per-row unmet
     conditions — verify each hard, do **not** flip a row on the exercise alone).
  2. **Was #253 answered** — especially **item 5** (Ask #1 A/B + timing, now
     that option B / #258 is merged) and **item 4** (6.9/S6 path-(b) §17.3
     ruling). If item 5 landed → the enforced pass (option A) + a **7-row**
     (6.4 / 6.5 / 6.16 / 6.22 / H5 / E4 / L6) verification, HARD, before any flip.
  3. **Did release-check 3b impl (#253 item 1 → #249 spec) get dispatched** if
     the operator said YES?
- STOP-condition watch: if #253 is *still* unanswered at #20 AND nava's exercise
  stalled AND no new ask-independent slice is identified — that is a genuine
  STOP-condition on the security cluster; #20 says so plainly. (Note the
  situation is materially better than #18: option B is done, so "ask-independent
  work" is not exhausted while nava's exercise + its evidence PR are live.)
- Friction: entries 1–4 closed; 5 open (8th no-recurrence arc); 6 held on
  #259 + #260 (consider upgrading `verified:`); 7 no-recurrence, countermeasure
  still pending the operator.

## Resume prompt

You are running roadmap trajectory check #20 for MAPS_Lean. Follow
`playbook/ROADMAP_TRAJECTORY_CHECK.md` (5-step + friction-log consumption) and
`playbook/TENTH_SEAT_REVIEW.md` §7 (read it before recording any clean result).
Worktree off `origin/main`; `git fetch origin main` first.

Anchor: `git log --oneline --grep='Roadmap trajectory check' main | head -1` →
the check-#19 squash; then `git log --oneline <that>..HEAD`, check every line.
The over-anchor is retired — no special anchor note needed.

Method (rule 14): no claim from a PR title/body/review summary; re-verify against
`git show`, merged code, `/usr/bin/grep` over `runtime/` excluding `tests/`,
targeted `unittest` modules (contention protocol — full suite is CI's).
`python3 -m runtime.smoke` must exit 0.

Specifically check: (a) **nava's lineage-bootstrap exercise** — did the working
`maps run bind-session` pass land (ATTACH row written on a fresh `.maps/`,
reverse-lookup + EXPLICIT lineage resolve), plus its checklist-evidence PR?
Which of H5 / 6.16 E6(b) / 6.22 did it advance, and what does each still need
(runbook §6)? **Do not flip a row on the exercise alone.** (b) **Was #253
answered** — item 5 (Ask #1 A/B + timing, option B / #258 now merged) and item 4
(6.9/S6 path-(b) §17.3 ruling)? If item 5 landed → verify 6.4 / 6.5 / 6.16 /
6.22 / H5 / E4 / L6 (7 rows) HARD before any flip; confirm no impl/review agent
ran an `--enforce-*` pass autonomously. (c) Did release-check 3b impl (#249
spec) get dispatched if the operator said YES to #253 item 1? (d) Re-derive
16/13/6. **Trigger 2 re-armed** (#18, #19 both found something) — a genuinely
clean #20 fires it: flag @mika BEFORE dispatching a Tenth-Seat sub-agent.
(e) Friction entries 5 / 6 / 7.

Deliverable: `work/notes/2026-XX-XX-roadmap-trajectory-check-20.md` (+
friction-log follow-up lines, + minority report iff Trigger 2). Update
`CAPABILITY_CHECKLIST.md` ONLY if a status genuinely moved (hard evidence) or a
clause is provably wrong — flag @mika before any status flip.

Workflow: own worktree; PR into `main` (never push); verification-only review;
do NOT spawn your own reviewer — ping @mika; no self-merge; report the PR number
to @mika. Do NOT commit your own review evidence.

STOP + flag @mika if: #253 is still unanswered AND nava's exercise stalled AND
no new ask-independent slice is identified (STOP-condition on the security
cluster — record it plainly); a status claim is wrong in a way that changes the
route to DONE; the trajectory action would be STOP or an envelope-leaving
REPRIORITIZE; §7 signals the check has gone shallow; or before dispatching the
Tenth-Seat sub-agent.
