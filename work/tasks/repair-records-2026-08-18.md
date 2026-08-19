# Task: file repair records for three 2026-08-18 incidents

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `REPAIR`
- Owner: `Claude / repair-records agent`
- Risk: `LOW`
- Goal: file `work/notes/` repair records (per `playbook/REPAIR_AND_LEARNING.md` and
  `templates/repair-record.md`) for three real DRIFT-severity incidents observed during this session on
  2026-08-18, and, where a countermeasure is not already established, propose (not implement) a durable
  next step per that playbook's "if a failure repeats, add a durable countermeasure" rule.

## Note on this task file's Type

No prior task doc in `work/tasks/` is scoped purely to filing a repair record (the closest precedent,
`work/notes/2026-08-18-stalled-dispatched-worker-repair.md`, was filed directly without its own task doc).
Existing `Type` values in use (`IMPLEMENTATION`, `ARCHITECTURE`, `EVALUATION`, `RESEARCH`, `MAINTENANCE`,
`PLANNING`, `documentation / information architecture`) don't have an exact fit for "the deliverable is a
repair record, not code or a design." `REPAIR` is used here as the most accurate label, tying directly to
`playbook/REPAIR_AND_LEARNING.md`'s own triage vocabulary, rather than overloading `IMPLEMENTATION` (nothing
is implemented -- the countermeasure proposals are explicitly deferred) or `documentation / information
architecture` (this isn't restructuring docs, it's recording incidents). This establishes the convention for
future repair-record-only task docs rather than following an existing one.

## Inputs and source of truth

- `playbook/REPAIR_AND_LEARNING.md` -- severity triage table, repair-note requirements, and the "if a failure
  repeats, add a durable countermeasure" rule this task's proposals are scoped against.
- `templates/repair-record.md` -- the record shape used for both new files.
- `work/notes/2026-08-18-stalled-dispatched-worker-repair.md` -- prior repair record for the same
  dispatched-worker-stall pattern; its "Prevention" section's flagged residual gap is the direct antecedent
  for incident 1.
- `work/coordination/README.md`'s "Stalled-work triage" section (added PR #95) -- the existing countermeasure
  incident 1 shows is necessary-but-not-sufficient.
- `work/tasks/context-builder-skill-integration-s6.md` and PR #109 (`gh pr view 109 --json commits`) -- live
  evidence for both incident 1 (dispatch-attempt stalls on this task) and incidents 2/3 (four review-evidence
  commits interleaved with three main-sync merges on the same PR).
- `playbook/MODEL_CAPABILITY_ROUTING.md` (added 2026-08-18, PR #103) -- effort-level routing section incident 3
  is framed against.

## Records filed

1. `work/notes/2026-08-18-dispatched-worker-stall-recurrence.md` -- the PR #95 countermeasure (manual
   GitHub-check triage habit) caught three dispatched-worker stalls on the S6/PR #109 task today, including two
   after an explicit "run tests in the foreground" prompt instruction, one of which used a wait/monitor
   construct anyway. Proposes (STRUCTURAL, not implemented here): dispatched-worker task briefs state an
   expected max duration, and the *dispatching* session schedules an active, mechanical check-in at that
   duration rather than relying on the worker's own completion signal or a prompt instruction alone.
2. `work/notes/2026-08-18-review-evidence-resync-classifier-friction.md` -- combines incidents 2 and 3. The
   auto-mode self-approval classifier flagged genuinely-independent re-reviews on PR #109 (shared bot identity
   is this repo's sanctioned review-evidence convention, not self-certification) on two of four review-evidence
   passes, all forced by `main` outpacing the review-evidence-then-merge cycle under strict branch protection.
   Explicitly does not propose loosening the classifier (already rejected this session). Proposes (not
   implemented here): a merge-queue/serialization convention for concurrent sessions landing against a
   fast-moving `main`, plus a minor observation that a zero-diff-confirmed re-review is a lower-effort routing
   case than a first-pass review per `MODEL_CAPABILITY_ROUTING.md`.

## Change boundary

- MAY CHANGE: the two new `work/notes/*.md` files above, this task file.
- MUST NOT CHANGE: any runtime code, the self-approval classifier, `work/coordination/README.md`,
  `playbook/MODEL_CAPABILITY_ROUTING.md` -- this task records incidents and proposals only; no countermeasure
  is implemented by this PR.
- OPERATOR APPROVAL REQUIRED: adopting either STRUCTURAL proposal named in the records above (dispatch
  check-in scheduling; merge-queue/serialization convention) is out of scope for this PR and would need its own
  task + review if taken up.

## Decision authority

Docs-only, `Risk: LOW`. No structural change is applied; both structural proposals are explicitly named as
proposals per `playbook/REPAIR_AND_LEARNING.md`'s "Structural: do not silently apply; use a decision/change
path" rule.

## Verification

- Both repair records cite live, checkable evidence: PR #109's actual commit hashes and timestamps (via `gh pr
  view 109 --json commits`), and the S6 task doc's existence/content.
- An independent SENTINEL review (fresh zero-context agent) verifies the records' claims against real PR #109
  history and the prior repair record before this PR merges, per repo convention.
