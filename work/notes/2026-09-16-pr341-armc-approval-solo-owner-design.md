# PR #341 — Arm C Gate 1 approval under a solo-owner project

Status: **DESIGN CORRECTED — EXISTING INDEPENDENCE REQUIREMENT PRESERVED**

This note addresses one question only: how the exact candidate
`GENERIC-CONTROL.md` can satisfy Gate 1's competent/non-strawman approval
requirement when the project has a solo human owner.

It does **not** change the Gate 1 standard, selection, case-construction custody,
the five normative benchmark owners, or benchmark execution authority.

## 1. Governing requirement

Current `GENERIC-CONTROL.md` requires, before issue enumeration/selection:

> an independent party without a MAPS_L development stake

to approve the exact candidate text as a competent non-strawman generic control,
or reject it and return a public correction finding.

That wording is controlling. PR #369 retired independent custody for **selection**;
it did not retire independence for this qualitative Arm C judgment.

A same-owner adversarial session may produce useful evidence, but it does not
satisfy this requirement and must not be labeled independent approval.

## 2. Why selection's beacon solution does not transfer

Selection is an arithmetic/predictability problem. A future NIST beacon can make
a precommitted selection outcome unknowable before the pulse and publicly
recomputable afterward.

Arm C approval is a qualitative content judgment about an already-fixed text:
whether it is a genuinely competent generic workflow rather than a deliberately
weak comparator. External randomness cannot make that judgment independent.

Therefore Gate 1 needs an actual independent reviewer, not a cryptographic
substitute and not a redefinition of same-owner critique as independence.

## 3. Lowest-friction compliant route

Use the repository's existing independent-review model.

A reviewer is eligible for this Gate 1 act only if the reviewer:

1. did not author `GENERIC-CONTROL.md`;
2. did not author the substantive benchmark/package changes being judged;
3. has no MAPS_L development stake in making Arm B win;
4. receives the exact candidate text/hash and the frozen Gate 1 criteria;
5. is free to return `CHANGES_REQUESTED` without pressure to make CI green.

A fresh independent review agent/session may perform this job when it actually
meets those conditions. Merely being a fresh session is not sufficient if it
inherits authorship or a development stake.

The reviewer must inspect the exact current candidate:

```text
generic_control_sha256 = 1eb3382e1b7e52d06523e44bacbf83177058a226b83c58b2fd1a07f09f3c780f
```

and explicitly judge whether a competent generic agent can reasonably:

- inspect relevant evidence/current state;
- plan proportionally;
- complete the highest-value in-scope work;
- use tools/helpers appropriately;
- preserve scope/authority;
- complete separable work when another part is blocked;
- verify outcomes/material side effects; and
- stop on completion, genuine blocking, or budget exhaustion,

without importing MAPS-specific machinery or being structurally handicapped
against Arm B.

## 4. One review can clear both PR #371 and Gate 1

To minimize ceremony, the independent reviewer of this design PR may also perform
the Gate 1 Arm C judgment in the same review **if** that reviewer satisfies §3.

If both the design and exact control pass, the evidence-only commit
`work/reviews/pr-371-review-evidence.md` should record at minimum:

```text
reviewer: <independent identity>
head_sha: <exact PR #371 substantive head reviewed>
independent: true
summary: <non-empty review summary>
arm_c_control_sha256: 1eb3382e1b7e52d06523e44bacbf83177058a226b83c58b2fd1a07f09f3c780f
arm_c_gate1_verdict: APPROVED
```

Human-readable evidence must state that the reviewer independently inspected the
exact `GENERIC-CONTROL.md` text and found it a competent non-strawman comparator
under the existing Gate 1 criteria.

If the control is materially weak, biased, or MAPS-shaped, return
`CHANGES_REQUESTED`; do not merge #371 and do not proceed to selection.

This evidence is the Gate 1 approval artifact after #371 is merged into the
#341 branch. No second same-purpose approval ceremony is required.

## 5. Optional supporting evidence

A taxonomy-first adversarial critique, external generic-agent reference, or later
pilot manipulation check may still be useful as supporting validity evidence.

Those exercises are optional. They do **not** substitute for the independent
Gate 1 approval above and must never be labeled as doing so.

## 6. Scope boundary

This design leaves unchanged:

- the candidate `GENERIC-CONTROL.md` text/hash;
- the Gate 1 wording in `INDEPENDENT-CURATOR-START-PROMPT.md`;
- Gates 2/3 public beacon selection;
- Gates 4/5 case-construction custody and corpus review;
- the five normative benchmark-owner documents;
- the benchmark package hash;
- all benchmark execution prohibitions.

No selection, case construction, benchmark agent run, evaluator/model/API call,
spending, or merge-to-main authority is created by this note.

## 7. Required sequence

1. Fresh independent reviewer inspects this corrected design and the exact Arm C
   control.
2. If both pass, reviewer commits evidence-only
   `work/reviews/pr-371-review-evidence.md` with the fields in §4.
3. Merge #371 into the #341 feature branch using the legitimate non-main branch
   merge route.
4. Treat #341's head as changed and perform fresh exact-head package review.
5. Only after Gate 1 and the revised selection package are accepted may public
   candidate selection proceed.

The later Gate 4/5 construction-custody question remains separate.
