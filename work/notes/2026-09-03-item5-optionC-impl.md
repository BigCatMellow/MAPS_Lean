# Item 5 / Option C impl — rebuild stopped-session records from `hcom events`

- Branch: `impl/item5-optionC-events-stopped-records`
- Spec: `work/notes/2026-09-03-hcom-list-stopped-nonjson-repair.md` **Part B** (Part A / option D
  guard already merged, PR #269 `a6ad820`).
- Scope: `runtime/communication/hcom_adapter.py` + `tests/test_hcom_adapter.py` only. No change to
  `runtime/recovery/`, `runtime/state/run_lineage.py`, or `runtime/harness/adapters/hcom.py`.

## Step 0 — empirical probe (installed `hcom 0.7.25`, `/home/home/.local/bin/hcom`, read-only)

| Question | Finding |
|---|---|
| `hcom events --json` shape | **There is no `--json` flag.** `hcom events` emits **JSONL** (one JSON object per line) by default; `--json` is an "unexpected argument". `HcomAdapter.read_events` already parses this correctly. |
| Event record shape | Top-level keys `{id, ts, type, instance, data}`. `instance` = agent **name**. `type` ∈ `message | status | life`. In a 500-event sample: 440 `status`, 44 `message`, 16 `life`. |
| `life` stop event | `{"type":"life","instance":"<name>","ts":"...","data":{"action":"stopped","by":"session|subagent","reason":"exit:clear|idle|timeout|..."}}` — carries **name + reason + ts, NO session id**. |
| `status` event, top-level session | `data` carries `"session":"<uuid>"` (this is hcom's `session_id`) on **every** transition (prompt / listening / `tool:*` / deliver). Also `new_status`, `new_context`, `writer`. A stop shows `new_status:"inactive"`, `new_context:"exit:clear"` (or other `exit:*`). |
| `status` event, subagent | `data` carries `"agent_id":"a…hex"` and **`"session": null`** — never a session uuid. Subagent exit shows `new_status:"inactive"`, `new_context:"exit:idle"`. |
| Authoritative `name → session_id` | The `data.session` field on any `status` event for that `instance`. Stable for the life of the session; emitted many times. This is the correlation key. |
| `hcom list --json` (alive) | Returns a JSON array; **each record has `session_id`** (plus `name`, `status`, `status_age_seconds`, `status_context`, `process_bound`, `launch_context`, …). |
| `hcom list --json <name>` for a stopped name | `Error: Not found: <name>` (non-zero exit). A stopped session is **not** individually queryable — `hcom events` is the only structured source. |
| `hcom list --stopped [--all] [--json]` | Human text, exit 0, `--json` ignored (confirmed — this is the item-5 blocker, hcom's design). |

**Verdict:** events reliably supply `name ↔ session_id` **for top-level sessions** — the only
kind recovery binds (`observe_silent_stops` works on `worker_id → session_name`, i.e.
`hcom claude` sessions, not subagents). Option C is viable. **No STOP condition hit.**

## Design

### Synthetic stopped-session record shape
Mirrors the alive `hcom list --json` keys the recovery path actually reads:

| key | value | consumed by |
|---|---|---|
| `name` | agent name (`instance`) | merge key; `session_name` bookkeeping; `_find_by_session_id` name check |
| `session_id` | from most recent `status` event with non-null `data.session`; **omitted if unknown** | `RecoverySupervisor._resolve_run_id` → `resolve_session_run(project_id,"hcom",session_id)`; `HcomSessionAdapter._find_by_session_id` |
| `status` | `"inactive"` (not in `LIVE_STATUSES`) | `session_is_live` → `False`; harness `_STATUS_MAP` |
| `process_bound` | `False` | `session_is_live` (belt-and-suspenders) |
| `status_context` | the `exit:*` reason string | advisory |
| `stopped` / `stop_reason` / `stop_ts` | advisory extras, namespaced to avoid alive-key collision | advisory only |

### Merge policy
- The alive `hcom list --json` list wins on any name collision — a synthetic record is added
  **only for a name not in the alive list**.
- A synthetic record is produced for every name with a stop signal in the lookback window: a
  `life` event `data.action=="stopped"` **or** a `status` event `data.new_status` in
  `{"inactive","stopped"}`. A later live transition (`life action in {ready,started,created}`
  or any non-stopped `status.new_status`) for the same name clears a stale stop.
- Subagent guard: if the stop `status` event explicitly carried `session: null` and no real
  `session` id was ever seen for that name, the record is dropped (subagents are never
  recovery targets).

### Lookback N = `_STOPPED_EVENTS_LOOKBACK = 2000`
`hcom events --last N`. Step-0 sample: a busy 3-agent coordinator produced ~300 events/hour
aggregate, overwhelmingly `status` events (each stamps its session_id). 2000 events ≈ 6h of
that history — comfortably longer than any plausible recovery inter-tick gap plus the
silent-stop probe delay — and well under `read_events`'s hard cap of 5000. Time-bounding via
`--after` was rejected: `--last` is already the `read_events` contract and adds no clock-skew
surface.

### Placement
`HcomAdapter._stopped_records_from_events()`, called from `list_sessions` **only** inside the
existing `except json.JSONDecodeError` branch — replacing option D's "return alive-only" with
"return alive + events-derived stopped". Kept intact: the warn-once flag, the
JSONDecodeError-narrowed catch, `_parse_session_list` on the alive fallback (still fails
closed on malformed alive JSON). The helper never raises — on any `HcomError` it logs and
returns `[]`, degrading to exactly the option-D (Part A) behavior.

### Defense-in-depth only
On any hcom build that **does** honor `--stopped --json`, the `json.loads` in `list_sessions`
succeeds, the `except` branch is never entered, and `_stopped_records_from_events` is never
called. This path exists solely for builds (0.7.25 and, per `hcom list --help`, every current
build) that ignore `--json` for `--stopped`.

## Blast radius — "unresolved run_id still possible when…"
A silent-stop incident still opens with `run_id = None` when the stopped session **both
started and stopped entirely before the lookback window** (> 2000 events / ~6h ago) — no
`status` event carrying its `data.session` remains, so the synthetic record omits
`session_id` and `_resolve_run_id` returns `None`. This is strictly smaller than the Part A
exposure (which lost lineage for *every* silent stop on a non-JSON build); it is unchanged
from Part A in outcome (advisory-evidence + canonical-lineage binding degrade, they do not
misbehave). Subagent stops (`session: null`) never had a resolvable `run_id` and are not
recovery targets, so their exclusion changes nothing.

## Reviewer flag (LEASE_EXPIRED vs HOOK_DENIED)
`_CANONICAL_DENIAL_CODES = {"HOOK_DENIED","APPROVAL_REQUIRED"}` (`runtime/recovery/supervisor.py:24`)
does not literally contain `LEASE_EXPIRED`; `runtime/recovery/production.py:394` says the
LBW-EXERCISE-1 denial is "most likely via `LEASE_EXPIRED`". **Option C does not touch this
path** — it only restores the `session_id` that `_resolve_run_id` needs to bind an incident
to its run. Whether the enforced pass emits a routable `resume_denied` on LBW-EXERCISE-1
depends on whether `LEASE_EXPIRED` surfaces as `resume_denied` or the guard-veto path
(→ `HOOK_DENIED`) fires. Left for review to confirm against current evidence.

## Verification
- `python3 -m unittest tests.test_hcom_adapter tests.test_recovery_supervisor tests.test_harness_hcom_adapter -v` — GREEN (90 tests).
- New frozen regression test: `test_list_sessions_include_stopped_reconstructs_from_events`.
- Existing option-D test `test_list_sessions_include_stopped_survives_nonjson_stopped_output`
  kept; its call-sequence assertion was loosened (it now also issues an `events` call after
  the alive fallback — a genuine contract change) but its behavioural assertions (no raise,
  alive-only payload when there are no stop signals) are unchanged.
- Full suite: see PR body.
- `recovery-tick` / `--enforce-*` NOT run (stop condition, same as #269).
