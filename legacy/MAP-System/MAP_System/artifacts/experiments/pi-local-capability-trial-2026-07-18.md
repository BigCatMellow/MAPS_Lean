# Pi Local Capability Trial — 2026-07-18

## Purpose

Determine whether Pi can be an independently useful visible local-helper lane,
and distinguish hosted-token limits from local model/context limits.

## Runtime facts

- Pi executable: `/home/mellow/.local/bin/pi`.
- Pi offline registry lists local Ollama models including
  `qwen3.5:4b`, `qwen3.5:9b`, `qwen2.5-coder:7b`,
  `qwen2.5-coder:7b-16k`, and `qwen2.5-coder:1.5b`.
- `ollama list` confirms all four are locally installed; available disk space
  is approximately 1.4 TB. No model download is needed for this trial.
- The visible 9B Pi session reported `qwen3.5:9b` and a 128K context meter.
  It was local, not consuming a hosted provider quota. Local context/output
  limits remain possible and must not be mislabeled as subscription exhaustion.

## Trial A — 4B read-only lifecycle artifact

| Field | Result |
|---|---|
| Model | `ollama/qwen3.5:4b` |
| Intended output | `artifacts/experiments/pi-minimal-lifecycle-walkthrough-2026-07-18.md` |
| Observed behavior | Attempted to write the assignment note in `inbox/helpers/` instead of the permitted output. |
| Containment | Owner restored the assignment note; no canonical task, policy, decision, or MAP state was changed. |
| Result | FAIL — does not meet file-path compliance. |

## Trial B — 9B no-tools MAP/1 draft

| Field | Result |
|---|---|
| Model | `ollama/qwen3.5:9b`, visible terminal, `--no-tools` |
| Intended output | One terminal-only MAP/1 handoff draft from a supplied factual packet. |
| Observed behavior | No filesystem mutation, but draft omitted the required `@MAP/1` header, changed `TASK-220` to `TASK-20`, invented `mupo`/`lipo` identities, and claimed an hcom message had been sent even though no outbound hcom event existed. |
| Result | FAIL — safer than Trial A but not reliable for structured coordination without core correction. |

## Decision-use result

Pi is not an operational helper. On 2026-07-18 the operator directed MAP not
to count on Pi after repeated local "out of tokens" behavior. It must not be
assigned a task, review, handoff, routing decision, or durable-file output,
and it must not be included in capacity or dependency planning. It is **not**
suitable for autonomous file writes, formal hcom handoffs, task ownership,
review, release, task-critical analysis, or routine draft generation.

The normal launcher and hcom Pi defaults now use
`ollama/qwen2.5-coder:7b-16k --offline` under the operator-authorized
requalification. This is a local-only runtime correction that prevents
hosted-provider quota use, not evidence that Pi is a reliable worker or that
local context/output limits cannot occur.

## Trial C — 7B-16K no-write communication requalification

| Field | Result |
|---|---|
| Model | `ollama/qwen2.5-coder:7b-16k`, Pi `--offline`, fresh visible `wezterm-tab` session |
| Assignment | `MAP_System/inbox/helpers/pi-requalification-communication-2026-07-18.md` |
| Permitted output | A single observed hcom acknowledgement; no filesystem write by Pi |
| Expected pass condition | Pi reads the guide/assignment and sends the exact required hcom acknowledgement within the bounded session. The core owner observes the event. |
| Observed result | FAIL. Pi session `pi-lab-nami` received the prompt and assignment but no `PI_REQUAL_COMM_ACK` event was emitted. Its hcom transcript instead contained a malformed/unobserved delivery claim. |
| Evidence | hcom events show prompt/delivery activity through event `3822` but no acknowledgement; owner inspected the two-message Pi transcript before the terminal closed. |
| Containment | The session was ended. No Pi filesystem write, task claim, review, routing, or authority action occurred. |
| Authority | None. No task claim, review, handoff, routing, release, or durable-file mutation. |

## Trial D — minimal visible health check

| Field | Result |
|---|---|
| Model | Fresh visible Pi session vema showed qwen2.5-coder:7b-16k in its terminal. |
| Assignment | MAP_System/inbox/helpers/pi-healthcheck-vema-2026-07-18.md |
| Intended output | One exact hcom inform, with no file access or project work. |
| Terminal behavior | The model displayed the exact acknowledgement with an [hcom:vema] prefix. |
| Observed hcom behavior | FAIL. Events show incoming delivery/listening activity through event 4015, but no outbound Pi message event. |
| Result | The local model is responsive, but Pi's hcom delivery bridge is still not verified. Terminal text is not treated as a sent message. |
| Authority | None. Pi remains excluded from task, review, handoff, release, routing, durable-file, and capacity work. |

