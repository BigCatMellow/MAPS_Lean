# EXP-0004 Orientation Manifest — Discovery Preflight

## Verdict

**REFINE.** The fixed scenario is live and well-bounded, and the proposed treatment remains reversible. Before it is used, pre-register the answer rubric, distinguish the immediate read action from the later task-state mutation, and define the byte comparison threshold. These are experiment-packet corrections only; they do not change MAP policy or canonical startup rules.

## Findings

```yaml
- title: Freeze an evaluator rubric outside the treatment packet
  classification: risk_or_contradiction
  trigger:
    - evaluation
    - paradox
    - assumption
  problem: EXP-0004 requires an independent evaluator to answer five fixed routing questions from a manifest before source verification, but it does not require a pre-registered answer rubric, source snapshot, or separation between the treatment author and the expected-answer definition. A compact packet can therefore be tailored to the known questions and appear correct without demonstrating that it preserves the authority and recovery distinctions a resumed agent needs.
  user_impact: A passing result could validate recall of a scripted answer rather than safe orientation. That would make later use of a manifest look evidence-backed even if it omits a conflict, currentness qualifier, or authority reference that the author did not anticipate.
  proposed_response: Before treatment construction, place a five-question rubric in the preflight/control record with required facts, acceptable uncertainty language, canonical sources, and snapshot times or hashes. Give the evaluator only the questions and treatment; adjudicate against the frozen rubric and then the canonical sources.
  minimal_version: Add one short table to the experiment control record: question, required fact, required authority/currentness reference, acceptable unknown response, and canonical verification source.
  alternatives:
    - Let the treatment author score the evaluator after the fact.
    - Ask an evaluator only whether the packet seems understandable.
    - Require a generic manifest framework before testing one scenario.
  evidence:
    - "Observed: MAP_System/emergence/experiments/EXP-0004-a-scoped-orientation-manifest-can-reduce-a-resumed-agent-s-conte.md requires five routing answers before verification but does not state an answer-key freeze, evaluator blinding, or source snapshot."
    - "Observed: MAP_System/inbox/helpers/helper-orientation-manifest-2026-07-18.md requires a verifier checklist, but does not require the checklist to be committed before the treatment is written."
    - "Observed: MAP_System/artifacts/experiments/token-efficient-durable-context-audit-2026-07-18.md finds that compact orientation can omit ownership, activation, review-date, status, supersession, and canonical-store identity even when it preserves an immediate routine action."
    - "Inference: The experiment needs to score authority/currentness recovery, not only a treatment author's ability to compress a known scenario."
  confidence: high
  scores:
    user_value: 5
    goal_alignment: 5
    necessity: 5
    novelty: 3
    leverage: 5
    confidence: 5
    reversibility: 5
    complexity: 1
    maintenance_burden: 1
    scope_risk: 1
  recommendation: implement
  reasoning_summary: A frozen rubric is the smallest anti-answer-key control. It preserves the one-scenario experiment while making a positive result interpretable.

- title: Separate the first safe read from the later rework state transition
  classification: risk_or_contradiction
  trigger:
    - purpose_and_lifecycle
    - contradiction
    - recovery
  problem: The scenario asks for the "first valid action" after resumption. TASK-227 is currently CHANGES_REQUESTED, but its handoff directs the owner to read the review and prepare the correction before invoking map_task.py rework. Treating "rework" as the first action would be unsafe; treating a generic "continue work" as correct would conceal the state-transition boundary the experiment is meant to test.
  user_impact: An evaluator can receive credit for the wrong immediate action, or a manifest can omit the review artifact and still pass. In either case the experiment fails to test whether compressed orientation protects the task lifecycle at its most consequential point.
  proposed_response: Split the routing question into (1) immediate safe orientation action and (2) next permitted mutation after preparation. Require the treatment to name the current task state, review record, and condition before rework.
  minimal_version: Replace one verifier row with two: "What must be read first?" and "When/how may the task re-enter rework?" Each row names its canonical reference.
  alternatives:
    - Score only the eventual goal of resubmitting the plan.
    - Make state mutation the first required action and omit the review record.
  evidence:
    - "Observed: MAP_System/tasks/TASK-227.json currently records status CHANGES_REQUESTED and owner claude-lab-gome."
    - "Observed: MAP_System/events/events.jsonl at 2026-07-18T04:46:23Z records TASK-227's CHANGES_REQUESTED transition and links MAP_System/artifacts/reviews/task227-review-lilo.md."
    - "Observed: MAP_System/handoffs/HANDOFF-20260718-system-improvement-kickoff-to-claude.md says to resolve the five review points before resubmitting and to run map_task.py rework only when ready to edit."
    - "Observed: the manifest assignment names both first valid action and interruption-safe recovery as required answers."
    - "Inference: Read-before-mutate is a distinct safety fact that must be separately measured, not inferred from the final intended task outcome."
  confidence: high
  scores:
    user_value: 5
    goal_alignment: 5
    necessity: 5
    novelty: 4
    leverage: 5
    confidence: 5
    reversibility: 5
    complexity: 1
    maintenance_burden: 1
    scope_risk: 1
  recommendation: implement
  reasoning_summary: The scenario has an unusually useful real transition boundary. Splitting it makes the treatment test safe recovery rather than only task recognition.

- title: Define material context reduction before measuring it
  classification: likely_requirement
  trigger:
    - evaluation
    - omission
    - token_cost
  problem: EXP-0004 fails if the packet does not materially reduce bytes, but neither the experiment nor the assignment defines the control population, exact measurement command, or a threshold for materiality. The prior audit shows that a small orientation projection can be 97% smaller than a raw discovery route while adding to a separately mandated startup stack; either comparator could make a claim look favorable.
  user_impact: The result may be judged after seeing its size, creating an arbitrary pass/fail decision and overstating total startup savings. The operator cannot tell whether the manifest reduces the actual scenario's first-action context or only a selectively chosen subset.
  proposed_response: Specify the exact control source list, wc command, and threshold before construction. Report both the scenario-local reduction and the treatment's additive cost against the current mandatory startup contract; claim only the former unless the mandatory contract is actually changed in a later experiment.
  minimal_version: State a pre-run threshold such as at least 50% fewer bytes than the listed scenario control, plus a required note that the existing startup contract remains unchanged.
  alternatives:
    - Use a qualitative "looks shorter" verdict.
    - Compare only against the full startup stack and ignore scenario-local retrieval.
    - Report a reduction without naming the comparator.
  evidence:
    - "Observed: EXP-0004 defines success as materially smaller than the measured baseline but supplies no numeric threshold or enumerated baseline."
    - "Observed: helper-orientation-manifest-2026-07-18 requires a control source list and byte/word counts, but not a predeclared pass threshold."
    - "Observed: token-efficient-durable-context-audit-2026-07-18.md distinguishes a 97.4% reduction versus raw discovery from no proven reduction of the mandatory 67,884-byte startup baseline."
    - "Inference: Both measurements are useful only if labeled separately before the treatment result is known."
  confidence: high
  scores:
    user_value: 4
    goal_alignment: 5
    necessity: 4
    novelty: 3
    leverage: 4
    confidence: 5
    reversibility: 5
    complexity: 1
    maintenance_burden: 1
    scope_risk: 1
  recommendation: implement
  reasoning_summary: This correction does not demand a global token budget. It makes the narrow experiment's efficiency claim falsifiable and prevents scenario-local savings from being misrepresented as startup-wide savings.

- title: Do not build a generic manifest runtime before the fixed-scenario experiment
  classification: rejected_idea
  trigger:
    - emergence
    - divergence
    - non_forcing
  problem: The need for a compact orientation packet can invite construction of a new manifest store, startup runtime, or index system before one fixed scenario has shown that a treatment preserves safe action.
  user_impact: A generalized layer would add authority and maintenance surface before there is evidence that manifest retrieval improves actual resumed-agent decisions.
  proposed_response: Reject preemptive generalization. Keep EXP-0004 read-only, scenario-specific, and non-canonical; decide later only from measured correctness, bytes, and follow-up source verification.
  minimal_version: No implementation.
  alternatives:
    - Use the required one-off treatment artifact.
    - Generate a later read-only view only if the experiment passes and a second scenario confirms transfer.
  evidence:
    - "Observed: EXP-0004 limits the manifest to a test packet, keeps canonical files available, and prohibits changing indexes or canonical behavior."
    - "Observed: token-efficient-durable-context-audit-2026-07-18.md recommends piloting a generated manifest beside the existing launcher before switching."
    - "Inference: The appropriate compression opportunity is a bounded measurement, not a new control plane."
  confidence: high
  scores:
    user_value: 1
    goal_alignment: 3
    necessity: 1
    novelty: 1
    leverage: 1
    confidence: 5
    reversibility: 2
    complexity: 5
    maintenance_burden: 5
    scope_risk: 4
  recommendation: reject
  reasoning_summary: The experiment already provides the smallest reversible test. Generalizing before it produces a proven gain would optimize structure rather than orientation quality.
```

## Pass coverage and method note

This preflight applied the seven Discovery passes only to EXP-0004's fixed orientation scenario and treatment design: lifecycle/recovery, missing safety facts, leverage from the existing operational orientation, analogy to answer-key optimization, contract contradictions, bounded alternatives, and explicit scoring. The current scenario is verified against the live TASK-227 task record, event transition, review handoff, and assignment note. The required corrections are limited to the experiment's control/treatment packet and verifier; no MAP-wide policy, startup rule, task state, or index change is proposed.
