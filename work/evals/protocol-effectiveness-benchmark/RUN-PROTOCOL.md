# Run Protocol

Status: **SECOND CORRECTION PASS APPLIED — NOT EXECUTED**

This file owns execution, isolation, randomization, human-response delivery, observable run records, evaluator/blinding procedure, stopping, invalidation, and batch completion. Arms/threshold values/pool lifecycle are owned by `BENCHMARK-SPEC.md`; case semantics by `CASE-DESIGN.md`; analysis/verdict logic by `SCORING-AND-ANALYSIS.md`.

## 1. Preconditions

No scored run may start until:

- corpus/case hashes are frozen;
- Treatment Surface Manifest was frozen before corpus construction;
- Threshold Manifest has no `UNSET` execution-blocking fields;
- Arm-C text/hash is frozen for the benchmark line when applicable;
- model/provider/settings are frozen;
- A/B(/C) capabilities and injection-channel parity are checked;
- human-response matcher/policy is frozen;
- evaluator/normalizer/adjudication stack is frozen;
- blinding sample/ceiling and normalization-audit sample are frozen;
- randomization plan is frozen;
- holdout/standard exposure state and confirmatory look count are verified;
- required pre-registration hashes are committed;
- case-secret snapshot canary passes;
- independent pre-run review approves the package.

This includes Smoke.

## 2. Environment parity

Each matched run starts from the same task-facing state after the common scrub policy:

```text
same task fixture/common bootstrap
same history-free or approved-sanitized target snapshot
same target-project instruction set
same TARGET_WRITABLE_PATHS
same PROCESS_SIDECAR_PATH
same credentials/permissions
same network policy
same tools/helper capacity
same model/settings/context limit
same run budget
same human-response policy/matcher
same neutral final-status contract
same hidden checks
```

Only the frozen arm treatment differs. B and C treatments use the same injection channel and position. The common bootstrap is delivered to A/B/C through the same common position.

Protocol/process sidecar storage is outside the target repository and equally available. Target writes are graded against the same visible writable-path contract.

## 3. Snapshot isolation and secret-leak canary

Use a fresh disposable container/project export per execution. No arm sees paired-arm artifacts, logs, messages, or mutations.

### 3.1 History-free/sanitized snapshots

For MAPS_HOME, use a history-free export by default. If VCS history is required for a task, the approved snapshot builder must remove benchmark-related material from reachable history/objects/reflogs/alternates as defined by the frozen scrub manifest.

The scrub covers benchmark-related material across the repository, including relevant evaluation, review, task, handoff, freeze, and friction records—not only `work/evals/`.

Target protocol files removed to prevent A contamination are removed symmetrically. A case whose requested subject requires one of those treatment files is ineligible for Experiment P.

### 3.2 Hidden material never enters run repositories

Hidden contracts, oracle answers, seeded-condition keys, and case-secret answer material for **all pools** remain outside every repository/workspace used to seed runs. Only non-secret IDs/hashes may be present.

### 3.3 Frozen canary check

Before any scored execution of a case:

1. place/reference a unique high-entropy canary token in that case's external hidden contract;
2. scan the complete agent-visible snapshot and any reachable VCS metadata/history for the token;
3. verify the token cannot be recovered through ordinary repository search, `git log`, `git show`, object traversal, reflogs/alternates, or equivalent accessible interfaces;
4. preserve the canary-check result/hash in batch evidence.

Any hit is an experimental-integrity defect. Do not run the affected case until the snapshot/package is corrected and re-reviewed as required.

Reset external mock/service state between runs. Real effects require explicit authorization and a controlled environment.

## 4. Temporal pairing, randomization, and counterbalancing

Paired runs execute concurrently when supported or are interleaved within the frozen `pair_time_window`.

Within each case block:

- randomize arm execution order;
- balance first-position frequency;
- randomize evaluator presentation independently;
- preserve randomization seeds;
- keep deterministic failure injections identical or explicitly counterbalanced.

## 5. Repetitions and tiers

Tier definitions, Arm-C requirements, and sample-size policy are owned by `BENCHMARK-SPEC.md`.

Execution rules only:

- every repetition is fresh;
- no trajectory carries between repetitions unless the case is explicitly a sequential episode-chain fixture;
- all repetitions preserve the same frozen benchmark-line manifests;
- Smoke yields descriptive/procedural evidence only, not a directional benchmark verdict.

