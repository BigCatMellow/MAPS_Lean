# Roadmap trajectory check #5 - after D0 audit and CI fixture repair

Fifth pass after PR #135 fixed the stale context-builder fixtures and PR #134
completed Portable Deployment D0.

## 1. Re-verified against real `main`

- `origin/main` includes PR #135 (`a123863`) and PR #134 (`46d3c5d`).
- PR #134 completed D0 and preserved the evidence note at
  `work/notes/2026-08-20-portable-deployment-d0-portability-audit.md`.
- `work/roadmaps/CAPABILITY_CHECKLIST.md` marks D0 `DONE`, D1 `NOT STARTED`,
  and D2a/D2b/D2c `NOT STARTED` before this D2a branch.
- `work/notes/2026-08-19-portable-deployment-operator-decisions.md` still
  supplies the five v1 decisions that unblock D2a.

## 2. What changed the picture

D0 found the install/smoke surface is not target-repo-portable yet and that D2a
should not depend on importing `TaskStore` into a target repo. That strengthens
the file-convention-only direction rather than changing it.

The D0 audit also makes clear that D1 and D2b need explicit root/interface
boundaries. D2a can still proceed first because it defines the target-owned
Markdown state shape that those later designs will target.

## 3. Decision: continue, select D2a

Continue the portable deployment lane and complete D2a now.

Selected work: `D2a-file-convention-design`, producing a MAPS_Lean-side design
note and draft target-repo templates for `.maps/` tasks, reviews, and roadmap
state.

Not selected:

- D1: still needed, but its installer-targeting design should consume the D0
  audit and D2a target file shape.
- D2b: depends on D2a.
- D2c/D3: depend on D2a/D2b and require Chain Shovel-specific planning/access.
- Runtime implementation: outside Roadmap 06's current design/planning boundary.
