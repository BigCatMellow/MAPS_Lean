# Run Protocol

Status: **DRAFT — CORRECTIONS APPLIED; NOT EXECUTED**

This file owns execution, isolation, randomization, human-response delivery, observable run records, evaluator/blinding procedure, stopping, invalidation, and batch completion. Arms/threshold values are owned by `BENCHMARK-SPEC.md`; case semantics by `CASE-DESIGN.md`; analysis by `SCORING-AND-ANALYSIS.md`.

## 1. Preconditions

No scored run may start until:

- corpus/case hashes are frozen;
- Treatment Surface Manifest is frozen;
- Threshold Manifest has no `UNSET` execution-blocking fields;
- model/provider/settings are frozen;
- A/B(/C) capabilities are parity-checked;
- human-response policy is frozen;
- evaluator/normalizer/adjudication stack is frozen;
- randomization plan is frozen;
- holdout seal/look-count is verified;
- independent pre-run review approves the package.

This includes Smoke. Smoke is not permission to choose thresholds after seeing A/B deltas.

## 2. Environment parity

Each matched run starts from the same task-facing state after the common scrub policy:

```text
same task fixture
same target snapshot
same target-project instruction set
same writable boundaries
same credentials/permissions
same network policy
same tools
same helper capacity
same model/settings/context limit
same run budget
same human-response policy
same neutral final-status contract
```

Only the frozen arm treatment differs.

Protocol/process sidecar storage is outside the target workspace and available equally to all arms. Target writes are graded against the same writable-path contract.

## 3. Isolation

Use a fresh disposable worktree/container/project copy per execution. No arm sees paired-arm artifacts, logs, messages, or mutations.

Reset mock/service state between runs. Real effects require an explicitly authorized sandbox/production-outcome study.

Task snapshots must not expose benchmark directories or sealed holdout material. Experiment P must not use network access to fetch mutable MAPS_L protocol/benchmark content.

## 4. Temporal pairing, randomization, and counterbalancing

Paired runs should execute concurrently when the provider supports it, or be interleaved within the frozen `pair_time_window`.

Within each case block:

- randomize arm execution order;
- balance first-position frequency;
- randomize evaluator presentation independently;
- preserve randomization seeds;
- keep deterministic failure injections identical or explicitly counterbalanced.

This reduces provider drift/load confounding, especially for latency.

## 5. Repetitions and tiers

Tier definitions are owned by `BENCHMARK-SPEC.md`.

Rules:

- every repetition is a fresh run;
- no trajectory carries into another repetition unless the case is explicitly a sequential episode-chain fixture;
- Smoke yields no directional benchmark verdict;
- C is mandatory for Standard/Full before MAPS-specific contribution claims;
- final claim-grade case count follows the predeclared precision target.

## 6. Human interaction policy

Use the frozen neutral policy from `BENCHMARK-SPEC.md`.

Default:

- non-boundary question/check-in → exact fixed reply: `Proceed within the stated scope using your best judgment.`
- seeded human-only boundary/preference → exact predefined case reply;
- asking never terminates a run by itself;
- every question/response is logged;
- avoidable questions count as burden, not automatic failure;
- cases where asking is objectively correct are included.

Record:

- question class;
- response text/class;
- whether response was predefined;
- intervention count;
- **observed** human elapsed minutes where measurable.

Do not estimate human minutes and do not infer intervention from ordinary message volume.

## 7. Observable run record

No private chain-of-thought is required.

Minimum record:

```text
batch_id
benchmark_version
case_id/case_hash
anonymous_arm_id
treatment_manifest_ref
threshold_manifest_ref
configuration_ref
model/provider/version/settings
starting_state_ref
seed/repetition
start/end timestamps
pair_block_id
execution_order

target files/documents opened
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

FINAL_STATUS
final artifact/diff/state refs
environment/harness termination reason
```

Files-read count may be recorded but is secondary because bulk reads can game it. Token/context consumption is the preferred reading-cost measure.

## 8. Common progress-update rule

Experiment P imposes **no** MAPS-specific live-update requirement.

If a platform requires progress updates, use the same frozen surface for every arm and exclude style/format from task success. Do not import SIMULATION_DESIGN's 2–4 update requirement into Experiment P scoring.

## 9. Grading pipeline

### Stage 1 — Objective/mechanical

Freeze deterministic results first:

- tests;
- state/diff assertions;
- forbidden effects;
- artifact properties;
- duplicate-effect checks;
- objective terminal class where machine-verifiable.

### Stage 2 — Evidence normalization

For unresolved semantic properties, construct a **minimal evidence packet** independent of protocol style:

- relevant target diff/artifact excerpt;
- objective state/check results;
- neutral `FINAL_STATUS` line;
- task-facing source evidence required by the rubric.

Strip or omit protocol-specific process artifacts, MAPS vocabulary, task-record formats, friction logs, `DONE/Changed/Verified` prose, helper orchestration chatter, and irrelevant verbosity unless the property directly concerns their target-side effect.

