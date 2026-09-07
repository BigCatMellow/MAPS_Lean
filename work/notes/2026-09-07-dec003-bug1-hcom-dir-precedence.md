# DEC-003 bug 1 — `HCOM_DIR` (shell) vs `--hcom-dir` (flag) precedence

**Status: operator product-behavior ruling required before any fix.**
Design/analysis note only. No runtime code, tests, or fix in this change.

Source of truth for the bug: `work/notes/2026-09-05-dec003-known-bugs-followup.md`
("Bug 1"), plus the code paths below read directly on branch
`design/dec003-bug1-hcom-dir-precedence` (off `main`, tip `c958cf6`).

---

## 1. Plain-language statement of the bug

`hcom` is the external tool MAPS uses to let agents talk to each other and to
track agent sessions. To keep one checkout's agent traffic from leaking into
another checkout's, `hcom` reads an environment variable, **`HCOM_DIR`**, that
points at a per-project directory (default `./.hcom`). Whoever runs `hcom` — a
human in a shell, or MAPS shelling out to it — can set `HCOM_DIR` to choose
which "world" of sessions/messages they act on.

MAPS has its own command-line option, **`--hcom-dir`**, on `maps recovery-tick`.
Internally every MAPS call to `hcom` goes through one wrapper object,
`HcomAdapter`. That wrapper builds the environment for the `hcom` subprocess
like this (`runtime/communication/hcom_adapter.py:88-91`):

```python
def environment(self) -> dict[str, str]:
    env = os.environ.copy()          # start from the caller's real environment
    env["HCOM_DIR"] = str(self.hcom_dir)   # ...then ALWAYS overwrite HCOM_DIR
    return env
```

The problem is the word *always*. `self.hcom_dir` defaults to `.hcom` and is
**never `None`** — there is no "the caller didn't specify one" state. So even
when nobody asked to redirect anything, the wrapper throws away whatever
`HCOM_DIR` the surrounding shell had exported and replaces it with its own
resolved path.

