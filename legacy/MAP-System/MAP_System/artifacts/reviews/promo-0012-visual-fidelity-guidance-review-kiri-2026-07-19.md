# Review: PROMO-0012 Visual-Fidelity Guidance

Reviewer: codex-lab-kiri  
Date: 2026-07-19  
Scope: Independent review of the provisional visual-fidelity sections only

## Verdict

APPROVED

No blocker or required finding remains in the scoped guidance.

## Reviewed Files

- `MAP_System/notes/review-guide.md` — `Visual-Fidelity Review`
- `MAP_System/notes/task-authoring-guide.md` — `Design / visual-port tasks`
- `MAP_System/emergence/insights/INS-0031-on-visual-fidelity-tasks-verify-by-screenshot-vs-reference-befor.md`
- `MAP_System/emergence/ideas/IDEA-0024-a-design-port-task-should-freeze-the-approved-mockup-as-the-acce.md`
- `MAP_System/emergence/promotions/PROMO-0012-idea-0024.md`

The adjacent `Risk-Tiered Review` section was read for compatibility only. This
review does not approve or take ownership of unrelated working-tree changes.

## Findings

| Severity | File | Finding | Required Action |
|---|---|---|---|
| None | Scoped sections | No blocking, required, or recommended defect found. | None. |

## Acceptance Review

| Check | Result | Evidence |
|---|---|---|
| Accurate to the observed failure | PASS | INS-0031 records three premature visual-match claims, the missing operator-width comparison, and the legacy bare-element selector collision. The guidance preserves those causal facts without claiming that screenshots replace functional tests. |
| Author guidance is concrete | PASS | The task-authoring section requires a frozen approved reference, a real-build comparison before submission, and the operator target viewport when the task claims visual fidelity. |
| Reviewer guidance is concrete | PASS | The review section repeats the three observable checks and adds bounded porting hygiene: prefer class-scoped selectors and avoid reusing bare element selectors already styled by legacy CSS. |
| Compatible with risk-tiered review | PASS | The rule is conditional on a task claiming that it matches an approved mockup. It strengthens the evidence for that claim; it does not change the task's risk tier, require another reviewer, add a release checklist, or create a new mechanical gate. |
| Non-duplicative | PASS | The two placements serve different readers. Task authors see what to encode in acceptance criteria; reviewers see what evidence to inspect. The task-authoring guide cross-links the fuller review guidance instead of duplicating its rationale and CSS example. |
| Scope and language are proportional | PASS | “Must” and “require” apply only to substantiating the explicit visual-match claim. Porting hygiene remains advisory through “prefer” and “avoid,” rather than becoming a universal selector ban. |

## Verification

- Read both files in full and inspected the scoped diff in surrounding context.
- Searched MAP notes and shared guidance for existing mockup, viewport,
  screenshot, and visual-fidelity rules; no conflicting or duplicate rule was
  found outside these two staged sections.
- `python3 MAP_System/scripts/map_emergence.py validate` — PASS before the
  review artifact was written: `OK emergence artifacts valid (80 checked)`.

## Notes

- This approval covers the low-risk guidance change authorized by the operator
  under PROMO-0012. It does not approve IDEA-0025's proposed screenshot tool or
  INS-0032's proposed mechanical surfacing; those remain separate work.
- The author may remove the provisional markers and close PROMO-0012 with the
  operator authority plus this independent review. No code, validator, task
  state, release gate, or runtime behavior was reviewed or changed here.
