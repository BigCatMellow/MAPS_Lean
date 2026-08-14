# Command Center Lab Roster And Authority

Status: current after TASK-302 and TASK-303
Canonical authority: `shared/project-brief.md` → `Operating Model`
Related: `AGENTS.md`, `notes/context-rotation-guide.md`,
`notes/command-center-lab-restart-startup.md`

## Fixed Visible Roster

A fresh Lab opens Shell, Codex Lab, Claude Lab, Pi Lab, Librarian, New Agent,
and Monitor. Each model-backed tab starts through its instruction-bearing
launcher. Additional task-scoped helpers remain on demand.

The fixed roster is an operator visibility and access contract. It is not an
authority roster, availability claim, work assignment, or coordinator
designation.

## Authority Contract

The canonical hierarchy is:

1. `bigboss` / operator / Command Center owns intent, priority, policy and
   scope decisions, high-authority approvals, veto, and stop control.
2. The operator may designate one coordinator for a run. Codex and Claude are
   eligible peer core agents; neither a provider name nor an open tab selects
   the coordinator.
3. Every active task has one accountable owner and a different independent
   reviewer for substantive work. SQLite task/review state binds those
   conflict-separated assignments.
4. Pi, Librarian, visible helpers, and local assistants provide bounded support
   under a named owner and hold no task, review, release, routing, policy,
   coordinator, or operator authority.

The coordinator integrates the run, routes already-authorized work, escalates
operator decisions, and accounts for helper output. The designation grants no
ability to bypass task claims, approval gates, privacy boundaries,
destructive-action safeguards, or independent review.

## Orchestrator routing vs. autonomous authority

Coordination is a scoped work assignment, not autonomous authority. The
coordinator may integrate and route already-authorized work but may not invent
policy, widen scope, consume an approval on the operator's behalf, collapse
owner/reviewer separation, or treat a fixed provider as a permanent rank.

RUKI SQLite is canonical lifecycle state, LangGraph recommends routes, hcom
communicates, and Command Center displays operator controls. These systems are
not owners or decision authorities.

## Routing And Review

Terminal presence is never availability truth. Before assigning work, use the
runner route and canonical RUKI task/review state. When a task is submitted,
use `scripts/review_routing.py` and the canonical review claim to choose a
reviewer outside the submission author's context-rotation lineage. If no
independent live reviewer is available, request operator direction instead of
collapsing owner and reviewer.

Workers and helpers must use operator-reachable visible terminals. A helper
needs a bounded assignment, durable helper note, and accountable core owner.
Closing or opening a tab does not change any lifecycle assignment.

## Session Continuity

Context rotation is separate from the authority hierarchy:

- `prepare` freezes a snapshot and transfers no authority.
- `ack` binds a live replacement to that snapshot and transfers no authority.
- successful `finalize` transfers only the explicit claims and obligations in
  the snapshot.

A replacement continues a designated coordinator role only after finalization,
only when the snapshot explicitly preserves that existing designation, and
only while the operator has not revoked it. Rotation does not promote a
provider, create a core seat, or grant operator, policy, owner, reviewer,
release, or routing authority.

## Historical Corrections

TASK-286 experimented with a minimal startup centered on a single Codex routing
tab. TASK-302 explicitly superseded that topology and restored the fixed
visible roster. TASK-303 resolves the remaining ambiguity by separating fixed
visibility from explicit authority designation. The current behavior does not
add a new scheduler, role registry, or orchestration subsystem.

## Migration

TASK-303 keeps TASK-302's seven-pane startup topology intact. It changes only
the canonical authority wording, the instruction-bearing fixed-agent prompts,
the presentation comment, and focused contradiction coverage.

## Rollback

Rollback TASK-303 by reverting its documentation, prompt, presentation-comment,
and contradiction-test changes together. Do not roll back TASK-302's fixed
roster as a side effect.

## Residual risk

Residual boundaries remain unchanged:

- operator approval and security gates still apply;
- no model-backed lane may be hidden from operator inspection and stop control;
- no task owner may approve its own substantive deliverable;
- prompts are guidance, while SQLite claims/reviews and verified continuity
  ledger transitions are the enforceable lifecycle records.
