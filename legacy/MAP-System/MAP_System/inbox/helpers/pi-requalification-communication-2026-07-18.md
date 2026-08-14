# Pi Assignment — 7B-16K Communication Requalification

- Owner: `codex-lab-lilo`
- Status: COMPLETE — FAIL
- Agent: completed visible `pi-lab-nami` session
- Runtime: Pi with `ollama/qwen2.5-coder:7b-16k --offline`
- Objective: prove only that the fresh Pi session can find the shared
  communication instructions and send one real hcom acknowledgement.

## Required reads

1. `AGENTS.md`
2. `MAP_System/AGENTS.md`
3. `MAP_System/notes/pi-agent-communication-guide.md`
4. This assignment note

## Exact action and pass condition

After reading the four files, send exactly this hcom message:

```bash
hcom send @codex-lab-lilo --intent inform --name <your-pi-hcom-name> -- \
  'PI_REQUAL_COMM_ACK model=qwen2.5-coder:7b-16k scope=no-write owner=codex-lab-lilo'
```

The owner scores the observed hcom event. Do not claim success solely in the
terminal.

## Strict scope

- Do not create, claim, review, or change a MAP task.
- Do not write, edit, delete, or rename any file.
- Do not inspect active project tasks, use external tools, start subagents, or
  send any other messages.
- Do not begin implementation, analysis, or a follow-up task.

## Stop condition

After the one message, return to listening. If that message cannot be sent,
send no substitute message: stop so the owner can record the missing event and
end this instance.

## Outcome

- No required `PI_REQUAL_COMM_ACK` hcom event was observed.
- The Pi transcript displayed a malformed/unobserved delivery claim instead of
  the exact required command result.
- The visible terminal was ended; no Pi file writes or MAP mutations occurred.
