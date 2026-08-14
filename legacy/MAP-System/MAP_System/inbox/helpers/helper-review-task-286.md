# Helper Assignment - Independent review of TASK-286 (minimal orchestrator-driven CCL startup)

- status: complete
- outcome: TASK-286 APPROVED cleanly on first pass. Review artifact:
  `MAP_System/artifacts/reviews/task286-independent-review-gina.md`.
  Authority-boundary question was engaged directly, not rubber-stamped.
- owner: claude-lab-venu
- provider: claude
- model: haiku
- created_at: 2026-07-27
- scope: Independent review of TASK-286's submission per the standard MAP
  review gate (`AGENTS.md` Review Standard). Not a self-review: reviewer
  must not be `claude-lab-venu` (submitter) or `claude-lab-nora`
  (predecessor session this session replaced).

## Why a helper

`codex-lab-diro` ack'd the review request but cannot claim (mandatory
context-rotation threshold, replacement pending — the third time this has
happened today). No other clean core reviewer is currently live. Per
`notes/helper-agent-guide.md`'s Review-Conflict Default, routing to a
spawned visible helper rather than escalating routing to the operator.

## Important process note (from two prior reviews today)

Do **not** use raw `git diff` against `git HEAD` to check forbidden
changes. This repo has not committed since 2026-07-15/23, so `git diff`
shows roughly two weeks of cumulative, unrelated work from many different
tasks and sessions — it produced a false-positive BLOCKER on an earlier
review today for exactly this reason. To confirm a submission touched only
its registered output paths, compare against the exact `output_paths` list
in `MAP_System/tasks/TASK-286.json`, or check `stat` mtimes for anything you
suspect is out of scope.

## Task summary

TASK-286: "Make Command Center Lab startup minimal and orchestrator-driven"
(P1, operator-directed lifecycle correction). This one is different in kind
from a typical roadmap task: it changes what opens by default every time
someone starts the AI Command Center Lab, and it changes the Codex
orchestrator's own prompt/authority framing. Read the full delivery
carefully — this is exactly the kind of change worth genuine scrutiny, not
a rubber stamp.

## Input paths (output_paths registered to TASK-286)

- `MAP_System/notes/command-center-orchestrator-lifecycle.md` (read this
  first — migration, rollback, residual risk, and the "orchestrator routing
  vs. autonomous authority" boundary are all documented here)
- `MAP_System/templates/install/bin/ai-command-center-lab-codex` (the
  orchestrator's prompt; diff mentally against
  `ai-command-center-lab-claude`/`-pi` for what else in the repo the
  original prompt template looked like)
- `MAP_System/templates/install/wezterm/ai-command-center-lab.lua` (the
  `gui-startup` function specifically)
- `MAP_System/tests/test_command_center_orchestrator_startup.py` (12 tests)

## Task record

`MAP_System/tasks/TASK-286.json` — read `acceptance_criteria` there.

## Expected review artifact

Use these exact section headers (required by `scripts/validate_review.py`):
`## Verdict`, `## Acceptance Criteria Check`, `## Files Reviewed`,
`## Forbidden Changes Check`. Cover:

1. Each acceptance criterion, PASS/FAIL/PARTIAL with evidence.
2. Forbidden-changes check using output-path/mtime comparison, not
   `git diff`.
3. Independent verification: run
   `MAP_System/.venv/bin/python MAP_System/tests/test_command_center_orchestrator_startup.py`
   directly and confirm 12/12. Read the actual `gui-startup` function in
   the `.lua` file yourself and confirm it really only spawns
   shell/codex/monitor — don't just trust the delivery note's claim.
4. **The authority question, carefully**: does the orchestrator prompt
   change actually grant the Codex lab session any new capability it didn't
   already have (bypass an approval gate, spawn headless, self-approve,
   bind a fixed provider to a role)? The delivery note claims "routing is
   not authority" — read the actual added prompt paragraph in
   `ai-command-center-lab-codex` and judge whether that claim holds up, not
   just whether the sentence exists.
5. Whether reducing default startup from 6 tabs to 3 could silently break
   an existing assumption elsewhere in the repo (search for any other file
   that assumes Claude/Pi/Librarian tabs are always open at startup).
6. Whether the test suite's inherent limitation (static text checks only,
   cannot drive an actual GUI wezterm session) is honestly disclosed rather
   than papered over — check the delivery note and test file docstring.

Save the review artifact to
`MAP_System/artifacts/reviews/task286-independent-review-<helper-tag>.md`.
Use `MAP_System/db/claims.py`'s `claim_review("TASK-286", "<your-hcom-name>",
db_path="MAP_System/map.db")` before reviewing, then — if approved — run the
sanctioned `map_task.py approve` command yourself. Report your verdict back
to `claude-lab-venu` via hcom either way.

## Stop condition

Stop after the review artifact is delivered, the sanctioned approve/reject
has actually run (verify canonical status changed), and the verdict is
reported via hcom — or if you cannot reach a verdict within your context/
turn budget, report back what was found so far and hand off rather than
stalling silently.
