# Target Work Sampling Manifest — candidate pre-authoring freeze

Status: **CANDIDATE OWNER COMPLETE — PUBLIC SELECTION MODEL (revision 3: pre-beacon candidate-ledger freeze); AWAITING FRESH INDEPENDENT REVIEW; NO CASE SELECTION PERMITTED UNTIL THEN**

Normative population rules remain in `../BENCHMARK-SPEC.md`. This file instantiates the sampling method and public source pools for independent approval. Under the public precommitment model, the MAPS_L owner **does** draw the sample directly, openly — there is no independent custodian for selection. Integrity comes from the beacon-anchored precommitment sequence below (grinding-resistant by construction) and public reproducibility (tamper-evident), not from denying the owner access to the result. See `../pre-corpus/INDEPENDENT-CURATOR-START-PROMPT.md` for the full procedure this section's formula feeds.

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

The operator must verify every named repository is still public/non-archived for the relevant historical window, exposes the required issue/PR metadata, and contains enough objectively eligible candidates. Any pool replacement must occur **before the eligible-candidate ledger is frozen**, be justified without MAPS-family/expected-winner information, change the definition hash, and receive the same pre-authoring review.

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

Holdout assignment occurs only after the 48 source identities have been selected and before case authoring. Within each domain, exactly one STRAIGHTFORWARD, one MEDIUM, and one COMPLEX selected identity is assigned to holdout by the independent secondary ranking below, yielding 12 holdouts total; the remaining 36 become Standard.

## Public deterministic selection

**Revision 3** preserves revision 2's public beacon-anchored model but closes
one timing defect: all judgment-bearing eligibility work is now frozen **before**
the qualifying beacon pulse exists.

The NIST beacon remains the sole source of selection unpredictability. There is
still no private selection secret and no selection custodian.

### Why the candidate set must freeze before the beacon

The ranking formula is only mechanically deterministic if the set being ranked
is already fixed. Several eligibility rules above require factual/qualitative
adjudication (for example, identifying the resolving PR, confirming a
history-free pre-fix base, or determining whether task-facing sources can be
separated from answer-bearing provenance).

If those judgments happen after the pulse, a selector can see which rows rank
well before deciding whether a row is "eligible." That creates a post-pulse
selection lever even when the rank formula itself is perfectly frozen.

Revision 3 removes that lever: candidate membership, domain, complexity, and the
evidence supporting every eligibility decision are committed before the pulse.

### Pre-beacon eligible-candidate ledger

Before choosing a qualifying beacon pulse, enumerate and adjudicate the complete
eligible population from the frozen 16 repositories under the rules above.

Create a public UTF-8 TSV at:

`work/evals/protocol-effectiveness-benchmark/selection/ELIGIBLE-CANDIDATE-LEDGER.tsv`

with LF line endings, this exact header, and rows sorted by
`lower(repository_full_name)`, then numeric `issue_number`:

```text
repository_full_name	issue_number	issue_url	domain	complexity	resolving_pr_number	issue_created_at	resolving_pr_merged_at	changed_files	changed_lines	pre_fix_base	eligibility_evidence_refs
```

Every row in this file is already adjudicated `ELIGIBLE`. The evidence refs
must be sufficient for a later auditor to reconstruct why the frozen filters
passed without consulting MAPS-family/expected-winner information.

Also preserve pre-freeze rejections in a public audit record if any were examined;
rejected rows are not part of the candidate-set hash and can never enter the
post-pulse ranking.

Canonical candidate-set hash:

```text
candidate_set_sha256 = SHA256(exact UTF-8 bytes of ELIGIBLE-CANDIDATE-LEDGER.tsv)
```

The complete candidate ledger and a small public
`selection/SELECTION-FREEZE.json` record must be committed in the same
pre-pulse commit. The freeze record contains at minimum:

```text
pre_authoring_package_hash
approved_design_head
source_pool_definition_sha256
candidate_set_sha256
candidate_count
candidate_ledger_git_blob_sha
candidate_ledger_freeze_timestamp
operator_identity
beacon_rule
selection_rank_formula_version = MAPS_PROTOCOL_EFFECTIVENESS_V0_PUBLIC_R3
holdout_rank_formula_version = MAPS_PROTOCOL_EFFECTIVENESS_V0_PUBLIC_HOLDOUT_R3
```

The freeze commit must exist before the qualifying pulse. A change to the
candidate ledger, candidate-set hash, source-pool definition, formulas, or freeze
timestamp after that commit invalidates the pending ceremony and requires a new
future pulse after a new independently reviewable freeze.

### Precommit fields

The public freeze record fixes:

```text
operator_identity = UNSET
source_pool_definition_sha256 = 5101ed5b416f9c61b64d658a03864d77550489ba1a5eca1ba19f3f0352cc4fe6
candidate_set_sha256 = UNSET
candidate_ledger_freeze_timestamp = UNSET
beacon_rule = first valid NIST Randomness Beacon 2.0 pulse with timestamp >= candidate_ledger_freeze_timestamp + 600 seconds
beacon_source = https://beacon.nist.gov/beacon/2.0/
```

The candidate ledger, freeze record, and exact formulas below are public and
committed before the qualifying pulse exists. At that point the eventual ranking
is unknowable but candidate membership is no longer editable without leaving a
new visible freeze commit.

