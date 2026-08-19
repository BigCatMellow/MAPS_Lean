# Roadmap trajectory check #2 — 2026-08-19

Second pass per `playbook/ROADMAP_TRAJECTORY_CHECK.md`, covering the arc
since check #1 (`work/notes/2026-08-19-roadmap-trajectory-check.md`, after
PR #117): PRs #118-#125, 8 more merged. Trigger: EXP-A produced a real
precision finding, and a new root-cause-adjacent gap (RnS's invocation loop)
surfaced while scoping a follow-up — both are the kind of findings this
check exists to fold in.

## 1. Re-verification

All of #118-#125 independently SENTINEL-reviewed at exact merge head
(`work/reviews/pr-118` through `pr-125`), including two reviews explicitly
instructed to reproduce claimed metrics/safety-properties rather than trust
them (PR #120's EXP-A numbers reproduced bit-for-bit; PR #124's
never-gates-a-decision safety property re-traced independently and its proof
test re-run). No drift found beyond the review-evidence merge-commit
mechanics already documented in `playbook/WORKTREE_ISOLATION.md`.

## 2. What changed the picture this arc

- **EXP-A ran for real** (PR #120): `_select_skills` scores F1 0.889 against
  a 12-case frozen corpus, with one concrete false-positive (permissive
  any-token-overlap matching triggers on a single shared word) and one
  concrete missed-activation (pure vocabulary shift, no literal overlap).
  This is now real evidence about a real production code path's actual
  reliability — the first such evidence anywhere in this arc for anything
  beyond pass/fail tests.
- **Root-cause finding acted on, not just documented** (PR #119, #123, #124):
  the "zero production `HarnessService` callers" finding turned into real
  forward progress, not just a note — `resume()` normalized, shadow
  observation wired into RnS with an empirically-proven safety property.
  This is the arc's biggest structural move: the Harness layer has its
  first real (if shadow-only) production connection.
- **A second, adjacent gap surfaced** (PR #125): scoping the "wire
  `harness_service=` with real data" follow-up revealed `RecoverySupervisor
  .tick()` itself has zero production invocation anywhere — not a
  harness-specific problem, a whole-module one. Correctly NOT acted on
  (building an invocation loop would be a new always-on daemon, against the
  roadmap's own non-goals without a real trigger) — captured as an insight
  instead and deferred to this check.
- **The genuinely-startable backlog thinned further.** After this arc, the
  16 remaining `NOT STARTED` rows are, on inspection, uniformly one of:
  `TRIGGERED`/conditional with no fired trigger (E7, SEC6), blocked on
  unmerged prerequisite wiring this arc didn't reach (L7/L8/L9 need L6's
  hash actually persisted on a real run; S7 needs S6 to mature further), or
  need real operational A/B data that doesn't exist yet because the systems
  being measured (hooks, ACI results, EnvironmentSpec compatibility in
  practice) have almost no production usage to measure (EXP-B/C/D/E). None
  of these were skippable by habit — each was checked and has a real reason
  it isn't ready, not just "harder" or "less interesting."
- **6.22/6.24** (memory trust class unification; least-privilege proof
  across scope/environment dimensions) remain `IN PROGRESS` with real
  partial evidence but need an actual design decision (what the unified
  vocabulary should be; what "capability intersection" means as testable
  code) that wasn't derivable from existing docs this arc — correctly not
  forced.

## 3. Decision: continue or pivot

**Continue the Option B arc; no pivot.** The RnS-invocation-loop finding
doesn't change roadmap priority — it's a precondition discovered mid-stream,
not a reason to abandon the harness-wiring direction. Recorded as an
insight (PR #125) rather than a roadmap item of its own, since it's not yet
clear it needs one (per the insight's own `--next-test`: decide at the next
check whether it needs a design note or stays out of scope pending a real
trigger).

Concretely, for whoever picks this up next: the next well-scoped,
non-speculative task in this arc is *not* obvious right now — the shadow
observation (PR #124) can't accumulate real data without RnS having a real
invocation loop, and building that loop needs its own trigger/justification
first. Rather than force a task, the honest state is: **this specific
sub-arc (Option B / H5-SEC3 unblocking) is now blocked on the same kind of
missing-invocation-loop question one level up**, and the right next move is
either (a) wait for a real operator-visible RnS incident to justify building
an invocation loop, or (b) pick a genuinely independent thread from the few
remaining checked-and-real candidates (6.22 or 6.24, both of which need a
real design pass, not a quick task) rather than stall. Both are legitimate;
neither should be treated as "nothing to do."
