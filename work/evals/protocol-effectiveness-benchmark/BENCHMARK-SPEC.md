# Benchmark Specification

Status: **SECOND CORRECTION PASS APPLIED — AWAITING FOCUSED RE-REVIEW; NOT FROZEN OR EXECUTED**

This file owns benchmark arms, treatment manifests, controlled variables, target population/pools, lifecycle, thresholds/guardrails that must be frozen before execution, and benchmark identity. Case semantics live in `CASE-DESIGN.md`; execution procedure in `RUN-PROTOCOL.md`; metrics and verdict logic in `SCORING-AND-ANALYSIS.md`.

## 1. Primary question

> Given otherwise equivalent capable agents, does applying the tested operating protocol improve objectively correct autonomous task completion enough to justify its overhead and failure modes?

For MAPS_L, protocol adherence is diagnostic only. No MAPS-specific vocabulary, record, status phrase, review shape, or documentation artifact is a success criterion unless the task-facing request itself explicitly requires it.

## 2. Hypotheses

- **H1 — Effectiveness:** protocol-enabled agents have a higher probability of case-correct terminal outcome than a matched no-protocol control on the primary unexposed standard + sealed-holdout population.
- **H2 — Reliability:** protocol-enabled agents have lower rates of serious correctness, authority, recovery, duplication, review, and false-completion failures.
- **H3 — Autonomous operation:** protocol-enabled agents require fewer avoidable human interventions without increasing false blocking, over-continuation, or unauthorized action.
- **H4 — Efficiency tradeoff:** any benefit can be compared against tokens/context, monetary cost, latency, tool/helper use, retries/rework, and observed human burden.
- **H5 — Generalization:** any observed advantage satisfies the frozen `H5_CONSISTENCY_V1` rule on external-project and unexposed holdout strata.

Known MAPS_L regression cases are **not** part of H1 or H5 inference.

## 3. What is not being tested

The primary benchmark does not ask whether an agent:

- recites MAPS_L rules;
- creates MAPS-shaped records;
- uses more planning, helpers, reviews, messages, or files;
- emits `DONE / Changed / Verified` or other MAPS-specific status text;
- follows an existing MAPS runtime regression property;
- looks more organized to a reviewer.

Those may be post-outcome diagnostics only.

## 4. Treatment Surface Manifest

Experiment P is invalid unless a frozen **Treatment Surface Manifest** exists **before corpus construction begins**.

The manifest must contain:

```text
manifest_version
tested_protocol_name
tested_protocol_immutable_ref
protocol_bundle_hash
protocol_bundle_paths_or_text
protocol_bundle_selection_rationale
injection_channel
injection_position
neutral_bootstrap_text
generic_control_text_and_hash
target_instruction_policy
auto_loaded_instruction_inventory_recursive
task_snapshot_scrub_manifest
benchmark_record_scrub_manifest
protocol_artifact_write_policy
process_sidecar_path
network_policy
live_update_policy
maps_home_snapshot_policy
```

### 4.1 Fixed treatment bundle before case access

Arm B receives one exact, immutable, offline protocol bundle for the entire benchmark line. The bundle contents and hash are frozen **before any benchmark case is authored or curated**.

Default: use the complete deployed protocol surface at the pinned tested ref that a normal MAPS_L agent would receive for the eligible task class. If a subset is necessary, its selection and justification must be made without case/trap access and independently reviewed before corpus construction.

Case authors may not choose a MAPS method per case. If the frozen protocol itself routes among included methods, that routing is agent behavior.

The bundle may not fetch mutable `main` or other live protocol text during a run.

### 4.2 Target-repository instructions and common bootstrap

Target-project instructions that are part of the task environment (for example `AGENTS.md`, `CLAUDE.md`, recursively nested `.claude/`, `.cursor*`, `.github/copilot-instructions.md`, or equivalents) must be recursively inventoried before the run.

For Experiment P:

