# Helper Note: helper-clearfront-skeleton-01

- hcom name: vida (batch 2e9c412a, launched 2026-07-16)
- Spawned by: claude-lab-gome
- Owner (accountable for integrating/discarding output): claude-lab-gome
- Model: Fable (per operator directive hcom #311 — Claude orchestrates with Fable)
- Task: TASK-208 — ClearFront extract CSS+data module, establish multi-file skeleton
- Scope: `Projects/ClearFront/app/index.html`, `Projects/ClearFront/app/styles/clearfront.css`,
  `Projects/ClearFront/app/js/data.js`, `Projects/ClearFront/artifacts/tests/task-208-skeleton-parity.md`
- Status: TASK-214 RELEASED (found and disclosed the `renderCombatReport`
  ctx gap mid-implementation; approved and folded into DEC-CF-005).
  Dispatched to TASK-215 (`js/render.js`) but hit a Fable usage-credits
  wall before starting ("Usage credits are required for this model" —
  distinct from a Sonnet session-limit reset, `/usage` showed no
  session limit reached). Escalated to bigboss (hcom #~1370s); operator
  directed doing TASK-215 directly instead of waiting. **Stopped**
  2026-07-17 (`hcom kill helper-clearfront-skeleton-01-vida`). Its
  accumulated context (window.CF/ctx pattern, 2 self-caught scoping
  gaps across 3 released tasks) is preserved in DEC-CF-004/005/006 and
  the released task records, so nothing is lost even though the helper
  itself is gone. Do not resume this helper for ClearFront work without
  confirming Fable credits are available again.
- What it learned/produced: clean split of CSS + 11 data values onto
  window.CF; flagged two scope items proactively (app/assets copy needed
  for relative portrait paths; HERO_NAMES declared mid-engine at baseline
  line 2914, moved per DEC-CF-003). Reusable CDP harness checked in at
  Projects/ClearFront/artifacts/tests/task208-cdp-smoke.mjs.

## Context the helper needs (already established, do not re-derive)

- `Projects/ClearFront/baseline/index.html` is the parity-proven source of
  truth to split (TASK-207, byte-for-byte + functionally verified against
  the original bundle).
- Module boundaries and the "why" are already decided:
  `Projects/ClearFront/shared/decisions.md` DEC-CF-002 (plain global
  `<script src>` files sharing a `window.CF` namespace — NOT ES modules,
  NOT a build step, must keep working via plain `file://` open) and
  DEC-CF-003 (exact line-range/function boundaries).
  `Projects/ClearFront/artifacts/planning/clearfront-module-map-2026-07-16.md`
  has the full function inventory.
- TASK-208 is deliberately the lowest-risk first slice: CSS (pure,
  mechanical) + data (CARD_LIBRARY/decklists/constants, zero function
  bodies). Engine/render/input stay inline in `app/index.html` for now —
  do not move them in this task.
- Full task record: `MAP_System/tasks/TASK-208.json` (acceptance criteria,
  output paths).
- Parity method to follow (same one used for TASK-207, see
  `Projects/ClearFront/artifacts/tests/task-extraction-parity.md`):
  headless Chromium screenshot compared against `baseline/index.html` at
  the champion-select screen, plus a CDP interaction check (click a
  champion, verify turn-1 state, zero console errors/exceptions).

## What's already learned (don't rediscover)

- TASK-207's review (`Projects/ClearFront/artifacts/reviews/task207-review-lilo.md`)
  found real bugs from writing files based on parsed/generated content
  without validating destination paths — be careful with any file-writing
  logic and don't assume "it rendered once" is sufficient proof.
- The original game is a single vanilla-JS IIFE, no React/Babel/build
  tooling — keep it that way.
