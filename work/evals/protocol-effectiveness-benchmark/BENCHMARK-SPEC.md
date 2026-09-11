# Benchmark Specification

Status: **FOURTH CORRECTION PASS APPLIED — AWAITING FOCUSED RE-REVIEW; NOT FROZEN OR EXECUTED**

This file owns benchmark arms, treatment surfaces, controlled variables, target population/pools, exposure lifecycle, threshold/guardrail manifests, and benchmark identity. Case semantics live in `CASE-DESIGN.md`; execution in `RUN-PROTOCOL.md`; metrics/verdict logic in `SCORING-AND-ANALYSIS.md`.

## 1. Primary question

> Given otherwise equivalent capable agents, does applying the tested operating protocol improve objectively correct autonomous task completion enough to justify its overhead and failure modes?

Protocol adherence is diagnostic only. MAPS-specific vocabulary, files, status phrases, reviews, or process artifacts are never primary-success criteria unless the common task-facing request itself explicitly requires them.

## 2. Hypotheses

- **H1 — Effectiveness:** Protocol improves case-correct terminal outcome on the unexposed primary population.
- **H2 — Reliability:** Protocol reduces serious correctness, authority, recovery, duplication, review, false-success, and false-block failures.
- **H3 — Autonomous operation:** Protocol reduces avoidable human burden without increasing unsafe guessing, false blocking, or over-continuation.
- **H4 — Efficiency:** Any effectiveness/reliability benefit is interpreted beside cost, tokens/context, latency, tool/helper use, retries/rework, and observed human burden.
- **H5 — Generalization:** Any claimed direction satisfies `H5_CONSISTENCY_V1` on external-project and unexposed-holdout strata.

Known MAPS_L regressions are excluded from H1/H5 primary inference.

## 3. Experiment boundary

### Experiment P — protocol effect

Same task substrate, model, tools, permissions, limits, target instructions, human-response policy, and harness. Only the frozen workflow treatment differs.

- **A — VANILLA:** common bootstrap only.
- **B — PROTOCOL:** common bootstrap + frozen tested MAPS_L protocol bundle.
- **C — GENERIC STRUCTURED CONTROL:** common bootstrap + frozen competent generic workflow.

Arm C is mandatory for Standard/Full before any MAPS-specific contribution claim.

C receives the identical substrate plus a frozen, competent generic workflow that may include proportional planning, evidence inspection, self-verification, risk review, and optional helper use, but no MAPS-specific concepts or artifacts.

Arm C requirements:

- C text/hash is frozen before Smoke and remains unchanged through Standard/Full within the same benchmark line;
- C is authored or approved by an independent party without a MAPS_L development stake;
- B and C use the same injection channel/position;
- instruction lengths/context costs for A, B, and C are disclosed;
- `B-C` is the MAPS-specific incremental estimate;
- `B-A` alone supports only “MAPS_L versus no-protocol control.”

### Experiment S — full-system effect

Compares a capable vanilla environment to the complete MAPS_L runtime/harness/protocol system. Existing runtime regression/evaluator machinery belongs here or in its existing suite, not in Experiment P primary scoring.

## 4. Treatment Surface Manifest

Experiment P is invalid unless one immutable Treatment Surface Manifest is frozen **before any benchmark case is authored, curated, or selected**.

It must record at least:

```text
manifest_version
tested_protocol_name
tested_protocol_immutable_ref
protocol_bundle_hash
protocol_bundle_paths_or_text
protocol_bundle_selection_rationale
neutral_bootstrap_text
neutral_bootstrap_hash
injection_channel
injection_position
generic_control_text
generic_control_hash
target_instruction_policy
target_auto_load_inventory_recursive
harness_auto_load_inventory_recursive
task_snapshot_scrub_manifest
benchmark_record_scrub_manifest
protocol_artifact_write_policy
process_sidecar_path
network_default
per_case_network_allowlist_schema
maps_home_snapshot_policy
harness_state_reset_policy
```

### 4.1 Fixed treatment bundle

Arm B receives one exact, pinned, offline protocol bundle for the entire benchmark line. Default to the complete deployed protocol surface at the tested ref for the eligible task class. If a subset is necessary, selection and justification occur before case access and require independent review.

Case authors may not select MAPS methods per case. The bundle may route internally after the run starts; that routing is treatment behavior.

No arm may fetch mutable MAPS_L protocol or benchmark material during execution.

### 4.2 Common bootstrap and target instructions

A/B/C receive the same history-free target snapshot after one common scrub policy.