- A/B/C receive the same history-free target-task snapshot after the common scrub policy;
- any file that is part of, substantially describes, or would expose the tested protocol is removed from **all** target snapshots and recorded in the scrub manifest unless the case is declared ineligible for Experiment P;
- a task whose requested subject is one of those scrubbed treatment/protocol-description files is ineligible for Experiment P;
- the common `neutral_bootstrap_text` is delivered to A/B/C through the same system/instruction channel and position;
- B and C receive their treatment text through the same injection channel and position;
- target-project instructions unrelated to the tested treatment remain byte-identical across arms;
- the common bootstrap freezes one precedence rule: **platform/system safety and explicit task authority govern first; target-project instructions govern target-project behavior; injected workflow guidance may organize work but may not override an explicit target-project instruction or expand task authority**;
- any intentional instruction-conflict case uses that same common precedence rule as its answer-key basis.

For MAPS_HOME, the task-snapshot source ref must equal the tested protocol ref where technically possible. Any unavoidable skew is disclosed before case construction and independently reviewed.

### 4.3 Task-facing write scope and process sidecar

Every fixture tells every arm, in common task-facing text:

```text
TARGET_WRITABLE_PATHS: <explicit paths/scope>
PROCESS_SIDECAR_PATH: <explicit path outside target repository, or NONE>
```

Process-sidecar storage is available equally to A/B/C. Process artifacts not requested as product output belong there.

Writing task records, friction logs, review evidence, or other protocol artifacts into a foreign target repository is not automatically permitted. If outside `TARGET_WRITABLE_PATHS`, it is graded exactly like any other scope violation.

### 4.4 Live-update behavior

Experiment P imposes no MAPS/SIMULATION_DESIGN-specific progress-update requirement. Any platform-required progress surface is identical across arms and excluded from task success. Private chain-of-thought is never required.

## 5. Comparison arms

### A — VANILLA

Receives the common substrate/bootstrap and no tested protocol bundle.

### B — PROTOCOL

Receives the identical substrate plus the frozen treatment bundle.

### C — GENERIC STRUCTURED CONTROL

Mandatory for **Standard and Full** tiers before making a MAPS-specific contribution claim.

C receives the identical substrate plus a frozen, competent generic workflow that may include proportional planning, evidence inspection, self-verification, risk review, and optional helper use, but no MAPS-specific concepts or artifacts.

Requirements:

- C text/hash is frozen before Smoke and remains unchanged through Standard/Full within the same benchmark line;
- C is authored or approved by an independent party without a MAPS_L development stake;
- B and C use the same injection channel/position;
- instruction lengths/context costs for A, B, and C are disclosed;
- **B − C** is the MAPS-specific estimate;
- **B − A** alone supports only “MAPS_L versus no-protocol control.”

## 6. Two experiments

### Experiment P — Protocol effect

```text
same task substrate + same harness/tool capability
A: common bootstrap only
B: common bootstrap + frozen tested protocol
C: common bootstrap + frozen generic structured control (Standard/Full)
```

### Experiment S — Full-system effect

```text
A: capable vanilla agent environment
B: complete MAPS_L runtime/harness/protocol system
```

Runtime-mechanism regression cases, MAPS portable Run Records, `runtime/evaluation/evaluator.py`, and existing MAPS_L end-to-end runtime properties belong here or in their existing regression suite. Experiment S has weaker mechanism attribution because runtime, persistence, orchestration, and tooling may differ.

Run P before using S to make protocol-level causal claims.

## 7. Controlled variables

For every paired block, freeze and record:

| Variable | Rule |
| --- | --- |
| model/provider/version | exact same within compared arms |
| reasoning/effort | same |
| sampling/seed policy | same; seed where supported |
| context limit | same effective limit |
| tools | same available capabilities |
| helpers/subagents | same capability and hard limits |
| target project | same history-free scrubbed snapshot |
| filesystem | equivalent isolated copy |
| network | same policy; no live protocol/benchmark fetch |
| credentials/permissions | same experimental authority |
| task wording/bootstrap | byte-identical across arms |
| hidden checks | identical and external to run snapshot |
| run budget | identical |
| human-response policy | identical |
| failure injection | identical or counterbalanced |
| evaluator stack | same frozen stack |
| artifact write scope | identical and task-facing |
| execution time window | paired/interleaved within frozen bound |
| treatment injection position | B/C identical; common bootstrap identical to all arms |

