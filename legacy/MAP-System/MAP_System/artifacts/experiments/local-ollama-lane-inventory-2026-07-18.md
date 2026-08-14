# Local Ollama Lane Inventory — 2026-07-18

## Recommendation

`propose_config_repair`

Do **not** download another model. The local runtime is reachable and already has suitable bounded-helper candidates. Repair the generic non-Pi lane so its allowlist, health expectations, capability documentation, and visible launcher agree with installed and actually drilled models. Keep every model draft-only and core-reviewed.

## Installed versus configured

Observed with `ollama list`, `pi --offline --list-models ollama`, the local-runner/health scripts, and Command Center launcher definitions.

| Model | Installed | Pi offline registry | Generic `local_runner` allowed / health-required | Other current configuration | Reliability evidence | Inventory result |
|---|---|---|---|---|---|---|
| `qwen3.5:4b` | yes | yes | no | MAP Steward model; dynamically advertised by Command Center | **Narrow pass:** bounded Steward JSON recommendations succeeded in ~9s through Ollama `/api/generate`; initial CLI structured output was malformed | Best existing candidate for bounded advisory/summary packets; not proven for file writes or general tasks |
| `qwen3.5:9b` | yes | yes | no | Pi launcher default, explicitly `--offline` | **Fail:** Pi MAP/1 draft omitted header, corrupted task ID, invented identities, and falsely claimed an hcom send; separate long run exhausted output/context | Do not use as an operational coordination worker; runtime availability is not reliability |
| `qwen2.5-coder:7b` | yes | yes | no | dynamically advertised by Command Center | no drill found | Installed only; no reliability claim |
| `qwen2.5-coder:1.5b` | yes | yes | yes | guide/capability matrix: fast syntax/key/path checks | no real reliability drill found; runner unit test is mocked | Available permitted narrow lane, but unproven beyond runtime presence |
| `qwen2.5-coder:1.5b-16k` | yes | no | no | none found | no drill found | Custom installed tag; do not infer equivalence to configured tag |
| `llama3.2:1b` | yes | not shown by Pi registry | yes | guide/capability matrix: tiny classification | **Fail/partial:** TASK-181 output was not directly usable; only rough grouping cue survived core rewrite | May provide disposable hints, not reliable structured output |
| `deepseek-r1:8b` | yes | yes | no | dynamically advertised by Command Center | no drill found | Installed only; no reliability claim |
| `nomic-embed-text:latest` | yes | no | no | none in inspected helper lane | not applicable; embedding model | Not a generative helper candidate |
| `llama3.2:3b` | no | no | yes | guide/capability matrix: summaries/orientation | older health artifact only; not current availability | Stale required/configured model |
| `qwen2.5-coder:3b` | no | no | yes | guide/capability matrix: JSON/schema/validator suggestions | **Fail:** TASK-181 timed out after 180s with no output | Do not download merely to restore an obsolete health checklist |
| `gemma3:4b` | no | no | yes | guide/capability matrix and Command Center summary default | **Fail:** TASK-181 drifted, omitted requested replacement markdown, emitted control artifacts | Do not download merely to restore an obsolete health checklist |

## Boundary evidence

### Local versus hosted

- `ollama list` reports eight locally stored model tags.
- `pi --offline --list-models ollama` exposes local Ollama models and their local context/output limits.
- The installed/template Pi launcher selects `ollama/qwen3.5:9b --offline`; its “out of tokens” failures therefore reflect local context/output behavior, not a hosted subscription quota.
- `local_runner.py` invokes `ollama run <model>` directly. It does not select a hosted provider.
- MAP Steward invokes local Ollama and has a deterministic fallback. Its model-backed action is opened visibly from Command Center.
- No model download is needed to test a non-Pi local lane.

### Authority and visibility

- Health policy reports `helper-capability-only`, `core_agent_status=not-registered`, `final_authority=core-agents-and-command-center`, and `starts_sessions=false`.
- The guide and capability matrix limit local models to summaries, classification, checks, drafts, recommendations, and diff suggestions under a core owner.
- Local models may not own tasks, approve reviews, release work, make authority/architecture decisions, or perform unsupervised writes.
- `local_runner.py` records output, helper note, and event only after an explicit bounded invocation; its unit test mocks Ollama and proves plumbing/guardrails, not model reliability.
- Pi’s visibility does not grant authority, and its two failed trials show why runtime/locality must not be confused with dependable execution.

## Why health is `attention`

`local_assistant_health.py` currently treats five hard-coded tags as all required:

- present: `llama3.2:1b`, `qwen2.5-coder:1.5b`;
- missing: `llama3.2:3b`, `qwen2.5-coder:3b`, `gemma3:4b`.

Ollama itself is reachable and Aider is installed/reachable (`aider 0.86.2`). Therefore `attention` means **configured inventory drift**, not local-runtime failure. The health script also ignores installed `qwen3.5:4b`, despite its narrow successful Steward drill.

There is a second configuration fault: Command Center dynamically advertises every `ollama list` model and points each entry at `~/.local/bin/ai-command-center-ollama-model`, while that launcher is missing. The base Goose launcher path is also missing. Pi’s dedicated launcher exists, but the assignment asks for a non-Pi local lane.

## Reliability conclusion

An available model has passed **one bounded reliability drill**:

- `qwen3.5:4b` produced valid structured MAP Steward recommendations from a bounded approved packet in about nine seconds after switching from malformed CLI output to Ollama’s JSON API with `think=false` and `format=json`.

That pass is shape-specific. It does not prove reliable durable-file output, coordination messages, task work, review, or broad summarization. Available `qwen3.5:9b` failed coordination accuracy; `llama3.2:1b` failed direct-use quality; no real drill was found for installed `qwen2.5-coder:1.5b`, its `-16k` tag, `qwen2.5-coder:7b`, or `deepseek-r1:8b`.

## Minimal repair proposal

### Exact files

- `MAP_System/scripts/local_assistant_health.py`
- `MAP_System/scripts/local_runner.py` (only if allowlist/config is separated from health requirements rather than imported unchanged)
- `MAP_System/notes/local-model-helper-guide.md`
- `MAP_System/shared/agent-capability-matrix.md`
- `MAP_System/templates/install/command-center-ui/app/server.py`
- a new install template for the currently referenced `ai-command-center-ollama-model` visible launcher, plus deployment to `~/.local/bin/ai-command-center-ollama-model`
- `MAP_System/tests/test_local_runner.py`
- focused health/launcher discovery tests (new or added to the existing Command Center server tests)

Do not add the missing Goose launcher unless Goose is separately chosen and tested; remove or suppress that advertised base entry instead of creating an unproven lane.

### Minimal acceptance criterion

> With no model download, health distinguishes runtime reachability from optional-model coverage and reports an available bounded lane for installed `qwen3.5:4b`; the generic Command Center action opens that model in a visible terminal through an existing launcher; one deterministic bounded JSON advisory fixture passes three consecutive runs with exact required keys and no invented task/identity/action claims; failures fall back or return attention without writing MAP truth. All output remains draft-only under a named core reviewer.

The three-run drill is deliberately narrower than Pi’s general-task trial. If it fails, retain the deterministic Steward fallback and classify the generic model lane as unavailable; do not expand scope or download another model as a reflex.

## Decision summary

- Recommendation: `propose_config_repair`
- Runtime issue: **no** — Ollama and Aider are reachable.
- Hosted quota issue: **no** for the tested Pi/Ollama paths — they are local/offline.
- Reliability issue: **yes**, task-shape dependent.
- Download needed: **no**.
- Safe present use: deterministic MAP Steward plus its narrowly drilled `qwen3.5:4b` advisory mode; other installed models remain unproven or failed.
