# Roadmap trajectory check #7 — arc: PRs #157-#161 (+#162 open)

Seventh pass. Pass #6 (`work/notes/2026-08-24-roadmap-trajectory-check-6.md`,
merged via #158) covered PRs #128-#156 (+#157 open) at `origin/main` HEAD
`ee7d14c`. This pass covers everything merged since: `ee7d14c..52a3de1` —
exactly four commits/PRs: #157 (`Bind Git runs to worktree identity`, merged
as `efe2c8b`/`c9c07fd`), #158 (pass #6's own note, `f3ebafe`), #160 (`RnS
harness resume call site`, `4431b3a`), and #161 (`Design SEC3/6.4
destructive-external-action Hook guard`, `52a3de1`). Plus PR #162 (`RnS
production trigger loop design`), currently OPEN, design-only, not yet
merged.

## 0. Situational awareness

- `gh pr list --state open`: exactly one open PR, #162, design-only note
  (`work/notes/2026-08-24-rns-production-trigger-loop-design.md`), no
  `runtime/`/`tests/` changes, has its own review-evidence file already
  staged but not yet independently approved/merged per this task's dispatch
  info. Left untouched — this check does not review or merge #162.
- No other in-flight worktrees observed with uncommitted newer-than-HEAD
  changes relevant to this arc.

## 1. Re-verified against real `origin/main` (52a3de1)

- `python3 -m runtime.smoke` passes clean.
- **PR #160 claim (RnS harness resume production call site) — confirmed
  real, not prose-only.** `runtime/recovery/supervisor.py::
  RecoverySupervisor.tick()` now routes resume attempts through
  `HarnessService.resume()` (via the existing, unmodified
  `HcomHarnessAdapter`) whenever it can construct an `ExecutionBinding`/
  `SessionRef` from the incident's session/run lineage, falling back to the
  prior direct `hcom.resume()` call except when an installed
  `CANONICAL_RUN` Hook actively denies (new `resume_denied` outcome, no
  task-truth mutation). This is exactly pass #6's §4a item 1 ("single most
  ready to dispatch item") and it landed as scoped.
- **Re-verified pass #6's flagged residual gap is still real and unclosed:**
  `grep -rn "RecoverySupervisor(" runtime/` and `grep -rn "\.tick(" runtime/`
  outside `tests/` return zero production callers — nothing in `runtime/`
  ever constructs a `RecoverySupervisor` or invokes `.tick()` except
  `tests/test_recovery_supervisor.py` and
  `tests/test_runtime_review_hardening.py`. #160 built the resume-routing
  *body* of `tick()`; it did not add anything that calls `tick()` in
  production. `CAPABILITY_CHECKLIST.md`'s own H4 row already states this
  accurately ("nothing yet triggers `tick()` in production"). This is the
  exact gap PR #162 (open) targets — re-confirmed independently before
  reading #162's own body, then cross-checked: #162 cites the same
  `work/insights/2026-08-19-recoverysupervisor-tick-has-zero-production-
  invocation-anywh-INSIGHT-e0b448a6.md` finding. Consistent.
- **6.5/H4/E4 checklist rows correctly still `IN PROGRESS`, not flipped to
  `DONE`** by #160 — validation-tier command execution remains
  unimplemented and nothing triggers `tick()` yet, so the phase's own exit
  gate ("representative failures caught immediately after mutation") is
  still not met. Confirmed the checklist text matches code exactly.
- **PR #161 (SEC3/6.4 destructive-external-action Hook guard) — confirmed
  design-only, as the dispatch instructions expected.** `git show 52a3de1
  --stat`: two files touched, `work/notes/2026-08-24-sec3-destructive-
  action-hook-guard-design.md` and its review evidence — zero `runtime/` or
  `tests/` changes. `CAPABILITY_CHECKLIST.md`'s SEC3/6.4 rows are unchanged
  by this PR and still correctly read `IN PROGRESS` ("only `CANONICAL_RUN`
  enforcement exists... zero registered guards" for
  `BEFORE_EXTERNAL_ACTION`/`BEFORE_DESTRUCTIVE_ACTION`). No roadmap item was
  marked `DONE` because of a design note — verified, not just asserted.
- **PR #162 (RnS production trigger loop design) — same pattern, confirmed
  design-only from its own diff** (`gh pr view 162 --json files`): exactly
  `work/notes/2026-08-24-rns-production-trigger-loop-design.md` +
  `work/reviews/pr-162-review-evidence.md`. Still open/unmerged; not counted
  toward this pass's scoreboard.
- **Master roadmap tag citations spot-checked directly** (not copied from
  pass #6's prose) for every item pass #6 cited in its horizon report: 6.4
  `P1`, 6.5 `P1`, 6.10 `P1/P2`, 6.16 `TRIGGERED`, 6.17 `TRIGGERED`, 6.19
  `TRIGGERED/P2`, 6.20 `TRIGGERED/P2`, 6.21 `P2/TRIGGERED`, 6.22 `P1
  design/security invariant`, 6.24 `P1/P2`, 6.25 `TRIGGERED`, 6.35 `P0
  design / open decision` — all match `00-MASTER-MAPS-CAPABILITY-ROADMAP.md`
  exactly as pass #6 cited them. No stale tag citation found this pass
  (unlike pass #4/#6's caught 6.16 P1-vs-TRIGGERED mislabel).

## 2. Master-inventory scoreboard (`CAPABILITY_CHECKLIST.md` §7)

Recounted directly from the current table (35 rows, 6.1-6.35):

- **DONE (16, unchanged from pass #6):** 6.1, 6.2, 6.3, 6.6, 6.7, 6.8, 6.13,
  6.14, 6.15, 6.18, 6.23, 6.26, 6.27, 6.28, 6.29, 6.30.
- **IN PROGRESS (13, unchanged from pass #6):** 6.4, 6.5, 6.9, 6.10, 6.11,
  6.16, 6.19, 6.20, 6.21, 6.22, 6.24, 6.33 (evaluation-only, by design),
  6.35.
- **NOT STARTED (6, unchanged from pass #6):** 6.12, 6.17, 6.25, 6.31, 6.32,
  6.34.

**No scoreboard delta this pass.** #160 deepened 6.5's evidence (real
production call site now exists) without flipping its label — correctly,
since the phase's exit gate is still unmet. #161/#162 are design notes and
correctly do not move any label. This arc's real progress is evidence
depth, not status-count movement.

## 3. What changed the picture since pass #6

- **6.5/H4/E4's "immediately next" item from pass #6 §4a landed exactly as
  scoped** (PR #160) — the RnS harness resume design (PR #154) was picked
  up and implemented with no scope drift: no task-truth mutation, no new
  trigger loop, `CANONICAL_RUN` deny path surfaced as a distinct outcome.
  Confirms the design-note pattern (fully bounded design PR, then a
  faithfully-scoped implementation PR) is working as intended across two
  consecutive arcs now (#154→#160, and now #161→#162 following the same
  shape for SEC3).
- **The next fast-follow pass #6 named ("validation-tier hook-in") has not
  yet been designed or picked up** — instead, a different but related gap
  got designed first: PR #162 targets "what triggers `tick()` at all in
  production," which is a prerequisite ordering question pass #6 did not
  explicitly separate from "validation tiers hook in." Both gaps are real
  and independent: even once something calls `tick()` in production (what
  #162 proposes), the resume path still runs no validation tier (what pass
  #6's step 2 named). Worth naming explicitly so a future session doesn't
  conflate "tick() gets invoked" with "6.5's exit gate is met" — they are
  two separate remaining slices, not one.
- **SEC3/6.4 (destructive/external-action Hook guard) got its first design**
  (PR #161), following the same finding→decision→boundary→non-goals shape
  as PR #154/#160's precedent: a caller-declared destructive/external
  boolean context plus a second `HookEnforcement` type gated the same way
  `CANONICAL_RUN` is today, no new action registry or policy engine. This
  was pass #6's §4b item 1 ("next tier," ranked #1) — correctly picked up
  next, in ranked order.
- No other roadmap surface moved. Portable deployment (6.35/D3), the
  TRIGGERED items (6.16, 6.17, 6.19-6.21, 6.25), and the EVIDENCE-GATED
  items (6.28-6.31/6.33-6.34, per the checklist's own listing — 6.28/6.29/
  6.30 are actually `DONE`, this refers to 6.31/6.33/6.34's still-gated
  status) are all untouched this arc — confirmed via the 4-commit diff
  covering only `runtime/recovery/supervisor.py`,
  `work/notes/2026-08-24-*trigger-loop-design.md`, and review-evidence
  files.

## 4. Decision: continue, no pivot

Both PRs this arc trace directly to items pass #6 itself ranked as
next-to-dispatch (§4a's RnS call-site, §4b's SEC3 ranked #1) and both
followed the design-then-implement pattern without scope drift. No new
speculative capability surfaced. No pivot warranted.

## 5. Horizon report

### 5a. Immediately next

1. **Merge PR #162** (RnS production trigger loop design) once its
   independent review lands cleanly — it is design-only, already scoped
   against the same non-daemon constraint the roadmap's §7.1/§7.9 requires
   (reuses the existing `claim` CLI mutation as the trigger event, plus a
   bounded new `recovery-tick` CLI subcommand for the all-silent-workers
   case). Then dispatch its "bounded follow-up implementation" scope the
   same way #154→#160 went, closing the "zero production invocation of
   `tick()`" gap this pass re-confirmed is still real.
2. **Validation-tier hook-in remains separately undesigned** (§3 above) —
   once #162's implementation lands, the harness will invoke `tick()` in
   production but still run no validation tier on resume. This is the
   actual remaining piece of 6.5/H4/E4's exit gate and needs its own design
   note (likely a short one, since #154's design already named this as a
   "separate fast-follow task" and scoped the call-site boundary that a
   validation-tier design would hook into).
3. **SEC3/6.4 destructive-external-action guard implementation** — PR #161's
   design is complete (caller-declared boolean context +
   `DESTRUCTIVE_EXTERNAL_ACTION` `HookEnforcement` type, gated like
   `CANONICAL_RUN`). Same shape as #154/#162: fully scoped, ready to
   dispatch as an implementation task with no further design work needed.

### 5b. Next tier — non-TRIGGERED/non-EVIDENCE-GATED candidates (unchanged from pass #6, still viable, re-verified against current code)

1. **6.10 — SEC4 Skill lifecycle persistence** (`P1/P2`). Transition-
   validation primitive (`runtime/skills/lifecycle.py`) still exists,
   tested, unpersisted. Unaffected by this arc's PRs. Still viable — no new
   design blocker found.
2. **6.22 — Memory trust enforcement gate** (`P1 design/security
   invariant`). Vocabulary (#127) and annotation (#149) unaffected by this
   arc. Still no gate consults `MemoryTrustClass` for a real decision.
   Still viable on the already-selected enforcement seam (#148).
3. **6.24 — production environment-report source/cache** (`P1/P2`).
   Unaffected by this arc. Caller-supplied-only remains the state; still
   missing a real production source and default required-for-routing rule.
4. **6.16 — finish worktree-binding integration** (`TRIGGERED`, legitimately
   active per its recorded trigger, pass #1). #157 merged this arc —
   `verify_git_run()`'s mismatch path exists and is tested but still not
   proven wired into a real production dispatch flow (checklist itself
   says "without adding worktree creation, cleanup, or merge authority").
   Re-verify a real call site invokes it before calling E6 closer to done.

### 5c. Correctly gated/blocked — do not re-investigate

Unchanged from pass #6, re-spot-checked, no drift found:

- **6.35/D3** — still blocked on an explicit operator target decision. No
  new pilot proposal should be inferred.
- **6.25/SEC6 credential broker** — `TRIGGERED`, no triggering condition
  recorded this arc either.
- **6.17/E7 sandboxes/rehydration** — `TRIGGERED`, gated on 6.16 maturing
  further; 6.16 is mid-flight (§5b item 4), still don't start E7.
- **6.31-6.32, 6.33-6.34** — `EVIDENCE-GATED`/`NOT STARTED` by current
  roadmap decision; `runtime/README.md`'s "not a production path" framing
  for 6.33 is unaffected by this arc's commits (no diff touched
  `runtime/context_retrieval_semantic.py` or `runtime/README.md`).
- **6.12/S7 Capability Packs** — gated on S6 reaching `DONE`; S6 status
  unaffected by this arc's four commits.
- **6.19/6.20/6.21 further authority increments** — pass #6's flagged
  discipline gap (TRIGGERED-tagged items got implementation-shaped PRs
  without a recorded trigger event) is unaffected this arc — no PR touched
  these three items. The gap is not resolved but also has not grown; no
  further authority-bearing work landed on them to re-flag.

## 6. Honesty check on drift

Every PR this arc (#157, #160, #161, and #162 pending) traces to an item
pass #6 itself explicitly ranked as next-to-dispatch. Nothing speculative
was added; both implementation and design work followed the established
design→bounded-implementation pattern with no scope creep (verified by
diffing exactly which files each PR touched, not by trusting PR titles).
The one open procedural item — pass #6's 6.19/20/21 undocumented-trigger
flag — is dormant, not resolved, since nothing touched those three this
arc. No roadmap update needed this pass; `CAPABILITY_CHECKLIST.md`'s
existing rows for 6.5, 6.4/SEC3, and 6.16 already accurately reflect this
arc's landed work (confirmed by direct code inspection, not just re-reading
the checklist's own prose).

## Resume prompt

If resuming mid-flight: PR #162 (`rns-trigger-loop-design`, "RnS production
trigger loop design") is open, design-only, and needs its independent
review to land cleanly before merge (never self-certify). Once merged,
dispatch its named bounded implementation task (reuse the `claim` CLI
mutation as trigger event + new `recovery-tick` CLI subcommand) to finally
give `RecoverySupervisor.tick()` a real production caller — re-verified
this pass that zero production caller currently exists
(`grep -rn "RecoverySupervisor(\|\.tick(" runtime/` outside `tests/` is
empty). After that lands, a short validation-tier-hook-in design is the
remaining piece to actually close 6.5/H4/E4's exit gate — don't conflate
"tick() has a production caller" with "6.5 is done," they are separate
slices (see §3). In parallel or after, SEC3/6.4's design (PR #161) is fully
ready to dispatch as an implementation task with no further design
questions open. Once either the validation-tier design or the SEC3
implementation lands (whichever completes first), run
`ROADMAP_TRAJECTORY_CHECK.md` pass #8. Otherwise, self-select from §5b's
ranked list (SEC4 skill-lifecycle persistence or memory-trust enforcement
gate are next-best-shaped after the two items above).
