# MAP Control Plane: SQLite, LangGraph, RnS, and hcom

These systems solve coordination problems that native agent windows do not
fully solve. They are retained. WezTerm is not part of their authority model.

## First-run takeaway

Use this document when your task touches task state, routing, session recovery,
hcom, or the WezTerm transition. SQLite records the mutable task lifecycle;
LangGraph recommends the next route; RnS recovers stalled sessions through
hcom; and WezTerm is only an optional presentation surface. Read no deeper
unless your task needs a specific component.

## SQLite: the task ledger

SQLite is not a project notes database. Its value is an atomic answer to
concurrent lifecycle questions:

- Which task is READY, ACTIVE, SUBMITTED, APPROVED, or RELEASED?
- Who successfully claimed it?
- Has the owner’s lease expired, allowing recovery?
- Who submitted it, so that person cannot review it themselves?

The guarded update means two agents can race to claim a task but only one
succeeds. Leases and heartbeats prevent abandoned sessions from holding work
forever. It also stores durable LangGraph checkpoints. Markdown remains the
human-readable brief, roadmap, decisions, evidence, and artifacts; do not
create competing manual copies of mutable task truth.

## LangGraph: dispatcher, not product planner

The human-authored Markdown roadmap and ProjectUpdater checklist define the
plan. LangGraph reads current task/dependency state plus policy, availability,
helper capacity, and approval gates to select a next operational route:

```text
review | wait_for_agent | propose_helper | claim_or_assign | policy_gate | wait_or_reconcile
```

It is deliberately read-first: a route is a recommendation/hint until an
accountable agent follows the appropriate claim, review, or escalation path.
This makes roadmaps actionable without letting an automated graph invent
priority, task scope, or approval.

## RnS: recovery after limits and restarts

RnS (Rise & Shine) is a deterministic supervisor for provider-limit and stale
session incidents. The real recovery asset is always a current handoff. RnS
adds the alarm clock: it records/infer a reset time, detects a stopped/stale
session, resumes or nudges it after the window, and backs off rather than
spamming retries. It does not auto-claim, reassign, or invent work.

The current implementation is coupled to hcom: hcom provides session listing,
bounded transcript access, resume, and message injection. Replacing WezTerm
does not affect that. Replacing hcom would require an explicit, tested adapter
to each provider's native session/resume interfaces.

## hcom versus WezTerm

| Concern | hcom | WezTerm |
| --- | --- | --- |
| Cross-provider message and identity | Current control transport | No |
| Resume/nudge sessions for RnS | Current implementation uses it | Only terminal destination today |
| Durable task truth | No; SQLite/files own it | No |
| Operator visibility | Can expose session state | Tab/pane cockpit |
| Authority | Never | Never |

Keep hcom with the existing RnS. Make WezTerm optional by changing only the
terminal/resume presentation adapter after native agent interfaces prove they
can provide equal recoverability.
