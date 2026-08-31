reviewer: SENTINEL-CHATGPT
head_sha: 826afc90387a8f825b9147a0b121475086f59257
independent: true
summary: CHANGES_REQUESTED — exact-head review found four blocking defects: lost global task-owner invariant, operational-independence N/A loophole, brittle completion-gate regression protection, and missing before→after route/read-cost evidence.

## Author fixes applied (not a re-review; a fresh independent reviewer is still required)

Head above is stale. On top of `826afc9` the author (BigCatMellow, orchestration
operator — not independent of this work) applied:

1. Restored the global task-owner invariant as hard invariant 12 in `AGENTS.md`
   ("One owner, independent review. Each active task has one accountable owner;
   no owner approves their own substantive work."); byte guard still met.
2. Tightened `playbook/TASK_LIFECYCLE.md` operational-independence gate: added
   stable rule IDs `OIG-DONE` / `OIG-NA-WHOLE` / `OIG-NA-AUTO`. Whole-gate `N/A`
   is now reserved for genuinely non-repeatable work and explicitly excludes
   "automation infeasible"; repeatable work keeps the gate `REQUIRED` with only
   the automation component `N/A — reason` and a mandatory manual reproduction
   fallback. `templates/task.md` fields updated to match.
3. Re-anchored `tests/test_documentation_sprawl.py` completion-gate regression
   tests on headings + rule IDs instead of exact sentences, and added tests for
   the actual completion-semantic invariant and the N/A escape hatch.
   (`tests/test_digital_fungus_routes.py` was already structural — no change.)
4. Recorded actual before→after common-route / read-cost numbers (single
   analyzer run over pre/post trees) in the PR body and the task file; fixed a
   dangling `docs/CONTEXT.md` link left by the retirement in
   `playbook/SIMULATION_DESIGN.md`.

This evidence file stays `CHANGES_REQUESTED` / non-approved; the disposition
must be re-decided by an independent reviewer against the new head.
