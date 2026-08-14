# MAP Discovery Practice Lifecycle — Independent Output

## Findings

```yaml
- title: Make a project's bootstrap state visible to its first task transition
  classification: risk_or_contradiction
  trigger:
    - purpose_and_lifecycle
    - omission
    - contradiction
    - foundational_assumption
  problem: MAP says a multi-session or multi-agent project must establish intent, assumptions or research needs, quality standards, risks, decision paths, and Emergence capacity before its first task. The task creation and promotion paths, however, validate only task-level fields and never establish or check a project bootstrap state. A task can therefore become READY and claimable without the project context that the lifecycle requires it to have.
  user_impact: The first implementer can receive a technically claimable task but lack an agreed completion condition, authority path, risk posture, or place to capture discoveries. The resulting ambiguity is discovered after work starts, when correction costs more and ownership/review disputes are more likely.
  proposed_response: Run a read-only fixture experiment that creates a minimally valid task in an otherwise unbootstrapped project root and records which lifecycle prerequisites are invisible to the existing READY/claim gates. If the gap is material, add a small bootstrap-readiness validator or explicit project bootstrap marker that task promotion can consult; retain the documented skip path for genuinely throwaway work.
  minimal_version: A non-mutating validator reports the seven bootstrap prerequisites and lets a task's project identify an explicit "trivial/skip" reason. It should warn first rather than block existing projects or ordinary MAP maintenance.
  alternatives:
    - Add a task-authoring checklist prompt only, without a validator.
    - Require each new task description to repeat the whole bootstrap context.
    - Treat every project as fully bootstrapped by the root MAP files.
  evidence:
    - "Observed: MAP_System/PROJECT_BOOTSTRAPPING_SYSTEM.md:27-57 states that a multi-agent/multi-session project must establish seven prerequisite forms of context before its first task."
    - "Observed: MAP_System/NEW_PROJECT_WIZARD.md:6-39 says to create the bootstrap artifacts before writing the first task and calls the bootstrap incomplete if one of its six answerable questions has no answer."
    - "Observed: MAP_System/scripts/map_task.py:create_task (lines 161-215) assigns READY whenever description, output_path, and criterion are present; it has no project-root or bootstrap check."
    - "Observed: MAP_System/scripts/promote_task.py:107-151 validates HPOM task fields and changes a task to READY, but never checks PROJECT_BOOTSTRAPPING_SYSTEM prerequisites."
    - "Observed: MAP_System/db/claims.py:122-193 permits a READY task claim after task-level policy checks; no project bootstrap state is read."
    - "Inference: The stated lifecycle invariant is currently a convention, not a control or even a surfaced preflight result."
  confidence: high
  scores:
    user_value: 4
    goal_alignment: 5
    necessity: 4
    novelty: 3
    leverage: 5
    confidence: 5
    reversibility: 5
    complexity: 2
    maintenance_burden: 2
    scope_risk: 3
  recommendation: investigate
  reasoning_summary: This does not assume every project needs more ceremony. It tests the narrower claim that the system should make its own stated prerequisite visible at the one transition where omission becomes executable, while preserving an explicit lightweight exception.

- title: Reconcile the two ways a task becomes READY before adding more lifecycle rules
  classification: risk_or_contradiction
  trigger:
    - contradiction
    - assumption
    - divergence
    - compression
  problem: Direct task creation assigns READY from three minimal fields, whereas the explicit promotion command requires eight HPOM fields in the task JSON before assigning READY. The claim gate then accepts READY using task-level completeness checks. These divergent entry paths make READY mean different things depending on which command an author happened to use.
  user_impact: A hypothetical ambiguous brief can be made immediately claimable through the direct path even though it would fail the promotion contract intended to make task execution self-contained. Authors and reviewers must infer which READY standard applies, and later fixes risk adding duplicate prose rather than resolving the one authoritative readiness rule.
  proposed_response: First run a read-only audit that classifies current READY/IN_PROGRESS task records by the direct-creation versus promotion schema and identifies whether the difference has produced rework or only legacy compatibility. If it is live, define one canonical READY predicate and have both commands call it; use a warning or NEEDS_SHAPING default during migration rather than retroactively blocking work.
  minimal_version: Extract one shared readiness function and add fixture tests showing that direct creation and explicit promotion return the same readiness result for an equivalent task payload.
  alternatives:
    - Deprecate promote_task.py and document the smaller direct-create schema as canonical.
    - Make map_task.py always create NEEDS_SHAPING, with an explicit promotion step for every task.
    - Leave both paths but publish a routing table explaining their intended separate use.
  evidence:
    - "Observed: MAP_System/scripts/map_task.py:162-166 selects READY if description, output_path, and criterion are supplied."
    - "Observed: MAP_System/scripts/promote_task.py:21-31 and 107-151 require objective, required_context, files_in_scope, forbidden_changes, acceptance_criteria, expected_artifacts, reviewer_role, and risk before setting READY."
    - "Observed: MAP_System/notes/state-machine-guardrails.md defines READY as the point where a task has passed a strict preflight gate."
    - "Observed: MAP_System/db/claims.py:122-193 accepts READY tasks after its own claim_block_reason policy checks, rather than re-running the promotion schema."
    - "Observed: MAP_System/shared/current-state.md lists the READY promotion gate as ACTIVE, so the stronger path is represented as live operational capability."
    - "Inference: Two non-identical readiness contracts create avoidable semantic branching at the core lifecycle transition."
  confidence: high
  scores:
    user_value: 4
    goal_alignment: 5
    necessity: 4
    novelty: 4
    leverage: 5
    confidence: 5
    reversibility: 4
    complexity: 3
    maintenance_burden: 2
    scope_risk: 3
  recommendation: investigate
  reasoning_summary: The proposed work is a reconciliation audit before a policy change, not a demand for a heavier gate. One readiness vocabulary would compress authoring, review, and recovery behavior and make an ambiguous kickoff fail or surface consistently.

- title: Do not add automatic reviewer assignment for the simulated review conflict
  classification: rejected_idea
  trigger:
    - adverse_path
    - analogy
    - evaluation
  problem: A task owner cannot self-review, so assigning a reviewer automatically can appear to remove a lifecycle pause.
  user_impact: Automation could reduce a routing step, but choosing a reviewer is not always a mechanical availability problem: task sensitivity, independence, active ownership, and visible-helper scope can matter.
  proposed_response: Reject a new automatic-assignment mechanism. Continue using the existing atomic review-claim and bounded visible-helper route for routine conflicts; escalate only when the existing policy says human authority is required.
  minimal_version: No implementation; retain the current route.
  alternatives:
    - Let the first eligible reviewer claim the submitted task atomically.
    - Use the existing visible helper path when no clean core reviewer is available.
  evidence:
    - "Observed: MAP_System/notes/review-guide.md:20-40 provides an atomic claim_review path that rejects self-review and duplicate open review claims."
    - "Observed: MAP_System/AGENTS.md 'Routine Reviewer Conflict Routing' defines the visible helper route when no clean core reviewer is available."
    - "Observed: MAP_System/emergence/insights/INS-0015-a-routine-no-self-review-reviewer-conflict-should-trigger-the-ex.md records this precise failure and its bounded remediation."
    - "Inference: A second automatic selector would duplicate an existing safe route while obscuring the judgment that should remain explicit for non-routine reviews."
  confidence: high
  scores:
    user_value: 1
    goal_alignment: 3
    necessity: 1
    novelty: 1
    leverage: 1
    confidence: 5
    reversibility: 3
    complexity: 4
    maintenance_burden: 4
    scope_risk: 3
  recommendation: reject
  reasoning_summary: The adverse path is already covered by an explicit, tested, visible route. Adding a new allocator would create process surface without evidence of an unmet need.

- title: Do not replace MAP's durable-file and SQLite structure with a new monolithic lifecycle store
  classification: rejected_idea
  trigger:
    - foundational_assumption
    - divergence
    - paradox
  problem: A single lifecycle store could seem to eliminate the distinction between task files, SQLite claims, handoffs, and status records.
  user_impact: It might simplify one interface, but it would risk erasing the inspectable human-readable mirror, established release/review gates, and the separation between availability, task ownership, and continuation context.
  proposed_response: Reject replacement. Investigate narrow reconciliation at proven seams instead, beginning with readiness and bootstrap visibility; keep existing canonical sources and mechanically generated views.
  minimal_version: No implementation. Use the two reversible audits above to identify whether a shared predicate or read model is enough.
  alternatives:
    - Build a read-only lifecycle dashboard over existing sources.
    - Add focused validators for demonstrated cross-source drift.
  evidence:
    - "Observed: MAP_System/shared/requirements.md requires canonical project state outside LangGraph while naming SQLite as the claim coordinator and file-backed records as the human-readable mirror."
    - "Observed: MAP_System/artifacts/reviews/agent-coordination-documents-review-2026-07-17.md explicitly rejects a second canonical STATE.json/TASKS.json structure and recommends mechanically generated views."
    - "Observed: MAP_System/artifacts/tests/taxonomy-tests-4-6-report.md documents that task mirror drift is already checked mechanically, while handoff-content drift is a narrower identified gap."
    - "Inference: The problem is inconsistent lifecycle contracts at a few transitions, not evidence that the durable-source architecture should be replaced."
  confidence: high
  scores:
    user_value: 1
    goal_alignment: 2
    necessity: 1
    novelty: 1
    leverage: 1
    confidence: 5
    reversibility: 1
    complexity: 5
    maintenance_burden: 5
    scope_risk: 5
  recommendation: reject
  reasoning_summary: Testing root assumptions does not justify substituting a new control plane for proven durable sources. The smaller experiments target the observed mismatch directly and preserve reversibility.
```

## Pass coverage and method note

All seven passes were performed independently against a hypothetical small project from kickoff to first release. The normal path traced project bootstrap, task creation, claiming, implementation, handoff, review, release, status, lesson capture, and emergence. The adverse path separately tested an ambiguous brief, a session-limit interruption, and a no-self-review conflict. I read the actual governing bootstrap, task-authoring, claim, review, release, availability, handoff, lesson, and emergence sources; I distinguished observed code/document behavior from inferences and proposals. The session-limit path has an established durable-handoff protocol, and the reviewer-conflict path has an established visible-helper protocol, so neither was inflated into a new surviving finding. I also tested the foundational alternative of a replacement lifecycle store and rejected it in favor of two reversible, read-only reconciliation experiments. No implementation, task, policy, decision, emergence, status, or task-state files were changed.