Preserve enough evidence to grade correctness; normalization must not remove a relevant failure.

### Stage 3 — Blinded semantic evaluation

Evaluator receives:

- anonymous case/arm labels;
- task-facing fixture;
- frozen property rubric;
- normalized evidence packet only.

Absolute property scoring precedes pairwise preference. Pairwise preference is supplementary.

### Stage 4 — Independent second evaluation

Use a different model family/provider where feasible for:

- ambiguous semantic properties;
- headline-affecting disagreements;
- S4 candidates;
- sampled QA.

### Stage 5 — Human adjudication

Adjudicators must be non-contributors to MAPS_L for the tested release or remain effectively blinded to arm identity.

Adjudicate:

- every S4 candidate;
- every headline-affecting unresolved dispute;
- suspected treatment leakage/benchmark defect;
- a predeclared random sample of unflagged runs/pairs.

Adjudicate in paired form where comparison context matters. Report adjudication reversals by arm so one arm does not receive more “exoneration opportunities.”

## 10. Blinding check

Before relying on semantic grades for headline results, test whether the normalized evidence still reveals treatment.

Procedure:

1. sample the predeclared blinding-check set;
2. ask a separate blinded evaluator to guess arm identity from the exact semantic evidence packet;
3. test guesses against 50% chance using the frozen rule in `BENCHMARK-SPEC.md`;
4. report accuracy and interval/test result.

If the predeclared blinding rule fails, semantic grades from that evidence representation are not headline-valid. Re-normalize or use a new evaluator under a new frozen batch/version before continuing.

## 11. Stopping rules

A run stops only on frozen conditions:

- requested objective outcome complete;
- correct genuine blocker reached;
- hard budget exhausted;
- safety/authority boundary requires termination;
- true external harness failure invalidates the pair;
- benchmark harness defect invalidates the pair.

Do not give one arm extra time/retries for appearing close.

Over-continuation after objective success is itself observable failure/overhead when the case defines a stop boundary.

## 12. INVALID, agent-caused failure, and UNKNOWN

`INVALID` is reserved for experimental-integrity failure external to agent behavior, such as:

- wrong model/config;
- mismatched start state;
- answer-key leakage;
- one-arm capability outage caused by harness setup;
- contaminated workspace;
- benchmark runner defect.

These are **not INVALID** merely because they involve the environment:

- helper fan-out exhausts allowed resources;
- runaway loop hits limit;
- protocol/context reading exhausts context;
- agent causes tool/resource saturation;
- agent chooses a bad retry strategy.

Those are agent/system outcomes and remain not-success/failure/incomplete as the case dictates.

Invalidity decisions should be made arm-blind. A single invalid execution invalidates its matched pair/block for that repetition; rerun the full pair/block under the frozen rerun policy. Report invalid rates/reasons by arm before replacement.

`UNKNOWN` is not success in the primary analysis. Preserve it and report best/worst-case sensitivity bounds.

No arm receives an extra unpaired attempt.

## 13. Benchmark-defect handling after outcomes exist

Potential benchmark defects are reviewed without arm outcome labels where possible.

If a case must be corrected/dropped after scored data exist:

- preserve the original case/result;
- create a new case/benchmark version;
- disclose the reason;
- report original-version and corrected-version aggregate results;
- do not erase a result because it is inconvenient for one arm.

Smoke can discover harness/grader defects, but observed A/B direction may not set thresholds, guardrails, or case-selection rules.

## 14. Run provenance

Record immutable refs where possible:

```text
benchmark/corpus hash
case hash
treatment manifest hash
threshold manifest hash
holdout bundle hash
target start ref
runner ref
normalizer/evaluator refs
analysis ref
```

If a provider model lacks immutable identity, record strongest available version/date/settings and disclose the limitation.

## 15. Batch completion

Preserve:

```text
frozen package identity
all original and replacement run IDs
invalid-pair decisions/reasons
objective grades
normalized evidence packet hashes
semantic grades
blinding-check result
second-evaluator grades
adjudications and reversal rates by arm
aggregate/paired metrics
PROCEED/BLOCK strata
external-project stratum
holdout consistency stratum
known-regression diagnostics (separate)
failure divergence records
protocol-adherence diagnostics (post-outcome only)
cost/context/latency/human burden
limitations
```

The final report must retain enough evidence to investigate surprising aggregates without exposing future sealed holdouts.

## 16. Smoke-to-standard sequence

1. validate harness on non-scored dummy cases;
2. verify task-snapshot scrub and treatment injection;
3. verify arm isolation and sidecar writes;
4. calibrate graders on exposed non-holdout material;
5. freeze all Smoke thresholds/policies;
6. independent pre-run review;
7. run Smoke;
8. inspect only harness/grader validity; **do not issue BETTER/WORSE/EQUIVALENT**;
9. any correction becomes a new version;
10. freeze Standard A/B/C package and independently review it;
11. run Standard.

No sealed holdout may be tuned on and then reused as confirmation.
