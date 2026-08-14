# TASK-228 Local Ollama Advisory Lane Test Record

Date: 2026-07-18
Owner: codex-lab-lilo
Scope: visible, local-only, non-Pi advisory lane. No live model inference was
run by this verification.

## Retrieval capsule

- Purpose: Records the bounded verification of MAP's visible local Ollama advisory lane and the exact installed model tag allowed to perform draft-only helper work.
- Proves: `qwen3.5:4b` allowlisting, loopback host enforcement, rejection of unknown tags, visible launcher wiring, disabled hidden summary work, and absence of Pi shortcuts or delegated authority.
- Applies to: TASK-228 code, tests, launcher templates, and local health observations verified on 2026-07-18 without live inference.
- Does not provide: Permission to download models, use remote Ollama hosts, run hidden model work, re-enable Pi, claim tasks, approve reviews, release changes, or assume later runtime health.
- Evidence type: measured_outcome
- Status: historical

## Verified behavior

| Check | Result | Evidence |
|---|---|---|
| Local runtime health | PASS | `local_assistant_health.py --json` reports `status: ok`, host `127.0.0.1:11434`, and `qwen3.5:4b` as the one available approved draft model. |
| Local-only runner | PASS | `test_local_runner.py` verifies unknown models are rejected, `qwen3.5:4b` is the tested model, and `run_ollama` forces `OLLAMA_HOST=127.0.0.1:11434`. |
| Health semantics | PASS | `test_local_ollama_lane.py` covers both the drilled-lane-present `ok` case and the drilled-lane-absent `attention` case. Installed but unproven tags do not become assignable. |
| Visible launcher | PASS | Template and deployed `~/.local/bin/ai-command-center-ollama-model` pass `sh -n`; an unsupported-model invocation exits 2 before opening a terminal or invoking Ollama. A sandboxed installer run produced an executable rendered launcher matching the template substitutions. |
| Command Center exposure | PASS | Focused test confirms only `qwen3.5:4b` is exposed. Inventory discovery and launch both force loopback even when the server inherits a hostile remote `OLLAMA_HOST`; missing Goose and Pi launch shortcuts are absent. The server disables the hidden summary-model worker and enqueue path. |
| Shared/task state | PASS | `validate_task_mirrors.py` and `validate_shared_state.py` passed after TASK-228 claimed its expanded output set. |

## Commands

```text
python3 MAP_System/tests/test_local_runner.py
python3 MAP_System/tests/test_local_ollama_lane.py
python3 -m py_compile MAP_System/scripts/local_assistant_health.py MAP_System/scripts/local_runner.py MAP_System/templates/install/command-center-ui/app/server.py
sh -n MAP_System/templates/install/bin/ai-command-center-ollama-model
sh -n ~/.local/bin/ai-command-center-ollama-model
COMMAND_CENTER_UI_WORKSPACE="$PWD" python3 MAP_System/templates/install/command-center-ui/app/server.py --help
MAP_System/.venv/bin/python MAP_System/scripts/local_assistant_health.py --json
MAP_System/.venv/bin/python MAP_System/scripts/validate_task_mirrors.py
MAP_System/.venv/bin/python MAP_System/scripts/validate_shared_state.py
MAP_INSTALL_BIN_DIR=<temporary-dir>/bin ... ./install-map-system.sh --yes --skip-apt --skip-hcom --skip-wezterm --skip-desktop --skip-venv
```

## Intentional non-tests

- No model download occurred.
- Pi is not a component of this local advisory lane or any check above. Its
  separately authorized, no-write requalification does not give Pi access to
  the lane or any authority.
- No local model was invoked from a hidden process.
- The three-run reliability drill remains deferred: it must be run through the
  Command Center's visible terminal action and independently recorded before
  any expansion beyond the existing narrow MAP Steward advisory shape.

## Full-suite note

`MAP_System/scripts/run_tests.sh` reached the new local checks successfully,
but the suite retains a pre-existing unrelated failure:
`validate_research_artifacts` rejects the already-present
`artifacts/research/hpom-operating-models-comparative-2026-07-18.md` filename
because it lacks a recognized research-artifact prefix. The failure is outside
TASK-228 output scope and was not changed here.

The suite also emitted its existing limit-watcher timeout warning for
`claude-lab-mira`; its focused test still passed. No model reliability result
is inferred from either unrelated suite condition.