## 6. Human-response delivery

The response content/policy/version is owned and frozen by `BENCHMARK-SPEC.md`. This section defines delivery.

### 6.1 Responder

Use one of these frozen modes:

1. **deterministic matcher** — preferred when seeded question classes can be recognized mechanically; or
2. **arm-blind responder** — receives normalized question text with treatment-identifying process vocabulary removed and applies the frozen response policy.

The same responder mode/configuration applies to all arms in a batch.

### 6.2 Misroutes

Log for every question:

```text
question_id
normalized_question_hash
matched_class
response_id/text
responder_mode
misroute_suspected = true|false
```

Suspected response misroutes are adjudicated arm-blind where possible and reported by arm. A responder mistake is not silently charged to the agent arm.

### 6.3 Human burden

Record attributable question/response events and **observed** human elapsed minutes where measurable. Do not estimate human minutes and do not infer intervention from ordinary message count.

Whether a question was avoidable/correct is a case/outcome property, not a style preference. `CASE-DESIGN.md` owns asking-is-correct semantics.

## 7. Observable run record

No private chain-of-thought is required.

Minimum record:

```text
batch_id
benchmark_line/version
case_id/case_hash
anonymous_arm_id
treatment_manifest_ref
threshold_manifest_ref
configuration_ref
model/provider/version/settings
starting_state_ref/snapshot_hash
seed/repetition
pair_block_id
start/end timestamps
execution_order

context/token consumption
searches
tool calls/results/errors
helper dispatches/results
tests/checks
writes/mutations/external effects
retries/recovery
state/status transitions
human questions/responses/interventions

input_tokens
output_tokens
cost_usd
latency_ms
tool_call_count
helper_call_count
search_count
retry_rework_count
observed_human_minutes
bulk_read/context_bytes_or_tokens where available
process_sidecar_artifact_count

FINAL_STATUS
final artifact/diff/state refs
environment/harness termination reason
```

Raw files-read count may be recorded only as a secondary diagnostic; token/context consumption is the preferred reading-cost measure.

## 8. Common progress-update rule

Experiment P imposes no MAPS-specific live-update requirement. If a platform requires progress updates, use the same frozen surface for all arms and exclude its style/format from task success. Do not import SIMULATION_DESIGN's update/observability requirements into Experiment P primary scoring.

## 9. Grading pipeline

### Stage 1 — objective/mechanical

Freeze deterministic results first: tests, state/diff assertions, forbidden effects, artifact properties, duplicate-effect checks, and objective terminal class where machine-verifiable.

### Stage 2 — evidence normalization

For unresolved semantic properties, construct a minimal evidence packet independent of protocol style:

- relevant target diff/artifact excerpt;
- objective state/check results;
- neutral `FINAL_STATUS` line;
- task-facing source evidence required by the rubric.

Strip or omit treatment-identifying process artifacts, MAPS vocabulary, task-record formats, `DONE/Changed/Verified` prose, helper chatter, and irrelevant verbosity unless the property directly concerns a target-side effect.

Normalization may not remove evidence relevant to correctness/failure.

### Stage 3 — blinded semantic evaluation

Evaluator receives anonymous case/arm labels, task-facing fixture, frozen property rubric, and normalized packet only. Absolute property scoring precedes any supplementary pairwise preference.

### Stage 4 — independent second evaluation

Use a different model family/provider where feasible for ambiguous semantic properties, headline-affecting disagreements, S4 candidates, and sampled QA.

### Stage 5 — adjudication

Adjudicators are non-contributors to the tested protocol release or effectively blinded to arm identity. Adjudicate every S4 candidate, headline-affecting unresolved dispute, suspected treatment leakage/benchmark defect, and the frozen random unflagged sample. Report reversals by arm.

## 10. Blinding and normalization-validity checks

The exact sample sizes/confidence/accuracy ceiling are frozen in the Threshold Manifest before Smoke.

### 10.1 Treatment-guess test

1. Draw the frozen blinding-check sample from normalized semantic packets.
2. Use a blinded guesser demonstrably at least as capable as the primary semantic evaluator for this discrimination task.
3. Record treatment-guess accuracy and a confidence interval at the frozen confidence level.
4. **Pass only if the upper confidence bound on guess accuracy is at or below the frozen `blinding_guess_accuracy_ceiling`.** Failure to reject 50% chance is not sufficient evidence of blinding.

