# Bounded Helpers

Helpers accelerate work inside an already-active task. They do not become the
task owner, reviewer, approver, or completion authority.

## Shared rule

Every helper output/edit path must fit the parent task's declared
`output_paths`, and the parent task must already be `ACTIVE`.

```text
ACTIVE task snapshot
  + output boundary
  + selected helper/model
        ↓
bounded helper operation
        ↓
helper result record
        ↓
accountable owner integrates/verifies
```

Helper records default to `.maps/state/helper-runs.json`. They are evidence of a
helper invocation, not canonical lifecycle state.

## Ollama

`OllamaHelper` is a text/draft lane:

- health check with `ollama ls`;
- run one explicit model with `ollama run <model>`;
- prompt passed via stdin;
- one explicitly scoped output file;
- no hard-coded approved model list — HPOM/capability profiles decide fitness.

## Aider

`AiderHelper` is a bounded edit lane:

- targets must fit task `output_paths`;
- target files must not already be dirty;
- uses one-shot `--message` mode;
- forces `--no-auto-commits` and `--no-dirty-commits`;
- never passes blanket `--yes` / `--yes-always`;
- exposes no generic extra-arguments escape hatch;
- compares Git changes before/after and rejects newly-created out-of-scope changes.

The wrapper does **not** auto-revert an out-of-scope edit because an automatic
revert could destroy unrelated work. It stops and requires inspection/repair.

## Authority

A helper result never means:

```text
helper completed  != task DONE
helper edited      != review passed
local model agrees != architecture approved
Aider succeeded    != acceptance criteria verified
```
