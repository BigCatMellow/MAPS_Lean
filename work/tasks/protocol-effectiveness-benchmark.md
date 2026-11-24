# Task: protocol effectiveness benchmark

- Status: `ACTIVE`
- AGI status: `AGI READY`
- Type: `PLANNING / EVALUATION`
- Owner: benchmark orchestration owner
- Risk: `MEDIUM`
- Goal: Carry the independently approved protocol-effectiveness design through a valid pre-authoring review, public deterministic selection, contamination-resistant corpus construction, and pre-freeze review, then stop before benchmark execution.
- Parent roadmap: `none — PR #341 is the bounded benchmark work`
- Autonomous continuation: `YES` whenever an in-scope gate is open.

## Current verified state

- Five normative benchmark-owner documents remain independently approved at design head `369bccaf68b258c70eb6efec0c9f70115c8014cb`.
- Benchmark effectiveness remains `UNKNOWN`: no A/B/C agents, Smoke, Standard, evaluator/model/API execution, or benchmark spending has occurred.
- PR #369 merged the public beacon-anchored selection rewrite into this branch. **Independent custody is retired for selection.**
- Current branch is synchronized with `main` as of 2026-10-06.
- Exact current pre-authoring package state is owned by
  [`../evals/protocol-effectiveness-benchmark/pre-corpus/PRE-AUTHORING-PACKAGE-MANIFEST.json`](../evals/protocol-effectiveness-benchmark/pre-corpus/PRE-AUTHORING-PACKAGE-MANIFEST.json).

## Current pre-authoring package

The manifest currently records:

- package hash `32295d7152542b3d6aa2ec0f903c03c8fae2cd82056b4e0e72295d4f278a8e2f`;
- owner recompute status `SELF_RECOMPUTED_NOT_YET_INDEPENDENTLY_VERIFIED`;
- status `candidate-owner-complete-revision3-candidate-ledger-freeze-awaiting-fresh-independent-review`;
- selected case content present: `false`;
- benchmark execution authorized: `false`.

The public selection mechanism is defined by:

- [`TARGET-WORK-SAMPLING-MANIFEST.md`](../evals/protocol-effectiveness-benchmark/pre-corpus/TARGET-WORK-SAMPLING-MANIFEST.md);
- [`INDEPENDENT-CURATOR-START-PROMPT.md`](../evals/protocol-effectiveness-benchmark/pre-corpus/INDEPENDENT-CURATOR-START-PROMPT.md); and
- [`CUSTODY-AND-EXPOSURE-PLAN.md`](../evals/protocol-effectiveness-benchmark/pre-corpus/CUSTODY-AND-EXPOSURE-PLAN.md).

Selection is public and beacon-anchored, but candidate membership is frozen first: after independent package/Gate 1 acceptance, the operator enumerates and adjudicates the complete eligible population, commits the canonical candidate ledger and `candidate_set_sha256` before a future NIST pulse, then performs only deterministic ranking/selection from that frozen set. Do not reroll or perform ordinary post-pulse eligibility adjudication.

## Gates still open

### Gate 1 — Arm C

The exact `GENERIC-CONTROL.md` text still requires competence/non-strawman approval.

PR #371 is the design child addressing how that judgment should work under the solo-owner environment. Do not claim Arm C approval until the approved mechanism is actually applied to the exact control text.

### Selection-mechanism review

The revised pre-authoring/selection mechanism requires fresh independent review before the package can again be accepted for public selection.

### Gate 4/5 — case-construction custody

Case fixtures, hidden contracts/oracles, hidden checks, canaries, answer-bearing provenance, and other sealed construction material remain governed by `BENCHMARK-SPEC.md` §9 and the current custody/exposure plan.

Whether the solo operator can satisfy the construction role requirement, or an eligible independent construction custodian is still necessary, remains a distinct later design boundary.

Child task:
[`protocol-effectiveness-corpus-construction.md`](protocol-effectiveness-corpus-construction.md).

## Source of truth

1. `AGENTS.md` — repository authority/invariants.
2. The five approved normative benchmark owner documents — experiment semantics.
3. Current `pre-corpus/` package — instantiated treatment/control/source-pool/selection/custody inputs.
4. This task — parent phase/status only.
5. Child corpus task — case-construction execution contract after its preconditions open.

If this task conflicts with a normative owner or current pre-corpus package, repair this task rather than blending the texts.

## Change boundary

- MAY CHANGE: public/non-secret pre-corpus manifests, task/review/handoff records, benchmark-specific packaging/hash evidence, branch-maintenance integration, PR #341 metadata.
- MUST NOT CHANGE without a new design review: the five accepted normative owner documents or their experimental semantics.
- MUST NOT: hand-pick/reroll selection for expected arm performance; expose hidden case-construction answers/oracles/canaries to protocol modifiers before the permitted look; execute benchmark arms; call benchmark evaluator/model APIs; spend money; change MAPS_L runtime/protocol behavior for benchmark advantage; merge PR #341 outside its own gates.
- HUMAN REAUTHORIZATION REQUIRED: spending/paid execution, new credentials/storage accounts controlled by the operator, merge, or material objective expansion.

## Acceptance criteria for the current arc

- [x] Approved design preserved durably.
- [x] Exact treatment bundle/source pools/selection mechanism instantiated.
- [x] Selection custody retired in favor of public deterministic beacon-anchored selection.
- [ ] Revised pre-authoring package receives fresh independent review.
- [ ] Exact Arm C receives the required competence/non-strawman approval under an approved mechanism.
- [ ] Public deterministic selection completes without reroll and publishes the required selection evidence.
- [ ] Gate 4 case-construction role/custody boundary is resolved before hidden material is created.
- [ ] Initial primary corpus is constructed under the approved exposure boundary.
- [ ] Distinct independent overlay/corpus reviewer verifies the freeze package.
- [ ] Fresh independent corpus/pre-freeze verdict opens the later pre-run gate.
- [ ] No benchmark execution occurs in this task.

## Current next actions

1. Fresh independent review of the revised pre-authoring/selection package.
2. Resolve/apply the Gate 1 Arm C approval mechanism (#371).
3. Once both permit it, freeze the complete eligible-candidate ledger/hash before a future qualifying pulse, then execute the public deterministic selection ceremony exactly as frozen.
4. Before any hidden case construction, resolve the distinct Gate 4/5 construction-custody question.

Benchmark execution remains a later, separate authorization gate.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`
