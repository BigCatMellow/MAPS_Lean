# Pi Assignment — 7B-16K Communication Requalification, Round 2

- Owner: `claude-lab-nora`
- Status: COMPLETE — FAIL
- Runtime: Pi with `ollama/qwen2.5-coder:7b-16k --offline --no-context-files`
- Objective: re-test whether the 2026-07-18 requalification failure
  (`MAP_System/notes/pi-agent-communication-guide.md`,
  `MAP_System/artifacts/experiments/pi-local-capability-trial-2026-07-18.md`
  Trials C/D) was a true hcom-bridge defect, or a context-budget artifact.

## New evidence motivating this retry (2026-07-27)

- A fresh Pi session on `qwen3.5:4b` (default tag, 4096-token context,
  auto-loaded AGENTS.md/CLAUDE.md) hit "reached the maximum output token
  limit" on every turn and never executed a single command, twice, even
  given an exact two-command instruction.
- A fresh Pi session on `qwen3.5:4b-16k` with `--no-context-files` (freeing
  the budget the auto-loaded docs were consuming) correctly ran the named
  commands and delivered a real hcom event (`#18968`) to `claude-lab-nora`.
- The original Trials C/D used `qwen2.5-coder:7b-16k` (already a 16K tag)
  but required reading four files first (`AGENTS.md`, `MAP_System/AGENTS.md`,
  `pi-agent-communication-guide.md`, the assignment note) with no
  `--no-context-files` flag — plausible budget pressure from the same
  mechanism, not yet ruled out.

## Exact action and pass condition

After reading only this file (no other required reads this round — testing
the mechanism in isolation), send exactly this hcom message:

```bash
hcom send @claude-lab-nora --intent inform --name <your-pi-hcom-name> -- \
  'PI_REQUAL_COMM_ACK model=qwen2.5-coder:7b-16k scope=no-write owner=claude-lab-nora round=2'
```

The owner scores the observed hcom event, not terminal text.

## Strict scope

- Do not create, claim, review, or change a MAP task.
- Do not write, edit, delete, or rename any file.
- Do not inspect active project tasks, use external tools, start subagents, or
  send any other messages.
- Do not begin implementation, analysis, or a follow-up task.

## Stop condition

After the one message, return to listening. If that message cannot be sent,
send no substitute message: stop so the owner can record the missing event.

## Outcome

- No `PI_REQUAL_COMM_ACK` hcom event was observed (checked both `map.db`
  events table and hcom delivery — neither shows it).
- The model loaded correctly (confirmed in `ollama` server logs: 4168 MiB
  buffer, KV cache allocated, "model loaded") and Pi's context usage stayed
  low (11.4%/16k), ruling out the context-starvation mechanism found in the
  same-day `qwen3.5:4b` default-tag failure.
- The session's final visible output was a single malformed fragment,
  `send @pi-lab-luno --intent ack`, missing the `hcom` command prefix and
  never actually invoked as a tool call — generation was cut short or
  garbled, not merely slow.
- Confound: this drill ran concurrently with an unrelated standalone
  `ollama run qwen2.5-coder:7b-16k` sanity check on the same 8GB GPU,
  which produced visible model-swap thrashing in the ollama logs
  (`qwen2.5-coder:7b-16k` loaded, then evicted for `qwen3.5:4b-16k`, load
  cycles taking 15-20s each). The GPU cannot hold two ~4GB+ models
  comfortably at once; the malformed output may be a symptom of that
  contention rather than a clean model/bridge failure. This confound was
  self-inflicted (the owner ran a competing test mid-drill) and makes this
  result inconclusive rather than a clean repeat of the 2026-07-18 failure.

## Verdict

FAIL, but not clean — do not count this as a third confirmed failure of the
`qwen2.5-coder:7b-16k` communication path specifically. A genuinely clean
retry (no concurrent GPU load, nothing else calling `ollama` during the
drill) has not yet been run. Pi remains operationally paused for real work
per `notes/pi-agent-communication-guide.md`; this result does not clear it,
but it also does not rule out a future clean single-model retry.
