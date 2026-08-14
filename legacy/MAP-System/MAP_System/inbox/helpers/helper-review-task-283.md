# Helper Assignment - Independent review of TASK-283 (scope contracts + retry budgets)

- status: complete
- owner: claude-lab-venu
- provider: claude
- model: sonnet
- created_at: 2026-07-27
- scope: Independent review of TASK-283's submission per the standard MAP
  review gate (`AGENTS.md` Review Standard). Not a self-review: reviewer
  must not be `claude-lab-venu` (submitter).

## Tier escalation (per `notes/helper-agent-guide.md`'s rubric)

- helper scope: independent review of a change to the live
  `pre_dispatch_policy.py` dispatch decision path — the function every real
  task dispatch in this workspace goes through.
- why Haiku is insufficient: `codex-lab-diro` (the intended core reviewer)
  explicitly declined and stated "this live dispatch-path review requires a
  fresh full-context reviewer" rather than just citing its own context-
  rotation unavailability. The prior four reviews today (TASK-281/282/285/286)
  were contained pilots explicitly not wired into live dispatch; this one
  edits the actual dispatch gate, so a misjudged approval has broader blast
  radius than any prior review this session.
- requested tier: sonnet (one step above the Haiku default).
- expected bounded use: one review of TASK-283's ~5 changed/new files, same
  scope and stop condition as every other reviewer packet today. Not an
  open-ended assignment.
