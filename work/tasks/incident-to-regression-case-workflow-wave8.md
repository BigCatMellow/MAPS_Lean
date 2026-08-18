# Task: Document the incident -> frozen regression case workflow (SEC7)

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `MAINTENANCE`
- Owner: `agent/incident-to-regression-case-workflow-wave8`
- Risk: `LOW`
- Goal: define the operational workflow that turns a real incident into a
  frozen regression case, closing the gap
  `work/roadmaps/CAPABILITY_CHECKLIST.md` flagged for
  `agent-harness-capabilities/04-agentic-security.md` phase **SEC7**: the
  data format and CLI (`freeze_regression_case`, `runtime/cli.py`'s
  `freeze-case` subcommand) already existed, but no doc anywhere named the
  expected repeatable process for actually using them.

## Inputs and source of truth

- `runtime/evaluation/regression_case.py` (unmodified) --
  `freeze_regression_case`/`IncidentCategory`/`validate_regression_case`;
  this task documents its existing contract, changes none of it.
- `runtime/cli.py` (unmodified) -- read the exact `freeze-case` and
  `run-record` subcommand argument lists (lines ~77-113) to keep the
  documented CLI invocation accurate.
- `playbook/REPAIR_AND_LEARNING.md` (existing "Repair triage"/"Learning
  loops" sections, unmodified except for the new addition) -- the workflow
  is added as a new subsection here rather than a new standalone doc, since
  it is the mechanical continuation of the existing "add a durable
  countermeasure" guidance already in that file.
- Confirmed via grep that no existing doc (`docs/`, `playbook/`) mentioned
  `freeze-case` or the regression-case workflow before this change.

## Change boundary

MAY CHANGE / ADD:
- `playbook/REPAIR_AND_LEARNING.md` (additive new subsection only)
- this task doc

MUST NOT CHANGE:
- `runtime/evaluation/regression_case.py`, `runtime/cli.py`, or any other
  runtime/test file -- this is a pure documentation task; the mechanism
  already exists and is already tested
  (`tests/test_frozen_regression_case.py`,
  `tests/test_frozen_regression_case_taxonomy.py`).
- `playbook/REPAIR_AND_LEARNING.md`'s existing "Repair triage" severity table
  and "Diagnostics do not grant repair authority" section -- referenced, not
  duplicated or altered.

## Required semantics

1. Documents a real storage convention (`work/regression-cases/<case_id>.json`)
   for frozen case artifacts, since none existed before -- this is a
   documentation decision, not a code change; no directory is created by
   this task (the doc says to create it "the first time it is used").
2. Explicitly restates, rather than silently omitting, that
   `promotion.automatic` is always `false` and a frozen case is evidence
   only -- never self-authorizes a harness/policy/routing change.
3. Frames the workflow as the mechanical continuation of existing repair
   triage, not a replacement for it -- the new subsection explicitly says it
   "does not change repair-note severity triage" and "does not itself decide
   when a countermeasure is warranted."

## Acceptance criteria

- [x] `playbook/REPAIR_AND_LEARNING.md` documents the exact `freeze-case` CLI
      invocation with all required flags, matching `runtime/cli.py`'s real
      argument list.
- [x] The doc states the `promotion.automatic=false` / evidence-only
      constraint explicitly.
- [x] The doc proposes a concrete storage location for frozen case JSON
      artifacts.
- [x] No runtime/test files changed.

## Verification

```text
python3 -m runtime.cli freeze-case --help
python3 -m unittest tests.test_frozen_regression_case tests.test_frozen_regression_case_taxonomy -v
```

(Confirms the documented CLI flags still match the real parser; full suite
not required for a docs-only change per this repo's convention -- CI's own
`test` job covers it.)

Review required: `INDEPENDENT_REVIEW`. Self-authored; owner is not eligible
to supply that review (`work/reviews/pr-<N>-review-evidence.md` required
before merge per `scripts/check_review_evidence.py`).

## Stop / escalate

Stop rather than guess if a reviewer determines the storage convention
(`work/regression-cases/`) conflicts with an existing, different convention
already in use elsewhere that this task's grep did not find.
