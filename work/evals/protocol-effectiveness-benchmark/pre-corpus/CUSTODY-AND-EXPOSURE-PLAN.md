# Primary Corpus / Holdout Custody and Exposure Plan — candidate

Status: **CANDIDATE OWNER COMPLETE — SELECTION CUSTODY DESCOPED (public
beacon-anchored model, `work/notes/2026-09-15-pr341-custody-descope-design.md`);
CASE-CONSTRUCTION CUSTODIAN STILL UNASSIGNED, CONSTRUCTION BLOCKED PENDING
THE DESIGN NOTE'S §5 DECISION**

Normative exposure rules remain in `../BENCHMARK-SPEC.md`. This file
records the concrete custody requirement for the first benchmark line.
**Selection custody (who draws the sample) is retired by this revision —
see `INDEPENDENT-CURATOR-START-PROMPT.md` Gates 0–3 and
`TARGET-WORK-SAMPLING-MANIFEST.md`'s "Public deterministic selection".
Case-construction custody (who builds the fixtures, especially for
`SEALED_HOLDOUT`) is unaffected and remains everything below, unresolved.**

## Required boundary

Primary case content is valid for confirmatory inference only while it is not accessible to anyone who can modify the tested MAPS_L protocol version or a successor.

That includes both:

- `FROZEN_STANDARD` case-specific task fixtures / outcome contracts / provenance sufficient to identify the case; and
- `SEALED_HOLDOUT` case content and all answer-bearing hidden material.

**Retired by revision 2:** this boundary no longer includes the selection
secret, derived selection seed, ranking table, selected issue IDs/URLs, or
holdout membership — there is no secret, and those values are published
directly (`INDEPENDENT-CURATOR-START-PROMPT.md` Gate 3). Knowing which 48
issues (and which 12 are holdout) does not, by itself, reveal any
case-specific outcome, hidden contract, oracle, or trajectory — those stay
governed by the two bullets above, unaffected.

Exposure is access-based, not intent-based. A promise not to look is insufficient.

## Current environment eligibility

**For selection: retired.** The current benchmark-spec owner context and
repository owner account now perform selection directly and openly — see
`INDEPENDENT-CURATOR-START-PROMPT.md` Gates 0–3. There is no selection
secret and no selection custodian; this section's restriction no longer
applies to drawing the sample.

**For case-construction content: unchanged, still in force.** The current
benchmark-spec owner context and repository owner account remain **not
eligible custodians** for unexposed primary case content (fixtures, hidden
contracts, oracle answers, canaries — `BENCHMARK-SPEC.md` §9.1–9.3),
because they can influence MAPS_L and can read material committed to this
PR/repository. A normal fresh chat under the same user account is
sufficient for independent *review* but is **not sufficient custody** for
selected primary/holdout case *content* if the user can access that chat.

This context therefore must not author hidden contracts, see the
case-specific answers/oracles for `SEALED_HOLDOUT` cases before the
confirmatory look, or otherwise access case-construction sealed material.
**Whether the operator can also build these fixtures themselves — the same
solo-owner question the selection descope answered for selection — is a
distinct, still-open question, named explicitly in
`work/notes/2026-09-15-pr341-custody-descope-design.md` §5. This file does
not resolve it and continues to state the unresolved requirement above
until it is.**

## Acceptable construction/holdout-builder custodian class

**Selection custody is retired — this section now covers case
construction only** (building fixtures for the 48 selected identities,
especially the 12 `SEALED_HOLDOUT` cases). A different independent
reviewer is still required for the later corpus/pre-freeze review (Gate 5).

Before selected case *content* exists, the construction custodian
environment must satisfy all:

1. builder does not hold a MAPS_L protocol-modifying role from the start
   of holdout construction through the designated confirmatory look
   (`BENCHMARK-SPEC.md` §9.4);
2. storage ACLs exclude repository owner, benchmark-spec owner, MAPS_L
   protocol contributors, and successor-protocol editors during the seal
   period;
