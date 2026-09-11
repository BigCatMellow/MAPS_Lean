# Target Work Sampling Manifest — candidate method

Status: **CANDIDATE METHOD — SOURCE POOLS / REFERENCE MODEL UNSET; NO CASE SELECTION PERMITTED**

Normative population rules remain in `../BENCHMARK-SPEC.md`. This file is the concrete sampling-method instance to be completed and frozen by an **independent curator before any case IDs are selected or MAPS-related labels are assigned**.

## Immutable benchmark cutoff

```text
benchmark_package_first_commit = bb030461433d264688699a277ee901ed70ae9ca7
benchmark_package_first_commit_date = 2026-09-10T15:50:07Z
approved_design_head = 369bccaf68b258c70eb6efec0c9f70115c8014cb
```

Operator-authored source requests are eligible only if they predate the package-first commit above or were authored by a non-stakeholder unable to influence MAPS_L.

## Independent curator fields — MUST be set before selection

```text
curator_identity = UNSET
curator_role = UNSET
prior_MAPS_L_development_role = UNSET
source_pool_freeze_timestamp = UNSET
sampling_reference_model_provider_version = UNSET
sampling_reference_training_cutoff = UNSET | UNKNOWN
source_pool_manifest_hash = UNSET
selection_seed = DERIVED AFTER source_pool_manifest_hash IS FROZEN
```

The curator must not select source pools because they exhibit MAPS-specific authority/recovery/review/continuation phenomena.

## Source-pool requirements

Freeze concrete source pools before task selection. Pools should be broad enough that task sampling, not hand-picking, determines the candidate set.

Requirements:

- cover software/code, automation/data, research/document/evidence, and configuration/operations work;
- use multiple unrelated projects/sources rather than one ecosystem;
- at least 50% of eventual primary cases must originate outside MAPS_L conventions;
- sources must provide a reconstructable pre-resolution starting state and task-facing request;
- exclude sources requiring private credentials, irreversible real-world effects, unsafe/illegal actions, or answer sources that cannot be separated from authorized task sources;
- do not use MAPS_L regression cases for primary sampling;
- do not inspect or assign `NONE | STRESS | COUNTERWEIGHT`, stress families, MAPS mechanism labels, or expected winner while freezing pools or drawing the sample.

The frozen source-pool record must identify each queue/repository/source, snapshot/ref/date, eligible task date window, and objective eligibility filters.

## Deterministic selection

After the independent curator freezes the complete source-pool manifest and its SHA-256, derive the first sampling seed as:

```text
selection_seed = SHA256(
  "MAPS_PROTOCOL_EFFECTIVENESS_V0\n" +
  approved_design_head + "\n" +
  source_pool_manifest_hash + "\n"
)
```

Use the digest as the deterministic PRNG seed. Do not reroll because selected tasks look favorable or unfavorable.

If an objectively ineligible selected task is rejected, record the frozen rejection reason and take the next item in the same deterministic ordering. Rejections may enforce executability, safety, reproducibility, and answer-leakage constraints only; they may not use MAPS mechanism/family labels or expected arm behavior.

## Population targets

Build toward the approved Standard target of 48 primary cases. Before authoring, the curator must freeze the `FROZEN_STANDARD` / `SEALED_HOLDOUT` allocation and justify it for the later independent corpus/pre-freeze review.

Across the combined primary population, preserve the owner-defined constraints:

```text
complexity = 25% straightforward/bounded; 50% routine consequential/medium; 25% complex/longitudinal
domain = roughly balanced across the four declared domains
project_origin = >=50% external to MAPS_L conventions
terminal_class_BLOCK = <=25%
NONE = >=40%
STRESS = <=30%
COUNTERWEIGHT >= STRESS by count
```

Domain/complexity balancing may be applied as ordinary target-population strata. MAPS-related overlay/family labels must be assigned only after sampling and case construction, then independently audited before freeze.

## Sampling reference / parametric recall

Before drawing cases, set an exact sampling reference model/provider/version and the latest credible publicly documented training-data cutoff for that version. If none is credibly documented, record `UNKNOWN`; do not infer one.

Every external selected case later records its resolution date and sampling-reference cutoff relation per the approved case schema.

Changing the eventual execution model may change only the later sensitivity classification, never case inclusion, overlay class, or sampling weight.

## Outputs permitted in this repository

Before the confirmatory look, this repository may contain only non-secret sampling procedure, frozen source-pool definitions that do not reveal selected cases, hashes/counts, and independently approved aggregate corpus metadata.

Do **not** commit selected primary case IDs, task fixtures, hidden contracts, answer-bearing provenance, selected source URLs, holdout content, or decryption material here if doing so gives access to anyone who can modify MAPS_L or a successor protocol.
