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
6. `pre-corpus/PRE-AUTHORING-PACKAGE-MANIFEST.json`;
7. every file pinned by that package manifest;
8. `pre-corpus/INDEPENDENT-CURATOR-START-PROMPT.md`;
9. r9 approval `work/reviews/pr-341-rereview-evidence-369bcca.md`.

The five normative owner documents are frozen design owners. Do not rewrite them while building the corpus.

## Preconditions before issue enumeration

All must be true before enumerating/ranking candidate issue IDs:

- package hash recomputes to `c0927f437e7a4d07d1a825eace7e3d061ad0bb9c6a8b8775c28b2e4bfd07e963`;
- treatment bundle hash recomputes to `7a944e3db3575c1f94df5872d8b15a644ecd7eb254893b10d9d1ebcd83aa3341`;
- exact neutral bootstrap, B launcher, and Arm-C text/hash are pinned;
- Arm C receives independent competence/non-strawman approval;
- static A/B/C instruction/context disclosure and dynamic context-cost accounting are accepted;
- source-pool definition hash recomputes to `5101ed5b416f9c61b64d658a03864d77550489ba1a5eca1ba19f3f0352cc4fe6`;
- reference model/cutoff and source pools receive independent acceptance before selection;
- curator/custodian identity and eligibility are recorded;
- genuinely separate access-controlled storage excludes MAPS_L protocol modifiers;
- curator privately generates a 256-bit selection secret and publicly commits only its SHA-256 **before** the frozen future NIST-beacon pulse;
- selected IDs/content, secret/seed, ranking ledger, and holdout membership cannot enter this repository or a user-visible MAPS_L-owner chat before the permitted look.

If any precondition is missing, stop before enumeration and return only the exact missing item(s).

## Boundary

### MAY

- independently accept/reject the public pre-authoring package before selection;
- generate/retain the private selection secret and derive the seed exactly under the frozen commit/beacon rule;
- enumerate objectively eligible public-source candidates inside sealed custody;
- deterministically rank/select 48 primary identities and assign 36 Standard / 12 Holdout under the frozen quotas;
- construct benchmark-visible and hidden case records in sealed storage;
- create canaries when hidden material is first created;
- reject objectively ineligible selected tasks using only frozen eligibility rules and deterministic replacement order;
- after sampling, construct terminal truth, hidden checks, stress-family records, counterweight fields, and task fixtures according to CASE-DESIGN;
- build the sealed-holdout bundle and freeze hashes/look-count/exposure-owner records;
- return only commitments, hashes, counts, aggregate strata, rejection totals, and non-secret custody evidence.

### MUST NOT

- modify MAPS_L runtime/protocol behavior or the five normative benchmark owners;
- privately substitute a different Arm C or source-pool definition and continue without re-review;
- select/reject tasks because they look favorable/unfavorable to MAPS_L;
- assign MAPS-related stress/counterweight/family labels before source selection;
- expose selection secret/seed, ranks, selected IDs/URLs, holdout membership, fixtures, hidden records, answer-bearing provenance, canaries, or resolution identifiers to MAPS_L protocol modifiers;
- put selected primary/holdout content in MAPS_L git history;
- run A/B/C agents, Smoke, Standard, evaluators, graders, or benchmark APIs;
- spend money;
- merge PR #341.

## Frozen selection rules

Use `pre-corpus/TARGET-WORK-SAMPLING-MANIFEST.md` exactly.

Key invariants:

- public pools: 16 external GitHub repositories across four declared domains;
- source-pool hash: `5101ed5b416f9c61b64d658a03864d77550489ba1a5eca1ba19f3f0352cc4fe6`;
- sampling reference: OpenAI `gpt-5.6-sol`, documented cutoff `2026-02-16`;
- issue creation after that cutoff; resolving PR merged before package first commit `2026-09-10T15:50:07Z`;
- 48 total: 12/domain; within each domain 3 straightforward / 6 medium / 3 complex;
- max 4 selected cases per repository;
- private selection seed derived only after secret precommit + qualifying future NIST pulse;
- selection and holdout rankings use HMAC-SHA256 keyed by the private derived seed;
- secret/seed/ranks remain sealed until permitted reveal;
- exactly one holdout per domain/complexity cell => 12 Holdout, 36 Standard;
- objective ineligibility takes next deterministic row; no winner-based rerolls.

