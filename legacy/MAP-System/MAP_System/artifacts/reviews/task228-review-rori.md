# Review: TASK-228 Visible Non-Pi Local Ollama Advisory Lane

task_id: TASK-228  
reviewer: helper-librarian-rori  
task_owner: codex-lab-lilo

## Verdict

APPROVED

## Acceptance Criteria

| Criterion | Result | Evidence |
|---|---|---|
| Health separates local runtime reachability from lane coverage, recognizes installed `qwen3.5:4b` as the sole drilled model, and downloads nothing | PASS | `local_assistant_health.py` pins health subprocesses to `127.0.0.1:11434`; live read-only health returned `ok`, one approved model, no missing models, and draft-only/visible policy. No download path was added or invoked. |
| `local_runner` permits only documented draft-only models and rejects unknown/unapproved models without writes | PASS | Allowlist is exactly `qwen3.5:4b`; unknown-model validation precedes prompt/output work. Reproduced `test_local_runner.py`, including no-output rejection and forced loopback environment. Durable helper note denies completion, approval, release, and final architecture authority; docs deny ownership/authority. |
| Generic Command Center action has a real visible launcher, rejects unsupported models, and cannot call a hosted provider | PASS | Template/deployed launcher are identical, shell-valid, allow only `qwen3.5:4b`, open WezTerm, and export loopback. The canonical installer now includes the launcher, and inventory discovery forces loopback even under a hostile ambient `OLLAMA_HOST`. |
| Docs distinguish narrow evidence from unproven/failed models; Pi stays paused; no authority expansion | PASS | Helper guide and capability matrix name only the bounded `qwen3.5:4b` advisory shape as draft-only/core-reviewed, mark Pi paused, and mark other installed tags unassignable/unproven. Server removes Pi/Goose launch advertisements; no Pi launcher or task path was changed. |
| Focused tests pass without live inference; three-run reliability drill is visibly deferred and not inferred | PASS | Reproduced both focused scripts, syntax/compile checks, live health, task mirrors, and shared-state validation. Model subprocesses in runner tests are mocked. Test artifact explicitly records no live inference and defers the drill to a visible terminal. Full suite result and unrelated failure are accurate. |

## Files Reviewed

- `MAP_System/artifacts/releases/task-228-release-checklist.md`
- `MAP_System/artifacts/tests/local-ollama-advisory-lane-test-2026-07-18.md`
- `MAP_System/notes/local-model-helper-guide.md`
- `MAP_System/scripts/local_assistant_health.py`
- `MAP_System/scripts/local_runner.py`
- `MAP_System/scripts/map_steward.py`
- `MAP_System/scripts/run_tests.sh`
- `MAP_System/shared/agent-capability-matrix.md`
- `MAP_System/templates/install/bin/ai-command-center-ollama-model`
- `MAP_System/templates/install/command-center-ui/app/server.py`
- `MAP_System/tests/test_local_ollama_lane.py`
- `MAP_System/tests/test_local_runner.py`
- `install-map-system.sh`

## Forbidden Changes Check

PASS — TASK-228’s implementation and release records stay within its registered output paths. No model download, Pi enablement, hosted-provider selection, hidden model worker, live model drill, task/review/release authority grant, or unsupervised model write was introduced. The separately authorized Pi no-write requalification remains documented as paused and outside TASK-228’s generic advisory lane.

## Prior Required Findings — Resolved

| ID | Severity | File | Finding | Required Action |
|---|---|---|---|---|
| R1 | RESOLVED | `install-map-system.sh` (`install_command_center_files`) | The installer now includes `ai-command-center-ollama-model`, and the task registered `install-map-system.sh` as an output. | Independent isolated install into `/tmp` exited 0, produced mode `0755`, resolved template placeholders, and passed `sh -n`. |
| R2 | RESOLVED | `MAP_System/templates/install/command-center-ui/app/server.py` (`ollama_models`) | Discovery now copies the environment and overwrites `OLLAMA_HOST` with `127.0.0.1:11434`. | `test_ui_discovery_forces_loopback_despite_ambient_host` passes with `OLLAMA_HOST=http://remote.invalid:11434`, asserts loopback reaches the subprocess, exposes `qwen3.5:4b`, and filters `qwen3.5:9b`. |

## Specific Safety Checks

- **Loopback inference and discovery:** PASS for `local_assistant_health.py`, `local_runner.py`, `map_steward.py`, server inventory/summary URL, and launcher.
- **Only drilled model advertised:** PASS after inventory returns; `VISIBLE_OLLAMA_MODELS` contains only `qwen3.5:4b` and filters other installed tags.
- **Pi and Goose advertisements:** PASS; no Pi-new or Goose base launch definition remains. `LAB_TAGS` recognizing an already-live Pi session is roster classification, not a launch advertisement.
- **Background summary model:** PASS; `SUMMARY_MODEL=None` makes `Summarizer.enqueue()` return before queueing. A daemon bookkeeping thread still exists, but it performs no model request without queued work.
- **Local-runner authority:** PASS; static allowlist, local host, scoped output/note/event, and explicit draft-only/core-review documentation remain.
- **Evidence honesty:** PASS. Full suite reproduced `67 pass / 1 fail`; the sole failure is the pre-existing unknown research-artifact filename `artifacts/research/hpom-operating-models-comparative-2026-07-18.md`. The limit-watcher resume timeout appeared as documented while its 32 focused tests passed.

## Verification

- `python3 MAP_System/tests/test_local_runner.py` — PASS (3 tests; mocked model call).
- `python3 MAP_System/tests/test_local_ollama_lane.py` — PASS (4 tests; no model inference).
- `python3 -m py_compile ...` for health, runner, Steward, and Command Center server — PASS.
- `sh -n` for template and deployed launcher — PASS.
- Unsupported launcher call through `sh` with `qwen3.5:9b` — exit 2 before WezTerm/Ollama.
- Template/deployed launcher `cmp` — identical.
- `local_assistant_health.py --json` — PASS, loopback host and sole approved `qwen3.5:4b` lane.
- `validate_task_mirrors.py` — PASS.
- `validate_shared_state.py` — PASS, 22 files.
- `MAP_System/scripts/run_tests.sh` — 67 PASS, 1 unrelated research-filename failure.
- Initial-review mocked discovery found no subprocess `env`, which established R2; re-review regression now confirms loopback is supplied under the same hostile ambient host.

## Independent Re-review — 2026-07-18

- Re-ran `test_local_runner.py`: 3/3 PASS.
- Re-ran `test_local_ollama_lane.py`: 5/5 PASS, including hostile ambient-host coverage.
- Re-ran task-mirror and shared-state validators: PASS.
- Ran the canonical installer in isolated `/tmp` destinations with user-service calls stubbed: exit 0; launcher rendered executable (`0755`), placeholders resolved, `sh -n` passed.
- Inspected `local_agent_defs()`: only the approved `qwen3.5:4b` entry survives inventory filtering.
- Inspected Pi references added by the separate operator-authorized no-write requalification: Pi remains operationally paused, is not exposed by TASK-228’s generic UI lane, and gains no task, review, handoff, release, file-mutation, or decision authority.
- No blocker or required finding remains. Final verdict: APPROVED.

## Notes

The repair does not re-enable Pi, download models, expand local authority, or preserve hidden background summarization. Deployment and locality gaps are closed without broadening the lane. This review did not change TASK-228 state or any implementation file.
