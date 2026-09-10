# References and Provenance

Status: supporting references for the draft benchmark specification.

The benchmark design should remain understandable and executable from its own frozen specification. These references explain the design lineage; they are not runtime authority.

## MAPS_L internal owners

### Repository operating contract

- [`../../../AGENTS.md`](../../../AGENTS.md)
  - Evidence outranks prose.
  - Capability does not create permission.
  - Do not silently expand scope.
  - Do not idle while authorized actionable work remains.
  - Do not manufacture work after success.
  - Independent review where required.
  - No process for process's sake.

### Agent-grade task readiness

- [`../../../playbook/AGI_STANDARD.md`](../../../playbook/AGI_STANDARD.md)
  - Fresh-Agent, No-Guess, Scope, Authority, Completion, Failure, and Continuation tests.
  - Useful benchmark dimensions, but not success points simply because MAPS_L defines them.

### Task lifecycle

- [`../../../playbook/TASK_LIFECYCLE.md`](../../../playbook/TASK_LIFECYCLE.md)
  - Shaping, execution, verification, recovery, continuation, independent review, and operational independence.

### Simulation design

- [`../../../playbook/SIMULATION_DESIGN.md`](../../../playbook/SIMULATION_DESIGN.md)
  - Existing reusable owner for controlled role/task scenarios, observable route choice, controlled traps, and precise failure classes.

### Checks and balances

- [`../../../docs/CHECKS_AND_BALANCES.md`](../../../docs/CHECKS_AND_BALANCES.md)
  - Risk-proportional verification and independent review expectations.

### Repair and learning

- [`../../../playbook/REPAIR_AND_LEARNING.md`](../../../playbook/REPAIR_AND_LEARNING.md)
  - Existing failure capture, recurrence, mechanical countermeasure, live verification, and frozen regression-case path.

### Existing frozen end-to-end benchmark

- [`../maps-end-to-end-benchmark-v1.json`](../maps-end-to-end-benchmark-v1.json)
  - Existing Layer-2 controlled and Layer-3 real-world outcome scenarios.
  - Preserves `PASS`, `FAIL`, `UNKNOWN`, and `NOT_RUN`.
  - Explicitly avoids collapsing blocker, quality, friction, cost, and outcome into one weighted score.
  - The protocol-effectiveness benchmark should reuse rather than duplicate these scenarios when they fit.

### Existing deterministic evaluation runtime

- [`../../../runtime/evaluation/evaluator.py`](../../../runtime/evaluation/evaluator.py)
  - Same-corpus baseline/candidate comparison.
  - Immutable configuration references.
  - Frozen case identity.
  - Cost and latency measurements.
  - No automatic promotion from score.

- [`../../../runtime/evaluation/regression_case.py`](../../../runtime/evaluation/regression_case.py)
  - Frozen incident/regression representation.
  - Sanitized portable fixtures.
  - Incident categories and expected properties.
  - Explicit non-automatic promotion.

## External evaluation references

These sources motivate general evaluation-design choices. They do not make MAPS_L-specific claims.

### Holistic Evaluation of Language Models (HELM)

Percy Liang et al., 2022, arXiv:2211.09110

https://arxiv.org/abs/2211.09110

Relevant design lesson: use standardized scenarios and multiple metrics so accuracy does not hide efficiency, robustness, calibration, or other tradeoffs.

### Do More Agents Help? Controlled and Protocol-Aligned Evaluation of LLM Agent Workflows

Yuhang Fu et al., 2026, arXiv:2606.05670

https://arxiv.org/abs/2606.05670

Relevant design lesson: when comparing agent workflows, normalize benchmark loading, tool access, answer contracts, accounting, and trajectory logging so workflow differences are interpretable rather than confounded by unequal substrates.

### Judging the Judges: A Systematic Study of Position Bias in LLM-as-a-Judge

Lin Shi et al., 2024, arXiv:2406.07791

https://arxiv.org/abs/2406.07791

Relevant design lesson: pairwise LLM evaluators can exhibit position bias. Anonymize conditions, counterbalance presentation order, prefer objective/absolute scoring first, and measure evaluator stability.

### NLP Evaluation in trouble: On the Need to Measure LLM Data Contamination for each Benchmark

Oscar Sainz et al., Findings of EMNLP 2023.

https://aclanthology.org/2023.findings-emnlp.722/

Relevant design lesson: exposure to benchmark material can inflate apparent capability. For a protocol-development project, the analogous risk is repeatedly tuning the protocol to a known benchmark. Preserve fresh holdouts and disclose exposure.

### LLM Benchmark Datasets Should Be Contamination-Resistant

Ali Al-Lawati et al., 2026, arXiv:2605.19999

https://arxiv.org/abs/2605.19999

Relevant design lesson: public, repeatedly exposed benchmarks face contamination/generalization problems; sealed or refreshed challenge material helps distinguish genuine generalization from benchmark familiarity.

## Statistical references/principles

The benchmark uses standard paired-experiment principles rather than prescribing one universal test:

- analyze matched A/B case outcomes as paired data;
- report effect magnitude and uncertainty, not only p-values;
- account for repeated runs nested within the same case;
- predeclare the smallest practically meaningful difference;
- permit `INCONCLUSIVE` when precision is insufficient;
- separate confirmatory analysis from exploratory subgroup/ablation analysis.

The exact confirmatory method should be frozen with the executable benchmark release after the case count, repetition structure, and target precision are known.

## Reference-use rule

External papers support benchmark methodology, not MAPS_L effectiveness. The effectiveness claim must come from the actual controlled results.
