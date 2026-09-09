# H4 — first production exposure of the enforced resume-validation gate — SUCCESS

**Status: SUCCESS.** `maps recovery-tick --enforce-validation` was run for the
first time against a real stalled incident whose bound environment made the
`quick` validation tier concretely fail. The gate parked the incident in the
distinct `blocked_validation` state **before any resume call**, keyed on a
genuine `{"attempted": true, "passed": false}` quick-tier result — no resume
fired, the transient `attempt` budget was untouched, and a control lane with the
flag omitted proceeded to a resume attempt on a byte-identical incident. This is
the direct analog of **PR #303** (6.16 guard first exposure) and **PR #320**
(6.4 `.stop()` first exposure).

Executed 2026-09-09 by `meme` (session `maps-h4-exercise-meme`), dispatched by
coordinator `leto` (session 39), hcom request #94399 (scope) / #94431 (proceed).
No prior involvement with the H4 / resume-validation-gate work or its authors
(`meme` is not `nazi`, who ran the sibling 6.4 exercise).

The gate code itself (`RecoverySupervisor(validation_blocks_resume=…)` +
`_quick_validation_failed` + the `tick()` park branch + `--enforce-validation`)
landed earlier as the first slice of
`work/notes/2026-08-31-resume-validation-gate-design.md` and was **not**
re-implemented here. No `runtime/` change was made or needed.

Frozen as regression case
`CASE-559ff1df61eb6c829b55c641b3ae0a4450f8dca9bfcc218e76df84fd53332a22` (`work/regression-cases/`).

---

## 1. Clone and baseline

Fresh classifier-safe clone `git clone https://github.com/BigCatMellow/MAPS_Lean
/tmp/exh4-473920`, branch `exercise/h4-validation-gate-first-exposure`.

