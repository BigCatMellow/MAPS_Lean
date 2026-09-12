# Independent curator/custodian start prompt — protocol-effectiveness-v0

Use this prompt **only** with a genuinely independent curator/custodian whose private working storage and working transcript are inaccessible to the MAPS_L repository owner, benchmark owner, protocol contributors, and successor-protocol editors until the permitted reveal.

A normal fresh chat under the same MAPS_L owner's account is **not** an eligible custody environment.

---

Act as the **independent corpus curator/custodian** for `BigCatMellow/MAPS_Lean` PR #341, benchmark line `protocol-effectiveness-v0`.

Your role is to independently validate the instantiated pre-authoring package, take sealed custody of the deterministic sample, construct the primary corpus/holdout without exposing it to MAPS_L protocol modifiers, and return only the allowed non-secret freeze evidence.

You are **not** authorized to execute A/B/C benchmark agents or spend money.

## Gate 0 — custody eligibility

Before reading or selecting any candidate issue IDs, determine whether all are true:

1. you do not hold a MAPS_L protocol-modifying role;
2. the MAPS_L repository/user owner cannot access your private selection/case working storage or private working transcript;
3. you can retain a 256-bit secret, ranking ledger, selected case identities, hidden contracts, holdout membership, and case artifacts without putting them in the MAPS_L repository or another owner-accessible location;
4. access to that private material can remain excluded from MAPS_L protocol modifiers until the permitted reveal;
5. a later distinct independent corpus reviewer can inspect the sealed package without first disclosing it to protocol modifiers.

If any is false, **STOP** before issue enumeration and return exactly:

`INELIGIBLE CUSTODY ENVIRONMENT`

plus the failed eligibility condition(s). Do not select or reveal case IDs.

## Read and follow

Read repository root `AGENTS.md`, then:

- `work/tasks/protocol-effectiveness-benchmark.md`
- `work/tasks/protocol-effectiveness-corpus-construction.md`
- `work/reviews/pr-341-rereview-evidence-369bcca.md`
- the five normative owner files under `work/evals/protocol-effectiveness-benchmark/`
- every file listed in `pre-corpus/PRE-AUTHORING-PACKAGE-MANIFEST.json`

The independently approved design head is:

`369bccaf68b258c70eb6efec0c9f70115c8014cb`

The candidate pre-authoring package hash is:

`1cc69cd2adfc41a40bd01505a75a99cfd54984a44a9160f0ae974f98be61b89d`

Recompute the package hash from the exact Git blob SHAs listed in `PRE-AUTHORING-PACKAGE-MANIFEST.json` using its declared hash rule.

If the package does not match exactly, **STOP** and return:

`STALE PRE-AUTHORING PACKAGE`

Do not silently review or curate a different package.

## Gate 1 — independent pre-authoring validation

Before generating the selection secret or enumerating candidate issue IDs, independently verify:

### Treatment surface

- immutable tested protocol ref is `5f07b33e9fa09a5e091c6f0993092230c2faf308`;
- 45-file treatment inventory is complete under the declared include/exclude rule;
- canonical bundle hash recomputes to `7a944e3db3575c1f94df5872d8b15a644ecd7eb254893b10d9d1ebcd83aa3341`;
- A/B/C share the neutral bootstrap and treatment injection position as declared;
- B receives only the frozen offline MAPS_L bundle/launcher treatment rather than mutable live MAPS sources;
- target-project authority remains common and byte-identical across arms;
- static instruction/context-cost disclosure is accurate and the dynamic B document-read accounting rule is neutral.

### Arm C

Independently judge the exact text in `GENERIC-CONTROL.md`.

Approve it only if it is a competent non-strawman generic workflow that reasonably permits:

- evidence inspection;
- proportional planning;
- self-verification;
- helper/tool use when useful;
- scope/authority respect;
- completion of separable authorized work;
- stopping at genuine blockers;

without importing MAPS_L-specific concepts/artifacts.

If the exact Arm-C text is materially weak, biased, or MAPS-shaped, **STOP before selection** and return a non-secret correction finding. Do not privately substitute another control and continue.

### Sampling/source pools

Verify `SOURCE-POOL-DEFINITION.json` canonical definition hash:

`5101ed5b416f9c61b64d658a03864d77550489ba1a5eca1ba19f3f0352cc4fe6`

Before selection, verify each named repository is usable for the declared historical window and that the objective issue/PR metadata needed by the eligibility filters is available.

Do not inspect or score candidates for MAPS-specific authority/recovery/review/continuation phenomena, expected winner, stress family, or overlay class while deciding whether the public pools themselves are adequate.

Reference model/cutoff for sampling sensitivity:

```text
provider = OpenAI
model = gpt-5.6-sol
documented knowledge cutoff = 2026-02-16
```

If a pool must be changed, **STOP before issue selection** and return only the non-secret pool-level reason. A pool-definition change requires a new definition hash/package review before selection.

### Custody

Verify your actual storage/access configuration satisfies `CUSTODY-AND-EXPOSURE-PLAN.md`.

Record non-secret curator/custodian identity, role, prior MAPS_L exposure, storage class, ACL summary, exposure owners, confirmatory-look count, and retirement-rule acknowledgement. Do not publish private storage paths, credentials, or secrets.

## Gate-1 verdict

If any material pre-authoring defect exists, return:

`PRE-AUTHORING CORRECTIONS REQUIRED`

with only non-secret findings. Do not generate a selection secret or enumerate issue IDs.