If the first qualifying pulse is unavailable, use the first later valid pulse.
Do not choose among already-published pulses after testing outcomes.

### Candidate ranking

After the qualifying pulse publishes, perform **no new eligibility
enumeration/adjudication**. Rank only rows in the frozen candidate ledger.

For each frozen eligible row:

```text
selection_rank = SHA256(
  "MAPS_PROTOCOL_EFFECTIVENESS_V0_PUBLIC_R3\n" +
  approved_design_head + "\n" +
  source_pool_definition_sha256 + "\n" +
  candidate_set_sha256 + "\n" +
  nist_pulse_timestamp + "\n" +
  nist_pulse_output_value + "\n" +
  lower(repository_full_name) + "#" + decimal(issue_number) + "\n"
)
```

Sort ascending by `selection_rank` within each domain/complexity stratum and
take the first rows needed to fill the 3/6/3 per-domain quota while enforcing
`max_cases_per_repository = 4`. A row skipped solely because the repository cap
is already full is recorded as `REPO_CAP`; that is arithmetic, not an
eligibility rejection.

### Narrow post-freeze invalidation

Post-pulse invalidation is exceptional and cannot become a second eligibility
pass.

A frozen row may be removed only when new evidence demonstrates an objective
contradiction to a frozen eligibility fact or a genuinely new source-availability
failure. The invalidation must:

1. cite the exact frozen filter/fact that failed;
2. publish the evidence and discovery time;
3. state why the defect was not reasonably available before freeze;
4. be independently confirmed before the next-ranked replacement is admitted;
5. never use MAPS mechanism/family labels, overlay needs, expected winner, or
   observed rank as a reason.

If independent confirmation is unavailable, stop with
`SELECTION BLOCKED — POST-FREEZE DEFECT REVIEW REQUIRED`; do not skip the row.

Qualitative re-interpretation merely because a highly ranked row is inconvenient
is prohibited.

### Holdout assignment

After the 48 identities are fixed, derive for each selected row:

```text
holdout_rank = SHA256(
  "MAPS_PROTOCOL_EFFECTIVENESS_V0_PUBLIC_HOLDOUT_R3\n" +
  approved_design_head + "\n" +
  candidate_set_sha256 + "\n" +
  nist_pulse_timestamp + "\n" +
  nist_pulse_output_value + "\n" +
  lower(repository_full_name) + "#" + decimal(issue_number) + "\n"
)
```

Within each domain/complexity cell, the smallest `holdout_rank` becomes
`SEALED_HOLDOUT`. All others are `FROZEN_STANDARD`.

Issue IDs, ranks, the complete ranking table, selected URLs, candidate-set hash,
and holdout membership are public. Gate 4/5 case-construction material (fixtures,
hidden contracts/oracles, canaries, answer-bearing provenance) remains sealed
under `BENCHMARK-SPEC.md` §9.1–9.3.

An independent auditor can reproduce the result from the frozen ledger, its hash,
the freeze commit, the formulas above, and the public NIST pulse.

## Terminal and overlay constraints

Terminal class and `NONE | STRESS | COUNTERWEIGHT` are **not** inputs to source selection. They are assigned only during protocol-neutral case construction under `CASE-DESIGN.md`, then independently audited.

The final corpus must still meet the approved limits (`BLOCK <=25%`, `NONE >=40%`, `STRESS <=30%`, `COUNTERWEIGHT >= STRESS`). If a sampled source cannot support a valid case without violating the task-facing source or answer-leakage rules, it may be rejected only under a documented objective eligibility reason and replaced by the next deterministic source row. Never reject merely to improve an overlay/family mix or expected arm result.

## Selection freeze rule

Before a qualifying pulse may exist:

- the source-pool definition and revision-3 selection mechanism must have fresh
  independent pre-authoring acceptance;
- the complete eligible-candidate ledger must be committed and hashed;
- the public `SELECTION-FREEZE.json` record must bind that
  `candidate_set_sha256`, the package hash, source-pool hash, formulas, operator,
  and immutable `candidate_ledger_freeze_timestamp`;
- the qualifying-pulse rule must point to a pulse at least 600 seconds after that
  freeze timestamp.

After the pulse, no candidate may be added and no ordinary eligibility
adjudication may be repeated. Only the narrow independently-confirmed
post-freeze invalidation path above may remove a frozen row.

Case-construction custody (Gate 4/5, holdout builder role) remains governed by
`CUSTODY-AND-EXPOSURE-PLAN.md` and is a separate unresolved boundary.

## Repository-safe outputs

Selection outputs are now fully public — see "Public deterministic
selection" above. This repository may contain the complete selection
result (identities, ranks, holdout membership) once Gate 2/3 complete.

What still may **not** be committed here, because it belongs to Gate 4/5's
separate case-construction seal (`BENCHMARK-SPEC.md` §9.1–9.3), unaffected
by this change: task fixtures, hidden contracts, answer-bearing
provenance, hidden canaries, or any material from which hidden
case-construction content is reconstructable, if doing so gives access to
anyone who can modify MAPS_L or a successor before the Gate 5 permitted
reveal.
