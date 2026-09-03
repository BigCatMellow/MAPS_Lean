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

Not promoted. Promotion is a deliberate decision made by a human or task-lifecycle process (see `playbook/TASK_LIFECYCLE.md`), not an automated step of this script.

## Disposition 2026-09-03 (Emergence pass, tuba)

**STALE.** Resolved. `runtime/recovery/production.py::run_recovery_tick` constructs a `RecoverySupervisor` and calls `tick()` since PR #165 (reachable as `maps recovery-tick`, piggybacked on `maps claim`). The observation was accurate for its date; the invocation gap it named is closed. Later chain: #258/#261 lineage bootstrap, #269/#276 adapter defect, #277 first `--enforce-canonical-run` pass. Kept as history; no re-open.
