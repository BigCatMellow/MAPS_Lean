# Roadmap trajectory check #4 - arc: PRs #128-#132

Fourth pass after the session-6 handoff. This covers the merged portable
deployment roadmap/design updates (#128-#129), incident taxonomy vocabulary
(#130), wikilink repair (#132), and environment-availability policy dimension
(#131).

## 1. Re-verified against real `main`

- `git log --oneline -5` confirms current `main` is `886090b`:
  #131, #132, #130, #129, and #128 are all merged.
- Live GitHub state verified on 2026-08-20: no open PRs. PR #131 and PR #132
  are `MERGED`, with both required checks (`test`, `review-evidence`) green.
- PR #131 review evidence is present at
  `work/reviews/pr-131-review-evidence.md`. The reviewer reproduced the
  circular-import issue, confirmed `runtime/routing/router.py` remains
  unwired, and ran the full suite after branch update.
- `runtime/policy/evaluator.py::evaluate_assignment` now accepts
  `environment_report` and rejects only `CompatibilityState.INCOMPATIBLE`.
  `runtime/routing/router.py` still does not source/pass an environment
  report, so roadmap 6.24 correctly remains `IN PROGRESS`.
- `runtime/incident_taxonomy.py::IncidentClass` exists with the roadmap's
  19-member vocabulary. `runtime/state/outcomes.py` still accepts free-text
  `failure_class`, so roadmap 6.27 correctly remains `IN PROGRESS`.
- `runtime/recovery/supervisor.py::tick()` still has no production callers
  outside tests. The Option B harness/RnS arc remains paused on the same
  precondition found in #125.
- Portable Deployment now has recorded operator decisions and D2 split into
  D2a/D2b/D2c, but no D2a design artifact or target `.maps/` templates exist
  on `main` before this pass.

## 2. What changed the picture

The #128-#129 portable-deployment work removed the main design fork for v1:
file-convention-only, sibling-clone adapter, best-effort review discipline,
stack-agnostic target scope, and target-repo-owned `.maps/` state are now
recorded operator decisions. That makes D2a the first unblocked portable
deployment task.

The #130 and #131 merges closed two vocabulary/capability gaps but left their
live enforcement/consumer wiring deliberately open. That is correct scope
control, not a pivot signal.

## 3. Decision: continue, select D2a

Continue the roadmap as written. Do not resume the paused Option B harness/RnS
arc without a real production invocation trigger. Do not pick SEC3 as a quick
task; destructive/external action classification still needs design first.

Selected next work: `D2a-file-convention-design`. It is a planning task whose
output is a MAPS_Lean-side design note plus draft target-repo template files.
It does not authorize an installer, sibling-clone adapter implementation, or
the Chain Shovel pilot.
