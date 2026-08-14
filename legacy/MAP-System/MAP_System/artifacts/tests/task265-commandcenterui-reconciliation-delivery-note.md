# TASK-265 Delivery Note: CommandCenterUI server.py Reconciliation

## Scope and authority

This edits `/home/mellow/Projects/CommandCenterUI/app/server.py`, outside
MAP's normal writable scope, per
`artifacts/planning/commandcenterui-boundary-decision.md`'s Required
Approval Before External Edits:

- **Operator approval naming the external path**: DEC-030 (2026-07-23,
  live is authoritative for features / merge direction live→template) and
  DEC-033 (2026-07-28, local-model allowlist is `qwen3.5:4b` only), both in
  `shared/decisions.md`. DEC-033 was recorded live with the operator by
  `task288-review-valo` while preparing this handoff; see
  `MAP_System/handoffs/HANDOFF-TASK-265-task288-review-valo-to-nisa.md`.
- **Output paths for the exact external files**: both
  `/home/mellow/Projects/CommandCenterUI/app/server.py` and
  `MAP_System/templates/install/command-center-ui/app/server.py` are
  registered on `TASK-265`.
- **Outside canonical MAP repo's normal writable scope**: yes — this note
  states that explicitly, as required.
- **This is not write-capable control work**: no new operator-triggered
  action or write-control surface was added. This restores a pre-existing
  security gate that was silently dropped, and merges pre-existing live
  feature work into the template per DEC-030's already-settled direction.
  The write-control spec does not apply.

## What changed

**Live `app/server.py`** (the only file with a real code change):
- Added `VISIBLE_OLLAMA_MODELS = {"qwen3.5:4b": ...}` back (it was present
  in the template the whole time; the 2026-07-21 untracked edit dropped it
  from live only).
- Restored the gate in `local_agent_defs()`: `description =
  VISIBLE_OLLAMA_MODELS.get(model_name); if description is None: continue`.
  Before this, every installed Ollama model (11, per `ollama list` on
  2026-07-28) was launchable through the UI; now only `qwen3.5:4b` is.
- `OLLAMA_MODEL_USES` (the live copy's broader 5-model description dict)
  is left in place, untouched, as inert description text per DEC-033 — it
  is no longer read by `local_agent_defs()` for gating, only
  `VISIBLE_OLLAMA_MODELS` is.

**Template `app/server.py`**: replaced wholesale with the (now-fixed) live
copy. Verified before doing this that every remaining template-only line
was strictly superseded by an already-present, already-improved live
equivalent (e.g. `OLLAMA_URL` hardcoded → `OLLAMA_HOST_PORT`-derived,
consolidated per DEC-029; `SUMMARY_MODEL = None` fixed → opt-in via
`COMMAND_CENTER_UI_SUMMARY_MODEL` env var) — not a case of template having
unique content that a blind copy would have destroyed. `diff` confirms
byte-identical after the copy.

**New test file**: `MAP_System/tests/test_command_center_ollama_allowlist.py`
(6 tests, all passing) — this is TASK-265 acceptance criterion 4's
mechanical drift check. It exercises the live file's actual
`local_agent_defs()`/`VISIBLE_OLLAMA_MODELS` (imported and run, not just
read as text) to prove the gate is fail-closed, and separately asserts
both copies still define/gate on the same qwen3.5:4b-only allowlist, so a
future edit that silently drops the gate again (in either copy) fails a
test instead of waiting for another audit.

## Verification performed

- `python3 -m py_compile` on both files: clean.
- `MAP_System/.venv/bin/python3 -m unittest MAP_System.tests.test_command_center_ollama_allowlist -v`:
  6/6 pass.
- Re-ran the 5 pre-existing `test_command_center_*` suites (composer
  alignment, attention history, agent identity, message intent, attention
  popup): all pass, unaffected.
- Manually loaded the live file via `importlib` with a monkeypatched
  `ollama_models()` returning 5 fake installed models (including
  `qwen3.5:4b`, `deepseek-r1:8b`, `nomic-embed-text`) and confirmed
  `local_agent_defs()` exposes exactly one `ollama-model-*` entry.

## Restart plan (required by the boundary decision)

The app is **not currently running** (checked via `ps aux` before editing
— no `server.py` process). This means:

- No live process needs restarting right now; the fix takes effect the
  next time the app is launched.
- Launch command: `command-center-ui` (full GUI window) or
  `run-command-center-app.sh --server-only` (headless, prints
  `http://127.0.0.1:8765/`) from `/home/mellow/Projects/CommandCenterUI`.
- **If the app is already running** the next time this kind of change
  lands: kill the `server.py` process and relaunch via the same command.
  Verified safe to do so with no data loss: the only persistent state is
  `SUMMARY_CACHE_PATH` (a JSON file, unaffected by this change) and
  `TerminalPromptLog`'s in-memory transcript-read offsets, which
  `ingest()` re-establishes from near the tail of each transcript on first
  read after restart (`pending_launch` discards the first, possibly
  partial, re-read entry) — worst case one terminal-prompt message is
  briefly skipped or duplicated once, not a data-loss or correctness risk.
- Post-restart verification: `curl http://127.0.0.1:8765/api/agents` (or
  the equivalent local-agent-listing endpoint) and confirm the response's
  Ollama entries include only `qwen3.5:4b`, not the full installed list.

## Review note

Not self-reviewed. `task288-review-valo` explicitly disqualified itself
(too hands-on already: diffed both files, took the DEC-033 decision live
with the operator, added the output path) separate from its own
helper-execution boundary. `claude-lab-lili` is disqualified as this
session's (`lili-replacement-nisa`'s) rotation predecessor. No other core
agent is currently live (codex down, only Pi is live besides the two
disqualified identities, and Pi is exploratory-only per DEC-008) — per
`scripts/review_routing.py` (TASK-290), this is the escalate-or-spawn-
fresh case. A fresh, uninvolved helper reviewer will be spawned rather
than escalating, since a brand-new hcom identity has no lineage conflict.
