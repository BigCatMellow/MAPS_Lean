# INSIGHT-102296b5: maps recovery-tick --enforce-canonical-run may be structurally unexercisable under the current high-touch operating mode

- Kind: `insight`
- Date: `2026-09-03`
- ID: `INSIGHT-102296b5`

## Observation

RnS / canonical-run enforcement only produces a routable resume_denied when a genuinely-live session silently stalls and its lease expires unattended. The project's actual operating mode is the opposite: coordinator seats, the gule merge-runner, limit_watcher, hcom presence tracking, and active babysitting mean sessions rarely stall unattended long enough. #277's pass had to use a synthetic bind-session precisely because no real stalled session was available.

## Source / context

work/notes/2026-09-03-item5-enforced-pass-results.md (synthetic --binding nava-worker-1); work/notes/2026-09-02-ask1-control-plane-runbook.md section 8; session-26 handoff (Mode A, gule seat)

## Potential value

Surfaces a tension between two parts of the program: the harness-enforcement roadmap assumes unattended stalls exist to catch, while the multi-agent operating style is designed to prevent them. Either the feature needs a deliberate test harness that manufactures a real stall, or the roadmap should acknowledge the feature is insurance for a failure mode the current mode makes rare.

## Smallest next test

Scope a controlled exercise: launch a real throwaway hcom session bound via maps run bind-session, let its lease expire with no babysitting, then run the enforced tick and observe whether a real routable resume_denied results. That is the missing evidence for the 7-row cluster.

## Promotion

Not promoted. Promotion is a deliberate decision made by a human or task-lifecycle process (see `playbook/TASK_LIFECYCLE.md`), not an automated step of this script.
