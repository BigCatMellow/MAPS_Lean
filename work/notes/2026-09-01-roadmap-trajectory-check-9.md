# Roadmap trajectory check #9 — arc: PRs #177-#180 + a 42-commit governance batch

Ninth pass. Pass #8 (`work/notes/2026-08-26-roadmap-trajectory-check-8.md`,
merged via PR #176 at head `722beab`; the dispatch's cited `f3fc1e2` is a
pre-merge commit on that same PR branch) covered PRs #164-#175. This pass covers
everything merged to `origin/main` since, at head `38cb136`:

- **#177** (`69bf053`) — design note for the Hook/Harness production composition
  root (the item pass #8 §5a ranked #1).
- **A 42-commit governance/consolidation batch** (`e369946`..`6462095`, all
  authored 2026-08-28 06:07-07:17 by `BigCat Mellow`) — rewrites the
  operating/authority model: AGENTS.md as sole operating contract, approved
  roadmap as autonomous execution authority, standing permission envelopes,
  autonomous review gates inside scope, brevity as a hard rule, AGI/HPOM
  playbook consolidation, doc-sprawl CI guard.
- **#178** (`d1ace1d`) — wiki + `/pilot` fresh-agent onboarding surface.
- **#179** (`ccc9bbf`) — Pilot navigation compaction; `INFORMATION_LIFECYCLE.md`
  owns the no-island rule; operational-independence gate in `TASK_LIFECYCLE.md`;
  retired `docs/WORKFLOW.md` + `docs/CONTEXT.md`.
- **#180** (`38cb136`) — implements #177: `runtime/recovery/production.py::
  build_canonical_harness_service`, opt-in `maps recovery-tick
  --enforce-canonical-run --harness-project-id P --repo-root PATH`, default-off.

Verification method (unchanged from pass #8): no claim taken from a PR title,
body, or review-evidence summary; every consequential claim verified against
`git show --stat` / `gh pr view` / `gh api .../commits/<sha>/pulls` / direct
`grep` over `runtime/` excluding `tests/`.

## 0. Situational awareness

- `python3 -m runtime.smoke` passes clean at `38cb136` (`ok: true`, exit 0).
- `git log f3fc1e2..origin/main --oneline` = 46 commits: PRs #177/#178/#179/#180
  (GitHub-authored squash/merge commits), plus 42 `BigCat Mellow`-authored
  commits with **no associated PR** (see §2c).
- Two lanes IN FLIGHT, not merged, treated as in-progress here (not
  re-investigated): **PR #174** ("Add bounded Spiderweb relationship audit",
  OPEN) and the `impl/worktree-binding-guard-*` PR (6.16/E6 guard-layer per
  #175's seam design). PR #173 ("Reconcile project truth and durable
  information links") is CLOSED unmerged.

## 1. Re-verification of pass #8's named items

### 1a. Did #180 add a real production composition caller? — Yes, but gated.

`grep -rn "register_canonical_run_guards\|HarnessService(\|HookRegistry()"
--include=*.py . | grep -v "^./tests/"` — pass #8 found ONLY definitions +
re-exports + `HarnessService`'s own internal `hooks or HookRegistry()` default.
Delta this pass: **`runtime/recovery/production.py:385-389` now composes all
three for real** —

```
registry = HookRegistry()
register_canonical_run_guards(registry, CanonicalRunGuard(task_reader, repo_root=repo_root))
return HarnessService([adapter], hooks=registry)
```

inside `build_canonical_harness_service()`. This is the first non-test
composition root in the repo's history. Pass #8's §3a root-cause finding ("no
production composition root") is **resolved as a code fact.**

### 1b. Is it reachable in a default (non-opt-in) production path? — No.
Verified against `runtime/recovery/production.py:452-467` and
`runtime/cli.py:413-435`:

- `run_recovery_tick(..., harness_project_id=None)` is the default; with `None`,
  `harness_service` stays `None` and nothing is constructed (`production.py:452`).
- `harness_project_id` is set ONLY by `maps recovery-tick --enforce-canonical-run`,
  which `argparse`-errors unless BOTH `--repo-root` and `--harness-project-id`
  are also passed (`cli.py:414-427`; "never inferred from an incident").
- `--repo-root` alone stays advisory-validation-only (`production.py:457`).
- The `maps claim` piggyback path never passes `harness_project_id`
  (`production.py` docstring line 22-23; `cli.py` claim branch does not thread it).
- `maps flow start` composes no `HarnessService` at all (unchanged).

So pass #8's finding that enforcement is NOT on a default production path
**still holds** — #180 did not silently change that. It is default-off by
explicit design (#177 §2c, because `CanonicalRunGuard` never returns ALLOW and
denies on absent evidence: first exposure converts working resumes to
`resume_denied`, most likely `LEASE_EXPIRED`).

### 1c. Are #180's `CAPABILITY_CHECKLIST.md` edits accurate; was any status
flipped? — Edits accurate; **no status flipped**; one row it should also have
touched was missed.

`git show 38cb136 -- work/roadmaps/CAPABILITY_CHECKLIST.md` updated **H5, E4,
6.5, 6.16** evidence text (all dated "Updated 2026-08-30"). Spot-checked each
against merged code:

| Row | #180's new text | Verdict |
|---|---|---|
| H5 | "`build_canonical_harness_service` is now the production composition root ... Default-off ... closes only after the first real production exposure" | Accurate. Label stays `IN PROGRESS`. |
| E4 | "a production `HookRegistry` now exists ... carries the `CanonicalRunGuard` fail-closed guard only — `make_validation_hook`'s advisory callback is still not attached" | Accurate — verified no `make_validation_hook` / validation callback in `production.py`. Label stays `IN PROGRESS`. |
| 6.5 | "the CANONICAL_RUN enforcement layer now has a production composition root ... but that guards canonical-run identity, not environment/validation-tier outcome, and has had no first production exposure" | Accurate. Label stays `IN PROGRESS`. |
| 6.16 | "`build_canonical_harness_service` now composes all three ... reachable only via the opt-in ... E6(b) remains open: enforcement is default-off" | Accurate. Label stays `IN PROGRESS`. |

- **H4 and 6.4**: #180 did not touch them and did not need to — neither claims
  anything the composition root falsifies (H4 is validation-hook scope; 6.4's
  "write/destructive/external guards not built" is still true — #180
  deliberately did NOT register `DestructiveExternalActionGuard`, #177 §3d,
  verified: no destructive-guard symbol in `production.py`).
- **SEC3** (§4, sub-roadmap row): still accurate — its claim is specifically
  that `BEFORE_EXTERNAL_ACTION` / `BEFORE_DESTRUCTIVE_ACTION` have "zero
  registered guards anywhere", which remains true.
- **E6** (§3, sub-roadmap row, line 50): **NOT updated by #180 and now
  falsified.** Its clause (b) still reads "`register_canonical_run_guards()`
  and `HarnessService(...)` have no non-test callers, so the CANONICAL_RUN
  enforcement layer is library-only". #180 added exactly such a caller. The
  master-inventory 6.16 row (line 125) got the corrected wording; the E6 row is
  the asymmetric-miss twin of the exact same finding. **Corrected this pass**
  (§2) — clause (b) rewritten to mirror the 6.16 row: composition root exists,
  default-off, no first exposure, worktree seam still not in `CanonicalRunGuard`.
  Label deliberately unchanged (`IN PROGRESS`).

### 1d. Targeted re-verification

| Claim under test | Result |
|---|---|
| #177 is design-only, no runtime code | **Confirmed** — `git show --stat 69bf053`: only `work/notes/...` + review evidence. |
| #178 / #179 did not touch `CAPABILITY_CHECKLIST.md`, the master roadmap, or `ROADMAP_TRAJECTORY_CHECK.md` | **Confirmed** — file lists are docs/wiki/`playbook`/`tests`/`tools` only; no roadmap-status file. |
| `TENTH_SEAT_REVIEW.md` survived the playbook consolidation | **Confirmed** — `playbook/TENTH_SEAT_REVIEW.md` present; `playbook/INDEX.md` still lists it. |
| `ROADMAP_TRAJECTORY_CHECK.md` now cross-references `TENTH_SEAT_REVIEW.md` (pass #8 §6 open item, PR #169's own follow-up) | **Still NOT done** — `grep "TENTH_SEAT\|Tenth Seat\|Trigger 2" playbook/ROADMAP_TRAJECTORY_CHECK.md` → empty. Commit `1680540` ("Move roadmap status governance into roadmap trajectory method") edited this file but did not add the xref. Remains a one-line docs fix, out of this PR's boundary. |
| `record_run_environment_evidence` still zero production writers | Not re-checked this arc (no PR touched `runtime/state/environment.py`); assumed still true per pass #8. |

## 2. Scoreboard and corrections

Recounted directly from the master-inventory §7 table (`CAPABILITY_CHECKLIST.md`
lines 108-144), 6.1-6.35:

**35 rows. DONE 16 / IN PROGRESS 13 / NOT STARTED 6.** Identical to pass #8 — no
status-label delta.

- **DONE (16):** 6.1, 6.2, 6.3, 6.6, 6.7, 6.8, 6.13, 6.14, 6.15, 6.18, 6.23,
  6.26, 6.27, 6.28, 6.29, 6.30.
- **IN PROGRESS (13):** 6.4, 6.5, 6.9, 6.10, 6.11, 6.16, 6.19, 6.20, 6.21,
  6.22, 6.24, 6.33, 6.35.
- **NOT STARTED (6):** 6.12, 6.17, 6.25, 6.31, 6.32, 6.34.

No merged PR this arc met any exit gate. #180 explicitly does not close 6.4 /
6.5 / 6.16 / H5 (default-off, no first enforced pass) — per #177 §5/§6 and
#180's own checklist text, and per this dispatch's MUST-NOT. Confirmed correct
to leave every label unchanged.

**One evidence-text correction this pass** (label unchanged):

1. **E6** (`CAPABILITY_CHECKLIST.md` §3, line 50) clause (b) — "`register_canonical_run_guards()`
   and `HarnessService(...)` have no non-test callers ... library-only" is
   falsified by `runtime/recovery/production.py::build_canonical_harness_service`
   (PR #180, `38cb136`). Rewritten to mirror the already-correct 6.16
   master-inventory row: a production composition root now exists but is
   default-off, exercised only on the opt-in `recovery-tick` path, with no first
   real exposure, and the E6(a) worktree-binding seam is still not inside
   `CanonicalRunGuard`.

This is the same asymmetric-miss failure mode pass #8 §2 caught six times: an
implementation PR updates the master-inventory row but not its sub-roadmap twin
(or vice versa). #180 was better than the #165/#171/#172 batch — it DID ship
checklist edits with the code — but still updated 6.16 without updating E6.
Narrower recurrence, same class.

## 3. What changed the picture

### 3a. Pass #8's #1 horizon item landed as designed

#177 → #180 is a faithful, correctly-scoped design→bounded-impl pair (verified
file-level, not from titles). #180's boundary: `runtime/recovery/supervisor.py`
untouched (the `harness_service` branch already existed), `cli.py` stays clean
of composition, `TaskStore` reused as `CanonicalRunSource` (no second store),
`DestructiveExternalActionGuard` deliberately not registered. It engages
`production.py`'s documented `harness_service=None` reasoning rather than
reversing it (adds an opt-in keyword beside it). Non-daemon, bounded-CLI-pass
shape per master roadmap §7.1/§7.9. **This is exactly what pass #8 asked for.**

Consequence for the horizon: the single gap that pass #8 said blocked 6.4, 6.5,
6.16 and H5 "all at once" is now a code fact resolved. Those four rows are no
longer blocked on *infrastructure* — they are blocked on **a decision to turn
enforcement on for a real pass**, plus (for 6.16) the worktree seam, plus (for
6.5) turning advisory validation into a gate. That is a materially different,
and smaller, blocker.

### 3b. The 42-commit governance batch: material to the operating model, immaterial to roadmap scope

Read the batch (`git log e369946..6462095`). It rewrites *how* work is
authorized and executed: approved roadmap = autonomous execution authority
(`aa53067`, `01f9fc2`), standing permission envelopes + exception-based
escalation (`763af93`), autonomous review gates inside scope (`ee2d3c6`),
consequential flags demoted to metadata not approval gates (`8e3689d`),
`AGENTS.md` as sole operating contract (`35b9023`), brevity as a hard rule
(`ed0a1e3`), AGI/HPOM playbook consolidation (`18c9ead`, `4f04cb6`, `e1c586c`),
and a doc-sprawl CI guard (`c89574a`, `a3ff945`).

Assessment against `ROADMAP_TRAJECTORY_CHECK.md` step 2 (does this materially
change assumptions / dependencies / risk / priority / scope / route to DONE?):

- **Roadmap scope / capability inventory: unchanged.** No capability number
  added, removed, re-scoped, or re-gated. The 35-row scoreboard is untouched by
  it. `00-MASTER-MAPS-CAPABILITY-ROADMAP.md` §6 priority tags unchanged
  (spot-checked 6.4 `P1`, 6.5 `P1`, 6.16 `TRIGGERED`, 6.10 `P1/P2`).
- **Route to DONE: mildly accelerated, not redirected.** The batch strengthens
  "approved roadmap authorizes autonomous execution", which *is* the premise
  this trajectory-check method already operated on. It removes some
  human-approval friction from dispatching the next roadmap item — consistent
  with, not contradicting, the roadmap.
- **No contradiction with a roadmap assumption found.** Checked specifically:
  the master roadmap's non-daemon invariant (§7.1/§7.9) and evidence-gated
  posture on 6.31-6.34 are not touched; `EXECUTION_INTEGRITY.md` is explicitly
  kept "subordinate to the operating contract" (`3699824`) but not weakened in
  substance.
- `1680540` edited `ROADMAP_TRAJECTORY_CHECK.md` itself ("Roadmap/status truth
  rule" section) — verified the current method file still carries the 5-step
  check, the one-canonical-status-view rule, and the "don't mark DONE from prose
  review alone" rule this pass depends on. Method not degraded.

### 3c. Process finding: the governance batch bypassed PR + independent review

`gh api repos/BigCatMellow/MAPS_Lean/commits/<sha>/pulls` for `e369946`,
`ed0a1e3`, `35b9023`, `c89574a`, `1680540`, `6462095` — **every one returns
empty.** No PR is associated with any of the 42 commits. They are authored by
`BigCat Mellow` (the operator's account), not by `GitHub` (the squash-merge
author on #177-#180), and land as a contiguous first-parent run with no merge
commit. Conclusion: **pushed directly to `origin/main`, bypassing the PR +
independent-review process** that every other change this arc (and the entire
recent history) went through.

This matches a known standing risk (`memory/feedback_no_direct_main_push.md`:
"branch protection can be silently bypassed"). Rule 17 (an owner never approves
their own substantive work) and the project's own independent-review
enforcement (`scripts/check_review_evidence.py`) are not satisfied for a change
that rewrites the operating contract — a high-consequence surface.

I am not reverting it: it is the operator's own account, the operator has
authority over the operating contract, and the content itself is coherent and
roadmap-consistent (§3b). But the *process* deviation is a substantive finding
and is flagged for operator awareness. If governance changes of this size are
going to land operator-direct by intent, the review-evidence contract should
say so explicitly rather than leave it as an apparent bypass.

### 3d. Not changed this arc

6.19/6.20/6.21 undocumented-trigger-discipline gap (pass #6) — dormant, no PR
touched them. 6.35/D3 still blocked on operator target decision. 6.24
production environment-report source/cache unchanged. 6.9/S6 progressive Skill
body loading unchanged. 6.22 tool-call gate unchanged. SEC4 store still has zero
non-test writers (no PR this arc touched `runtime/state/skill_lifecycle_*`).

## 4. Decision: CONTINUE

Per method step 3, one action: **`CONTINUE`.**

Reasoning: pass #8 chose `REPRIORITIZE` to move the composition root to #1.
#180 delivered it, faithfully and in the shape pass #8 specified (§3a). The
remaining horizon items are all still in-scope, still correctly ordered, and no
new evidence forces a re-rank or a scope change. The governance batch changes
the authority model but not roadmap scope or the route to DONE (§3b). The one
process finding (§3c) is a governance/review-discipline issue, not a
roadmap-trajectory signal. There is no discovered blocker that changes several
items, the checklist is not "mostly conditional/blocked" beyond what pass #8
already recorded, and task-level steering is not signalling a stale priority
model. `CONTINUE` is the honest call — the plan is pointing at DONE and the
last arc advanced it exactly as planned.

Not `ADD IN-SCOPE WORK`: the ROADMAP_TRAJECTORY_CHECK↔TENTH_SEAT_REVIEW xref
(§1d) and the E6 checklist correction (§2) are housekeeping already covered by
existing follow-ups / this PR, not new scope.

## 5. Horizon report

### 5a. Immediately next — re-ranked now that the composition root exists

1. **Settle the two design questions blocking the first enforced `--enforce-canonical-run`
   pass** (serves 6.4, 6.5, 6.16, H5 — `P1` throughout). #177 §5 Q4/Q5 are
   explicitly unresolved: (Q4) how an enforced `HOOK_DENIED` interacts with the
   RnS retry budget (it becomes `resume_denied` → on repeat
   `failed`/`retry_budget_exhausted` with no fallback), and (Q5) the operator
   workflow for an expired-lease denial. These must be answered *before*
   enforcement is switched on for any real project, because the first pass
   converts currently-working resumes into denials. Short design note, not an
   impl. **Ranked #1: it is the single gate in front of closing four `IN
   PROGRESS` rows, and the infra it needs already exists.**
2. **Worktree-binding guard enforcement** (`work/tasks/worktree-binding-guard-enforcement.md`,
   6.16/E6, `TRIGGERED`) — *in flight* (`impl/worktree-binding-guard-*` PR).
   Now that `build_canonical_harness_service` exists, this guard will actually
   be composed rather than registered onto nothing. Should land before or with
   item 1's first enforced pass so that pass enforces the current seam. Not a
   fresh dispatch — track the in-flight PR to merge.
3. **SEC4 Half 2 — real authority wiring + first writer** (6.10, `P1/P2`).
   Fully independent of the Hook layer, fully designed
   (`work/notes/2026-08-25-sec4-skill-lifecycle-persistence-design.md`), and
   #171's store still has **zero non-test writers**. A first real
   `record_skill_lifecycle_*` writer plus `decided_by` authority resolution is
   the natural next slice. **Best fresh dispatch if item 1 is taken or
   deferred.**
4. **SEC3 guard first call site** (6.4, `P1`). `#164`'s design names it as the
   separate follow-up; same "needs a composed registry" dependency as item 2,
   now satisfiable.

### 5b. Next tier

1. **Turn advisory validation into a gate** (6.5/H4/E4). #172's
   `resume_validation` field is consulted by nothing; who may let a failed
   `quick` tier block a resume is a real open question. Short design first.
2. **6.24 — production environment-report source/cache** (`P1/P2`). Unchanged.
3. **6.22 — memory-trust enforcement past the Context Builder plan to a
   tool-call gate** (`P1`). The row's own surviving "Still missing" clause.
4. **6.9/S6 — progressive loading of matched Skill bodies.** Still the one
   Skill-routing slice that is metadata-only.

### 5c. Correctly gated/blocked — do not re-investigate

Unchanged from pass #8, re-spot-checked: **6.35/D3** (operator target
decision), **6.25/SEC6** (`TRIGGERED`, no recorded trigger), **6.17/E7** (gated
on 6.16), **6.31-6.34** (`EVIDENCE-GATED`/`NOT STARTED` by current roadmap
decision), **6.12/S7** (gated on S6).

