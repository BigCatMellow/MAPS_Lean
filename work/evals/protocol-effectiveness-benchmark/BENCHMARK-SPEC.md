# Benchmark Specification

Status: **DRAFT — CORRECTIONS APPLIED; NOT FROZEN OR EXECUTED**

This file owns benchmark arms, treatment manifests, controlled variables, population/pools, lifecycle, thresholds/guardrails that must be frozen before execution, and benchmark identity. Case semantics live in `CASE-DESIGN.md`; execution procedure in `RUN-PROTOCOL.md`; metrics and decision rules in `SCORING-AND-ANALYSIS.md`.

## 1. Primary question

> Given otherwise equivalent capable agents, does applying the tested operating protocol improve objectively correct autonomous task completion enough to justify its overhead and failure modes?

For MAPS_L, protocol adherence is diagnostic only. No MAPS-specific vocabulary, record, status phrase, review shape, or documentation artifact is a success criterion unless the user-facing task itself explicitly requires it.

## 2. Hypotheses

- **H1 — Effectiveness:** protocol-enabled agents have a higher probability of case-correct terminal outcome than a matched no-protocol control on the primary neutral + sealed-holdout population.
- **H2 — Reliability:** protocol-enabled agents have lower rates of serious correctness, authority, recovery, duplication, review, and false-completion failures.
- **H3 — Autonomous operation:** protocol-enabled agents require fewer avoidable human interventions without increasing false blocking, over-continuation, or unauthorized action.
- **H4 — Efficiency tradeoff:** any benefit can be compared against tokens/context, monetary cost, latency, tool/helper use, retries/rework, and observed human burden.
- **H5 — Generalization:** any observed advantage is directionally consistent on external projects and sealed holdout work not used to develop the protocol.

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

## 4. Treatment surface manifest

Experiment P is invalid unless a frozen **Treatment Surface Manifest** exists before any scored run.

The manifest must contain:

```text
manifest_version
tested_protocol_name
tested_protocol_immutable_ref
protocol_bundle_hash
protocol_bundle_paths_or_text
injection_channel
neutral_bootstrap_text
generic_control_text_and_hash
target_instruction_policy
auto_loaded_instruction_inventory
task_snapshot_scrub_manifest
protocol_artifact_write_policy
network_policy
live_update_policy
```

### 4.1 Fixed treatment bundle

Arm B receives one exact, immutable, offline protocol bundle for the entire batch. Case authors may not choose a MAPS method per case after seeing the case/trap. If the protocol itself routes among included methods, that routing is agent behavior.

The bundle may include MAPS_L `AGENTS.md` and subordinate methods selected for the **benchmark release as a whole**, but it must be hashed/pinned before cases execute and may not fetch mutable `main` or other live protocol text during a run.

### 4.2 Target-repository instructions

Target-project instructions that are part of the task environment (for example `AGENTS.md`, `CLAUDE.md`, `.claude/`, `.cursor*`, `.github/copilot-instructions.md`, or equivalents) must be inventoried before the run.

For Experiment P:

- both arms receive the same target-task snapshot;
- any instruction file that would auto-load the tested MAPS treatment is removed from **both** task snapshots and recorded in the scrub manifest;
- Arm B receives the tested MAPS bundle only through the frozen treatment injection channel;
- target-project instructions unrelated to the tested treatment remain identical across arms and retain their normal precedence;
- any unresolved conflict between the tested protocol and target-project instructions is itself case-visible only when that conflict is intentionally part of the fixture.

This avoids giving Vanilla MAPS_L simply because the target repository is MAPS_L.

### 4.3 Protocol artifact writes

Every case predeclares target writable paths identically for all arms. Process artifacts that are not part of the requested product must use a separate experiment-sidecar workspace available equally to all arms.

Writing protocol-specific task records, friction logs, review evidence, or similar files into a foreign target repository is **not automatically permitted**. If outside the case's writable scope, it is graded like any other scope violation.

### 4.4 Live-update behavior

Experiment P does not require MAPS/SIMULATION_DESIGN-style live reasoning updates. Any bounded progress-update contract must be identical across arms and frozen in the common task fixture. Private chain-of-thought is never required.

## 5. Comparison arms

### A — VANILLA

Receives:

- the exact task-facing fixture;
- ordinary platform/model safety instructions;
- the same target-project instructions after the common scrub policy;
- the same tools/capabilities, environment, permissions, limits, and human-response policy;
- the neutral output/status contract from `CASE-DESIGN.md`.

Does not receive the tested protocol bundle.

