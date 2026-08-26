# Handoff: project reconciliation and Proof Phase

- From: repository archaeology / reconciliation pass
- To: next MAPS_Lean worker
- Task: [reconciliation maintenance branch](../../state/CURRENT.md)
- Status: `ACTIVE — reconciliation maintenance; architecture expansion frozen pending proof`
- Related durable records:
  - [Tenth-Seat review](../../playbook/TENTH_SEAT_REVIEW.md)
  - [Roadmap trajectory check](../../playbook/ROADMAP_TRAJECTORY_CHECK.md)
  - [Future Ideas Backlog](../../migration/FUTURE_IDEAS_BACKLOG.md)
  - [Capability checklist](../roadmaps/CAPABILITY_CHECKLIST.md)
  - [Portable deployment roadmap](../roadmaps/agent-harness-capabilities/06-portable-deployment.md)

## What is true now

- VERIFIED: baseline `main` before this reconciliation branch was
  `d22036bcebca3d7eb729c2b9dd70e82c229ac60a`, merging PR #172.
- VERIFIED: PR #171 is the one open implementation PR at this handoff. It is
  Skill-lifecycle durable storage Half 1 only; its own contract leaves Half 2
  authority wiring separate and does not mark SEC4/6.10 DONE.
- VERIFIED: PR #172 made resume-path validation production-invokable but
  deliberately advisory/inert for ordinary real runs because no production
  writer currently supplies run-bound environment evidence.
- VERIFIED: the Tenth-Seat protocol is an active playbook method. Trajectory
  checks #6 and #7 each found substantive issues, so a future clean check #8
  must evaluate the protocol's Trigger 2 before treating the result as settled.
- VERIFIED: repository archaeology found substantial information/status drift:
  old notes can look unfinished after later implementation, and accepted review
  findings can survive only inside review/PR prose unless dispositioned.
- VERIFIED: no open GitHub issues currently serve as a secondary backlog for
  these roadmap/reconciliation items.
- ASSUMED / UNKNOWN: no claim is made here that every historical artifact has
  been fully reconciled. Live code, current checklist evidence, and GitHub state
  still win over historical prose.

## Work completed

- Added a repo-wide rule that forward-relevant durable information must connect
  to its source/parent/successor/evidence and should link instead of duplicate.
- Connected `ROADMAP_TRAJECTORY_CHECK.md` back to the Tenth-Seat triggers.
- Tightened E/I guidance so promoted/rejected/superseded ideas preserve their
  later disposition through links.
- Updated core templates so decisions, AGI checks, and handoffs carry durable
  relationship context.
- Began current-state/documentation reconciliation without adding runtime
  capabilities.

## Work not completed

- External Proof Phase / D3 real-project pilot has not been run.
- PR #171 remains governed by its own review/merge process.
- Skill lifecycle Half 2 is not authorized by this handoff.
- Legacy deletion remains separately operator-gated.
- A full historical backlink retrofit is intentionally not being attempted.
- Branch cleanup and hcom fork-pin removal require their own evidence checks;
  neither should be inferred from this handoff.

## Decisions and constraints

- Freeze new major capability families until external comparative evidence
  demonstrates a concrete need.
- Preserve history; reconcile current meaning. Do not rewrite old observations
  to pretend later outcomes were known at capture time.
- Prefer standard relative Markdown links over copied rationale. Backlinks may
  be derived; do not create a second mutable graph/authority store.
- Tenth-Seat review remains rare and trigger-based, not a CI gate or permanent
  contrarian role.
- Use the existing D3 external-pilot concept as the first real proof vehicle
  rather than inventing a duplicate pilot framework.

## Current blocker / risk

- Main risk: navigation/status drift can cause a fresh worker either to miss a
  good deferred idea or to rediscover an already-implemented old design as new
  work.
- External proof remains blocked until a real target repository/task and the
  necessary operator authority/access are explicitly selected.

## Working state

- Reconciliation branch: `maintenance/reconcile-project-truth-20260826`
- Baseline main: `d22036bcebca3d7eb729c2b9dd70e82c229ac60a`
- Known active implementation PR: #171
- Known last merged implementation PR at baseline: #172

## Next action

1. Finish and independently review the reconciliation-only maintenance PR; then
   start the external Proof Phase/D3 pilot rather than opening another internal
   capability wave.

## Do not redo / do not assume

- Do not recreate an additional loose-ends database: MAPS already has future
  ideas, E/I, decisions, trajectory checks, handoffs, and the capability
  checklist. Reconcile these before adding another layer.
- Do not assume a dated `future task` note is still unfinished until checked
  against current code/checklist/merged PRs.
- Do not interpret `IN PROGRESS` as one homogeneous maturity state; distinguish
  design, implementation, tests, production reachability, real evidence input,
  and external proof when that distinction matters.
- Do not wire Skill Half 2, destructive-action enforcement, automatic recovery
  remediation, or other authority expansion merely to complete a roadmap shape.

## Evidence / paths

- [Agent operating contract](../../AGENTS.md)
- [Active playbook index](../../playbook/INDEX.md)
- [Tenth-Seat protocol](../../playbook/TENTH_SEAT_REVIEW.md)
- [Roadmap trajectory check](../../playbook/ROADMAP_TRAJECTORY_CHECK.md)
- [E/I](../../playbook/EMERGENCE.md)
- [Current state](../../state/CURRENT.md)
- [Capability checklist](../roadmaps/CAPABILITY_CHECKLIST.md)
- [Future Ideas Backlog](../../migration/FUTURE_IDEAS_BACKLOG.md)

## Continuation link

- Superseded by / next handoff: `none yet`

This handoff reports durable orientation only. Recover live PR/CI/task state via
`work/coordination/README.md` before acting.
