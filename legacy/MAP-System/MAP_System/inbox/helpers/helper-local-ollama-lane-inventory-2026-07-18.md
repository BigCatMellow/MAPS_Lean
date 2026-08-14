# Helper Assignment — Local Ollama Lane Inventory

- Owner: codex-lab-lilo
- Helper tag: helper-librarian-rori
- Status: COMPLETE
- Trigger: Pi is paused after repeated local context/output exhaustion. The
  operator still wants any future helper lane to be local-only rather than
  dependent on hosted token quotas.
- Decision consumer: codex-lab-lilo needs to decide whether MAP needs a model
  download, a narrow configuration/task proposal, or no change to the
  non-Pi local helper lane.

## Objective

Audit the installed local Ollama inventory against the actual MAP local-helper
configuration. Distinguish a local-runtime issue from a reliability/authority
issue. Do not treat Pi's failure as evidence that every local helper is
unusable.

## Scope

Read only:

1. `ollama list` and `pi --offline --list-models ollama` output as needed;
2. `MAP_System/scripts/local_assistant_health.py`;
3. `MAP_System/scripts/local_runner.py`;
4. `MAP_System/notes/local-model-helper-guide.md`;
5. `MAP_System/shared/agent-capability-matrix.md`;
6. local-runner tests and current Command Center local-model launcher paths.

## Required output

`MAP_System/artifacts/experiments/local-ollama-lane-inventory-2026-07-18.md`

Include installed-versus-configured table, all local/hosted boundary evidence,
why health is `ok` or `attention`, a bounded recommendation (`no_change`,
`install_models`, or `propose_config_repair`), and—only if repair is
recommended—the exact files/tests and a minimal acceptance criterion. State
whether an available model has passed a reliability drill; do not infer it.

## Boundaries

- Do not download models, change config, edit code/docs, start Pi, or create a
  task.
- Do not recommend a local model for task ownership, review approval, release,
  authority decisions, or unsupervised writes.
- Completion: reported `MAP_System/artifacts/experiments/local-ollama-lane-inventory-2026-07-18.md` with recommendation `propose_config_repair`; no model download or configuration change was made by the helper.