If all Gate-1 checks pass, record:

`PRE-AUTHORING PACKAGE ACCEPTED FOR SEALED SELECTION`

and continue privately.

## Gate 2 — non-reroll secret/beacon commitment

Inside your private custody environment:

1. generate a cryptographically random 256-bit `selection_secret`;
2. keep the secret private;
3. compute `selection_secret_commitment = SHA256(selection_secret)`;
4. durably publish/return only that commitment and its timestamp **before** the qualifying public beacon pulse;
5. use the exact beacon rule in `TARGET-WORK-SAMPLING-MANIFEST.md`: first valid NIST Randomness Beacon 2.0 pulse at or after `source_pool_freeze_timestamp + 600 seconds`;
6. record the public pulse timestamp/index/output/certificate identifier where available;
7. derive `selection_seed` exactly as specified using HMAC-SHA256;
8. keep `selection_seed` private;
9. return only `selection_seed_commitment = SHA256(selection_seed)`.

Do not choose another secret/pulse/seed because you dislike the resulting sample.

If the secret or seed is exposed to a MAPS_L protocol modifier before the permitted reveal, stop and mark the selection contaminated; do not silently reseal it.

## Gate 3 — private deterministic source selection

Inside custody only:

1. enumerate objectively eligible issue rows from the frozen 16-repository definition;
2. assign domain and mechanical complexity only under the frozen rules;
3. derive the private HMAC selection rank for each eligible row;
4. select 48 identities under the exact per-domain/per-complexity quotas and `max_cases_per_repository = 4`;
5. record every objective rejection and `REPO_CAP` skip in the sealed ledger;
6. never reject/reroll because a task seems favorable or unfavorable to MAPS_L;
7. derive private holdout ranks and assign exactly 12 SEALED_HOLDOUT identities under the frozen rule; remaining 36 are FROZEN_STANDARD.

Do not return selected IDs, URLs, ranks, ranking table, seed, or holdout membership to the MAPS_L owner.

If the frozen pools cannot fill a required stratum under the objective eligibility rules, stop and return only:

`SOURCE POOL INSUFFICIENT`

plus aggregate pool/domain/complexity deficiency counts that do not reveal selected/candidate identities. Do not improvise new repositories.

## Gate 4 — sealed case construction

Construct the cases privately under `work/tasks/protocol-effectiveness-corpus-construction.md` and the normative CASE/RUN/SPEC owners.

Required properties include:

- history-free/pre-fix starting state with no resolving commit/object leakage;
- task-facing fixture derived from the source request, not the answer;
- hidden contract contains checks, never unstated process requirements;
- exact run-visible boundary;
- correct PROCEED/BLOCK truth and blocker classes;
- hidden canaries created with hidden material;
- source/resolution identifiers kept off run-visible surfaces;
- sampling-reference resolution/cutoff fields recorded privately;
- terminal class and MAPS-related families/overlays assigned only after source selection;
- counterweight labels satisfy the approved primary-outcome harm-path rule;
- simple competent A/C agents are allowed to win and protocol overhead may make B lose;
- combined population constraints are satisfied without winner-based replacement.

Do not run candidate benchmark agents while constructing cases.

## Gate 5 — independent overlay audit

Every primary case's `NONE | STRESS | COUNTERWEIGHT` classification must receive the independent overlay audit required by the normative design.

If you authored the case/overlay, do not self-approve that overlay. Use a distinct independent reviewer who also has eligible sealed access and does not expose cases to MAPS_L protocol modifiers.

Resolve overlay findings inside custody. Preserve reclassifications in the sealed record.

## Sealed outputs

Keep private until the permitted look:

- selection secret/seed;
- candidate/ranking ledgers;
- selected issue IDs and URLs;
- Standard/holdout membership;
- task fixtures and starting-state packages;
- visible/private case records;
- hidden checks/answers;
- blocker classes;
- stress/counterweight records;
- canaries/resolution identifiers;
- answer-bearing provenance.

## Non-secret return package

Return only the fields allowed by the corpus-construction task, including:

```text
pre_authoring_package_hash
protocol_bundle_hash
generic_control_hash + exact-text approval statement
source_pool_definition_sha256
sampling_reference_model/cutoff
curator/custodian identity + eligibility statement
storage/access-control class
selection_secret_commitment
public NIST pulse evidence
selection_seed_commitment
candidate_attempt / accepted / rejected aggregate counts
rejection-reason aggregate counts
aggregate domain / complexity / project-origin / terminal-class counts
aggregate NONE / STRESS / COUNTERWEIGHT counts after independent overlay audit
aggregate seeded_stress prevalence
FROZEN_STANDARD_count
SEALED_HOLDOUT_count
corpus_hash
holdout_bundle_hash
confirmatory_look_count
exposure owners
freeze timestamp
```

Do not include information from which selected identities are trivially reconstructable.

## Final curator status

Return exactly one:

- `SEALED CORPUS READY FOR INDEPENDENT CORPUS/PRE-FREEZE REVIEW`
- `PRE-AUTHORING CORRECTIONS REQUIRED`
- `SOURCE POOL INSUFFICIENT`
- `CUSTODY BREACH — SELECTION CONTAMINATED`
- `INELIGIBLE CUSTODY ENVIRONMENT`
- `STALE PRE-AUTHORING PACKAGE`

Even `SEALED CORPUS READY...` does **not** authorize benchmark execution. The next gate is a distinct independent corpus/pre-freeze review using sealed-access evidence plus the non-secret return package.
