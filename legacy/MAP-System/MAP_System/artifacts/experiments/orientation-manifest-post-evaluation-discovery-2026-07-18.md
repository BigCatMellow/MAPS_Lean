# EXP-0004 Orientation Manifest — Post-Evaluation Discovery Check

## Verdict

**admit_refined_experiment.** The independent evaluation identified a bounded, falsifiable repeat: a new scenario, six-row frozen rubric, explicit read-before-mutate scoring, blinded evaluator, predeclared scenario-local threshold, and preserved control evidence. It tests the observed failure without changing startup policy, indexes, or runtime behavior. One small guard below clarifies that the dynamic control must be retained as content, not only as hashes.

## Findings

```yaml
- title: Retain the complete point-in-time control packet, with hashes as supplemental provenance
  classification: likely_requirement
  trigger:
    - evaluation
    - recovery
    - evidence_integrity
  problem: The baseline could verify only the 89.00% arithmetic because the original concatenated control and dynamic runner/hcom outputs were not retained. The proposed repeat permits a retained control snapshot or content hashes. Hashes alone can confirm later source identity, but they cannot reconstruct or independently inspect a point-in-time dynamic control that included runner and hcom output.
  user_impact: A refined experiment could again claim a scenario-local reduction without allowing a later evaluator to reproduce the control bytes or inspect whether the control included the same live-state uncertainty as the treatment.
  proposed_response: Require the next experiment to store the exact concatenated raw control packet or immutable per-source snapshots as a non-canonical experiment artifact, record its hash and the measurement command, and compare the treatment against that retained content. Hash individual static sources as additional provenance, not a substitute for the dynamic control.
  minimal_version: Add one required pre-treatment control artifact containing the raw concatenated scenario sources and captured command outputs, followed by wc -w -c and sha256 output recorded in the evaluation.
  alternatives:
    - Retain hashes only and trust later source reconstruction.
    - Reuse the current treatment's historical control number.
    - Build a persistent manifest or index runtime to make measurements reproducible.
  evidence:
    - "Observed: MAP_System/artifacts/experiments/orientation-manifest-baseline-evaluation-2026-07-18.md states that the raw concatenated control and point-in-time hcom output were not preserved, so the evaluator could verify stated arithmetic but not the historical 51,378-byte measurement."
    - "Observed: EXP-0004's completed Result requires a future test to use a retained/hashes control, an exact wc command, and a predeclared threshold."
    - "Observed: the baseline evaluator recommends a retained concatenated control snapshot or content hashes, while noting that current file sizes are different objects and cannot substitute for the historical baseline."
    - "Inference: For dynamic evidence, a hash without retained content preserves identity only if the original content remains obtainable; it does not preserve the control needed for independent evaluation."
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
  reasoning_summary: This is an experiment-local evidence correction, not a new data store. It makes the already-proposed repeat reproducible at the one point where the baseline was not.

- title: Do not expand the refined repeat into a manifest runtime, index, or startup-policy project
  classification: rejected_idea
  trigger:
    - scope_drift
    - divergence
    - non_forcing
  problem: The promising scenario-local compression and 5/6 safety result could invite a generalized runtime or canonical startup replacement before the refined experiment has established repeatable correctness.
  user_impact: Premature expansion would add a new authority/retrieval layer and maintenance burden while the experiment has not yet shown a safe immediate-action result or any reduction of the mandatory startup contract.
  proposed_response: Reject expansion. Admit only the one refined, independently evaluated scenario; retain the existing canonical orientation unchanged regardless of its outcome.
  minimal_version: No implementation beyond the next experiment's artifacts.
  alternatives:
    - Run the six-row refined scenario with retained control evidence.
    - Park the work after that repeat if the evaluator again misses a safety dimension or fails the threshold.
  evidence:
    - "Observed: EXP-0004 limits the manifest to a test packet and its completed Result explicitly says no runtime, index, AGENTS, policy, or task-state change follows."
    - "Observed: the baseline evaluation says the 89.00% number is scenario-local only and cannot prove mandatory-startup savings."
    - "Observed: the preflight artifact already rejected building a generic manifest runtime before a fixed-scenario experiment."
    - "Inference: The observed failure calls for a tighter control, not a broader system."
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
    scope_risk: 5
  recommendation: reject
  reasoning_summary: The refined experiment is already the smallest test of the missing read-before-mutate and reproducibility controls. Generalization would answer a different question without evidence.
```

## Pass coverage and method note

This was an event-triggered post-evaluation pass only. It reviewed the frozen experiment intent, preflight, canonical control, treatment, and independent baseline evaluation for the new decision point: whether the specified repeat tests the observed failure. The repeat is admitted with one evidence-retention clarification. No broad discovery cadence, runtime/index/policy proposal, or canonical-state change is recommended.