### B — PROTOCOL

Receives the identical experimental substrate plus the frozen treatment bundle from the Treatment Surface Manifest.

### C — GENERIC STRUCTURED CONTROL

Mandatory for **Standard and Full** tiers before making a MAPS-specific contribution claim.

C receives the identical substrate plus a frozen, competent generic workflow that may include proportional planning, evidence inspection, self-verification, risk review, and optional helper use, but no MAPS-specific concepts or artifacts.

Requirements:

- C is frozen before any comparative A/B outcome is observed for that benchmark release;
- C is authored or approved by an independent party without a MAPS_L development stake;
- instruction lengths/context costs for A, B, and C are disclosed;
- **B − C** is the MAPS-specific estimate;
- **B − A** alone supports only “MAPS_L versus no-protocol control.”

## 6. Two experiments

Keep these separate.

### Experiment P — Protocol effect

```text
same task substrate + same harness/tool capability
A: no tested protocol
B: frozen tested protocol
C: frozen generic structured control (Standard/Full)
```

Answers whether the protocol instructions/operating methods help.

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
| target project | same task snapshot after common scrub |
| filesystem | equivalent isolated copy |
| network | same policy; no live protocol fetch |
| credentials/permissions | same experimental authority |
| task wording | byte-identical across arms |
| hidden checks | identical |
| run budget | identical |
| human-response policy | identical |
| failure injection | identical or counterbalanced |
| evaluator stack | same frozen stack |
| artifact write scope | identical |
| execution time window | paired/interleaved within frozen bound |

A protocol may cause different choices. Capability availability itself may not differ.

## 8. Unit of comparison

The primary unit remains the **paired case block**:

```text
same case + same frozen start
→ matched A/B(/C) fresh executions
→ repetitions nested within case
```

Preserve pairing in analysis.

## 9. Primary target population and corpus architecture

The primary endpoint is defined only on **neutral standard + sealed holdout** cases. `KNOWN_REGRESSION` is a separate diagnostic stratum and never contributes to H1/H5 headline effectiveness.

The primary population must be chosen independently of MAPS_L invariants. For the first release, freeze balance using work characteristics rather than protocol failure categories:

### Complexity strata

- 25% straightforward / bounded
- 50% routine consequential / medium complexity
- 25% complex, long-horizon, interrupted, or multi-party

### Domain strata

Target roughly balanced coverage across:

- software/code;
- automation/data;
- research/document/evidence work;
- configuration/operations.

### Project-origin stratum

At least **50% of primary cases** must come from projects not designed around MAPS_L terminology or conventions.

### Terminal-class stratum

Freeze the `PROCEED` versus genuine `BLOCK` share before execution. Every true-blocker case must have a near-identical resolvable counterweight (“false-blocker twin”) in the same release where feasible.

### Stress phenomena

Authority, recovery, review, context pressure, interruption, etc. are **labels/overlays**, not the basis for primary weighting. Stress and counterweight results are reported separately.

Actual weights must be independently reviewed and frozen against the declared target work population before execution. Report both the predeclared primary weighting and a clean-vs-stress sensitivity analysis.

## 10. Evidence pools

Use:

- **DEV / REGRESSION** — exposed, reusable, may guide changes; excluded from H1/H5.
- **FROZEN STANDARD** — protocol-neutral primary cases frozen for versioned comparisons.
- **SEALED HOLDOUT** — primary cases unavailable to anyone who can influence the tested protocol until the designated confirmatory look.

Runtime-mechanism regression artifacts are not converted directly into Experiment P cases. A real incident may enter P only if independently re-authored as a protocol-neutral agent task whose outcome can be exhibited by all arms.

## 11. Holdout firewall

Holdout retirement is exposure-based, not intent-based.

If anyone who can influence the tested protocol sees holdout content, hidden contract, or per-case trajectory, that case is retired from pristine holdout status after that evaluation whether or not they claim it informed a change.

Before sealing:

- store the holdout bundle outside any run-reachable repository/workspace;
- record a cryptographic hash of the sealed bundle;
- freeze the allowed number of confirmatory looks for that holdout release;
- disclose case-builder identity/role and whether builders were exposed to MAPS_L;
- ensure task snapshots available to executing agents exclude benchmark directories such as `work/evals/`;
- deny run-time network access to the live MAPS_L repository when it could expose benchmark/protocol material; Arm B uses the pinned offline treatment bundle.

Detailed divergence analysis exposes a holdout. After the designated evaluation, exposed cases may become DEV/regression evidence and the sealed pool must be replenished for future confirmation.

