# Agent Instructions

This repository is organized for file-based multi-agent work. Prefer durable
files over chat memory: task records, shared notes, handoffs, events, and review
artifacts are the source of truth.

## Required Reading

1. `docs/agent-quickstart.md`
2. `docs/project-map.md`
3. The relevant project rules:
   - Reusable system work: `MAP_System/AGENTS.md`
   - Pathwell work: `Projects/Pathwell/AGENTS.md`
   - ProjectUpdater work: `Projects/ProjectUpdater/AGENTS.md`
   - ClearFront work: `Projects/ClearFront/AGENTS.md`

## Routing

- Work on the reusable multi-agent framework in `MAP_System/`.
- Work on the Pathwell story project in `Projects/Pathwell/`.
- Work on the ProjectUpdater tracker app in `Projects/ProjectUpdater/`.
- Work on the ClearFront trading card game in `Projects/ClearFront/`.
- Treat `archive/`, `logs/`, `.venv/`, `.locks/`, `exports/`, and `snapshots/`
  as non-primary context unless a task explicitly asks for them.

## What Each Folder Answers

| Question | Where to look |
|---|---|
| What are the rules for this project? | `MAP_System/AGENTS.md` |
| What is the canonical MAP authority hierarchy? | `MAP_System/shared/project-brief.md` → `Operating Model` |
| What is the current state of the system? | `MAP_System/shared/current-state.md` |
| What decisions have been made? | `MAP_System/shared/decisions.md` |
| How do I author, promote, review, or release a task? | `MAP_System/notes/` |
| How should I communicate with other agents? | `Guidelines/llm-communication-rules.md` then `MAP_System/AGENTS.md` |
| When should I use a local model vs. a core agent? | `MAP_System/notes/local-model-helper-guide.md` |
| What are the general AI collaboration protocols? | `Guidelines/` (universal — applies to any project in this workspace) |
| What does HPOM mean and how does it work? | `MAP_System/shared/hpom.md` |
| How do I capture an insight, idea, or experiment? | `MAP_System/emergence/README.md` |
| How do I promote an idea into a task? | `MAP_System/emergence/IDEA_PROMOTION_RULES.md` |
| What is the MAP Bedrock program's current phase/status/next-action? | `MAP_System/artifacts/planning/map-bedrock-phase-checklist-2026-08-10.md` (agent-readable, canonical); `Projects/ProjectUpdater/app/index.html`'s "MAP Bedrock" project is the same data as a human-facing dashboard, imported from that file — read the file, don't assume the dashboard is independently authoritative |

## Git

Use the provided wrapper from the repository root:

```bash
MAP_System/scripts/map-git status
```

Do not use destructive Git commands unless the user explicitly requests them.
