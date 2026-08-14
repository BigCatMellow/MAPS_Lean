# Task: Question-led onboarding simulation

- Status: `DONE`
- Owner: `lean-question-helper`
- Risk: `LOW`
- Type: `research / process evaluation`
- Goal: Test the improved first-run path and expose the helper’s real
  uncertainties, assumptions, and decision points while it orients.
- Allowed output paths:
  - `work/reviews/TASK-002-question-led-onboarding-report.md`
  - `work/reviews/TASK-002-independent-review.md`
  - `work/handoffs/TASK-002-question-led-onboarding-handoff.md`
- Do not change:
  - `legacy/`
  - runtime code, configuration, installers, databases, launchers, and
    active guidance documents

## Acceptance criteria

- [x] The helper follows `docs/FIRST_RUN.md` from the Lean root and records its
  actual read order.
- [x] Before each substantial orientation decision, the helper records a brief
  question or assumption and next step in its report; real uncertainty is
  preferred, and “no question” is permitted when the route is clear.
- [x] The helper sends the coordinator at most five concise live updates in the
  form `question/assumption → next step`, without waiting for an answer unless
  genuinely blocked.
- [x] The report evaluates whether FIRST_RUN, README, CURRENT, CONTROL_PLANE,
  and INDEX gave a sufficient route and names remaining friction with proposed
  fixes.
- [x] The helper stays inside the allowed output paths and writes a compact
  handoff for independent review.

## Verification

- Coordinator monitors the live updates and declared output paths.
- Independent reviewer checks that the report is grounded in active Lean docs
  and distinguishes a true blocker from a non-blocking question.

## Notes

This is a usability test, not a request to implement recommendations. Do not
read `legacy/` or execute runtime commands. Do not wait for a response to a
non-blocking question; record the assumption you made and continue.

## Completion

- Owner report: `work/reviews/TASK-002-question-led-onboarding-report.md`
- Handoff: `work/handoffs/TASK-002-question-led-onboarding-handoff.md`
- Independent review: `work/reviews/TASK-002-independent-review.md`
