# Roadmap trajectory check #31

Independent author lane (`fore`, hcom name `trajectory-check-fore`,
dispatched by `rumi` — an independent reviewer, not the coordinator `venu`).
Zero prior involvement in whatever merged since `b60b81d`. Fresh clone from
`https://github.com/BigCatMellow/MAPS_Lean.git` to a unique `/tmp` path
(never `~/Projects/MAPS_Lean`), `git status --porcelain` clean at start.

Anchor (check #30's own squash commit, `git log --oneline --grep='Roadmap
trajectory check' main | head -1`): `b60b81d`.
Arc: `b60b81d..HEAD` = `git log --oneline b60b81d..HEAD`:

```
f192ab7 6.4: require_write_scope_binding opt-in flag -- schema + API, no guard yet (#362)
6ee99b7 6.4: scope verify_git_run enforcement wiring -- names a fork, stops before choosing (#361)
0a58d23 6.4: composed-but-inert write-scope guard + verify_git_run discovery (#360)
8adfa31 Add pre-dispatch roadmap-row freshness check (#359)
41277b5 docs: refresh Development status for 2026-09-14
08fd074 docs: refresh Development status for 2026-09-13
557abf6 Add mechanical safeguard for handoff-register drift (rule 20) (#358)
a92169f Track THINK/PLAN/Prime as cross-project dependencies (visibility only) (#357)
e9fff49 6.22: first non-vacuous WITHHOLD pass through MemoryProvenanceGuard (fixture b) (#356)
8ef7a27 Bulk-register legacy handoffs as UNTRIAGED (#351)
330160f Design: 6.22 WITHHOLD/DENY fixture construction (#355)
d80411a Add reset desk log (#353)
a0d979c Register session43 handoff, add missing receipt (#354)
03d26b5 Add standing merge authorization to opcmd_merge.py (#352)
8f70527 Document isolated-worktree default in AGENTS.md (IDEA-20615e4d) (#350)
```

13 PRs (#350, #351, #352, #353, #354, #355, #356, #357, #358, #359, #360,
#361, #362) plus two direct-to-`main` commits with no associated PR
(`08fd074`, `41277b5`, both "docs: refresh Development status", both
authored by the operator's own git identity — see below). No PR merged
outside this range (`gh pr list --state merged --limit 15` cross-checked
against the log).

**Mid-pass re-fetch note (two rounds).** Round 1: #360 and #361 (the active
6.4 guard-work lane) landed while this pass was waiting on the full test
suite — `origin/main` moved from `8adfa31` to `6ee99b7` mid-run, exactly the
stop condition this pass's dispatch named ("if you find the 6.4 lane has
already changed `CAPABILITY_CHECKLIST.md` rows out from under you,
re-fetch and re-derive"). Re-fetched, fast-forwarded the local clone
(`git status --porcelain` before the merge showed only this pass's own
uncommitted edits, no conflict), and re-derived the scoreboard fresh below.
Round 2: #362 landed shortly after this PR was first opened (the PR sat at
`mergeStateStatus: BEHIND` and was correctly flagged as missing #362 by
independent review, `zali`, on PR #363 — see that PR's review-evidence).
Re-fetched again, rebased this branch onto current main (`f192ab7`, clean,
no conflicts), and extended the re-verify/arc coverage through #362 below.
`venu`/`zali`/`bane`'s lane remains not this pass's to manage or redirect —
only re-verified as merged-and-landed content, same as any other PR in the
arc.

Not this pass's concern beyond the re-verify above: #341 (protocol
effectiveness benchmark, blocked on its own design gate) — confirmed
untouched.

## 1. Re-verify reality

**PR #350 (AGENTS.md isolated-worktree convention, `IDEA-20615e4d`).**
Verified live at this pass's `HEAD`: `AGENTS.md` line 141 reads "dispatch
workers into isolated worktrees/clones, never the shared checkout
([Worktree Isolation](playbook/WORKTREE_ISOLATION.md))". Real, not
hand-waved — see Emergence section below for the correction this required
to the idea record's own history.

**PR #352 (standing merge authorization).** Already covered by check #30's
handoff context; unchanged this arc. `scripts/opcmd_merge.py` still requires
`mergeStateStatus=CLEAN` + independent APPROVE + CI-green; no further change
to it this arc.

**PRs #353/#354 (reset desk log, session43 handoff receipt fix).** Both
docs/process files, no `runtime/` or checklist touch. Confirmed
`work/coordination/RESET_DESK_LOG.md` and the session43 register row both
exist as claimed.

**PRs #355/#356 (6.22 WITHHOLD/DENY fixture (b)).** Re-read the merged
checklist row text (`work/roadmaps/CAPABILITY_CHECKLIST.md` §7, row 6.22)
directly rather than trusting the PR body: it now documents a real promoted
`REVIEWED_GUIDANCE` lesson (demoted to `WITHHOLD` by a past `review_at`)
carried through a real `maps run send-context --deliver-context` call,
`MemoryProvenanceGuard`'s per-item loop running non-vacuously for the first
time, correctly taking the `WITHHOLD`+`embedded=false` referenced-only
branch, and the claim text grepped absent from the delivered payload (zero
matches). Row correctly stays `IN PROGRESS`: the note's own stated residual
(`WITHHOLD_EMBEDDED`, `WITHHOLD_EMBEDDING_UNDECLARED`, and guard-level `DENY`
remain structurally unreachable through the real assembler) is not
overclaimed away. No status flip needed.

**PR #357 (THINK/PLAN/Prime cross-project tracking).** Visibility-only per
its own stated operator scope decision — confirmed §8 of
`CAPABILITY_CHECKLIST.md` exists and does not create new fleet-dispatchable
rows or authority. No action needed from this pass.

**PR #358 (handoff-register drift mechanical safeguard) — exercised for
real by this very pass.** `scripts/check_handoff_receipts.py` (CI-wired)
covers only `work/handoffs/*.md` (in-repo). The playbook's new
"Handoff-register reconciliation" step names the trajectory check as the
reconciliation owner for the outside-repo `/home/home/MAPS_Lean_Handoff_*.md`
files specifically because CI structurally cannot see them. Running that
step this pass (see §"Handoff-register reconciliation" below) found exactly
the kind of drift the safeguard predicts and fixed it — this is the
safeguard working as designed on its very next pass, not a new failure of
it.

**PR #359 (pre-dispatch roadmap-row freshness check).** 3rd occurrence of
`feedback_dispatched_already_merged_work.md`'s pattern (6.22 work
re-dispatched citing a stale note after PR #355/#356 had already done it,
caught by the worker before duplicate work happened). Verified the diff
adds only `scripts/check_dispatch_freshness.py` + its test — no
`CAPABILITY_CHECKLIST.md` or `runtime/` touch. Did not independently
re-derive the script's own test pass/fail here (out of this pass's bounded
scope, and CI already gates it); confirmed only that it exists and is
scoped as claimed.

