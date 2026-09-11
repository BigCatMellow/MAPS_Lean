# Task: protocol effectiveness corpus construction

- Status: `BLOCKED_ON_DEPENDENCY`
- AGI status: `AGI READY`
- Type: `EVALUATION DATASET / CUSTODY`
- Owner: independent corpus curator/custodian
- Risk: `HIGH`
- Parent: [`protocol-effectiveness-benchmark.md`](protocol-effectiveness-benchmark.md)
- Goal: Construct the initial unexposed primary corpus and sealed holdout under the independently approved Experiment-P design, preserve access-based exposure integrity, and return only a non-secret freeze package for independent pre-run review.
- Autonomous continuation: `YES` once an eligible curator/custody environment exists.

## Source / inputs

Read first:

1. repository `AGENTS.md`;
2. `work/evals/protocol-effectiveness-benchmark/BENCHMARK-SPEC.md`;
3. `CASE-DESIGN.md`;
4. `RUN-PROTOCOL.md`;
5. `SCORING-AND-ANALYSIS.md` only for case-independent analysis requirements;
6. `pre-corpus/TREATMENT-SURFACE-MANIFEST.md`;
7. `pre-corpus/GENERIC-CONTROL.md`;
8. `pre-corpus/TARGET-WORK-SAMPLING-MANIFEST.md`;
9. `pre-corpus/CUSTODY-AND-EXPOSURE-PLAN.md`;
10. r9 approval `work/reviews/pr-341-rereview-evidence-369bcca.md`.

The five normative owner documents are frozen design owners. Do not rewrite them while building the corpus.

## Preconditions

Before selecting a single case:

- treatment bundle inventory/hash is set and independently checked;
- exact neutral bootstrap, B launcher, and C text/hash are frozen;
- Arm C has independent competence/non-strawman approval;
- A/B/C instruction/context costs are measured and disclosed;
- independent curator identity/role is recorded;
- concrete source pools and sampling-reference model/cutoff are frozen;
- deterministic selection seed is derived from the frozen source-pool manifest;
- an access-controlled storage channel exists that excludes anyone who can modify MAPS_L or a successor protocol;
- selected case IDs/content will not be committed to this repository or shown in a user-visible MAPS_L-owner chat before the permitted look.

If any precondition is missing, stop case selection and return the exact missing item.

## Boundary

### MAY

- finalize the non-secret sampling/source-pool manifest inside the approved rules;
- deterministically select candidate tasks inside the sealed custody environment;
- construct benchmark-visible case records and hidden companion records in sealed storage;
- create canaries when hidden material is first created;
- reject objectively ineligible selected tasks using only frozen eligibility rules and deterministic replacement order;
- assign ordinary domain/complexity/project-origin strata;
- after sampling, construct terminal truth, hidden checks, stress-family records, counterweight fields, and task fixtures according to CASE-DESIGN;
- build the sealed-holdout subset and freeze its hash/look-count/exposure-owner record;
- return hashes, counts, aggregate stratum summaries, rejection ledger, and non-secret custody evidence to PR #341.

### MUST NOT

- modify MAPS_L runtime/protocol behavior;
- modify the five normative benchmark owner documents;
- select tasks because they look favorable/unfavorable to MAPS_L;
- assign MAPS-related stress/counterweight/family labels before sampling;
- expose selected FROZEN_STANDARD/SEALED_HOLDOUT identities, fixtures, hidden records, answer-bearing provenance, canaries, or resolution identifiers to MAPS_L protocol modifiers;
- put selected primary/holdout content in MAPS_L git history;
- run A/B/C agents, Smoke, Standard, evaluators, graders, or benchmark APIs;
- spend money;
- merge PR #341.

## Construction requirements

Build toward the approved Standard target of 48 primary cases. Freeze the exact FROZEN_STANDARD/SEALED_HOLDOUT allocation before authoring and preserve the combined owner-defined population constraints.

For every selected case, enforce `CASE-DESIGN.md` exactly. In particular:

- A/B/C can technically succeed under equal capability;
- hidden material adds checks only, never unstated requirements;
- exact run-visible field boundary is preserved;
- PROCEED/BLOCK truth and accepted blocker classes are frozen;
- BLOCK cases satisfy the prevalence ceiling and resolvable-twin rule where feasible;
- source/provenance and later resolution are separable from authorized run sources;
- external cases receive sampling-reference cutoff fields;
- seeded stress is recorded before overlay audit;
- counterweight labels require the approved harm-path semantics;
- a simple competent agent is allowed to win and protocol overhead can make an arm lose.

## Required sealed outputs

Keep inaccessible to MAPS_L protocol modifiers until the permitted look:

```text
selected case IDs / source identifiers
case fixtures / starting-state packages
benchmark-visible case records
hidden companion records
objective checks / semantic properties
accepted blocker classes
seeded_stress_families
counterweight fields
canaries / resolution identifiers
holdout membership and holdout content
answer-bearing provenance
```

## Required non-secret repository outputs

Return only:

```text
treatment_surface_manifest_hash
protocol_bundle_hash
generic_control_hash
target_work_sampling_manifest_hash
sampling seed derivation evidence (not selected ordering)
curator/custodian identity + eligibility statement
storage/access-control class
candidate selections attempted / accepted / rejected counts
rejection-reason counts under frozen categories
aggregate domain/complexity/project-origin/terminal-class counts
aggregate NONE/STRESS/COUNTERWEIGHT counts after independent overlay review
aggregate seeded_stress prevalence
FROZEN_STANDARD count
SEALED_HOLDOUT count
corpus_hash
holdout_bundle_hash
confirmatory look count
exposure owners
freeze timestamp
```

Do not include data from which selected case identities can be trivially reconstructed if that would create exposure.

## Verification / review

Before this task can become DONE:

1. independently verify deterministic sampling/rejection procedure;
2. independently audit every primary case's overlay class after case construction;
3. verify population constraints and BLOCK/twin rules;
4. verify hidden checks are task-derived and protocol-neutral;
5. verify case sources/answers cannot leak through intended run surfaces;
6. verify access logs/custody state and seal hashes;
7. obtain a fresh independent **corpus/pre-freeze review**.

Required next-gate verdict should explicitly state whether the actual corpus/freeze package is approved to proceed to the separate pre-run manifest/threshold/runner gate. It does not authorize execution by itself.

## Failure / recovery

- Ineligible sampled task → record frozen reason; take next deterministic candidate.
- Exposure before freeze → retire affected case from pristine primary status and deterministically replace it.
- Custody breach after freeze → retire affected case and report exposure; do not silently reseal the same case.
- Stratum imbalance caused by objective rejections → continue deterministic within-stratum ordering; do not hand-pick a replacement.
- Required source necessarily reveals resolution → case is ineligible.
- Missing independent custody → remain BLOCKED; public shaping may continue but no case content is created.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Current blocker

`independent curator/custodian + access-controlled storage unavailable in the current MAPS_L owner context`.

A fresh review chat is not enough if the repository owner can access the selected case content; exposure is access-based. The next worker must have genuinely separate custody for selected primary/holdout material.
