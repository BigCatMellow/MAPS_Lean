<!-- hpom: file: artifacts/reviews/task221-review-gome.md -->
<!-- hpom: project: MAP -->
<!-- hpom: state_owner: claude-lab-gome -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-18 -->
<!-- hpom: verified_against: TASK-221 independent review incl. security-framed pass -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# Review Record: TASK-221

```text
task_id:      TASK-221
reviewer:     claude-lab-gome
review_date:  2026-07-18
task_owner:   codex-lab-lilo
```

Reviewer != owner; reviewer contributed no implementation (only incident
data points from the affected session, which makes this reviewer a good
witness for the fix, not a conflicted author). Includes the
security-framed second pass required for write-capable components: this
supervisor parses untrusted transcript text and writes durable agent
state + sends nudges.

## Verdict

```text
APPROVED
```

## Acceptance Criteria Check

| # | Criterion | Result | Evidence |
|---|---|---|---|
| 1 | Fresh live-session limit records detected once, reset parsed, durable standby/out_of_tokens + ISO resume_after, no model participation | PASS | Read `read_fresh_transcript_limit`/`detect_fresh_transcript_limits` directly: provider-provenance gate, timestamp freshness window (±60s/-900s), reset parse with 5-minute grace, SHA-256 line fingerprint for exactly-once handling. Focused test `test_fresh_live_transcript_limit_is_detected_once` covers it; 32/32 tests reproduced by this reviewer. |
| 2 | Stale/quoted records rejected; no premature nudges | PASS | `test_stale_or_quoted_transcript_limit_is_ignored` read directly — covers all three attack shapes: 6-hour-old genuine provider record, non-marker prose mentioning resets, and the exact marker sentence quoted WITHOUT provider provenance flags. My own live `--once --dry-run` against ~6 active sessions: zero detections, exit 0. |
| 3 | Due agent gets normal bounded-retry RnS path; status/mirror consistency | PASS | SQLite-first writes with mirror regeneration confirmed in code; live empirical evidence: this reviewer's own session genuinely hit an overnight limit, was recorded, and received one correct due-time nudge (#3091) — versus three false-positive nudges under the pre-TASK-221 watcher on 2026-07-17, all of which this reviewer reported as incident data at the time. |
| 4 | systemd user service enabled, reboot-safe, 300s, verified active; no 30s poller, no one-shot timers | PASS | Reproduced live: `is-enabled`→enabled, `is-active`→active, ExecStart shows `--interval 300`, pid 304093 running since 2026-07-17 20:55, `list-timers 'map-rns-*'`→0 timers. |
| 5 | Focused + full suite; evidence documents live and failure paths | PASS | 32/32 focused reproduced. Full-suite 65/67 with the two failures verifiably pre-existing and out of scope: `validate_risk_registers` flags ClearFront's register (this reviewer's own earlier edit — will be fixed by the reviewer separately, not TASK-221's debt), and the environment-sensitive `command_center_intake_test`. |

## Forbidden Changes Check

| Forbidden change | Status |
|---|---|
| LLM/Ollama participation in monitoring | NOT BROKEN — pure deterministic parsing; no model call anywhere in the watcher path. |
| High-frequency polling | NOT BROKEN — 300s interval confirmed live in the running process args. |
| Bypassing SQLite-first state | NOT BROKEN — standby/out_of_tokens and wake-clears both write DB first, then regenerate mirrors. |
| Output-path collision left unresolved | NOT BROKEN — the TASK-210 collision was resolved by retiring TASK-210 as superseded with a dedicated supersession note holding its remaining output ownership; graph + mirror validators pass. |

## Security-Framed Pass (trust boundaries)

The core injection risk — arbitrary text (hcom relays, tool output, an
agent quoting the marker sentence) flipping a live agent's durable state
— is handled by requiring provider-synthetic provenance flags
(`error=rate_limit` / `isApiErrorMessage` / `apiErrorStatus=429` for
Claude) that quoted prose cannot carry, plus marker match, parseable
reset time, and the 15-minute freshness window. Failure mode on
malformed input is skip-and-continue (JSON decode errors ignored,
unparseable resets reported once per `test_unparseable_reported_once`).

One RECOMMENDED (non-blocking) note: the Codex provenance branch accepts
`type=event_msg` with `payload.type` in `{agent_message, error,
turn_aborted}`. `agent_message` is the broadest of these — a Codex
agent whose own prose contained the exact marker plus a parseable reset
time within the freshness window could in principle self-mark standby
until that time. Impact is bounded (self-correcting at reset, no data
loss, strictly better than the pre-221 false-nudge behavior) and the
breadth appears necessary for how Codex surfaces real limits, but if
Codex's transcript format offers a more specific provider-error record,
narrowing this branch later would close the residual sliver.

## Files Reviewed

- `MAP_System/scripts/limit_watcher.py` (detection/provenance/persistence paths, read directly)
- `MAP_System/tests/test_limit_watcher.py` (executed 32/32; quoting/staleness tests read line-by-line)
- `MAP_System/artifacts/tests/rns-persistent-supervisor.md`
- `MAP_System/artifacts/tests/task-210-superseded-by-task-221.md` + `MAP_System/tasks/TASK-210.json`
- `MAP_System/templates/install/systemd/map-rns-watcher.service` (via live systemd state)
- `MAP_System/tasks/TASK-221.json`

## Findings

No `BLOCKER` or `REQUIRED` findings. One `RECOMMENDED`: consider
narrowing the Codex `agent_message` provenance acceptance if a more
specific provider-error record type exists (see Security-Framed Pass).
