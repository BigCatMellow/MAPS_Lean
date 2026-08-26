# Current State

**This file is a durable orientation snapshot, not a live status board.** It was
reconciled against `main` on 2026-08-26 at
`d22036bcebca3d7eb729c2b9dd70e82c229ac60a` before the reconciliation
maintenance branch began. Do not trust a PR number, CI result, or active-worker
claim here without recovering live state through
[`work/coordination/README.md`](../work/coordination/README.md).

## Latest coordination handoff

Use
[`work/handoffs/2026-08-26-project-reconciliation-and-proof-phase.md`](../work/handoffs/2026-08-26-project-reconciliation-and-proof-phase.md)
for the current durable project interpretation, then recover live GitHub state
before acting.

## Durable project direction

- MAPS_Lean is a working agent-control-plane prototype with explicit task
  authority, context/evidence boundaries, recovery, review, Skills foundations,
  environment evidence, and evaluation machinery.
- The next project phase is **reconciliation + external proof**, not another
  broad internal capability wave. Existing mechanisms should be exercised on a
  real external task and measured for outcome benefit and control-plane cost.
- Use the existing portable-deployment D3 concept as the first real external
  proof vehicle. Do not count synthetic/self-only validation as final proof.
- New major capability families are frozen unless real testing exposes a
  concrete failure the existing mechanisms cannot address.
- Historical notes preserve provenance, not current status. Reconcile any dated
  `future task`, `not implemented`, or `no production caller` statement against
  current code, the capability checklist, and merged PR history before treating
  it as an active gap.

## Durable information rules

- [AGENTS.md](../AGENTS.md) is the active repository-wide operating contract.
- Keep forward-relevant durable artifacts connected to the source, task,
  decision, evidence, successor, implementation, or other context that gives
  them meaning. Prefer links over repeated explanation.
- Preserve an old observation when its disposition changes; link forward to the
  implementing, rejecting, superseding, or resolving artifact instead of
  rewriting history.
- The [Tenth-Seat protocol](../playbook/TENTH_SEAT_REVIEW.md) is an active,
  narrow review method. Its triggers are now also referenced by
  [roadmap trajectory checks](../playbook/ROADMAP_TRAJECTORY_CHECK.md).

## Current bounded work at this reconciliation point

- PR #171 was the one open implementation PR at the 2026-08-26 baseline. It is
  Skill-lifecycle durable storage Half 1; Half 2 authority wiring is separate
  future work and is not authorized merely because Half 1 exists.
- PR #172 is merged. It made resume-path validation production-invokable but
  intentionally advisory and normally inert because no production writer yet
  supplies run-bound environment evidence.
- Review/deferred findings that are not blockers still require an explicit
  disposition so they do not survive only inside PR/review prose.

## Remaining migration action

Top-level `legacy/` deletion remains separately operator-gated. Do not infer
deletion authority from this status file, cleanup goals, or the Proof Phase.

## What this file does not authorize

This snapshot does not grant permission to:

- merge or close a PR;
- delete `legacy/` or stale branches;
- wire Skill lifecycle Half 2;
- add automatic remediation/reassignment;
- add a new memory/knowledge-graph service;
- perform destructive/external actions;
- or change the roadmap merely to match historical prose.

Recover live evidence, follow the relevant task/decision authority, and prefer
the smallest mechanism that addresses an observed failure.
