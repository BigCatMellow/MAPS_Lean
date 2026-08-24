# Roadmap trajectory check #4 — arc: PRs #128-#156 (+#157 open)

Fourth pass. `-3.md` covered #126-#127 + a re-verify gate with no new PRs.
This pass covers everything merged since then: #128 through #156 on
`origin/main` (HEAD `ee7d14c`), plus PR #157 (`Bind Git runs to worktree
identity`), currently OPEN/draft, mergeable, not yet merged.

## 0. Situational awareness (live state, not durable)

- `gh pr list --state open`: exactly one open PR, #157, draft, mergeable,
  head `run-worktree-binding`. No other PR is currently open.
- No worktree matching the RnS-harness-resume fast-follow work is currently
  active. `/tmp/rns-harness-callsite-task` exists but is stale: its HEAD
  (`9c17fe5`) is ~9 PRs behind main, it has a clean working tree tracking
  `origin/rns-harness-callsite-task`, and that branch's own PR (#148,
  "Design memory trust enforcement seam") already merged and is unrelated to
  RnS resume. The directory name is misleading leftover state, not evidence
  of in-flight work. **Correction to this task's own framing: no other
  session currently appears to be implementing the RnS harness resume
  call-site fast-follow.** It's designed (PR #154) but not yet dispatched as
  an implementation task.
- `/tmp/*` also holds ~30 other worktrees from earlier sessions
  (`portable-d1-installer-design`, `session-roadmap-update`,
  `context-builder-*`, `policy-env-wave20`, etc.) — none show uncommitted
  changes newer than their last commit; they read as merged-and-abandoned,
  not active. Left untouched per instructions.

## 1. Re-verified against real `origin/main` (ee7d14c)

- `python3 -m runtime.smoke` passes clean.
- 6.22/PR#149 claim: `runtime/context_builder.py` imports `MemoryTrustClass`
  and actually annotates `guidance`/`withheld_guidance`/`skills` items with
  `budget_class` and trust-derived mappings (`CANDIDATE_LESSON`, `RETIRED`,
  `SUPERSEDED`) — confirmed real, not prose-only.
- 6.16/E6/PR#157 claim: `runtime/integrity/git_scope.py` now has
  `collect_git_worktree_identity()` (repo_root, git_common_dir, git_dir,
  worktree_private_dir, head_revision) and `verify_git_run()` compares it
  against a stored `manifest["worktree"]`, returning `worktree_mismatch` /
  `worktree_unavailable` — matches `work/notes/2026-08-24-worktree-run-
  binding-design.md`'s recommended schema. Real, additive, not yet merged
  (still open as #157).
- 6.24/PR#151 claim: `runtime/routing/environment_reports.py::
  select_fresh_environment_reports` exists and does real staleness/spec/
  project/revision filtering; `task_environment` table confirmed present in
  `runtime/state/environment_contract.py`, `readiness.py`, `integrity.py`.
- 6.5/H4/E4 claim (still IN PROGRESS, no production call site): confirmed —
  no PR between #128 and #157 adds a real `HarnessService.resume()` caller
  in `runtime/recovery/supervisor.py`. The RnS resume design (PR #154,
  `work/notes/2026-08-21-rns-harness-validation-callsite-design.md`) is
  complete and bounded but its recommended implementation task has not been
  dispatched yet — see §0.
- Spot-checked `work/coordination/README.md`: durable role/authority
  conventions, no live status claims to re-verify against.

All sampled `CAPABILITY_CHECKLIST.md` rows held up against actual code.

## 2. What changed the picture since pass #3

- **Portable deployment (6.35) got a full sub-roadmap** (`06-portable-
  deployment.md`, PRs #128-#129, #133-#138, #142) with D0-D2c all landing
  this arc, then the named pilot target (Chain Shovel) was explicitly
  demoted from "selected" to "example" (#142) after `work/handoffs/2026-08-
  21-...md` flagged the drift. D3 (first external pilot) remains
  correctly `NOT STARTED`, blocked on an operator-only decision (target
  selection/access/authority) — no code work should attempt to infer this.
- **6.19/6.20/6.21 moved from `TRIGGERED`-and-untouched (pass #3's own
  "correctly left alone") to `IN PROGRESS` with real merged code** (#143
  `maps flow start`, #144 helper continuity registry, #145 no-progress
  advisory, #146 routing CLI input, #155 `maps flow review-start`) —
  **without any recorded trigger-condition evidence.** The master roadmap
  tags these `TRIGGERED/P2` / `P2/TRIGGERED`, meaning "implement only when
  usage/risk demonstrates need." No task, handoff, or design note in this
  arc names the triggering usage/risk event. This is worth naming honestly:
  either (a) an implicit judgment call was made that composing existing
  guarded primitives into deterministic flows is low-risk enough not to need
  a formal trigger, which is plausible given every increment stayed
  advisory/metadata-only and stopped short of actual authority, or (b) this
  is quiet trigger-gate erosion. Given all three (6.19/20/21) increments
  are explicitly non-authoritative (metadata TTL checks, read-only
  advisories, flows that stop before provider/verdict actions), this reads
  as (a) — bounded, reversible slices, not the "provider health checks"
  or "recovery action" substance the trigger was meant to gate. Continue,
  but flag: if a future increment on 6.19/20/21 crosses into actually
  consuming the advisory (auto-resume, auto-reassign), that crosses the
  trigger and needs the condition named explicitly first.
- **RnS harness resume call site got a complete, narrowly-bounded design**
  (PR #154) that sequences H4/E4/6.5 correctly (base resume wiring before
  validation-tier hook-in) — but per §0, this design has not yet been
  picked up by an implementation task. This is the single most
  "ready to dispatch" item on the whole roadmap right now: fully scoped,
  explicit stop conditions, explicit non-goals, no open design questions.
- **Git worktree isolation (6.16) got a second real increment** (#156
  design, #157 implementation-in-review) closing the gap pass #3's arc
  didn't touch: run manifests can now bind and verify actual Git worktree
  identity, not just changed-path scope.
- **Memory trust (6.22) got its enforcement-seam design** (#148) and first
  real annotation wiring (#149) — vocabulary (from pass #3's own #127 work)
  now actually touches `context_builder.py` output, though no gate consults
  it yet.
- **Task environment contract storage** (#152/#153) is new infrastructure
  the master roadmap doesn't name as its own numbered item — it's plumbing
  underneath 6.24, not a new roadmap surface. No checklist update needed
  beyond what's already there.

## 3. Decision: continue, no pivot

Every item above traces cleanly back to master roadmap §1's "operating
system around capable AI workers" framing — task truth, authority
boundaries, deterministic hooks, environment awareness, review evidence.
Nothing this arc invented new speculative capability work outside the
checklist. The one soft flag (6.19/20/21 TRIGGERED-without-recorded-trigger)
is a documentation-discipline gap, not a direction problem — the actual
code stayed inside safe bounds. No roadmap update needed this pass beyond
what's already current.

## 4. Horizon report

### 4a. Immediately next (after the RnS design's fast-follow lands)

The task's own framing assumed base RnS harness resume wiring was already
mid-flight elsewhere; it is not (§0). So "immediately next" is two serial
steps, both already fully specified and ready to dispatch with no further
design work:

1. **Dispatch the bounded implementation task PR #154 already named**:
   "RnS harness resume production call site" — construct `ExecutionBinding`
   inside `RecoverySupervisor.tick()`, route through
   `HarnessService.resume()` reusing the existing `HcomHarnessAdapter
   .resume()` semantics, preserve the RnS safety contract (no task-truth
   mutation, no new trigger loop, no validation execution). Explicit test
   list is already written in the design note — an implementer doesn't need
   to invent scope.
2. **Validation-tier fast-follow** (separate PR, per the design's own
   sequencing): attach `EnvironmentSpec.validation.quick` at the new
   resume-adjacent harness event, sourced from explicit task/run evidence
   only (no default spec, no cache, no mandatory gate). This is what
   actually closes H4/E4/6.5's exit gate.

Once both land, `work/notes/2026-08-24-worktree-run-binding-design.md`'s
schema (already drafted, PR #157 implementing it) plus the RnS resume path
together give the harness its first real production-authoritative call
site with worktree-identity-bound evidence — a genuine milestone, not just
another increment.

### 4b. Next tier — 3-5 viable non-TRIGGERED/non-EVIDENCE-GATED candidates

1. **6.4 — SEC3 destructive/external-action hook guards** (`P1`). Registry
   (H3) is `DONE`; only `CANONICAL_RUN` enforcement exists.
   `HookEvent.BEFORE_EXTERNAL_ACTION`/`BEFORE_DESTRUCTIVE_ACTION` are
   declared enum values with zero registered guards. Viable now because the
   registry/enforcement machinery already exists — this is "add the second
   enforcement type," not new infrastructure.
2. **6.10 — SEC4 Skill lifecycle persistence** (`P1/P2`). The
   discovered→validated→...→retired transition-validation primitive
   (`runtime/skills/lifecycle.py`) already exists and is tested; it just
   isn't durable or wired to real operator authority yet. Viable now
   because the hard design work (state machine, transition rules) is done —
   remaining work is storage + call-site wiring, same shape as 6.16/6.24's
   recent increments.
3. **6.22 — Memory trust enforcement gate** (`P1`). Vocabulary (#127) and
   annotation (#149) both landed; no gate actually *consults*
   `MemoryTrustClass` to make a decision yet. Viable now because the
   enforcement-seam design (#148) already selected a bounded first seam —
   an implementer has a concrete target, not a blank page.
4. **6.24 — continue toward production environment-report source/cache**
   (`P1/P2`). Currently caller-supplied-only; still missing a real
   production source and default required-for-routing rule. Viable as
   an incremental next slice on infrastructure that's already 4 PRs deep
   this arc (#146, #150, #151, #152/153) with a design note already
   resolving the freshness/filtering boundary.
5. **6.16 — finish worktree-binding integration** (`P1` architectural,
   currently `IN PROGRESS`). #157 is open/mergeable now — get it reviewed
   and merged, then verify `verify_git_run()`'s new mismatch path is
   actually exercised by a production call site (currently only tested,
   not proven wired into a real dispatch flow).

### 4c. Correctly gated/blocked — do not re-investigate

- **6.35/D3 — first external portable-deployment pilot**: blocked on an
  explicit operator decision (target repo, access, authority). D0-D2c are
  all done; D3 needs a name and a yes from the operator, not more design
  work. Chain Shovel was explicitly rejected as inferred authority — don't
  re-propose it or any other target without an operator naming it.
- **6.25/SEC6 — credential broker**: `TRIGGERED`, no triggering condition
  (frequent credential-bearing remote tasks) has occurred or been recorded.
  Correctly untouched.
- **6.17/E7 — sandboxes/snapshots/rehydration**: `TRIGGERED`, explicitly
  gated on 6.16/E6 maturing further first. E6 is mid-flight (#157); don't
  start E7 until worktree binding actually merges and proves out.
- **6.28-6.31, 6.33-6.34 — evaluation/refinement/retrieval/mission layer**:
  all `EVIDENCE-GATED`, and the roadmap's own stance (context builder stays
  explicit-first) is still correct per `runtime/README.md`'s explicit
  "not a production path" framing for the one built evaluation candidate
  (6.33). No new evidence this arc changes that.
- **6.12/S7 — Capability Packs**: gated on S6 (skill routing) reaching
  `DONE`. S6 is `IN PROGRESS` (attributed selection wired, body loading
  still not real) — stay parked until S6 actually closes.
- **6.19/6.20/6.21 further authority increments**: current metadata/advisory
  slices are fine to continue (§2), but do not let a future increment cross
  into real provider-health checks, auto-resume, or auto-reassignment
  without first naming the trigger condition explicitly, per the master
  roadmap's own tag on these three items.

## 5. Honesty check on drift

The roadmap still traces cleanly to §1's "operating system around capable
AI workers" — every merged PR this arc is infrastructure for task truth,
authority, environment awareness, or review evidence, not personality/
feature creep. The one real discipline gap found this pass is procedural,
not directional: `TRIGGERED`-tagged items got implementation-shaped PRs
without a recorded trigger event (§2). Recommend the next session that
touches 6.19/20/21 add an explicit one-line "trigger observed: ..." note
before further authority-bearing work on those three, so this doesn't
quietly become the norm for other `TRIGGERED` items too.

## Resume prompt

If resuming mid-flight: PR #157 (`run-worktree-binding`, "Bind Git runs to
worktree identity") is open/draft/mergeable and needs an independent
reviewer dispatched before merge (never self-certify). After it merges,
dispatch the RnS harness resume production call-site implementation task
exactly as scoped in `work/notes/2026-08-21-rns-harness-validation-
callsite-design.md`'s "Bounded follow-up implementation" section — that
design is complete and ready, nobody has picked it up yet. Once that lands
and its validation-tier fast-follow lands, run `ROADMAP_TRAJECTORY_CHECK.md`
pass #5. Otherwise, self-select from §4b's ranked list (SEC3 hook guards or
SEC4 skill-lifecycle persistence are the next-best-shaped candidates after
RnS/validation).
