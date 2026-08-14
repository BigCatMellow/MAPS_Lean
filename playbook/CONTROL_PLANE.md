# MAP Control Plane: SQLite, LangGraph, RnS, and hcom

These systems solve coordination problems that native agent windows do not
fully solve. They are retained. WezTerm is not part of their authority model.

Need to install or rebuild them on a fresh clone? Follow
[Control-Plane Setup](../docs/CONTROL_PLANE_SETUP.md).

The proven legacy implementation needed for migration has been curated into
[`migration/legacy-runtime-source/`](../migration/legacy-runtime-source/README.md).
Use that staging source when rebuilding a retained subsystem; do not depend on
`legacy/` remaining present and do not import staging code directly into the
active runtime. The extraction/promotion checklist is
[here](../migration/LEGACY_RUNTIME_EXTRACTION.md).

## First-run takeaway

Use this document when your task touches task state, routing, recovery, hcom,
or the WezTerm transition. SQLite records mutable task truth; LangGraph
recommends the next route; RnS recovers stalled sessions through hcom; and
WezTerm is only an optional presentation surface.

Keep runtime state separated by responsibility:

```text
.maps/state/maps.db                  # MAPS task truth
.maps/state/langgraph-checkpoints.db # LangGraph execution/checkpoint state
.hcom/                               # hcom communication/session state
```

Do not merge these stores merely because more than one component uses SQLite.

## SQLite: the task ledger

SQLite answers concurrent lifecycle questions atomically:

- Which task is NEEDS_SHAPING, READY, ACTIVE, READY_FOR_REVIEW, BLOCKED,
  CHANGES_REQUESTED, or DONE?
- Who successfully claimed it?
- Has the current claim lease expired?
- Who authored the current submission, so that person cannot approve it?
- Which review/release/approval gates have actually passed?

The legacy implementation proved that ownership, current claim, submission
authorship, review, and release are separate facts. Preserve those invariants
when simplifying the schema.

The guarded mutation means two agents can race to claim a task but only one
succeeds. Leases and heartbeats prevent abandoned sessions from holding work
forever. Markdown remains the human-readable brief, roadmap, decisions,
evidence, and artifacts; do not create competing hand-maintained copies of
mutable task truth.

A consequential task may enter `READY` only after the active AGI readiness gate
passes.

## LangGraph: dispatcher, not product planner

The human-authored Markdown roadmap defines the plan. LangGraph reads current
task/dependency state plus AGI readiness, policy, availability, helper capacity,
and approval gates to select a bounded next route:

```text
review | wait_for_agent | propose_helper | claim_or_assign | policy_gate | wait_or_reconcile
```

A route is a recommendation until an accountable MAPS operation performs a
guarded state transition. LangGraph does not invent priority, task scope, or
approval.

Legacy stored custom LangGraph checkpoint tables in the task DB. Lean changes
that implementation detail: LangGraph checkpoint persistence belongs in
`.maps/state/langgraph-checkpoints.db`, separate from `maps.db`.

## RnS: recovery after limits and restarts

RnS (Rise & Shine) is a deterministic supervisor for provider-limit, stale
session, and interrupted-execution incidents. The durable recovery asset is the
task/handoff state; RnS adds detection, scheduling, resume/nudge, verification,
and bounded retry.

Preserve these rules from the tested legacy implementation:

- do not spam retries;
- do not revive intentionally terminal/superseded sessions;
- do not steal a live claim;
- do not auto-create, claim, reassign, or invent work;
- recover through a session adapter rather than a specific terminal UI.

The old implementation used hcom plus a WezTerm terminal destination. Lean
keeps the hcom recovery capability but removes mandatory WezTerm coupling.

## hcom versus WezTerm

| Concern | hcom | WezTerm |
| --- | --- | --- |
| Cross-provider message/session transport | Yes | No |
| Session list/liveness/resume for current RnS design | Yes | Terminal host only |
| Durable MAPS task truth | No | No |
| Operator visibility | Can expose session state | Optional cockpit |
| Authority | Never | Never |

hcom owns communication/session state. MAPS owns task/project authority. Keep
those stores and responsibilities separate.