3. storage can preserve selected case fixtures, hidden companion records,
   canaries, resolution identifiers, and source/provenance without placing
   them in MAPS_L git history or a run-reachable repository;
4. only permitted non-secret hashes, counts, role identities, and
   aggregate metadata return here before the confirmatory look;
5. the custody system can later make the sealed bundle available to the
   independently approved runner/evaluator without exposing it to protocol
   modifiers first;
6. access events are auditable enough to determine whether a case must
   retire from confirmatory status.

Examples of acceptable classes include an independently controlled private
repository/object store, an independent sealed evaluation service, or an
encrypted bundle whose decryption key remains exclusively with an eligible
custodian until the permitted reveal. The specific service/account is not
chosen here. **Whether the solo operator satisfies condition 1 for holdout
construction — the same way they now openly satisfy the (retired)
selection eligibility requirement — is exactly the open question in the
design note's §5, not decided by listing these conditions.**

## Selection secrecy — retired

`TARGET-WORK-SAMPLING-MANIFEST.md`'s "Public deterministic selection"
(revision 2) replaces the prior secret/HMAC-seed construction described
here. There is no `selection_secret`, no derived `selection_seed`, and
nothing about selection is sealed — see that file for the current
mechanism (public, beacon-anchored, grinding-resistant by construction)
and `INDEPENDENT-CURATOR-START-PROMPT.md` Gate 2 for the "do not reroll"
disclosure covering the residual risk a secret cannot address either way.

## Required non-secret pre-selection record — retired for selection

**Superseded by revision 2.** Selection bookkeeping (operator identity,
source-pool hash, beacon-rule acknowledgement, pulse evidence) now lives in
`TARGET-WORK-SAMPLING-MANIFEST.md`'s "Precommit fields" and is published
in full, not held as a non-secret subset of a sealed record — there is no
sealed record for selection any more. The fields formerly listed here for
the pre-pulse and post-pulse pre-selection stages (`curator_role`,
`selection_secret_commitment`, `secret_commit_timestamp`,
`selection_seed_commitment`, and the rest) no longer apply; do not record
them here or anywhere as if they still meant something.

## Required case-construction/holdout-seal record

**Unaffected by this revision — still applies, still open pending the
design note's §5.** Before sealing the holdout (Gate 4, case construction),
record only:

```text
corpus_hash = UNSET
holdout_bundle_hash = UNSET
FROZEN_STANDARD_count = UNSET
SEALED_HOLDOUT_count = UNSET
seal_timestamp = UNSET
```

Never record hidden answers, case-identifying sealed metadata, or decryption material in this public/non-secret record. (Selected IDs/URLs, ranking values, and holdout membership are no longer secret under revision 2 — see "Required non-secret pre-selection record — retired for selection" above; recording them is expected, not a leak.)

## Exposure / retirement rule

**Selection identities/ranking/holdout membership:** no longer a contamination concern — they are published by design (revision 2), not accidentally exposed.

**Case-construction content (unaffected):** if a case's hidden contract, oracle, trajectory, or other case-specific answer-bearing material becomes accessible to a MAPS_L protocol modifier before the permitted look, mark that case exposed. It may remain DEV/regression evidence but may not contribute pristine confirmatory evidence to a successor protocol. This is unrelated to whether the case's *identity* (which issue it is) is known — that alone was never what made a case exposed under §8's definition, and is even less so now that identities are public from the start.

## Current blocker

**Selection: none.** Issue enumeration/ranking/selection can proceed directly under `INDEPENDENT-CURATOR-START-PROMPT.md` Gates 0–3, once a fresh independent review of revision 2's mechanism lands (design note §8) — not blocked on finding a custodian.

**Case construction/authoring: still blocked**, pending the design note's
§5 decision on whether the solo operator satisfies `BENCHMARK-SPEC.md`
§9.4's holdout-builder role requirement, or whether an eligible
independent construction custodian is still required for that step.

Public package shaping, hashing, and selection may continue once
independently reviewed; benchmark execution remains prohibited regardless.
