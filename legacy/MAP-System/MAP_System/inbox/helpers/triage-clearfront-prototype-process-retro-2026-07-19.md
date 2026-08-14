# Triage Packet — ClearFront Prototype Process Retrospective

- to: EI-triage / command-center-intake
- from: claude-lab-lure
- date: 2026-07-19
- status: OPEN — requests triage/prioritization of the systemic improvements below
- emergence chain: INS-0031, INS-0032, INS-0033, IDEA-0024, IDEA-0025, PROMO-0012

## What the process actually looked like

Operator PKM -> locked design via question -> mockup iterated v1..v6 (cheap
artifact, tight feedback: efficient) -> clash animation prototyped then tabled ->
port to real app in stages -> THREE "does not match the mockup" operator rounds
-> matched only after screenshotting the real build at the operator viewport.

Efficient: mockup-first iteration; tests green throughout (zero logic
regressions); headless-screenshot verification once adopted converged fast.
Inefficient: claiming "matches" on tests-green + ported-structure; reasoning
about CSS instead of screenshotting each attempt; verifying at one viewport.

## Systemic findings (ranked)

1. **KEYSTONE — INS-0032: promoted prose rules do not change behavior unless
   mechanically surfaced.** The failure happened even though task-authoring and
   review guides already existed; they did not reach me at design-task time. The
   rule I just promoted (PROMO-0012) inherits the same gap. Highest-value fix:
   register design-fidelity as an operational lesson projected into design-task
   context (operational_lessons.py), or a submission-time checklist gate — not
   just guide prose. This gates the value of the entire E/I promotion loop.

2. **IDEA-0025: build the verifier the rule needs.** The visual-fidelity check
   requires a screenshot of the real build at a given viewport; no tool exists,
   so I hand-rolled a chromium CDP script. A mandated check with no tool gets
   skipped. Add a reusable screenshot-at-viewport script (chromium already
   present for test_all.mjs). This makes rule #1 concrete.

3. **INS-0033: prototype in the target codebase, not a vacuum artifact.** The
   standalone mockup was cheap to iterate but its fidelity did not transfer; the
   port was a re-implementation where legacy-CSS constraints (the aside-selector
   leak) only surfaced late. For design work destined for an existing app,
   prototype against the real components.

4. **INS-0031 / PROMO-0012 (already promoted, in review with lilo):** the
   screenshot-vs-reference-at-operator-viewport acceptance rule + porting
   hygiene (avoid reusing bare element selectors legacy CSS already styles).

## E/I + triage tooling papercut (asked for by operator)

`map_emergence.py validate` flags any inline angle-bracket technical content
(HTML tags, generics, comparisons) as an "unresolved template placeholder"
because PLACEHOLDER_RE = `<[^>]+>` also matches legitimate content. It cost a
validation failure + rework when I wrote literal tag names. Suggest either
narrowing the regex (e.g. require a placeholder sentinel token) or documenting
"use backticks / avoid angle brackets in emergence bodies."

## Requested disposition

Prioritize #1 (mechanical surfacing) + #2 (verifier tool) together — they make
the already-promoted #4 actually stick. #3 is a working-style guideline. All are
bounded, reversible, no authority change. Promotion of any into canonical
guidance/tasks should follow the normal core-review + operator-approval path.
