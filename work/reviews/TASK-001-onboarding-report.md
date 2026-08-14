# TASK-001 first-run onboarding report

- Task: [TASK-001 first-run onboarding simulation](../tasks/TASK-001-first-run-onboarding-simulation.md)
- Owner: lean-onboarding-helper
- Status: owner-complete; independent review remains required by the task
- Scope: active Lean documentation only. No legacy source was read.

## Result

The active route was sufficient to establish the repository's operating
constraints, current shared context, proportional verification, continuation
practice, and the retained-versus-optional architecture. It was not quite a
single, explicit first-run path: a capable agent can orient safely, but must
infer where the concise control-plane explanation lives and what to do with a
current-state entry that is unrelated to its assigned task.

## Active files read, in order

1. `AGENTS.md` — root operating contract; selected first because the README
   explicitly names it as the first start-here step.
2. `README.md` — repository purpose, startup route, layout, and the top-level
   retained-control-plane summary.
3. `work/tasks/TASK-001-first-run-onboarding-simulation.md` — assigned scope,
   write boundary, acceptance criteria, and verification requirements.
4. `state/CURRENT.md` — shared continuation context, as directed by the
   README; it established the current goal and showed that this task must not
   alter it.
5. `playbook/INDEX.md` — method selector required by `AGENTS.md` for work
   beyond a small edit; it also gives a concise control-plane description.
6. `docs/CHECKS_AND_BALANCES.md` — low-risk owner-check requirement and the
   task's independent-review expectation.
7. `templates/handoff.md` — required structure for the durable handoff.
8. `docs/CONTEXT.md` — selected from the Index's continuation route; it
   confirms that a future agent should work from task, current state, and
   handoff rather than chat history.
9. `playbook/TASK_LIFECYCLE.md` — selected to verify that the supplied task
   record has a usable owner, boundaries, criteria, and output paths.
10. `playbook/CONTROL_PLANE.md` — selected after the Index identified the
    retained plane, to obtain the authoritative active explanation of its
    components.
11. `docs/WORKFLOW.md` — selected to confirm the ordinary scoped-task to
    proportional-review flow and handoff trigger.
12. `playbook/SOURCE_CATALOG.md` — selected to distinguish active condensed
    practice from retained reference-only implementation.

## Control-plane understanding

- **SQLite** is the canonical mutable task ledger: atomic claims prevent two
  agents from winning the same claim, and it records lifecycle state, leases,
  submissions, independent-review separation, and LangGraph checkpoints.
  Markdown remains the human-readable task/evidence/decision layer; it must
  not become a competing manual copy of mutable task truth.
- **LangGraph** is a read-first dispatcher. From task/dependency state,
  policy, availability, helper capacity, and approval gates, it recommends an
  operational route. It neither sets product priorities nor acts in place of
  an accountable agent's claim, review, or escalation.
- **RnS (Rise & Shine)** is the deterministic recovery supervisor for
  provider-limit and stale-session incidents. It relies on current durable
  handoffs, resumes or nudges at the appropriate time, and backs off; it does
  not claim, reassign, or invent work.
- **hcom** is the current cross-provider message and session-control transport.
  RnS presently uses it for session inspection, bounded transcript access,
  resume, and message injection. It carries no authority and does not own task
  truth.
- **WezTerm Command Center** is optional terminal/pane presentation. It may be
  replaced or omitted without removing SQLite, LangGraph, RnS, or hcom; hcom
  would need a tested replacement adapter before removal from the current RnS
  implementation.

## Onboarding friction and smallest fixes

| Path | Observed friction | Smallest proposed fix |
| --- | --- | --- |
| `README.md` | The numbered start route says to pick a playbook method, but it does not link to the one-page control-plane explanation. A first-time agent must enumerate files or rely on the abbreviated README summary. | Add a `playbook/CONTROL_PLANE.md` link next to the retained-control-plane summary or as a numbered optional orientation step. |
| `README.md` and `state/CURRENT.md` | The instruction to read current state is conditional on “continuing shared work,” but gives no cue for how a newly assigned task should interpret an unrelated active goal. | Add one sentence: read it for constraints only; do not modify or take over an unrelated active task. |
| `playbook/INDEX.md` | `CONTROL_PLANE.md` is not listed in the “Need / Use” method table even though it is the detailed active source for the components the Index summarizes. | Add a `Understand retained runtime controls` row linking to `CONTROL_PLANE.md`. |
| `README.md` / `playbook/INDEX.md` | hcom is described as currently required by RnS, but the active path provides no operational-status, availability, or safe-usage entry point. This leaves a first-time agent unable to tell whether hcom is applicable in its environment. | Add a short availability note and link to the future active-runtime manifest once Phase 0 creates it. |

## Smallest next action

Perform the Phase 0 action already named in `state/CURRENT.md`: create a
read-only active-runtime manifest plus WezTerm-coupling inventory. That
manifest can supply the missing canonical operational entry point without
changing this low-risk onboarding task's scope.

## Owner verification

- Only the two paths allowed by TASK-001 were created.
- No legacy, runtime, configuration, installer, database, launcher, or active
  guidance files were modified.
- The report covers the required read order, component roles, four concrete
  friction points with path-specific fixes, and a smallest next action.
