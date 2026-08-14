# Promotion Record

Promotion ID: PROMO-0015
Project: MAP
Source idea: IDEA-0031
Source experiment: NONE
Decision owner: bigboss
Date: 2026-07-29
Status: APPROVED

## What is being promoted?

- promote: Document remote-authority classifier blocking as distinct from raw
  SQL blocking, with a report-don't-blindly-retry response.

## Why it should become real work

- why: A sanctioned context-rotation authority call failed in practice.
  Documentation prevents unsafe assumptions without weakening the classifier.

## What it becomes

- [x] HPOM-task
- [ ] decision-record
- [ ] shared-state-update
- [ ] project-artifact
- [x] MAP-system-improvement
- [ ] parked-reference

## Required next action

- next: Implement in the bounded INS-0054–0057 integration task and route the
  result to an independent reviewer.

## Approval

Approved by: bigboss, through the 2026-07-29 direction to consider INS-0054
through INS-0057 and implement the warranted system changes
Date: 2026-07-29

---

- rule: Classifier exemptions and automatic retry of policy denials are
  excluded from this approval.
- rule: no self-approval for substantive MAP changes
