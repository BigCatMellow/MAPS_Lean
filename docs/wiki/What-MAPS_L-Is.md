# What MAPS_L Is

MAPS_L is a way to make agent work durable, governable, and recoverable. It
wraps capable AI workers with explicit task truth, authority boundaries,
orchestration, verification, and evidence.

It is an **operating system for work**, not a model and not a terminal program.
A model supplies reasoning; MAPS_L supplies the surrounding structure that
keeps work aligned across agents, tools, sessions, failures, and time.

Back to [[Home]].

## The problem it addresses

An agent can produce useful work and still fail operationally:

- it may act on a stale task description;
- two agents may claim or edit the same work;
- a replacement session may lose the original task boundary;
- a review may be performed by the author or a continuation of the author;
- a plausible result may be accepted without evidence;
- a stopped session may be resumed after its authority or lease expired; or
- a remembered instruction or Skill may be loaded without enough trust.

MAPS_L makes those facts explicit and, where implemented, mechanically guarded.
It still relies on capable agents for judgment. It does not turn every decision
into a rule or every task into a large process.

## Authority, orchestration, and execution

These are separate concerns:

| Layer | Responsibility | Does not do |
| --- | --- | --- |
| Human owner / approved project | Sets the objective and permission envelope | Approve every routine child step |
| Orchestration operator | Owns the parent outcome, shapes work, dispatches, recovers, reconciles, verifies, and continues | Transfer parent accountability to a worker |
| Worker / agent slot | Executes a bounded task and returns evidence | Expand scope or declare the parent project complete |

Fresh human approval is required for a true boundary crossing: a changed
objective, material scope expansion, new spending or credentials, an
unapproved destructive/external act, or an irreducibly subjective decision.
Routine task shaping, review, correction, and continuation inside approved
scope do not reset authority to zero.

## Responsibility boundaries

| Component | Owns | Important limit |
| --- | --- | --- |
| **SQLite task state** | task lifecycle, claims, leases, policy, submissions, review facts, run records, evidence | mutable task truth, not project planning |
| **LangGraph** | deterministic route recommendation and checkpoint state | does not invent priority, scope, or permission |
| **hcom** | communication and provider-session transport/control | messages and sessions are not task truth |
| **RnS recovery** | bounded recovery of known active sessions | does not create, claim, or reassign work |
| **Helpers** | bounded delegated execution or research | do not inherit parent ownership or review authority |
| **Execution integrity** | frozen run contract, context hashes, Git/worktree identity, and proof | freezes authority; never grants it |
| **Markdown records** | readable roadmaps, tasks, decisions, evidence, reviews, and handoffs | should not duplicate live mutable state |
| **Terminal/UI layers** | optional presentation and interaction | never authority |

The local stores are intentionally separate:

```text
.maps/state/maps.db                  task truth
.maps/state/langgraph-checkpoints.db routing/checkpoint memory
.maps/state/recovery.json            RnS incident state
.hcom/                               hcom session/message state
```

## Task truth and durable evidence

MAPS_L separates what must change atomically from what should remain readable:

- SQLite answers who owns a task, whether a lease is live, which review is
  open, and whether a guarded transition is allowed.
- Markdown explains the objective, plan, rationale, acceptance criteria,
  review, and handoff.
- GitHub holds live PR, CI, mergeability, and review coordination facts.

One fact should have one authority. Dashboards, Wiki pages, traces, and status
summaries are derived views and must not silently become writers of canonical
truth.

## The operating loop

```text
recover current truth
-> define outcome and DONE
-> shape bounded work
-> act or dispatch
-> observe evidence
-> verify/review
-> reconcile into parent state
-> continue while authorized work remains
```

The operator stops only when the parent scope is complete, a concrete authority
or safety boundary blocks further work, or it is waiting on a named active
dependency. It should neither idle before completion nor manufacture new work
after success.

## Methods versus runtime enforcement

MAPS_L contains both:

- **Methods:** playbooks for project bootstrap, task lifecycle, decisions,
  review, worktree isolation, emergence, repair, and other recurring jobs.
- **Runtime controls:** executable task state, routing, context planning,
  session lineage, recovery, Hooks, Skill trust, and integrity checks.

A method may exist without a runtime guard. A guard may be implemented without
the live evidence required to call the wider capability complete. See
[[Capability Status]] before relying on a production path.

## What MAPS_L is not

- It is not a second brain or general file-categorization system.
- It is not a promise that every documented roadmap feature is implemented.
- It is not a replacement for capable reasoning or human authority.
- It is not an invitation to run every subsystem on every task.
- It is not tied to hcom, WezTerm, one provider, or one interface as a source of
  authority.

Authoritative overview:
[`README.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/README.md) and
[`playbook/CONTROL_PLANE.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/CONTROL_PLANE.md).
