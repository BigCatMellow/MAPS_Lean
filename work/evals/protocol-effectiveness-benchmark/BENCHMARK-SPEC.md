# Benchmark Specification

Status: **DRAFT — PRE-FREEZE**

## 1. Primary question

> Given an otherwise equivalent capable agent, does applying the tested operating protocol improve successful autonomous completion of consequential work enough to justify its overhead?

For MAPS_L, the primary tested protocol is the active repository operating contract and only the subordinate methods actually routed by the task. The benchmark must not reward MAPS_L merely for using MAPS_L vocabulary or artifacts.

## 2. Hypotheses

### H1 — Effectiveness

Protocol-enabled agents have a higher probability of objectively successful task completion than matched vanilla agents.

### H2 — Reliability

Protocol-enabled agents have lower rates of serious correctness, authority, recovery, duplication, review, and false-completion failures.

### H3 — Autonomous operation

Protocol-enabled agents require fewer human interventions and successfully continue eligible work more often.

### H4 — Efficiency tradeoff

Any benefit can be measured against token, monetary, latency, tool-call, documentation-read, retry, and rework overhead.

### H5 — Generalization

Any observed advantage persists on neutral external projects and sealed cases that were not used to develop the protocol.

These are empirical claims. A valid result may reject any or all of them.

## 3. What is not being tested

The primary benchmark does not ask:

- whether an agent can recite MAPS_L rules;
- whether a run produces MAPS-shaped documents;
- whether a reviewer prefers the style of MAPS output;
- whether more planning, more agents, more messages, or more files imply better work;
- whether the full MAPS_L runtime is superior when the intended experiment is only about protocol instructions.

Protocol adherence may be recorded to explain results, but it is not part of the primary success score.

## 4. Comparison arms

### A — VANILLA

Receives:

- exact task fixture;
- normal model/system safety and platform instructions;
- same tool capabilities as treatment;
- same environment, repository snapshot, permissions, limits, and human-response policy.

Does **not** receive MAPS_L project operating instructions or MAPS-specific task methods unless the case itself naturally contains MAPS_L as subject matter.

### B — PROTOCOL

Receives the identical experimental environment plus the tested MAPS_L protocol/configuration.

### Optional C — GENERIC STRUCTURED CONTROL

Added after the A/B design is stable. Receives the same environment plus a short, competent generic workflow such as:

```text
understand the objective
inspect relevant evidence
identify constraints
plan proportionally
execute
verify
review important risks
report result and unresolved issues
```

Purpose: distinguish "structured instructions help" from "MAPS_L-specific mechanisms help."

## 5. Two distinct experiments

Do not collapse these into one result.

### Experiment P — Protocol effect

```text
same harness/runtime capabilities
A: no MAPS_L protocol
B: MAPS_L protocol
```

Answers: **Do the instructions/operating methods themselves help?**

### Experiment S — Full-system effect

```text
A: capable vanilla agent environment
B: complete MAPS_L runtime/harness/protocol system
```

Answers: **Does the complete product help in realistic use?**

Run Experiment P first. Experiment S adds runtime, persistence, orchestration, and tooling differences and therefore has weaker mechanism attribution.

## 6. Controlled variables

For a matched A/B pair, freeze and record:

| Variable | Rule |
| --- | --- |
| model/provider | exact same model/version/provider |
| reasoning/effort | same setting |
| temperature/sampling | same configured policy; seed where supported |
| context window | same effective limit |
| tools | same available capabilities |
| helper/subagent capability | same availability and limits |
| repository/project | same clean starting revision |
| filesystem | equivalent clean copy |
| network | same availability |
| credentials/permissions | same experimental authority |
| task wording | byte-identical fixture where feasible |
| hidden acceptance contract | identical |
| run budget | identical time/cost/step/attempt limits |
| human response policy | identical |
| failure injections | identical deterministic schedule or counterbalanced schedule |
| evaluator | same frozen evaluator stack |

A protocol may cause the treatment agent to *choose* different tools, helpers, files, or reviews. That is part of the treatment effect. The capability to make those choices must be equivalent across arms.

## 7. Unit of comparison

The primary unit is a **paired case execution**:

```text
same case + same frozen starting state
→ one A run
→ one B run
```

Repeated executions form a case block. Analysis should preserve pairing rather than treating all runs as unrelated observations.

## 8. Corpus architecture

Recommended starting composition:

