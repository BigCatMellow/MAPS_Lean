# Insight Record

Insight ID: INS-0031
Project: MAP
Related task: NONE
Detected by: claude-lab-lure
Date: 2026-07-19
Status: OPEN

## Short description


- obs: On visual-fidelity tasks, verify by screenshot-vs-reference before claiming 'matches the design'; passing tests + a ported structure are necessary but not sufficient, and premature 'done' claims cause operator rework loops.

## Trigger


- src: During the ClearFront side-rails UI port I declared the work 'matches the mockup' three times while it still visibly diverged (Stage 1 layout-only; Stage 2 contain-fit champions + plain title vs the mockup's cover-fill champions + CLEARFRONT gradient wordmark). The operator pushed back each time: 'doesnt look like what we worked on', 'this again doesnt look like the mockup', 'just make that'.

## The synthesis


- synth: On visual-fidelity tasks, verify by screenshot-vs-reference before claiming 'matches the design'; passing tests + a ported structure are necessary but not sufficient, and premature 'done' claims cause operator rework loops.

## Why it might matter


- why: The port passed 10/10 tests and reproduced the mockup's STRUCTURE at each claim, so I conflated structural/functional correctness with visual fidelity -- but the operator's real acceptance bar was pixel-fidelity to the approved mockup. Convergence only became fast once I screenshotted the real app (headless chromium) after every change and compared it to the frozen mockup. The champion cover-fill alone took 3 CSS attempts that CSS-reasoning-without-screenshots failed to resolve but per-iteration screenshots settled immediately.

## Evidence


- ev: Session transcript 2026-07-19: mockup iterated v1-v6 cheaply via artifacts (efficient); real-app port then triggered 3 'not the mockup' rounds before matching. Efficient parts: mockup-first iteration, tests-green-throughout (no logic regressions), headless-screenshot verification once adopted. Inefficient part: claiming 'matches' on structural completion, and reasoning about CSS instead of screenshotting each attempt. Durable record: Projects/ClearFront/notes/ui-redesign-kickoff-2026-07-19.md.

## Risk


- risk: Acting without promotion could bypass HPOM governance.

## Scope


- scope: Only the files and artifacts named in this record.

## Recommended next action

- [ ] ignore
- [ ] park
- [ ] task
- [x] idea  ([[IDEA-0024-a-design-port-task-should-freeze-the-approved-mockup-as-the-acce]])
- [ ] experiment
- [ ] escalate-human

## Notes

- root-cause-confirmed (2026-07-19): the final divergence the operator caught
  was a legacy CSS leak — the new side-rails were `aside` elements
  (class lrail/rrail), and the original stylesheet had element-typed rules
  (`aside { grid-template-columns:1fr 1fr }`, `aside { display:none }`) that
  hijacked the new rails and only manifested at the OPERATOR'S window width
  (~963px CSS), not the 1440px I had been screenshotting. Fix was changing the
  rails from the aside element to a div element. Two generalizable traps:
  (a) verifying at one viewport hides responsive breakage; (b) reusing
  element-typed selectors (aside, main, section) from a pre-existing stylesheet
  silently restyles new markup of the same element type.

- TRIAGE RULE (record for intake/EI-triage so it does not recur): any task whose
  acceptance is "matches an approved visual mockup / redesign" MUST carry, as an
  explicit acceptance criterion: (1) the approved mockup frozen as the reference
  artifact; (2) a screenshot of the REAL build compared against it BEFORE
  submission; (3) verification at the operator's actual/target viewport width,
  not just a wide desktop. Tests-green + ported-structure is necessary but not
  sufficient and must not be reported as "matches the design". When porting into
  an existing stylesheet, prefer class-scoped selectors and avoid reusing bare
  element selectors (`aside`/`main`/`section`) the legacy CSS already styles.
  See [[IDEA-0024-a-design-port-task-should-freeze-the-approved-mockup-as-the-acce]].
