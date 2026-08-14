# EXP-0005 Recovery Orientation Treatment

Scenario: recover `TASK-227` without reopening `TASK-220`.

## Current state

- `TASK-227` is `CHANGES_REQUESTED` and owned by `claude-lab-gome`.
- `TASK-220` is `RELEASED`; do not reopen it.

## Required order of work

> Read TASK-227 review and handoff before mutating task state or plan output.

This is the first required action; `rework` is not the first action.

Later, only when ready to edit, the owner follows the normal TASK-227 rework
path. After rework, resolve **all five REQUIRED review findings** before
resubmission. Do not edit the plan before rework or create replacement work.
Exact CLI flags can be checked when executing that later action.

## Authority and helper limits

- A core agent may revise the task plan or make a proposal.
- Command-center alone approves an `AUTHORITY` or `POLICY` decision; neither a
  core proposal nor a helper recommendation is binding.
- A helper, if used, is visible, temporary, scoped, durably recorded, and
  core-owned. It does not take task ownership, bypass approval, or directly
  mutate core truth.

## Availability uncertainty

Check live hcom before relying on durable status. At the frozen capture,
`claude-lab-gome` was live/listening while the durable record said
`standby` / `out_of_tokens` through `2026-07-18T05:05:00-04:00`. This conflict
does not establish provider capacity; capacity remains unresolved.

## Canonical pointers

| Item | Canonical pointer |
|---|---|
| TASK-227 state and owner | `MAP_System/tasks/TASK-227.json` |
| TASK-220 released state | `MAP_System/tasks/TASK-220.json` |
| First read; five REQUIRED findings; rework/resubmission | `MAP_System/artifacts/reviews/task227-review-lilo.md`; `MAP_System/handoffs/HANDOFF-20260718-system-improvement-kickoff-to-claude.md` |
| Authority boundary | `MAP_System/DECISION_AUTHORITY_SYSTEM.md`; TASK-227 review |
| Helper boundary | `MAP_System/AGENTS.md`; handoff guardrails |
| Live/durable availability conflict | `MAP_System/agents/README.md`; `MAP_System/agents/status.json`; captured hcom output in `MAP_System/artifacts/experiments/orientation-manifest-refined-rubric-control-2026-07-18.md` |

## Size measurement

`wc -w -c MAP_System/artifacts/experiments/orientation-manifest-refined-treatment-2026-07-18.md`:

```text
0312 2619 MAP_System/artifacts/experiments/orientation-manifest-refined-treatment-2026-07-18.md
```

Size-threshold result: `2619` bytes is at most `22,216` bytes, so it meets the
predeclared at-least-50%-fewer-than-`44,432`-byte control threshold. This is a
measurement only, not a rubric or production decision.
