# DEC-003 known-bug 2 — LIVE REPRO EVIDENCE (tag-prefix vs bare-instance-name)

- Date: 2026-09-06 (machine clock / hcom event stream stamps 2026-09-07; the
  host is ~1 day ahead — timestamps below are verbatim from the tools)
- Investigator: `vuro` (hcom `maps-lean-vuro`), session
  https://claude.ai/code/session_011UeJqKa3p6nisn4MaK12eG
- hcom: `0.7.25` (`/home/home/.local/bin/hcom`)
- Repo state: fresh clone of `origin/main` @ `c958cf6` (#298), no runtime code
  changed. Branch `investigate/dec003-bug2-name-mismatch`.
- Companion task contract: `work/tasks/dec003-bug2-name-mismatch.md`
- Reproducible driver: see the command block at the end of this file.

## Result: **REPRODUCED** on current `main` + current hcom.

The note's "not confirmed" claim is now confirmed. Both sub-effects observed:
1. the option-C dedup at `HcomAdapter.list_sessions` fails to recognise a
   synthesized stopped record as a dup of its (gone) alive entry for a tagged
   agent, and
2. `RecoverySupervisor._resolve_run_id` returns `None` (→ `run_id: null` on the
   silent-stop incident) for a tagged agent reconstructed via option C, even
   though the events stream *did* carry that agent's `session_id`. **This
   second effect was reached via a *simulated* supervisor lookup** (the driver
   below, steps 4/5, drives `list_sessions` for real but hand-rolls the
   `sessions.get(binding_name)` / `_resolve_run_id` step rather than running a
   full `observe_silent_stops` against a real binding + `run_session_links`
   row); the name-key miss and the empty `session_id` it produces are
   verified, the `None` is the direct, unavoidable consequence of that empty
   `session_id`.

## The two name strings (captured verbatim)

### ALIVE side — `hcom list --json`, `name` field

```
  name='maps-lean-vuro'    base_name='vuro'   tag='maps-lean'
  name='maps-lean-leta'    base_name='leta'   tag='maps-lean'
  name='opcmd-gule-romi'   base_name='romi'   tag='opcmd-gule'
  name='zamu'              base_name='zamu'   tag=None
  name='hore'              base_name='hore'   tag=None
  name='mizo'              base_name='mizo'   tag=None
```

`hcom list --json` (alive) composes `name = "<tag>-<base_name>"` for a tagged
agent. It **also** exposes `base_name` and `tag` as separate keys.

### EVENTS side — `hcom events`, `instance` field (same agents)

`life` / `status` / `message` events **always** carry the BARE `base_name` in
`instance`:

```
{"type":"status","instance":"leta","data":{"session":"949a8a4a-…","new_status":"active",…}}
{"type":"life","instance":"romi","data":{"action":"stopped","reason":"exit:clear"}}
{"type":"life","instance":"gigi","data":{"action":"batch_launched","tag":"maps-coord-succ2","instances":["gigi"]}}
{"type":"life","instance":"zale"  … tag "housekeep" batch_launched, then stopped}
```

`batch_launched` life events carry the tag as `data.tag` and the bare names as
`data.instances` — the tag is **metadata alongside** the bare name, never fused
into `instance`.

### hcom's OWN stopped listing — `hcom list --stopped --all`

Also BARE-name-primary, tag as a parenthetical:

```
  vima (claude tag:maps-lean) 5m ago  [killed by:zamu]  ~/Projects/MAPS_Lean
  gigi (claude tag:maps-coord-succ2) 20h ago  [exit:clear by:session]  …
  zale (claude tag:housekeep) 1d ago  [killed by:viva]  …
```

**Summary:** the alive `hcom list --json` `name` is the *only* hcom surface
that prefixes. Every other surface (events `instance`, `list --stopped` text,
`batch_launched.instances`) is bare + separate tag.

## Which spawn paths are affected

**Every tagged spawn path.** Captured tagged agents whose synthesized
option-C record came back BARE while their alive `list --json` name was
prefixed: `leta`/`vuro` (`tag:maps-lean`), `romi` (`tag:opcmd-gule`), `zale`
(`tag:housekeep`), `demo` (`tag:pr300review`), `luno`/`nezu`/`luna`/`lato`
(pr*review tags), `zura`/`kava`/`buna`/`lulu`/`nima` (`maps-lean-*` tags),
`gigi`/`viva` (`maps-coord-succ*`), plus ~20 more in the 400-event `life`
window.

**Control — untagged agents are NOT affected:** `zamu`, `hore`, `mizo`,
`rafa`, `beto` — `instance` == `list --json` name == `base_name`, no mismatch.

Caveat for one candidate fix (below): `batch_launched.data.tag` is set to the
**tool name** (`claude` / `codex` / `gemini`) when the agent was launched with
no explicit `--tag`. hcom does *not* prefix those in `list --json` (tag ==
tool ⇒ treated as untagged). So `data.tag` alone is not a clean "is this
prefixed" signal — a fix that rebuilds the prefixed name from events must
replicate hcom's exact rule (`tag` present AND `tag != tool`), or it will
wrongly prefix default-tag agents.

## Mechanism (verified against source, line numbers read not trusted)

`runtime/communication/hcom_adapter.py`:
- `_stopped_records_from_events` sets `name = str(event.get("instance") …)` —
  i.e. BARE `base_name`. It never reads a tag, and synthesized records carry
  **no `base_name` key**.
- `list_sessions(include_stopped=True)`, `except json.JSONDecodeError` branch:
  `alive_names = {item.get("name") …}` (PREFIXED for tagged alive agents) and a
  synthesized record is kept only `if record["name"] not in alive_names`. Bare
  `leta` ∉ `{maps-lean-leta, …}` ⇒ **dedup never fires for a tagged agent**.

`runtime/recovery/supervisor.py`:
- `observe_silent_stops` / `tick` build `sessions = {item.get("name"): item …}`
  from `list_sessions(include_stopped=True)` — so alive tagged records are
  keyed prefixed, synthesized stopped records keyed bare.
- Iterate `bindings.items()` → `(worker_id, session_name)`. A recovery binding
  for a tagged agent is created to match the alive `list --json` name (that is
  the only place the recovery operator/coordinator sees the session), i.e.
  **prefixed**. This is a *structural* inference from the `--binding
  WORKER_ID=SESSION_NAME` contract (it takes the operator-visible display
  name, which is tag-prefixed for a tagged agent), **not** empirical evidence:
  no tagged agent has actually been recovery-bound, so there is no live
  "tagged agents currently resolve" case to point at. The implementer
  confirmed the structural inference by tracing `--binding` / `production.py`
  (bindings arg is populated only from the `--binding` CLI, verbatim).
- `sessions.get(session_name, {})` → for a *stopped* tagged agent that is
  `sessions.get("housekeep-zale", {})` → `{}` (the record is under bare key
  `zale`).
- `session_is_live({})` is `False` ⇒ silent-stop **detection still works**.
- `_resolve_run_id(task, {})` → `session_id = ""` → returns `None` **⇒
  `run_id: null` on the incident**, even though `sessions["zale"]` holds the
  real `session_id` (`e3770ba2-…`).

## Captured driver output (step 5)

```
  sessions.get('housekeep-zale') -> {}  <-- MISS
  _resolve_run_id sees session_id = '' -> run_id resolves to None
  (synthesized record actually present under bare key "zale": True ->
     {'name': 'zale', 'session_id': 'e3770ba2-30c0-4f37-81b6-6b56fa01f5f8'} )
```

## Reproducible command block

Run from a fresh clone of `origin/main` with `hcom 0.7.25` on PATH and a
populated `HCOM_DIR` (`/home/home/.hcom` here). Read-only; spawns nothing.

```bash
# 1. ALIVE name vs base_name vs tag
hcom list --json | python3 -c "import json,sys;[print(x['name'],x.get('base_name'),x.get('tag')) for x in json.load(sys.stdin)]"

# 2. EVENTS instance is always bare; tag lives in batch_launched.data.tag
hcom events --last 400 --all --sql "type='life' AND data LIKE '%batch_launched%'"

# 3. hcom's own stopped listing (bare + parenthetical tag)
hcom list --stopped --all | head

# 4+5. drive the option-C fallback + simulate the supervisor lookup
python3 - <<'PY'
from runtime.communication.hcom_adapter import HcomAdapter
a = HcomAdapter(hcom_dir="/home/home/.hcom")
sessions = {x.get("name"): x for x in a.list_sessions(include_stopped=True)}
print("tagged alive keys :", sorted(n for n in sessions if "-" in n))
z = sessions.get("zale")   # tag:housekeep agent, bare synthesized key
print("bare synth record :", {k: z.get(k) for k in ("name","session_id","status")} if z else None)
miss = sessions.get("housekeep-zale", {})   # what a recovery binding would hold
print("binding-name miss :", miss or "{}")
print("run_id would be   :", None if not str(miss.get("session_id") or "").strip() else "RESOLVED")
PY
```

To repro a full end-to-end stop transition (optional; the historical event
stream above is already sufficient): `hcom 1 claude --tag bug2probe` → while
alive `hcom list --json` (note prefixed `bug2probe-<name>`) → `hcom kill
<name>` → `hcom events --sql "instance='<name>'"` (note bare) → re-run step 4.
