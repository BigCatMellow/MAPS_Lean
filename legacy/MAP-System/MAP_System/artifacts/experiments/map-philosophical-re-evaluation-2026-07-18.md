# MAP Philosophical Re-evaluation — Independent Output

## Findings

```yaml
- title: Treat model-backed discovery as an event-triggered decision-support call, not an open-ended improvement activity
  classification: risk_or_contradiction
  trigger:
    - purpose_and_lifecycle
    - paradox
    - autonomy_and_visibility
    - durable_evidence_and_token_cost
  problem: MAP's pilot evidence says the Discovery Agent is valuable at meaningful phase boundaries and explicitly rejects a continuous paid/model session. The active system-improvement lane nevertheless frames discovery as an ongoing loop and has commissioned successive broad passes. Without a recorded trigger, decision consumer, known-set boundary, and yield/curation stop condition, visible activity can become token-expensive surveying whose durable artifacts outpace decisions.
  user_impact: The operator receives more proposals and records without a proportional increase in decisions or shipped value; core-agent time shifts from acting on validated priorities to repeatedly adjudicating adjacent analysis. Conversely, a bounded trigger makes discovery available precisely when deterministic signals or a changed phase make semantic judgment useful.
  proposed_response: Run one reversible consolidation experiment for the current improvement phase: admit one further model-backed discovery pass only from a named trigger (phase exit, material architecture change, Sentinel anomaly, or operator question), freeze its known set, name the decision owner/consumer, and record useful-new findings plus curation minutes. Compare this with the current sequence before setting any standing cadence.
  minimal_version: Add a discovery-run header to the next experiment artifact with trigger, decision consumer, known-set scope, finding-count cap of none, and a stop rule based on useful-new rate or an already-covered decision queue. This is reporting structure, not a new approval gate.
  alternatives:
    - Keep issuing discovery passes whenever a helper is available.
    - Schedule a continuous model scout alongside the deterministic Sentinel.
    - Stop model-backed discovery entirely and rely only on deterministic signals.
  evidence:
    - "Observed: MAP_System/artifacts/experiments/clearfront-discovery-agent-adjudication-2026-07-17.md concludes ADOPT WITH REFINEMENT and says not to run Discovery continuously as a paid/model session; it names phase boundaries, architectural changes, and unexplained Sentinel patterns as appropriate triggers."
    - "Observed: The same adjudication reports a four-item sample only, says yield is not yet stable, and requires useful-new rate, rejection quality, scope drift, and curation time rather than a finding quota."
    - "Observed: MAP_System/shared/hpom.md routing questions 4-6 require a helper to justify coordination cost, have explicit outputs/stopping conditions, and remain visible/reachable."
    - "Observed: MAP_System/notes/system-improvement-kickoff.md's continuous-improvement section says not to keep an agent busy to produce activity and requires a completed pass to return to visible listening until it has another concrete question."
    - "Observed: MAP_System/inbox/helpers/helper-discovery-system-lifecycle.md and helper-philosophical-discovery-2026-07-18.md establish successive broad discovery passes during the same improvement lane."
    - "Inference: The missing control is not visibility or proposal-only authority; it is an explicit admission rule that connects the cost of another semantic pass to a decision it can improve."
  confidence: high
  scores:
    user_value: 4
    goal_alignment: 5
    necessity: 4
    novelty: 4
    leverage: 5
    confidence: 5
    reversibility: 5
    complexity: 1
    maintenance_burden: 1
    scope_risk: 2
  recommendation: investigate
  reasoning_summary: This preserves the pilot's demonstrated value while honoring its own limit. It improves flow by making discovery a response to evidence or a decision need, not a substitute for implementation or a way to demonstrate creativity.

- title: Do not turn the deterministic Sentinel into a continuous model scout
  classification: rejected_idea
  trigger:
    - emergence
    - analogy
    - evaluation
  problem: The Sentinel's incomplete recall can make a constantly running model interpreter appear to be the obvious way to improve discovery coverage.
  user_impact: Continuous interpretation might notice more associations, but it would introduce recurring token cost, idea noise, and an opaque attention drain without showing that the additional proposals improve decisions.
  proposed_response: Reject this expansion. Keep the Sentinel deterministic and source-bounded; invoke the visible Discovery Agent only under the event-triggered experiment above.
  minimal_version: No implementation.
  alternatives:
    - Add approved durable review artifacts as another deterministic Sentinel source, then remeasure recall.
    - Run bounded visible semantic passes at named decision boundaries.
  evidence:
    - "Observed: MAP_System/artifacts/tests/emergence-sentinel-pilot.md reports 1/4 recall and correctly limits the Sentinel to durable signals rather than claiming general semantic discovery."
    - "Observed: MAP_System/tasks/TASK-224.json explicitly prohibits a continuous paid-model session and automatic promotion."
    - "Observed: MAP_System/artifacts/experiments/clearfront-discovery-agent-adjudication-2026-07-17.md reaches the same non-continuous conclusion after a useful pilot."
    - "Inference: Low deterministic recall establishes a role distinction, not evidence that an always-on paid interpreter has positive net yield."
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
  reasoning_summary: The Sentinel and Discovery Agent are complementary because one is cheap and deterministic while the other is bounded judgment. Merging them into continuous model monitoring would erase that useful boundary.

- title: Do not replace the durable multi-source architecture with a single autonomous control plane
  classification: rejected_idea
  trigger:
    - foundational_assumption
    - divergence
    - contradiction
  problem: The lifecycle's file, SQLite, event, status, handoff, and decision records can look like excessive structure compared with a single autonomous controller.
  user_impact: A single controller could reduce some synchronization work, but it would concentrate mutable authority, obscure human-readable evidence, and make visible review/recovery depend on one runtime interpretation.
  proposed_response: Reject replacement. Continue testing the narrower proven seams—READY-contract reconciliation, bootstrap visibility, and read-only attention projections—before considering any architectural consolidation.
  minimal_version: No implementation.
  alternatives:
    - Generate read-only views from canonical sources.
    - Reconcile one inconsistent predicate or cross-source seam at a time.
  evidence:
    - "Observed: MAP_System/shared/architecture.md assigns distinct responsibilities to durable files, SQLite atomic runtime state, LangGraph routing, scripts, and agents."
    - "Observed: MAP_System/shared/requirements.md requires canonical project state outside LangGraph and retains file-backed task records as a human-readable mirror."
    - "Observed: MAP_System/artifacts/experiments/map-discovery-practice-lifecycle-2026-07-18.md already identifies two narrow lifecycle-contract experiments rather than evidence of a failing overall architecture."
    - "Observed: MAP_System/artifacts/experiments/system-improvement-plan-challenge-2026-07-18.md recommends reversible tests of individual foundational assumptions and explicitly avoids replacing MAP up front."
    - "Inference: The evidenced problem is inconsistent interpretation at particular transitions, not a demonstrated inability of the durable-source architecture to support flow."
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
  reasoning_summary: Foundational reconsideration should compare concrete failure modes with simpler reversible alternatives. No evidence here supports exchanging inspectable distributed authority for a new autonomous control plane.

- title: Do not remove explicit review and release gates in the name of autonomous flow
  classification: rejected_idea
  trigger:
    - paradox
    - analogy
    - evaluation
  problem: Gates can delay delivery and produce artifacts, so removing them may appear to maximize autonomy and token economy.
  user_impact: Eliminating gates would shorten the visible path but remove the independent challenge that has caught real defects and would turn speed into unverified state change.
  proposed_response: Reject blanket gate removal. Continue calibrating review weight by risk and measure gates against escaped defects and curation cost, as the ClearFront model already demonstrated.
  minimal_version: No implementation.
  alternatives:
    - Use high/medium/low risk lanes with one review at an appropriate batch boundary.
    - Automate deterministic checks while retaining independent judgment at high-risk boundaries.
  evidence:
    - "Observed: MAP_System/notes/review-guide.md's Risk-Tiered Review section explicitly distinguishes high-risk independent review from batchable low-risk work."
    - "Observed: MAP_System/artifacts/experiments/system-improvement-plan-challenge-2026-07-18.md finds the plan's refusal to add extra discovery/review steps proportionate, rather than recommending their removal."
    - "Observed: MAP_System/shared/hpom.md keeps final integration and independent approval with the appropriate authority tier."
    - "Inference: The useful correction is calibration and automation of repeatable checks, not removing the authority boundary that protects project truth."
  confidence: high
  scores:
    user_value: 1
    goal_alignment: 3
    necessity: 1
    novelty: 1
    leverage: 1
    confidence: 5
    reversibility: 2
    complexity: 4
    maintenance_burden: 4
    scope_risk: 5
  recommendation: reject
  reasoning_summary: Autonomy and safety are not opposites when deterministic checks and risk-calibrated review share the work. Removing gates would answer a flow-cost concern by discarding the evidence boundary.
```

## Pass coverage and method note

All seven Discovery passes were performed independently over MAP's purpose, lifecycle, omissions, emergent leverage, analogies, contradictions, divergence, and evaluation. The review specifically tested the requested foundational tensions: autonomy against visibility, durable evidence against token cost, explicit gates against real flow, and system structure against the standing software-delivery purpose. Existing decision support was checked before retaining a proposal: DEC-028 has already selected and delivered its first software proving slice (TASK-205), while the ClearFront pilot has already established the Discovery Agent's non-continuous role. One proportionate refinement survived: make further semantic discovery admission event-triggered and yield-accountable. Three foundational alternatives were preserved as rejected ideas. No implementation, task, policy, decision, E/I promotion, status, or task-state files were changed.