Concrete failure that already happened (PR #298, DEC-003 option B exercise):
an operator shell had `export HCOM_DIR=/path/to/session-A/.hcom` so that
manual `hcom` commands acted on session A. They then ran a MAPS recovery pass
*without* `--hcom-dir`. MAPS silently pointed `hcom` at `<cwd>/.hcom` instead
of session A. The recovery tick read and wrote the wrong hcom world, produced
nonsense, and it took **two wasted `recovery-tick` attempts** to notice,
because nothing warned. `VERIFIED` (cost figure from the bug note; behavior
from the code above).

### Important framing: `hcom` has no `--hcom-dir`

`hcom --help` and `hcom config --help` (v0.7.25, checked live) show **no
`--hcom-dir` / `--dir` flag anywhere**. `hcom`'s only per-project selector is
the `HCOM_DIR` environment variable. Its documented config precedence is:

```
defaults  <  config.toml  <  env vars
```

So `hcom` itself treats `HCOM_DIR` (an env var) as the *highest*-priority
project selector. `VERIFIED` (live `hcom --help`, `hcom config --help`).

`--hcom-dir` is therefore a **MAPS-only concept**. Its *entire* mechanism of
effect is: MAPS reads the flag, stores it as `hcom_dir`, and `environment()`
converts it into the `HCOM_DIR` env var for the subprocess. There is nothing
else it can do. This matters for the options below: "which wins" is really
"when MAPS forwards an `HCOM_DIR` to `hcom`, whose value does it forward —
the flag's, or the one already in the environment?" `VERIFIED`.

---

## 2. Where `HCOM_DIR` and `--hcom-dir` each come from, and who sets them today

### `HCOM_DIR` (environment variable)

- Set by the operator's shell / hcom launch tooling. In a normal hcom-launched
  agent session it is **always present** — e.g. this analysis session runs with
  `HCOM_DIR=/home/home/.hcom` exported by the hcom launcher. `VERIFIED` (`env |
  grep -i hcom` in this session).
- `hcom` reads it to pick the project directory. `VERIFIED` (hcom docs).
- `HcomAdapter.environment()` starts from `os.environ.copy()` so it is
  inherited — and then unconditionally overwritten (the bug). `VERIFIED`.

### `--hcom-dir` (MAPS flag) and the `hcom_dir=` constructor arg

Every construction of `HcomAdapter` in `runtime/` (grep `hcom_dir`):

| Call site | `hcom_dir` value | Who sets it | Explicit? |
|---|---|---|---|
| `runtime/cli.py:230` | argparse `--hcom-dir`, `default=DEFAULT_HCOM_DIR` (`".hcom"`) | operator types it on `maps recovery-tick`; **argparse fills `.hcom` when omitted** | **cannot tell** — default and explicit `.hcom` look identical |
| `runtime/cli.py:817` → `run_recovery_tick_isolated(hcom_dir=args.hcom_dir, ...)` | passes the argparse value straight through | operator (or default) | see above |
| `runtime/cli.py:781` — `claim` piggyback → `run_recovery_tick_isolated(store, hcom_timeout_seconds=...)` | **does not pass `hcom_dir` at all** → `DEFAULT_HCOM_DIR` = `".hcom"` | **automated**, never operator | always default |
| `runtime/recovery/production.py:355,428,565` (`build_canonical_harness_service`, `run_recovery_tick`, `run_recovery_tick_isolated`) | signature default `DEFAULT_HCOM_DIR = ".hcom"`; forwarded to `HcomAdapter(hcom_dir=...)` at `production.py:402,519,538` | whatever the CLI branch passed | inherits caller |
| `runtime/smoke.py:111` | `HcomAdapter(hcom_dir=root / ".hcom")` — explicit, disposable temp dir | test/smoke harness | always explicit, always a throwaway path |

`hcom_dir` is then `Path(hcom_dir).resolve()` in `__init__`
(`hcom_adapter.py:83`), i.e. resolved against the process cwd.

**Key findings:**

- **No automated flow ever passes a non-default `--hcom-dir` / `hcom_dir`.**
  The only non-default explicit value anywhere is `smoke.py`'s throwaway temp
  path. `VERIFIED` (grep of `runtime/`).
- The `claim` piggyback recovery pass (`cli.py:781`) is automated, runs after
  every successful `maps claim`, and always uses `.hcom` resolved against the
  cwd — **it never consults an exported `HCOM_DIR`**. If an operator's shell
  has `HCOM_DIR` pointed at a real session and they run `maps claim` from a
  directory that has a `.hcom/`, the piggyback pass acts on the wrong world.
  This is the bug firing on a fully automated path, not just on `recovery-tick`.
  `VERIFIED` (code path) / `ASSUMED` (that this has bitten someone — not
  observed, only #298's `recovery-tick` case is on record).
- argparse cannot distinguish "operator typed `--hcom-dir .hcom`" from
  "operator omitted it". Any option that treats explicit-flag differently from
  default **requires a sentinel default** (e.g. `None`) threaded through
  `cli.py` and the three `production.py` signatures. `VERIFIED` (argparse
  behavior; `default=DEFAULT_HCOM_DIR` at `cli.py:230`).
- `environment()` is the single chokepoint — it is the only place `HCOM_DIR`
  is written and the only thing `_run` passes as `env=` (`hcom_adapter.py:109`).
  A fix has exactly one behavioral site to change plus the plumbing to give it
  the information it needs. `VERIFIED` (grep `environment(` / `HCOM_DIR`).

### Does any current passing flow *rely* on the override as-is?

No flow *depends* on `HCOM_DIR` being overwritten. What flows depend on is the
**effective default**: "when no one says otherwise, act on `<cwd>/.hcom`." Every
option below preserves that. The override only changes behavior when the shell
`HCOM_DIR` and the MAPS-side value **disagree**, and today MAPS always wins that
disagreement silently. `VERIFIED` (no non-default automated `hcom_dir`; default
path unchanged under every option).

---

## 3. Options

Throughout: "explicit flag" = operator actually passed `--hcom-dir` (needs the
sentinel); "shell `HCOM_DIR`" = the var was set in the environment MAPS
inherited; "default" = `.hcom` resolved against cwd.

### Option A — explicit flag wins; else inherit shell `HCOM_DIR`; else `.hcom`

`environment()` sets `HCOM_DIR` only when the flag was explicitly given.
Otherwise it leaves whatever `os.environ.copy()` carried (or nothing).

- **Pro:** matches `hcom`'s own precedence model (env vars are a first-class,
  highest-priority selector — we'd stop fighting it). Fixes the #298 case: an
  operator who exported `HCOM_DIR` gets what they asked for. Explicit intent
  (`--hcom-dir`) still overrides, which is the least surprising reading of a
  command-line flag. The `claim` piggyback would now follow the operator's
  shell session instead of guessing cwd — arguably a correctness *gain*.
- **Con:** requires the sentinel-default refactor (`cli.py` + 3 `production.py`
  signatures + `DEFAULT_HCOM_DIR`). Behavior of `maps claim` / `recovery-tick`
  in a shell that has a *stale* `HCOM_DIR` exported (very common — every
  hcom-launched session has one) changes: it now follows that var. If the var
  is stale/wrong, MAPS now follows it silently instead of silently using cwd —
  trades one silent wrong-dir for another, though the operator at least set the
  var themselves.
- **Blast radius:** `hcom_adapter.py` (`__init__` gains an "explicit" flag,
  `environment()` conditional); `cli.py:230` default → `None`; `production.py`
  3 signatures + `DEFAULT_HCOM_DIR` → `None` sentinel + pass-through;
  `tests/test_hcom_adapter.py` (env assertions), `test_recovery_production_trigger.py`,
  `test_hcom_lineage.py`. ~4 runtime files, ~3 test files. No schema, no
  persistence, no external contract.

### Option B — shell `HCOM_DIR` always wins when set; `--hcom-dir` only fills the gap

`environment()` never overwrites an inherited `HCOM_DIR`; the MAPS value is used
only when the var is absent.

- **Pro:** smallest diff — `environment()` becomes
  `env.setdefault("HCOM_DIR", str(self.hcom_dir))`, no sentinel needed. "The
  environment is king" is a defensible ops stance.
- **Con:** **makes `maps recovery-tick --hcom-dir /X` silently do nothing**
  whenever the shell already exports `HCOM_DIR` (which is almost always, in an
  hcom session). A flag that is silently ignored under the common case is worse
  than the current bug — it inverts the "explicit intent wins" expectation.
  Rejected.
- **Blast radius:** 1 line in `environment()` + test updates. Small code,
  large behavioral surprise.

### Option C — on conflict (both set and different): warn once, then apply **the explicit flag**

Like Option A, but when the explicit flag and a differing shell `HCOM_DIR` are
both present, emit a single `_LOGGER.warning` (once per adapter instance, mirror
the existing `self._warned_stopped_nonjson` pattern at `hcom_adapter.py:85`)
naming both paths and which one won, then proceed with the flag's value.

- **Pro:** everything Option A gives, plus the #298 failure mode ("silently
  redirected, no warning") is directly addressed — the operator sees the
  mismatch on the first tick instead of after two wasted attempts. Non-conflict
  cases are unchanged and silent.
- **Con:** slightly more code than A (the warn path + dedup flag). Needs a
  decision on *where* the warning goes (stderr via logging — consistent with
  the module's existing logger; `recovery-tick` emits JSON on stdout so stderr
  is safe and already used for the `claim` piggyback failure line at
  `cli.py:785`). "Warn but continue" can be ignored in non-interactive runs.
- **Blast radius:** Option A's, plus ~10 lines in `environment()` /
  `__init__` and one more test case. Still no external contract change.

### Option D — on conflict: hard error, force the caller to disambiguate

`environment()` (or `__init__`) raises `HcomError` if an explicit `--hcom-dir`
disagrees with a set shell `HCOM_DIR`.

- **Pro:** impossible to act on the wrong world by accident. Strongest
  guarantee.
- **Con:** in this environment **every** hcom-launched session exports
  `HCOM_DIR` (e.g. `/home/home/.hcom`), so any operator who both is in a normal
  hcom shell *and* passes `--hcom-dir` for a specific checkout would hit a hard
  error on a completely reasonable invocation. Turns a routine command into a
  "now unset your env var first" chore. Also makes the automated `claim`
  piggyback fragile: if it ever gains an explicit dir it could start erroring
  mid-`claim`. Too aggressive for how common a set `HCOM_DIR` is.
- **Blast radius:** Option A's plumbing + an exception path; plus every caller
  and test that runs with both set must be audited. Highest test churn.
  `run_recovery_tick_isolated`'s contract ("never raise") would need the error
  caught and converted, adding a branch there too.

### Option E (surfaced by the code) — normalise + compare resolved paths, only act on a *real* difference

Independent of A–D: `HCOM_DIR` inheritance vs flag should compare
`Path(x).resolve()` on both sides, so `.hcom`, `./.hcom`, and an absolute path
to the same directory are treated as equal and never trigger a warning/error.
`__init__` already does `Path(hcom_dir).resolve()`; the inherited var is a raw
string today. This is a modifier to whichever of A/C/D is chosen, not a
standalone answer. `VERIFIED` (`hcom_adapter.py:83`).

---

## 4. Recommendation

**Option C** (which is Option A + warn-once-on-conflict), with Option E's
resolved-path comparison folded in.

Reasoning:

1. **Explicit intent must win.** `--hcom-dir` is a flag an operator typed for a
   reason; silently ignoring it (Option B) or erroring on a near-universal
   condition (Option D) both fail the "principle of least surprise" test. A/C
   keep the flag authoritative.
2. **Stop overriding what wasn't set.** The actual defect is that
   `environment()` has no concept of "unset". Once it does, the natural default
   is to inherit the shell's `HCOM_DIR` — which is also exactly how `hcom`
   itself ranks that variable (`env vars` are its top precedence tier). We
   should align with the tool we're wrapping, not overrule it by default.
3. **The #298 cost was the *silence*, not the precedence per se.** Two wasted
   ticks happened because nothing said "these disagree." The warn-once path
   (C over bare A) spends ~10 lines to make that failure mode loud, using a
   pattern (`self._warned_*`) already in the file. Cheap insurance directly
   targeting the observed cost.
4. **Blast radius is contained.** One behavioral chokepoint (`environment()`),
   a sentinel threaded through 4 runtime files, no schema/persistence/external
   contract touched, and the default "act on `<cwd>/.hcom`" path — which every
   current automated flow actually relies on — is byte-for-byte unchanged.

If the operator wants the absolute minimum diff and is willing to accept that
`--hcom-dir` becomes advisory, Option B is the fallback — but it is not
recommended.

---

## 5. What the mechanical fix would touch (pointer, NOT a task contract)

If the operator picks Option C:

- `runtime/communication/hcom_adapter.py`
  - `__init__`: accept the "was `hcom_dir` explicitly provided" signal
    (either a `None` default meaning "inherit", or a separate boolean); keep
    `Path(...).resolve()` only when a concrete value exists.
  - `environment()`: set `HCOM_DIR` only for an explicit value; when both an
    explicit value and an inherited `HCOM_DIR` exist and their
    `Path.resolve()` differs, `_LOGGER.warning(...)` once (new `self._warned_*`
    flag) then use the explicit value.
- `runtime/cli.py:230`: `--hcom-dir` `default=DEFAULT_HCOM_DIR` → `default=None`.
- `runtime/recovery/production.py`: `DEFAULT_HCOM_DIR` semantics → a `None`
  sentinel meaning "inherit/adapter-default"; signatures at lines ~355, ~428,
  ~565 and the pass-throughs at ~402, ~519, ~538 thread it without
  substituting `.hcom`.
- Leave `runtime/smoke.py:111` as-is (explicit throwaway path — correct under
  every option).
- Tests: `tests/test_hcom_adapter.py` (the `HCOM_DIR` env assertions + a new
  conflict-warning case), `tests/test_recovery_production_trigger.py`,
  `tests/test_hcom_lineage.py`.
- Docs: `runtime/communication/README.md` "Project isolation" section should
  state the precedence (explicit flag > inherited `HCOM_DIR` > `.hcom`).

Rough scope: ~4 runtime files, ~3 test files, 1 doc. No new module, no
persistence, no external/CI contract. One slice.

---

## 6. Claim labels

| Claim | Label |
|---|---|
| `environment()` unconditionally overwrites `HCOM_DIR` (`hcom_adapter.py:88-91`) | VERIFIED |
| `self.hcom_dir` is never `None`; default `.hcom`, `.resolve()` in `__init__` | VERIFIED |
| `hcom` v0.7.25 has **no** `--hcom-dir`/`--dir` flag; only `HCOM_DIR` env var | VERIFIED (live `hcom --help`, `hcom config --help`) |
| `hcom` config precedence is `defaults < config.toml < env vars` | VERIFIED (`hcom config --help`) |
| `--hcom-dir`'s only mechanism of effect is setting `HCOM_DIR` for the subprocess | VERIFIED (grep; `environment()` is the sole writer, `_run` the sole consumer) |
| No automated flow passes a non-default `--hcom-dir`/`hcom_dir` (only `smoke.py`'s temp path) | VERIFIED (grep of `runtime/`) |
| `claim` piggyback (`cli.py:781`) runs automated, never passes `hcom_dir`, uses `<cwd>/.hcom` | VERIFIED |
| The `claim` piggyback has actually redirected someone to the wrong world | ASSUMED (only #298's `recovery-tick` case is on record) |
| `#298` cost 2 wasted `recovery-tick` attempts | VERIFIED (bug note) |
| argparse cannot distinguish explicit `--hcom-dir .hcom` from omitted | VERIFIED |
| Every hcom-launched session exports `HCOM_DIR` (so Option D would error routinely) | VERIFIED for this environment (`env | grep hcom`); ASSUMED to generalize to all operator setups |
| No current flow *depends on* the override; all depend only on the `<cwd>/.hcom` default, preserved by every option | VERIFIED |
| Exact line counts / test list in §5 | ASSUMED (fix not implemented) |
| Whether operator wants precedence (product call) vs. this being a pure mechanical bug | UNKNOWN — the reason this note exists |

---

## Resume prompt

You are picking up DEC-003 bug 1 (`HCOM_DIR` vs `--hcom-dir` precedence). The
analysis is done and lives in
`work/notes/2026-09-07-dec003-bug1-hcom-dir-precedence.md` on branch
`design/dec003-bug1-hcom-dir-precedence` (PR open against `main`, under the
3-day operator merge hold — do not merge). The note recommends **Option C**
(explicit `--hcom-dir` wins > inherited shell `HCOM_DIR` > `.hcom` default,
with a warn-once on a real conflict and resolved-path comparison). Next step is
an **operator ruling** on which option to adopt — this is flagged as a
product-behavior call, not a mechanical fix, because `hcom` treats `HCOM_DIR`
as its top precedence tier and MAPS currently overrules it silently. Once the
operator rules, shape a one-slice fix task from §5 of the note (do not treat
§5 as a contract as-is). Do not touch any `runtime/` file, test, or checklist
until the ruling lands. Coordinator is `lira` (hcom).
