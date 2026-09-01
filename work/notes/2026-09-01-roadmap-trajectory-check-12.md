# Roadmap trajectory check #12 — arc: `7459333..HEAD`

Twelfth pass. Predecessor: `work/notes/2026-08-31-roadmap-trajectory-check-11.md`
(arc PRs #194–#207, ended at `7459333` / check-11 squash commit; scoreboard held
16 DONE / 13 IN PROGRESS / 6 NOT STARTED, unchanged since pass #8).

## Arc derivation (per playbook as amended by PR #212)

Anchor = squash-merge commit of the previous `Roadmap trajectory check #N` PR on
`main`:

```
$ git log --oneline --grep='Roadmap trajectory check' main | head -1
7459333 Roadmap trajectory check #11 (PRs #194-#207) (#209)

$ git log --oneline 7459333..HEAD
5230c73 Follow-up to #210: close 3 non-blocking items on the stale-caller checker (#213)
015dcc6 SEC3/6.4: validate_ready rejects destructive envelope without operator reauthorization (PR #194 residual) (#211)
c3d62ac docs: trajectory-check arc is a commit range, not a hand-listed PR set (#212)
98b85c3 rule-20 safeguard: CI check for stale "no production caller" docstrings (#210)
```

Arc = **4 PRs: #210, #212, #211, #213**. Not hand-listed — enumerated by the
range, which is exactly why: the dispatch expected "#210, #211, #212" but #213
merged while this check was in progress, and the range command caught it. 1
CI-safeguard PR + its follow-up, 1 docs PR, 1 impl PR. Small arc (the check-11
PR merged only this session; four PRs have merged since). HEAD at check =
`5230c73`.

Verification method (rule 14): no claim taken from a PR title/body/review
summary; every consequential claim re-checked against `git show`, `/usr/bin/grep`
over `runtime/` excluding `tests/`, and a targeted test run.

## 0. Situational awareness

- `python3 -m runtime.smoke` → **exit 0 at `5230c73`** (`sqlite_task_lifecycle`
  ok, WAL / foreign_keys=1 / busy_timeout=5000).
- Targeted test run: `tests.test_policy_state`, `tests.test_state_store`,
  `tests.test_destructive_external_action_guard` at `015dcc6` → 51 tests OK
  (84s); `tests.test_check_stale_no_caller_docstrings` re-run at `5230c73`
  (post-#213) → **18 tests, OK** (was 7 before #213).
- **Scoreboard recounted from the master-inventory §7 table**
  (`work/roadmaps/CAPABILITY_CHECKLIST.md` lines 108–144, 6.1–6.35 = 35 rows,
  Status column):
  - **DONE 16** — 6.1, 6.2, 6.3, 6.6, 6.7, 6.8, 6.13, 6.14, 6.15, 6.18, 6.23,
    6.26, 6.27, 6.28, 6.29, 6.30.
  - **IN PROGRESS 13** — 6.4, 6.5, 6.9, 6.10, 6.11, 6.16, 6.19, 6.20, 6.21,
    6.22, 6.24, 6.33 (`IN PROGRESS (evaluation-only, by design)`), 6.35.
  - **NOT STARTED 6** — 6.12, 6.17, 6.25, 6.31, 6.32, 6.34.
  - **Identical to passes #8 / #9 / #10 / #11.** No label moved across the
    #210–#212 arc. Fifth consecutive pass at 16/13/6.
- `work/roadmaps/00-MASTER-MAPS-CAPABILITY-ROADMAP.md` header still reads
  `PLANNING MASTER — NOT ACTIVE AUTHORITY`; CAPABILITY_CHECKLIST.md is the
  canonical live status view (no second tracker introduced this arc).

## 1. Re-verification of checklist claims against merged code

### 1a. #211 / SEC3 / 6.4 — `validate_ready` destructive-envelope reauth rule. Confirmed.

`git show 015dcc6 -- runtime/state/readiness.py`: `_validate_ready_conn` now
selects `destructive_action, external_side_effect, requires_operator_approval`
from `task_policy` and appends the reason
`destructive/external envelope requires operator reauthorization (set
requires_operator_approval)` when either envelope boolean is set and the reauth
flag is not. Verified live:

- `/usr/bin/grep -n "requires_operator_approval" runtime/state/readiness.py` →
  the rule is present at the readiness layer only; no guard-code change
  (`runtime/policy/destructive_action_guard.py` untouched in the diff —
  `git show 015dcc6 --stat` = `runtime/state/readiness.py +23`,
  `tests/test_policy_state.py +58`, `work/reviews/pr-211-review-evidence.md`).
- No `schema.sql` change, no new policy field (diff confirms).
- Targeted run: `tests.test_policy_state` includes the four new cases
  (destructive-without-flag fails ready; external-side-effect-without-flag fails
  ready; destructive-with-flag passes + promotes; non-consequential unaffected) —
  all pass.

**Does #211 change 6.4's dependency on operator ask #1?** *Partially, and worth
recording precisely.* The rule runs inside `promote_ready` /
`validate_ready`, which is a **default production path** (`maps` promotion) —
not gated behind `--enforce-canonical-run` or any opt-in. So one concrete SEC3
property is now actually enforced in the default flow with no operator decision
required: *a task whose envelope permits a destructive/external action cannot
reach `READY` without `requires_operator_approval` set* (and `record_operator_
approval`'s `NO_APPROVAL_REQUIRED` gate — checklist line 60 / evaluator — then
requires a real `maps approve`). This makes
`DestructiveExternalActionGuard`'s `OPERATOR_REAUTHORIZATION_ABSENT` branch
*reachable for the class it was written for*.

But it does **not** constitute a "first enforced pass" and does **not** flip
6.4. The guard itself still fires only from `HarnessService.stop()`
(`/usr/bin/grep -rn "BEFORE_DESTRUCTIVE_ACTION" runtime/ --include=*.py`
excluding tests → `runtime/harness/service.py` firing site + the guard
registration only), `HarnessService.stop()` still has **zero production
callers** (`/usr/bin/grep -rn "\.stop(" runtime/ --include=*.py` excluding
tests → only `RecoverySupervisor` calls `.resume(...)`, never `.stop(...)`),
and the guard is still composed default-off in
`build_canonical_harness_service`. The capability-declaration-manifest half of
6.4 is still NOT built. **6.4 label correctly stays IN PROGRESS.** The SEC3
row (line 59) already carries this exactly as of PR #211 — verified accurate,
no edit needed.

### 1b. #210 — rule-20 CI safeguard for stale "no production caller" docstrings. Confirmed.

`git show 98b85c3 --stat`: `scripts/check_stale_no_caller_docstrings.py +~200`,
`.github/workflows/review-evidence.yml +2`,
`tests/test_check_stale_no_caller_docstrings.py`,
`runtime/state/skill_lifecycle_storage.py` (docstring fix),
`runtime/policy/memory_provenance_guard.py` + `runtime/recovery/production.py`
(noqa annotations). Verified live:

- `scripts/check_stale_no_caller_docstrings.py` exists (7166 bytes).
- `.github/workflows/review-evidence.yml:34` → `run: python
  scripts/check_stale_no_caller_docstrings.py`, alongside `check_review_evidence.py`
  (line 9 comment cites CLAUDE.md rule 20). So it is a **CI gate**, not just a
  script.
- `runtime/state/skill_lifecycle_storage.py:1-15` docstring now names the real
  callers (`register_skill_catalog()` for `record_skill_lifecycle_subject()`;
  `maps skill approve|activate|retire|supersede` for
  `record_skill_lifecycle_transition()`) — the previously-stale claim is gone.
- `tests.test_check_stale_no_caller_docstrings` — 5 tests pass (planted-caller
  fails, split-line caught, no-caller/test-only/bare-mention pass, noqa
  suppresses, repo clean).

This discharges the recurring incident tracked in memory
`feedback_stale_no_production_caller_docstrings` (which had named
`production.py` #206 and `skill_lifecycle_storage.py:12` as open). Both are now
closed and a mechanical CI safeguard exists — the rule-20 escalation is
satisfied. **No roadmap row maps to this; it is a process-safeguard PR.**

### 1b′. #213 — follow-up hardening of the #210 checker. Confirmed; checker-quality only.

`git show 5230c73 --stat`: `scripts/check_stale_no_caller_docstrings.py`
(rewrite), `tests/test_check_stale_no_caller_docstrings.py` (7→18 tests). No
`runtime/` file, no `.yml` step-placement change, no docstring/roadmap change
(diff confirms — the only non-test, non-script file touched is a removed
`work/reviews/pr-213-review-evidence.md` squash artifact). Closes luve's 3
non-blocking #210 review items: (1) same-module caller blind spot — caller
detection moved from `grep "<symbol>("` + defining-file exclusion to a pure AST
pass over every non-test `runtime/*.py`, with lexical self-recursion excluded;
(2) multi-backtick phrase→symbol attribution rewritten + test-locked;
(3) dead inner-call-shape regex removed. Verified live: `tests.test_check_stale_
no_caller_docstrings` → 18 tests OK at `5230c73`; `python3 scripts/check_stale_
no_caller_docstrings.py` → exit 0 on the current tree. The CI gate from #210 is
unchanged in placement (`review-evidence.yml:34`), now backed by a stronger
checker. **No roadmap row maps to this.**

### 1c. #212 — trajectory-check playbook amendment. Confirmed (this pass consumes it).

`git show c3d62ac -- playbook/ROADMAP_TRAJECTORY_CHECK.md`: "The check" section
now leads with "Derive the work arc from a commit range, never a hand-listed set
of PR numbers", with the concrete `git log --oneline --grep='Roadmap trajectory
check' main | head -1` + `git log --oneline <last-check-commit>..HEAD` commands.
This pass **used exactly that method** (see "Arc derivation" above) — the
amendment is live and self-consistently applied on its first use. `pr-212-review-
evidence.md` (APPROVE, maps-lean-luve, independent) is in the merge.

### 1d. The four "single-threaded" items — re-verified against current merged code.

Check #11 §2/§4 named **6.4, 6.5, 6.16, 6.22** as all blocked on the same
first-enforced-`recovery-tick` operator decision. Re-checked at `015dcc6`:

| Row | Enforcement code merged? | Composed into `build_canonical_harness_service`? | Exposed in a default flow? |
|-----|---|---|---|
| 6.4 / SEC3 | yes (#194 destructive guard; #211 readiness rule) | guard yes, default-off | **readiness rule yes (new, #211); guard no** |
| 6.5 / H4 / E4 | yes (#199 `--enforce-validation` gate) | yes, default-off (`--enforce-validation`) | no |
| 6.16 / E6 | yes (#180 canonical-run guard + worktree seam) | yes, default-off (`--enforce-canonical-run`) | no |
| 6.22 | yes (#202 `MemoryProvenanceGuard` on `BEFORE_SEND`) | yes, default-off | no — and `HarnessService.send()` has no production caller either |

`/usr/bin/grep -rn "build_canonical_harness_service\|harness_project_id"
runtime/ --include=*.py` (excl. tests): still reached only via the opt-in
`harness_project_id` keyword on `run_recovery_tick` / `run_recovery_tick_isolated`
→ `maps recovery-tick --enforce-canonical-run --harness-project-id P --repo-root
PATH`. Never `maps claim`, never `maps flow start`.

So the count is **still accurate**: 6.5, 6.16, 6.22 route entirely through
operator ask #1; 6.4 routes through it for the guard half but **#211 carved out
a live, ungated enforcement sliver** at the readiness layer. Net: the "4 items,
1 ungiven decision" fragility check #11 flagged is unchanged — and it is now on
its **second consecutive pass** (this is the REPRIORITIZE trigger check #11
explicitly pre-registered).

### 1e. SEC4 B1 (operator-identity registry) — did the operator decision land? No.

`work/notes/OPERATOR_ASK_2026-08-31-session13.md` ask #2 is the env-evidence
ratification; the SEC4 trust-root/bootstrap decision is a separate
`OPERATOR DECISION REQUIRED` callout in
`work/notes/2026-08-31-sec4-operator-lifecycle-transitions-and-identity-design.md`.
`/usr/bin/grep -rn "authorized_operators" runtime/` → **no hits**. The
`authorized_operators` table + opt-in check has not landed. `--actor` /
`decided_by` on the `maps skill` verbs remains a structural non-empty check
(checklist line 60, verified accurate). B1 is still design-pending on an unmade
operator decision.

### 1f. Operator asks #1 and #2 — still open.

`work/notes/OPERATOR_ASK_2026-08-31-session13.md` is still **untracked**
(`git status` in the canonical checkout: `?? work/notes/OPERATOR_ASK_2026-08-31-
session13.md`) — not committed, so not in any handoff-durable location beyond
the file. Sessions 13 (`niko`), 14, 15 (`mono`) have all run since it was
written; neither ask has an operator answer recorded anywhere in `work/`.

## 2. What changed (materially)

1. **#211 is the first ungated enforcement win in the SEC3/6.4 cluster.** Every
   prior arc's security slice (#180, #194, #195, #199, #202) added a guard to
   `build_canonical_harness_service` *without exposing it*. #211 is different: it
   put one concrete SEC3 property (destructive envelope ⇒ operator reauth flag
   ⇒ `maps approve` required before `READY`) into `validate_ready`, which runs
   on **every** promotion with no opt-in. It does not flip 6.4, but it is a
   real, live tightening — and it is a template: *find the readiness/shaping-time
   check that makes a guard's branch reachable, and enforce it there rather than
   waiting for the hook-layer exposure decision.*

2. **The "4 items / 1 ungiven decision" fragility is now on its second
   consecutive pass.** Check #11 §5 wrote, verbatim: "If that decision does not
   land soon, the next trajectory check should treat 'four items blocked on one
   ungiven decision' as a REPRIORITIZE trigger." The decision did not land. Three
   sessions have run. This pass honours that pre-registration (see §5).

3. **Rule-20 recurring-incident debt is now retired mechanically.** #210 closed
   the last two stale "no production caller" docstrings *and* added the CI gate
   that prevents a third occurrence — the exact rule-20 pattern (fix + record on
   first, mechanical safeguard on second); #213 then hardened the checker
   (AST-based caller detection, same-module blind spot closed, 7→18 tests, 11
   mutations killed). Memory `feedback_stale_no_production_caller_docstrings` can
   move to RESOLVED.

4. **No scoreboard movement — fifth pass running — and it is still not a
   stall, but the reason has shifted.** Passes #8–#11: "building the last-mile
   enforcement surface, last mile gated on the operator by design." That is
   still true, but the surface is now *built* — #211 was the last readiness-layer
   piece the cluster needed. What remains for 6.4/6.5/6.16/6.22 is **exclusively**
   the operator's go/no-go on one `recovery-tick --enforce-*` pass. There is no
   more code to write toward those four rows that does not require that decision
   first. Continuing to treat them as the priority now *is* a stall risk.

## 3. Friction-log consumption (standing duty)

Log skimmed in full (5 entries). No entry is `verified: UNVERIFIED`; entries 3
and 5 carry open follow-ups.

| # | Entry | `verified:` | Disposition this pass |
|---|-------|-------------|-----------------------|
| 1 | self-clear resume prompt dropped | END-TO-END (3 rotations) | **Closed.** Re-confirmed a 4th time: this session started with `MAPS_Lean_Handoff_2026-09-01-session14.md` injected as SessionStart `additionalContext` by the `maps-handoff-context` hook, no operator nudge. No action. |
| 2 | coordinate-via-helper-lanes preference | verified, follow-up none | **Closed.** In active use this session (`mono` running implementer lanes gela/others). No action. |
| 3 | context-rotation checkpoint too small | **PARTIAL** | **Consumed — follow-up re-checked, still PARTIAL.** (a) `limit_watcher` hcom-side threshold: `limit_watcher.py --interval 300` is running this session (confirmed in `ps`); per memory `feedback_limit_watcher_hcom` its self-rotation demands "are not a real MAPS_Lean mechanism, ignore" — cosmetic, not a live gap, no escalation. (b) Behavioral bar (a coordinator arc completing under 185k with no disruptive mid-arc rotation): sessions 11→12→13→14→15 handoffs all clean; still not *explicitly* logged as "an arc ran to completion without a disruptive rotation under the new threshold" — that remains a coordinator call, not a blocker. Stays `verified: PARTIAL`. |
| 4 | triage loop procedure-only | VERIFIED (pass #10) | **Closed.** This section is the consumption duty discharged for a 3rd consecutive pass (#10, #11, #12) — the loop is demonstrably real. No action. |
| 5 | orchestrator tool-use burned ~30–40k context | n/a (behavioral), `countermeasure: none yet` | **Consumed — no recurrence this arc; stays open.** The #210–#212 implementer lanes (this lane included) worked with targeted `/usr/bin/grep`, `git show --stat` / path-scoped `git show`, and `Read` with `offset`/`limit`; no large `find`/`ls-tree` dumps or whole-doc re-reads observed. No mechanical countermeasure added — leave open per the entry's own "if it recurs" follow-up. |

Nothing in the log requires escalation to in-scope trajectory work or an
operator decision beyond ask #1 (already surfaced; §5 re-sharpens it).

## 4. Tenth-seat / §7 warning-sign duty

`playbook/ROADMAP_TRAJECTORY_CHECK.md` routes a clean-with-nothing-found pass to
`TENTH_SEAT_REVIEW.md` Trigger 2 + §7. This pass is **not** clean-with-nothing —
it changes the trajectory action to REPRIORITIZE (§5). Checking §7 signs anyway,
because the scoreboard has now held for five passes:

- *"The same conclusion every pass regardless of evidence"* — the scoreboard
  number is identical across #8–#12, but this pass does **not** repeat check
  #11's CONTINUE. It acts on the fragility check #11 pre-registered. The
  conclusion moved *because the triggering condition check #11 named actually
  occurred* (the decision did not land across three sessions). That is
  evidence-driven, not inertia.
- *"Verdict drifting toward reassurance"* — the opposite: this pass sharpens
  from "one thing to watch" (check #11) to "REPRIORITIZE + re-surface ask #1
  with a go/no-go framing" (§5, §6). Less reassuring than #11, deliberately.
- *"No one has run the full check"* — the arc was derived by command per PR
  #212's amendment; all 3 PRs in range were checked; the scoreboard was
  recounted from the source table, not copied from #11.
- *"Every consequential claim cites evidence"* — §1 cites `git show` output,
  `/usr/bin/grep` results with the exclusion, file:line, and a passing targeted
  test run for each claim.

No sign the check process itself has gone wrong. One durable improvement already
shipped this arc (PR #212's arc-derivation amendment); it worked on first use.

## 5. Trajectory action: **REPRIORITIZE**

Not CONTINUE. Reasoning:

1. **Check #11 pre-registered this exact action for this exact condition.**
   "If that decision does not land soon, the next trajectory check should treat
   'four items blocked on one ungiven decision' as a REPRIORITIZE trigger."
   The decision has not landed across sessions 13, 14, 15. The condition is met.
2. **The surface those four rows need is now fully built.** #211 was the last
   readiness-layer piece. 6.4, 6.5, 6.16, 6.22 have zero remaining code work
   that does not first require the operator's `--enforce-*` go/no-go. Dispatching
   more "guarded default-off slice" PRs at that cluster produces merges but no
   verifiable roadmap progress — five passes of a static scoreboard is the
   evidence.
3. **REPRIORITIZE here is within the approved envelope.** It changes *work
   order*, not objective/scope/permission. No roadmap edit, no operator
   authority question beyond re-surfacing ask #1 (which is already an open ask,
   not new scope).

### Concrete new next-3 (all fully independent of operator asks #1 and #2)

1. **SEC4 capability-declaration manifest for third-party Skills/tools.**
   Checklist line 60 / 6.10: *"there is still no capability-declaration manifest
   for third-party Skills/tools (SEC4's other half, NOT STARTED)."* This is the
   single largest genuinely-unstarted security item and touches neither ask.
   First step: a design note scoping the manifest shape + where it gates (likely
   `build_project_skill_catalog` / `load_catalog_skill`, which are already
   production-wired per #200/#197). SEC4's lifecycle half is the most-advanced
   security cluster on the board — finishing its other half is high-leverage.

2. **6.21 — `maps flow` review lifecycle operations.** Checklist line 130:
   *"Review record/recover/release/handoff flows remain unimplemented."*
   `runtime/flow_review.py` already has `maps flow review-start`. The
   record/recover/release/handoff verbs are deterministic-lifecycle composition
   work in the same shape as the shipped `flow start` / `review-start` — no
   enforcement decision, no new authority. Directly advances 6.21.

3. **L6 — persist `harness_config_hash` onto real run manifests.** Checklist
   line 74: `runtime/harness/config_ref.py` (`harness_config_ref()`) exists and
   `ExecutionBinding.harness_config_hash` can carry it, *"but no production call
   site actually sets/persists the hash onto a real run manifest yet."* Wire it
   into `create_run_manifest` / `maps flow start`. This makes "each evaluated run
   can identify which configuration produced it" true in practice and unblocks
   L7 (6.31), which is otherwise NOT STARTED purely on this dependency.

(4th if a lane frees: **6.9 / S6 progressive Skill-body loading** — `load_skill`
/ `load_catalog_skill` body activation is still never called from
`context_builder._select_skills`; genuinely independent.)

### Does operator ask #1 need re-surfacing with sharper framing? **Yes.**

Current framing (`OPERATOR_ASK_2026-08-31-session13.md` §1) is accurate but
buries the ask in mechanism. Sharper framing for @mono to carry to the operator:

> **6.4, 6.5, 6.16, 6.22 — and H5, E4 — are code-complete for their next
> milestone and blocked only on one decision.** Every guard is merged and
> composed into `build_canonical_harness_service`. None needs more design or
> code. They need one operator action: authorize (or decline) a single
> `maps recovery-tick --enforce-canonical-run --repo-root <checkout>` pass
> against one named project, once. Expected first-run effect: some currently-
> working resumes become `resume_denied` (most likely `LEASE_EXPIRED`),
> remediated per `docs/CONTROL_PLANE_SETUP.md` §5. Until this happens, 4–6
> roadmap rows cannot advance regardless of any other work — and trajectory
> checks #11 and #12 have both now flagged this as the single highest-leverage
> item on the board.

This is a **recommendation to re-surface an existing operator ask**, not an
answer to it and not a new ask. Flagged to @mono as an operator-decision item.

## 6. Checklist update

**None.** No status moved. The SEC3 row (line 59) already carries the #211
readiness rule accurately (verified §1a); no other row's evidence text is
materially stale as of this arc. This note is evidence, not a status change.
Per the dispatch, a REPRIORITIZE of *work order within the approved envelope*
does not get a roadmap edit — it is delivered as this note + the @mono flag.

## 7. Recorded for the next pass (check #13)

- **Arc anchor for check #13:** the squash commit of *this* PR (`Roadmap
  trajectory check #12`). Use `git log --oneline --grep='Roadmap trajectory
  check' main | head -1` then `<that>..HEAD` — per PR #212, now the standing
  method.
- `python3 -m runtime.smoke` exit 0 at `5230c73` (arc HEAD).
- Scoreboard: 16 DONE / 13 IN PROGRESS / 6 NOT STARTED (35 rows, §7 table) —
  fifth consecutive pass unchanged.
- **Trajectory action this pass was REPRIORITIZE** (first non-CONTINUE since the
  scoreboard stabilised). Next-3 handed to @mono: (1) SEC4 capability-declaration
  manifest, (2) 6.21 review lifecycle ops, (3) L6 harness-config-hash
  persistence. If check #13 finds those three untouched *and* ask #1 still
  unanswered, that is a RESEARCH/STOP-level signal about dispatch throughput,
  not another REPRIORITIZE.
- Operator ask #1 re-surfaced to @mono with a go/no-go framing (§5). If it lands
  before check #13, verify 6.4/6.5/6.16/6.22 hard before any flip.
- Operator ask #2 (env-evidence-writer ratification) — still open, still
  "not a blocker" per its own text.
- Friction entry 3 stays `verified: PARTIAL`; entry 5 stays open (no recurrence
  this arc).
- Memory `feedback_stale_no_production_caller_docstrings` → RESOLVED by #210
  (CI safeguard `scripts/check_stale_no_caller_docstrings.py` in
  `review-evidence.yml`).

## Resume prompt

You are running roadmap trajectory check #13 for MAPS_Lean. Follow
`playbook/ROADMAP_TRAJECTORY_CHECK.md` exactly (5-step check + friction-log
consumption). Work in a worktree off `origin/main`; `git fetch origin main`
first.

Arc: anchor = `git log --oneline --grep='Roadmap trajectory check' main | head -1`
(the check-#12 squash commit), then `git log --oneline <anchor>..HEAD`. Do NOT
hand-list PRs — this method is the standing rule per PR #212.

Method (rule 14): take no claim from a PR title/body/review summary; re-verify
every consequential claim against `git show`, `/usr/bin/grep` over `runtime/`
excluding `tests/`, and a targeted test run. `python3 -m runtime.smoke` must
exit 0 — record the sha.

Specifically check: (a) Did operator ask #1 (first enforced
`--enforce-canonical-run` / `--enforce-validation` production pass) get
answered? If authorized and run, 6.4/6.5/6.16/6.22 + H5/E4 may finally be
flippable — verify hard before flipping. (b) Did the check-#12 REPRIORITIZE
next-3 get dispatched and land: SEC4 capability-declaration manifest, 6.21
review lifecycle ops (`maps flow record|recover|release|handoff`), L6
harness-config-hash persistence on real run manifests? (c) Re-derive the
16/13/6 scoreboard from the master-inventory §7 table. (d) Friction entry 3
(behavioral bar) and entry 5 (recurrence). (e) SEC4 B1 — did the operator
trust-root decision get made and did `authorized_operators` land?

If check #12's next-3 are untouched AND ask #1 is still unanswered, that is a
RESEARCH/STOP-level signal about dispatch throughput — escalate to @mono /
operator, do not just REPRIORITIZE again.

Deliverable: `work/notes/2026-XX-XX-roadmap-trajectory-check-13.md` —
situational awareness, what-changed, a single trajectory action with reasoning,
friction-log consumption results, recounted scoreboard. Update
`work/roadmaps/CAPABILITY_CHECKLIST.md` ONLY if a status genuinely moved (with
hard evidence — merged code + passing tests).

Workflow: own worktree; PR into `main` (never push to main); do NOT spawn your
own reviewer — ping the coordinator; no self-merge; report the PR number to the
coordinator.

STOP + flag the coordinator if: reality contradicts a checklist claim in a way
that needs a status flip you are not certain of, or the trajectory action would
be STOP or a REPRIORITIZE that leaves the approved envelope.
