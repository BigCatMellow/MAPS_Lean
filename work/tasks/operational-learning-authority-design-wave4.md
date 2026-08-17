# Task: operational learning authority design Wave 4

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `ARCHITECTURE`
- Owner: `agent/operational-learning-authority-wave4`
- Risk: `MEDIUM`
- Goal: Answer the five unresolved operational-learning questions named in the
  2026-08-16 reconciliation checkpoint — canonical storage, promotion/retirement
  authority, expiry/supersession mechanics, applicability conflict/precedence,
  and safe context injection — with a staged, smallest-safe-next-step proposal
  for each, and an explicit split of what this task can decide versus what
  requires an operator decision. No runtime change is authorized.

## Inputs and source of truth

- Inputs:
  - root `AGENTS.md`, especially the negative operating contract (do not make
    material assumptions; ask rather than guess) and the authority/ownership
    section;
  - `runtime/operational_learning.py` at current `main` head (PR #43, merged) —
    `validate_lesson_record()` and `project_applicable_lessons()`, read in full;
  - `runtime/outcome_lesson_candidate.py` at current `main` head (PR #60,
    merged) — `build_outcome_lesson_candidate()`, read in full;
  - `work/tasks/operational-learning-projection-wave3.md` and
    `work/tasks/outcome-lesson-candidate-wave3.md` (original task framing and
    stated non-goals for #43/#60);
  - `work/roadmaps/00-MASTER-MAPS-CAPABILITY-ROADMAP.md` §4 non-negotiable
    architecture laws (4.1 one fact one authority, 4.2 capability is not
    authority, 4.6 durable state needs lifecycle, 4.8 no self-authorizing
    refinement), §6.30 Operational learning lifecycle, and Wave 6 (§"Wave 6 —
    Controlled operational learning and harness refinement") including its
    absolute non-goal;
  - `work/roadmaps/current-capability-reconciliation-2026-08-16.md` §4.5
    Operational learning and §9 Bounded next planning questions (the exact
    named gap this task answers);
  - `runtime/state/schema.sql`, read for house style only (`run_helper_links`,
    `run_recovery_links`, `run_environment_evidence`) — immutable-by-default
    append-only relationship tables with explicit `BEFORE UPDATE`/`BEFORE
    DELETE` triggers that `RAISE(ABORT, ...)`;
  - `work/tasks/communication-task-run-join-wave3.md` and
    `work/notes/2026-08-15-communication-task-run-join-design.md` (PR #51) as
    the format/rigor model for this same kind of design-only task.
- Authoritative sources: merged `runtime/operational_learning.py` and
  `runtime/outcome_lesson_candidate.py` are authoritative for what already
  exists. The master roadmap and the 2026-08-16 reconciliation doc are
  authoritative for target end-state and the exact open questions. Prose
  summaries (including this file) are navigation only, never stronger than the
  source they cite.
- Evidence labels: everything in this document is `ASSUMED`/proposal unless
  marked `VERIFIED` against the files above. Where the reconciliation doc names
  a genuinely open operator decision, this document keeps it `UNKNOWN` /
  `OPERATOR DECISION REQUIRED` rather than resolving it for expedience.
- Dependencies / preconditions: none beyond merged #43/#60. This task
  deliberately does not depend on A1/A2/A3 execution-lineage work, #44/#45
  communication lineage, or #41/#53 Context Builder v2 evaluation — those are
  separate open stacks and are not touched here.

## Change boundary

- MAY CHANGE:
  - `work/tasks/operational-learning-authority-design-wave4.md` (this file)
  - `work/notes/2026-08-17-operational-learning-authority-design.md`
- MUST NOT CHANGE:
  - `runtime/operational_learning.py`
  - `runtime/outcome_lesson_candidate.py`
  - `runtime/state/schema.sql`
  - any other runtime file
  - any other agent's branch
  - any existing task/note file
- MAY CHANGE IF NECESSARY: none. Any schema/API sketch in the note is prose /
  fenced code inside the design doc, not a runtime edit.
- OPERATOR APPROVAL REQUIRED: promotion/retirement authority model selection;
  automatic-promotion evidence gates (if any); applicability conflict
  precedence policy; the actual injection boundary between "another Context
  Builder source" and anything stronger. See Decision authority below and the
  note's per-section "Operator decision required" callouts.

## Decision authority

Owner (this task) may decide:

- which of the five areas can be staged into a smallest-safe-next-step versus
  which sub-parts are pure open policy;
- the shape of an illustrative (non-binding) SQLite schema sketch, following
  existing `runtime/state/schema.sql` house style, for canonical lesson
  storage — as design prose, not a schema-file edit;
- how conflict/precedence *detection* could work mechanically (this is
  evidence surfacing, not itself an authority grant);
- how expiry/supersession *mechanics* could work without deciding who is
  allowed to promote in the first place;
- the recommended minimal next implementation task boundary, if/when an
  operator decision unblocks it.

Owner must not decide (this task explicitly declines to resolve, and instead
frames as an operator decision):

- who or what mechanism is allowed to promote a `CANDIDATE` lesson to `ACTIVE`,
  or retire an `ACTIVE` lesson — operator-only-every-time vs. bounded
  automatic promotion under evidence gates vs. a hybrid;
- whether any role (TOWER/ANVIL/FOUNDRY/SENTINEL/SWITCHYARD) gains a new
  "policy promotion" authority by default;
- how applicability conflicts between two ACTIVE lessons are ultimately
  resolved when detection alone is insufficient (silent precedence rule vs.
  mandatory operator surfacing);
- whether lesson guidance is ever allowed to be anything stronger than another
  Context Builder evidence source (i.e., whether it may ever become
  injected instruction text rather than advisory, cited evidence);
- exact operator-visible review cadence/interface for `REVIEW_DUE` lessons.

## Acceptance criteria

- [x] `runtime/operational_learning.py` and `runtime/outcome_lesson_candidate.py`
      read in full and their exact existing behavior (validation/projection
      only, no persistence, no mutation, no promotion) is stated correctly.
- [x] Canonical storage question answered with a concrete schema sketch in the
      existing `TaskStore`/`schema.sql` house style (append-only, trigger-enforced
      immutability), explicitly rejecting a second mutable database per the
      "one fact, one authority" law.
- [x] Promotion/retirement authority question is answered as a set of real
      options with tradeoffs, explicitly not resolved by this task.
- [x] Expiry/supersession lifecycle mechanics are designed concretely,
      distinguishing what can be mechanical (trigger/scheduled check) from what
      needs the same authority as promotion.
- [x] Applicability conflict/precedence is reasoned about against the "do not
      infer from probably" rule rather than asserted, and a smallest-safe
      detection-first proposal is given.
- [x] Safe context injection is designed as an evidence source analogous to
      Context Builder's existing evidence surfacing, tied explicitly to
      roadmap law 4.2 ("capability is not authority") and the Wave 6 non-goal.
- [x] Each of the five areas has a staged, smallest-safe-next-step proposal
      (not a finished implementation) mirroring PR #51's design rigor.
- [x] A "Decision authority" section explicitly separates owner-decidable
      design questions from operator-required policy questions.
- [x] Only the two declared files are changed; no runtime/schema file is
      touched.

## Verification and evidence

- Verification: manual re-read of `runtime/operational_learning.py`,
  `runtime/outcome_lesson_candidate.py`, `runtime/state/schema.sql`
  (`run_helper_links`/`run_recovery_links`/`run_environment_evidence`), the
  master roadmap §4/§6.30/Wave 6, and the reconciliation doc §4.5/§9, cross-checked
  against claims made in the note; `git status`/`git diff` confirms only the
  two declared files changed.
- Evidence to preserve: exact `main` head this branch was cut from, changed-file
  list, confirmation no schema/runtime file was touched.
- Review required: `INDEPENDENT_REVIEW` before this design becomes
  implementation authority for any future wave.

## Conditional execution rules

- Environment / target: planning/documentation only; no runtime execution.
- Ordered procedure: read AGENTS.md → read #43/#60 in full → read wave3 task
  docs → read roadmap §4/§6.30/Wave 6 → read reconciliation §4.5/§9 → read #51
  task+note as format model → read schema.sql house style → write task doc →
  write note doc.
- Failure branches: if any of the five areas cannot be staged without silently
  deciding an operator question, mark it `OPERATOR DECISION REQUIRED` in the
  note rather than picking an answer.
- Rollback / recovery: revert the two new files; no durable data exists to
  migrate.
- Security / privacy controls: N/A — no data handled beyond repository text
  already public in this branch.
- External side effects: none.
- Effort limit: design/prose and illustrative schema sketch only; no Python
  implementation beyond what fits as a fenced code block inside the note.
- Approved reference: PR #51 task+note pair as the structural/rigor model.

## Stop / escalate

Stop rather than guess if:

- an area cannot be staged without asserting who holds promotion/retirement
  authority — stop and label it an operator decision instead;
- a proposal would require touching `runtime/operational_learning.py`,
  `runtime/outcome_lesson_candidate.py`, or `runtime/state/schema.sql` to be
  concrete enough — stop and note it as a follow-up implementation task;
- the master roadmap or reconciliation doc appear to have changed underneath
  this task (re-check exact current `main` head before finalizing).

Escalate to: operator, for the promotion-authority and injection-boundary
decisions named above.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- This task deliberately produces no `promote()`/`retire()`/store function and
  no schema migration. The SQLite sketch in the note is illustrative design
  prose, matched to existing house style, not an authorized schema change.
- Five operator-decision flags are raised explicitly rather than folded into
  prose so a later task can pick them up without re-deriving this analysis.

## Completion / handoff

- Completed: five-area design doc with staged next-steps and explicit
  decision-authority split.
- Not completed: any runtime implementation, schema migration, or promotion
  mechanism; independent review.
- Current blocker: none for this bounded design tranche. Real forward progress
  on operational-learning persistence is blocked on explicit operator answers
  to the five flagged questions in
  `work/notes/2026-08-17-operational-learning-authority-design.md`.
- Next action if not DONE: obtain independent review of this design doc; once
  operator decisions land, shape a narrowly bounded Wave 5 implementation task
  for exactly the smallest-safe-next-step this note describes (not the whole
  lifecycle at once).
