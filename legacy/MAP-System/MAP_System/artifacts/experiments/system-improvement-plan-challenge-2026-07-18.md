# System Improvement Plan Challenge Pass

- Reviewer: helper-review-steward-moku
- Scope: advisory challenge of `notes/system-improvement-implementation-plan.md`
- Authority: no implementation, task-state, policy, decision, or E/I changes

## Overall assessment

The priority order is credible: it correctly treats TASK-221, TASK-218/219,
and the existing helper/review machinery as shipped rather than rebuilding
them. It also uses two risk-calibrated task records instead of six process
tasks. The plan can reduce cycle time and operator uncertainty if the five
issues below are resolved during task shaping.

## Priority assessment

| Priority | Assessment | Trace |
|---|---|---|
| 1. Visible coordination surface | Sound highest priority, but needs explicit source precedence and freshness semantics before a UI renders potentially conflicting live/durable state. | Plan 1a; `shared/subsystem-apis.md`; TASK-082 and TASK-203 review records. |
| 2. Durable memory and learning | Appropriate low-risk leverage point. The index must define its coverage and test sample so its two-hop claim is observable rather than aspirational. | Plan 2a; `notes/operational-learning-guide.md`; book lessons §§1, 6. |
| 3. Helper boundaries | Consolidation is appropriate and the no-direct-mutation boundary is valuable. It changes agent authority, so the plan must follow its own decision-routing answer. | Plan 3a and "decisions.md vs notes" answer; `MAP_System/AGENTS.md`. |
| 4. Discovery and review loop | No material issue found. Proposal-only discovery, frozen findings, and existing promotion gates match EXP-0003/TASK-226 and avoid adding review ceremony. | Plan 4a/4b; `notes/discovery-agent-guide.md`; TASK-226 review. |
| 5. Monitoring and nudge behavior | Correctly re-scoped after TASK-221, but a universal record rule needs an inventory/boundary or it becomes a new, unverifiable policy burden. | Plan 5a/5b; TASK-221 evidence and review; Sentinel’s visible 30-minute schedule. |
| 6. Command Center UX cleanup | Correctly deferred until the data contract is established. No material issue found. | Plan 6a; book lessons §4. |

## Challenge findings

| # | Severity | Finding | Why it matters | Concrete adjustment |
|---|---|---|---|---|
| C1 | REQUIRED BEFORE 1a | 1a combines `agents/status.json`, `map.db` claims, and event-log activity but does not specify precedence, timestamps, or the UI result when they disagree. Existing evidence already shows status-mirror drift and live-vs-durable ambiguity. | A polished card could confidently display stale or contradictory state, increasing rather than reducing operator uncertainty. | Put a small read-model contract in the task: source for each field, freshness indicator, conflict/warn state, and one deterministic mixed-state test in addition to the staged screenshot. Do not add a new store. |
| C2 | REQUIRED BEFORE 2a | The two-hop acceptance claim says "any active convention" but does not enumerate the indexed population, define `CURRENT` ownership, or specify how a new note is classified. | The index can become another long, incomplete directory and create maintenance toil without proving a fresh session can find load-bearing rules. | Define a bounded initial inventory (for example all `CURRENT` notes plus named shared files), a five-convention lookup acceptance sample, and an explicit owner/update path. Keep a validator deferred until actual drift occurs. |
| C3 | REQUIRED BEFORE 3a | The plan correctly says the no-direct-mutation rule belongs in `shared/decisions.md`, but the immediate slate labels 3a as documentation-only and does not name the decision-class/approval route. | This is an authority change, not merely consolidation; placing it only in prose leaves conflicts with existing helper permissions unresolved. | Split the authority decision from the low-risk documentation batch, or make the batch task explicitly include a decision proposal/record with the required decision class and review authority before cross-references are changed. |
| C4 | RECOMMENDED | 5a would declare any unrecorded scheduled/recurring nudge an invisible background process to remove, yet the plan does not inventory existing schedules or distinguish purely read-only UI timers from message/state-changing automation. | A broad rule can create retroactive, untestable debt or incorrectly classify safe UI polling as prohibited automation. | First list the currently active recurring processes and define the boundary: state/message-changing processes require the record; pure read-only rendering/polling is documented where it already lives. Then apply the convention prospectively. |
| C5 | RECOMMENDED | 1a’s "live helper" population is not defined across hcom session names, durable helper notes, and finished-but-still-visible terminal sessions. | The operator surface can either hide an active helper or retain stale cards, recreating the exact interpretation work it aims to remove. | State the inclusion rule and terminal condition in the 1a task: join live hcom identity with a matching active helper note; show unmatched/ambiguous identities as attention warnings rather than silently guessing. |

## No-material-issue results

- The reordering of monitoring after visibility is justified by TASK-221’s
  released supervisor and its independently reproduced bounded retry behavior.
- Deferring UX polish until 1a supplies a truthful data contract follows the
  kickoff and avoids turning layout work into a substitute for state repair.
- Declining extra discovery/review steps is proportionate to the risk-tiered
  review model and the ClearFront audit’s documented ceremony cost.

## Root-assumption challenge and reversible tests

The plan should not preserve MAP layers merely because they already exist. The
following alternatives are worth testing before treating the current stack as
foundational:

| Assumption | Evidence so far | Reversible test | Decision signal |
|---|---|---|---|
| SQLite claims plus JSON/graph mirrors are worth their synchronization cost. | Atomic claims and mirror validation caught real state drift, but the dual representation adds writes and review overhead. | For one low-risk documentation batch, use SQLite as the sole operational board and generate mirrors only at submission/review; measure state-change steps, mirror failures, and reviewer reconstruction time. | Keep dual state only if it improves independent reconstruction or catches drift at a cost lower than the manual recovery it prevents. |
| hcom events are the right raw source for operator attention. | hcom provides live observability, yet the 2026-07-17/18 confusion required raw transcript/file reading and historical sessions can be misleading. | Have 1a render a read-only, explicitly freshness-labeled attention projection for one week; compare operator questions/time-to-identify an owner or blocker against the raw hcom path. | Retain event-derived attention only if it reduces, rather than shifts, interpretation work. |
| Every helper needs a durable note before work. | The rule creates accountability and has supported review routing, but short bounded checks can incur coordination cost disproportionate to their risk. | Define a one-week exception for deterministic, non-model, read-only checks under a core task record, with a visible command/output but no helper note; compare missed ownership/context incidents. | Narrow the note rule only if the exception preserves traceability without incidents; do not extend it to model judgment or mutable work. |
| `notes/` is the right primary retrieval layer for operational knowledge. | TASK-223’s scoped machine-readable lesson projection improved startup retrieval; a large note index may duplicate that function. | Build the 2a index as a generated, read-only view of metadata for a bounded subset, then ask fresh sessions to retrieve five governing rules via the index and via lesson projection. | Prefer the path with lower context load and equal or better correct retrieval; do not maintain two manual directories. |

These tests are deliberately small and reversible. None requires replacing MAP
or weakening its safety boundaries up front; each produces evidence for keeping,
shrinking, or replacing a layer.

## Conclusion

Proceed with the two-task slate after C1–C3 are made explicit during shaping.
C4–C5 should be acceptance/edge-case constraints, not separate policy-engine
work. The plan otherwise stays within its stated leverage-point and
anti-hidden-authority principles.
