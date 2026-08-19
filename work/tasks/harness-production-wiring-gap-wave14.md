# Task: Harness production-wiring gap — research note (6.4/6.5/6.31)

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `RESEARCH`
- Owner: `Claude / research agent`
- Risk: `LOW`
- Goal: document, with direct-read evidence, the shared root cause behind
  five roadmap phases currently marked `IN PROGRESS`/`NOT STARTED` for the
  same restated reason ("no production call site invokes it yet"), lay out
  the concrete options for a first real production call site, and recommend
  a direction with reasoning — without implementing any of it.

## Inputs and source of truth

- Inputs: `work/roadmaps/CAPABILITY_CHECKLIST.md` (H4, E4, H5, L6, L7, SEC3
  rows); `runtime/harness/service.py`, `runtime/harness/adapters/hcom.py`,
  `runtime/harness/types.py`, `runtime/harness/hooks.py`,
  `runtime/harness/config_ref.py`, `runtime/environment/validation.py`;
  `runtime/helpers/README.md`, `runtime/helpers/ollama.py`,
  `runtime/helpers/aider.py`; `runtime/recovery/supervisor.py`;
  `runtime/communication/`; `runtime/cli.py`;
  `work/notes/2026-08-17-recovery-equivalence-authority-design.md` (style
  and structure template); `work/tasks/harness-service-wave1.md`,
  `work/tasks/harness-foundation-wave1.md`,
  `work/tasks/harness-canonical-guard-wave1.md` (historical intent).
- Authoritative source of truth: direct grep/read of the actual repository
  state, not the checklist's own prose (the checklist rows are corroborated
  against direct evidence, not assumed accurate).

## Verified root-cause evidence (reproducible)

```
grep -rln "ExecutionBinding(" runtime/ --include=*.py
grep -rln "HarnessService(" runtime/ --include=*.py
```

Both return zero matches. `ExecutionBinding(...)` and `HarnessService(...)`
are constructed only in `tests/test_harness_*.py` and
`tests/test_agentic_security_*.py`. See the note for the full evidence
listing and the five checklist rows this explains.

## Change boundary

- MAY CHANGE: `work/notes/2026-08-19-harness-production-wiring-gap.md`
  (new file), this task file.
- MUST NOT CHANGE: any `runtime/*.py` file, any `tests/*.py` file,
  `work/roadmaps/CAPABILITY_CHECKLIST.md` (this note documents and
  recommends; it does not itself resolve the gap, so no checklist row is
  updated by this task).
- OPERATOR APPROVAL REQUIRED: none for this task itself (pure research/
  documentation). The recommended direction documented in the note (Option
  B: migrate `runtime/recovery/supervisor.py`'s hcom resume path through
  `HcomHarnessAdapter`/`HarnessService`) is explicitly **not implemented
  here** — landing it requires a separate, scoped implementation task with
  its own change boundary and its own independent review.

## Decision authority

- Owner may decide: that the five checklist rows share one root cause;
  that helpers and RnS are the only two current production execution
  paths; which option is recommended as the first production call site and
  why (documented in the note with full reasoning); that no runtime/test
  file needs to change for this task.
- Owner must escalate: nothing further within this task's scope — this
  task produces a note and a recommendation, not code. The follow-up
  implementation task (Option B wiring) is out of this task's scope and is
  expected to be dispatched separately.

## Acceptance criteria

- [x] `work/notes/2026-08-19-harness-production-wiring-gap.md` states the
      root-cause finding with reproducible grep evidence.
- [x] All five affected checklist rows (H4, E4, H5, L6, L7, SEC3) are cited
      by name with their current checklist wording.
- [x] The note describes, from direct reads, how MAPS actually executes
      work today (bounded helpers = one-shot subprocess; RnS = direct hcom
      session resume; `runtime/cli.py` = pure task-state CRUD, no execution
      loop).
- [x] At least three distinct options for a first production call site are
      described, each with concrete mechanics, risk/blast-radius, and which
      checklist rows it would unblock.
- [x] The note recommends one direction (Option B) with explicit reasoning
      for why it was chosen over the alternatives, rather than presenting
      an open menu — per explicit direction for this task.
- [x] The note states plainly that no code is safe to build in this task
      itself; the recommended direction is left to a dedicated follow-up
      implementation task.
- [x] No `runtime/*.py` or `tests/*.py` file is touched.
- [x] `work/roadmaps/CAPABILITY_CHECKLIST.md` is not touched.

## Verification and evidence

This is a `RESEARCH` task with no code changes.

- Root-cause grep evidence reproduced and confirmed as shown above (both
  commands return zero matches under `runtime/`).
- `git status`/`git diff --stat` confirms only the note file and this task
  file are added/changed — no `runtime/` or `tests/` file appears in the
  diff.
- No full test-suite run is needed or performed: there is no code change
  for a test suite to validate.

## Conditional execution rules

- N/A — single-pass documentation task with no branching execution paths.

## Stop / escalate

- Would stop/escalate if grep evidence had contradicted the premise (e.g.
  if a production call site already existed) — it did not; evidence
  confirmed the premise before writing began.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS` — root-cause claim is grep-verified, not assumed.
- Scope Test: `PASS` — change boundary is a single new note plus this task
  file.
- Authority Test: `PASS` — no code/architecture change is made; a
  recommendation is documented for a follow-up task's owner and reviewer.
- Completion Test: `PASS`
- Failure Test: `PASS` — note explicitly states what remains undecided
  within the follow-up implementation task's own scope.
- Continuation Test: `PASS` — note's "Continuation" section states the next
  step (a dedicated Option B implementation task) explicitly.

## Notes / decisions

- This task's instructions were updated mid-task: the note was originally
  scoped to flag "which option to pursue" as requiring an explicit operator
  decision (mirroring the 2026-08-17 recovery-equivalence note's pattern).
  That was revised during the task to instead require a decisive
  recommendation with honest reasoning, per explicit direction relayed for
  this specific task. The note reflects the revised framing; this task doc
  records both so the history isn't lost.
- The recommended direction (Option B) is a recommendation for a follow-up
  task, not an implementation. No `runtime/` code changes in this task.

## Completion / handoff

- Completed: root-cause verification, note, this task file.
- Not completed / explicitly out of scope: implementing Option B (or any
  option) in `runtime/`; updating `CAPABILITY_CHECKLIST.md` rows; a second
  opinion on the Option B recommendation, if requested separately by the
  dispatching agent before the follow-up implementation task is scoped.
