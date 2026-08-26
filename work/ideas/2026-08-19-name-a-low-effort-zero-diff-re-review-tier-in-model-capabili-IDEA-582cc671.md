# IDEA-582cc671: Name a low-effort zero-diff re-review tier in MODEL_CAPABILITY_ROUTING.md

- Kind: `idea`
- Date: `2026-08-19`
- ID: `IDEA-582cc671`

## Observation

PR #109's four review-evidence cycles (documented in work/notes/2026-08-18-review-evidence-resync-classifier-friction.md) each ran a full from-scratch independent review (full diff, full 626-629 test suite, ~10-15 min) even on three passes that were pure zero-diff main-sync merges, where only steps 1-2 of the review (confirm sync merge changed none of the PR's own files, confirm nothing under MUST-NOT-CHANGE moved) needed re-running -- the third step, re-attesting the prior verification still holds, is what actually differed.

## Source / context

[Review-evidence resync/classifier friction](../notes/2026-08-18-review-evidence-resync-classifier-friction.md); [MODEL_CAPABILITY_ROUTING.md](../../playbook/MODEL_CAPABILITY_ROUTING.md) effort-level routing section added in PR #103.

## Potential value

A named 'zero-diff-confirmed re-review' effort tier would save real reviewer time on any PR that races a fast-moving main under strict branch protection -- exactly the situation this session repeatedly hit across waves 5-12 (PRs #100, #109 and others needed multiple update-branch cycles). It also gives the self-approval classifier friction (also noted in that repair record) a structural way to distinguish 'first full review' from 'confirmed zero-diff re-attestation' by looking at what tier the review-evidence commit declares.

## Smallest next test

Next time a PR needs a review-evidence rebind after a pure main-sync merge, try running only the two confirm-zero-diff checks plus a short re-attestation note (skip the full test suite re-run when the diff is genuinely empty) and see whether that holds up under scrutiny -- if it does, propose the tier as a small addition to MODEL_CAPABILITY_ROUTING.md.

## Promotion

Not promoted at capture time. Promotion is a deliberate decision made by a human or task-lifecycle process (see `playbook/TASK_LIFECYCLE.md`), not an automated step of this script.

## Current disposition — 2026-08-26

`TEST`

The review-evidence rebinding/synchronization cost continued to recur in later
work, so the underlying friction remains real. The principle has **not** been
promoted to a standing tier because the cheaper procedure still needs evidence
that it preserves the exact-subject review invariant.

Revisit during the Proof Phase or the next proven zero-code-diff rebind. Measure:

- full-review versus bounded re-attestation time/tool/token cost;
- whether any full rerun after a proven zero-diff sync finds a new substantive
  defect;
- whether the abbreviated path can prove byte/diff equivalence and preserve the
  exact reviewed-subject binding.

Do not weaken review independence or SHA/subject binding to save time. If the
bounded path cannot preserve those invariants, reject the idea.
