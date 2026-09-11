# Primary Corpus / Holdout Custody and Exposure Plan — candidate

Status: **CANDIDATE — CUSTODIAN UNASSIGNED; CASE CONSTRUCTION BLOCKED**

Normative exposure rules remain in `../BENCHMARK-SPEC.md`. This file records the concrete custody requirement for the first benchmark line.

## Required boundary

Primary case content is valid for confirmatory inference only while it is not accessible to anyone who can modify the tested MAPS_L protocol version or a successor.

That includes both:

- `FROZEN_STANDARD` case-specific task fixtures / outcome contracts / provenance sufficient to identify the case; and
- `SEALED_HOLDOUT` case content and all answer-bearing hidden material.

Exposure is access-based, not intent-based. A promise not to look is insufficient.

## Current environment eligibility

The current benchmark-spec owner context and the repository owner account are **not eligible custodians for unexposed primary case content**, because they can influence MAPS_L and can read material committed to this PR/repository.

A normal fresh chat under the same user account is therefore sufficient for independent *review* but is **not sufficient custody for selected primary/holdout case content** if the user can access that chat.

## Acceptable custody class

Before selected case content exists, assign a custodian/environment satisfying all:

1. the custodian does not hold a MAPS_L protocol-modifying role from first case selection through the designated confirmatory look;
2. storage ACLs exclude the repository owner, benchmark-spec owner, MAPS_L protocol contributors, and successor-protocol editors during the seal period;
3. the custodian can preserve selected case fixtures, hidden companion records, canaries, resolution identifiers, and source/provenance without placing them in MAPS_L git history or another run-reachable repository;
4. only non-secret hashes, counts, role identities, exposure-owner identities, and aggregate metadata return to this repository before the confirmatory look;
5. the custody system can later make the sealed bundle available to the independently approved runner/evaluator without exposing it to protocol modifiers first;
6. every access event is auditable enough to determine whether a case must retire from confirmatory status.

Examples of acceptable classes include an independently controlled private repository/object store, an independent sealed evaluation service, or an encrypted bundle whose decryption key remains exclusively with an eligible custodian until the confirmatory look. The specific service/account is not chosen here.

## Required non-secret freeze record

Before case authoring begins, record in this repository:

```text
custodian_identity_or_service = UNSET
custodian_role = UNSET
prior_MAPS_L_exposure = UNSET
storage_class = UNSET
access_control_summary = UNSET
protocol_modifiers_excluded = UNSET
exposure_owners = UNSET
confirmatory_look_count = UNSET
retirement_rule_acknowledged = yes | UNSET
selected_content_committed_to_MAPS_L_repo = no
```

Before sealing the holdout, additionally record:

```text
holdout_bundle_hash = UNSET
holdout_case_count = UNSET
seal_timestamp = UNSET
```

Never record secret paths, keys, hidden answers, case-identifying sealed metadata, or decryption material in this public/non-secret record.

## Failure rule

If selected primary case content becomes accessible to a MAPS_L protocol modifier before its permitted look, mark the affected case exposed. It may remain DEV/regression evidence but may not contribute pristine confirmatory evidence to a successor protocol.

## Current blocker

Actual case selection/authoring cannot start from this chat/repository context until an eligible independent curator/custodian with an access-controlled storage channel is assigned. Public pre-authoring manifests and review prompts may continue.
