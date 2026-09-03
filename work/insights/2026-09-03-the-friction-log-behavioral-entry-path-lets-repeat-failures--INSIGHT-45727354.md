# INSIGHT-45727354: The FRICTION_LOG 'behavioral entry' path lets repeat failures close without ever getting a mechanical safeguard

- Kind: `insight`
- Date: `2026-09-03`
- ID: `INSIGHT-45727354`

## Observation

Several FRICTION_LOG entries (orchestrator-context-burn, dispatched-worker-stalls, fresh-clone contamination) are 'verified: n/a (behavioral)' + 'countermeasure: none mechanical', and the N=3-clean-arcs close rule lets them close with no test/hook/script ever added. orchestrator-context-burn closed at pass #21 after 10 clean arcs with an explicitly non-mechanical countermeasure. Operator rule 20 says a repeat failure earns a durable MECHANICAL countermeasure; the behavioral-close path is a structural exception to that.

## Source / context

playbook/REPAIR_AND_LEARNING.md section 6 close definition; work/coordination/FRICTION_LOG.md orchestrator entry (closed pass #21); operator rule 20 (CLAUDE.md, not yet in AGENTS.md)

## Potential value

This is not necessarily wrong - not every behavioral pattern has a sensible mechanical guard - but it is an unexamined tension between the close definition and rule 20, and it means the friction loop can mark things 'solved' that only got instructions. Worth an explicit note in REPAIR_AND_LEARNING that behavioral-close is a deliberate carve-out, with the bar for it.

## Smallest next test

Audit the FRICTION_LOG: how many entries closed via behavioral-N=3 vs via a real mechanical countermeasure? If behavioral-close is common, tighten its bar (e.g. requires an explicit 'no mechanical guard is feasible because X' line) or require an operator ack.

## Promotion

Not promoted. Promotion is a deliberate decision made by a human or task-lifecycle process (see `playbook/TASK_LIFECYCLE.md`), not an automated step of this script.
