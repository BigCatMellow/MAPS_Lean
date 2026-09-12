# Run Protocol

Status: **FOURTH CORRECTION PASS APPLIED — NOT EXECUTED**

This file owns execution, isolation, parity, randomization, human-response delivery, observable run records, leakage checks, normalization/blinding, invalidation/reruns, and batch completion. Arms/pools/threshold values and Smoke information policy live in `BENCHMARK-SPEC.md`; case truth semantics in `CASE-DESIGN.md`; verdict logic in `SCORING-AND-ANALYSIS.md`.

## 1. Preconditions

No scored run, including Smoke, may start until all items below are frozen and independently approved:

- benchmark line/version;
- corpus/case hashes;
- Treatment Surface Manifest;
- Threshold Manifest with **every listed field set; any `UNSET` blocks execution**;
- target-work sampling manifest;
- model/provider/settings;
- A/B(/C) capability-parity evidence;
- human-response matcher/policy;
- evaluator/normalizer/adjudication stack;
- randomization plan;
- per-case network/retrieval allowlists;
- hidden-material canary/resolution-identifier records;
- holdout seal/look count;
- pre-run review.

## 2. Environment parity

Each matched execution receives:

```text
same visible task fixture
same target snapshot
same target-project instructions
same neutral bootstrap
same TARGET_WRITABLE_PATHS
same PROCESS_SIDECAR_PATH capability
same credentials/permissions
same per-case network/retrieval allowlist
same tools/helper capacity
same model/settings/context limit
same run budget
same human-response policy
same neutral FINAL_STATUS contract
same harness/global non-treatment instruction state
```

Only the frozen arm treatment differs.

B and C treatment text is injected at the same channel/position. A receives no replacement MAPS-like text beyond the common neutral bootstrap.

## 3. Isolation and state reset

Use a fresh disposable target workspace/image per execution.

Before every execution, except inside an explicitly declared sequential episode-chain case:

- clear process sidecar contents;
- clear harness/session memory and **all non-chain caches**;
- disable or reset persistent agent state;
- ensure no paired/prior run artifact is visible;
- reset mock/service state;
- verify harness/user/global instruction files, installed skills/profiles, memory, MCP/config injection sources, process environment variables, shell rc/profile files, global VCS configuration/hooks, runner-injected metadata, and mounted reusable state are empty or byte-identical across arms except the declared treatment;
- verify agent-visible environment variables and runner metadata contain no arm identity, case labels, hidden case metadata, answer-bearing provenance, or resolution identifiers.

No arm sees logs, artifacts, messages, hidden contracts, or mutations from another run.

## 4. Snapshot and hidden-material leakage gate

### 4.1 Snapshot construction

Use history-free exports by default. Any retained VCS history must satisfy the sanitization rule in `BENCHMARK-SPEC.md`.

The assembled execution environment includes, for leakage purposes:

```text
target workspace + VCS metadata/history if any
container/image filesystem visible to the agent
treatment/common-bootstrap bundles
PROCESS_SIDECAR_PATH
harness home/config
user/global instruction directories
installed skill/profile material
MCP/resource configuration visible to the agent
persistent/session memory and all non-chain caches
process environment variables
shell startup files and global VCS config/hooks
runner-injected metadata and mounted reusable state
enabled model/provider-hosted retrieval/tool configuration
```

### 4.2 Canary lifecycle

Canaries are created when hidden material is first created, per `CASE-DESIGN.md`/`BENCHMARK-SPEC.md`. The runner does not invent a last-minute token and call that sufficient.

Before each scored run, scan the **fully assembled environment** for:

- every canary associated with the case;
- frozen case-distinctive resolution identifiers;
- known hidden-contract/oracle path names where that check does not reveal them to the executing agent.

The scan includes ordinary file search, process environment/runner metadata, shell/global VCS state, mounted reusable state, and all accessible VCS/object-history mechanisms. A canary or forbidden resolution hit blocks the run before execution and invalidates the snapshot package until repaired and independently rechecked.

### 4.3 External/network/retrieval leakage gate

Network/retrieval defaults to deny-all across every model-reachable channel. For an externally enabled case, enforce exactly the frozen per-case allowlist from `BENCHMARK-SPEC.md` §4.5.

Before execution, verify that the allowlist cannot reach the target project's upstream/forks, resolved issue/PR threads, post-snapshot releases/package versions, search/index/cache reproductions, or other frozen resolution sources identified by the case. If required task access cannot be separated from answer-bearing sources, the case is ineligible.

