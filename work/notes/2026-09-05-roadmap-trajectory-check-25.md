# Roadmap trajectory check #25 — 2026-09-05

Twenty-fifth pass. Independent analysis lane (`traj25-saki`, dispatched by
coordinator `viva`). Method per `playbook/ROADMAP_TRAJECTORY_CHECK.md` (5-step
+ friction-log consumption + Emergence pass) and `playbook/TENTH_SEAT_REVIEW.md`
§7.

**Trajectory action: `CONTINUE`.** No roadmap/status claim is wrong in a way
that changes the route to DONE. Scoreboard moved this arc: **18 / 11 / 6**
(was 17/12/6), re-derived by direct count — a real, earned flip (6.5), not a
carried-forward error.

## Setup / base verification

- Fresh clone (`/tmp/traj25-work`, distinct from the coordinator checkout at
  `~/Projects/MAPS_Lean`, never touched for writes). `git rev-parse
  origin/main` == `HEAD` == **`c958cf6ba099edf2363e0d66b40f10c2c1174425`**.
  `git status --porcelain` empty.
- Anchor: `git log --oneline --grep='Roadmap trajectory check' main | head -1`
  → `777c612` ("Roadmap trajectory check #24 … (#296)").
- Arc `git log --oneline 777c612..HEAD` = exactly **3 PRs, merge order #297,
  #294, #298** — matches the dispatch brief.

## 0. Situational awareness

- `python3 -m runtime.smoke` → **exit 0**.
- `python3 -m unittest tests.test_exp_b_skill_routing` → **3 OK**,
  `corpus_sha256` `2cff0e40…4565` (frozen), `selection_f1` 0.8667,
  `exact_cases` 19/25, `false_activation_cases` **0**. 6.9/S6 DONE not
  regressed — no status-truth emergency.