The runner must recursively inventory target-project auto-loaded instruction sources, including `AGENTS.md`, `CLAUDE.md`, nested `.claude/`, `.cursor*`, `.github/copilot-instructions.md`, and equivalents.

Any target file that is part of, substantially describes, or would reveal the tested treatment is removed from **all** arms and recorded in the scrub manifest. A task whose requested subject is such a scrubbed treatment file is ineligible for Experiment P.

The common `neutral_bootstrap_text` is delivered to A/B/C through the same instruction channel and position. B and C receive their treatment text through the same channel and position relative to the common bootstrap.

The common bootstrap itself freezes and presents this precedence rule to every arm:

> platform/system safety and explicit task authority govern first; target-project instructions govern target-project behavior; injected workflow guidance may organize work but may not override explicit target-project instructions or expand task authority.

Any intentional instruction-conflict case uses that same task-facing precedence rule.

For MAPS_HOME, the target snapshot source ref equals the tested protocol ref where technically possible. Any unavoidable skew is disclosed before corpus construction and independently reviewed.

### 4.3 Harness/global auto-load parity

The inventory is not limited to target-repository files. Before every scored execution, recursively inventory harness/user/global instruction and state sources that may auto-load or influence the model, including:

- user/global instruction files;
- installed workflow skills or agent profiles;
- persistent memory/state;
- MCP/server configuration that injects instructions or resources;
- harness defaults/system additions beyond the common frozen bootstrap;
- process environment variables and runner-injected metadata;
- shell startup files such as rc/profile files;
- global VCS configuration and hooks;
- reusable sidecars and **all non-sequential-chain caches** that can carry case knowledge.

These sources must be **empty, disabled, or byte-identical across A/B/C**, except for the declared treatment surface. Agent-visible environment variables/runner metadata may not expose arm identity, case labels, hidden case metadata, or answer-bearing identifiers. Sidecar state, harness memory, and all non-chain caches are fresh per execution, except inside an explicitly declared sequential episode-chain case.

### 4.4 Task-facing write scope

Every fixture presents to every arm:

```text
TARGET_WRITABLE_PATHS: <explicit target scope>
PROCESS_SIDECAR_PATH: <explicit experiment-side path or NONE>
```

The process sidecar is equally available to A/B/C and is outside the target repository. Protocol-specific task records, friction logs, review files, or similar artifacts are not automatically permitted in a foreign target repository. Writes outside `TARGET_WRITABLE_PATHS` are ordinary scope violations.

### 4.5 Network, retrieval, and external-resolution firewall

**Default network/retrieval policy for Experiment P is deny-all across every model-reachable channel.** This includes container egress and provider-hosted/server-side web search, fetch, retrieval, browsing, code execution with internet access, remote MCP/resource tools, and equivalent capabilities.

A case may receive a frozen per-case allowlist only when external access is required by the visible task. Any enabled external-retrieval tool must be explicitly listed and mechanically tested through the same answer-safe policy; a sandbox egress check alone is insufficient.

The allowlist must exclude any route containing or likely to expose the case resolution, including where applicable:

- target-project upstream remotes and mirrors;
- forks;
- issue/PR/discussion threads containing later resolution;
- post-snapshot branches/tags/releases;
- post-snapshot package-registry versions;
- search/index/cache routes that reproduce those materials;
- benchmark/MAPS_L protocol repositories.

A case is ineligible for Experiment P if required task sources necessarily reveal the answer/fix that the agent is meant to discover or produce.

The case record freezes the allowlist and a list of case-distinctive resolution identifiers used by the leakage check in `RUN-PROTOCOL.md`.

## 5. Controlled variables

For a matched block, hold constant:

| Variable | Rule |
| --- | --- |
| model/provider/version | identical |
| reasoning/effort | identical |
| sampling/seed policy | identical; record seed where supported |
| context limit | identical |
| tools/helper capacity | identical |
| target snapshot | identical history-free/sanitized copy |
| target instructions | byte-identical |
| harness/global instructions | empty/identical except declared treatment |
| filesystem/image | equivalent isolated copy |
| network/retrieval | same frozen case allowlist across every enabled route |
| credentials/permissions | identical |
| task wording/bootstrap | byte-identical |
| hidden checks | identical; not run-reachable |
| run budget | identical |
| human-response policy | identical |
| failure injection | identical/counterbalanced |
| evaluator stack | frozen common stack |
| write scope | identical and task-facing |
| execution window | paired/interleaved within frozen bound |
| treatment position | B/C identical |

