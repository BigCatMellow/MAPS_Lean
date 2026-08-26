# Roadmap trajectory check #8 — arc: PRs #164-#175

Eighth pass. Pass #7 (`work/notes/2026-08-24-roadmap-trajectory-check-7.md`,
merged via PR #163) covered PRs #157-#162 at `origin/main` `ee5e364`. This pass
covers everything merged since, at `origin/main` `6c87d18` (PR #175): **#164**
(SEC3 `DestructiveExternalActionGuard`, unwired), **#165** (RnS recovery-tick
production trigger), **#166** (memory-trust gate design), **#167** (SEC4
skill-lifecycle persistence design), **#168** (RnS validation-tier hook-in
design), **#169** (`playbook/TENTH_SEAT_REVIEW.md`), **#170** (memory-trust gate
impl), **#171** (SEC4 persistence impl, Half 1), **#172** (validation-tier
hook-in impl, advisory), **#175** (6.16/E6 worktree-binding seam design).

This is the first pass to run since `TENTH_SEAT_REVIEW.md` landed. Its §7
warning-sign check and its Trigger 2 tripwire are both evaluated in §6 below.

## 0. Situational awareness

- `python3 -m runtime.smoke` passes clean at `6c87d18`.
- `origin/main` moved during this pass (#175 merged mid-analysis); the branch
  was reset onto `6c87d18` and every claim below re-verified at that head, not
  carried over from the earlier read.
- Verification method: `git show --stat` / `gh pr view --json files` per PR plus
  direct `grep` over `runtime/` excluding `tests/`. No claim below is taken from
  a PR title, a PR body, or a review-evidence file's own summary.

## 1. Re-verification of pass #7's named items

### 1a. Was PR #164 an accurate closure of SEC3's design? — Partially: design
implemented, capability deliberately not delivered. Row correct.

`runtime/policy/destructive_action_guard.py` exists with
`DestructiveExternalActionGuard` + `register_destructive_external_action_guards`,
and `HookEnforcement.DESTRUCTIVE_EXTERNAL_ACTION` exists in
`runtime/harness/hooks.py`. **Confirmed unwired**: `grep -rn
"DestructiveExternalActionGuard\|DESTRUCTIVE_EXTERNAL_ACTION\|register_destructive"`
outside `tests/` returns only the definition module and its `runtime/policy/
__init__.py` re-export. The guard's own docstring says so ("No production code
path calls this today"), and `tests/test_destructive_external_action_guard.py`
carries a source guard asserting it. **6.4/SEC3 correctly remains `IN
PROGRESS`** — no change needed.

### 1b. Did PR #165 actually close the "zero production invocation" gap? — Yes
for `tick()`; no for the harness routing that gap was supposed to unlock.

`runtime/recovery/production.py:382` constructs a `RecoverySupervisor` and line
394 calls `.tick()`, reachable two ways from `runtime/cli.py`: the new
`recovery-tick` subcommand (line 382-390) and an opportunistic piggyback on
`maps claim` (line 376). Pass #7's grep (`RecoverySupervisor(\|\.tick(` outside
`tests/` → empty) now returns real production hits. **The headline gap is
genuinely closed.**