The mechanical preflight must **exercise every enabled external-access tool/channel**, including provider-hosted or server-side web search/fetch/retrieval/code-execution routes and remote MCP/resource tools. A container/sandbox egress test alone is not sufficient. Any route that can reach a forbidden resolution source fails the case package before execution.

## 5. Temporal pairing, randomization, and repetitions

Paired runs execute concurrently when technically appropriate or are interleaved inside the frozen `pair_time_window`.

Within each case block:

- randomize arm execution order;
- balance first-position frequency;
- randomize evaluator presentation independently;
- preserve randomization seeds;
- keep deterministic failure injections identical or explicitly counterbalanced.

Repetitions are fresh executions and nested within case. No trajectory carries between repetitions unless the case explicitly defines a sequential episode chain.

## 6. Human-response delivery

`BENCHMARK-SPEC.md` owns the mandatory neutral policy. This section owns delivery and routing only.

### 6.1 Frozen responder

Use either:

- a deterministic frozen matcher; or
- an operator/responding evaluator that is genuinely blind to arm identity and frozen to the same response table.

Mandatory behavior inherited from SPEC:

- non-boundary clarification/check-in → `Proceed within the stated scope using your best judgment.`
- seeded human-only authority/preference question → predefined case answer;
- asking never itself terminates or stalls a run;
- avoidable questions are burden events, not automatic task failure.

Equivalent question classes receive equivalent replies across arms.

### 6.2 Misroutes

Log question text/class, matcher decision, delivered response, arm-blind responder identity where relevant, and whether the response matched the frozen table.

If adjudication determines a responder/matcher misroute **materially affected the task outcome**, mark the matched A/B(/C) block for that repetition `INVALID` and rerun the **entire matched block** under `invalid_pair_rerun_policy`. No arm is rerun alone.

A non-outcome-affecting misroute is logged as experimental-friction evidence only and does not change task success.

## 7. Observable run record

Capture observable behavior without private chain-of-thought.

Minimum fields:

```text
batch_id / benchmark_line / benchmark_version
case_id / case_hash
anonymous_arm_id
treatment_manifest_ref
threshold_manifest_ref
configuration_ref
model/provider/version/settings
starting_state_ref
seed/repetition
pair_block_id
execution_order
start/end timestamps
network_allowlist_ref
snapshot_leakage_check_ref

files/documents opened
context/token consumption
searches
tool calls/results/errors
helper dispatches/results
tests/checks
writes/mutations/external effects
retries/recovery
state/status transitions
human questions/responses/interventions

input_tokens / output_tokens
cost_usd
latency_ms
tool_call_count / helper_call_count / search_count
retry_rework_count
observed_human_minutes
bulk_read/context bytes or tokens where available

FINAL_STATUS
final artifact/diff/state refs
environment/harness termination reason
```

Raw files-read count is secondary because bulk reads can game it. Prefer tokens/context consumption for reading cost.

## 8. Stopping rules

A run stops only on frozen conditions:

- requested objective outcome complete;
- correct genuine blocker reached;
- hard budget exhausted;
- safety/authority boundary requires termination;
- true external harness failure invalidates the matched block;
- benchmark runner defect invalidates the matched block.

Do not grant extra time/retries because one arm appears close. A question is not a stop condition; the responder returns under §6.

Over-continuation after task success remains observable failure/overhead when the visible task defines the stop boundary.

## 9. Grading pipeline

### Stage 1 — objective/mechanical

Freeze deterministic evidence first: tests, state/diff assertions, forbidden effects, artifact properties, duplicate-effect checks, and machine-verifiable terminal facts.

### Stage 2 — normalization

For unresolved semantic properties, construct a minimal evidence packet containing only what the property needs:

- relevant target diff/artifact excerpt;
- objective check/state results;
- neutral `FINAL_STATUS`/`REASON`;
- required task-facing source evidence.

Strip irrelevant protocol vocabulary/process artifacts, MAPS task records, friction logs, `DONE/Changed/Verified` prose, helper chatter, and verbosity **unless the target-side effect of that material is itself relevant**.

Normalization may not remove evidence needed to detect correctness, scope, safety, latency, human-burden, or other frozen outcomes.

### Stage 3 — blinding validation **before semantic grades are unmasked**

Run both tests below before any benchmark editor, normalizer author, or evaluator-config author can see per-arm semantic grades.

#### Treatment-identification test

`BENCHMARK-SPEC.md` freezes:

```text
blinding_check_sample_size
blinding_guess_task
blinding_guess_accuracy_ceiling
blinding_confidence_level
blinding_guesser_capability
```

