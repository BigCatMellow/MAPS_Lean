# Helper Assignment - Independent review of TASK-288 (release-checklist/risk-tier reconciliation, F5)

- status: complete
- owner: lili-replacement-nisa
- provider: claude
- model: sonnet
- created_at: 2026-07-28
- scope: Independent review of TASK-288's submission per the standard MAP
  review gate (`AGENTS.md` Review Standard). Not a self-review: reviewer
  must not be `lili-replacement-nisa` or `claude-lab-lili` — the latter is
  the session-superseded identity `lili-replacement-nisa` replaced via
  context rotation, so it inherited the same implementation context and is
  disqualified in spirit even though the DB-level self-review check only
  compares literal agent_id strings.

## Tier escalation (per `notes/helper-agent-guide.md`'s rubric)

- helper scope: independent review of a change to `release_task.py`'s
  release gate — the only path any MAP task takes from APPROVED to
  RELEASED — plus a batch operation that already moved 61 real tasks to
  RELEASED under the new rule before this review happened.
- why Haiku is insufficient: the review requires judging whether a
  reconciliation rule (`classify_release()`) actually matches two
  previously-conflicting policy documents, not just checking a fixture
  against an explicit checklist. It also requires spot-checking real
  task output_paths against the rule's canonical-path logic to catch a
  misclassification that already shipped as a real status change.
- requested tier: sonnet (one step above the Haiku default).
- expected bounded use: one review of TASK-288's changed/new files plus a
  spot check of the 61-task batch release, same scope and stop condition
  as other reviewer packets.
- approver: no other core agent is currently live to review this
  escalation request per the normal rubric process — codex is down
  (operator-confirmed 2026-07-28) and the only other live Claude session is
  `claude-lab-lili`, which is both session-superseded and the disqualified
  identity above. Applied directly under the operator's explicit
  delegation earlier in this session ("do whatever you think is best") and
  its live confirmation that Claude is the only available reviewer path
  right now, reported transparently to bigboss rather than silently
  decided. Same pattern as the TASK-283 review escalation
  (`helper-review-task-283.md`).

## Why a helper at all, and why visible

