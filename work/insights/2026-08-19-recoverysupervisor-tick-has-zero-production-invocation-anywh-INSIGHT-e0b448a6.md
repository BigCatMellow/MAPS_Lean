# INSIGHT-e0b448a6: RecoverySupervisor.tick() has zero production invocation anywhere

- Kind: `insight`
- Date: `2026-08-19`
- ID: `INSIGHT-e0b448a6`

## Observation

grep -rln 'RecoverySupervisor(' runtime/ --include=*.py and grep for '.tick(' in runtime/cli.py and scripts/*.py both return zero production hits -- RecoverySupervisor is exercised only by tests/test_recovery_supervisor.py. This means the entire RnS module (not just its harness-layer connection) has no real trigger loop: no cron, no CLI subcommand, no daemon calls tick() periodically in production. Session #124's shadow-mode harness-resume observation, once wired with a real harness_service, still cannot accumulate real data because nothing ever calls tick() outside tests in the first place.

## Source / context

This session (2026-08-19), while scoping a follow-up to PR #124 (shadow-mode RnS observation). Confirmed via direct grep, not inferred.

## Potential value

Explains why RnS's roadmap-adjacent phases (E5, and now the harness-shadow-observation data-accumulation plan) can't progress on real evidence yet -- there's no real invocation path to generate that evidence from. Building a new invocation loop would be a new always-on daemon, which work/roadmaps/00-MASTER-MAPS-CAPABILITY-ROADMAP.md section 7's explicit non-goals list forbids by default ('a large maps daemon', 'always-on process-police/discovery agents') without a clear trigger/need. This is a genuine architecture gap worth the next ROADMAP_TRAJECTORY_CHECK.md pass considering, not something to unilaterally build.

## Smallest next test

At the next trajectory check, decide whether RnS's invocation gap needs its own design note (mirroring 2026-08-19-harness-production-wiring-gap.md's approach) or stays deliberately out of scope until an operator-driven trigger (e.g. a real incident where a stopped session went unrecovered) makes it material.

## Promotion

Not promoted at capture time. Promotion is a deliberate decision made by a human or task-lifecycle process (see `playbook/TASK_LIFECYCLE.md`), not an automated step of this script.

## Current disposition — 2026-08-26

`PARTIALLY RESOLVED / HISTORICAL OBSERVATION`

The original zero-production-invocation claim was true when recorded but is no
longer current. Later work added an explicit production composition and CLI
invocation path for one-shot recovery ticks, including the advisory resume-path
validation integration merged in PR #172.

Related current artifacts:

- [RnS production trigger-loop design](../notes/2026-08-24-rns-production-trigger-loop-design.md)
- [RnS validation-tier hook-in design](../notes/2026-08-25-rns-validation-tier-hookin-design.md)
- [current reconciliation handoff](../handoffs/2026-08-26-project-reconciliation-and-proof-phase.md)

The remaining question is narrower: whether real production worker/session
bindings and evidence sources are sufficient for useful recovery behavior, and
whether any always-on trigger is actually needed. Do not rediscover this old
"zero callers" statement as a reason to build a daemon.