## Construction requirements

For every selected case, enforce CASE-DESIGN exactly. In particular:

- A/B/C can technically succeed under equal capability;
- hidden material adds checks only, never unstated requirements;
- exact run-visible field boundary is preserved;
- PROCEED/BLOCK truth and accepted blocker classes are frozen;
- BLOCK cases satisfy the prevalence ceiling and resolvable-twin rule where feasible;
- source/provenance and later resolution are separable from authorized run sources;
- external cases receive sampling-reference cutoff fields;
- seeded stress is recorded before overlay audit;
- counterweight labels require the approved primary-outcome harm-path semantics;
- a simple competent A/C agent is allowed to win and protocol overhead can make B lose.

Terminal class and MAPS-related overlay/family labels are not selection inputs.

## Required sealed outputs

Keep inaccessible to MAPS_L protocol modifiers until the permitted look:

```text
selection_secret / selection_seed
candidate eligibility/ranking/rejection ledger
selected case IDs / source URLs
holdout membership
case fixtures / starting-state packages
benchmark-visible case records
hidden companion records
objective checks / semantic properties
accepted blocker classes
seeded_stress_families
counterweight fields
canaries / resolution identifiers
answer-bearing provenance
```

## Required non-secret outputs

Return only:

```text
pre_authoring_package_hash
protocol_bundle_hash
generic_control_hash + exact-text approval statement
source_pool_definition_sha256
sampling reference model/cutoff
curator/custodian identity + eligibility statement
storage/access-control class
selection_secret_commitment
public NIST pulse evidence
selection_seed_commitment
candidate attempts / accepted / rejected aggregate counts
aggregate rejection-reason counts
aggregate domain / complexity / project-origin / terminal-class counts
aggregate NONE / STRESS / COUNTERWEIGHT counts after independent overlay audit
aggregate seeded_stress prevalence
FROZEN_STANDARD_count
SEALED_HOLDOUT_count
corpus_hash
holdout_bundle_hash
confirmatory look count
exposure owners
freeze timestamp
```

Do not return data from which selected identities can be trivially reconstructed.

## Verification / review

Before DONE:

1. deterministic secret/beacon/selection commitments are reproducible later without revealing secret now;
2. distinct sealed-access reviewer audits every primary overlay class after construction;
3. population constraints and BLOCK/twin rules pass;
4. hidden checks are task-derived and protocol-neutral;
5. case sources/answers cannot leak through intended run surfaces;
6. access logs/custody state and seal hashes pass;
7. a **different independent corpus/pre-freeze reviewer** returns the required next-gate verdict.

That verdict may open only the separate pre-run manifest/threshold/runner gate. It does not authorize benchmark execution.

## Failure / recovery

- Ineligible sampled task → record frozen reason; take next deterministic row.
- Source pool cannot fill a required cell → return `SOURCE POOL INSUFFICIENT`; do not add repositories privately.
- Secret/seed/sample exposure before permitted look → `CUSTODY BREACH — SELECTION CONTAMINATED`; new secret commitment + later beacon + reselection required.
- Exposure of one case without seed/sample-wide exposure → retire affected case and follow deterministic replacement rule.
- Stratum imbalance caused by objective rejections → continue deterministic within-stratum order; never hand-pick.
- Required source necessarily reveals resolution → case ineligible.
- Missing independent custody → remain BLOCKED; no case IDs are enumerated.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Current blocker

`independent curator/custodian + access-controlled storage unavailable in current MAPS_L owner context`.

The owner-side public package is complete. Exact next action is external handoff via `pre-corpus/INDEPENDENT-CURATOR-START-PROMPT.md`, pinned to package `c0927f437e7a4d07d1a825eace7e3d061ad0bb9c6a8b8775c28b2e4bfd07e963`. Another fresh chat visible to the MAPS_L owner is not eligible custody.
