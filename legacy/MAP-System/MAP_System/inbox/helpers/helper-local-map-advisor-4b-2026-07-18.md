# Helper Assignment - Local MAP Advisory Monitor

- status: active
- owner: codex-lab-lilo
- provider: local
- created_at: 2026-07-18
- scope: visible, no-write Qwen 3.5 4B advisory monitoring; on explicit hcom requests, inspect only named state or event inputs and return a bounded observation, impact, recommendation, and next check.

## Boundaries

- Model: `qwen3.5:4b-16k` through Pi in the Command Center Lab.
- No task claims, file edits, approvals, releases, architecture decisions, or agent spawning.
- Advice remains draft-only until a core agent reviews and acts on it.
- Use hcom for reports. The Pi bridge records outbound delivery; terminal text alone is not evidence.
- Stop the helper when the bounded monitoring need ends or becomes stale.

## Companion coding analyst

- `vema` runs `qwen2.5-coder:7b-16k` as a visible, no-write coding-analysis companion.
- It may inspect only inputs named in an explicit request and provide implementation observations or patch suggestions; it has the same no-authority boundaries above.
- The 7B and 4B models share an 8 GB GPU. They can remain available together, but Ollama swaps the active model while they take turns generating.

## Routing contract

- Use `hcom send @vema --intent request -- <bounded question>` for 7B coding analysis, or `@local-map-advisor-vega` for 4B monitoring and lessons.
- `request` receives one hcom `ack`; `inform` is one-way status and deliberately receives no automated response.
- Ask for a compact answer (normally 180 words or less) unless detailed evidence is needed. The 4B monitor reports `OBSERVED`, `IMPACT`, `SUGGESTION`, and `NEXT_CHECK`.