`origin/main` was `18b064c` at clone time — two documentation-only commits
(`d042ab2` "Add live development status wiki page", `18b064c` "Add Development to
wiki navigation") had landed on `main` directly since the session-38 handoff tip
`25c7729`; neither touches `runtime/`, `tests/`, or the gate. All gate callsites
verified at this HEAD.

Green baseline on the clone (blocking foreground, no Monitor):

```
$ python3 -m unittest tests.test_recovery_supervisor
Ran 76 tests in 145.621s
OK

$ python3 -m runtime.smoke ; echo $?
... "ok": true
0
```

### The forced-failure spec (test artifact — explicitly untracked)

A minimal valid `EnvironmentSpec` was written to `h4-exercise-spec.json` **at the
clone root**, whose `validation.quick` is a single command that deterministically
exits non-zero:

```json
"validation": {
  "quick": ["sh -c 'echo H4-EXERCISE: deliberate quick-tier failure, exit 1 >&2; exit 1'"],
  "normal": [], "full": []
}
```

`environment_spec_hash` = `2948d8d9211f9b34522cf41faa1a522d73041ec8b778f833c05a6eebce363201`.

**This file was never `git add`-ed** — it is a throwaway test artifact that
existed only in the working tree of the clone. `git status` on the exercise
branch shows it as untracked, not staged, and it is **not** part of this PR.
It is reproduced above in full so a reviewer can see exactly what made the tier
fail. The failure is a genuine `subprocess` exit-1 from `run_validation_tier`,
not a mock:

```
$ python3 -c "from runtime.environment.spec import load_environment_spec; \
  from runtime.environment.validation import run_validation_tier; \
  print(run_validation_tier(load_environment_spec('h4-exercise-spec.json'),'quick',repo_root='.').passed)"
False
```

---

## 2. The three lanes

One shared task DB (`/tmp/exh4-473920/.maps/state/maps.db`, `maps init`, no
operator registry). Three lanes, each with its own cwd (`recovery.json` is
written relative to cwd), its own real untagged hcom session spawned in a fresh
`/tmp` scratch dir (never under `~/Projects/MAPS_Lean` or `.claude/worktrees/`),
bound via `maps run bind-session` to an `EXPLICIT` run/session lineage, then
killed (`hcom kill`, SIGTERM) to simulate a real stall. Untagged names sidestep
the DEC-003 bug-2 class (`name == base_name == events instance`), so `run_id`
resolved on every incident.

| lane | task | session | contract `environment` block | `recovery-tick` flag |
|---|---|---|---|---|
| **A — blocked** | `H4EXP-A` | `gine` `aac0a2c7-…` | `spec_ref: h4-exercise-spec.json` | `--enforce-validation` |
| **B — control** | `H4EXP-B` | `laza` `e5985a5d-…` | `spec_ref: h4-exercise-spec.json` (same) | *(omitted)* |
| **C — attempted:false** | `H4EXP-C` | `zelu` `1705b7a2-…` | *(none)* | `--enforce-validation` |

`maps flow start --repo-root /tmp/exh4-473920` recorded a real
`run_environment_evidence` row for A and B (`recorded_by = "maps-flow-start"`,
the PR #204 production writer; `environment_spec_hash` matches the spec above)
and **no** row for C (no `environment` block → the validator later reports
`no_spec_bound`).

Tick invocation (lane A; B omits the flag; all three share the rest):

```
python3 -m runtime.cli --db <db> recovery-tick --enforce-validation \
  --repo-root /tmp/exh4-473920 --hcom-dir /home/home/.hcom \
  --binding h4exp-a-w=gine
```

`--hcom-dir /home/home/.hcom` explicit per DEC-003 bug-1 (the flag defaults to
`.hcom` resolved against cwd, not the real global transport). **No
`--enforce-canonical-run`** — `--enforce-validation` requires only `--repo-root`
(`runtime/cli.py:1011`); the gate sits in `tick()` before any
`HarnessService`/direct-`hcom.resume()` call, so no canonical wiring is needed.

### Cadence

`silent_stop_probe_delay_seconds` is `900` and not CLI-plumbed, so every
re-probe was a real ~900 s wall-clock wait.

| tick | time (UTC) | lane A (gine) | lane B (laza) | lane C (zelu) |
|---|---|---|---|---|
| 1 baseline | 16:12:10–11Z | `last_live {gine:true}`, no incident | `{laza:true}`, none | `{zelu:true}`, none |
| — kill — | 16:12:1xZ | `hcom kill gine` | `hcom kill laza` | `hcom kill zelu` |
| 2 transition | 16:12:27–28Z | incident `RNS-6beafd077363`, `resume_after +900s`, `run_id` resolved | `RNS-9b2437533fe7` | `RNS-3e71e2dd5aaa` |
| 3 resume decision | 16:28:48 / :49 / 29:00Z | **`resume_blocked_validation`** | `resume_failed` (resume attempted) | `resume_failed` (resume attempted) |
| 4 | 16:44:24Z | **`resume_blocked_validation`** (`validation_blocks: 2`) | — | — |
| 5 | 17:00:06Z | **`fail` / `validation_block_persistent`** (`validation_blocks: 3`) | — | — |

Lanes B and C revived their killed sessions on the resume attempt (expected —
`hcom r --go <name>`); both were killed immediately afterward (`hcom kill laza
zelu`), per the DEC-003 precedent.

---

## 3. Lane A — the parked action dict (VERIFIED, captured verbatim, tick 3)

```json
{
  "action": "resume_blocked_validation",
  "reason": "quick_validation_failed",
  "harness_resume": null,
  "incident_id": "RNS-6beafd077363",
  "validation_blocks": 1,
  "resume_validation": {
    "attempted": true,
    "passed": false,
    "tier": "quick",
    "environment_spec_hash": "2948d8d9211f9b34522cf41faa1a522d73041ec8b778f833c05a6eebce363201",
    "result": {
      "tier": "quick", "passed": false, "skipped": [],
      "ran": [{
        "command": "sh -c 'echo H4-EXERCISE: deliberate quick-tier failure, exit 1 >&2; exit 1'",
        "found": true, "returncode": 1,
        "output": "H4-EXERCISE: deliberate quick-tier failure, exit 1", "passed": false
      }]
    }
  }
}
```

`recovery.json` incident after tick 3:

```json
{
  "incident_id": "RNS-6beafd077363", "state": "blocked_validation",
  "attempt": 0, "validation_blocks": 1, "canonical_denials": 0,
  "last_error": "quick validation tier failed",
  "resume_after": "2026-09-09T16:27:27Z",
  "last_attempt_at": "2026-09-09T16:28:49Z",
  "next_attempt_at": "2026-09-09T16:43:49Z",
  "run_id": "RUN-564ce8f4c490460d87312de5c7e870ec", "session_name": "gine"
}
```

- **`harness_resume: null`** — no `HarnessService` call, and the direct
  `hcom.resume()` fallback was never reached either. **No resume fired.**
- **`attempt: 0`** — the transient retry budget was not consumed (design note
  Q6 / PR #195 parity).
- `state: "blocked_validation"` — the distinct, re-processable parked state.
- `next_attempt_at = last_attempt_at + 900s` exactly — rescheduled on the flat
  `silent_stop_probe_delay_seconds` probe interval, not the escalating backoff
  ladder.
- `resume_validation.passed is false` (not absent) keyed on a real
  `returncode: 1` — `_quick_validation_failed` matched a concrete
  `{attempted: true, passed: false}`, nothing weaker.

### Consecutive blocks and the ceiling (ticks 4–5)

- **Tick 4** (16:44:24Z): a second consecutive `resume_blocked_validation`,
  `validation_blocks: 2`, `attempt` still `0`, state still `blocked_validation`,
  rescheduled +900s.
- **Tick 5** (17:00:06Z): `validation_blocks` reached
  `_MAX_CONSECUTIVE_VALIDATION_BLOCKS = 3` → `action: "fail"`, `reason:
  "validation_block_persistent"`, incident `state: "failed"`, `last_error:
  "validation_block_persistent"`. Still `attempt: 0` — the ceiling is its own
  consecutive-block counter, disjoint from the transient retry budget and from
  `canonical_denials` (PR #195 / #320 parity). Verbatim action dict:

```json
{
  "action": "fail", "reason": "validation_block_persistent",
  "harness_resume": null, "incident_id": "RNS-6beafd077363",
  "validation_blocks": 3,
  "resume_validation": {
    "attempted": true, "passed": false, "tier": "quick",
    "environment_spec_hash": "2948d8d9211f9b34522cf41faa1a522d73041ec8b778f833c05a6eebce363201",
    "result": { "tier": "quick", "passed": false, "skipped": [],
      "ran": [{ "command": "sh -c 'echo H4-EXERCISE: deliberate quick-tier failure, exit 1 >&2; exit 1'",
        "found": true, "returncode": 1,
        "output": "H4-EXERCISE: deliberate quick-tier failure, exit 1", "passed": false }] }
  }
}
```

  `recovery.json` incident after tick 5: `state: "failed"`, `attempt: 0`,
  `validation_blocks: 3`, `canonical_denials: 0`, `last_error:
  "validation_block_persistent"`, `last_attempt_at: "2026-09-09T17:00:06Z"`.

---

## 4. Control comparison — computed, not asserted

Lane B is the same incident shape (same task contract, same `spec_ref`, same
recorded evidence row, same killed-session stall) run through `recovery-tick`
**without** `--enforce-validation`. Its tick-3 action dict:

```json
{
  "action": "resume_failed", "attempt": 1,
  "error": "hcom command failed (2): hcom r --go laza --headless: ",
  "harness_resume": null, "incident_id": "RNS-9b2437533fe7",
  "resume_validation": {
    "attempted": true, "passed": false, "tier": "quick",
    "environment_spec_hash": "2948d8d9211f9b34522cf41faa1a522d73041ec8b778f833c05a6eebce363201",
    "result": { "... identical to lane A ..." }
  }
}
```

Set-diff of the two tick-3 action dicts (actually computed):

```
resume_validation  : IDENTICAL between lane A and lane B  (same genuine failing quick tier)
harness_resume     : null in both
only in lane A     : reason="quick_validation_failed", validation_blocks=1
only in lane B     : attempt=1, error="hcom r --go laza --headless ..."
lane A incident.attempt stayed 0   ;   lane B incident.attempt -> 1  (state: probing)
```

The `resume_validation` payload — the advisory observation — is **byte-identical**
in both lanes: the environment was equally broken either way. The only input
that differed is the `--enforce-validation` flag, and it is the only thing that
changed the outcome from "resume attempted" (`resume_failed`, `attempt` bumped,
`state: probing`) to "resume parked" (`resume_blocked_validation`, `attempt`
untouched, `state: blocked_validation`). Flag off ⇒ byte-identical to today,
including the advisory `resume_validation` recording (design note Q5 / MUST-NOT
5).

---

## 5. `attempted:false` lane — not blocked even under the flag (design Q6)

Lane C's task carried **no** `environment` block, so `maps flow start` recorded
no `run_environment_evidence` row. Under `recovery-tick --enforce-validation`,
tick 3:

```json
{
  "action": "resume_failed", "attempt": 1,
  "error": "hcom command failed (2): hcom r --go zelu --headless: ",
  "harness_resume": null, "incident_id": "RNS-3e71e2dd5aaa",
  "resume_validation": { "attempted": false, "reason": "no_spec_bound" }
}
```

`resume_validation.attempted is false` → `_quick_validation_failed` returns
`False` → the gate did **not** fire despite `--enforce-validation` being set.
The incident proceeded to a resume attempt exactly as lane B did. A missing /
unparseable / ambiguous / budget-skipped spec is never an environment-broken
signal (design note MUST-NOT 4, Q6.4). `passed` is **absent**, not `false`.

---

## 6. Honest caveats (#303 / #320 style)

1. **The failing tier command is synthetic.** `sh -c '… exit 1'` is a
   deliberately-authored always-fail command in a throwaway spec, not a real
   environment defect (a missing tool, a version skew). What is genuine is the
   mechanism: `run_validation_tier` ran a real subprocess, it exited non-zero,
   and `RunBoundValidator` returned a real `{attempted: true, passed: false}`
   that the gate consumed. This is the same shape #303 used (a deliberately
   worktree-mismatched run) — a real mechanism exercised by a constructed
   trigger.
2. **No `--enforce-canonical-run` in this exercise.** The validation gate is
   upstream of the canonical guard and needs no `HarnessService`; composing the
   two (`--enforce-validation --enforce-canonical-run` together) is covered by
   design note Q4's "compose cleanly" claim but was **not** exercised here.
3. **`normal` / `full` tiers and the per-spec
   `EnvironmentSpec.validation.enforcement` field remain deferred** — this
   exercise only touches `quick` + the operator-invocation opt-in, exactly the
   first-slice scope. The row's gap language for those is unchanged.
4. **Session revival on the control/attempted-false lanes.** `hcom r --go` on a
   killed session can bring it back (it did for `laza` and `zelu`); both were
   killed again immediately. This is a property of the direct-resume fallback,
   not of the gate, and does not affect lane A (which never resumed).
5. **`environment_evidence: null` on the lane-A action dict.** That key carries
   the separate `_advisory_environment_evidence` (E5) surface, which needs an
   `environment_reader`; this pass supplied a `resume_validator` but no
   `environment_reader`, so it is `null` — unrelated to `resume_validation`.

---

## 7. Roadmap impact — row H4 annotated, **Status NOT changed**

Per the scope report (hcom #94399 reply) and `leto`'s confirmation (#94431),
row H4 stays **IN PROGRESS**. Its stated gap has two remaining clauses:

> …no first production exposure of an enforced pass yet, and `normal`/`full`
> tiers plus the per-spec `EnvironmentSpec.validation.enforcement` field remain
> deferred.

This exercise closes **only the first clause**. The deferred `normal`/`full`
tiers and the per-spec enforcement field are untouched, so the row does not
flip. A dated annotation was appended to the H4 row (and only that row) citing
this note and the frozen case id.

The same first-clause language appears verbatim on the **E4** and **6.5** rows;
those were **not** edited (output boundary — row H4 only). A follow-up
trajectory check should reconcile them against this note.

---

## 8. Boundaries honoured

- No `runtime/` change (none needed; stop condition did not fire).
- No test file touched.
- Created only: this note, the frozen regression case
  (`work/regression-cases/CASE-559ff1df61eb6c829b55c641b3ae0a4450f8dca9bfcc218e76df84fd53332a22.json`), and a single dated annotation on
  the H4 row of `work/roadmaps/CAPABILITY_CHECKLIST.md`.
- `h4-exercise-spec.json` left untracked in the clone working tree, never
  staged, not in this PR (`git status` verified before every commit).
- No operator hcom session other than the three throwaway lanes was touched;
  all three (`gine`, `laza`, `zelu`) confirmed gone from `hcom list` after the
  run.
- No `work/reviews/pr-*-review-evidence.md` written by `meme` (two-phase
  review — the reviewer/coordinator commits that).

---

## Resume prompt

The H4 enforced-validation-gate first-exposure exercise is **done (SUCCESS)** —
do not re-run it. The evidence note is this file; the frozen case is
`work/regression-cases/CASE-559ff1df61eb6c829b55c641b3ae0a4450f8dca9bfcc218e76df84fd53332a22.json`; row H4 in
`work/roadmaps/CAPABILITY_CHECKLIST.md` carries a dated annotation citing both,
with **no Status change** (still IN PROGRESS: `normal`/`full` tiers + the
per-spec `EnvironmentSpec.validation.enforcement` field remain deferred). The
E4 and 6.5 rows share the "no first production exposure" clause and were
deliberately left unedited — a trajectory check should reconcile them. This PR
needs INDEPENDENT_REVIEW (owner `meme` is not eligible); check whether that
review has landed before treating the PR as final. The throwaway clone
`/tmp/exh4-473920` and lane dirs `/tmp/exh4-lane-{a,b,c}` / `/tmp/exh4-sess-{a,b,c}`
should be `rm`-ed on stand-down.
