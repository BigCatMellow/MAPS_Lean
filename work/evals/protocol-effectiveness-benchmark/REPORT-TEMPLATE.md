# Protocol Effectiveness Benchmark Report Template

Status: report schema only. Freeze its version/hash before scored execution.

Use this template only after the benchmark line, corpus, treatment/threshold manifests, evaluator stack, and analysis rules were frozen and independently approved.

---

# <Tested Protocol> — <Benchmark Line / Version>

## Verdicts

Report each permitted comparison separately:

```text
B vs A — tested protocol vs no-protocol control:
BETTER | WORSE | EQUIVALENT | INCONCLUSIVE | TRADEOFF
confirmatory: yes | no

B vs C — tested protocol vs generic structured control (Standard/Full):
BETTER | WORSE | EQUIVALENT | INCONCLUSIVE | TRADEOFF
confirmatory: yes | no
```

An experimental-integrity failure maps to the owner-defined `INCONCLUSIVE` verdict and `confirmatory: no`; the report template does not define a sixth verdict label.

Do not call B−A a MAPS-specific contribution. B−C is required for that claim.

State the empirical conclusion, interval, applicable guardrails, and verdict-precedence rule. Smoke receives no directional/equivalence verdict.

## Experimental identity

```text
benchmark_line/version:
target_work_sampling_manifest_hash:
corpus_hash:
holdout_bundle_hash:
treatment_surface_manifest_hash:
threshold_manifest_hash:
generic_control_hash:
analysis_rule_hash:
model/provider/version/settings:
sampling_reference_model/provider/version:
sampling_reference_training_cutoff:
runner_ref:
normalizer_ref:
primary_evaluator_ref:
second_evaluator_ref:
adjudication_policy_ref:
run_budget:
human_response_policy/matcher_ref:
pair_time_window:
run_date/window:
pre_registration_commit:
A instruction length / context cost:
B instruction length / context cost:
C instruction length / context cost:
```

## Population and exposure state

```text
primary cases total:
unexposed FROZEN_STANDARD cases:
SEALED_HOLDOUT cases:
KNOWN_REGRESSION diagnostic cases:
external-project share:
PROCEED/BLOCK share:
NONE/STRESS/COUNTERWEIGHT share:
overlay-review reclassifications by original/final class:
primary cases with non-empty seeded_stress_families[]:
sampling cutoff relation POST_CUTOFF / PRE_OR_WITHIN_CUTOFF / UNKNOWN:
execution-model cutoff relation POST_CUTOFF / PRE_OR_WITHIN_CUTOFF / UNKNOWN:
standard cases retired from current confirmatory inference due exposure:
holdout look number / allowed looks:
```

State whether the frozen corpus satisfied all target-population and stress/counterweight prevalence rules.

## Headline primary result

Primary measure: **case-correct terminal outcome**.

| Comparison | Tested arm | Comparator | Difference | Frozen 95% interval | Primary status |
| --- | ---: | ---: | ---: | --- | --- |
| B−A | | | | | |
| B−C | | | | | |

### Terminal strata

| Stratum | A success | B success | C success | B−A | B−C |
| --- | ---: | ---: | ---: | ---: | ---: |
| PROCEED | | | | | |
| BLOCK | | | | | |
| External project | | | | | |
| MAPS_HOME | | | | | |
| NONE / no seeded trap | | | | | |
| STRESS | | | | | |
| COUNTERWEIGHT | | | | | |
| Seeded §6.2 stress present | | | | | |
| Unexposed FROZEN_STANDARD | | | | | |
| SEALED_HOLDOUT | | | | | |

Known regressions are reported separately and never mixed into H1/H5 primary success.

## Terminal calibration

| Metric | A | B | C |
| --- | ---: | ---: | ---: |
| TRUE_SUCCESS | | | |
| TRUE_BLOCK | | | |
| TRUE_BLOCK_WITH_REASON_ERROR | | | |
| FALSE_SUCCESS | | | |
| of which: declared BLOCKED after forbidden effect | | | |
| FALSE_BLOCK | | | |
| BLOCKED_WRONG_CLASS | | | |
| INCOMPLETE | | | |
| INCOMPLETE_CALIBRATION | | | |
| over-continuation | | | |

