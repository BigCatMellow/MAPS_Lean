# Triage Packet — Visual-Fidelity Acceptance Rule

- to: EI-triage / command-center-intake
- from: claude-lab-lure
- date: 2026-07-19
- source: [[INS-0031-on-visual-fidelity-tasks-verify-by-screenshot-vs-reference-befor]]
  → [[IDEA-0024-a-design-port-task-should-freeze-the-approved-mockup-as-the-acce]]
- status: OPEN — requests triage into a durable acceptance-criteria rule

## Why this packet exists

On the ClearFront UI redesign (G1 prove-it), the implementing agent (me) told
the operator the build "matches the mockup" three separate times while it still
visibly diverged. Each claim was backed by 10/10 passing tests and a correctly
ported STRUCTURE — but the operator's actual bar was pixel-fidelity to the
approved mockup, and I never compared the real build to the mockup at the
operator's own window width. The final defect was a legacy CSS leak (`aside {…}`
element rules restyling new `<aside>` rails) that only appeared at ~963px, not
the 1440px I screenshotted. Result: ~3 avoidable operator-rework rounds.

## Requested triage outcome

Attach this as a standing acceptance rule for any task whose acceptance is
"matches an approved visual mockup/redesign":

1. **Freeze the reference.** The approved mockup is stored as the reference
   artifact on the task.
2. **Screenshot-vs-reference before submission.** A screenshot of the REAL
   build must be captured and compared to the frozen mockup — not the test
   suite, not a description.
3. **Verify at the operator's target viewport width**, not just wide desktop.
4. **Do not report "matches the design" on tests-green + ported-structure
   alone** — that is necessary but not sufficient.
5. **Porting hygiene:** when styling into an existing stylesheet, prefer
   class-scoped selectors; avoid reusing bare element selectors
   (`aside`/`main`/`section`) the legacy CSS already targets.

## Suggested disposition

Promote IDEA-0024 into (a) a line in `notes/review-guide.md` under visual/UI
review, and/or (b) a task-authoring checklist item for design-port tasks. Small,
reversible, mechanically checkable. No authority change.