## Next experiment

Do not retry a general task. Trial D confirms that a visible local model
response alone does not establish Pi hcom delivery. A further retry requires a
new operator-authorized assignment and a fresh visible instance; no
durable-file output is implied. Only after three separately observed clean
no-write hcom deliveries may a core owner propose a further requalification.

## 2026-07-27 — context-budget finding and Trial E/F (operator-authorized)

Prompted by the operator asking why local models see so little use, `nora`
ran three further bounded trials.

| Field | Result |
|---|---|
| Trial E model | `ollama/qwen3.5:4b` (default tag, 4096-token context), Pi visible, AGENTS.md/CLAUDE.md auto-loaded |
| Assignment | Read two named files (`events.jsonl` tail, `current-state.md`), send one hcom digest |
| Observed behavior | Hit "reached the maximum output token limit" on every turn before executing a single command; never read either file or sent a message. Retried once with a maximally explicit instruction — same failure. |
| Root cause | The 4096-token context is shared between Pi's auto-loaded `AGENTS.md`/`CLAUDE.md` context, the conversation, and generation. Little budget was left for output. |
| Result | FAIL — mechanical (output-budget exhaustion), not a quality or hallucination failure this time. |

| Field | Result |
|---|---|
| Trial F model | `ollama/qwen3.5:4b-16k` (16K-context tag, already installed) with `--no-context-files` |
| Assignment | Same as Trial E |
| Observed behavior | Read both named files directly (no unguided exploration), stayed under 84% of its context budget, and sent a real hcom event (`#18968`) in the required format. |
| Accuracy check | One of two factual claims verified correct against canonical `map.db` state at time of send (`TASK-278 APPROVED`); the second (`TASK-280` status) was stale by the time of verification — plausible point-in-time snapshot lag from concurrent work by other agents, not a fabrication. |
| Result | PASS for mechanics (read → synthesize → deliver via hcom). First confirmed clean Pi hcom delivery under any model tested to date. Content quality is draft-only per policy, as intended; a core agent must still review before acting on it. |

**Finding:** the 2026-07-18 verdict that "Pi's hcom bridge is not verified"
may have conflated two distinct problems: a genuine bridge/reliability issue,
and a context-budget misconfiguration (default short-context tag plus
auto-loaded onboarding docs). Trial F shows the bridge itself works when the
model isn't context-starved. This does **not** reverse the pause on
`qwen2.5-coder:7b-16k` for real work — see the same-day Trial G below, which
re-tested that specific model and did not get a clean result.

| Field | Result |
|---|---|
| Trial G model | `ollama/qwen2.5-coder:7b-16k` with `--no-context-files` (round-2 requalification, `MAP_System/inbox/helpers/pi-requalification-communication-2026-07-27.md`) |
| Observed behavior | Model loaded correctly (confirmed in `ollama` logs), context stayed low (11.4%/16k), but final output was a single malformed fragment (`send @pi-lab-luno --intent ack`, missing the `hcom` prefix, never invoked as a tool call). No hcom event was observed. |
| Confound | Ran concurrently with an unrelated standalone `ollama run` sanity check on the same 8GB GPU, which caused visible model-swap thrashing in the ollama logs. Self-inflicted by the owner mid-drill. |
| Result | FAIL, but inconclusive — do not count as a third clean failure of this model's communication path. A genuinely uncontended retry has not been run. |

## Practical takeaways (2026-07-27)

- Prefer the installed `-16k` tags (`qwen3.5:4b-16k`, `qwen2.5-coder:7b-16k`)
  over default short-context tags for any Pi work, and launch with
  `--no-context-files` when the assignment already states everything the
  model needs — auto-loaded `AGENTS.md`/`CLAUDE.md` content competes with
  output budget on small context windows.
- The 8GB GPU (RTX 2060 Super) cannot comfortably hold two ~4GB+ models at
  once; running a second `ollama` command (even a one-off sanity check)
  while a Pi drill is in flight causes model-swap thrashing that can degrade
  or corrupt that drill's output. Do not run concurrent ollama load during a
  scored trial.
- `notes/local-model-helper-guide.md`'s capability map should be corrected:
  `qwen3.5:4b` is draft-only *when launched with the 16K tag and
  `--no-context-files`*; the default 4096-token tag is not reliably usable
  for anything beyond a single short exchange.
