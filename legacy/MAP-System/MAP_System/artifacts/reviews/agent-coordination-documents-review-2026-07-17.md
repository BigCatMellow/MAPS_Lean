# Review: proposed MAP coordination and communication documents

Date: 2026-07-17  
Reviewer: codex-lab-lilo

Reviewed:

- `/home/mellow/Projects/MultiAgentProject/MAP_AGENT_COORDINATION_DESIGN_PHILOSOPHY.md`
- `/home/mellow/Projects/MultiAgentProject/optimal-agent-communication-guide.md`

## Verdict

Both documents can improve MAP, and their central diagnosis matches the
independent ClearFront audit: shared state, bounded ownership, evidence, and
event-triggered review are useful; routine narration, uniform ceremony, and
agents without independent value are not.

Adopt the coordination philosophy incrementally as operating guidance. Do not
adopt the proposed MAP/1 DSL as an agent convention yet. The DSL document
correctly says shorthand is safe only after a parser, schema validator,
versioned registry, contradiction handling, selective retrieval, and a
plain-English renderer exist. Asking agents to emit it before those controls
would move ambiguity into terse syntax without producing reliable context
savings.

## Adopt now

1. **State-change-only communication.** Record transitions, new evidence,
   blockers, decisions, and changed risks. Do not emit routine narration or
   per-output-path `PROGRESS` events.
2. **Bounded assignment contracts.** Every delegated agent task should state
   objective, scope, inputs, required output, permissions, and stopping
   condition. Spawn an agent only for real parallelism, distinct capability,
   context isolation, or independent verification.
3. **Event-triggered deliberation.** Use debate or multi-agent discussion for
   contradictory evidence, material discoveries, failed critical evaluation,
   major changes, consequential actions, or unresolved authority—not routine
   completion.
4. **One canonical record per concern.** Keep tasks, decisions, current state,
   risks, evidence, and reviews distinct. Generate mirrors and human-readable
   views mechanically rather than maintaining parallel narratives.
5. **Outcome metrics.** Track accepted requirements, regressions, duplicated
   work, handoff reconstruction, and review findings that changed outcomes.
   Message count or agent count is not progress.
6. **Risk-calibrated review.** DEC-CF-008 and the new review-guide lanes are a
   practical implementation of the documents' change-control model.

## Pilot separately

The readable MAP/1 proposal is promising for repetitive machine-facing hcom
updates and handoffs. Treat it as a measured experiment, not a global rule:

- define a minimal schema for `type`, `id`, `state`, `owner`, `next`, `need`,
  `refs`, and `verify`;
- implement parsing, validation, exact-recipient checks, and English rendering;
- compare it with concise structured English on interpretation accuracy,
  receiving-context tokens, latency, and rework;
- reject unknown versions and malformed or contradictory records;
- expand usage only if the pilot improves total coordination cost without
  increasing misunderstandings.

Until then, the existing hcom `intent` plus concise Issue / Options /
Recommendation / Needed requests provide most of the routing benefit with less
implementation risk.

## Do not import wholesale

- Do not add a second canonical `STATE.json`/`TASKS.json` structure beside the
  existing MAP database, task files, and current-state records. Reconcile the
  existing authority model first and generate views from it.
- Do not require a handoff after every short session when durable task state and
  evidence already make continuation unambiguous.
- Do not turn all normative suggestions in the 1,300-line philosophy into
  mandatory gates. That would recreate the ceremony problem it warns against.
- Do not count token savings from shorter transport if software later expands
  the same content into the model context; measure receiving context and rework.

## Recommended implementation order

1. Finish the current ClearFront improvement batch: risk lanes, one-command
   test gate, and consolidated delivery evidence.
2. Change event guidance/tooling to emit transitions rather than narrative
   progress and ensure events route to the project-local canonical stream.
3. Add an agent-assignment template with a required stopping condition and
   explicit spawn justification.
4. Identify the authoritative state representation and mechanically generate
   mirrors/readable summaries from it.
5. Run a small MAP/1 communication pilot only after steps 1–4 reduce existing
   duplication.

The documents should guide simplification, not become two more layers every
agent must repeatedly quote or certify.