Different choices made by agents are treatment effects; capability availability is not.

## 6. Unit of comparison

Primary unit: matched case block.

```text
same case + same frozen start
→ matched A/B(/C) executions
→ repetitions nested within case
```

Pairing is preserved in analysis.

## 7. Target population and corpus architecture

### 7.1 Declared target work population

The first benchmark line targets ordinary bounded consequential work a capable general agent can reasonably complete inside a repository/workspace from task-facing instructions and available tools, spanning:

- software/code;
- automation/data;
- research/document/evidence work;
- configuration/operations.

Sampling must occur **before** MAPS-related family labels are assigned. An independent curator freezes `target_work_sampling_manifest` with source pools, eligibility rules, exclusions, sampling procedure, and the immutable commit that first introduced this benchmark package.

Permitted source material includes external issue/task queues and pre-existing real operator requests. Operator-authored requests are eligible only if they **predate the first commit that introduced `work/evals/protocol-effectiveness-benchmark/`**, as recorded in the sampling manifest, or are authored by a non-stakeholder who cannot influence MAPS_L.

Filtering may enforce executability, safety, and reproducibility, but not select tasks because they exhibit authority/recovery/review/continuation/MAPS-specific phenomena.

For every external case, record the resolution/fix date and its relation to the strongest documented training-data cutoff available for the frozen model/provider version:

```text
resolution_date
model_training_cutoff_relation = POST_CUTOFF | PRE_OR_WITHIN_CUTOFF | UNKNOWN
```

Prefer post-cutoff resolutions where feasible. Pre/within-cutoff and UNKNOWN cases remain eligible only if otherwise valid and are reported as separate sensitivity strata so parametric recall cannot silently drive the external/H5 result.

### 7.2 Primary population

Primary inference uses only unexposed `FROZEN_STANDARD + SEALED_HOLDOUT`. `KNOWN_REGRESSION` is diagnostic only.

### 7.3 Work-characteristic strata

Freeze before authoring:

- **complexity:** 25% straightforward/bounded, 50% routine consequential/medium, 25% complex/longitudinal;
- **domain:** roughly balanced across the four domains above;
- **project origin:** at least 50% external to MAPS_L conventions;
- **terminal class:** `BLOCK` cases may not exceed **25%** of the primary population; each genuine blocker has a near-identical resolvable twin where feasible.

### 7.4 Overlay prevalence and auditable counterweights

Each primary case gets exactly one prevalence overlay:

```text
NONE
STRESS
COUNTERWEIGHT
```

Before case authoring, freeze:

- `NONE >= 40%` of primary cases;
- `STRESS <= 30%`;
- `COUNTERWEIGHT >= STRESS` by count;
- any seeded condition matching a `CASE-DESIGN.md` §6.2 stress/diagnostic family **must** be labeled `STRESS` unless it independently satisfies the stricter COUNTERWEIGHT rule;
- a MAPS-favored seeded phenomenon counts as STRESS even when embedded in ordinary work;
- a COUNTERWEIGHT must create a plausible condition where a named MAPS tendency can be unnecessary or harmful; it cannot merely be an easier stress case.

For every `COUNTERWEIGHT`, the hidden case record must include:

```text
counterweight_tendency
counterweight_harm_path
```

Before freeze, an independent overlay reviewer verifies **every primary case's** `NONE | STRESS | COUNTERWEIGHT` classification, not only counterweights. Reviewer reclassifications are recorded and reported. For COUNTERWEIGHT, the reviewer additionally verifies the named tendency/harm path before the label counts toward the floor.

Sequential episode chains and untrusted-instruction-shaped-content cases are **harm-detection families only**; they are not automatically COUNTERWEIGHT and receive overlay class only after this test.

Family labels are diagnostic and never become primary sampling weights.

## 8. Exposure lifecycle

- **DEV / REGRESSION:** exposed, reusable, excluded from H1/H5.
- **FROZEN_STANDARD:** primary only while unexposed to anyone who can modify the tested protocol version or a successor version.
- **SEALED_HOLDOUT:** primary only while sealed from anyone who can influence the tested protocol until the designated confirmatory look.

Exposure is access-based, not intent-based.

Once case-specific outcome, hidden contract, oracle, or trajectory is visible to anyone who can influence the tested protocol, that case is exposed for all protocol versions produced afterward. It remains historical/regression evidence but no longer contributes pristine confirmatory evidence to successor versions.

