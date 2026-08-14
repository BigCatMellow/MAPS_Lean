# Pi Agent Communication Guide

Status: REQUALIFICATION FAILED — operationally paused
Owner: codex-lab-lilo
Applies to: visible `pi-lab-*` and `helper-pi-*` hcom sessions

## Purpose

Pi is a visible local diagnostic lane, not an operational MAP helper. It
communicates through hcom and durable MAP files; terminal narration is not a
project handoff.

Launch the normal Pi lab with the local-only default
`ollama/qwen2.5-coder:7b-16k` and Pi's `--offline` mode. This avoids
hosted-provider quota use. Local models still have context and output ceilings,
so an "out of tokens" style message can indicate local
generation/context pressure, not a cloud subscription limit; report the exact
model and error to the owner.

## Operational pause

The operator paused Pi for normal work on 2026-07-18 after repeated local
context/output exhaustion and two failed bounded trials. The operator
subsequently authorized one fresh, visible requalification on
`qwen2.5-coder:7b-16k`; this is the sole exception. Do **not** assign Pi to a
task, review, handoff, routing decision, or durable-file output; do not list
it as a dependency or capacity source. The exception is a no-write
communication drill named in
`MAP_System/inbox/helpers/pi-requalification-communication-2026-07-18.md`.

Local-only prevents hosted quota consumption. It does not make the model
reliable and does not remove its context-window or maximum-output limits.

## If an operator-authorized diagnostic is requested

1. Read the named assignment note completely. It names the only permitted
   output path and prohibited paths.
2. Verify the assignment path is **not** the output path. Never edit the
   assignment note, task record, decision log, or policy file unless the
   assignment explicitly permits it.
3. Send the accountable owner a concise hcom acknowledgement:

```bash
hcom send @codex-lab-lilo --intent inform --name <your-pi-hcom-name> -- \
  '!ACK <scope>; output=<exact-permitted-path>; stop=<stopping-condition>'
```

Use the owner named in the assignment instead of `@codex-lab-lilo` when it is
different. Use `--reply-to <id>` only when answering an hcom message whose
intent was `request`.

## During a diagnostic

- Send `--intent inform` to the owner only for a material progress point,
  completed artifact, or exact blocker. Include the durable path and current
  state; do not replay reasoning history.
- Use `--intent request` only to `@bigboss` for an operator decision,
  approval, blocker, conflict, privacy/scope risk, or question. Format it:
  `Issue`, `Options`, `Recommendation`, `Needed`.
- Do not request routine clarification from the operator. Name the exact
  blocker to the owner and stop if the task cannot proceed safely.
- Do not claim completion until the permitted artifact exists and any required
  command has been run. Terminal text alone is not completion.

## End of a diagnostic

Send one factual completion message:

```bash
hcom send @codex-lab-lilo --intent inform --name <your-pi-hcom-name> -- \
  'done=<scope>; artifact=<exact-path>; verify=<result>; blocker=none'
```

Then return to listening. The core owner integrates, reviews, or rejects the
result. Pi never approves a task, changes a task state, or treats a local-model
draft as a final decision.

## Current limit

There is no proven Pi work lane. The 2026-07-18 4B trial confused an assignment
path with an output path. The 9B no-tools draft produced an invalid MAP/1 shape
and a false delivery claim. A future requalification would need an explicit
operator decision, a terminal-only exact-match drill, and three clean trials
before any scope beyond a disposable diagnostic is considered. The 7B-16K
drill failed: it did not send the required observed hcom acknowledgement and
its transcript made a malformed/unobserved delivery claim. A later fresh
7B-16K health check displayed the exact acknowledgement in its terminal but
again produced no outbound hcom event. This confirms that terminal text is not
delivery evidence and that Pi's hcom bridge is not verified. Do not start
another automatic retry. A fresh visible instance may be considered only under
a new operator-authorized, separately recorded drill.

## References

- `AGENTS.md`
- `MAP_System/AGENTS.md`
- `MAP_System/notes/local-model-helper-guide.md`
- `../optimal-agent-communication-guide.md`
- `MAP_System/inbox/helpers/pi-minimal-lifecycle-walkthrough-2026-07-18.md`
