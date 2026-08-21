# Roadmap trajectory check #4 - arc: PRs #128-#132 + session handoffs

Fourth pass after PRs #128-#132 landed and before selecting new self-directed work.

## 1. Re-verified against real `main` (`886090b`)

- `gh pr list --state open` returned no open PRs for `BigCatMellow/MAPS_Lean`.
- `gh pr view 131` showed PR #131 merged with `test` and `review-evidence` successful.
- `git log --oneline --max-count=8` shows PRs #128, #129, #130, #132, and #131 merged after trajectory check #3.
- `work/roadmaps/CAPABILITY_CHECKLIST.md` now includes the portable deployment section and marks D0-D6 `NOT STARTED`.
- `work/notes/2026-08-19-portable-deployment-operator-decisions.md` records the five operator decisions for portable deployment v1. Its earlier example-target language was corrected on 2026-08-21; no pilot target is selected.

## 2. What changed the picture

- Portable deployment is now a real roadmap lane, not just an open design question. PR #128 added Roadmap 06; PR #129 resolved the five architecture questions as: file-convention-only v1, sibling-clone + lightweight adapter, best-effort review discipline, stack-agnostic scope, and target-project state committed in that target repo.
- Session 2 handoff says D2a/D2b/D2c are unblocked and ready. The durable checklist still marks D0 and D1 `NOT STARTED`, and Roadmap 06 still defines D0/D1 as Phase 0 foundation with D1 depending on D0.
- PR #130 and PR #131 progressed 6.27 and 6.24 respectively, but both remain `IN PROGRESS` because their new primitives are not wired into consuming paths.
- PR #132 was a docs/navigation fix and does not materially change roadmap priority.

## 3. Decision: continue on portable deployment, start with D0

Decision: continue, no pivot.

Rationale:

- D0 traces directly to `CAPABILITY_CHECKLIST.md` and Roadmap 06.
- D0 is the first Phase 0 item and D1 explicitly depends on it.
- D2a/D2b/D2c are unblocked by operator decisions, but starting them before the D0 audit would skip the roadmap's own stated foundation check.
- D0 is low-risk, docs-only research with no external-project access and no runtime changes.

Selected work: `D0-portability-audit`, producing a written audit of the `scripts/install_maps.sh` / `runtime.smoke` surface and updating D0 status only.

Not selected:

- D1: depends on D0.
- D2a/D2b/D2c: unblocked, but better sequenced after D0/D1 or at least after D0.
- D3 pilot: blocked on D2a-D2c, explicit target/task selection, and external repo access/authority.
- Existing runtime lanes 6.19/6.20/6.21/6.25: still `TRIGGERED` or otherwise not evidenced as triggered.
