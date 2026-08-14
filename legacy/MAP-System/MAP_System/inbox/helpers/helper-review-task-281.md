# Helper Assignment - Independent review of TASK-281 (run manifests pilot)

- status: complete
- outcome: TASK-281 APPROVED (`REV-TASK-281-helper-review-task-281-tuna-4bf45bf0`, review-final: `MAP_System/artifacts/reviews/task281-independent-review-tuna.md`). Initial verdict was an erroneous REJECT/BLOCKER (git-diff-against-stale-HEAD methodology error, not a real forbidden-changes violation); corrected after evidence pushback (file mtimes), then a follow-up correction to make the review record's section headers match validate_review.py's canonical names before the sanctioned `approve` call would pass.
- owner: claude-lab-venu
- provider: claude
- model: haiku
- created_at: 2026-07-27
- scope: Independent review of TASK-281's submission per the standard MAP
  review gate (`AGENTS.md` Review Standard). Not a self-review: reviewer must
  not be `claude-lab-venu` (submitter) or `claude-lab-nora` (predecessor
  session this session replaced).

## Why a helper

`codex-lab-diro` ack'd the review request but cannot claim: it is at
mandatory context-rotation threshold (>150k) with a replacement pending.
No other clean core reviewer (Codex or Claude core session) is currently
live. Per `notes/helper-agent-guide.md`'s Review-Conflict Default, routing
to a spawned visible helper rather than escalating routing to the operator.

## Task summary

TASK-281: "Pilot immutable task revisions and minimal run manifests"
(TASK-277 P1 roadmap item). Fresh, greenfield implementation (attempt 1/3),
submitted and unclaimed. Standalone additive capability — does not touch
`graph/runner.py` or any shared dispatch code (not a registered output
path), so nothing changes in live task dispatch. Explicitly framed as a
bounded pilot; the delivery artifact itself says it does not authorize
production rollout.

## Input paths (output_paths registered to TASK-281)

- `MAP_System/artifacts/experiments/task281-run-manifest-pilot.md` (pilot
  report — read this first, it explains the design and the size
  measurement)
- `MAP_System/migration/run_manifest_schema.sql` (new, additive SQL schema;
  intentionally separate from `migration/schema.sql`)
- `MAP_System/scripts/run_manifest.py` (new script: `create`/`show`/
  `check-stale` over a new `run_manifests` table)
- `MAP_System/tests/test_run_manifest.py` (10 focused tests)
- `MAP_System/workflow/templates/run_manifest.json` (documentation template
  for the manifest shape)

## Task record

`MAP_System/tasks/TASK-281.json` — read `acceptance_criteria` there.

## Expected review artifact

A review record following `AGENTS.md`'s Review Standard (BLOCKER/REQUIRED/
RECOMMENDED/OPTIONAL severities), covering:

1. Each acceptance criterion in `TASK-281.json`, PASS/FAIL/PARTIAL with
   evidence.
2. Forbidden-changes check: confirm nothing outside the five registered
   output paths was touched, and specifically that `graph/runner.py` /
   `scripts/pre_dispatch_policy.py` were not edited (this pilot must not
   change live dispatch behavior).
3. Independent verification: run `MAP_System/.venv/bin/python
   MAP_System/tests/test_run_manifest.py` directly and confirm 10/10; spot-
   check at least one claim in the pilot report (e.g. that
   `run_manifest_context_refs` genuinely has no content column, or that
   `check_stale()` genuinely ignores a lifecycle-only task update) by
   reproducing it independently rather than trusting the delivery note.
4. Whether the `task_revision` hash's exclusion of lifecycle fields (status/
   owner/claimed_by/lease/attempt/timestamps) is the right boundary, or too
   broad/narrow.
5. Whether the pilot's non-production-rollout framing is credible given what
   was actually implemented (i.e., does anything here quietly become
   load-bearing for other tasks).

Save the review artifact to
`MAP_System/artifacts/reviews/task281-independent-review-<helper-tag>.md`.
Use `MAP_System/db/claims.py`'s `claim_review("TASK-281", "<your-hcom-name>",
db_path="MAP_System/map.db")` before reviewing (atomic open-review claim),
then report the verdict back to `claude-lab-venu` via hcom.

## Stop condition

Stop after the review artifact is delivered and the verdict is reported via
hcom, or if this helper cannot reach a verdict within its context/turn
budget — in that case, report back what was found so far and hand off
rather than silently stalling.
