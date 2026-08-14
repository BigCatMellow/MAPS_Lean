# Helper Assignment - Independent review of TASK-265 (CommandCenterUI server.py reconciliation)

- status: active
- owner: lili-replacement-nisa
- provider: claude
- model: sonnet
- created_at: 2026-07-28
- scope: Independent review of TASK-265's submission per the standard MAP
  review gate (`AGENTS.md` Review Standard). Not a self-review: reviewer
  must not be `lili-replacement-nisa` or `claude-lab-lili` (rotation
  lineage). `task288-review-valo` is also excluded — not by the DB-level
  or lineage check, but because it explicitly disqualified itself: it
  diffed both server.py files, took the DEC-033 decision live with the
  operator, and added the output path while preparing this handoff, so it
  is not independent of the substance even though it never wrote to
  either file. `pi-lab-mule` is excluded because Pi is exploratory-only
  (DEC-008), not a review authority, even though it is not in the
  submission author's rotation lineage — `scripts/review_routing.py`
  (TASK-290) only checks author/lineage independence, not provider-tier
  authority, so this is a caller-side judgment on top of that tool, not a
  gap in it.

## Tier escalation

Same justification as `helper-review-task-288.md`/`helper-review-task-290.md`:
codex is down, no other live core agent is eligible (see above). Sonnet,
given this touches a live, external, security-relevant file
(`~/Projects/CommandCenterUI/app/server.py`) — the highest-stakes review
this session has needed.

## Why this review matters more than the last two

TASK-265 restores a real security gate: before this fix, live `server.py`
exposed and made launchable *every* installed Ollama model (11, as of
2026-07-28) through the Command Center UI, not just a reviewed set. This
went unnoticed for a week (flagged 2026-07-21, not picked up until today).
Give this the most scrutiny of the three reviews you have done this
session.

## What TASK-265 actually did

Full detail in
`MAP_System/artifacts/tests/task265-commandcenterui-reconciliation-delivery-note.md`
— read that first, it covers scope/authority (DEC-030, DEC-033), what
changed in both `server.py` copies, verification performed, and the
restart plan required by
`artifacts/planning/commandcenterui-boundary-decision.md`. Short version:

1. Live `server.py`: restored `VISIBLE_OLLAMA_MODELS = {"qwen3.5:4b": ...}`
   and the `local_agent_defs()` gate that reads it (`if description is
   None: continue`) -- both were silently dropped by the 2026-07-21
   untracked edit, per `artifacts/audits/task254-untracked-edit-2026-07-21.md`.
   `OLLAMA_MODEL_USES` (live's broader, non-gating 5-model description
   dict) is left in place, unused for gating, per DEC-033.
2. Template `server.py`: copied wholesale from the now-fixed live file
   (DEC-030's merge direction), after verifying every remaining
   template-only line was strictly superseded by an already-present,
   already-improved live equivalent.
3. New `MAP_System/tests/test_command_center_ollama_allowlist.py` (6
   tests) — TASK-265 acceptance criterion 4's mechanical drift check.

## Expected review artifact

1. Each acceptance criterion, PASS/FAIL/PARTIAL with evidence, including
   the two carried over from DEC-029/030 (remote-Ollama policy question,
   authoritative-copy question) which were already settled before this
   submission — confirm they are genuinely settled, not re-litigate them.
2. **Reproduce, don't trust**: run
   `MAP_System/.venv/bin/python3 -m unittest MAP_System.tests.test_command_center_ollama_allowlist -v`
   yourself (6 tests). Also re-run the 5 pre-existing `test_command_center_*`
   suites to confirm no regression.
3. Read `local_agent_defs()` and `VISIBLE_OLLAMA_MODELS` directly in
   **both** `/home/mellow/Projects/CommandCenterUI/app/server.py` and
   `MAP_System/templates/install/command-center-ui/app/server.py` —
   confirm the gate is real code, not just present in one copy, and that
   `OLLAMA_MODEL_USES` genuinely cannot expose an unlisted model (test 4
   in the new suite claims this; verify the logic yourself, not just the
   test's pass/fail).
4. `diff` the two `server.py` files yourself and confirm they are
   byte-identical (the delivery note claims this) — if they have drifted
   even slightly since submission, that is itself a finding.
5. Check whether the CommandCenterUI app is currently running
   (`ps aux | grep server.py`) and whether the delivery note's restart
   plan is accurate given whatever you find.
6. Whether leaving `OLLAMA_MODEL_USES` in the file, unused, is the right
   call versus removing it entirely — DEC-033 explicitly permits leaving
   it as "inert description text," but form your own view on whether
   dead-but-plausible-looking config is itself a latent risk (a future
   editor could plausibly "helpfully" wire it back in as a gate, not
   knowing DEC-033 rejected that).
7. Whether it was reasonable to fold `OLLAMA_MODEL_USES` (5 models, 2 of
   which -- `llama3.2:3b`, `llama3.2:1b` -- are not installed at all per
   the delivery note context) into the template via the wholesale copy
   rather than dropping it -- i.e., did the wholesale-copy approach
   correctly carry forward something DEC-033 said should be *allowed to
   remain*, not something it said should be *removed*.
8. Forbidden-changes check: confirm nothing outside TASK-265's registered
   `output_paths` was touched.

Save the review artifact to
`MAP_System/artifacts/reviews/task265-independent-review-<helper-tag>.md`.
Use `MAP_System/db/claims.py`'s `claim_review("TASK-265", "<your-hcom-name>",
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