If this rule fails, semantic grades from that representation are not headline-valid; re-normalize and create a newly frozen batch/line as required.

### 10.2 Normalization-loss audit

For the frozen `normalization_audit_sample_size_per_arm`, an arm-blind auditor compares raw admissible evidence with normalized packets and records whether any task-relevant evidence was incorrectly dropped or distorted.

Report loss/error rate separately by arm. A materially asymmetric normalization-loss pattern blocks reliance on semantic grades until corrected under a new frozen package.

## 11. Stopping rules

A run stops only on frozen conditions: requested objective outcome complete, correct genuine blocker, hard budget exhaustion, required safety/authority stop, true external harness failure invalidating the pair, or benchmark harness defect invalidating the pair.

Do not give one arm extra time/retries for appearing close. Over-continuation after an explicit task stop boundary is an observable outcome/overhead event.

## 12. INVALID, agent-caused failure, and UNKNOWN

`INVALID` is reserved for experimental-integrity failure external to agent behavior, such as wrong model/config, mismatched start state, answer-key leakage, one-arm harness capability outage, contaminated workspace, or runner defect.

Agent-caused helper fan-out, runaway loops, context exhaustion, resource saturation, and bad retry strategy are not INVALID merely because they interact with the environment.

Invalidity decisions are arm-blind where possible. A single invalid execution invalidates its matched pair/block for that repetition; rerun the full pair/block under the frozen policy. Report original invalid rates/reasons by arm before replacement. No arm receives an extra unpaired attempt.

`UNKNOWN` is not success. Preserve it for the sensitivity analysis defined in `SCORING-AND-ANALYSIS.md`.

## 13. Benchmark-defect handling after outcomes exist

Potential defects are reviewed without arm labels where possible.

If a case must be corrected/dropped after scored data exist:

- preserve the original case/result;
- create a new version/line as required;
- disclose reason;
- report original and corrected-version aggregates;
- never erase an inconvenient arm result.

## 14. Run provenance

Record immutable refs/hashes for benchmark line/corpus, case, treatment manifest, threshold manifest, generic control, holdout, target snapshot, runner, normalizer/evaluators, analysis rules, and committed pre-registration record.

If a provider model lacks immutable identity, record strongest available version/date/settings and disclose that limitation.

## 15. Batch completion

Preserve:

```text
frozen package identity
all original/replacement run IDs
invalid-pair decisions/reasons by arm
objective grades
normalized packet hashes
normalization-loss audit
blinding treatment-guess result
semantic/second-evaluator grades
adjudications/reversal rates by arm
aggregate paired metrics
PROCEED/BLOCK strata
external/MAPS_HOME strata
NONE/STRESS/COUNTERWEIGHT strata
unexposed holdout/standard consistency strata
known-regression diagnostics separately
failure divergence records
protocol-adherence diagnostics post-outcome only
cost/context/latency/human burden
limitations
```

## 16. Smoke-to-Standard within one benchmark line

1. validate harness on non-scored dummy cases;
2. verify history-free/sanitized snapshots, recursive scrub, secret canaries, treatment injection, sidecar, and arm isolation;
3. calibrate graders on exposed non-holdout material;
4. freeze **one** Treatment Surface Manifest, Threshold Manifest, Arm-C text/hash, evaluator/normalizer rules, verdict rules, and run policy for the benchmark line **before Smoke**;
5. independent pre-run review;
6. run Smoke;
7. expose to anyone who can edit/freeze the later Standard package only **arm-pooled operational evidence** needed to assess harness/grader validity; withhold per-arm effectiveness/overhead deltas until the Standard package is frozen;
8. if no rule/package change is required, carry the exact same frozen manifests/rules into Standard and run it;
9. if any margin, guardrail, safety/tradeoff/verdict rule, headline endpoint, budget, human-response policy, Arm-C text, evaluator criterion, or treatment bundle must change, start a **new benchmark line**, re-freeze before a new Smoke, and do not use prior per-arm Smoke direction to set the replacement values.

Smoke never issues `BETTER`, `WORSE`, or `EQUIVALENT`. No exposed holdout/standard case may be reused as pristine confirmation for a later protocol version contrary to `BENCHMARK-SPEC.md`.
