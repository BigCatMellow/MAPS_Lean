# MAP Recovery Phase 2 Status (TASK-309)

- regenerated: 2026-08-04, by claude-lab-luzo (coordinator)
- reason: the prior version of this file could not be located (no git
  history for this path; it was evidently always an untracked/local-only
  working file). Regenerated from current canonical task state rather than
  left missing, per TASK-309's own acceptance criteria.
- authority revision at time of writing: `sha256:552d9dcedd4ae5e24d677a1c1c881658ad0e3ff14e3f0a61e2ca12c99ab3e8de`, freshness FRESH

## Workstream status

| Task | Title | Status | Owner | Reviewer(s) | Evidence |
|---|---|---|---|---|---|
| TASK-310 | WS-1: Make MAP authority freshness truthful | RELEASED | zeno | codex-lab-lime | `artifacts/reviews/task310-independent-review-codex-lab-lime.md`, `task310-rereview-codex-lab-lime.md`, `task310-final-rereview-codex-lab-lime.md` |
| TASK-313 | WS-1 prerequisite: resolve runner/Command Center path ownership | APPROVED | codex-lab-vumo | mimi | `artifacts/reviews/task313-independent-review-mimi.md` |
| TASK-314 | WS-1: Command Center authority-freshness display (local/template) | RELEASED | rotation-replacement-mimi-koda | claude-lab-mika, ws1-review2-muvi | `artifacts/reviews/task314-independent-review-claude-lab-mika.md`, `task314-independent-review-ws1-review2-muvi.md` |
| TASK-311 | WS-2: Resolve active MAP output ownership collisions | APPROVED | rotation-replacement-kite-veni | mimi | `artifacts/reviews/task311-independent-review-mimi.md` |
| TASK-312 | WS-3: Restore one reproducible green MAP baseline | RELEASED | zeno | codex-lab-lime | `artifacts/reviews/task312-independent-review-codex-lab-lime.md` |
| TASK-306 | Version/align Biggie Command Center Lab with Smalls | RETIRED (split, DEC-040) | claude-lab-nene | muza | `artifacts/reviews/task306-review-muza.md`; superseded by TASK-314 (local half) and a deferred WS-6 task (Smalls cross-PC half, not yet created) |
| TASK-307 | Revalidate/review/deploy the damo-nivo map-authority gateway patch | APPROVED | claude-lab-nene | codex-lab-vumo | `artifacts/reviews/task307-smalls-predeploy-review-codex-lab-vumo.md`, `task307-smalls-rereview-codex-lab-vumo.md`, `task307-smalls-rereview3-codex-lab-vumo.md` |
| TASK-308 | Deploy and live-verify the reviewed TASK-307 gateway patch | APPROVED | claude-lab-nene | (see TASK-307 review chain) | `artifacts/operations/gateway-rotation-ops-deployment-2026-07-29.md` |
| TASK-315 | Converge Biggie and Smalls source through reviewed GitHub checkpoint | RELEASED | zeno | helper-review-task315-polo, codex-lab-nido | `artifacts/reviews/task315-final-review-helper-review-task315-polo.md`, `task315-pr-review-codex-lab-nido.md`; `artifacts/operations/biggie-smalls-source-convergence-20260801.md` |
| TASK-316 | Fix map-authority mirror-sync self-block from limit-watcher | APPROVED | helper-fix-authority-316-bume | helper-review-task316-317-zinu | `artifacts/reviews/task316-independent-review-zinu.md` |
| TASK-317 | Add map_task.py `describe` verb (NEEDS_SHAPING promotion) | APPROVED | helper-fix-authority-316-bume | helper-review-task316-317-zinu | `artifacts/reviews/task316-317-independent-review-zinu.md` |

## Gate outcome

WS-1 (authority freshness truthful) and WS-2 (output ownership collisions)
and WS-3 (reproducible green baseline) are each RELEASED/APPROVED per the
table above — the sequencing gate TASK-309 exists to enforce (WS-1/2/3
complete before WS-4+) is satisfied as of this writing.

TASK-316/317 (2026-08-03/04) were an unplanned but necessary detour: a
regression in TASK-310's own writer-service check (found live, not during
TASK-310's original review) was permanently blocking mirror sync
system-wide. Root-caused, fixed, independently reviewed, and deployed to
both Biggie and Smalls with checksum verification. Not part of the original
WS-1/2/3 plan, but blocking to all of it, so treated as in-sequence.

## Known open items (not gating WS-4+, but unresolved)

- **TASK-296** (docs-only maintenance, priority 3): stale lease,
  claude-lab-dodo, expired since 2026-08-01, never reconciled.
  `recover-orphan` doesn't apply (claimant field isn't null); proper fix is
  `expire_leases()` run from Smalls (the authority host), not yet done.
- **Code-sync timers**: both Biggie and Smalls now run
  `map-code-sync.timer` (fast-forward from `origin/main` every 5 minutes,
  see `artifacts/operations/code-sync-timer-setup-2026-08-03.md`) so
  reviewed fixes stop getting stranded on one checkout. Smalls' first sync
  attempt was refused by git (three untracked local files collided with
  the incoming fast-forward: two live-regenerated task-mirror JSON files,
  one already-identical test file) -- verified safe to clear, but the
  actual removal is blocked by the harness's own permission classifier on
  this session (remote file deletion), unresolved as of this writing.
- **hcom relay/cross-device presence**: still broken (Smalls hasn't been
  "seen" by the relay in many hours). A self-hosted local-LAN broker was
  attempted and dead-ended (hcom's relay client only trusts real
  publicly-issued CA certificates, not a private CA, even when installed
  in the OS trust store) -- fully torn down afterward. SSH now provides
  real bidirectional Biggie<->Smalls shell/file access as the practical
  substitute; native hcom cross-device visibility would need a real
  domain + publicly-trusted certificate to fix properly.

## Authority

Canonical lifecycle state lives in Smalls' `map.db`, reached via the
sanctioned `map-authority` gateway from Biggie. This file is a snapshot,
not a source of truth -- re-run `map-authority route` / `task show` for
current state.
