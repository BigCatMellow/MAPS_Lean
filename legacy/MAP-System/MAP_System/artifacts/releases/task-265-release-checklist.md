# Release Checklist: TASK-265

## Header

```
task_id:      TASK-265
released_by:  lili-replacement-nisa
release_date: 2026-07-28
review_record: MAP_System/artifacts/reviews/task265-independent-review-task265-review-fera.md (APPROVED)
```

## Checklist

- [x] Shared-file updates complete
- [x] Decisions recorded
- [x] Follow-up tasks created
- [x] Event log entry prepared
- [x] Emergence capture considered

## Summary

Restores a real security gate that a week-old untracked edit had silently
dropped: live `~/Projects/CommandCenterUI/app/server.py`'s
`local_agent_defs()` had no allowlist at all, so every Ollama model
installed on the machine (11, as of 2026-07-28) was launchable through the
Command Center UI, not just a reviewed set. Flagged once on 2026-07-21
(`artifacts/audits/task254-untracked-edit-2026-07-21.md`) and not picked
up until this task.

Restored `VISIBLE_OLLAMA_MODELS = {"qwen3.5:4b": ...}` and the
`local_agent_defs()` gate that reads it, per DEC-033 (recorded live with
the operator while preparing this task's handoff). Live's broader,
non-gating `OLLAMA_MODEL_USES` description dict is left in place, unused
for gating, per DEC-033's explicit allowance. Folded live's other feature
work (terminal-prompt reading, chat intent validation, the
`ollama-goose`/`pi-lab-new` launchers, the `OLLAMA_HOST_PORT`
consolidation) into the stale in-repo template via a wholesale copy, per
DEC-030's merge direction (live → template) — verified beforehand that
every remaining template-only line was strictly superseded by an
already-improved live equivalent, not unique content a blind copy would
have destroyed. The two `server.py` copies are now byte-identical.

Added `tests/test_command_center_ollama_allowlist.py` (6 tests) as the
mechanical drift check this task's acceptance criteria required: it
imports and executes the real `local_agent_defs()` under a monkeypatched
installed-model list to prove the gate is fail-closed, and separately
asserts both copies still define and gate on the same qwen3.5:4b-only
allowlist, so a future silent regression fails a test instead of waiting
for another audit.

The two carried-over open questions (whether CommandCenterUI may reach a
remote `OLLAMA_HOST`; which `server.py` copy is authoritative) were
already settled by DEC-029 and DEC-030 respectively before this
submission — confirmed still true, not re-litigated.

## Verification

- `python3 -m py_compile` on both `server.py` copies: clean.
- `MAP_System/.venv/bin/python3 -m unittest MAP_System.tests.test_command_center_ollama_allowlist -v`:
  6/6 PASS.
- All 9 `test_command_center_*` suites present in the tree re-run: PASS
  (2 environment-gated suites ran 0 tests, unrelated to this change).
- `diff` on the two `server.py` copies: byte-identical.
- Manual `importlib` load of the live file with a monkeypatched
  `ollama_models()` returning 5 fake installed models: exactly one
  `ollama-model-*` entry exposed (`qwen3.5:4b`).
- App-running check (`ps aux`): no `server.py` process running, confirming
  no live restart was needed; documented restart command and
  post-restart verification for when the app is next running, per
  `artifacts/planning/commandcenterui-boundary-decision.md`'s required
  restart plan.
- Independent review: `task265-review-fera`, a fresh helper spawned
  specifically for this review (no other live agent was eligible:
  `lili-replacement-nisa`/`claude-lab-lili` are rotation-lineage
  disqualified, `task288-review-valo` self-disqualified from hands-on
  involvement preparing the handoff, `pi-lab-mule` is exploratory-only per
  DEC-008). APPROVED with zero findings; reproduced all 4 acceptance
  criteria, all 6 new tests plus 9 pre-existing suites, the byte-identical
  claim, the gate logic directly in both files, and the forbidden-changes
  check via `git status --porcelain` (live file isn't git-tracked at all,
  confirmed no `.git` under `~/Projects/CommandCenterUI`).

## Rollback

Reversible by normal means: this is a pure code change (allowlist
restoration + a stale-template sync), no schema or migration involved.
Reverting the live file's diff would restore the pre-2026-07-21-fix state
(no gate) — not recommended, since that is the vulnerability this task
closes. If a rollback of the *template merge specifically* were ever
needed (e.g. a live feature turns out to have an undiscovered issue), the
pre-merge template content is recoverable from git history
(`MAP_System/templates/install/command-center-ui/app/server.py`), unlike
the live file which is not version-controlled.