**PRs #360/#361/#362 (6.4 guard-work lane, landed mid-pass — all three
now).** Re-verified directly against the rebased checklist row rather than
the PR bodies:
`runtime/policy/write_scope_guard.py::WriteScopeGuard` now exists
(caller-declared, fail-closed, same shape as the destructive/external
guard), composed into `build_canonical_harness_service`
(`HookEnforcement.WRITE_SCOPE` / `HookEvent.BEFORE_WRITE`) — but the row's
own text is explicit that `BEFORE_WRITE` has zero firing call sites
anywhere in `runtime/` (this harness mediates only
`start`/`send`/`resume`/`stop`, never an in-session file write), so the
guard is composed-but-genuinely-inert, not yet production-exposed the way
the destructive-action guard eventually was. Credential guard: explicitly
declined as premature (no credential concept exists in the task/policy
schema yet, SEC6's own gate for a credential broker is unmet). The
capability-declaration-manifest phrase in the row's original text is named
as a false lead (it refers to the distinct, already-shipped SEC4/6.10
Skill-manifest system, not 6.4-specific unbuilt work) — a real correction to
a long-standing row misreading, not new work. #361 explicitly scopes (does
not yet wire) `verify_git_run` as the well-grounded template for actually
closing the write gap, deliberately deferring the DENY-capable wiring
decision as bigger than its own slice. **#362** (coordinator-decided
follow-on to #361's fork B) adds `write_scope_binding_required` (opt-in,
default `0`) to `run_manifests`, threaded through
`TaskStore.create_run_manifest`, `flow_start()`, and both CLI surfaces —
mirroring the existing `require_worktree_binding` pattern exactly. Schema +
API only, explicitly no guard yet; confirmed via `git diff` against its
merge commit that it does **not** touch `CAPABILITY_CHECKLIST.md` at all
(no row text, no bucket). Row **correctly stays IN PROGRESS** across all
three PRs — re-verified from the diffs and row text directly, not taken on
the PRs' own say-so. Not this pass's lane to act further on; #362 is the
last PR of this lane as of this pass (`gh pr list --state open` shows no
further #36x).

**Direct-to-`main` push alert, 3rd/4th firing.** `08fd074` and `41277b5`
("docs: refresh Development status" for 2026-09-13 and 2026-09-14) both
triggered `direct-push-alert` as `failure` — confirmed via `gh run list
--workflow direct-push-alert.yml`. Both are authored by the operator's own
git identity (`BigCat Mellow`), not an agent, and touch only status-doc
prose (no checklist/`runtime/`/merge-ledger content). This is the alert
(PR #348, resolved at check #30) firing exactly as designed — a loud,
non-blocking, post-hoc surface, explicitly not a merge gate since branch
protection is admin-bypassable. Not a new incident; no action needed.

**Scoreboard re-derivation.** Direct count of `CAPABILITY_CHECKLIST.md` §7
6.x rows (row number + status column extracted and paired programmatically,
all 35 rows counted, not sampled), **re-run a third time after the #362
rebase, not from either earlier clone**: **19 DONE / 10 IN PROGRESS (9 + 6.33
"evaluation-only, by design") / 6 NOT STARTED.** Unchanged from check #30 —
#360/#361/#362 expanded 6.4's evidence text but did not flip its bucket.
6.4 and 6.22 remain the two live IN PROGRESS rows with open fleet work
against them (6.4: no further open PR in the lane as of this pass — `gh pr
list --state open` confirmed only #363 itself and the unrelated #341; 6.22:
fixture (b) landed this arc, residual gaps stand as stated above).

**`python3 -m runtime.smoke`**: exit 0, `ok: true`.

**Full test suite**: run in the foreground exactly once, per checks #29/#30's
explicit warning against stacking retries after a prior host-OOM incident.
Confirmed no other test process running first (`pgrep -af "unittest
discover"` / `pytest` both clean). The harness auto-moved the same single
attempt to background after its 10-minute foreground-call cap (not a second
invocation, not polled with `sleep` — waited for the harness's own
completion notification). **Result: UNKNOWN.** The single attempt was
itself killed by the harness ~1013 lines / ~4 test modules from the end
(reached `test_frozen_regression_case`, alphabetically near the tail of the
suite, all `ok` up to that point, zero failures observed) with "system is
running low on memory" — this pass confirmed the host was clean of any
*self-caused* concurrency beforehand, so this looks like host-wide pressure
from other concurrent agent activity (plausibly the active 6.4 lane's own
CI runs), not a repeat of check #29's self-inflicted triple-launch. Per
this pass's own dispatch instructions and check #29/#30's precedent: not
retried, recorded as UNKNOWN, deferred to CI (`test` status check already
required on every PR, including this one). Detail logged to
`feedback_concurrent_test_suite_oom.md` (session memory) for the next pass.

## 2. Handoff-register reconciliation

`ls -1 /home/home/MAPS_Lean_Handoff_*.md | sort -V | tail -8` — one file
written since check #30 (2026-09-13): `MAPS_Lean_Handoff_2026-09-15-session-
bobo-plan-calibration.md`. It carries the required receipt block (`Handoff
ID: MAPS-HO-20260915-session-bobo-plan-calibration`, `status: OPEN`,
`Reviewed: NOT YET`, `Continued at: NOT YET`) but had **no matching row** in
`work/handoffs/README.md` — exactly the drift class PR #358 exists to catch
for outside-repo files. **Fixed this pass**: added the register row
(`OPEN`, `Reviewed: NOT YET`, `Continued at: NOT YET`, matching the
handoff's own receipt — this pass does not itself claim to have reviewed or
continued that handoff, only to have registered its existence).

## 3. Emergence pass

**Imagine.** No new `work/insights/`/`work/ideas/` records filed this pass.
This arc was process/infrastructure work (handoff registration, reset desk,
cross-project tracking, a 6.22 fixture, two mechanical safeguards) with
outcomes already well-understood at merge time; recorded as a valid "zero
new records" outcome per `EMERGENCE.md` Phase 1 — this pass did find real
content in the sweep below, so this is not a "found nothing, arc after arc"
pattern (Tenth Seat §7 first bullet does not apply).

**Sweep — disposition for the two items check #30 explicitly carried
forward:**

| Record | Disposition this pass | Rationale |
|---|---|---|
| `IDEA-20615e4d` (isolated worktrees) | **closed (verified)** | PR #350 confirmed live at `HEAD` (`AGENTS.md` line 141). This also required a correction: the record's own 2026-09-03 disposition had prematurely claimed "AGENTS.md carries the worktree convention" when it didn't yet (check #30 caught the gap with a live `grep`); appended a 2026-09-15 disposition to the record correcting that history and confirming the real closure. No further sweep attention needed. |
| `INSIGHT-2b8b9a4b` (mergedBy self-merge-detection no-op) | **promote** | 3rd consecutive incubate pass (checks #29, #30, #31) — ran the record's own "smallest next test" rather than leaving it a 4th time. `gh api repos/BigCatMellow/MAPS_Lean/branches/main/protection` (live, this pass's `HEAD`) shows `required_approving_review_count: 0` and `require_last_push_approval: false`. GitHub's native "require approval of the most recent reviewable push" is available and unset; enabling it (+ ≥1 required approval) would make PR #345's failure class mechanically unrepresentable at the platform level, independent of the shared `gh` CLI identity. This is a GitHub branch-protection settings change, not a code change — recommended, not applied. Named in Operator-section. |

Full `work/insights/`/`work/ideas/` backlog (20 records total, `ls -1
work/insights/ work/ideas/` counted directly) was swept line-by-line at
check #29 (2026-09-12); no PR in this arc touched either directory besides
this pass's own two edits above (`git log --oneline b60b81d..HEAD --
work/insights/ work/ideas/` = empty), so no new evidence accumulated for the
other 18 records this arc. Re-sweep deferred to the next pass with material
new evidence, same approach check #30 took.

No other record crossed an N=3 incubate-without-movement bound this pass.

## 4. Friction-log consumption

```
python3 tools/triage_status.py --root .
FRICTION_LOG: 16 entries - 7 closed, 9 open (0 unresolved).
Nothing open. The triage loop is current.
```

Same counts as check #30 — no new friction-log entries filed this arc
(PR #359's 3rd-occurrence incident was fixed directly with a mechanical
countermeasure in the same PR per rule 20, rather than logged as a separate
open friction entry awaiting one).

## 5. Trajectory action

**CONTINUE.** This arc landed one real capability advance (6.22 fixture
(b), non-vacuous WITHHOLD exercise), the full 6.4 write-scope lane (#360's
guard, #361's scoping-only follow-on, #362's opt-in flag), two mechanical
rule-20 safeguards (handoff-register drift, dispatch-freshness), and
process/infra work (standing merge authorization exercised without
incident, reset desk, cross-project visibility tracking). Nothing changes
roadmap scope, priority, or route to DONE. No PR in this lane remains open
as of this pass.

## 6. Tenth Seat Review §7 check

This pass found real content (a corrected/closed Emergence record, a
promoted recommendation with fresh evidence, a caught-and-fixed
handoff-register drift) — not a rubber-stamp "nothing to report" pass.
Trigger 2 does not apply. No minority report required.

## Operator-section

Nothing crossed an N=3 auto-escalation bound in the friction log. One
Emergence item did:

- `INSIGHT-2b8b9a4b` — 3rd consecutive incubate pass, now **promoted** with
  concrete evidence (above): main's branch protection currently has
  `required_approving_review_count: 0` and `require_last_push_approval:
  false`. Recommend enabling both (≥1 required approval + require-approval-
  of-most-recent-push) to make reviewer self-merge mechanically
  unrepresentable, closing the gap PR #345 exposed. This is a GitHub repo
  settings change — an operator/coordinator decision, not applied by this
  pass.

## Resume prompt

You are running roadmap trajectory check #32 for MAPS_Lean. Independent
author lane — no prior involvement in whatever merged since this check's own
squash commit. Follow `playbook/ROADMAP_TRAJECTORY_CHECK.md` (5-step +
friction-log consumption + handoff-register reconciliation + Emergence pass)
and `playbook/TENTH_SEAT_REVIEW.md` §7. Fresh clone to a UNIQUE path (never
`~/Projects/MAPS_Lean`, `.claude/worktrees/`, or `.maps/` for writes); verify
`git rev-parse origin/main` == `HEAD`, `git status --porcelain` empty. Run
the full test suite in the foreground exactly **once** — if a single attempt
doesn't finish (the harness may auto-move a long-running foreground call to
background after its own 10-minute cap; that is not a second invocation and
does not need to be avoided), wait for its completion notification rather
than polling with `sleep`; if it errors out entirely, record UNKNOWN and
defer to CI rather than retrying.

Anchor: the squash commit of check #31's own PR (find with `git log
--oneline --grep='Roadmap trajectory check' main | head -1`). Enumerate
`git log --oneline <anchor>..HEAD`, check every PR — do not hand-list.

Carried to #32 explicitly:
1. `INSIGHT-2b8b9a4b` — now at **promote** disposition (this pass, #31);
   check whether the operator/coordinator acted on the branch-protection
   recommendation (`required_approving_review_count` / `require_last_push_
   approval`) or it's still pending.
2. Handoff-register reconciliation — run
   `ls -1 /home/home/MAPS_Lean_Handoff_*.md | sort -V | tail -5` and check
   only files written since this check; confirm each carries a receipt and
   a matching `work/handoffs/README.md` row.
3. Re-derive the scoreboard from `CAPABILITY_CHECKLIST.md` §7 by direct
   count — expect 19/10/6 unless something moved (6.4's write-scope lane —
   #360/#361/#362 — is fully landed as of this pass with no row flip; check
   whether a follow-on PR wiring `BEFORE_WRITE`'s firing call site or the
   `verify_git_run` template #361 named has appeared).
4. Also watch for the same mid-pass-refetch situation this pass hit twice:
   if any lane lands a PR while you're mid-run (even after your own PR is
   open — this happened here after independent review caught it), re-fetch,
   rebase/fast-forward, and re-derive rather than trusting a stale clone or
   an already-open PR's content (see this note's own "Mid-pass re-fetch
   note" above for the mechanics that worked both times).

DELIVERABLE: one PR, branch off `main`, titled `Roadmap trajectory check #32
(<anchor>..HEAD — PRs <list>) (#<PR>)`, adding
`work/notes/<date>-roadmap-trajectory-check-32.md` in the same PR. Update
`CAPABILITY_CHECKLIST.md` ONLY if a status genuinely moved — flag the
coordinator first. You do NOT self-review, self-approve, or merge.
