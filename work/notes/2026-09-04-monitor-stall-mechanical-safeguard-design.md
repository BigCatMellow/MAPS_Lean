# Design note: mechanical safeguard for the dispatched-worker full-suite stall

- Status: DESIGN NOTE ONLY in the carrying PR — no `AGENTS.md` / `playbook/` /
  `templates/` behavior change here. Impl is a separate PR, script ships usable
  immediately (a test tool, inert until briefs point at it).
- Author: `miso` (coordinator, session 29), 2026-09-04.
- Source of truth: `work/coordination/FRICTION_LOG.md` entry
  **"2026-09-03 — dispatched worker stalls on its own full `unittest` suite"**
  (+ its 2026-09-04 traj-#22 follow-up flipping `countermeasure:` to
  "scoped-needed (rule 20)"); `work/notes/2026-09-04-roadmap-trajectory-check-22.md`
  §3.2 / §3.4 / §7; `work/notes/2026-08-18-stalled-dispatched-worker-repair.md`
  Prevention §1; memory `feedback_subagent_monitor_polling_stall`,
  `feedback_pipe_to_tail_masks_exit_code`, `feedback_mutation_script_detach_leaves_source_mutated`.
- Rule references: rule 19 (dispatch precision), rule 20 (repeat failure → a
  *mechanical* safeguard, not another instruction).
- Review: verification-only for the note; the impl PR gets a real independent review.

---

## 1. Problem

The `unittest discover -s tests` full suite has several modules at ~7–8 s/test
(`test_flow_release_check`, `test_context_builder`, the `test_exp_b_skill_routing`
batteries). A single module is 3+ min; the whole suite is far over any short
foreground timeout. A dispatched worker therefore:

- runs it foreground → hits the timeout → looks like a stall, OR
- **backgrounds it and sits on a `Monitor` / wait-loop** reading a buffered-empty
  output file → burns its entire context lane delivering nothing; the coordinator
  has to intervene.

The dispatch instruction *already* forbids this in every impl brief and in
`ROADMAP_TRAJECTORY_CHECK.md`. It **still recurred 2× in session 27** (`rovu`,
`buro`; coordinator `mimi` intervened both times). Per rule 20 the instruction is
spent — this needs a mechanical safeguard. It converges with the 2026-08-18
repair record's deferred "mechanical timeout/heartbeat for dispatched workers".

The real gate is CI (`test` / `runtime-stack-tests.yml`, 15-min budget) — that is
authoritative and unchanged. The problem is purely the *local* pre-push check a
worker feels it must run.

## 2. Goal / non-goals

**Goal:** a dispatched worker can get a trustworthy local full-suite result from a
**single foreground command that never looks hung and is self-bounding**, so there
is no reason to background it or put a `Monitor` on it.

**Non-goals:**
- Not a replacement for CI. Local run stays advisory; CI `test` is the gate.
- Not a change to how tests are written or to `unittest` discovery semantics.
- Not a dispatched-worker daemon / heartbeat service (rule 13 — machinery only on
  repeated evidence, and a simpler fix exists).

## 3. Design — two layers

### 3.1 Primary (repo-side, mechanical): `scripts/run_tests_sharded.py`

A stdlib-only runner that shards discovery by top-level test module and runs each
module as its **own subprocess**, streaming progress:

```
python scripts/run_tests_sharded.py [--timeout-per-module SEC] [-k PATTERN] [--jobs N]
```

Behavior:
- Discover test modules the same way `unittest discover -s tests` would (glob
  `tests/test_*.py`, honor an existing `load_tests` if present — or just shell out
  to `python -m unittest tests.<module>` per module).
- Run each module in a subprocess with a per-module timeout (default 300 s — every
  known module fits; a module that blows it is a real bug, reported not hidden).
- **Stream one line per module as it completes**, to stdout, unbuffered:
  `PASS  tests.test_foo                (12.3s)` / `FAIL  tests.test_bar  (…)` /
  `TIMEOUT tests.test_baz  (>300s)`. A heartbeat line every ~30 s for a module
  still running (`… tests.test_slow running 90s`). Continuous output ⇒ never
  looks hung ⇒ no reason to background it.
- Aggregate: print a summary (`N modules, M passed, K failed/timed-out`), list the
  failing modules, and **exit non-zero iff any module failed or timed out**
  (mirrors `feedback_pipe_to_tail_masks_exit_code` — exit code is trustworthy,
  no pipe-to-tail needed).
- `--jobs N` optional parallelism (default 1 — deterministic; parallel is opt-in
  because some modules touch shared `.maps/` fixtures).
- On its own failure to even start a module, that module is `ERROR`, not silently
  skipped.

Total wall time is roughly the current suite time, but the worker sees steady
progress and a bounded per-step cost, and can trust the exit code. That removes
the incentive that produces the stall.

### 3.2 Secondary (harness-side, local): a `Monitor`-on-a-test-run block

`.claude/settings.local.json` is **git-ignored** (local-machine config — same
class as the `maps-handoff-context` SessionStart hook). Add a `PreToolUse` hook
matching the `Monitor` tool (and `Bash` with `run_in_background: true`) that
**denies** the call when its target command matches
`unittest|pytest|run_tests_sharded|-m unittest`, with a message:
"Run the test suite as a blocking foreground `python scripts/run_tests_sharded.py`
— do not background it or Monitor it (FRICTION_LOG 2026-09-03)."