| Pool | Share | Purpose |
| --- | ---: | --- |
| neutral ordinary tasks | ~50% | real usefulness and ceremony cost |
| known regression/historical failures | ~25% | targeted reliability |
| sealed novel/challenge tasks | ~25% | generalization / anti-overfit |

At least one third of neutral/holdout work should come from projects not designed around MAPS_L terminology or repository conventions.

The percentages are targets, not immutable scientific constants. Freeze the actual mix before execution and disclose it.

## 9. Internal vs external validity

### Internal validity

The A/B difference should be attributable primarily to protocol exposure. Protect it with matched environments, immutable fixtures, randomized order, fixed graders, and sealed analysis rules.

### External validity

Results should transfer beyond MAPS_L's own repository. Include several project/task domains and report results by domain rather than only as an aggregate.

Suggested domains:

- software bug fix;
- multi-file implementation/refactor;
- automation/data transformation;
- research/evidence synthesis;
- documentation/configuration maintenance;
- multi-step project orchestration;
- interrupted/recovery work;
- review/verification task.

## 10. Benchmark contamination and overfitting

Known MAPS_L incidents are legitimate **regression evidence**, but not a sufficient effectiveness corpus. A protocol designed in response to those incidents can overfit them.

Use three pools:

- **DEV/REGRESSION** — visible and reusable during development;
- **FROZEN STANDARD** — versioned comparison set;
- **SEALED HOLDOUT** — unavailable to protocol developers until a designated evaluation.

After a holdout is exposed and directly informs a protocol change, retire it from holdout status and preserve it as regression evidence.

## 11. Hidden objective contract

Every case must be created with its success and failure conditions before either arm runs.

The hidden contract may contain:

- exact behavioral tests;
- expected output properties;
- forbidden mutations/actions;
- required evidence;
- seeded defects;
- correct blocker conditions;
- acceptable alternative implementations;
- severity mapping;
- allowed uncertainty states.

Do not expose hidden answer-key material to the executing agents.

## 12. Evidence hierarchy

Prefer grading in this order:

1. deterministic mechanical checks;
2. direct artifact/state inspection;
3. bounded semantic evaluator against a frozen rubric;
4. second independent evaluator for ambiguous cases;
5. human adjudication for evaluator disagreement or critical-severity findings.

Private chain-of-thought is never required. Observable actions and outputs are sufficient.

## 13. Anti-MAPS bias check

Before freeze, an independent reviewer should ask of every metric and case:

- Could Vanilla succeed without producing MAPS-shaped artifacts?
- Is a MAPS behavior being scored because it is intrinsically useful, or only because MAPS says to do it?
- Does the case include a plausible path where less process is better?
- Would the same success contract make sense if the tested protocol had another name?
- Are known MAPS strengths overrepresented?
- Are protocol weaknesses such as ceremony, navigation cost, over-review, false blocking, and latency directly testable?

Any criterion that cannot survive this review should be rewritten or removed before freeze.

## 14. Benchmark sizes

Recommended operating tiers:

| Tier | Cases | Repetitions/arm/case | Total A/B executions |
| --- | ---: | ---: | ---: |
| smoke | 12 | 2 | 48 |
| standard | 36 | 3 | 216 |
| full/release | 60+ | 5 | 600+ |

These counts are pragmatic starting points, not claims of universal statistical power. Before a high-stakes public claim, conduct a power/precision analysis using the observed variance and target effect size.

## 15. Version identity

Every executable benchmark release should freeze:

```text
benchmark_version
corpus_hash
case hashes
protocol/configuration immutable ref
model/provider/version/settings
runner version
rubric/evaluator version
analysis version
run-budget policy
human-response policy
```

Never silently edit a frozen release. Corrections become a new benchmark version with explicit compatibility notes.

## 16. Promotion firewall

Benchmark evidence may support a change; it may not automatically authorize one.

```text
frozen benchmark
→ executed results
→ comparative analysis
→ failure/mechanism analysis
→ proposed protocol/runtime change
→ required review/authority path
→ implementation
→ regression verification
```

Do not modify the benchmark because a result is inconvenient. Do not modify the protocol mid-run.

## 17. First validation gate

Before execution, independently verify:

- case mix and project diversity;
- treatment/control capability parity;
- hidden-answer leakage absence;
- evaluator blinding and order counterbalancing;
- severity definitions;
- metric definitions;
- equivalence/tradeoff thresholds;
- run limits;
- holdout sealing;
- immutable source/configuration refs;
- report schema;
- status accurately says **not yet executed**.
