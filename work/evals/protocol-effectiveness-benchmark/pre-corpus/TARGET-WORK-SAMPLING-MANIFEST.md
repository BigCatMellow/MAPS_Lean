# Target Work Sampling Manifest — candidate pre-authoring freeze

Status: **CANDIDATE OWNER COMPLETE — INDEPENDENT CURATOR/CUSTODIAN UNASSIGNED; NO CASE SELECTION PERMITTED**

Normative population rules remain in `../BENCHMARK-SPEC.md`. This file instantiates the sampling method and public source pools for independent approval. The MAPS_L owner does **not** draw the sample.

## Immutable benchmark cutoff

```text
benchmark_package_first_commit = bb030461433d264688699a277ee901ed70ae9ca7
benchmark_package_first_commit_date = 2026-09-10T15:50:07Z
approved_design_head = 369bccaf68b258c70eb6efec0c9f70115c8014cb
```

Operator-authored source requests are eligible only if they predate the package-first commit above or were authored by a non-stakeholder unable to influence MAPS_L. This first primary line instead uses external public issue queues only.

## Sampling reference model / cutoff

Candidate reference, fixed before selection:

```text
sampling_reference_provider = OpenAI
sampling_reference_model_provider_version = gpt-5.6-sol
sampling_reference_training_cutoff = 2026-02-16
sampling_reference_cutoff_status = PUBLICLY_DOCUMENTED
sampling_reference_source = https://developers.openai.com/api/docs/models/gpt-5.6-sol
sampling_reference_source_checked = 2026-09-11
```

The public model documentation states a February 16, 2026 knowledge cutoff. Source-task creation is therefore constrained to after that cutoff, while resolution must predate the benchmark package's first commit. The eventual execution model may differ; that changes only the later sensitivity relation, not inclusion or sampling weight.

No API/model execution or spending is authorized by naming this reference model.

## Concrete source-pool definition

Machine-readable definition:

`SOURCE-POOL-DEFINITION.json`

```text
source_pool_definition_sha256 = 5101ed5b416f9c61b64d658a03864d77550489ba1a5eca1ba19f3f0352cc4fe6
hash_rule = SHA256(UTF-8 canonical JSON of the definition object with recursively sorted keys, compact separators, and one trailing LF)
```

The candidate pools are 100% external to MAPS_L conventions:

| domain | repositories |
| --- | --- |
| software/code | `astral-sh/ruff`, `encode/httpx`, `pallets/flask`, `pytest-dev/pytest` |
| automation/data | `apache/airflow`, `dbt-labs/dbt-core`, `pandas-dev/pandas`, `PrefectHQ/prefect` |
| research/document/evidence | `jupyter-book/jupyter-book`, `matplotlib/matplotlib`, `mkdocs/mkdocs`, `readthedocs/readthedocs.org` |
| configuration/operations | `ansible/ansible`, `docker/compose`, `helm/helm`, `kubernetes-sigs/kustomize` |

Candidate task window:

```text
issue_created_after = 2026-02-16T23:59:59Z
resolving_PR_merged_before = 2026-09-10T15:50:07Z
```

Independent curator must verify every named repository is still public/non-archived for the relevant historical window, exposes the required issue/PR metadata, and contains enough objectively eligible candidates. Any pool replacement must occur **before any issue IDs are drawn**, be justified without MAPS-family/expected-winner information, change the definition hash, and receive the same pre-authoring review.

## Objective eligibility filters

A candidate is eligible only when all are true:

1. public issue contains a task-facing problem/request independent of the resolving PR;
2. exactly one same-repository merged PR is the resolving implementation for sampling purposes;
3. resolving PR merged after issue creation and before the package-first commit;
4. a pre-fix base can be reconstructed and exported history-free without any resolving commit/object;
5. task can be executed and verified offline after frozen dependency/image preparation;
6. no private credentials, destructive real-world effects, unsafe/illegal action, or unavailable proprietary dependency are required;
7. resolving patch touches at most 12 files and 800 changed lines after excluding lock/vendor/generated-file churn;
8. task is not primarily benchmark/test-harness work for this benchmark;
9. task-facing sources can be separated from resolving PR, final patch, resolution comments, and answer-bearing provenance.

Eligibility may not use MAPS mechanism/family labels, expected winner, authority/recovery/review/continuation phenomena, or overlay class.

## Complexity strata

Complexity is assigned mechanically from the hidden resolving patch **only for sampling strata**, never shown to the agent:

