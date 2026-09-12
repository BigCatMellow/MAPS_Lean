# Primary Corpus / Holdout Custody and Exposure Plan — candidate

Status: **CANDIDATE OWNER COMPLETE — CUSTODIAN UNASSIGNED; CASE CONSTRUCTION BLOCKED**

Normative exposure rules remain in `../BENCHMARK-SPEC.md`. This file records the concrete custody requirement for the first benchmark line.

## Required boundary

Primary case content is valid for confirmatory inference only while it is not accessible to anyone who can modify the tested MAPS_L protocol version or a successor.

That includes both:

- `FROZEN_STANDARD` case-specific task fixtures / outcome contracts / provenance sufficient to identify the case; and
- `SEALED_HOLDOUT` case content and all answer-bearing hidden material.

For this line it also includes the **selection secret, derived selection seed, ranking table, selected issue IDs/URLs, and holdout membership**, because revealing those values would make the supposedly unexposed public-source sample reconstructable.

Exposure is access-based, not intent-based. A promise not to look is insufficient.

## Current environment eligibility

The current benchmark-spec owner context and repository owner account are **not eligible custodians** for unexposed primary case content or selection secret material, because they can influence MAPS_L and can read material committed to this PR/repository.

A normal fresh chat under the same user account is sufficient for independent *review* but is **not sufficient custody** for selected primary/holdout case content if the user can access that chat.

This context therefore must not generate the curator secret, enumerate/rank eligible issue IDs, select cases, see holdout membership, or author hidden contracts.

## Acceptable curator/custodian class

The selecting curator and custodian may be the same independent party for construction. A different independent reviewer is still required for the later corpus/pre-freeze review.

Before selected content exists, the curator/custodian environment must satisfy all:

1. custodian does not hold a MAPS_L protocol-modifying role from source-pool acceptance/secret precommit through the designated confirmatory look;
2. storage ACLs exclude repository owner, benchmark-spec owner, MAPS_L protocol contributors, and successor-protocol editors during the seal period;
3. storage can preserve selection secret/seed, ranking ledger, selected case fixtures, hidden companion records, canaries, resolution identifiers, and source/provenance without placing them in MAPS_L git history or a run-reachable repository;
4. only permitted non-secret commitments, hashes, counts, role identities, public beacon evidence, exposure-owner identities, and aggregate metadata return here before the confirmatory look;
5. the custody system can later make the sealed bundle available to the independently approved runner/evaluator without exposing it to protocol modifiers first;
6. access events are auditable enough to determine whether a case must retire from confirmatory status;
7. the curator can generate and retain a cryptographically random 256-bit selection secret unavailable to protocol modifiers;
8. the curator can durably publish the secret commitment **before** the qualifying NIST beacon pulse without publishing the secret itself.

Examples of acceptable classes include an independently controlled private repository/object store, an independent sealed evaluation service, or an encrypted bundle whose decryption key and sampling secret remain exclusively with an eligible custodian until the permitted reveal. The specific service/account is not chosen here.

## Sampling-secret custody

`TARGET-WORK-SAMPLING-MANIFEST.md` owns the exact derivation algorithm. Custody consequences:

- `selection_secret` is generated only after the source-pool definition is independently accepted;
- only `SHA256(selection_secret)` is returned before the public beacon pulse;
- the secret commitment must be durably timestamped before the pulse selected by the frozen beacon rule;
- `selection_secret`, derived `selection_seed`, selection ranks, ranking ledger, selected issue IDs, and holdout membership remain sealed;
- public NIST pulse evidence and `SHA256(selection_seed)` may return here because they do not permit reconstruction without the secret;
- at the permitted reveal, secret/seed/ledger can be disclosed for independent no-reroll recomputation.

If secret or seed becomes accessible to a protocol modifier early, the current selection is contaminated even if case fixtures themselves were never opened. Re-freeze requires a new independently committed secret + later beacon pulse and deterministic reselection; do not silently reuse the exposed sample.

## Required non-secret pre-selection record

Before issue enumeration/ranking begins, record in this repository or equivalent immutable public evidence:

```text
custodian_identity_or_service = UNSET
curator_role = UNSET
prior_MAPS_L_exposure = UNSET
storage_class = UNSET
access_control_summary = UNSET
protocol_modifiers_excluded = UNSET
exposure_owners = UNSET
confirmatory_look_count = UNSET
retirement_rule_acknowledged = yes | UNSET
selected_content_committed_to_MAPS_L_repo = no
source_pool_definition_sha256 = 5101ed5b416f9c61b64d658a03864d77550489ba1a5eca1ba19f3f0352cc4fe6
selection_secret_commitment = UNSET
secret_commit_timestamp = UNSET
beacon_rule_acknowledged = yes | UNSET
```

After the qualifying public beacon pulse and seed derivation, but before selection results are exposed, additionally record only:

```text
nist_pulse_timestamp = UNSET
nist_pulse_index_or_identifier = UNSET
nist_pulse_output_value = UNSET
nist_pulse_certificate_identifier_if_available = UNSET
selection_seed_commitment = UNSET
```

Before sealing the holdout, additionally return only:

```text
corpus_hash = UNSET
holdout_bundle_hash = UNSET
FROZEN_STANDARD_count = UNSET
SEALED_HOLDOUT_count = UNSET
seal_timestamp = UNSET
```

Never record secret paths, keys, `selection_secret`, `selection_seed`, ranking values, selected IDs/URLs, holdout membership, hidden answers, case-identifying sealed metadata, or decryption material in this public/non-secret record.

## Exposure / retirement rule

If selected primary case content, selection secret/seed, ranking ledger, or selected identities become accessible to a MAPS_L protocol modifier before the permitted look, mark the affected selection/cases exposed. They may remain DEV/regression evidence but may not contribute pristine confirmatory evidence to a successor protocol.

A secret/seed exposure that makes the complete sample reconstructable contaminates the whole selected primary sample, not merely one case.

## Current blocker

Actual secret generation, issue enumeration/ranking, case selection, or authoring cannot start from this chat/repository context. An eligible independent curator/custodian with genuinely separate access-controlled storage is required.

Public package shaping, hashing, and curator instructions may continue; benchmark execution remains prohibited.