- `tests.test_documentation_sprawl`, `tests.test_check_review_evidence`,
  `tests.test_frozen_regression_case(_taxonomy)` → 50 OK (targeted re-run of
  the modules this arc's PRs touch, foreground, not backgrounded).
- Full suite delegated to CI's `test` check.

## 1. Re-verify reality (arc = #297, #294, #298)

| PR | What it did | Verified |
|---|---|---|
| **#297** (`092e451`) | Zero-diff revalidation review tier: `check_review_evidence.py` now accepts a stale `head_sha` when it is an ancestor of the resolved head with an *empty* diff between them (pure-rebase re-bind), teaching the checker the pattern that forced full re-reviews on every rebase (`IDEA-582cc671`/`IDEA-968eb261`, both flagged "promote" at #24). | `git show --stat`: 4 files, +185. Re-ran `tests.test_check_review_evidence` here → OK (61 new lines of test in the PR itself, all pass). Read the diff to `MODEL_CAPABILITY_ROUTING.md` — additive only, exact-match and merge-commit walk-back paths untouched. Independent review evidence (`pr-297-review-evidence.md`) records adversarial bypass attempts (mode-only-change, unrelated-branch identical-tree, walk-back tamper) that were tried and rejected — a real adversarial pass, not a rubber-stamp. **This PR's own mechanism is what let #298 (below) survive a same-arc rebase without a second full review — directly load-bearing this pass.** |
| **#294** (`67450d9`) | Lands the operator's 2026-09-04 decision: `AGENTS.md` "Merge authority" now names `scripts/opcmd_merge.py` as **mandatory**, not optional — a coordinator/seat self-claim is never sufficient, only an operator hcom authorization (per-PR or explicit batch-designation) merges. Also raises `AGENTS_BYTE_BUDGET` 11,200→13,000 to fit the operator-approved wording. | `git show --stat`: 3 files, +101/-5 (AGENTS.md +20/-5, test threshold bump, review evidence). Read the new §"Merge authority" text in full against `work/notes/2026-09-04-merge-auth-mechanical-backstop-design.md` §6 item 3 — wording matches the design note's own recommendation, not a paraphrase. Confirmed this PR was **DRAFT as of check #24**, now merged — this is the fact #24's operator-section item 1 asked #25 to check. Independent review evidence (`pr-294-review-evidence.md`, `lara`) APPROVE. |
| **#298** (`c958cf6`) | DEC-003 option B, attempt 2 (counted): a genuinely-live throwaway hcom session (`zora`, untagged) was bound via `maps run bind-session` to a real `flow start` run manifest, killed to simulate a stall, left unattended past both its lease and the silent-stop `resume_after` window (~900s). The 3rd `recovery-tick --enforce-canonical-run` pass produced a real, routable `resume_denied` (`HOOK_DENIED` / `CanonicalRunGuard` `LEASE_EXPIRED`) — frozen as regression case `CASE-378fb326…4663e5c9`. Flips 4 of the 7-row cluster (**6.5, H5, E4, L6**) to DONE; **6.4, 6.16, 6.22 correctly walked back to IN PROGRESS** after independent review found each has its own distinct, more specific unmet gap (BEFORE_DESTRUCTIVE_ACTION never fired since only `.resume()` was called, not `.stop()`; no `--require-canonical-run` worktree-bound run exercised; `.send()`/`BEFORE_SEND` never called) that a resume-only LEASE_EXPIRED capture does not touch. | Read `work/decisions/DEC-003-harness-enforcement-cluster-exit-criterion.md` Result section in full — `resume_denied` payload and `CanonicalRunGuard` `guard_code="LEASE_EXPIRED"` claim cross-checked against `runtime/recovery/production.py:392-397` (cited lines exist and match). Confirmed regression case file exists (`work/regression-cases/CASE-378fb326d2aceaa0cd3ceeb5ce314f8dba541a234a7331d86e6d31f24663e5c9.json`, 338 lines) and is routed in `work/README.md`'s index (post-fix). Independently re-derived the 7-row split: `grep`-checked the CAPABILITY_CHECKLIST.md rows myself (§2 below) — 6.5/H5/E4/L6 read DONE with the resume_denied evidence cited; 6.4/6.16/6.22 read IN PROGRESS with their gap language intact, matching the review's stated walk-back exactly, not just trusting the commit message. Review evidence (`pr-298-review-evidence.md`, `bona`, independent) caught the unrouted-directory CI-red and the 3-row overclaim pre-merge — a real Phase-1 catch, then correctly re-verified the content-free rebase onto #294/#297 (empty diff confirmed) rather than re-reviewing from scratch, using #297's own new zero-diff path. Two real, unfixed, out-of-scope mechanical bugs are honestly recorded in the results note (`recovery-tick --hcom-dir` silently overriding shell `HCOM_DIR`; a tag-prefix/bare-name mismatch stranding `run_id: null` for tagged agents) — not swept under the win. |

All three PRs independently reviewed (`lara` on #294, an independent reviewer
on #297, `bona` on #298) — no reviewer repeated, no self-review, no author
reviewing their own PR.

## 2. What changed (name it)

- **The 7-row harness-enforcement cluster is no longer a single unit**: 4 rows
  (6.5, H5, E4, L6) are genuinely DONE on real evidence — the first live,
  routable `resume_denied` this cluster has ever produced, after 13+ trajectory
  passes (#8 onward) of "one step away" framing. 3 rows (6.4, 6.16, 6.22) stay
  IN PROGRESS, each now with a *sharper*, more specific stated gap (a
  different guard/hook path that this exercise's shape — resume-only,
  lease-expiry — structurally cannot exercise). This is real progress, not a
  relabeling: confirmed by direct re-read of both the Result section and the
  post-walk-back checklist text, not the PR title alone.
- **Scoreboard moved 17/12/6 → 18/11/6**, re-derived by direct `awk`-count of
  the §7 6.x table's Status column (35 rows total, unchanged set) — only
  `6.5` is inside that specific 35-row table; H5/E4/L6 are separate IDs
  outside it and were already counted DONE elsewhere in the doc. This is the
  first scoreboard movement since #21 (4 consecutive unchanged passes before
  this one). **Flagging to the coordinator per the dispatch brief's
  instruction (e)** — this is a real flip already landed in the merged #298,
  not an edit I am making; recording it accurately here.
- **DEC-003 is functionally resolved**: `Status: ADOPTED` in the doc header is
  now stale prose (the Result section reads as a completed exercise, attempt
  2 of a 2-attempt budget, succeeded on the first counted try — the
  2026-09-04 OAuth-wall episode was a precondition failure, not counted).
  Not editing the doc's own `Status:` line myself (outside this pass's
  narrow edit boundary — flagging for whoever holds write access to the
  decisions/ directory, same pattern as #24's flag on the 2026-08-18 record).
- **The merge-authority mechanical gate is now live and *observed working on
  a real merge*** — see §3.1. This is the single largest finding this pass:
  the entry that has been UNVERIFIED across 4 straight passes (#21-#24) now
  has a concrete, dated, mechanically-produced observation.

No `runtime/` behavior change this arc — #297 and #294 are process/tooling
and doc-authority changes; #298's only `runtime/` interaction was *invoking*
existing recovery-tick machinery against a real session, not modifying it.

## 3. Friction-log consumption (mandatory)

Walked `work/coordination/FRICTION_LOG.md` in full + ran
`python3 tools/triage_status.py --root .`:

```
FRICTION_LOG: 15 entries - 6 closed, 9 open (1 unresolved).

## OVERDUE - operator-escalation candidates (>= 3 passes or past --stale-days)
- coordinator merge marks treated as merge authorization (recurrence) (opened 2026-09-03, 3 passes seen)

## Drift+ repair records missing a countermeasure or regression case
- work/notes/2026-08-18-stalled-dispatched-worker-repair.md (severity DRIFT)
```

### 3.1 `coordinator merge marks treated as merge authorization` — CLOSED this pass

This entry has carried UNVERIFIED across #21/#22/#23/#24 (N=3 auto-escalated
at #23, carried as a status-update at #24 once the operator's partial answer
surfaced). This pass found the concrete live observation the entry has been
waiting for:

- **`#294` merged** (confirmed §1) — the mandatory-path decision is now in
  `AGENTS.md`, not just answered outside hcom.
- **A real gate-refusal/enforcement observation exists.** The coordinator
  checkout's git-ignored `work/coordination/merge-ledger.jsonl` (read-only,
  not committed, checked in place at `~/Projects/MAPS_Lean` — never written
  to) contains exactly one entry:
  ```
  {"authz_excerpt": "You are the merge seat for this session. Merge any PR
  the coordinator marks review-cleared and CI-green.", "authz_from":
  "bigboss", "authz_id": 89280, "caller": "gule", "dry_run": false,
  "head_sha": "92e4d3a1…", "pr": 298, "scope": "batch-designation", "ts":
  "2026-09-05T11:14:38.935537+00:00"}
  ```
  This `ts` is 3 seconds before `#298`'s actual `mergedAt`
  (`2026-09-05T11:14:41Z`, confirmed via `gh pr view 298 --json mergedAt`
  against the coordinator checkout's GitHub remote) — the gate ran, resolved
  a real operator (`bigboss`) authorization naming the merge seat (`gule`)
  for a batch, and only then invoked the merge. `#297` and `#294` predate
  this (`#294` cannot gate its own landing commit; `#297` merged before
  `#294` made the gate mandatory) — so `#298` is correctly the first PR in
  scope for this observation, and it passed.
- Per `REPAIR_AND_LEARNING.md`'s close definition: countermeasure is concrete
  and durable (`scripts/opcmd_merge.py`, mandatory per `AGENTS.md`);
  `verified:` now has a real live-confirmation with date/mechanism (this
  ledger entry); `follow-up` — the exact question the ladder asked ("was
  `gule` observed enforcing the gate") now has a YES answer. **Appending
  `**CLOSED — live gate-refusal-path observation confirmed, PR #298,
  2026-09-05, ledger entry above**` as the final follow-up line in this PR's
  diff** (see `work/coordination/FRICTION_LOG.md`).

### 3.2 Drift+ record `2026-08-18-stalled-dispatched-worker-repair.md` — still open

Unchanged from #23/#24: Prevention §1 gap is discharged in substance by #288
(`scripts/run_tests_sharded.py`), but the record itself still has no pointer
to #288. Outside this pass's edit boundary. Carried forward.

### 3.3 Dispatched-worker-stall entry — no new observed use

`grep -rl "run_tests_sharded" work/notes/ work/reviews/` shows the same
pre-#24 file set (no new hit this arc). No dispatched worker in #297/#294/
#298 used the sharded runner as its primary test invocation. Still "shipped,
first-real-use pending." No status change.

### 3.4 Incubation ladder — `INSIGHT-45727354` / `INSIGHT-68a53a28` — no operator disposition, still open past N=3

Checked both records directly (per the brief, not re-running the audit):
neither carries a dated `## Promotion` disposition line added since #23/#24.
`git diff 777c612..HEAD -- work/insights/ work/ideas/` — **empty**, no
insight/idea file touched this arc. Both stay open, carried to #26.

### 3.5 Behavioral watch entries

- `stale slice-boundary NonGoalTests` — no scope-expanding `_select_skills`/
  `context_builder` slice in this arc (revalidation-tier, doc-authority,
  DEC-003-exercise PRs only). Stays open, no new exposure.
- `fix commit lands on top of review-evidence` — checked commit order in
  both #294 and #298: #294's byte-budget fix landed *before* its evidence
  commit; #298's F1/F2 fixes (`tiki`) landed before the final evidence
  commit, and the later rebase-rebind commit is an explicit, correctly-named
  re-bind (not a silent evidence-goes-stale case) — itself now covered by
  #297's zero-diff acceptance path. No occurrence this arc either way. Stays
  open.

## 4. Emergence pass (mandatory)

### 4.1 Phase 1 — Imagine → Capture

Bounded pass against the #297/#294/#298 arc (a review-tooling addition, a
doc-authority landing, and a decision-closing production exercise — a
"process hardening + a genuine capability closure" arc). **Zero new records
this pass.** The one candidate worth naming — "the merge-ledger file that
just closed a 4-pass-old escalation is git-ignored and lives only in
whichever checkout ran the merge; a trajectory pass that clones fresh
(as this method requires) cannot see it without also reading the
coordinator checkout read-only" — is fully captured as this pass's §3.1
finding rather than a separate `work/insights/` record (no-duplicate-truth):
it is a one-time observation about *this* closure, not a durable structural
gap (the ledger's existence and gitignore status were already a known,
deliberate design choice per the #287/#294 design note, not a new problem).

### 4.2 Sweep — `work/insights/` + `work/ideas/` open records

No file in either directory changed this arc (confirmed §3.4/§3.1). Two
records have a materially stale `## Promotion` line given what actually
happened since they were written — recorded here, not edited (outside this
pass's edit boundary; same posture as #24's flag on the 2026-08-18 record):

| Record | Disposition | Rationale |
|---|---|---|
| `IDEA-582cc671`, `IDEA-968eb261` (zero-diff re-review tier) | **kill — implemented.** `#297` is exactly this idea, merged. `## Promotion` still reads "Not promoted" — stale, should be updated to point at `#297`. | Direct implementation confirmed §1. |
| `INSIGHT-651d8c62`, `INSIGHT-102296b5` (7-row cluster "one step away" / possibly unexercisable) | **kill — resolved.** `DEC-003`'s Result section (§298, confirmed §1/§2) directly answers both: the criterion was exercisable (not structurally blocked) and has now been met for 4 of 7 rows. `## Promotion` still reads "Not promoted" — stale. | DEC-003 Result section, direct read. |
| `INSIGHT-45727354`, `INSIGHT-68a53a28` | **incubate, past N=3, no operator disposition** | See §3.4. Not re-running the audit, carrying forward. |
| All other records (`INSIGHT-29a10ad4`, `-e0b448a6`, `-75785aae`, `-ab696436`, `-a6406800`; `IDEA-20615e4d`, `-bc6cd243`, `-a134ad7c`, `-9e7014fa`) | **unchanged from #24** | No touch this arc; re-litigating would duplicate #24's already-correct dispositions. |

## 5. DEC-003 status — exercise SUCCEEDED, cluster split 4 DONE / 3 IN PROGRESS

`work/decisions/DEC-003-harness-enforcement-cluster-exit-criterion.md`:
header still reads `Status: ADOPTED` but the Result section (added by #298)
records a completed, successful option-B exercise — attempt 2 (counted;
attempt 1 was an OAuth-wall precondition failure, not counted) produced a
real `resume_denied`. 6.5/H5/E4/L6 flip DONE on this evidence; 6.4/6.16/6.22
each have a distinct, more specific unmet gap this exercise's shape does not
reach (see §1/§2) and correctly stay IN PROGRESS. The doc's own `Status:`
field is stale prose relative to its own Result section — flagged, not
edited (outside boundary).

## 6. Tenth Seat / §7 (read before recording)

**Trigger 2 status: ARMED, did NOT fire this pass — did not come close.**
This pass found substantial, verifiable, non-cosmetic things:

- §3.1 closed a 4-pass-old operator-escalation item on a concrete,
  independently-checked artifact (a merge-ledger entry with a timestamp that
  precedes the actual GitHub merge by 3 seconds) — not a restatement of
  "the gate exists," a genuine live-observation confirmation.
- §2 re-derived the scoreboard by direct count and found it had actually
  moved for the first time in 4 passes — a real status change, not a
  carried-forward number.
- §1's cross-check of #298's 4-DONE/3-IN-PROGRESS split against the
  checklist's own row text (not the commit message) independently confirmed
  the walk-back was faithful to the review's stated reasoning.

**Trigger 1 check (status-flipping PR approved with zero findings):** #298
flipped 7 (net 4) checklist rows to DONE and was reviewed by an independent
reviewer (`bona`) who found and required fixes for 2 real defects (unrouted
directory, 3-row overclaim) before approving — Trigger 1 does not apply
(findings were non-zero, and substantive).

§7 "signs this has gone wrong" checked against this pass: none present — this
report is not written after the fact to paper over a shallow pass (the
merge-ledger closure and the scoreboard re-derivation were both concrete,
checkable-by-anyone findings); this lane (`traj25-saki`) is a fresh dispatch,
no repeat-role pattern; nothing here closes a report on weak evidence — §3.1
closes only with a dated, quoted artifact.

## 7. Operator-decision / escalation items

1. **None newly required.** The one item that was UNVERIFIED across 4 passes
   (merge-marks entry) is now CLOSED with evidence (§3.1) — no operator
   action needed on it.
2. **`INSIGHT-45727354` / `INSIGHT-68a53a28`** — both past N=3 incubation
   (escalated at #23), still no operator disposition. Carried forward again.
3. **`work/notes/2026-08-18-stalled-dispatched-worker-repair.md`** — still
   missing its 1-line pointer to PR #288 (out of this pass's edit boundary).
4. **Stale `## Promotion` lines** on `IDEA-582cc671`, `IDEA-968eb261`,
   `INSIGHT-651d8c62`, `INSIGHT-102296b5` (§4.2) and `DEC-003`'s stale
   `Status: ADOPTED` header (§5) — cosmetic/bookkeeping, not blocking, flagged
   for whoever next holds write access to those directories.

Nothing here requires operator action *before work continues* — CONTINUE
stands.

## 8. Recorded for the next pass (check #26)

- **Arc anchor for #26**: the squash commit of *this* PR (#25).
- `python3 -m runtime.smoke` exit 0; EXP-B 3 OK, f1 0.8667,
  `false_activation_cases` 0 — a regression here is a status-truth emergency.
- **Scoreboard 18/11/6** — first movement since #21 (6.5 flipped). Re-derive
  from the §7 6.x table's Status column directly before recording; flag the
  coordinator before any further flip.
- **7-row cluster is now split**: 6.5/H5/E4/L6 DONE (closed); 6.4/6.16/6.22
  IN PROGRESS with sharper, distinct stated gaps (`.stop()`/
  `BEFORE_DESTRUCTIVE_ACTION`; `--require-canonical-run` worktree-bound run;
  `.send()`/`BEFORE_SEND`). #26 should not re-litigate the 4 closed rows;
  watch for movement on the remaining 3.
- **Merge-marks entry CLOSED** (§3.1) — #26 does not need to re-check it
  unless a new coordinator-mark-only merge is observed, which would open a
  fresh entry per the close definition, not reopen this one.
- **Stale `## Promotion`/`Status:` bookkeeping** (§4.2/§5) — cosmetic, low
  priority, still open for whoever has write access.
- **`INSIGHT-45727354` / `INSIGHT-68a53a28`** — still no operator
  disposition as of #25 either. Don't re-run the audit — just check.
- **FRICTION_LOG bookkeeping**: this pass appended its own dated CLOSED line
  in the same PR that records the disposition — keep doing that.

## Resume prompt

You are running roadmap trajectory check #26 for MAPS_Lean. Independent
analysis lane. Follow `playbook/ROADMAP_TRAJECTORY_CHECK.md` (5-step +
friction-log consumption + Emergence pass) and `playbook/TENTH_SEAT_REVIEW.md`
§7 (read before recording any clean result). Fresh clone to a UNIQUE path
(`git clone https://github.com/BigCatMellow/MAPS_Lean /tmp/traj26-$$/`); verify
`git rev-parse origin/main` == `HEAD`, `git status --porcelain` empty. NEVER
touch `~/Projects/MAPS_Lean`, `.claude/worktrees/`, or `.maps/` for writes
(read-only checks against the coordinator checkout, e.g. a git-ignored ledger
file, are fine and were useful this pass — see §3.1). Do NOT run `maps
recovery-tick` or any `--enforce-*` pass, and do NOT spawn a real hcom
session, unless explicitly authorized.

Anchor: `git log --oneline --grep='Roadmap trajectory check' main | head -1` ->
the check-#25 squash; then `git log --oneline <that>..HEAD`, check every line.

Method (rule 14): no claim from a PR title/body/review summary alone;
re-verify against `git show`, merged code, `/usr/bin/grep`, targeted
`unittest` modules foreground. `python3 -m runtime.smoke` must exit 0.
`tests.test_exp_b_skill_routing` must stay 3 OK, f1 0.8667,
`false_activation_cases` 0. Full suite is CI's — do NOT background-and-wait
on it, do NOT put a Monitor on a test run, do NOT loop `kill -0 <pid>; sleep`.

Context from #25: arc #297/#294/#298 landed the zero-diff revalidation tier,
the mandatory merge-authority gate, and DEC-003's successful real-stall
exercise. Scoreboard moved **17/12/6 → 18/11/6** (first movement since #21).
The 7-row cluster split: 6.5/H5/E4/L6 DONE, 6.4/6.16/6.22 IN PROGRESS on
sharper distinct gaps. The 4-pass merge-marks escalation CLOSED on a real
live-observation (merge-ledger entry for PR #298, operator `bigboss`
batch-designating `gule`, timestamped 3s before the actual GitHub merge).
Trigger 2 ARMED, did NOT fire (this pass had plenty to engage with).

Specifically check at #26: (a) did any further movement happen on 6.4/6.16/
6.22 (a `.stop()`/`BEFORE_DESTRUCTIVE_ACTION` exercise, a
`--require-canonical-run` worktree-bound run, or a `.send()`/`BEFORE_SEND`
exercise)? (b) is the merge-ledger gate still being observed on every merge
since #298 (spot-check 1-2 more ledger entries if the coordinator checkout is
reachable read-only), or did a bare `gh pr merge` slip through (a NEW friction
entry, not a reopen of the closed one)? (c) did `scripts/run_tests_sharded.py`
see its first real dispatched-worker use? (d) `INSIGHT-45727354` /
`INSIGHT-68a53a28` — operator disposition yet (do not re-run the audit, just
check)? (e) re-derive the scoreboard from `CAPABILITY_CHECKLIST.md` §7 by
direct count of the 6.x table's Status column — expect 18/11/6 unless one of
6.4/6.16/6.22 moved; flag the coordinator before any further flip. (f)
Trigger 2: a genuinely-clean #26 FIRES it — flag the coordinator BEFORE
recording a clean result or dispatching a Tenth-Seat sub-agent, then write
`work/reviews/trajectory-26-minority-report.md`.

DELIVERABLE: one PR, branch `analysis/roadmap-trajectory-check-26`, adding
`work/notes/2026-09-<DD>-roadmap-trajectory-check-26.md` (+ any `FRICTION_LOG`
follow-up lines — append them in this PR, do not just describe them in prose
— + emergence sweep dispositions + minority report iff Trigger 2 fires).
Update `CAPABILITY_CHECKLIST.md` ONLY if a status genuinely moved (hard
evidence) — flag the coordinator first. Author email
`201203536+BigCatMellow@users.noreply.github.com`. Commit trailer
`Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>`. TWO-PHASE REVIEW: do
NOT push your own review evidence, do NOT spawn your own reviewer; when the PR
is open and CI `test` is green, report the PR number + full head SHA to the
coordinator via hcom (prefix every message with your name), then stand by for
review findings.
