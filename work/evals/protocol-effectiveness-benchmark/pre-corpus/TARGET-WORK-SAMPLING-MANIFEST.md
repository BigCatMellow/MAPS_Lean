# Target Work Sampling Manifest — candidate pre-authoring freeze

Status: **CANDIDATE OWNER COMPLETE — PUBLIC SELECTION MODEL (revision 2, `work/notes/2026-09-15-pr341-custody-descope-design.md`); AWAITING FRESH INDEPENDENT REVIEW OF THIS MECHANISM CHANGE; NO CASE SELECTION PERMITTED UNTIL THEN**

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

The operator must verify every named repository is still public/non-archived for the relevant historical window, exposes the required issue/PR metadata, and contains enough objectively eligible candidates. Any pool replacement must occur **before any issue IDs are drawn**, be justified without MAPS-family/expected-winner information, change the definition hash, and receive the same pre-authoring review.

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

**Revision 2** (`work/notes/2026-09-15-pr341-custody-descope-design.md`,
reviewed by `rumi`). Replaces the prior secret-seed construction. Keeps
the NIST beacon as the sole source of unpredictability; drops the secret
entirely, since no independent custodian exists to protect one from the
operator who is also the one selecting.

### Why the beacon still matters with no secret

Every input to a selection formula except the beacon pulse is already
public and frozen before selection begins (`approved_design_head`,
`source_pool_definition_sha256`, and the candidate issue identities
themselves, which are pre-existing GitHub-assigned facts). If the formula
depended on *only* those inputs, anyone — including the operator —
could privately test many textually-different, equally-defensible formula
variants against the already-known pool and pre-register whichever
produces the most favorable 48-case list, with no detectable trace. This
was a real gap in revision 1 of this section, caught by independent
review; see the design note §3 for the full account, quoting the finding
directly.

The beacon pulse closes that gap: its `nist_pulse_output_value` does not
exist at the moment the formula must be committed, so no formula variant
can be tested against the real future value before committing to one. The
beacon is not there to hide anything from the operator (nothing is
hidden); it is there so that *at commit time*, the eventual result is
genuinely unknowable to whoever is committing.

### Precommit fields

Before any issue IDs are enumerated/ranked, the operator sets:

```text
operator_identity = UNSET
source_pool_freeze_timestamp = UNSET
source_pool_definition_sha256 = 5101ed5b416f9c61b64d658a03864d77550489ba1a5eca1ba19f3f0352cc4fe6
beacon_rule = first valid NIST Randomness Beacon 2.0 pulse with timestamp >= source_pool_freeze_timestamp + 600 seconds
beacon_source = https://beacon.nist.gov/beacon/2.0/
```

`source_pool_freeze_timestamp` is committed to git, publicly, **before**
the qualifying pulse exists, alongside the exact formulas below (verbatim,
as checked-in text — this section, unmodified from what was committed, is
itself the commitment). **Once committed, `source_pool_freeze_timestamp`
is final.** Changing it later is not a private do-over — the same rule
that already governs a pool-*content* change (new hash, new review)
applies to a freeze-*timestamp* change, because re-declaring the timestamp
alone, with byte-identical pool content, is enough to select a different
qualifying pulse and therefore a completely different 48-case draw. See
`INDEPENDENT-CURATOR-START-PROMPT.md` Gate 2's "Do not reroll" section for
why this is disclosed as a residual risk rather than claimed as fully
prevented: the immutability rule makes a reroll attempt *visible* in git
history, not impossible to attempt.

If the first qualifying pulse is unavailable, use the first later valid
pulse; the operator may not choose among available pulses after seeing
resulting samples — this is unenforceable by mechanism once the pulse
exists (nothing stops re-checking a later pulse against an already-known
formula), so it is enforced by the same before-the-pulse commitment
discipline as the formula itself: the pulse-selection rule above is
committed before any qualifying pulse exists, exactly like the formula.

### Candidate ranking

For each objectively eligible issue row, once the qualifying pulse
publishes:

```text
selection_rank = SHA256(
  "MAPS_PROTOCOL_EFFECTIVENESS_V0_PUBLIC\n" +
  approved_design_head + "\n" +
  source_pool_definition_sha256 + "\n" +
  nist_pulse_timestamp + "\n" +
  nist_pulse_output_value + "\n" +
  lower(repository_full_name) + "#" + decimal(issue_number) + "\n"
)
```

Sort ascending by `selection_rank` within each domain/complexity stratum and take the first rows needed to fill the 3/6/3 per-domain quota, enforcing `max_cases_per_repository = 4`. A row skipped solely because the repository cap is already full is recorded as `REPO_CAP`, not as an eligibility rejection.

If a drawn row proves objectively ineligible, preserve the rejection reason and take the next row in deterministic order. Do not reroll because the task appears favorable/unfavorable to any arm.

### Holdout assignment

After the 48 identities are fixed, derive for each selected row:

```text
holdout_rank = SHA256(
  "MAPS_PROTOCOL_EFFECTIVENESS_V0_PUBLIC_HOLDOUT\n" +
  approved_design_head + "\n" +
  nist_pulse_timestamp + "\n" +
  nist_pulse_output_value + "\n" +
  lower(repository_full_name) + "#" + decimal(issue_number) + "\n"
)
```

Within each domain/complexity cell, the smallest `holdout_rank` becomes `SEALED_HOLDOUT`. All others are `FROZEN_STANDARD`.

**Issue IDs, ranks, ranking tables, selected URLs, and holdout membership
are published, not sealed** — there is no custodian to seal them from, and
pretending otherwise would add cosmetic-only restriction with no technical
backing. What "sealed" still correctly describes, unaffected by this
change: the *case-construction content* for those identities (hidden
contracts, oracle answers, canaries — `BENCHMARK-SPEC.md` §9.1–9.3, Gate
4/5). Knowing *which* 48 issues and *which* 12 are nominally holdout does
not reveal their hidden answers; see the design note's §6 for the
precise boundary this draws.

At any point, an independent auditor can recompute the commitments,
rankings, and holdout assignment directly from this section's formulas
plus the publicly recorded `source_pool_freeze_timestamp` and NIST pulse
evidence — no disclosure step is needed because nothing was withheld.

## Terminal and overlay constraints

Terminal class and `NONE | STRESS | COUNTERWEIGHT` are **not** inputs to source selection. They are assigned only during protocol-neutral case construction under `CASE-DESIGN.md`, then independently audited.

The final corpus must still meet the approved limits (`BLOCK <=25%`, `NONE >=40%`, `STRESS <=30%`, `COUNTERWEIGHT >= STRESS`). If a sampled source cannot support a valid case without violating the task-facing source or answer-leakage rules, it may be rejected only under a documented objective eligibility reason and replaced by the next deterministic source row. Never reject merely to improve an overlay/family mix or expected arm result.

## Selection freeze rule

The MAPS_L owner performs selection directly under this model — see
"Why the beacon still matters with no secret" above for what still makes
that safe. Before the formula/freeze-timestamp commitment is created:

- the source-pool definition must already be independently accepted
  (unchanged — this predates and is unaffected by the custody descope);
- any revision to the pool changes `source_pool_definition_sha256` and
  therefore the committed selection procedure, exactly as before;
- **this mechanism itself (this section, revision 2) requires a fresh
  independent pre-authoring freeze review before selection may proceed** —
  it is a different cryptographic construction from what any prior review
  approved, not a superficial edit (design note §8). `owner_recompute_status`
  in `PRE-AUTHORING-PACKAGE-MANIFEST.json` reflects a mechanical
  self-recompute by the editing party, not an independent confirmation;
  treat it as unreviewed until a fresh independent pass records otherwise.

Case-construction custody (Gate 4/5, holdout builder role) remains
governed by `CUSTODY-AND-EXPOSURE-PLAN.md`'s construction-scoped sections,
unaffected by this change and still open per the design note's §5.

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