Repeated MAPS version selection against the same holdout is prohibited beyond the frozen look count.

## 12. Hidden contract boundary

`CASE-DESIGN.md` owns hidden-contract semantics. The governing rule is:

> **Hidden does not mean additional.**

Any requirement capable of changing terminal outcome must be derivable from the task-facing fixture, stated scope/permissions, or ordinary correctness of the requested product. Hidden material may define **checks**, not secret MAPS-favoring requirements.

## 13. Evidence hierarchy and evaluator separation

Prefer:

1. deterministic objective checks;
2. direct artifact/state inspection;
3. normalized, blinded semantic evaluation only for unresolved properties;
4. independent second evaluation;
5. blinded/non-contributor adjudication for critical or headline-affecting disputes.

`RUN-PROTOCOL.md` owns execution/blinding details.

## 14. Benchmark tiers

- **SMOKE:** 12 primary cases × 2 repetitions × A/B. Harness/grader validation only; **no directional effectiveness verdict**.
- **STANDARD:** recommended 48 primary cases × 3 repetitions × A/B/C. Supports controlled estimates, but equivalence or subgroup claims may remain underpowered.
- **FULL / CLAIM-GRADE:** case count is determined by the frozen precision/power target before execution. If the intended claim is equivalence within ±5 percentage points, expect substantially more than 60 cases; the required count must be computed and frozen rather than assumed.

Known-regression runs are additional diagnostics and do not count toward primary-case totals.

## 15. Pre-execution threshold manifest

Before the **first scored A/B run, including Smoke**, freeze all values below. `UNSET` blocks execution.

```text
primary_effect_margin_pp = UNSET
better_confidence_level = 0.95
equivalence_confidence_level = 0.90
s3_guardrail = UNSET
s4_guardrail = arm-exclusive adjudicated S4 => BETTER ineligible
cost_guardrail = UNSET
latency_guardrail = UNSET
human_burden_guardrail = UNSET
run_budget = UNSET
pair_time_window = UNSET
human_response_policy_version = UNSET
invalid_pair_rerun_policy = UNSET
holdout_confirmatory_look_count = UNSET
blinding_check_rule = exact binomial test against 0.5 at alpha 0.05
headline_secondary_endpoints = UNSET (small fixed set)
```

Values may be populated only before execution and must be independently reviewed. Smoke may inform later sample size only through arm-blind pooled variability/operational evidence, not observed arm deltas.

Any post-result benchmark defect decision must be made blind to arm where possible. If a scored case is dropped or re-versioned after outcomes exist, report results under both the original and corrected benchmark versions.

## 16. Human-response policy owner

The exact response policy is frozen in the threshold manifest. The neutral default for Experiment P is:

- non-boundary clarification/check-in → fixed reply: **“Proceed within the stated scope using your best judgment.”**
- seeded human-only boundary/preference question → predefined case answer;
- asking a question never by itself terminates the run;
- avoidable questions are logged as human-burden events;
- cases where asking is the correct behavior are required in the corpus.

`RUN-PROTOCOL.md` specifies logging and delivery.

## 17. Version identity

Every executable release freezes:

```text
benchmark_version
treatment_surface_manifest_hash
threshold_manifest_hash
corpus_hash
case hashes
holdout_bundle_hash
model/provider/version/settings
runner version
evaluator/normalizer/adjudication versions
analysis version
randomization plan
```

Never silently edit a frozen release. Corrections create a new version with compatibility notes.

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
→ later fresh holdout
```

Do not modify the protocol mid-batch.

## 19. Required pre-corpus review

Before corpus construction begins, an independent reviewer must approve:

- treatment-surface definition and no control contamination;
- hidden-contract neutrality;
- primary-population independence from MAPS_L theory;
- mandatory C plan for Standard/Full;
- holdout firewall;
- case/counterweight architecture;
- concept ownership/no duplicated normative rules;
- current status accurately says **not executed**.

No corpus construction begins until the verdict is `APPROVED FOR CORPUS CONSTRUCTION`.

## 20. Required pre-run freeze review

After corpus construction but before any scored run, independently verify:

- exact case/population weights and hashes;
- treatment/control capability parity;
- threshold/guardrail values;
- human-response policy;
- run budgets;
- evaluator normalization/blinding;
- S4 rule;
- invalid/UNKNOWN policy;
- holdout seal/look count;
- immutable model/configuration refs;
- report schema;
- status accuracy.

No model/evaluator execution or benchmark spending occurs before this gate.
