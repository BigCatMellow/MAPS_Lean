# INSIGHT-ab696436: Design/decision notes carry stale forward-references to work that has since merged

- Kind: `insight`
- Date: `2026-09-04`
- ID: `INSIGHT-ab696436`

## Observation

DEC-003 skeleton (PR #280, merged) frames runbook OPTION B as 'Requires the option-B lineage-bootstrap wiring first (scoped in 2026-09-02-lineage-bootstrap-wiring-scoping.md; = NEXT WORK 2)'. That wiring — the 'maps run bind-session' verb + tests + exercise + checklist evidence — was already fully merged in #258/#261/#263 before #280 was written. Same staleness the s26 handoff carried ('OPTION B not yet scoped') and memory feedback_lineage_bootstrap_already_merged records. A decision doc that will drive an operator call now cites completed work as a prerequisite.

## Source / context

PR #280 DEC-003-harness-enforcement-cluster-exit-criterion.md Options section; runtime/cli.py L131/585 (bind-session verb present); git log #258/#261/#263; memory feedback_lineage_bootstrap_already_merged; trajectory check #22

## Potential value

An operator reading DEC-003 Option B would think a multi-day wiring task blocks the controlled real-stall exercise, when only the exercise itself remains. Decision docs assembled from handoff snapshots need a 'verify each cited prerequisite against origin/main' step before they go to the operator.

## Smallest next test

Coordinator filling DEC-003's Recommendation this session corrects the Option B text to note the wiring is merged (#258/#261/#263) and only the live-stall exercise remains. If a 3rd design/decision doc ships with a stale 'blocked on X' where X is merged, add a checklist item to the design-note template.

## Promotion

Not promoted. Promotion is a deliberate decision made by a human or task-lifecycle process (see `playbook/TASK_LIFECYCLE.md`), not an automated step of this script.

- 2026-09-04 (trajectory check #22): the specific `DEC-003` instance is **RESOLVED** by PR #284 (`2e25e95`), which corrects the Option B text ("The wiring is merged and exercised … the rule resolves to B: a bounded controlled real-stall exercise, not new wiring"). The generalisable observation — decision docs assembled from handoff snapshots need a "verify each cited prerequisite against `origin/main`" step — stays open as an incubate-pass-1 item for the design-note template; a 3rd stale "blocked on X where X is merged" occurrence promotes it.
