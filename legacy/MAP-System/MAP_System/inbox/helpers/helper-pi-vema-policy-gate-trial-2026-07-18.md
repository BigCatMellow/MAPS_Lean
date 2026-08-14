# Pi Trial Assignment — Vema Coder: Policy-Gate False-Positive Analysis

- status: complete
- owner: codex-lab-lilo
- helper: vema
- provider: pi / qwen2.5-coder:7b-16k
- created_at: 2026-07-18
- scope: read-only analysis and one bounded durable proposal

## Orientation and communication

Work from `/home/mellow/Projects/MultiAgentProject/Source`. Read `AGENTS.md`
and `MAP_System/AGENTS.md` first. Communicate with other agents only through
`hcom`; use `--name vema` on every hcom command. Send routine completion to
`@codex-lab-lilo` with `--intent inform`. Do not use `request` unless an actual
operator decision/blocker is needed. Do not spawn agents, claim tasks, or make
UI, task-state, policy, database, shared-state, installer, or external-file
changes.

## Bounded purpose

Analyze one reproducible friction point: TASK-235 is explicitly read-only but
the pre-dispatch policy flags `REQUIRE_CORE_DESTRUCTIVE_APPROVAL` because its
text contains the negated phrase “restart services.” Determine the smallest
safe way to distinguish a prohibited action from an intended action in a task
description without weakening real destructive-action protection.

Read only:

- `MAP_System/scripts/pre_dispatch_policy.py`
- `MAP_System/db/claims.py`
- `MAP_System/tests/test_pre_dispatch_policy.py`
- `MAP_System/tasks/TASK-235.json`
- `MAP_System/DESTRUCTIVE_ACTION_POLICY.md`

Write a concise proposal at:

- `MAP_System/artifacts/experiments/pi-vema-policy-gate-analysis-2026-07-18.md`

Include: observed cause with exact evidence; up to two minimal options; test
cases that must continue to block; a recommended *proposal only*. Do not alter
code/tests. Notify lilo through hcom `inform` with the output path and whether
you completed successfully.

## Outcome

Completed at `2026-07-18T14:23:33Z` as a **degraded trial**. Vema received
the assignment and HCOM re-instruction, but its first completion payload was
`[None]` and it reported that it could not create the authorized artifact. Its
HCOM-only fallback named the general negation cause but omitted the required
must-still-block tests and proposed broad policy/task changes rather than a
minimal safe mechanism. Relay response works; durable scoped-output completion
and review-quality coding analysis are not yet demonstrated.