The subset row above does not define a new terminal class; `CASE-DESIGN.md` owns terminal classifications.

## Safety and reliability

| Metric | A | B | C | Frozen threshold / rule | Crossing basis |
| --- | ---: | ---: | ---: | --- | --- |
| S3+ rate | | | | | |
| adjudicated S4 raw count | | | | `S4_RULE_V1` | exact case-level rule |
| B-exclusive S4 vs A | | | N/A | | exact case-level rule |
| A-exclusive S4 vs B | | | N/A | | exact case-level rule |
| B-exclusive S4 vs C | N/A | | | | exact case-level rule |
| C-exclusive S4 vs B | N/A | | | | exact case-level rule |
| false success | | | | | |
| false block | | | | | |
| scope/authority violation | | | | | |
| duplicate effect | | | | | |
| review-induced harm | | | | | |
| helper-induced harm | | | | | |
| context/budget exhaustion | | | | | |

State explicitly which `S4_RULE_V1` and S3 guardrail conditions fired, if any.

## Human burden and responder integrity

| Metric | A | B | C |
| --- | ---: | ---: | ---: |
| avoidable questions/interventions | | | |
| required human-only boundary/preference interactions | | | |
| predefined experimental responses | | | |
| observed human minutes | | | |
| responder misroutes | | | |

Do not estimate human minutes. Interpret question count beside false-block, authority, and asking-is-correct outcomes.

## Efficiency

| Measurement | A | B | C |
| --- | ---: | ---: | ---: |
| input tokens | | | |
| output tokens | | | |
| context/cache consumption | | | |
| cost USD | | | |
| latency | | | |
| tool calls | | | |
| helper calls | | | |
| searches | | | |
| retries/rework | | | |
| target files changed | | | |
| process-sidecar artifact count | | | |

Raw file/document count may appear only as a secondary diagnostic. Prefer token/context consumption.

Also report per-case-correct-success efficiency when failures would distort raw totals.

## Frozen headline-secondary guardrails

| Metric | Benefit threshold | Harm threshold | Crossing basis | A/B crossing | B/C crossing |
| --- | --- | --- | --- | --- | --- |
| | | | | | |

`TRADEOFF` may arise only from the explicit `S4_RULE_V1` branches or preregistered registered-guardrail branches defined by `TRADEOFF_RULE_V1`. Exploratory or post-hoc metrics may never trigger it.

## Verdict derivation

For each comparison show the exact frozen path:

```text
PRIMARY_STATUS:
S4_RULE_V1 result:
S3/other adverse guardrails crossed + crossing bases:
registered benefit thresholds crossed + crossing bases:
TRADEOFF_RULE_V1 result:
VERDICT_PRECEDENCE_V1 final label:
```

## H5 generalization consistency

For B vs each claimed comparator:

```text
external-project point estimate:
unexposed holdout point estimate:
external exclusive-S4 relation:
holdout exclusive-S4 relation:
H5_CONSISTENCY_V1: SUPPORTED_BETTER | SUPPORTED_WORSE | SUPPORTED_EQUIVALENT | INCONCLUSIVE
```

Do not upgrade an underpowered holdout consistency check into a standalone effectiveness claim.

## Parametric-recall sensitivity

```text
sampling reference model/provider/version:
sampling reference documented cutoff (or UNKNOWN):
POST_CUTOFF / PRE_OR_WITHIN_CUTOFF / UNKNOWN case counts under sampling reference:
executed model/provider/version:
executed model documented cutoff (or UNKNOWN):
POST_CUTOFF / PRE_OR_WITHIN_CUTOFF / UNKNOWN case counts under executed model:
external/H5 direction on POST_CUTOFF sensitivity subset:
```

The executed-model relation is recomputed deterministically from the frozen resolution dates; it does not retroactively alter case inclusion or weights.

## Paired outcomes and repetitions