This cannot live in the repo, so:
- The impl PR adds a documented **template** for it at
  `scripts/hooks/block-monitor-on-tests.example.json` (or a short section in
  `work/coordination/README.md`) that an operator / session pastes into their
  local `.claude/settings.local.json`.
- The FRICTION_LOG follow-up records that the local hook is the enforcement layer
  and the repo can only carry the template (same caveat the resume-prompt entry
  already uses).

### 3.3 Dispatch-brief wording (follow-up, operator-adoptable)

Once 3.1 lands, impl/review briefs change from
"run the named modules foreground; do NOT background the full suite"
to
"local full-suite check = `python scripts/run_tests_sharded.py` foreground (it
streams per-module progress and is self-bounding); never background it, never
`Monitor` it; CI `test` is the gate."
`ROADMAP_TRAJECTORY_CHECK.md` and `templates/` get the same swap. **This wording
change is a small follow-up PR** (touches `playbook/` + `templates/`), not part of
the impl PR, so the impl PR stays a clean tool-add.

## 4. Why this is the mechanical fix rule 20 wants

- The worker's stall is driven by an *incentive* (need a local result, suite too
  big to watch). 3.1 removes the incentive mechanically — the command is now
  watchable and bounded.
- 3.2 is a hard backstop for the specific failing action, at the harness level,
  where an instruction cannot be "read as already satisfied".
- Neither is "another line in a brief" — 3.1 is a tool, 3.2 is a `deny` hook.

## 4b. Known limitation / follow-up (added during impl, 2026-09-04)

Per-module subprocess isolation (§3.1) exposes a **latent circular import** that
full alphabetical `unittest discover -s tests` masks:
`runtime/environment/__init__.py` <-> `runtime/state/environment.py`. Under
full discovery an earlier module imports `runtime.state` completely before any
`test_environment_*` module loads, so the cycle resolves; in isolation the four
`test_environment_*` modules (`fingerprint`, `fingerprint_safety`, `spec`,
`validation`) would ERROR.

**Workaround shipped here:** the runner imports `WARMUP_IMPORTS = ("runtime.state",)`
inside every shard subprocess before loading the target module, reproducing that
ordering. Unconditional (deterministic); `ImportError` is swallowed so it is
harmless in a fixture tree without the package. Covered by
`tests/test_run_tests_sharded.py` and a FRICTION_LOG entry
(2026-09-04, class: drift).

**Real fix is a separate PR:** break the `runtime.environment` <->
`runtime.state.environment` cycle (deferred import or a shared lower-level
module). Until then `WARMUP_IMPORTS` is the seam; if another module pair develops
the same coupling, add it there rather than growing brief text.

## 5. Implementation scope (for the impl dispatch)

- **MAY create:** `scripts/run_tests_sharded.py`, `tests/test_run_tests_sharded.py`,
  `scripts/hooks/block-monitor-on-tests.example.json` (+ a short README pointer if
  the reviewer prefers), `work/notes/2026-09-04-monitor-stall-mechanical-safeguard-design.md`
  (verbatim copy of this note).
- **MUST NOT touch:** `AGENTS.md`, `playbook/`, `templates/`, any CI workflow, any
  existing script or source file, `check_review_evidence.py`.
- **Acceptance:**
  - `python scripts/run_tests_sharded.py -k test_documentation_sprawl` runs just
    that module, streams a `PASS/FAIL` line, exits 0 on pass.
  - Injecting a deliberately failing module (in a tmp fixture dir via `-s`, or a
    unit test that drives the runner against a fixture) → runner prints `FAIL
    <module>` and exits non-zero, and still runs the other modules.
  - A module exceeding `--timeout-per-module` → `TIMEOUT` line, non-zero exit,
    other modules still run.
  - Output is line-buffered/flushed (no all-at-end dump).
  - `tests/test_run_tests_sharded.py` covers pass / fail / timeout / exit-code,
    driving the runner against a small fixture tree — NO dependence on the real
    suite's timing, NO network.
- **Verify:** `python scripts/run_tests_sharded.py` foreground on the real repo
  (dogfood — it should not need backgrounding). Then confirm `python -m unittest
  discover -s tests` is still green as the authoritative comparison — run THAT as
  a blocking foreground call too if time allows, else state you relied on CI.
  Do NOT background either. Do NOT `Monitor` either.

## 6. Resume prompt

You are implementing the dispatched-worker full-suite stall safeguard from
`work/notes/2026-09-04-monitor-stall-mechanical-safeguard-design.md`. Read that
note in full (§3, §5). Fresh-clone `BigCatMellow/MAPS_Lean` to a unique
`/tmp/<tag>-$$/` path — never `~/Projects/MAPS_Lean` or `.claude/worktrees/`.
Branch off current `origin/main`. Add `scripts/run_tests_sharded.py` +
`tests/test_run_tests_sharded.py` + `scripts/hooks/block-monitor-on-tests.example.json`
+ the design note file (verbatim from the scratchpad copy the coordinator gives
you). Stdlib only. Do NOT touch `AGENTS.md`, `playbook/`, `templates/`, CI, or any
existing file. Dogfood the runner foreground on the real repo. Run `python -m
unittest discover -s tests` as a BLOCKING FOREGROUND call for the comparison — do
NOT background it, do NOT `Monitor` it (this is the exact failure the PR fixes).
Open a PR, post head SHA + CI status to hcom, request independent review
(two-phase). Stop and report if unittest discovery semantics for this repo are
non-obvious (e.g. a custom `load_tests`) — do not guess.