```text
STRAIGHTFORWARD = <=2 files AND <=80 changed lines
MEDIUM = not STRAIGHTFORWARD AND <=6 files AND <=300 changed lines
COMPLEX = not STRAIGHTFORWARD/MEDIUM AND <=12 files AND <=800 changed lines
```

Lock/vendor/generated-file churn is excluded by the same frozen rule for every source.

## Primary quotas

Exact combined primary target:

```text
primary_total = 48
per_domain = 12
per_domain_complexity = 3 STRAIGHTFORWARD / 6 MEDIUM / 3 COMPLEX
FROZEN_STANDARD = 36
SEALED_HOLDOUT = 12
max_cases_per_repository = 4
project_origin_external = 100%
```

The combined 48 therefore preserves the approved 25% / 50% / 25% complexity target and balanced four-domain population without using MAPS-derived family weights.

Holdout assignment occurs only after the 48 source identities have been selected and before case authoring. Within each domain, exactly one STRAIGHTFORWARD, one MEDIUM, and one COMPLEX selected identity is assigned to holdout by the independent secondary hash below, yielding 12 holdouts total; the remaining 36 become Standard.

## Deterministic selection

Independent curator fields that must be set before drawing IDs:

```text
curator_identity = UNSET
curator_role = UNSET
prior_MAPS_L_development_role = UNSET
source_pool_freeze_timestamp = UNSET
source_pool_definition_sha256 = 5101ed5b416f9c61b64d658a03864d77550489ba1a5eca1ba19f3f0352cc4fe6
selection_seed = UNSET UNTIL CURATOR ACCEPTS EXACT POOL DEFINITION
```

After independent acceptance of the exact definition, derive:

```text
selection_seed = SHA256(
  "MAPS_PROTOCOL_EFFECTIVENESS_V0\n" +
  approved_design_head + "\n" +
  source_pool_definition_sha256 + "\n"
)
```

For each objectively eligible issue row derive:

```text
selection_rank = SHA256(
  selection_seed + "\n" +
  lower(repository_full_name) + "#" + decimal(issue_number) + "\n"
)
```

Sort ascending by `selection_rank` within each domain/complexity stratum and take the first rows needed to fill the 3/6/3 per-domain quota, enforcing `max_cases_per_repository = 4`. A row skipped solely because the repository cap is already full is recorded as `REPO_CAP`, not as an eligibility rejection.

If a drawn row proves objectively ineligible, preserve the rejection reason and take the next row in deterministic order. Do not reroll because the task appears favorable/unfavorable to any arm.

After the 48 identities are fixed, derive:

```text
holdout_rank = SHA256(selection_seed + "\nHOLDOUT\n" + lower(repository_full_name) + "#" + decimal(issue_number) + "\n")
```

Within each domain/complexity cell, the smallest `holdout_rank` becomes SEALED_HOLDOUT. All others are FROZEN_STANDARD.

Actual issue IDs/ranks/selected URLs remain exclusively with the independent curator/custodian before the permitted look and are never committed here.

## Terminal and overlay constraints

Terminal class and `NONE | STRESS | COUNTERWEIGHT` are **not** inputs to source selection. They are assigned only during protocol-neutral case construction under `CASE-DESIGN.md`, then independently audited.

The final corpus must still meet the approved limits (`BLOCK <=25%`, `NONE >=40%`, `STRESS <=30%`, `COUNTERWEIGHT >= STRESS`). If a sampled source cannot support a valid case without violating the task-facing source or answer-leakage rules, it may be rejected only under a documented objective eligibility reason and replaced by the next deterministic source row. Never reject merely to improve an overlay/family mix or expected arm result.

## Custody / freeze rule

The MAPS_L owner can propose the public source-pool definition but cannot be the selecting curator or custodian. Before `selection_seed` is used:

- an eligible independent curator/custodian and access-controlled storage must be assigned per `CUSTODY-AND-EXPOSURE-PLAN.md`;
- that curator independently accepts or revises the source-pool definition without examining selected IDs first;
- any revision changes `source_pool_definition_sha256` and therefore the seed;
- a fresh independent pre-authoring freeze review approves the complete instantiated treatment/control/sampling/custody package.

## Repository-safe outputs

Before the confirmatory look, this repository may contain only public procedure/source-pool definitions, hashes/counts, role identities, exposure-owner identities, and independently approved aggregate metadata.

Do **not** commit selected primary case IDs, task fixtures, hidden contracts, answer-bearing provenance, selected source URLs, holdout content, ranking tables, or decryption material here if doing so gives access to anyone who can modify MAPS_L or a successor.