But the closure is narrower than "RnS now runs through the harness". That
production constructor **deliberately passes `harness_service=None`**
(`runtime/recovery/production.py:391`, "environment_reader/harness_service
deliberately omitted"), so the `HarnessService.resume()` routing PR #160 built —
the whole point of the H5/6.5 arc — is *still* exercised only by
`tests/test_recovery_supervisor.py`. Every production resume takes the fallback
direct `HcomAdapter.resume()` path. The checklist's H5 row still asserted the
opposite half of this ("`tick()` itself has no production trigger loop") and did
not record the new, sharper half. **Corrected this pass** (see §2).

### 1c. Are #166/#167/#168's designs faithfully implemented in #170/#171/#172?

- **#166 → #170 (memory trust gate, 6.22): faithful, correctly scoped.**
  `runtime/policy/memory_trust_gate.py::admit_memory_evidence()` exists and is
  the single decision point in `runtime/context_builder.py` (lines 238, 359) —
  bucket membership and `budget_class` are its outputs, not parallel
  derivations, exactly as designed. 6.22 stays `IN PROGRESS` and its "Still
  missing" clause was **narrowed, not deleted** — both surviving clauses
  re-verified true: no action/tool-call gate consults `MemoryTrustClass`
  (enforcement reaches the Context Builder plan only), and `SkillTrustState` /
  `SkillLifecycleState` / `operational_learning.py` remain unmigrated separate
  systems of record. **No correction needed** — this is the one row of the three
  that was updated in the same PR as the code.
- **#167 → #171 (SEC4 persistence, 6.10): faithful and correctly Half-1-only,
  but the row was never updated.** Half-2 boundary confirmed clean:
  `gh pr view 171 --json files` shows exactly `runtime/state/schema.sql`,
  `runtime/state/skill_lifecycle_storage.py`, `runtime/state/store.py`, one test
  file, and its review evidence — `context_builder.py`, `skills/catalog.py`, and
  `trust.py` untouched, **no Half-2 leakage**. However, PR #171 shipped **no
  `CAPABILITY_CHECKLIST.md` change**, leaving SEC4 and 6.10 asserting a "pure,
  unpersisted primitive with no durable storage" that the merged code falsifies.
  **Corrected this pass** (§2).
- **#168 → #172 (validation-tier hook-in, 6.5/H4/E4): faithful and correctly
  advisory-only, but the rows were never updated.** `runtime/recovery/
  production.py::RunBoundValidator` really does call `run_validation_tier()`
  against each about-to-be-resumed incident's own declared spec, budget-capped
  per tick, and `runtime/cli.py`'s `--repo-root` (no default, by explicit design
  comment) opts in. The result lands in an advisory `resume_validation` field
  consulted by nothing. PR #172 also shipped **no checklist change**, leaving
  H4, E4 and 6.5 asserting that no production call site invokes validation and
  that hook-in "remains the still-unstarted fast-follow". **Corrected this pass**
  (§2).

### 1d. Targeted re-verification requested for this pass

| Claim under test | Result |
|---|---|
| 6.5/H4/E4 still genuinely `IN PROGRESS`, not implied `DONE` | **Confirmed `IN PROGRESS`** — correct label, but evidence text was stale (§2). |
| `record_run_environment_evidence` still has zero production writers | **Confirmed.** Only `runtime/state/environment.py:44` (the definition) and a docstring mention in `runtime/recovery/production.py:180`; all callers are in `tests/`. |
| 6.4/SEC3 still `IN PROGRESS`, guard unwired | **Confirmed** (§1a). No correction needed. |
| 6.10/SEC4 still `IN PROGRESS`, Half 1 only, no Half-2 leakage | **Confirmed** on scope; **evidence text stale** (§2). |
| 6.22 still `IN PROGRESS` with "Still missing" narrowed not deleted | **Confirmed correct as written.** |
| `playbook/INDEX.md` lists `TENTH_SEAT_REVIEW.md` | **Confirmed** — `playbook/INDEX.md:16`, with a correctly-scoped "not for" clause. |
| Master-roadmap tag citations | **Confirmed** — 6.4 `P1`, 6.5 `P1`, 6.10 `P1/P2`, 6.11 `P2`, 6.16 `TRIGGERED`, 6.22 `P1 design/security invariant`, 6.24 `P1/P2`. No mislabel this pass (cf. passes #4/#6). |

## 2. Scoreboard and corrections

Recounted directly from the current §7 table: **35 rows. DONE 16 / IN PROGRESS
13 / NOT STARTED 6** — identical membership to pass #7 (DONE: 6.1, 6.2, 6.3,
6.6, 6.7, 6.8, 6.13, 6.14, 6.15, 6.18, 6.23, 6.26, 6.27, 6.28, 6.29, 6.30; IN
PROGRESS: 6.4, 6.5, 6.9, 6.10, 6.11, 6.16, 6.19, 6.20, 6.21, 6.22, 6.24, 6.33,
6.35; NOT STARTED: 6.12, 6.17, 6.25, 6.31, 6.32, 6.34).

**No status-label delta.** Every label is correct. But this pass found **six
rows whose evidence text was falsified by merged code** — a different failure
mode from the label drift earlier passes hunted, and the first time this check
has caught it at this scale. Corrected in this PR, with the label deliberately
left unchanged in every case:

1. **H4** — "no production call site invokes it yet" → false since #172.
   Rewritten to name the real call site and separate the three conditions that
   actually keep the exit gate unmet (opt-in, advisory, `quick`-only).
2. **E4** — same, plus a newly-noted residual: PR #106's `make_validation_hook`
   factory is still unused, because no production `HookRegistry` exists at all.