A protocol may cause different choices. Capability availability itself may not differ.

## 8. Unit of comparison

The primary unit remains the **paired case block**:

```text
same case + same frozen start
→ matched A/B(/C) fresh executions
→ repetitions nested within case
```

Preserve pairing in analysis.

## 9. Target population and primary corpus architecture

### 9.1 Declared target work population

The first benchmark line targets **ordinary bounded consequential work that a capable general agent could reasonably complete inside a repository/workspace from task-facing instructions and available tools**, across software/code, automation/data, research/document/evidence, and configuration/operations work.

Its sampling source must be independent of MAPS_L failure categories: external repository issue/task queues and operator-authored work requests are sampled **before** assigning any authority/recovery/review/continuation/MAPS-related label. Tasks may be filtered for executability and safety, but not selected because they instantiate a MAPS invariant.

Before case authoring, an independent curator freezes a `target_work_sampling_manifest` describing the source pools, eligibility rules, exclusions, and sampling procedure. That manifest is part of corpus provenance.

### 9.2 Primary endpoint population

The primary endpoint is defined only on **unexposed FROZEN_STANDARD + SEALED_HOLDOUT** cases. `KNOWN_REGRESSION` is a separate diagnostic stratum and never contributes to H1/H5 headline effectiveness.

### 9.3 Work-characteristic strata

Freeze the first release around characteristics independent of protocol theory:

- **complexity:** 25% straightforward/bounded, 50% routine consequential/medium, 25% complex/longitudinal;
- **domain:** roughly balanced across software/code, automation/data, research/document/evidence, configuration/operations;
- **project origin:** at least 50% external to MAPS_L conventions;
- **terminal class:** predeclared `PROCEED` vs genuine `BLOCK`, with blocker/resolvable twins where feasible.

### 9.4 Stress-overlay ceiling and counterweight floor

Each primary case has exactly one corpus-overlay class for prevalence accounting:

```text
NONE
STRESS
COUNTERWEIGHT
```

Freeze these constraints before authoring cases:

- at least **40%** of primary cases are `NONE` — no seeded MAPS-stress trap;
- at most **30%** are `STRESS`;
- `COUNTERWEIGHT` case count must be **at least** the `STRESS` case count inside the primary pools;
- a case designed to demonstrate a MAPS-favored behavior counts as `STRESS` even if it also contains ordinary work;
- a counterweight case must create a plausible condition where the corresponding MAPS tendency could be unnecessary or harmful; it cannot merely be an easier stress case.

Stress family labels remain diagnostic overlays and never become sampling weights.

The independent population/weight reviewer must check both work-characteristic strata **and** overlay prevalence. Report the frozen primary weighting plus clean/no-trap vs stress vs counterweight sensitivity analyses.

## 10. Evidence pools and exposure lifecycle

Use:

- **DEV / REGRESSION** — exposed, reusable, may guide changes; excluded from H1/H5.
- **FROZEN STANDARD** — primary only while unexposed to anyone able to modify the tested protocol for the protocol version being evaluated.
- **SEALED HOLDOUT** — primary cases unavailable to anyone who can influence the tested protocol until the designated confirmatory look.

Runtime-mechanism regression artifacts are not converted directly into Experiment P cases. A real incident may enter P only if independently re-authored as a protocol-neutral agent task whose outcome can be exhibited by all arms.

### 10.1 Standard-pool retirement across protocol versions

Exposure rules apply to FROZEN_STANDARD as well as holdout:

- once per-case outcome, hidden contract, or trajectory is visible to anyone who can influence the tested protocol, that case is **exposed** for every protocol version produced afterward;
- an exposed standard case remains valid historical/regression evidence but counts as DEV for later protocol versions;
- a later protocol version may receive a `BETTER` or `EQUIVALENT` headline only if the required decision rules also hold on an **unexposed primary stratum** or a refreshed standard pool;
- aggregate historical tables may still show exposed cases, but they are visibly separated from current confirmatory inference.

