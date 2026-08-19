# Roadmap trajectory check — 2026-08-19

Run per the new `playbook/ROADMAP_TRAJECTORY_CHECK.md` (added in this same
PR), at the natural arc boundary this session hit: 11 PRs merged
(`#105`-`#115`, plus `#116` from a concurrent session and this doc PR),
`work/roadmaps/CAPABILITY_CHECKLIST.md`'s remaining `NOT STARTED` rows all
turned out to be `TRIGGERED`/conditional or blocked on unmerged prerequisite
wiring — a clear signal to stop and check trajectory before picking the next
task by habit.

## 1. Re-verification

Every `DONE`/`IN PROGRESS` status touched this arc was independently
SENTINEL-reviewed at exact merge head before merging (`work/reviews/pr-105`
through `pr-117`), not just asserted. No additional spot-check drift found
beyond what those reviews already caught (the two review-evidence
head-rebind mechanics issues, both resolved — see §2).

## 2. What changed the picture this arc

- **Root cause found, not previously named as one thing:** `grep -rln
  "ExecutionBinding(" runtime/ --include=*.py` returns zero production
  files — `runtime/harness/service.py`'s `HarnessService` has no real
  caller anywhere in the codebase yet. This is the single underlying reason
  H4, H5 (remaining-adapters half), L6, L7, and SEC3 are all independently
  stuck at "the pieces exist, nothing calls them in production." The
  checklist already said this per-phase; the arc-level finding is that it's
  *one* gap, not five independent ones — worth naming once instead of
  re-discovering per phase. A design note (`work/notes/2026-08-19-harness-
  production-wiring-gap.md`, separate PR) lays out the wiring options and a
  recommended direction.
- **Review-evidence mechanics friction, twice:** an empty "trigger CI
  re-run" commit and a `main`-merge-to-update-branch step each broke the
  `check_review_evidence.py` walk-back (it requires a trailing commit's own
  diff to be non-empty to treat it as evidence-only, and never walks past a
  merge commit). Both were root-caused and worked around cleanly (rebind
  `head_sha` to the actual new head, verify the reviewed files are
  byte-identical via `git diff`, re-run the check script locally before
  pushing). Not a roadmap-priority change, but a real repeated-friction
  pattern worth a durable countermeasure if it recurs again (per
  `playbook/REPAIR_AND_LEARNING.md`'s "if a failure repeats, add a durable
  countermeasure" rule) — e.g. a short note in `scripts/check_review_evidence.py`'s
  own docstring or a CI-adjacent doc explaining the rebind procedure, so
  the next session doesn't have to re-derive it. Not filed as a full repair
  record this pass since it was resolved inline both times without lasting
  impact; worth revisiting if it happens a third time.
- **Shared-worktree collisions between concurrent sessions:** happened
  twice early in this arc (a fork/subagent running `git checkout`/`gh pr
  checkout` directly in the shared `~/Projects/MAPS_Lean` clone, discarding
  another lane's uncommitted work). Fully mitigated for the rest of the arc
  by requiring every dispatched agent to work in an isolated `git worktree`
  and never touch the shared checkout's branch state — this became a
  standing dispatch-prompt convention for the remainder of the session and
  should stay one going forward.
- **EXP-A (Skill-routing benchmark) in flight as of this check** — its
  results aren't folded in yet; the next trajectory check (or a fast-follow
  note) should incorporate whatever it finds about `_select_skills`'s
  precision.

## 3. Decision: continue or pivot

**Continue, with one redirect already acted on.** Nothing this arc surfaced
contradicts the roadmap's own priority ordering enough to justify
reprioritizing away from the capability checklist. The one real pivot this
arc produced — the harness-production-wiring gap — is being handled as a
new bounded item (a decisive design note, then implementation), not a
reason to stop working the existing backlog. No new roadmap item is being
opened beyond that; the gap is already implicitly covered by the H4/H5/L6/
L7/SEC3 rows it explains, it just needed naming once at the arc level.

Going forward this arc: once the harness-wiring note lands with a concrete
recommended direction, that becomes the next implementation lane (likely a
meaningfully larger task than this arc's other items, since it touches how
multiple subsystems connect — worth its own careful scoping rather than
folding into a quick wave-numbered task).
