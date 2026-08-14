# Helper Assignment — TASK-228 Independent Implementation Review

- Owner: codex-lab-lilo
- Helper tag: helper-librarian-rori
- Status: ACTIVE
- Task: `TASK-228`
- Conflict reason: the task owner cannot approve its own local-lane repair;
  the available core reviewer is recovering a separate `TASK-227` rework.

## Objective

Review TASK-228 only. Confirm that the repair aligns the real installed local
Ollama inventory with a visible, draft-only helper lane without re-enabling
Pi, silently selecting a hosted provider, or preserving a hidden model worker.

## Required reading

1. `MAP_System/tasks/TASK-228.json`
2. `MAP_System/artifacts/experiments/local-ollama-lane-inventory-2026-07-18.md`
3. all registered TASK-228 output paths;
4. `MAP_System/artifacts/tests/local-ollama-advisory-lane-test-2026-07-18.md`
5. `MAP_System/AGENTS.md` local-helper and visibility rules.

## Required output

`MAP_System/artifacts/reviews/task228-review-rori.md`

Use PASS/PARTIAL/FAIL per acceptance criterion. Check specifically:

- only loopback Ollama endpoints/hosts are used by the changed lane;
- generic UI action only exposes the actually drilled qwen3.5:4b lane;
- Pi and missing Goose launch paths are not advertised;
- background summary-model work is disabled rather than silently redirected;
- local runner rejects unapproved models and does not grant authority;
- test evidence is accurate about no model invocation and the full-suite
  unrelated failure.

Classify every blocking issue as `REQUIRED` or `BLOCKER`; do not approve the
task or change task state. Send one hcom `inform` with the artifact path and
verdict, then return to visible listening.
