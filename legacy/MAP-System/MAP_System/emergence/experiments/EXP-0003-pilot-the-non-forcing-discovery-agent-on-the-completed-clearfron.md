# Experiment Record

Experiment ID: EXP-0003
Project: MAP
Source idea: INS-0028 and operator-approved Discovery Agent specification.
Owner: codex-lab-lilo
Date: 2026-07-17
Status: REVIEWED

## Hypothesis


- hyp: Pilot the non-forcing Discovery Agent on the completed ClearFront phase.

## Test


- test: Run the supplied seven-pass, non-forcing Discovery Agent method on the completed ClearFront decomposition phase. Freeze a known-findings truth set before reading the new output, then classify each result as known duplicate, useful refinement, genuinely new useful finding, weak/speculative, or scope drift.

## Scope


- scope: ClearFront purpose, user lifecycle, rules/design, TASK-207 through TASK-220 decisions and artifacts, audit, existing E/I, and current app architecture. Proposal-only; no edits.

## Limits


- limits: Visible wezterm-tab only; no implementation; exactly one finding classification; no idea quota; no automatic E/I promotion; preserve rejected ideas; no raw private transcript dependence.

## Success criteria


- pass: At least one genuinely new or materially refined high-value finding; zero mislabeled optional-as-required findings; zero implementation edits; scope drift below 20%; adjudication under 30 minutes; output is evidence-linked and machine-checkable.

## Failure criteria


- fail: Only duplicates, idea inflation, unsupported requirements, implementation changes, excessive scope drift, or curation cost exceeding likely value.

## Evidence to collect

- ev: `MAP_System/artifacts/experiments/clearfront-discovery-known-findings-2026-07-17.md`; `MAP_System/artifacts/experiments/clearfront-discovery-agent-pilot-2026-07-17.md`; `MAP_System/artifacts/experiments/clearfront-discovery-agent-adjudication-2026-07-17.md`

## Review path

- review: Coordinator novelty/value adjudication followed by independent TASK-226 review.

## Result

- result: 2 genuinely new useful findings; 1 useful new rejection; 1 known duplicate correctly rejected; 0 scope drift; 0 implementation edits; 0 optional-as-requirement mislabels. Verdict: adopt with refinement for bounded visible phase-boundary use.

## Decision

- [x] adopt
- [ ] revise
- [ ] reject
- [ ] park

## Notes

- note: Before reuse add explicit fact/inference/proposal fields, existing-record check, and decision owner. Do not turn this into a continuous model loop.