## 11. Hidden-material and holdout firewall

Exposure is determined by access, not claimed intent.

### 11.1 Storage rule for every pool

Hidden contracts, oracle answers, seeded-condition keys, and any case-specific secret capable of revealing the expected result are stored **outside every repository/workspace used to seed agent run snapshots, at every commit/history point**. This applies to DEV, FROZEN_STANDARD, and SEALED_HOLDOUT.

Run repositories may contain only task-facing fixtures and non-secret provenance identifiers.

### 11.2 MAPS_HOME snapshot rule

MAPS_HOME run snapshots are history-free exports by default. If history is technically required, it must be sanitized so benchmark-related files cannot be recovered with `git log`, `git show`, object traversal, reflogs, alternate objects, or equivalent mechanisms.

The scrub manifest covers benchmark-related records across the repository, including relevant `work/evals/`, `work/reviews/`, `work/tasks/`, handoffs, freeze records, and friction entries—not only the benchmark folder.

Before any scored run, a frozen canary check places a unique case-secret token in each hidden contract and proves that token is unreachable from the agent snapshot, including `.git`/VCS history and ordinary repository search. Any canary hit invalidates the snapshot before execution.

### 11.3 Holdout construction independence

The tested protocol ref and complete treatment bundle/hash are frozen **before holdout construction starts**.

A holdout builder must hold no protocol-modifying role from the start of holdout construction through the designated confirmatory look. Builder identity/role and prior MAPS_L exposure are disclosed.

Before sealing:

- store holdout contents outside run-reachable repositories;
- compute the sealed bundle hash;
- freeze the allowed confirmatory-look count;
- deny run-time access to live MAPS_L benchmark/protocol content;
- record exposure owners and retirement behavior.

Detailed divergence analysis constitutes exposure.

### 11.4 Pre-registration hashes

Before the first scored run, commit to the repository/PR a pre-registration record containing only immutable identities/hashes, not holdout contents:

```text
benchmark_line
corpus_hash
holdout_bundle_hash
treatment_surface_manifest_hash
threshold_manifest_hash
generic_control_hash
analysis_rule_hash
```

Repeated MAPS version selection against the same exposed holdout/standard corpus is prohibited beyond the frozen rules above.

## 12. Hidden contract boundary

`CASE-DESIGN.md` owns hidden-contract semantics. Governing rule: **hidden does not mean additional**. Hidden material defines checks, not secret MAPS-favoring requirements.

## 13. Evidence hierarchy

Prefer deterministic objective checks, then artifact/state inspection, then normalized blinded semantic evaluation, independent second evaluation, and finally blinded/non-contributor adjudication where required. `RUN-PROTOCOL.md` owns execution/blinding details.

## 14. Benchmark tiers

- **SMOKE:** 12 primary cases × 2 repetitions × A/B. Harness/grader validity only; no directional effectiveness verdict.
- **STANDARD:** recommended 48 primary cases × 3 repetitions × A/B/C.
- **FULL / CLAIM-GRADE:** size set by the frozen precision/power target before execution.

Known-regression runs are additional diagnostics.

## 15. Pre-execution Threshold Manifest

One Threshold Manifest and one Arm-C text/hash are frozen **before Smoke** and carry unchanged through Standard/Full within the same benchmark line. `UNSET` blocks execution.