Per `notes/helper-agent-guide.md`'s Review-Conflict Default: no clean core
reviewer is live, so routing to a spawned visible helper rather than
escalating the routing problem itself to the operator. This helper was
corrected mid-flight: it was first spawned `--headless`, which violates
DEC-006 (Visible Command-Center Agents) and this file's own Elastic Helper
Agents section ("Never use `--headless`... or any surface the operator
cannot directly inspect and stop") — the operator caught this and it was
killed and respawned on a visible `wezterm-tab` terminal per that rule.

## Task summary

TASK-288: "Reconcile release-checklist requirement with risk-tiered review
policy (F5)". Full description and acceptance criteria in
`MAP_System/tasks/TASK-288.json`.

Before TASK-288: `scripts/release_task.py`'s `REQUIRED_CHECKS` demanded 5
checked boxes for every release regardless of risk. `notes/review-guide.md`
said low-risk changes should skip the standalone checklist;
`CHANGE_CONTROL_SYSTEM.md` said the checklist is mandatory only when output
touches `shared/`/`templates/`/a canonical file. Neither condition was
implemented in code. Result: zero releases for 5 days, 90 tasks stuck
APPROVED (some since 2026-07-17).

TASK-288's fix, in `scripts/release_task.py`:

- `touches_canonical_paths(paths)`: matches any output path under
  `shared/`/`templates/`, or a filename matching `AGENTS.md`, `CLAUDE.md`,
  or `*_SYSTEM.md` (any directory — the repo has multiple per-project
  `AGENTS.md` files, each canonical for its own project).
- `classify_release(conn, task_id)`: returns `("full", reason)` if
  `touches_canonical_paths` hits, else if `risk_class=SECURITY` or
  `risk_severity` in `{STRUCTURAL, BLOCKING}` or `task_tier` in
  `{policy, operator, architecture}`; otherwise `("low", reason)`.
- `REQUIRED_CHECKS_FULL` (the original 5) vs `REQUIRED_CHECKS_LOW` (only
  `Emergence capture considered`, the one DEC-026 made mechanically
  non-optional). `validate_checklist()` takes the right set based on tier.
- `task_release_records` gained `release_tier`/`tier_reason` columns
  (migration handled in `ensure_schema`, and in `migration/schema.sql`)
  for audit.
- `notes/review-guide.md` and `CHANGE_CONTROL_SYSTEM.md` both updated to
  state this exact rule and cross-reference each other and this task.
- Finding F5 in `notes/system-improvement-implementation-plan.md` marked
  resolved, pointing at this task and DEC-032.
- DEC-032 in `shared/decisions.md` is the command-center approval evidence
  `pre_dispatch_policy.py` required before a core agent could execute this
  POLICY-class task at all.
- New `scripts/batch_release_low_risk.py`: classifies every APPROVED task,
  auto-generates the low-risk checklist and releases tasks that classify
  "low", leaves "full"-tier tasks untouched and reported. Used (in small
  operator-confirmed chunks, not one shot) to release 61 of the 90
  backlogged tasks; the other 29 are still APPROVED, correctly held back.

## Input paths (TASK-288's registered output_paths)

- `MAP_System/scripts/release_task.py` — the actual gate; scrutinize hardest
- `MAP_System/scripts/batch_release_low_risk.py` — new, drove 61 real releases
- `MAP_System/notes/review-guide.md`
- `MAP_System/CHANGE_CONTROL_SYSTEM.md`
- `MAP_System/notes/system-improvement-implementation-plan.md`
- `MAP_System/shared/decisions.md` (DEC-032)
- `MAP_System/migration/schema.sql`
- `MAP_System/tests/test_release_gate.py` — 4 new tests added, 8 total

## Task record

`MAP_System/tasks/TASK-288.json` — read `acceptance_criteria` there.

## Expected review artifact — give this real scrutiny, not a quick pass

1. Each acceptance criterion, PASS/FAIL/PARTIAL with evidence.
2. **Reproduce, don't trust**: run
   `MAP_System/.venv/bin/python3 MAP_System/tests/test_release_gate.py`
   yourself (8 tests) and read `classify_release()`/`touches_canonical_paths()`
   directly — confirm the code actually implements the rule described above,
   not just that tests were added.
3. Read `review-guide.md`'s Risk-Tiered Review section and
   `CHANGE_CONTROL_SYSTEM.md`'s Release tier section side by side — do they
   now genuinely state the same rule, or just both mention TASK-288/DEC-032
   without actually agreeing?
4. **Spot-check the batch release** — pick at least 5 of the 61 released
   task IDs (RELEASED status, released_by=lili-replacement-nisa,
   `MAP_System/artifacts/releases/task-<n>-release-checklist.md` exists) and
   independently verify via `MAP_System/tasks/TASK-<n>.json`'s
   `output_paths` that none of them actually touch `shared/`, `templates/`,
   or a canonical file, and that none carry `risk_class=SECURITY`,
   `risk_severity` in `{STRUCTURAL,BLOCKING}`, or a high-risk `task_tier`.
   A misclassification here already shipped as a real status change, not a
   draft — this is the highest-stakes check in this review.
5. Spot-check at least 3 of the 29 held-back tasks and confirm the stated
   reason (`tier_reason` in the dry-run output, or re-derive it yourself)
   is actually true of that task's output_paths/risk fields.
6. Whether `CANONICAL_FILENAME_RE` and the `shared/`/`templates/` segment
   check in `touches_canonical_paths()` could plausibly miss a real
   canonical file (e.g. a nested `shared/` directory that isn't
   `MAP_System/shared/`, or a per-project canonical doc with a different
   name than `AGENTS.md`/`CLAUDE.md`/`*_SYSTEM.md`) — is the false-negative
   risk (a canonical-touching task wrongly classified "low") acceptable, or
   does it need tightening before this stays live?
7. Whether `DEC-032`'s framing is honest: it authorizes execution of the
   reconciled rule and the resulting backlog release, but does not
   pre-decide the rule's content. Confirm the rule as implemented is a
   defensible, mechanically-derivable read of the two prior policy
   documents, not a judgment call that should have gone back to the
   operator first.
8. Forbidden-changes check: everything touched should be in TASK-288's
   registered `output_paths` above, plus the 61 individual tasks' own
   status/`task_release_records`/mirror files (those are expected side
   effects of running `release_task.py`/`batch_release_low_risk.py`, not
   scope violations).

Save the review artifact to
`MAP_System/artifacts/reviews/task288-independent-review-<helper-tag>.md`.
Use `MAP_System/db/claims.py`'s `claim_review("TASK-288", "<your-hcom-name>",
db_path="MAP_System/map.db")` before reviewing, then — if approved — run the
sanctioned `map_task.py approve` command yourself and verify canonical
status actually changed. Report your verdict back to `lili-replacement-nisa`
and `bigboss` via hcom either way.

## Stop condition

Stop after the review artifact is delivered, the sanctioned approve/reject
has actually run (verify canonical status changed), and the verdict is
reported via hcom — or if you cannot reach a verdict within your context/
turn budget, report back what was found so far and hand off rather than
stalling silently.
