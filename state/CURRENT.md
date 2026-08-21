# Current State

**This file is a durable orientation snapshot, not a live status board.** It
was last brought back into alignment with reality on 2026-08-17. Do not trust
a PR number, test count, or "current tranche" claim below without checking it
against live GitHub state. For the actual current PR/task/review queue, use
`work/coordination/README.md` and recover state live from GitHub as it
instructs — that is the authoritative live-state entry point, not this file.

## Latest coordination handoff

The latest compact multi-session handoff is
[`work/handoffs/2026-08-21-roadmap-progress-and-handoff.md`](../work/handoffs/2026-08-21-roadmap-progress-and-handoff.md).
Use it for durable orientation only, then recover live GitHub state per
`work/coordination/README.md` before acting on PRs, CI, or current blockers.

## Durable facts (unlikely to need per-PR updates)

- Current goal: the MAPS Lean migration's runtime replacement is complete and
  merged. The only remaining migration action is an explicit
  operator-approved deletion of top-level `legacy/` (not yet authorized — see
  "Remaining migration action" below).
- Original replacement-runtime promotion: PR #16 (squash commit
  `78791fca0d5cd0def5bae2c5b2eb9addcbf0770e`). Former stacked PRs #9-#15 are
  closed as superseded by PR #16 and remain only as historical review context.
  Substantial further work has landed on `main` since PR #16 — do not treat
  PR #16 as describing current `main`.
- `work/reviews/RUNTIME_INTEGRATION_REVIEW.md` records the original fresh
  adversarial integration review for PR #16. It was performed by the same
  assistant continuity that participated in implementation, so it is not
  represented as an independent model/human review.
- Independent verification is mechanical and GitHub-hosted: compile, Ruff,
  Bandit, dependency checks, regression tests, LangGraph/SQLite smoke,
  installer checks, and the active legacy-dependency gate, all required by
  branch protection on `main` (PR-only, required Runtime CI check, no
  force-push/delete — see issue #61 for the mechanical-independent-review gap
  that branch protection does not yet close).
- Release decision remains: Lean does **not** restore a universal
  `APPROVED -> RELEASED` state machine. Real deploy/destructive/external
  actions are explicit policy-gated tasks/actions.
- Historical Markdown/task/report files may still mention `legacy/`; they are
  provenance/safety records and are not execution dependencies. The curated
  preservation snapshots remain under `migration/` and are evidence, not
  runtime dependencies.

## Remaining migration action

**Only one migration action remains:** explicit operator-approved deletion of
 top-level `legacy/`.

Do not infer deletion authority from this status file. The deletion must be a
separate explicit operator instruction/change.