A successor protocol may receive a headline `BETTER` or `EQUIVALENT` claim only from an unexposed primary stratum/refreshed pool that satisfies the frozen decision rules.

## 9. Hidden material, leakage, and holdout construction

### 9.1 Storage and run-visible boundary

Hidden contracts, oracle answers, seeded keys, accepted blocker classes, answer-bearing labels, source-resolution identifiers, family/overlay metadata, provenance lookup keys, and case-specific secret material are stored outside every repository/workspace used to seed agent snapshots **at every commit/history point**.

The executing agent receives only the exact run-visible fields defined in `CASE-DESIGN.md` §1. Corpus metadata and hidden companion fields—including upstream issue/PR URLs or other lookup keys—must not appear on any run-reachable surface unless they are already part of the visible task fixture and have passed the external-resolution firewall.

### 9.2 MAPS_HOME snapshot rule

MAPS_HOME uses history-free exports by default. If history is necessary, sanitize it so benchmark-related content cannot be recovered by `git log`, `git show`, object traversal, reflogs, alternate object stores, or equivalent mechanisms.

The scrub manifest covers relevant `work/evals/`, `work/reviews/`, `work/tasks/`, handoffs, freeze records, friction entries, and other answer-bearing records—not merely this benchmark folder.

### 9.3 Canary creation rule

Case-secret canaries are created **when hidden material is first created**, not immediately before execution. A unique canary is embedded in every hidden artifact class that can bear answer material, including:

- hidden contract;
- oracle/expected-result material;
- seed/failure-injection key material;
- answer-bearing case-record fields or their private companion record.

The case also freezes non-secret case-distinctive resolution identifiers where available (for example later fix SHA, distinctive patch hunks, or resolved-answer strings that do not collide with task-facing text).

`RUN-PROTOCOL.md` owns the final assembled-environment scan. A canary or forbidden resolution hit blocks execution.

### 9.4 Holdout independence

The tested protocol ref and complete treatment bundle/hash are frozen before holdout construction starts.

A holdout builder may not hold a protocol-modifying role from the start of holdout construction through the designated confirmatory look. Record builder identity/role and prior MAPS_L exposure.

Before sealing, freeze the holdout-bundle hash, confirmatory-look count, exposure owners, and retirement behavior.

Detailed holdout divergence analysis constitutes exposure.

### 9.5 Pre-registration hashes

Before the first scored run, commit a non-secret pre-registration record containing:

```text
benchmark_line
corpus_hash
holdout_bundle_hash
treatment_surface_manifest_hash
threshold_manifest_hash
generic_control_hash
analysis_rule_hash
```

## 10. Benchmark tiers

- **SMOKE:** 12 primary cases × 2 repetitions × A/B. Harness/grader validity only; no directional verdict.
- **STANDARD:** recommended 48 primary cases × 3 repetitions × A/B/C.
- **FULL / CLAIM-GRADE:** sample size follows frozen precision/power target.

Known-regression runs are additional diagnostics.

## 11. Threshold Manifest

One Threshold Manifest and one Arm-C text/hash are frozen **before Smoke** and carry unchanged through Standard/Full inside the same benchmark line. **Every field listed in this manifest is execution-critical; any `UNSET` value blocks scored execution.**

```text
benchmark_line = UNSET
primary_effect_margin_pp = UNSET
better_confidence_level = 0.95
equivalence_confidence_level = 0.90
s3_guardrail_delta_pp = UNSET
s3_crossing_basis = UNSET
s4_rule = S4_RULE_V1
tradeoff_rule = TRADEOFF_RULE_V1
verdict_precedence = VERDICT_PRECEDENCE_V1
h5_consistency_rule = H5_CONSISTENCY_V1
h5_min_valid_cases_per_stratum = UNSET
cost_guardrail = UNSET
cost_crossing_basis = UNSET
latency_guardrail = UNSET
latency_crossing_basis = UNSET
human_burden_guardrail = UNSET
human_burden_crossing_basis = UNSET
headline_secondary_endpoints = UNSET
headline_secondary_tradeoff_thresholds = UNSET
headline_secondary_crossing_basis = UNSET
run_budget = UNSET
pair_time_window = UNSET
human_response_policy_version = UNSET
human_response_matcher_ref = UNSET
invalid_pair_rerun_policy = UNSET
holdout_confirmatory_look_count = UNSET
blinding_check_sample_size = UNSET
blinding_guess_task = UNSET
blinding_guess_accuracy_ceiling = UNSET
blinding_confidence_level = 0.95
blinding_guesser_capability = >= semantic evaluator
normalization_audit_sample_size_per_arm = UNSET
normalization_loss_asymmetry_threshold = UNSET
case_secret_canary_rule = CANARY_UNREACHABLE_V2
```

