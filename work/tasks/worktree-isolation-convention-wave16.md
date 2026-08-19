# Task: Worktree isolation convention (E6 / 6.16)

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `DOCS`
- Owner: `Claude / docs agent`
- Risk: `LOW`
- Goal: formalize, as a playbook convention, the ad-hoc git-worktree-per-agent
  mitigation this session developed after hitting the E6/6.16 promotion
  trigger ("shared-worktree collisions become a material risk") for real —
  document the rule, the proven recipe, the branch-behind-`main` merge-commit
  wrinkle, and the empty-commit sharp edge — and update the roadmap checklist
  rows to reflect that the trigger has fired and the workflow-level
  convention is documented and in active proven use.

## Inputs and source of truth

- `migration/FUTURE_IDEAS_BACKLOG.md` lines 1331-1401 ("P1 — Git worktree
  isolation for parallel coding") — the existing, already-designed "Smallest
  Lean version" this task formalizes; its "Hard boundaries" section is the
  authority for what this task must NOT introduce (no new merge authority, no
  new schema/authority system).
- `work/roadmaps/agent-harness-capabilities/03-environment-and-reproducibility.md`
  E6 phase text (lines ~632-637) and its Target/exit-gate text in
  `work/roadmaps/00-MASTER-MAPS-CAPABILITY-ROADMAP.md` section 6.16
  (lines ~913-928).
- `work/insights/2026-08-19-check-review-evidence-py-s-head-sha-walk-back-stops-silently-INSIGHT-29a10ad4.md`
  and `work/notes/2026-08-19-roadmap-trajectory-check.md`'s "Shared-worktree
  collisions between concurrent sessions" and "Review-evidence mechanics
  friction, twice" bullets — the recorded evidence that the trigger fired and
  the recurring wrinkles this doc needed to cover.
- `work/notes/2026-08-19-harness-production-wiring-gap.md` — read for this
  repo's current expected structure/rigor for a note-plus-formalization task
  (used as a rigor reference, not a structural template — that role is filled
  by `work/tasks/harness-production-wiring-gap-wave14.md` below).
- `playbook/HELPERS_AND_COMMUNICATION.md` — closest existing structural
  template for the new doc; read in full before deciding fold-in vs.
  new file.
- `scripts/check_review_evidence.py` — read in full for the exact
  merge-commit/empty-commit walk-back mechanics documented in the new doc.

## Change boundary

- MAY CHANGE: `playbook/WORKTREE_ISOLATION.md` (new file),
  `playbook/INDEX.md` (one new row), `playbook/HELPERS_AND_COMMUNICATION.md`
  (one new cross-reference section), `work/roadmaps/CAPABILITY_CHECKLIST.md`
  (E6 and 6.16 rows only), this task file.
- MUST NOT CHANGE: any `runtime/*.py` file, any `tests/*.py` file, any other
  row in `CAPABILITY_CHECKLIST.md`, `work/roadmaps/00-MASTER-MAPS-CAPABILITY-ROADMAP.md`
  or `03-environment-and-reproducibility.md` (phase text is read, not edited
  — E6's own definition is not changed by this task, only the checklist's
  status tracking of it).
- OPERATOR APPROVAL REQUIRED: none — docs-only change with no code, schema,
  or authority-system addition.

## Decision: new file vs. folding into `HELPERS_AND_COMMUNICATION.md`

Decided: **new file** (`playbook/WORKTREE_ISOLATION.md`), cross-referenced
from `HELPERS_AND_COMMUNICATION.md` rather than folded in.

Reasoning: `HELPERS_AND_COMMUNICATION.md` is about the helper-management
relationship itself — when to spawn one, what to record before spawning,
communication/escalation rules, when to stop one. It is short and
deliberately general-purpose across every kind of helper task (research,
review, summarization, implementation). Worktree isolation is a specific,
mechanical git procedure that applies only to writable-repo-work helpers,
and it needed: an exact command recipe, a worked example of the
merge-commit/`head_sha` rebind procedure, and a distinct sharp-edge warning
about empty commits. That content is long enough and specific enough (git
mechanics, not helper-relationship policy) that folding it into
`HELPERS_AND_COMMUNICATION.md` would have roughly tripled that doc's length
and mixed two different kinds of guidance (relationship policy vs. git
procedure) in one file. A short cross-reference section was added to
`HELPERS_AND_COMMUNICATION.md` instead, so a reader following the existing
doc's normal path still finds the new one.

## Decision: no helper script added

Decided: **no helper script** (e.g. `scripts/dispatch_worktree.sh`) was
added. The proven recipe is already three commands (`git fetch`,
`git worktree add ... -b ... origin/main`, `git worktree remove ... --force`)
with no error-prone flags or branching logic; a wrapper script would save at
most one line of typing per invocation while adding a new file to maintain,
document, and keep in sync with the doc's recipe if the recipe ever changes.
The dispatch mechanism in practice is prompt text given to each spawned
agent (per this task's own dispatch instructions), not a shared script
invocation site — a wrapper script has no natural caller to install itself
into without inventing one, which would be scope creep beyond a docs task
per this task's own explicit instruction not to build a project-management
CLI. If a real caller (e.g. a dispatch-automation layer) is ever built, a
wrapper becomes worth reconsidering then.

## Acceptance criteria

- [x] `playbook/WORKTREE_ISOLATION.md` states the rule plainly (worktree per
      writable dispatched agent; never mutate shared checkout branch state;
      remove worktree when done).
- [x] It gives the exact recipe used this session (`git fetch origin main`,
      `git worktree add /tmp/<name> -b <branch> origin/main`, work from
      inside that path, `git worktree remove /tmp/<name> --force` only after
      push/PR succeeds).
- [x] It covers the branch-behind-`main` merge-commit wrinkle with a
      concrete worked example: creating the merge commit, diffing the
      reviewed files across it (`git diff <old-head> <new-head> --stat --
      <reviewed files>`), and rebinding `head_sha` with a `rebase_note`
      field.
- [x] It covers the empty-commit sharp edge (`check_review_evidence.py`'s
      walk-back requires each trailing commit's own diff to be non-empty to
      treat it as skippable) and the fix (bind `head_sha` to that exact
      commit rather than walking further back).
- [x] `playbook/INDEX.md` has a new row pointing to the doc.
- [x] `work/roadmaps/CAPABILITY_CHECKLIST.md`'s E6 and 6.16 rows are updated
      from `NOT STARTED` to `IN PROGRESS`, with evidence citations and an
      honest statement of what remains unclosed (no `runtime/` code, no
      base-revision-bound-to-run-manifest linkage).
- [x] No `runtime/*.py` or `tests/*.py` file is touched.
- [x] Fold-in-vs-new-file and helper-script decisions are recorded with
      reasoning (this file, above).

## Verification and evidence

This is a `DOCS` task; no Python test suite is required or run.

- `git diff --stat` against `origin/main` (performed from inside the
  isolated worktree used for this task, not the shared checkout) confirms
  only the files listed in "Change boundary" changed — no `runtime/` or
  `tests/` file appears.
- The new doc's worked example commands (`git diff <a> <b> --stat --
  <files>`) were checked against `scripts/check_review_evidence.py`'s actual
  walk-back implementation (`_reviewed_code_head`, lines ~44-72) — the
  described merge-commit-stops-the-walk and empty-commit behavior match the
  script's real logic, not a guessed description of it.
- This task itself was executed inside an isolated worktree
  (`/tmp/worktree-isolation-doc-worktree`, branch
  `playbook/worktree-isolation-convention-wave16`), practicing the exact
  convention it documents.

## Conditional execution rules

- N/A — single-pass documentation task with no branching execution paths.

## Stop / escalate

- Would escalate if the backlog doc's "Hard boundaries" section had implied
  a new schema/authority mechanism was required — it does not; the smallest
  Lean version is explicitly workflow-shaped, which is what this task
  delivers.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS` — the recipe, the merge-commit wrinkle, and the
  empty-commit edge case are each grounded in this session's actual recorded
  incidents (`work/insights/`, `work/notes/2026-08-19-roadmap-trajectory-check.md`)
  and in direct reads of `scripts/check_review_evidence.py`, not invented.
- Scope Test: `PASS` — change boundary is docs plus two checklist rows; no
  `runtime/`/`tests/` file touched.
- Authority Test: `PASS` — the new doc explicitly states worktree isolation
  does not grant merge authority and does not change task ownership/review
  routing, matching the backlog doc's "Hard boundaries."
- Completion Test: `PASS`
- Failure Test: `PASS` — the checklist update honestly states what remains
  open (no code-level E6 closure).
- Continuation Test: `PASS` — checklist row's remaining-work note names the
  unclosed half explicitly for a future task to pick up.

## Notes / decisions

- E6/6.16 status set to `IN PROGRESS`, not `DONE`: the phase's exit gate
  ("concurrent writable runs do not share mutable worktree state") is met at
  the workflow/convention level (proven in use this session) but the
  broader phase text (`EnvironmentSpec`/`HarnessAdapter`-integrated base
  revision binding, automated enforcement) is not implemented in code, so
  `DONE` would overstate this task's scope.
- No new schema table, lock mechanism, or authority system was added,
  matching the backlog doc's explicit "Hard boundaries" (worktree isolation
  MUST NOT imply merge authority; must integrate with existing task
  ownership/review independence/recovery-cleanup, not replace them).

## Completion / handoff

- Completed: `playbook/WORKTREE_ISOLATION.md`, `playbook/INDEX.md` row,
  `playbook/HELPERS_AND_COMMUNICATION.md` cross-reference,
  `CAPABILITY_CHECKLIST.md` E6/6.16 rows, this task file.
- Not completed / explicitly out of scope: any `runtime/` code for
  worktree-per-run enforcement or base-revision-to-run-manifest binding
  (left for a future task if/when the code-level half of E6 is picked up);
  a helper script (decided against, reasoning above).
