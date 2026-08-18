# Task: Add PROGRAM_STEERING.md — program-level self-check before self-selected work

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `MAINTENANCE`
- Owner: `FOUNDRY`
- Risk: `LOW`

## Goal

Add a new playbook doc, `playbook/PROGRAM_STEERING.md`, that defines a lightweight
program-level steering/self-check protocol a session runs before starting any
*self-selected* work (work not explicitly directed by the operator and not an
already-scoped, open task doc) — most importantly the moment `gh issue list
--state open` comes back empty and a session is about to decide what to work on
next. Link it into `playbook/INDEX.md`.

This fills a real gap: `playbook/AGI_STANDARD.md` only asks "is this one task
clear," not "is this the right task at all." A session earlier today drifted at
the program level — closed an issue by documenting already-enforced behavior,
then nearly self-terminated instead of picking up genuine unstarted roadmap
phases, and had to be manually redirected by the operator. Nothing in the
playbook currently names or prevents that failure mode.

## Inputs and source of truth

- `VERIFIED` — `playbook/AGI_STANDARD.md` (full read): defines AGI-ready
  single-task instructions; this new doc is its explicit complement, not a
  replacement.
- `VERIFIED` — `playbook/INDEX.md` (full read): table of playbook docs with a
  one-line "need / use / do not confuse with" row per doc; the new doc gets a
  row in the same shape.
- `VERIFIED` — `playbook/TASK_LIFECYCLE.md` (full read): task shaping,
  ownership, and state-machine conventions this doc's language should stay
  consistent with.
- `VERIFIED` — `playbook/REPAIR_AND_LEARNING.md` (full read): severity table
  (Cosmetic/Drift/Blocking/Structural) and repair-note conventions;
  PROGRAM_STEERING.md must cross-reference this rather than duplicate it.
- `REPORTED` — the operator's own account (relayed via this task's assigning
  context) of the concrete drift incident that motivates this doc: a session
  treated an empty issue queue as "nothing to do," authored a documentation
  PR describing already-shipped behavior to close an issue, then nearly
  self-terminated, and had to be manually redirected.
- `ASSUMED` — `work/roadmaps/CAPABILITY_CHECKLIST.md` will exist as the
  consolidated capability status tracker (built by a concurrent, separate
  session). It does not exist at the time this task is written. This task
  MUST reference it by name and expected shape (NOT STARTED / IN PROGRESS
  status labels) without depending on its current content, and MUST NOT
  create, edit, or block on that file.
- `ASSUMED` — `playbook/MODEL_CAPABILITY_ROUTING.md` is being extended by a
  second concurrent session. This task MUST NOT touch that file.

## Preconditions and dependencies

- No dependency on `work/roadmaps/CAPABILITY_CHECKLIST.md` existing yet — this
  doc's text is written to make sense whether or not that file has landed,
  and to fail gracefully (a session cross-checks against real code/tests
  instead) if it hasn't.
- No dependency on the `MODEL_CAPABILITY_ROUTING.md` work.

## Change boundary

### MAY CHANGE

- `playbook/PROGRAM_STEERING.md` (new file);
- `playbook/INDEX.md` (one new table row, in the existing table shape, placed
  near `AGI_STANDARD.md`/`TASK_LIFECYCLE.md`/`REPAIR_AND_LEARNING.md`);
- `work/tasks/program-steering-protocol.md` (this file);
- `work/reviews/pr-<N>-review-evidence.md` (created by the independent
  reviewer, not by this task's owner).

### MUST NOT CHANGE

- `work/roadmaps/CAPABILITY_CHECKLIST.md` (owned by a concurrent session; may
  not exist yet — do not create it);
- `playbook/MODEL_CAPABILITY_ROUTING.md` (owned by a concurrent session);
- any other playbook, runtime, schema, or test file;
- any other task or review record.

## Decision authority

FOUNDRY may choose exact wording, structure, and normative-language phrasing
of `PROGRAM_STEERING.md` to match existing playbook tone, provided it covers
the five required elements listed in acceptance criteria. FOUNDRY may not
invent new severity tiers beyond `REPAIR_AND_LEARNING.md`'s existing table,
change AGI_STANDARD.md's fields, or claim `CAPABILITY_CHECKLIST.md` exists/has
specific content it has not verified.

## Acceptance criteria

- [x] `playbook/PROGRAM_STEERING.md` exists and states, using MUST/SHOULD/MAY
      normative language matching `AGI_STANDARD.md`'s style, when the check
      runs: before starting self-selected work, explicitly naming the
      "`gh issue list --state open` returns empty" trigger as the most
      important case.
- [x] The doc gives a short, concrete series of self-check questions covering:
      (a) does the candidate task trace to a NOT STARTED / IN PROGRESS entry
      in `work/roadmaps/CAPABILITY_CHECKLIST.md` or an explicit operator
      request — and if neither, that gap MUST be named in the task doc's own
      inputs/reasoning section rather than silently assumed reasonable; (b) is
      this task closing an issue by documenting already-shipped behavior
      instead of building something new — named as a specific smell,
      legitimate sometimes but must be called out as exactly that; (c) has the
      checklist itself been cross-checked against real merged state recently,
      or is it plausibly stale — if stale, re-verify the specific item against
      code/tests before trusting its label.
- [x] The doc includes a "drift smell list" naming at least: easiest-task
      bias over highest-value task, treating zero open issues as zero
      available work, documenting already-working behavior instead of
      building unimplemented behavior, re-deriving "what's next" from scratch
      instead of consulting the checklist, and scope creep beyond a task
      doc's own change boundary.
- [x] The doc states what to do when drift is caught (self- or
      operator-caught): name it plainly in the current handoff/task doc,
      redirect to the traced-back item, and cross-reference
      `playbook/REPAIR_AND_LEARNING.md`'s severity table for whether a repair
      record is warranted — without duplicating that table's content.
- [x] The doc explicitly cross-references `playbook/AGI_STANDARD.md`, framing
      itself as the complementary "is this the right task" check to
      AGI_STANDARD's "is this task clear" check.
- [x] `playbook/INDEX.md` gains exactly one new row for
      `playbook/PROGRAM_STEERING.md` in the existing table format/column
      shape, placed so it reads naturally alongside the other task-shaping /
      lifecycle rows.
- [x] No other file is touched.

## Verification

- Manual read-through confirming all five required elements are present and
  concrete (not vague filler): trigger, self-check questions, drift smell
  list, corrective action, cross-references.
- `git diff --stat` against `main` shows only the three files listed under
  MAY CHANGE.
- Independent review (see below) confirms the doc is genuinely actionable
  and its cross-references are correct.

## Review requirement

Independent review required (SENTINEL-style, zero prior context, bound to the
exact PR head SHA), written to
`work/reviews/pr-<N>-review-evidence.md`. FOUNDRY (task owner/author) must not
self-certify. `scripts/check_review_evidence.py <N>` and the `review-evidence`
required CI check must pass before merge.

## Stop / escalation conditions

- If `work/roadmaps/CAPABILITY_CHECKLIST.md` or
  `playbook/MODEL_CAPABILITY_ROUTING.md` show uncommitted/conflicting
  concurrent edits at push time, stop and report rather than force a merge —
  do not touch those files to resolve it.
- If independent review returns CHANGES_REQUESTED, address the named findings
  in a new commit on the same branch/PR; do not merge over an unresolved
  finding.
- If CI (`test` or `review-evidence`) fails for a reason unrelated to this
  change, stop and report rather than modifying unrelated CI config.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `NOT APPLICABLE` — session-local, single-PR docs task.
