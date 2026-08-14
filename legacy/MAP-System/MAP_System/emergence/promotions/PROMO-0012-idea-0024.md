# Promotion Record

Promotion ID: PROMO-0012
Project: MAP
Source idea: IDEA-0024
Source experiment: NONE
Decision owner: claude-lab-lure
Date: 2026-07-19
Status: COMPLETE

## What is being promoted?


- promote: Promote the visual-fidelity acceptance rule into canonical guidance: design/redesign-port tasks freeze the approved mockup as reference and require a screenshot-of-real-build vs reference at the operator target viewport before submission; tests-green+structure is not 'matches the design'.

## Why it should become real work


- why: Operator approved promotion (2026-07-19) after the ClearFront UI port produced ~3 avoidable rework rounds from premature 'matches' claims; root cause was single-viewport verification plus a legacy element-selector CSS leak ([[emergence/insights/INS-0031-on-visual-fidelity-tasks-verify-by-screenshot-vs-reference-befor]]). Making the check a written acceptance/review rule prevents recurrence.

## What it becomes

- [ ] HPOM-task
- [ ] decision-record
- [ ] shared-state-update
- [ ] project-artifact
- [x] MAP-system-improvement
- [ ] parked-reference

## Required next action

- next: COMPLETE as of 2026-07-29. `review-guide.md` received the promoted
  rule on 2026-07-19, but the prior completion text incorrectly claimed that
  `task-authoring-guide.md` had also been updated then. TASK-305 corrected
  that omitted second application on 2026-07-29 and disclosed the overlap in
  its delivery note.

## Approval

- authority: Operator (bigboss) approved the promotion DIRECTION on 2026-07-19
  ("promote the rule") — the authority to make it canonical.
- independent-review: APPROVED by codex-lab-kiri 2026-07-19, no findings
  (routed to kiri after codex-lab-lilo and codex-lab-hana both idled out
  mid-review — the liveness friction recorded in INS-0034). kiri authored
  neither the doc edits nor IDEA-0024 (both authored by claude-lab-lure), only
  the source triage packet, so this is an independent review of the change itself.
  Record: `MAP_System/artifacts/reviews/promo-0012-visual-fidelity-guidance-review-kiri-2026-07-19.md`.

Approved by: bigboss (authority) + codex-lab-kiri (independent review)
Date: 2026-07-19

---

- rule: Approval complete (Status: COMPLETE) — operator authority + independent review recorded above
- rule: no self-approval for substantive MAP changes
