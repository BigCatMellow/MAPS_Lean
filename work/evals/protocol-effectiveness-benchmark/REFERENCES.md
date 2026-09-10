# References and Provenance

Status: supporting references for the draft benchmark specification.

These sources explain design lineage. They do not define Experiment P outcome criteria, pool weights, thresholds, or verdict rules, and they do not prove MAPS_L effectiveness.

## MAPS_L internal owners

- [`../../../AGENTS.md`](../../../AGENTS.md) — repository operating contract. Its invariants may motivate hypotheses/diagnostic labels but must not become hidden success requirements.
- [`../../../playbook/AGI_STANDARD.md`](../../../playbook/AGI_STANDARD.md) — MAPS task-readiness method. AGI compliance is diagnostic only in Experiment P.
- [`../../../playbook/TASK_LIFECYCLE.md`](../../../playbook/TASK_LIFECYCLE.md) — MAPS lifecycle method. Its records/states are not P success points.
- [`../../../playbook/SIMULATION_DESIGN.md`](../../../playbook/SIMULATION_DESIGN.md) — reusable MAPS simulation method. Its mandatory live updates, route reporting, and observability failure classes are **not imported into Experiment P primary grading**.
- [`../../../docs/CHECKS_AND_BALANCES.md`](../../../docs/CHECKS_AND_BALANCES.md) — MAPS risk/review method; useful for MAPS-side diagnostics, not a control-arm requirement unless the common task fixture requires equivalent behavior.
- [`../../../playbook/REPAIR_AND_LEARNING.md`](../../../playbook/REPAIR_AND_LEARNING.md) — owner for post-result repair/regression promotion.
- [`../maps-end-to-end-benchmark-v1.json`](../maps-end-to-end-benchmark-v1.json) — existing MAPS end-to-end/runtime protocol. Its MAPS-shaped properties are **not reused as Experiment P primary properties**. They remain separate diagnostics/Experiment S evidence.
- [`../../../runtime/evaluation/evaluator.py`](../../../runtime/evaluation/evaluator.py) — deterministic MAPS frozen-regression comparator. It is not the Experiment P scorer: its one-result-per-case, portable Run Record provenance, limited measurement schema, and property-regression semantics do not represent A/B/C × repetitions.
- [`../../../runtime/evaluation/regression_case.py`](../../../runtime/evaluation/regression_case.py) — MAPS runtime regression representation. Existing runtime-mechanism cases remain outside P unless independently re-authored as protocol-neutral agent tasks.

## External evaluation references

External sources motivate methodology only.

### Holistic Evaluation of Language Models (HELM)

Percy Liang et al., 2022, arXiv:2211.09110  
https://arxiv.org/abs/2211.09110

Lesson: standardized scenarios and multiple metrics help prevent one accuracy number from hiding robustness, calibration, efficiency, or other tradeoffs.

### Do More Agents Help? Controlled and Protocol-Aligned Evaluation of LLM Agent Workflows

Yuhang Fu et al., 2026, arXiv:2606.05670  
https://arxiv.org/abs/2606.05670

Lesson: normalize task loading, tool access, answer contracts, accounting, and trajectory logging so workflow comparisons are not substrate comparisons.

### Judging the Judges: A Systematic Study of Position Bias in LLM-as-a-Judge

Lin Shi et al., 2024, arXiv:2406.07791  
https://arxiv.org/abs/2406.07791

Lesson: evaluator position/order and presentation can bias pairwise judgments; use objective scoring first, counterbalance, and measure blinding/stability.

### NLP Evaluation in trouble: On the Need to Measure LLM Data Contamination for each Benchmark

Oscar Sainz et al., Findings of EMNLP 2023  
https://aclanthology.org/2023.findings-emnlp.722/

Lesson: exposure can inflate benchmark performance; protocol-development benchmarks need explicit standard/holdout exposure accounting.

### LLM Benchmark Datasets Should Be Contamination-Resistant

Ali Al-Lawati et al., 2026, arXiv:2605.19999  
https://arxiv.org/abs/2605.19999

Lesson: repeatedly exposed public benchmarks are vulnerable to overfitting; sealed/refreshed challenge material improves generalization evidence.

## Statistical principles

The benchmark uses standard paired-experiment principles:

- preserve matched case blocks;
- account for repetitions nested within case;
- report effect magnitude plus uncertainty;
- predeclare practical margin, guardrails, and analysis before the first scored run;
- treat equivalence as requiring affirmative interval evidence, not failure to reject difference;
- keep critical failures visible even when rare;
- separate confirmatory endpoints from exploratory subgroups;
- permit `INCONCLUSIVE`.

The exact executable rules are owned by the package's specification/scoring files, not this references file.

## Reference-use rule

No external or internal reference may substitute for controlled outcome evidence. A MAPS document can motivate what to test; it cannot define “MAPS wins.”