```text
benchmark_line = UNSET
primary_effect_margin_pp = UNSET
better_confidence_level = 0.95
equivalence_confidence_level = 0.90
s3_guardrail_delta_pp = UNSET
s4_rule = S4_RULE_V1
tradeoff_rule = TRADEOFF_RULE_V1
verdict_precedence = VERDICT_PRECEDENCE_V1
h5_consistency_rule = H5_CONSISTENCY_V1
cost_guardrail = UNSET
latency_guardrail = UNSET
human_burden_guardrail = UNSET
headline_secondary_endpoints = UNSET (small fixed set)
headline_secondary_tradeoff_thresholds = UNSET (metric => benefit direction/threshold + harm direction/threshold)
run_budget = UNSET
pair_time_window = UNSET
human_response_policy_version = UNSET
human_response_matcher_ref = UNSET
invalid_pair_rerun_policy = UNSET
holdout_confirmatory_look_count = UNSET
blinding_check_sample_size = UNSET
blinding_guess_accuracy_ceiling = UNSET
blinding_confidence_level = 0.95
blinding_guesser_capability = >= semantic evaluator
normalization_audit_sample_size_per_arm = UNSET
case_secret_canary_rule = CANARY_UNREACHABLE_V1
```

Rule IDs above are defined exactly in `SCORING-AND-ANALYSIS.md` or `RUN-PROTOCOL.md`; this manifest selects and freezes them.

### 15.1 No post-Smoke re-freeze inside a benchmark line

After any arm-level scored Smoke outcome exists, none of the following may change inside that benchmark line:

- practical margin;
- safety/S3/S4 rules;
- tradeoff/verdict rules or headline-secondary thresholds;
- headline secondaries;
- run budgets;
- human-response policy;
- Arm-C text;
- evaluator/normalizer decision criteria.

A change starts a **new benchmark line** and requires a fresh pre-run package. Anyone authorized to edit/freeze that replacement line may see only arm-pooled Smoke operational evidence until the replacement Standard package is frozen. Per-arm Smoke outcome deltas are withheld from benchmark-line editors during that decision.

Smoke may inform sample size only through arm-pooled variability/operational evidence.

Post-result benchmark-defect decisions are arm-blind where possible. If a scored case is dropped/re-versioned, preserve and report both original and corrected-version results.

## 16. Human-response policy owner

The exact policy/matcher is frozen in the Threshold Manifest. `RUN-PROTOCOL.md` owns delivery, logging, arm-blind classification, and misroute handling. Case semantics for asking-is-correct live in `CASE-DESIGN.md`.

## 17. Version identity

Every executable release freezes:

```text
benchmark_line/version
target_work_sampling_manifest_hash
treatment_surface_manifest_hash
threshold_manifest_hash
corpus_hash
case hashes
holdout_bundle_hash
generic_control_hash
model/provider/version/settings
runner version
evaluator/normalizer/adjudication versions
analysis-rule hash
randomization plan
```

Never silently edit a frozen release. Corrections create a new version/line with compatibility notes.

## 18. Promotion firewall

Benchmark evidence never self-authorizes a MAPS_L change:

```text
frozen benchmark
→ results
→ comparative/failure analysis
→ proposed change
→ normal authority/review
→ implementation
→ DEV/regression verification
→ later fresh unexposed confirmation
```

Do not modify the protocol mid-batch.

## 19. Required pre-corpus review

Before corpus construction, an independent reviewer must approve:

- treatment bundle freeze timing and control contamination protections;
- hidden-material storage/history scrub/canary rule;
- hidden-contract neutrality;
- declared target population and stress/counterweight prevalence bounds;
- standard/holdout exposure lifecycle;
- mandatory C design and channel parity;
- case/counterweight architecture;
- concept ownership/no duplicated normative rules;
- current status accurately says not executed.

No corpus construction begins until the verdict is `APPROVED FOR CORPUS CONSTRUCTION`.

## 20. Required pre-run freeze review

After corpus construction but before any scored run, independently verify:

- exact population/overlay weights and hashes;
- committed pre-registration hashes;
- treatment/control capability parity;
- Threshold Manifest has no `UNSET` field;
- one-line Smoke→Standard freeze discipline;
- human-response matcher/policy;
- run budgets;
- evaluator normalization/blinding and normalization-loss audit;
- S4/S3/tradeoff/verdict rule IDs;
- INVALID/UNKNOWN policy;
- hidden-secret canary passes;
- holdout seal/look count;
- immutable model/configuration refs;
- report schema;
- status accuracy.

No scored model/evaluator execution or benchmark spending occurs before this gate.