3. **6.5** — "validation-tier command execution itself remains unimplemented" →
   false since #172. Rewritten to "observed rather than enforced".
4. **H5** — "`tick()` itself has no production trigger loop" → false since #165.
   Rewritten, and the surviving half sharpened: the production trigger passes
   `harness_service=None`, so harness routing is still test-only (§1b).
5. **SEC4** — "pure, unpersisted primitive with no durable storage" → false
   since #171. Rewritten to name the store, and to state the genuinely
   remaining gaps (no Half-2 authority, **zero non-test writers**, no CLI).
6. **6.10** — same stale "unpersisted" claim in the master-inventory row.

Plus one asymmetry fix: the **6.16** master-inventory row now carries the
composition-layer finding that the E6 row already recorded (below).

**Common cause of 1-6: three consecutive implementation PRs (#165, #171, #172)
shipped no checklist edit**, against `CAPABILITY_CHECKLIST.md`'s own closing
instruction to "edit this file in the same PR that changes the underlying code,
or as a fast follow docs-only PR immediately after". PR #170 did it correctly.
The checklist did not go wrong by drifting slowly; it went wrong because the
same procedural step was skipped three times in one arc. Worth naming as a
process finding, not just six text fixes.

## 3. What changed the picture

### 3a. One root cause now explains four separate `IN PROGRESS` rows

Independently verified this pass (not taken from PR #175's report, though it
agrees):

```
grep -rn "register_canonical_run_guards\|HarnessService(\|HookRegistry()" --include=*.py . | grep -v "^./tests/"
→ runtime/policy/__init__.py    (re-export)
→ runtime/policy/harness_guard.py:194  (definition)
→ runtime/harness/service.py:27  (HarnessService's own internal default)
```

**Nothing in this repo composes a `HarnessService`, a `HookRegistry`, or a guard
registration outside `tests/`.** The Hook enforcement layer — the mechanism
6.4/SEC3, 6.5/H4/E4, 6.16/E6 and H5 all route through — has no composition root
in production. Consequences, each confirmed above rather than inferred:

- SEC3's guard is unwired (§1a) — and wiring it would have nothing to register
  onto.
- 6.16/E6's designed enforcement seam is `CanonicalRunGuard`
  (`work/notes/2026-08-26-worktree-binding-enforcement-seam-design.md`), which
  is likewise never composed; implementing that follow-up alone would produce a
  guard that never fires.
- H5/6.5's harness-routed resume is bypassed in production by
  `harness_service=None` (§1b).
- E4's Hook-callback validation factory has no registry to attach to.

This is precisely the shape `ROADMAP_TRAJECTORY_CHECK.md` §2.2 names as
plan-changing evidence: "a phase turning out to depend on something bigger than
scoped... discovering zero production callers of a whole subsystem". It is also
structurally the *same* finding as the RnS `tick()` gap that PR #165 just fixed
— the project has now hit the "built, tested, never composed" pattern twice on
different subsystems, which makes it a class of defect rather than an incident.

### 3b. The arc's real pattern: enforcement layers landing inert

#164 (guard, unwired), #171 (store, zero writers), #172 (validation, advisory)
each shipped a correct, well-tested, faithfully-scoped mechanism that **nothing
consults**. That is defensible per-PR — bounded scope is a project value, and
every one of these correctly declined to flip a status row — but four
consecutive inert landings is a trajectory signal, not four independent
choices. The backlog is accumulating mechanisms faster than it is accumulating
call sites, and the checklist staleness in §2 is a downstream symptom: rows
describe capabilities as absent because, functionally, they still are.

### 3c. Not changed

6.19/6.20/6.21's undocumented-trigger discipline gap (flagged pass #6) remains
dormant — no PR this arc touched them. 6.35/D3 still blocked on an operator
target decision; no pilot inferred. 6.17/E7 still correctly gated behind 6.16.
6.25/SEC6 still shows no recorded triggering condition. 6.31-6.34 unchanged.

## 4. Decision: reprioritize (not a pivot)

Per §3a, the highest-value next item is no longer any individual guard,
validator, or store — it is **a production composition root**: one place that
builds a `HookRegistry`, registers the guards that already exist, constructs a
`HarnessService`, and hands it to the flows that already run (`maps flow start`,
`maps recovery-tick`). Every currently-blocked enforcement item is downstream of
it, and none of them can be honestly closed without it.

This reprioritizes *ordering*, not direction: no roadmap item is abandoned, no
new capability number is proposed, and 6.4/6.5/6.16's own scopes are unchanged.
It is a re-ranking justified by this arc's evidence, made under
`ROADMAP_TRAJECTORY_CHECK.md` §2.3, and acted on rather than proposed.

Deliberately *not* proposed: a daemon, scheduler, or always-on service to hold
the composed objects. Master roadmap §7.1/§7.9 reject that, and #165 already
demonstrated the acceptable shape — compose inside an explicitly-invoked,
bounded CLI pass that exits.

## 5. Horizon report

### 5a. Immediately next

1. **Production composition root for the Hook/Harness layer** (serves 6.4, 6.5,
   6.16, H5; `P1` throughout). Design-first, small: name the one or two
   bounded entry points that should compose a `HookRegistry` +
   `register_canonical_run_guards` + `HarnessService`, and what happens on a
   deny. Note `runtime/recovery/production.py` already documents *why* it passes
   `harness_service=None`, so the design must engage that stated reasoning
   rather than reverse it silently. **Ranked #1: it unblocks three other rows
   and is a prerequisite for #175's own follow-up.**
2. **Worktree-binding guard enforcement** (`work/tasks/worktree-binding-guard-
   enforcement.md`, 6.16/E6, `TRIGGERED`). Fully scoped by #175's design. Should
   land *after* or *with* item 1 — on its own it registers a guard onto a
   registry nothing builds.
3. **SEC3 guard first call site** (6.4, `P1`). Same dependency as item 2; #164's
   design already names it as the separate follow-up.
4. **SEC4 Half 2 — real authority wiring** (6.10, `P1/P2`). Independent of items
   1-3 (no Hook layer involved), fully designed in
   `work/notes/2026-08-25-sec4-skill-lifecycle-persistence-design.md`, and the
   store from #171 currently has zero writers — a first real writer plus
   `decided_by` authority resolution is the natural next slice. **Best choice if
   item 1 is deferred or dispatched to someone else.**

### 5b. Next tier

1. **Turn advisory validation into a gate** (6.5/H4/E4). #172's `resume_validation`
   is consulted by nothing; the decision of *who* may let a failed `quick` tier
   block a resume is a real open question its own design note flags. Needs a
   short design, not just an impl.
2. **6.24 — production environment-report source/cache** (`P1/P2`). Unchanged
   this arc; caller-supplied-only remains the state.
3. **6.22 — extend memory-trust enforcement past the Context Builder plan to a
   tool-call gate** (`P1 design/security invariant`). The row's own surviving
   "Still missing" clause.
4. **6.9/S6 — progressive loading of matched Skill bodies.** Unchanged; still
   the one Skill-routing slice that is metadata-only.

### 5c. Correctly gated/blocked — do not re-investigate

Unchanged from pass #7, re-spot-checked: **6.35/D3** (operator target decision),
**6.25/SEC6** (`TRIGGERED`, no recorded trigger), **6.17/E7** (gated on 6.16,
which §3a shows is further from done than it looked), **6.31-6.32/6.33-6.34**
(`EVIDENCE-GATED`/`NOT STARTED` by current roadmap decision), **6.12/S7** (gated
on S6).

## 6. Tenth Seat check (`playbook/TENTH_SEAT_REVIEW.md`)

**Trigger 2 — evaluated, does not fire.** The tripwire was armed: that file
records passes #6 and #7 as each having found something, and explicitly says
"this tripwire is armed for pass #8". The trigger requires this pass to report
**no substantive finding**. It does not: six falsified evidence blocks (§2), a
named process failure (three implementation PRs skipping the checklist step),
and a root-cause finding that re-ranks the horizon (§3a/§4). Trigger 2's
precondition is therefore unmet and no minority report is produced for this
pass. Recording the evaluation rather than the conclusion alone, so the next
pass can see the tripwire was actually checked and not quietly skipped.

**Trigger 1 — not applicable to this pass.** This note is not a review of a
zero-finding status-flipping PR. Note for the record that no PR this arc flipped
a status row to `DONE` at all, so the conjunction could not have arisen.

**§7 warning-sign check (this pass's assigned duty).** `ls work/reviews/ | grep
-i minority` → empty; 90 files, none a minority report. No reports have
accumulated since the convention landed one day ago, so every warning sign
("all GREEN", "same agent keeps drawing the role", "reports accumulate and
nothing ever reopens") is vacuously not-yet-observable. The check costs nothing
and is discharged; the first real evaluation will be pass #9's or later.

**Open item, not fixed here (outside this PR's boundary):**
`playbook/ROADMAP_TRAJECTORY_CHECK.md` still contains **no cross-reference to
`TENTH_SEAT_REVIEW.md`** — the link is one-way (`TENTH_SEAT_REVIEW.md` cites
`ROADMAP_TRAJECTORY_CHECK.md` five times, including assigning it §7's standing
duty). `playbook/INDEX.md` lists both, so neither is unreachable, but a session
following the trajectory-check procedure top-to-bottom would never learn that
Trigger 2 or the §7 duty exists. This pass only found them because its dispatch
said to. That is PR #169's own stated follow-up and remains open; it should be a
one-line addition to §2 or §4 of `ROADMAP_TRAJECTORY_CHECK.md` in a separate
docs PR.

## 7. Honesty check on drift

Every PR this arc traces to an item pass #7 or pass #6 ranked as
next-to-dispatch; #169 is the one exception and was an operator-supplied process
convention, correctly built with no runtime code and no roadmap number. No
speculative capability was added, and the design→bounded-implementation pattern
held across three pairs (#166→#170, #167→#171, #168→#172) with no scope drift in
any of them — verified by file-level diffs, not PR titles.

Two things this pass got wrong to record honestly: it initially analyzed against
`44ab61f` and had to redo the E6/6.16 portion when #175 merged mid-pass; and the
composition-root finding in §3a was surfaced to this pass by PR #175's arc
before being independently verified, so it is confirmed-by-this-pass but not
discovered-by-this-pass. The four-row scope of its consequences (§3a bullets) is
this pass's own.

Evidence weakening this pass's own conclusion, recorded per the project's
standing practice: the §4 reprioritization rests on treating "no production
composition root" as a defect. It is possible the project intends the runtime to
stay a library that an external caller composes, in which case §3a is the
designed state and not a gap. Nothing in `runtime/README.md` or the master
roadmap says so, and `runtime/cli.py`'s existing flows argue against it — but no
document explicitly rules it in either, so item 1 in §5a is deliberately scoped
as *design-first*, and that question is the first thing its design note must
settle.

## Resume prompt

Trajectory check #8 is merged; `CAPABILITY_CHECKLIST.md`'s H4, H5, E4, SEC4,
6.5, 6.10 and 6.16 rows were corrected in it (evidence text falsified by merged
code — no status label changed). Pick up §5a item 1: write a bounded design note
for a **production composition root** that builds a `HookRegistry`, calls
`register_canonical_run_guards()`, constructs a `HarnessService`, and hands it to
the CLI flows that already exist — because `grep -rn
"register_canonical_run_guards\|HarnessService(\|HookRegistry()" --include=*.py .
| grep -v "^./tests/"` currently returns only definitions and re-exports, so
every Hook-based enforcement item (6.4/SEC3, 6.5/H4/E4, 6.16/E6, H5) is blocked
behind it. The design must (a) explicitly settle whether `runtime/` is intended
to be library-only — nothing on record says either way, and that question
invalidates the whole item if answered "yes"; (b) engage, not silently reverse,
`runtime/recovery/production.py`'s documented reason for passing
`harness_service=None`; (c) stay non-daemon per master roadmap §7.1/§7.9,
following PR #165's bounded-CLI-pass precedent. If that item is taken by another
session, SEC4 Half 2 (§5a item 4) is independent of it and fully designed. Also
still open from PR #169: `playbook/ROADMAP_TRAJECTORY_CHECK.md` has no
cross-reference back to `playbook/TENTH_SEAT_REVIEW.md`, so its Trigger 2 and its
§7 standing duty are undiscoverable to a session following the trajectory-check
procedure alone — a one-line docs PR. Standing process finding to enforce next
arc: PRs #165, #171 and #172 each shipped implementation with no
`CAPABILITY_CHECKLIST.md` edit, which is what caused all six stale rows this pass
corrected; require the checklist edit in the implementation PR itself. Run pass
#9 after the next 3-6 merges. Note for pass #9: `TENTH_SEAT_REVIEW.md` Trigger 2
did **not** fire for pass #8 (this pass found plenty), so the tripwire stays
armed only if pass #8 and pass #9 both find something.
