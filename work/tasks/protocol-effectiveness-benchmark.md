# Task: protocol effectiveness benchmark

- Status: `BLOCKED_ON_DEPENDENCY`
- AGI status: `AGI READY`
- Type: `PLANNING / EVALUATION`
- Owner: benchmark orchestration owner
- Risk: `MEDIUM`
- Goal: Carry the independently approved protocol-effectiveness design through a contamination-resistant primary-corpus/holdout freeze, then stop before benchmark execution.
- Parent roadmap: `none — PR #341 is the bounded benchmark work`
- Autonomous continuation: `YES` whenever eligible in-scope work exists.

## Current verified state

- Pre-corpus design gate: **APPROVED FOR CORPUS CONSTRUCTION** at reviewed head `369bccaf68b258c70eb6efec0c9f70115c8014cb`.
- Independent approval: [`../reviews/pr-341-rereview-evidence-369bcca.md`](../reviews/pr-341-rereview-evidence-369bcca.md).
- J3/v5 resolved; I2–I4 and all B/M/N/F/G/H owner findings remain resolved; 512-state S4 result has zero ambiguity/unhandled/mismatch.
- The five normative owner documents have not been changed during pre-authoring instantiation.
- Benchmark effectiveness remains `UNKNOWN`: no candidate agents, benchmark evaluators/models/APIs, Smoke, Standard, or spend have occurred.

## Owner-complete public pre-authoring package

Under [`../evals/protocol-effectiveness-benchmark/pre-corpus/`](../evals/protocol-effectiveness-benchmark/pre-corpus/):

- `TREATMENT-SURFACE-MANIFEST.md`
  - tested ref `5f07b33e9fa09a5e091c6f0993092230c2faf308`;
  - 45-file / 298,322-byte offline treatment surface;
  - treatment bundle hash `7a944e3db3575c1f94df5872d8b15a644ecd7eb254893b10d9d1ebcd83aa3341`;
  - static A/B/C instruction disclosure and dynamic context-cost accounting method instantiated.
- `GENERIC-CONTROL.md`
  - exact competent candidate Arm C hash `1eb3382e1b7e52d06523e44bacbf83177058a226b83c58b2fd1a07f09f3c780f`;
  - independent competence/non-strawman approval still required.
- `SOURCE-POOL-DEFINITION.json`
  - 16 external public GitHub repositories across four domains;
  - canonical definition hash `5101ed5b416f9c61b64d658a03864d77550489ba1a5eca1ba19f3f0352cc4fe6`;
  - exact 48-case domain/complexity quotas and objective eligibility filters.
- `TARGET-WORK-SAMPLING-MANIFEST.md`
  - sampling reference `OpenAI gpt-5.6-sol`, documented cutoff `2026-02-16`;
  - selection uses curator-secret precommit + future NIST-beacon HMAC derivation so selected public issue IDs are not reconstructable by MAPS modifiers.
- `CUSTODY-AND-EXPOSURE-PLAN.md`
  - selection secret/seed/ranking ledger/selected identities are protected alongside case content.
- `PRE-AUTHORING-PACKAGE-MANIFEST.json`
  - exact six-input candidate package hash `1cc69cd2adfc41a40bd01505a75a99cfd54984a44a9160f0ae974f98be61b89d`.
- `INDEPENDENT-CURATOR-START-PROMPT.md`
  - standalone external curator/custodian contract.

Child task: [`protocol-effectiveness-corpus-construction.md`](protocol-effectiveness-corpus-construction.md).

## Owner-found contamination correction

During owner-side shaping, the initial public deterministic-seed proposal was rejected: because the source pools are public, a public seed would allow a protocol modifier to reconstruct the selected issue IDs.

The corrected candidate method requires a private curator secret committed before a qualifying future public NIST beacon pulse, then HMAC-based private rankings. Public commitments preserve later no-reroll auditability without exposing the sample.

No issue IDs were enumerated/ranked/selected in the MAPS_L owner context before this correction.

## Source of truth

- `AGENTS.md` — authority/invariants.
- Approved five normative owner documents — benchmark design rules, mechanically pinned by v5.
- Public pre-corpus package — instantiated treatment/control/sampling/custody inputs only.
- This task — parent phase/state.
- Child corpus task — exact sealed construction/custody contract.

## Change boundary

- MAY CHANGE: public/non-secret pre-corpus manifests, task/review/handoff records, benchmark-specific packaging/hash evidence, PR #341 metadata.
- MUST NOT CHANGE without a new design review: the five accepted normative owner documents or their experimental semantics.
- MUST NOT: enumerate/rank/select pristine primary source IDs in owner-visible context; expose selected primary/holdout content or sampling secret/seed; execute benchmark arms; call benchmark evaluator/model APIs; spend money; change MAPS_L runtime/protocol behavior; merge PR #341.
- HUMAN REAUTHORIZATION REQUIRED: spending/paid execution, new credentials/storage accounts controlled by the operator, merge, or material objective expansion.

## Corpus-phase acceptance

- [x] Design approval preserved durably.
- [x] Owner-side exact treatment bundle inventory/hash and context-cost accounting method instantiated.
- [x] Owner-side external source-pool definition, quotas, objective filters, sampling reference model/cutoff, and non-derivable selection algorithm instantiated.
- [x] Access-based custody contract and standalone curator handoff instantiated.
- [ ] Exact Arm C receives independent competence/non-strawman approval.
- [ ] Eligible independent curator/custodian accepts/finalizes the public package and records non-secret identity/custody/commitment metadata before issue enumeration.
- [ ] Initial primary corpus and sealed holdout are constructed under sealed custody without exposure to protocol modifiers.
- [ ] Distinct independent overlay/corpus reviewer verifies strata, leakage boundaries, hidden-check neutrality, case truth, custody, hashes, and freeze package.
- [ ] Fresh independent corpus/pre-freeze verdict opens the later pre-run gate.
- [ ] No benchmark execution occurs in this task.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Current blocker / exact next action

**True dependency:** an eligible independent curator/custodian with working storage and transcript inaccessible to MAPS_L protocol modifiers.

The current repository owner/user account and this chat are ineligible custody environments. Another fresh review chat under the same account does not solve this boundary.

Exact next action: give `pre-corpus/INDEPENDENT-CURATOR-START-PROMPT.md` plus the package pinned by `PRE-AUTHORING-PACKAGE-MANIFEST.json` to a genuinely separate curator/custodian. They either return non-secret pre-authoring corrections or accept the package, precommit the secret, and proceed privately.

Benchmark execution remains a later gate.
