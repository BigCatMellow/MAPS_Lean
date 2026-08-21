# Handoff: MAPS_L roadmap progress and next execution slice

- From: `/root`
- To: next MAPS_Lean agent
- Task: continue MAPS_L runtime/roadmap execution after PRs #142-#146
- Status: no open PRs; next likely work is H4/E4/6.5 validation-tier production-call-site shaping

## What is true now

- VERIFIED: as of 2026-08-21, `origin/main` includes PRs #142 through #146.
- VERIFIED: no helper agents are actively working at this handoff. Prior reviewer agents for PRs #144-#146 are completed.
- VERIFIED: Chain Shovel / the prior named target was removed from active portable-deployment planning. It was an example, not an authorized target.
- VERIFIED: portable deployment 6.35 remains `IN PROGRESS`; D0/D1/D2a/D2b/D2c are complete, and D3 is still `NOT STARTED`.
- VERIFIED: 6.19, 6.20, 6.21, and 6.24 are all `IN PROGRESS` with new merged runtime/CLI pieces.
- VERIFIED: latest merged main at handoff was `b87fc7221fd6bd928f699881eacd16261231c363`.
- UNKNOWN: the first real external portable-deployment pilot target, task, access path, reviewer, CI/hosting policy, and merge authority.

## Work completed

- Merged PR #142: removed the example target from active portable-deployment planning.
- Merged PR #143: added `maps flow start`.
- Merged PR #144: added `HelperContinuityStore`.
- Merged PR #145: added `no_progress_advisory`.
- Merged PR #146: added routing CLI input for caller-supplied environment reports.

## Work not completed

- No external portable-deployment D3 pilot was started.
- No portable installer, target-local adapter implementation, or external target `.maps/` initialization exists.
- 6.19 helper continuity does not auto-resume helpers and does not prove provider health.
- 6.20 no-progress detection is advisory only; it does not label incidents, kill/reassign workers, or drive recovery.
- 6.21 has only the first flow (`maps flow start`); review/recover/release/handoff flows remain unimplemented.
- 6.24 still lacks a production environment-report source, freshness/cache policy, and task-to-`EnvironmentSpec` association.
- H4/E4/6.5 validation tiers still lack a real production caller.

## Decisions and constraints

- Do not infer D3 target authority from any roadmap or example text. D3 needs explicit operator/target-owner selection and access.
- Keep 6.19/6.20 advisory/metadata-only until provider health, task authority, and remediation policy are explicitly designed.
- `maps flow start` must remain composition over existing guarded APIs, not a second workflow engine.
- Environment compatibility reports remain caller-supplied evidence. Missing reports preserve prior routing behavior.
- Only `CompatibilityState.INCOMPATIBLE` rejects on environment; `DRIFTED` and `UNKNOWN` do not.
- H4/E4 production validation wiring should be shaped before implementation because no obvious current composition root both owns an `EnvironmentSpec` and production `HarnessService` hook registration.

## Current blocker / risk

- Portable deployment is blocked on external target selection/access/authority.
- Validation-tier wiring risks accidental scope expansion if an agent invents a spec source, freshness rule, or hook composition root without evidence.
- The shared checkout at `/home/home/Projects/MAPS_Lean` was dirty during this work; feature work used isolated `/tmp` worktrees to avoid touching unrelated user changes.

## Struggles faced / improvements

- Example-target drift: Chain Shovel was treated as selected even though it was only an example. Improvement: task/roadmap docs should distinguish examples from operator decisions explicitly, and reviewers should search for active-plan target assumptions.
- Stale durable state: `state/CURRENT.md` was old and warned not to trust its own live claims. Improvement: update the durable handoff pointer after meaningful multi-PR sessions instead of relying on chat memory.
- Publication-policy friction: several reviewer evidence commits could not be pushed by subagents and had to be pushed by `/root`. Improvement: root should expect to validate/push evidence commits after review agents finish.
- Shell quoting issue: a PR body containing backticked command text was interpreted by the shell during `gh pr create`. Improvement: avoid shell-sensitive Markdown in double-quoted command strings; use single quotes or API patch.
- Optional LangGraph dependency: one CLI test initially required checkpointed routing and failed when optional LangGraph packages were absent. Improvement: tests for CLI parsing/wiring should patch the boundary unless the test is explicitly optional-dependency-gated.
- Review caught fail-closed gaps:
  - PR #144: malformed helper-continuity records could be treated as reusable.
  - PR #145: non-integer no-progress thresholds could raise instead of returning `UNKNOWN`.
  Improvement: for advisory/metadata features, include malformed-input tests from the start.

## Working state

- Changed/uncommitted paths: none in the merged feature worktrees at handoff time.
- Open PRs: none when checked after PR #146 merge.
- Last verification performed on clean `/tmp/maps-main-verify` at `origin/main`:
  - `python3 -m runtime.smoke` passed.
  - `python3 -m unittest tests.test_routing_cli tests.test_routing_policy tests.test_no_progress tests.test_bounded_helpers tests.test_flow_start -v` passed 46 tests.
- Known failing checks: none known on `main`.

## Next action

1. Shape H4/E4/6.5 validation-tier production-call-site work before implementation. Confirm the trusted composition root, `EnvironmentSpec` source, repo root, hook event, and failure behavior. If that boundary cannot be proven, write a design/decision note rather than wiring code.

## Do not redo / do not assume

- Do not redo PRs #142-#146.
- Do not assume an external pilot target exists.
- Do not mark 6.19, 6.20, 6.21, or 6.24 `DONE`; each has explicit remaining exit-gate gaps.
- Do not wire validation hooks into production by guessing where `EnvironmentSpec` should come from.
- Do not use chat transcript as durable project memory; update handoffs/checklist/current-state files.

## Evidence / paths

- `runtime/flow_start.py`
- `runtime/helpers/common.py`
- `runtime/no_progress.py`
- `runtime/routing/cli.py`
- `tests/test_flow_start.py`
- `tests/test_bounded_helpers.py`
- `tests/test_no_progress.py`
- `tests/test_routing_cli.py`
- `work/roadmaps/CAPABILITY_CHECKLIST.md`
- `work/roadmaps/agent-harness-capabilities/06-portable-deployment.md`
- `work/tasks/maps-flow-start-lifecycle.md`
- `work/tasks/helper-continuity-registry.md`
- `work/tasks/no-progress-advisory.md`
- `work/tasks/routing-environment-reports-cli.md`
