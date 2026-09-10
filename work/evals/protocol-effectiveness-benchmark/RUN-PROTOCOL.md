# Run Protocol

Status: **DRAFT — PRE-FREEZE**

This procedure exists to make treatment/control comparisons reproducible and difficult to bias after results are visible.

## 1. Freeze before execution

Before the first run in an evaluation batch, freeze:

- benchmark version and corpus hash;
- all included case hashes;
- hidden acceptance contracts;
- arm definitions;
- model/provider/version/settings;
- available tools and helper limits;
- clean starting-state references;
- run budgets and stop conditions;
- human-response policy;
- failure-injection schedule;
- evaluator prompts/schemas/models/settings;
- scoring rules;
- severity assignments;
- equivalence and unacceptable-tradeoff thresholds;
- randomization/counterbalancing plan;
- analysis version.

No protocol or scoring change may be introduced mid-batch. Abort/restart under a new batch identity if a material defect is discovered.

## 2. Environment parity

Each A/B run begins from equivalent state.

Required parity includes:

```text
same task fixture
same repository/project revision
same writable/non-writable boundaries
same credentials/permissions
same network policy
same tools
same helper/subagent capacity
same model and inference settings
same context/run budget
same human-response policy
```

The protocol arm may use capabilities differently. Capability availability itself should not differ in the protocol-only experiment.

## 3. Isolation

Use a fresh disposable worktree/container/project copy for each execution where practical. No arm may see artifacts, logs, messages, or modifications produced by its paired run.

Reset external mock/service state between runs. For real external effects, use a controlled sandbox or idempotent fixture unless a real-production outcome study is explicitly authorized.

## 4. Randomization and counterbalancing

Do not always run Vanilla first or always present one output first to evaluators.

For each repeated case block:

- randomize A/B execution order;
- balance first-position frequency across the corpus;
- randomize evaluator presentation order independently of execution order;
- preserve the randomization seed/plan in the batch record.

If deterministic failure timing depends on step order, either keep an identical injection trigger across arms or counterbalance the trigger schedule and report it.

## 5. Repetitions

Suggested tiers:

```text
SMOKE:    12 cases × 2 repetitions × 2 arms = 48 executions
STANDARD: 36 cases × 3 repetitions × 2 arms = 216 executions
FULL:     60+ cases × 5 repetitions × 2 arms = 600+ executions
```

Repetitions should be genuine fresh executions. Do not let one run's trajectory influence the next.

## 6. Human interaction policy

Freeze how the human/operator behaves before execution.

Examples:

- no human response unless a true experimental blocker requires it;
- fixed canned response to equivalent clarification classes;
- maximum N interventions;
- predefined authority answers for seeded boundary questions.

Every intervention must be attributable and logged. Free-form operator rescue creates a large confound and should be minimized.

Measure both:

- intervention count;
- estimated/observed human minutes.

Do not infer intervention merely from ordinary chat/message traffic.

## 7. Observable run record

Capture the trajectory without private chain-of-thought.

Minimum fields:

```text
batch_id
benchmark_version
case_id
case_hash
anonymous_arm_id
configuration_ref
model/provider/version/settings
starting_state_ref
seed/repetition
start/end timestamps

files/documents opened
searches performed
tool calls + results/errors
helper/subagent dispatches + returned status
tests/checks run
writes/mutations/external effects
retries/recovery actions
state/status transitions
human interventions

input tokens
output tokens
context/cache measurements where available
cost_usd
latency_ms
tool-call count
files-read count
files-changed count
retry/rework count

final declared status
final artifact/diff/state references
```

MAPS_L portable Run Records may supply much of this evidence where available. Missing joins remain `UNKNOWN` rather than reconstructed speculatively.

## 8. No hidden-reasoning requirement

Executing agents may be asked for concise observable decision statements when useful, such as:

```text
assumption/question → evidence checked → next action
```

Do not require private reasoning traces. Evaluation should be based on outputs, tool actions, artifacts, state, and explicit bounded explanations.

## 9. Primary grading order

### Stage 1 — Mechanical/objective checks

Run all deterministic graders first and freeze results.

Examples:

- tests;
- exact state checks;
- diff/path boundaries;
- forbidden side effects;
- expected artifact presence/content properties;
- duplicate-effect detection;
- correct terminal state where machine-verifiable.

### Stage 2 — Blinded semantic grading

Only unresolved semantic properties go to the evaluator. The evaluator receives anonymized treatment identity and only evidence necessary for the rubric.

The evaluator must not know which output is MAPS_L where feasible.

### Stage 3 — Independent second grade

Use a second fresh evaluator for:

- ambiguous semantic findings;
- grader disagreement;
- consequential failures;
- sampled quality assurance.

### Stage 4 — Human adjudication

Required for:

- S4 findings;
- unresolved evaluator disagreement affecting headline conclusions;
- suspected benchmark defect;
- suspected treatment leakage.

Freeze prior grader outputs before adjudication.

## 10. Pairwise evaluator bias controls

When comparing artifacts directly:

- anonymize arm labels;
- counterbalance left/right or first/second position;
- randomize pair order;
- prefer absolute rubric scoring before pairwise preference;
- test evaluator stability on a calibration subset;
- record disagreement rather than forcing consensus invisibly.

Pairwise preference is supplementary. Objective case success remains primary.

## 11. Stopping rules

A run stops when any frozen condition applies:

- objective success reached and required verification complete;
- correct true blocker reached;
- hard budget exhausted;
- unrecoverable environment failure invalidates the run;
- safety/authority boundary requires termination;
- benchmark harness defect makes treatment comparison invalid.

Do not give one arm extra time or retries because it appears close to success.

## 12. Invalid runs

Mark a run `INVALID` rather than PASS/FAIL when experimental integrity is broken, for example:

- wrong model/configuration;
- starting-state drift;
- hidden-answer leakage;
- unavailable capability in only one arm;
- benchmark harness failure unrelated to agent behavior;
- contaminated workspace from another run.

Report invalid-run counts and reasons. Replace them only according to a frozen rerun policy.

## 13. Run identity and provenance

Every run should be reconstructible from immutable references where technically possible:

```text
benchmark/corpus hash
case hash
protocol/config ref
project starting ref
runner ref
evaluator ref
analysis ref
```

If a provider model cannot be immutably identified, record the strongest available model/version/date/settings evidence and disclose that limitation.

## 14. Smoke-to-standard progression

Recommended sequence:

1. dry-run the harness with dummy/non-scored cases;
2. verify logging and arm isolation;
3. calibrate objective/semantic graders on non-holdout cases;
4. independently review the complete frozen smoke package;
5. run Smoke;
6. analyze benchmark defects separately from protocol outcomes;
7. correct benchmark defects only by versioning/re-freezing;
8. run Standard only after the procedure is stable.

Do not tune MAPS_L on the sealed Standard/holdout results and then report the same cases as independent confirmation.

## 15. Batch completion record

At batch completion preserve:

```text
exact frozen package identity
all valid run IDs
all invalid run IDs + reasons
objective grades
semantic grades
adjudications
aggregate metrics
paired analysis
scenario/domain breakdowns
failure analyses
protocol adherence diagnostics
cost/latency/human-burden measures
known limitations
```

The final report must retain enough per-case evidence to investigate surprising aggregates.
