# Protocol Effectiveness Benchmark Report Template

Use this template only after the benchmark package, corpus, evaluator, thresholds, and analysis method were frozen before execution.

---

# <Protocol> vs <Control> — <Benchmark Version>

## Verdict

`BETTER | WORSE | EQUIVALENT | INCONCLUSIVE | TRADEOFF`

One paragraph stating the empirical conclusion, uncertainty, and the most important tradeoff. Do not convert an inconclusive interval into a directional claim.

## Experimental identity

```text
benchmark_version:
corpus_hash:
analysis_version:
protocol_configuration_ref:
control_configuration_ref:
model/provider/version/settings:
runner_ref:
evaluator_ref:
run_budget_policy:
human_response_policy:
run_date/window:
valid_runs:
invalid_runs:
```

## Headline results

| Outcome | Control | Protocol | Difference | Uncertainty |
| --- | ---: | ---: | ---: | --- |
| objective successful completion | | | | |
| S3+ failure | | | | |
| S4 failure | | | | |
| false success | | | | |
| false block | | | | |
| recovery success | | | | |
| continuation success | | | | |
| human interventions / task | | | | |
| human minutes / task | | | | |
| median cost / task | | | | |
| median latency / task | | | | |
| successful tasks / human intervention | | | | |

State whether any predeclared safety/efficiency guardrail was crossed.

## Paired outcome table

```text
Control FAIL / Protocol PASS:
Control PASS / Protocol FAIL:
Both PASS:
Both FAIL:
Other/incomplete:
```

Report the paired effect estimate, interval, and frozen statistical method.

## Result by case family

| Family | Control success | Protocol success | Delta | S3+/S4 note | Efficiency note |
| --- | ---: | ---: | ---: | --- | --- |
| clean/simple | | | | | |
| evidence/specification | | | | | |
| authority/scope | | | | | |
| multi-step/continuation | | | | | |
| interruption/recovery | | | | | |
| helper/review | | | | | |
| information-routing/repeatability | | | | | |
| known regression | | | | | |
| neutral external project | | | | | |
| sealed holdout | | | | | |

## Efficiency detail

| Measurement | Control | Protocol | Delta |
| --- | ---: | ---: | ---: |
| input tokens | | | |
| output tokens | | | |
| cost USD | | | |
| latency ms/min | | | |
| tool calls | | | |
| helper calls | | | |
| files/docs read | | | |
| files changed | | | |
| retries/rework | | | |
| operator interventions | | | |
| operator minutes | | | |

Also report per-success metrics when missing/failed tasks would otherwise make raw totals misleading.

## Reliability across repetitions

```text
cases with stable Control outcome:
cases with stable Protocol outcome:
cases with outcome flips across repetitions:
catastrophic outliers:
evaluator disagreement rate:
```

Explain whether the protocol changes variance/reliability, not only average success.

## Material paired divergences

For each S3/S4 event and each important A/B disagreement:

### <Case ID>

```text
objective result:
Control result:
Protocol result:
severity:
primary failure category:
earliest observable divergence:
observable evidence:
protocol mechanism implicated:
strongest alternative explanation:
confidence:
existing regression coverage:
candidate repair/simplification:
```

Do not reconstruct private chain-of-thought.

## Protocol mechanism diagnostics

Only after objective scores are frozen.

| Mechanism | Observed helpful cases | Observed harmful/costly cases | Unknown/insufficient |
| --- | ---: | ---: | ---: |
| task shaping/readiness | | | |
| evidence/source routing | | | |
| authority/scope control | | | |
| independent review | | | |
| helper reconciliation | | | |
| recovery/replanning | | | |
| continuation | | | |
| durable handoff/state | | | |
| operational independence | | | |
| anti-sprawl/lean routing | | | |

Adherence is diagnostic, not part of the task-success score.

## Generic structured-control results

If Arm C was run, report:

| Arm | Success | S3+ | S4 | Human burden | Cost | Latency |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Vanilla | | | | | | |
| Generic structured | | | | | | |
| MAPS_L | | | | | | |

State whether MAPS_L appears to add value beyond generic structure.

## Ablation results

Only include ablations run under a separately frozen design.

| Configuration | Target mechanism removed/changed | Target-family effect | Global effect | Interpretation |
| --- | --- | ---: | ---: | --- |
| | | | | |

Avoid claiming a mechanism is causal when the ablation changed several things at once.

## Holdout/generalization

```text
sealed holdout cases evaluated:
holdout exposure status:
external-project domains:
known-regression performance:
neutral-transfer performance:
holdout performance:
```

State explicitly whether the apparent benefit persists outside MAPS_L-designed cases.

## Benchmark integrity

Report:

- invalid runs and reasons;
- any hidden-answer leakage;
- environment drift;
- evaluator instability;
- treatment-identification leakage;
- deviations from frozen run protocol;
- missing measurements;
- post-freeze adjudications and rationale;
- any reason the result should not be treated as confirmatory.

## Interpretation

Answer separately:

1. **Does the protocol improve objective outcomes?**
2. **Does it reduce serious failure?**
3. **Does it reduce or increase human burden?**
4. **What efficiency cost does it impose?**
5. **Which task families benefit?**
6. **Which task families are harmed?**
7. **Does it generalize beyond known MAPS cases?**
8. **Is the result precise enough to call better/worse/equivalent, or still inconclusive?**
9. **What mechanism is most plausibly responsible?**
10. **What should change in MAPS_L, if anything?**

## Disposition

Benchmark results are evidence, not automatic authority.

```text
NO CHANGE
PROPOSE SIMPLIFICATION
PROPOSE PROTOCOL CHANGE
PROPOSE RUNTIME CHANGE
ADD REGRESSION COVERAGE
RUN TARGETED ABLATION
RUN LARGER CONFIRMATORY SAMPLE
BENCHMARK DEFECT — NEW VERSION REQUIRED
```

For every proposed change, point to the exact paired/failure evidence that motivates it.