- approver: no other core agent is currently live to review this escalation
  request per the normal rubric process (`codex-lab-diro` is the one that
  flagged the need and is unavailable; no other Codex/Claude core session is
  live). Applied directly under the operator's explicit delegation in the
  active chat turn on 2026-07-27 ("do whatever you think is best... not me
  holding hands"), reported transparently to bigboss rather than silently
  decided.

## Why a helper at all

Per `notes/helper-agent-guide.md`'s Review-Conflict Default: no clean core
reviewer is live, so routing to a spawned visible helper rather than
escalating the routing problem itself to the operator. What's escalated
here is only the model tier, given diro's explicit stakes assessment.

## Process notes from four prior reviews today

1. Do **not** use raw `git diff` against `git HEAD` to check forbidden
   changes. This repo has not committed since 2026-07-15/23; `git diff`
   shows unrelated cumulative work and produced a false-positive BLOCKER on
   an earlier review today for exactly this reason. Compare against the
   exact `output_paths` list in `MAP_System/tasks/TASK-283.json`, or check
   `stat` mtimes.
2. Review records need these exact section headers for
   `scripts/validate_review.py`: `## Verdict`, `## Acceptance Criteria Check`,
   `## Files Reviewed`, `## Forbidden Changes Check`.
3. An "LGTM" over hcom is not itself an approval — run the sanctioned
   `map_task.py approve` command yourself and verify canonical status
   actually changed.

## Task summary

TASK-283: "Enforce run path scope and retry budgets deterministically"
(final TASK-277 P2 roadmap item). Fresh, greenfield implementation, attempt
1/3. Full detail, design rationale, and the three-tier containment
distinction acceptance criterion 5 requires are all in the delivery note —
read that first: `MAP_System/artifacts/tests/task283-scope-budget-delivery-note.md`.

Short version: new `scripts/verify_run_scope.py` provides three checks —
(1) `validate_scope_contract()`, a dispatch-preflight self-consistency
check on a declared readable/writable/forbidden path contract; (2)
`verify_post_run_diff()`, a post-hoc detector of out-of-scope/forbidden
writes given a caller-supplied list of changed paths; (3)
`check_budget()`/`write_escalation_artifact()`, retry/runtime budget
exhaustion detection with a durable JSON escalation record. None of these
are genuine harness containment — nothing stops a worker from writing
outside scope or exceeding budget at the OS/process level, and the delivery
note says so explicitly. `pre_dispatch_policy.py` gains a new, **opt-in**
check: a task with a `scope_contract` field gets it preflight-validated;
invalid contracts are rejected for every tier above 0. A task with no
`scope_contract` (every real task currently in `map.db`) is unaffected.

## Input paths (output_paths registered to TASK-283, including two
re-registered from TASK-281 now that it's terminal)

- `MAP_System/artifacts/tests/task283-scope-budget-delivery-note.md`
- `MAP_System/scripts/pre_dispatch_policy.py` — **the live dispatch file;
  scrutinize this one hardest**
- `MAP_System/scripts/verify_run_scope.py` (new)
- `MAP_System/tests/test_run_scope.py` (new, 25 tests)
- `MAP_System/workflow/runtime_policy.yaml` — additive edit to an
  already-live, multi-consumer file
- `MAP_System/scripts/run_manifest.py` (re-registered from TASK-281)
- `MAP_System/migration/run_manifest_schema.sql` (re-registered from TASK-281)

## Task record

`MAP_System/tasks/TASK-283.json` — read `acceptance_criteria` there.

## Expected review artifact — give this real scrutiny, not a quick pass

1. Each acceptance criterion, PASS/FAIL/PARTIAL with evidence.
2. **Reproduce, don't trust**: confirm directly that
   `evaluate_pre_dispatch()` behaves identically before/after for a task
   with no `scope_contract` field — read the diff in `pre_dispatch_policy.py`
   yourself and trace the code path, don't just take the delivery note's
   word that the 25 pre-existing tests passing proves it (they're evidence,
   but read the actual insertion point too — right after the tier-0 early
   return, before any tier-specific branch).
3. Confirm `runtime_policy.yaml`'s new `scope_budget_contracts` section is
   genuinely inert to its four other consumers
   (`graph/runner.py`, `scripts/halt_state.py`,
   `scripts/multigate_regression_test.py`,
   `scripts/task_fingerprint_holdout.py`) — check what each one actually
   reads from the file, don't just trust the claim.
4. Independent verification: run
   `MAP_System/.venv/bin/python MAP_System/tests/test_run_scope.py` (25),
   `MAP_System/.venv/bin/python MAP_System/tests/test_run_manifest.py` (10),
   `MAP_System/.venv/bin/python MAP_System/tests/test_pre_dispatch_policy.py`,
   `MAP_System/.venv/bin/python MAP_System/tests/test_pre_dispatch_gate_inputs.py`,
   `MAP_System/.venv/bin/python MAP_System/tests/test_capability_whitelist.py`.
   All must pass, and the last three especially must show **no behavior
   change** for existing cases.
5. Whether the delivery note's containment-boundary claims (prompt guidance
   / preflight+post-run detection / no genuine harness containment) are
   honest given what's actually implemented — could a careless reader of
   `runtime_policy.yaml`'s `containment_level` field or the new task
   fields mistake this for real enforcement?
6. Whether the `ALTER TABLE` migration for `run_manifests` (readable_scope/
   forbidden_scope) is safe against a database that already has rows from
   TASK-281 — trace `run_manifest.py`'s `connect()` yourself, don't just
   trust `test_pre_existing_run_manifests_table_migrates_additive_columns`.
7. Forbidden-changes check using output-path/mtime comparison, not
   `git diff`.

Save the review artifact to
`MAP_System/artifacts/reviews/task283-independent-review-<helper-tag>.md`.
Use `MAP_System/db/claims.py`'s `claim_review("TASK-283", "<your-hcom-name>",
db_path="MAP_System/map.db")` before reviewing, then — if approved — run the
sanctioned `map_task.py approve` command yourself. Report your verdict back
to `claude-lab-venu` via hcom either way.

## Stop condition

Stop after the review artifact is delivered, the sanctioned approve/reject
has actually run (verify canonical status changed), and the verdict is
reported via hcom — or if you cannot reach a verdict within your context/
turn budget, report back what was found so far and hand off rather than
stalling silently.