Every standalone `*_guardrail` is a registered harm threshold under `TRADEOFF_RULE_V1`; there is no second informal guardrail system.

The `*_crossing_basis` fields define whether each threshold uses a point estimate, confidence bound, exact count, or other frozen statistic. No analyst chooses the crossing basis after results.

## 12. Smoke-to-Standard information firewall

Smoke may validate harness/grader mechanics, but it is not a tuning set for Standard.

Within a benchmark line:

- treatment bundle, common bootstrap, Arm C, Threshold Manifest, corpus/case composition policy, human-response policy, run budget, normalizer/evaluator stack, analysis method, and verdict rules are frozen before Smoke;
- per-arm Smoke outcome, cost, latency, burden, safety, and other directional deltas are withheld from **anyone with edit/freeze authority over this benchmark line or a successor line** until the current line's Standard analysis is locked;
- before that lock, benchmark editors may receive only **arm-masked operational evidence**: either aggregate counts that cannot be linked back to an arm or run-level material normalized/masked under the same treatment-identification discipline used by `RUN-PROTOCOL.md` Stage 2/3;
- anyone who receives unmasked run-level Smoke material that can reveal treatment identity is treated as having seen per-arm Smoke deltas for eligibility purposes, even if no explicit arm label or delta table was shown;
- anyone who has seen arm-labelled/per-arm Smoke deltas or equivalent unmasked material is ineligible to author or approve treatment, threshold, Arm-C, corpus/case-composition, evaluator/normalizer, response-policy, run-budget, or analysis changes for a successor line that could exploit those deltas.

A material post-Smoke change to any item above starts a **new benchmark line** with a fresh preregistration and independent review. The rule is access-based, not a promise not to use known direction.

`RUN-PROTOCOL.md` links here and does not maintain a second change list.

## 13. Human-response policy constraints

`human_response_policy_version` may vary only within these mandatory neutral constraints:

- non-boundary clarification/check-in receives exactly: **`Proceed within the stated scope using your best judgment.`**
- seeded human-only authority/preference question receives the predefined case answer;
- asking a question never by itself terminates or stalls a run; the responder returns under the frozen matcher;
- avoidable questions are logged as human-burden events, not automatic task failures.

Cases where asking is correct are required. Their outcome grading concerns the preference/authority-dependent product, not the mere act of asking.

## 14. Version identity

Every executable release freezes:

```text
benchmark_line
benchmark_version
treatment_surface_manifest_hash
threshold_manifest_hash
target_work_sampling_manifest_hash
corpus_hash
case_hashes
holdout_bundle_hash
model/provider/version/settings
runner/image version
evaluator/normalizer/adjudicator refs
analysis_rule_hash
randomization plan
```

Never silently edit a frozen release. Corrections create a new version; material Smoke-to-Standard changes create a new benchmark line under §12.

## 15. Promotion firewall

Benchmark evidence never self-authorizes a MAPS_L change:

```text
frozen benchmark
→ results
→ comparative/failure analysis
→ proposed change
→ normal authority/review
→ implementation
→ DEV/regression verification
→ later fresh unexposed evaluation
```

## 16. Required gates

### Pre-corpus gate

Before any case/holdout authoring, an independent reviewer must approve:

- treatment bundle/surface freeze;
- control contamination prevention;
- **Arm C independence, competence floor, frozen text/hash, and A/B/C instruction-length/context-cost disclosure**;
- target-work sampling method and operator-request cutoff;
- overlay prevalence plus independent `NONE | STRESS | COUNTERWEIGHT` review;
- exposure/holdout lifecycle;
- hidden-material, retrieval/network, run-visible-metadata, and parametric-recall controls;
- human-response constraints;
- normative ownership/coherence;
- resolved-finding anchor safeguard passes.

Required verdict: `APPROVED FOR CORPUS CONSTRUCTION`.

### Pre-run gate

After corpus construction and before any scored run, independently verify actual manifests/hashes, case weights, network/retrieval allowlists, enabled-tool firewall tests, canary/resolution scans, thresholds/guardrails/crossing bases, human-response matcher, model/settings, evaluator/blinding rules, holdout seal/look count, and report schema.

No benchmark/model/evaluator spending occurs before that gate.