Default permitted guess-task shape is a **balanced binary `B vs non-B` classification** using normalized packets, with non-B sampled evenly from available A/C packets. A different task must be frozen before execution and its chance baseline stated explicitly.

The blinding check passes only when the configured upper confidence bound on identification accuracy is **at or below** the frozen ceiling. Failure to reject chance is not evidence of blinding.

The guesser must be at least as capable as the semantic evaluator for treatment identification.

#### Normalization-loss audit

Audit the frozen `normalization_audit_sample_size_per_arm` independently in each arm. Compare raw task-relevant evidence with normalized packets for removed outcome-relevant information.

Use the frozen `normalization_loss_asymmetry_threshold`. If arm-to-arm loss exceeds it, normalized semantic evidence is not headline-valid.

Any re-normalization decision must be made **without access to per-arm semantic grades**, then applied to the full affected batch under one frozen representation. Do not selectively re-normalize losing/winning cases.

### Stage 4 — blinded semantic evaluation

Only after Stage 3 passes, evaluator receives anonymous case/arm labels, task-facing fixture, frozen rubric, and normalized packet. Absolute property scoring precedes pairwise preference.

### Stage 5 — independent second evaluation

Use a different model family/provider where feasible for ambiguous properties, headline disputes, S4 candidates, and sampled QA.

### Stage 6 — human adjudication

Adjudicators are non-contributors to the tested MAPS_L release or effectively blinded. Adjudicate every S4 candidate, headline-affecting dispute, suspected treatment leakage/benchmark defect, and a predeclared random unflagged sample. Report reversals by arm.

## 10. INVALID and UNKNOWN

`INVALID` is reserved for experimental-integrity failure external to agent behavior, such as wrong configuration, mismatched start state, answer leakage, harness-caused one-arm capability outage, contaminated workspace, responder misroute that materially affected outcome, or runner defect.

Agent-caused exhaustion is not INVALID, including helper fan-out, loops, context exhaustion from protocol reading, resource saturation, or poor retry strategy.

Invalidity decisions are arm-blind where possible. A single invalid execution invalidates its matched A/B(/C) block for that repetition; rerun the full block under the frozen policy. **No arm receives an unpaired extra attempt.** Report invalid counts/reasons by arm before replacement.

`UNKNOWN` is not success in primary analysis and remains visible for sensitivity bounds.

## 11. Benchmark-defect handling

Potential benchmark defects are reviewed without arm outcome labels where possible. Preserve original result/version; corrections produce a new version and disclose both original and corrected aggregates where scored data exist.

No case is erased because its outcome is inconvenient.

## 12. Smoke-to-Standard procedure

The authoritative Smoke information/change firewall is **`BENCHMARK-SPEC.md` §12**. This file does not restate its change list.

Execution sequence:

1. validate harness on unscored dummy material;
2. verify snapshot scrub/treatment injection/global-auto-load parity;
3. verify leakage canaries/resolution identifiers/network-retrieval allowlists and exercise every enabled external-access tool;
4. verify arm isolation/sidecar, environment, shell/global-VCS state, and harness-memory/cache reset;
5. calibrate graders on exposed non-holdout material;
6. freeze and independently review the benchmark line under SPEC §12;
7. run Smoke;
8. expose only **arm-masked** operational evidence to benchmark editors as permitted by SPEC §12; aggregate evidence must be unlinkable to arm and run-level evidence must be normalized/masked;
9. treat anyone given unmasked arm-identifiable run-level Smoke material as exposed to per-arm deltas for SPEC §12 eligibility;
10. repair only under the benchmark-line/version rules in SPEC §12;
11. freeze/verify Standard execution package without releasing prohibited per-arm Smoke deltas;
12. run Standard.

Smoke never produces `BETTER`, `WORSE`, or `EQUIVALENT`.

## 13. Batch completion

Preserve:

```text
frozen identities/hashes
all original/replacement run IDs
snapshot/network/retrieval leakage checks
invalid-block decisions/reasons
objective grades
normalized packet hashes
blinding-identification result
normalization-loss audit
semantic/second-evaluator grades
adjudications/reversals by arm
aggregate/paired metrics
PROCEED/BLOCK strata
external/home strata
external resolution-date/training-cutoff sensitivity strata
NONE/STRESS/COUNTERWEIGHT strata
holdout/unexposed status
known-regression diagnostics separately
S4 case-level exclusivity derivation
UNKNOWN sensitivity
failure-divergence records
post-outcome protocol diagnostics
cost/context/latency/human burden
limitations/deviations
```

The final report retains sufficient evidence to audit surprising aggregates without exposing future sealed holdouts.