## 6. Tenth Seat check (`playbook/TENTH_SEAT_REVIEW.md`)

**Trigger 2 — evaluated, does not fire.** The tripwire was armed (pass #8's
Resume prompt: "stays armed only if pass #8 AND pass #9 both find something";
pass #8 found plenty). Trigger 2 requires *this* pass to report **no
substantive finding**. It does not: (a) a falsified `CAPABILITY_CHECKLIST.md`
row corrected (§2, E6 clause b); (b) a process finding that a 42-commit rewrite
of the operating contract bypassed PR + independent review (§3c); (c) a
re-ranked horizon with a concrete new #1 (§5a). Trigger 2's precondition is
unmet — no minority report is produced. Recording the evaluation, not just the
conclusion, so pass #10 can see it was checked.

**Tripwire state for pass #10:** pass #8 found something, pass #9 found
something → per pass #8's own phrasing the tripwire **stays armed** for pass
#10. If pass #10 also finds nothing substantive, that's the two-consecutive
condition — produce the minority report then.

**Trigger 1 — not applicable.** No PR this arc flipped a status row to `DONE`,
so the "zero-finding status-flipping PR" conjunction could not arise. Recorded
for completeness.

**§7 warning-sign duty (this pass's assigned standing check).** `ls
work/reviews/ | grep -i "minorit\|tenth"` → empty. No minority/dissent reports
have accumulated since the convention landed (PR #169, ~6 days ago). Every
warning sign ("all GREEN", "same agent keeps drawing the role", "reports
accumulate and nothing reopens") is still vacuously not-yet-observable — but
note that the §3c process finding is precisely the kind of thing a standing
adversarial seat exists to surface, and it was surfaced here by ordinary
verification discipline, not by a dedicated dissent pass. The check is
discharged; first real evaluation is still a future pass's.

**Open item (out of this PR's boundary):**
`playbook/ROADMAP_TRAJECTORY_CHECK.md` still has no cross-reference to
`TENTH_SEAT_REVIEW.md` (§1d) — PR #169's own stated follow-up, now two passes
old. A session following the trajectory-check procedure top-to-bottom still
cannot discover Trigger 2 or the §7 duty. One-line docs fix; should be picked
up as housekeeping.

## 7. Honesty check on drift

Does every merged PR this arc trace to something a prior pass ranked
next-to-dispatch?

- **#177, #180** — pass #8 §5a item 1, verbatim. Clean.
- **#178, #179** — Pilot onboarding / navigation. **Not** on any trajectory
  pass's horizon. These are operator-directed operability work (the "Pilot"
  fresh-agent surface), not roadmap-capability work, and they carry PR +
  review evidence (`work/reviews/pr-178-*`, `pr-179-*`). Not speculative
  *capability* additions — they add no `runtime/` capability, only docs/wiki +
  doc-sprawl tests. Defensible as out-of-band operability investment, flagged
  here for completeness per the honesty duty.
- **The 42-commit governance batch** — operator-directed operating-model work,
  no roadmap number, no `runtime/` code. Not speculative capability. But it
  bypassed the process every other change followed (§3c) — that is the honest
  concern, recorded.

**Evidence weakening this pass's own conclusions, recorded per standing
practice:**

1. The `CONTINUE` call rests on judging the governance batch as
   roadmap-neutral (§3b). That is a substantial read of 42 commits done by
   `git log` + targeted `git show`, not a line-by-line audit of every diff. It
   is possible one of them re-scopes something subtle (e.g. the
   "consequential flags as metadata" change `8e3689d` could interact with how
   6.4/SEC3's future guards surface deny decisions). I checked the commits most
   likely to matter; I did not read all 42 diffs in full.
2. §1b's "still default-off, unchanged" conclusion depends on `maps claim`
   never threading `harness_project_id`. I verified the `recovery-tick` branch
   and the `production.py` default; I read the claim-piggyback path via the
   docstring and `cli.py` structure rather than tracing every call frame.
3. The §5a #1 ranking assumes turning enforcement on is genuinely the critical
   path. If the operator does not intend `--enforce-canonical-run` to be used
   on a real project any time soon, then items 3 (SEC4 Half 2) and 5b.1
   (validation→gate) are the real next work and item 1 is premature. #177's own
   design leaves that timing as an operator call.

## Resume prompt

Trajectory check #9 is merged. `CAPABILITY_CHECKLIST.md`'s E6 row (§3, clause b)
was corrected — its "no non-test callers / library-only" claim was falsified by
PR #180's `runtime/recovery/production.py::build_canonical_harness_service`, the
first production composition root; label unchanged (`IN PROGRESS`). Scoreboard
holds at 35 rows, 16 DONE / 13 IN PROGRESS / 6 NOT STARTED — no label moved this
arc, and no PR met an exit gate. Trajectory action was `CONTINUE`: pass #8's #1
item (the composition root) landed faithfully in #177→#180, default-off by
design, so 6.4/6.5/6.16/H5 are no longer blocked on infrastructure — they are
blocked on a decision to run a first enforced `--enforce-canonical-run` pass.
Pick up §5a item 1: a short design note answering #177 §5 questions 4 and 5
(enforced `HOOK_DENIED` vs. the RnS retry budget; operator workflow for an
expired-lease denial) — the gate in front of closing four `IN PROGRESS` rows.
If that is taken or the operator is not ready to enable enforcement, §5a item 3
(SEC4 Half 2: first real `record_skill_lifecycle_*` writer + `decided_by`
authority resolution, fully designed in
`work/notes/2026-08-25-sec4-skill-lifecycle-persistence-design.md`, store still
has zero non-test writers) is the independent fresh dispatch. Track the
in-flight `impl/worktree-binding-guard-*` PR and PR #174 (Spiderweb audit) to
merge. TWO standing process findings for operator attention: (1) a 42-commit
rewrite of the operating contract (`e369946`..`6462095`, 2026-08-28) was pushed
directly to `main` with no PR and no independent review — either that is
intended for operator-direct governance changes and the review-evidence
contract should say so, or branch protection needs tightening; (2)
`playbook/ROADMAP_TRAJECTORY_CHECK.md` still has no cross-reference to
`playbook/TENTH_SEAT_REVIEW.md` (PR #169's own follow-up, now two passes
unaddressed) — one-line docs fix. Tenth Seat Trigger 2 did NOT fire for pass #9
(this pass found substantive things); per pass #8's phrasing the tripwire stays
armed, so if pass #10 finds nothing substantive, produce the minority report
then. Run pass #10 after the next 3-6 merges.
