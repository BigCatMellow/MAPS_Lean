# MAPS_L

MAPS_L is a provider-neutral operating system around capable AI workers. It
combines task truth, bounded authority, orchestration, reusable methods,
verification, recovery, and durable evidence. It does not replace agent
judgment, and it is not tied to one model, provider, terminal, or user
interface.

This Wiki is the **orientation surface for a fresh agent** and an explanation
layer. It is **not an authority store** or a source of live task state. For work
in this repository, current
[`AGENTS.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/AGENTS.md),
approved roadmap/task scope, runtime state, merged code/tests, and current
GitHub evidence take precedence.

## Start here

- New to the system: [[What MAPS_L Is]]
- Want a practical example: [[First Task Walkthrough]]
- Need current development status: [[Development]]
- Need to know whether a capability is actually complete: [[Capability Status]]
- Working in this repository: follow
  [`docs/FIRST_RUN.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/docs/FIRST_RUN.md)

The normal repository reading budget is:

```text
target authority + approved roadmap/task + one relevant MAPS_L method
```

Do not read the whole Wiki or repository as a prerequisite.

## The system in one view

```text
human owner approves objective and permission envelope
                         |
                         v
orchestration operator recovers truth and selects bounded work
                         |
             acts or dispatches agent slots
                         |
                         v
              evidence returns to operator
                         |
       reconcile -> verify/review -> continue or stop
```

The operator owns the parent outcome. A worker owns only its bounded task.
**Delegation transfers execution, never ownership.** A finished child task is a
reconciliation point, not proof that the larger project is complete.

## Operating depths

Use only as much MAPS_L as the work needs.

| Depth | Appropriate use | Typical mechanisms |
| --- | --- | --- |
| **Method-only** | Small or single-agent work | objective, DONE condition, boundary, verification, one playbook method |
| **Orchestrated** | Multi-task, multi-agent, or long-lived work | roadmap, bounded workers, task records, handoffs, independent review |
| **Runtime-backed** | Concurrent or resumable work needs machine-enforced state | SQLite, LangGraph, hcom, RnS recovery, run binding, Hooks |

The existence of a runtime feature is not a reason to use it. Choose the
smallest mechanism that removes a real coordination, authority, recovery, or
verification failure mode.

## Core pages

- [[What MAPS_L Is]] — purpose, concepts, and responsibility boundaries
- [[Task, Run and Flow Lifecycle]] — task states, immutable runs, and every
  current `maps flow` verb
- [[Execution, Recovery and Worktrees]] — session lineage, guarded recovery,
  lease expiry, and Git worktree enforcement
- [[Context, Memory, Skills and Capabilities]] — context plans, trust classes,
  progressive Skill loading, manifests, and known enforcement limits
- [[Review, Authority and Merge Safety]] — independent review, operators,
  release checks, and the mandatory merge route
- [[Emergence, Triage and Learning]] — cross-root synthesis, improvement
  capture, recurrence handling, and frozen regression cases
- [[Operator and Developer Tools]] — installation, tests, housekeeping,
  Spiderweb, and common operator surfaces

## Rules that prevent common failures

- Capability is not permission.
- Evidence outranks prose, summaries, and confidence.
- SQLite owns mutable task truth; Markdown records human-readable intent and
  evidence. Do not maintain a second hand-edited task database.
- LangGraph recommends routes; it does not create scope or authority.
- hcom transports messages and controls sessions; it does not own task truth.
- RnS recovers known active work; it does not invent or reassign work.
- A context plan assembles what may be read. It is not the same as delivering
  that context to a provider session.
- An open PR or proposal is not current behavior.
- Production code may exist while a capability remains **IN PROGRESS** because
  its required real-world exercise or evidence has not occurred.

## Optional `/pilot` entry point

The repository includes a thin Agent Skill at
[`/.claude/skills/pilot/SKILL.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/.claude/skills/pilot/SKILL.md).
When a client discovers it, `/pilot` invokes the MAPS_L operating method. It is
not another authority source and does not import MAPS_Lean-specific permission
into the target project.
