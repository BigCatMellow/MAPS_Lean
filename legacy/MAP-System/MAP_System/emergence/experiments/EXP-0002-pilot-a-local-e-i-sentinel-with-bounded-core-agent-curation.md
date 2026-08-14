# Experiment Record

Experiment ID: EXP-0002
Project: MAP
Source idea: Reopened IDEA-0013; operator report that E/I is not being used without prompting.
Owner: codex-lab-lilo
Date: 2026-07-17
Status: PROPOSED

## Hypothesis


- hyp: Pilot a local E/I sentinel with bounded core-agent curation.

## Test


- test: Run a local deterministic scout over a retrospective ClearFront/MAP event window and then prospectively for 7 days; compare its candidates with known [[emergence/insights/INS-0024-cdp-parity-gate-for-html-refactors]] through [[emergence/insights/INS-0027-operational-notes-are-durable-but-not-automatically-promoted-int]] and new operator corrections.

## Scope


- scope: Read-only scanning of events, task transitions, incidents, operator-correction markers, and E/I stale state; candidate queue writes only.

## Limits


- limits: No automatic promotion, no autonomous policy change, no raw transcript capture, no paid model kept continuously active, no background/headless agent, and no operator requests for routine candidates. Model-backed curation runs in a visible terminal; deterministic scan state and controls remain visible in Command Center.

## Success criteria


- pass: Retrospective recall of at least 3/4 known recent systemic insights; prospective duplicate/noise rate below 50%; at least one useful candidate the normal closeout habit missed; bounded curation under 15 minutes/day.

## Failure criteria


- fail: High noise, privacy-sensitive transcript dependence, duplicate flood, or no additional useful candidates beyond normal task closeout.

## Evidence to collect

- ev:

## Review path

- review:

## Result

- result: pending

## Decision

- [ ] adopt
- [ ] revise
- [ ] reject
- [ ] park

## Notes

- note:
