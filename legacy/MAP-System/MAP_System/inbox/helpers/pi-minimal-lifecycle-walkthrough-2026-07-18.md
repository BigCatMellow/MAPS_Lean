# Pi Assignment — Minimal MAP Lifecycle Walkthrough

- Owner: codex-lab-lilo
- Agent: fresh visible `helper-pi-lifecycle-*` session (replaces stale `pi-lab-puma`)
- Model/runtime: Pi with local `ollama/qwen3.5:4b`; Pi's offline model registry and `ollama list` confirm the model is already installed, so no download is needed.
- Status: FAILED_SAFELY — the 4B trial attempted to overwrite this assignment rather than the permitted artifact. The owner restored this note; no canonical MAP state was changed. A future Pi trial must be read-only/draft-only and use a stronger model.
- Objective: Independently trace the smallest credible operator-guided MAP project from a brief through one shaped task, an interruption/recovery, independent review, and release. The purpose is to test the “learn to walk” north-star outcome, not to redesign MAP.
- Scope: Read-only. Use `AGENTS.md`, `MAP_System/AGENTS.md`, `docs/agent-quickstart.md`, `MAP_System/notes/system-improvement-kickoff.md`, `MAP_System/notes/limit-exhaustion-protocol.md`, and the task/review/release command help. Do not inspect ClearFront or use current active task state.
- Required output: `MAP_System/artifacts/experiments/pi-minimal-lifecycle-walkthrough-2026-07-18.md`, containing exactly: a six-step path, the minimum evidence needed at each step, three friction points, and one smallest next experiment. Mark observations versus inferences.
- Prohibited: task creation or state changes, implementation edits, policy/decision changes, E/I promotion, external research, and hidden/headless execution.
- Stop condition: write only the named artifact, send its path and a one-line completion result through hcom, then return to listening. If blocked, send the exact blocker through hcom instead of continuing silently.

## Runtime note

The previous `pi-lab-puma` session is not reused: durable ClearFront handoff
and event evidence records repeated non-progress/limit failures on a much
larger task, and the live hcom lookup no longer resolves it reliably. This
replacement intentionally used a smaller local model only for a smaller,
read-only, fixed-format job; the failed trial shows the model is still not
reliable for autonomous file-path compliance. Future Pi use stays visible and
draft-only until a stronger-model comparison proves otherwise.
