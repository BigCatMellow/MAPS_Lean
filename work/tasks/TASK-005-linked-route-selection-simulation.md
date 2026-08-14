# Task: Linked route-selection simulation

- Status: `DONE`
- Owner: `lean-route-helper`
- Risk: `LOW`
- Type: `research / process evaluation`
- Goal: Test whether a first-time agent can use Lean's actual links to select
  the right methods and templates for a durable project with unverified,
  time-sensitive external dependencies.
- Allowed output paths:
  - `work/reviews/TASK-005-linked-route-selection-report.md`
  - `work/reviews/TASK-005-independent-review.md`
  - `work/handoffs/TASK-005-linked-route-selection-handoff.md`
- Do not change:
  - `legacy/`
  - active guidance, runtime code, databases, launchers, installers, or
    external services

## Scenario

An operator wants a project that will span multiple sessions and agents. It
will integrate a third-party API whose pricing, authentication behavior, and
current SDK support have not been verified. The operator wants a roadmap in
ProjectUpdater eventually, but has not approved an implementation design or
budget. No code is to be written now.

## Acceptance criteria

- [ ] The helper begins at the Lean root and follows actual Markdown links for
  orientation and method/template selection; do not use directory-wide searches
  to discover the intended active route.
- [ ] The report records the actual linked route taken and identifies at least
  two plausible methods considered, why each applies or does not, and the
  selected minimum method set.
- [ ] The report identifies the specific project records/templates that should
  be created first and explains their order.
- [ ] The report clearly distinguishes research, architecture/design, operator
  approval, roadmap preparation, and implementation authority.
- [ ] The helper sends at most six live `question/assumption → next step`
  updates to the coordinator and does not wait for non-blocking answers.
- [ ] A compact handoff is written; no source documents or runtime material are
  changed.

## Verification

- Coordinator monitors the live updates and checks declared output paths.
- Independent reviewer checks the route against active Lean links and confirms
  it does not smuggle architecture or implementation authority into research.

## Notes

This is an evaluation only. The helper may read active documents that it
reaches through links, but must not read `legacy/`, execute runtime commands,
or make ProjectUpdater changes.

## Review result

The simulation established that the linked route is sufficient for method and
authority selection, but not for locating the exact bootstrap templates. A
follow-up documentation correction linked Project Bootstrap and Research to the
project brief, research brief, risk register, and roadmap templates. Focused
traversal verification passed; see `work/reviews/TASK-005-independent-review.md`.
