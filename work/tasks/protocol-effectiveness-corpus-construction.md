# Task: protocol effectiveness corpus construction

- Status: `BLOCKED`
- AGI status: `AGI READY`
- Type: `EVALUATION DATASET / CUSTODY`
- Owner: case-construction owner (role/custody mechanism unresolved)
- Risk: `HIGH`
- Parent: [`protocol-effectiveness-benchmark.md`](protocol-effectiveness-benchmark.md)
- Goal: After public selection and Gate 4 authority/custody resolution, construct the initial benchmark cases and hidden materials under the approved Experiment-P design, preserve exposure integrity, and return the non-secret freeze package for independent pre-run review.
- Autonomous continuation: `YES` once the preconditions below are satisfied.

## Source / inputs

Read first:

1. repository `AGENTS.md`;
2. `work/evals/protocol-effectiveness-benchmark/BENCHMARK-SPEC.md`;
3. `CASE-DESIGN.md`;
4. `RUN-PROTOCOL.md`;
5. `SCORING-AND-ANALYSIS.md`;
6. current `pre-corpus/PRE-AUTHORING-PACKAGE-MANIFEST.json`;
7. every file pinned by that package manifest;
8. current `pre-corpus/INDEPENDENT-CURATOR-START-PROMPT.md`;
9. current `pre-corpus/CUSTODY-AND-EXPOSURE-PLAN.md`;
10. r9 approval `work/reviews/pr-341-rereview-evidence-369bcca.md`.

The five normative benchmark owner documents are frozen design owners. This task must not restate or override them when a link is sufficient.

## Preconditions before case construction

All must be true:

- revised pre-authoring package has fresh independent acceptance;
- exact Arm C has the required competence/non-strawman approval;
- public deterministic selection (Gates 2/3) has completed under the frozen beacon rule;
- selected IDs/URLs/ranks and holdout membership have been published as required by the current selection protocol;
- Gate 4 case-construction role/custody question has an approved resolution;
- the resulting hidden-material storage/access boundary satisfies `BENCHMARK-SPEC.md` §9 and the current custody/exposure plan;
- no benchmark execution has begun.

Until those conditions are met, remain `BLOCKED` and do not create hidden case material.

## Boundary

### MAY — after preconditions open

- consume the already-public selected 48 identities;
- construct benchmark-visible fixtures and hidden companion records under `CASE-DESIGN.md`;
- create task-derived hidden checks rather than hidden requirements;
- create/record canaries and answer-bearing provenance under the approved exposure boundary;
- assign post-selection stress/counterweight/family fields under the normative rules;
- apply objective case-construction rejection/replacement rules defined by the benchmark owners;
- build the Standard/Holdout construction packages and freeze hashes/look-count/exposure-owner records;
- return the non-secret construction/freeze evidence permitted by the normative owners.

### MUST NOT

- modify MAPS_L runtime/protocol behavior or the five normative benchmark owners;
- rerun or alter the already-approved selection process merely because a selected case is inconvenient;
- reject tasks because they look favorable/unfavorable to MAPS_L;
- expose hidden contracts, oracle answers, hidden checks, canaries, answer-bearing provenance, or sealed fixtures to MAPS_L protocol modifiers before the permitted look;
- run A/B/C agents, Smoke, Standard, evaluators, graders, or benchmark APIs;
- spend money;
- merge PR #341.

## Selection boundary

Selection is **not** a sealed child-task activity anymore.

PR #369 retired selection custody. The current pre-corpus protocol makes selection public and beacon-anchored. Selected IDs/URLs, ranks, and holdout membership are expected to be public after Gate 3 and are not themselves case-content leaks.

This task begins with those selected identities only after the parent task has completed the selection gates.

## Construction requirements

Follow `CASE-DESIGN.md`, `RUN-PROTOCOL.md`, and `BENCHMARK-SPEC.md` exactly. In particular:

- A/B/C must be technically capable of success under equal capability;
- hidden material adds checks only, never unstated requirements;
- exact run-visible field boundaries are preserved;
- PROCEED/BLOCK truth and accepted blocker classes are frozen from task-derived truth;
- source/provenance and later resolution remain separated from authorized run sources;
- external cases carry the required sampling-reference cutoff fields;
- stress/counterweight/family assignment happens after source selection under the approved semantics;
- simple competent A/C agents are allowed to win and protocol overhead is allowed to make B lose.

## Keep sealed during construction

Subject to the approved Gate 4/5 exposure plan, keep inaccessible to MAPS_L protocol modifiers until the permitted look:

```text
case fixtures / starting-state packages when answer-bearing
hidden companion records
objective hidden checks / semantic properties
accepted blocker classes when hidden
stress/counterweight records when answer-bearing
canaries / resolution identifiers
answer-bearing provenance
sealed holdout construction bundle
```

Selected issue identities, public ranks, and holdout membership are **not** in this sealed list under the current selection model.

## Required non-secret construction outputs

Return only the fields permitted by the normative owners/current custody plan, including the applicable package hashes, aggregate construction/rejection counts, aggregate strata/terminal/overlay counts, corpus/freeze hashes, exposure-owner/look-count records, and freeze timestamp.

Do not return hidden case answers or data that defeats the approved exposure boundary.

## Verification / review

Before DONE:

1. construction/custody state satisfies the approved Gate 4/5 boundary;
2. distinct reviewer audits required overlays after construction;
3. population constraints and BLOCK/twin rules pass;
4. hidden checks are task-derived and protocol-neutral;
5. case sources/answers cannot leak through intended run surfaces;
6. access/custody state and freeze hashes pass;
7. a different independent corpus/pre-freeze reviewer returns the required next-gate verdict.

That verdict may open only the separate pre-run gate. It does not authorize benchmark execution.

## Failure / recovery

- Objective selected-case ineligibility discovered during construction → apply the frozen replacement rule; do not hand-pick.
- Source pool/selection deficiency that cannot be solved under frozen rules → return the applicable parent selection failure status; do not improvise repositories.
- Hidden case material exposed before the permitted look → retire/replace affected confirmatory material according to the normative exposure rules.
- Missing approved construction custody/role boundary → remain `BLOCKED`; do not author hidden material.
- Missing independent construction/pre-freeze review → do not mark DONE.

## Current blocker

Public selection has not yet completed, and the separate Gate 4 case-construction role/custody mechanism remains unresolved.

Immediate parent-side work is therefore:

1. fresh independent review of the revised pre-authoring/selection package;
2. Gate 1 Arm C approval resolution;
3. public deterministic selection.

Only then should this child move from `BLOCKED` to active construction.