```text
A fail / B pass:
A pass / B fail:
both A/B pass:
both A/B fail:

C fail / B pass:
C pass / B fail:
both B/C pass:
both B/C fail:
```

Report the frozen clustered/bootstrap/hierarchical method, per-case pass fractions, outcome flips, latency/cost dispersion, and catastrophic outliers.

## INVALID and UNKNOWN sensitivity

```text
original invalid executions by arm and reason:
invalid pair/block count:
replacement pair/block IDs:
UNKNOWN by arm:
pessimistic UNKNOWN sensitivity:
optimistic UNKNOWN sensitivity:
paired best/worst-case interval:
```

Agent-caused resource/context/runaway failures must not appear as INVALID.

## Snapshot/secret integrity

```text
history-free/sanitized snapshot rule:
recursive auto-load inventory result:
benchmark-record scrub result:
case-secret canary result:
canary scope included VCS history/objects: yes/no
hidden-material storage location class (not secret path):
```

Any answer-key leak makes the affected scored comparison non-confirmatory.

## Blinding and normalization integrity

```text
blinding-check sample size:
predeclared guess-accuracy ceiling:
guess accuracy:
confidence interval:
upper bound <= ceiling: yes/no
guesser capability vs semantic evaluator:
normalization audit sample per arm:
normalization-loss/error rate by arm:
semantic evidence headline-valid: yes/no
```

Do not treat failure to reject chance as proof of blinding.

## Material paired divergences

For each S3/S4 event and important A/B or B/C disagreement:

### <Case ID / repetition>

```text
objective result:
arm results:
severity:
primary failure category:
earliest observable divergence:
observable evidence:
protocol mechanism implicated:
strongest alternative explanation:
confidence:
current exposure consequence for later protocol versions:
existing regression coverage:
candidate repair/simplification:
```

Do not reconstruct private chain-of-thought. Per-case divergence analysis exposes a standard/holdout case for later protocol versions.

## Protocol mechanism diagnostics

Only after primary outcome grades are frozen.

| Mechanism | Helpful observations | Harmful/costly observations | Unknown |
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

Adherence is diagnostic only.

## Generic structured-control interpretation

Standard/Full must include Arm C before a MAPS-specific contribution claim.

```text
B−A interpretation: tested protocol vs no-protocol control
B−C interpretation: MAPS-specific incremental effect vs generic structured control
```

State whether B−C supports additional value beyond competent generic structure.

## Known-regression diagnostics

Report separately:

```text
cases:
results by arm/system as applicable:
relationship to existing runtime evaluator/Experiment S:
```

Never mix these cases into H1/H5 primary success.

## Benchmark integrity and deviations

Report snapshot drift, hidden-answer leakage, treatment contamination, evaluator instability, normalization loss, responder misroutes, invalid pairs, deviations from frozen procedure, post-freeze adjudications, exposed-case exclusions, missing measurements, and any reason the result is not confirmatory.

## Interpretation

Answer separately:

1. Does the protocol improve case-correct terminal outcomes?
2. Does it reduce or increase serious failure?
3. Does it reduce or increase human burden?
4. What efficiency/context cost does it impose?
5. Does B−C support MAPS-specific value beyond generic structure?
6. Do no-trap, stress, and counterweight strata tell different stories?
7. Does the effect remain directionally consistent on external and unexposed holdout work?
8. Is precision sufficient for the final label?
9. What observed mechanism most plausibly explains the difference?
10. What should change, if anything?

## Disposition

Benchmark evidence is not automatic authority.

```text
NO CHANGE
PROPOSE SIMPLIFICATION
PROPOSE PROTOCOL CHANGE
PROPOSE RUNTIME CHANGE
ADD DEV/REGRESSION COVERAGE
RUN TARGETED ABLATION
REFRESH UNEXPOSED STANDARD/HOLDOUT
RUN LARGER CONFIRMATORY SAMPLE
BENCHMARK DEFECT — NEW VERSION/LINE REQUIRED
```

Tie every proposed change to exact paired/failure evidence.
