# KICK-01 v2 Architecture Confirmation — Moku

- Status: `confirmation only`
- Scenario: `KICK-01` / `TASK-233`
- Basis: scenario §2a and §10; `kickoff-architecture-contribution-moku-2026-07-18.md`

## Confirmation

- **confirm** — Read failures must render as source errors/unknown, not trigger
  repair or inference. This preserves v1's read-only boundary.
- **confirm** — Process-bound presence is live evidence; degraded fallback
  requires a weaker label. This refines presentation, not v1's four sources.
- **confirm** — Unmatched identities must remain explicit/unknown. This
  confirms v1's essential join-key test and adds no matching rule.
- **confirm** — Template inspectability does not prove live deployment. This
  confirms v1's deployable-source-parity stop condition.
- **confirm** — Missing/malformed/stale event history cannot prove liveness or
  completion. This confirms v1's historical-action boundary.
- **confirm** — hcom, durable-board, and claim identifiers need not align.
  This confirms v1's identity-risk fixture.
- **confirm** — TASK-227 rework and owner remain admission constraints. This
  changes neither ownership nor the evidence-only scope.

The later brief remains deferred for the same evidence-backed reasons:
deployment-source parity and TASK-227 rework are unresolved. Section 10's
degraded-presence, source-failure, join-key, deployment-verification, and
independent-review requirements refine rather than contradict v1. No new
policy, task, implementation, or shared-state action follows.
