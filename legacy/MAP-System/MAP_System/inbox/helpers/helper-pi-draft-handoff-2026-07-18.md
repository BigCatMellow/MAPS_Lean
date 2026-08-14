# Pi Assignment — Read-Only MAP/1 Handoff Draft Trial

- Owner: codex-lab-lilo
- Helper tag: helper-pi-draft
- Model/runtime: visible Pi terminal with local `ollama/qwen3.5:9b`, `--no-tools`.
- Status: COMPLETE — FAIL: no filesystem writes occurred, but the 9B terminal
  draft omitted `@MAP/1`, altered task/agent identifiers, and falsely claimed
  hcom delivery. The owner captured the result in the Pi capability trial;
  Pi remains draft-only and is not routed task-critical work.
- Objective: Test whether a stronger local Pi model can turn a bounded factual packet into a concise, valid-looking MAP/1 handoff draft without file/tool authority.
- Scope: The owner supplies a compact packet in the initial visible prompt. Pi may only render its draft in the terminal; the owner reads it, checks it against `../optimal-agent-communication-guide.md`, and records any result.
- Required output: terminal-only draft with `@MAP/1`, `type`, `id`, `state`, `owner`, `done`, `next`, `blocker`, `risk`, `verify`, and `refs`. No hcom reply or filesystem artifact is expected from Pi.
- Prohibited: all tools, filesystem writes, hcom sending, task/policy/decision actions, inference beyond the supplied factual packet, and final-quality claims.
- Stop condition: one terminal draft. The owner records PASS/FAIL plus the useful/invalid portions in a durable experiment artifact, then stops the helper.

## Reason for this narrow lane

The 4B file-writing trial failed safely by confusing an assignment path with an
output path. This trial separates drafting from durable mutation and tests the
already-installed 9B local model on the structured, repetitive communication
shape it is more likely to support. It must not be treated as proof of broader
Pi autonomy.
