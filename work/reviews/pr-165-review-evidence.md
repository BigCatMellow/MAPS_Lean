reviewer: agent-aaa1b01bbb3211fbc (independent reviewer, did not author this PR)
head_sha: 148357bbf6fb68c817141e3aad986871bde41e3f
independent: true
summary: APPROVED — design-note compliance, the bounded-trigger claims, and all three rounds of fixes verify clean: F1 (claim latency, now bounded at 3.0s per hcom call) and F4 (guard evadable by `from threading import Thread`) confirmed RESOLVED empirically, and B1 (the `heartbeat_at` timestamp flake) confirmed RESOLVED by a 100-execution repeat-run loop with zero failures plus a perturbation check proving the widened normalization did not make the tests vacuous; five non-blocking findings remain recorded.

# Review: PR #165 RnS production trigger loop call site

- Design note (spec): `work/notes/2026-08-24-rns-production-trigger-loop-design.md`
- Reviewer: `agent-aaa1b01bbb3211fbc`
- Reviewed code head: `148357bbf6fb68c817141e3aad986871bde41e3f`
- True merge-base: `f02ed62f16799a977532f4a4930e5841cf8207af`
- Verdict: `APPROVED` — no blocking item outstanding; five non-blocking findings
  recorded (F2, F3, F5, F8, F9)

## Review history

Reviewed in four passes against four shas, all with identical intent:

1. `c286da7` — full review. Verdict `APPROVED` with six non-blocking findings F1-F6.
2. `2d4fd0a` — same content, rebased onto `origin/main` `f02ed62`. Confirmed unchanged:
   `git diff c286da7 2d4fd0a --stat -- runtime/ tests/` is **empty**. All boundary
   greps re-run against the new merge-base and still hold.
3. `9f41a42` — the author's fix commit for F1 and F4. Targeted re-verification of
   those two fixes (both `RESOLVED`, sections 8 and 9), plus repeat runs of the new
   test module, which surfaced the blocking finding B1. Verdict at that sha was
   `CHANGES_REQUESTED`.
4. `148357b` — the author's test-only fix for B1. Targeted re-verification of that
   fix alone (section 10). Verdict `APPROVED`.

Everything in sections 1-7 was verified at `c286da7`/`2d4fd0a` and re-confirmed to
still hold at `9f41a42` and `148357b`.

## 1. Change set

`git diff f02ed62..148357b --stat` — the three expected files and nothing else
(`runtime/cli.py` modified, `runtime/recovery/production.py` new,
`tests/test_recovery_production_trigger.py` new), plus this evidence file. The F1/F4
fix commit `git diff 2d4fd0a..9f41a42 --stat` touches those same three files only, and
the B1 fix commit `git diff --stat 8991fcc..148357b` touches
`tests/test_recovery_production_trigger.py` alone (16 insertions, 3 deletions) —
`git diff --name-only 8991fcc..148357b -- runtime/ scripts/` is **empty**, so no
production file was changed to fix the flake. `PASS`.

## 2. Non-tautology check — `PASS`

The blunt form first: with `runtime/cli.py` reverted to the parent commit **and**
`runtime/recovery/production.py` deleted (new test file kept), the module fails to
import at all —

```
ImportError: Failed to import test module: test_recovery_production_trigger
ModuleNotFoundError: No module named 'runtime.recovery.production'
```

That is uninformative on its own, so a finer-grained variant was run: parent-commit
`runtime/cli.py` restored in place while **keeping** the PR's `production.py` and the
new test file, isolating exactly which tests depend on the new CLI wiring.
`python3 -m unittest tests.test_recovery_production_trigger -v` →
**`Ran 18 tests in 98.777s / FAILED (failures=3, errors=6)`**.

Genuinely-failing tests against old code (9 of 18):

- `test_subcommand_runs_one_bounded_pass_and_exits` — `ERROR`
- `test_subcommand_passes_hcom_overrides_and_bindings_through` — `ERROR`
- `test_subcommand_defaults_match_hcom_adapter_defaults` — `ERROR`
- `test_subcommand_rejects_malformed_binding` — `ERROR`
- `test_subcommand_reports_failure_without_raising` — `ERROR`
  - all five with `argparse.ArgumentError: argument command: invalid choice: 'recovery-tick' (choose from 'init', 'create', ... 'flow')` → `SystemExit: 2`
- `test_claim_success_output_unchanged_when_recovery_has_nothing_to_do` — `ERROR`
  (`mock.patch("runtime.cli.run_recovery_tick_isolated")` cannot resolve the attribute on old `cli.py`)
- `test_claim_triggers_one_recovery_pass_after_success` — `FAIL`:
  `Lists differ: [] != [True, True]` (old `claim` makes zero hcom session listings)
- `test_claim_still_succeeds_when_recovery_tick_fails` — `FAIL`:
  `AssertionError: 'recovery-tick failed (claim unaffected)' not found in ''`
- `test_claim_still_succeeds_when_recovery_tick_raises_unexpectedly` — `FAIL`:
  `AssertionError: 'unexpected recovery explosion' not found in ''`

Tests that legitimately still pass against old `cli.py` — they exercise the new
`production.py` helper directly, or are pure guards. That is correct for a guard test,
and is stated here rather than glossed: `test_runs_exactly_one_observe_then_one_tick_and_returns`,
`test_harness_service_and_environment_reader_are_not_wired`,
`test_real_supervisor_pass_completes_against_an_empty_hcom`,
`test_isolated_variant_contains_failures`, `test_unisolated_variant_still_raises`,
`test_claim_does_not_trigger_recovery_when_the_claim_itself_fails` (asserts an
absence — vacuously true on old code, legitimate as a regression guard),
`test_claim_success_payload_matches_direct_store_call` (a never-should-change
invariant, correctly passing before and after — but see B1),
`test_no_daemon_scheduler_or_hook_machinery_in_trigger_source` and
`test_supervisor_public_signatures_untouched` (guards/pins).

Working tree restored afterward: `git checkout HEAD -- runtime/` then
`git status --porcelain` → **empty**, verified before proceeding.

## 3. Boundary compliance (design note "Must not do") — `PASS`

Verified by diff/grep, not prose, and re-run against `148357b`:

- `git diff f02ed62..148357b -- runtime/recovery/supervisor.py runtime/harness/ | wc -l`
  → **`0`**. `tick()`/`observe_silent_stops()` internals and signatures are untouched.
- `grep -rn "HarnessService(\|HcomHarnessAdapter(" runtime/ scripts/ | wc -l` → **`0`**.
  The PR's answer 6 (re-confirm the gap by grep) is true at this commit; no new harness
  production wiring was built.
- `git diff f02ed62..HEAD | grep -inE "thread|multiprocessing|asyncio|sched|cron|daemon|Timer|atexit|fork|Popen|HookEvent|HookRegistry|validation_tier|EnvironmentSpec|make_validation_hook|time\.sleep|DONE"`
  returns hits on **only** the `production.py` docstring saying those mechanisms are
  deliberately absent, and the guard test's own forbidden-token literals. No scheduler,
  cron entry, thread, process, or daemon is introduced.
- No validation-tier execution: zero hits for `validation_tier` / `EnvironmentSpec` /
  `make_validation_hook` in the diff.
- `git diff f02ed62..148357b --name-only -- work/` names **only this evidence file**;
  `git diff 2d4fd0a..9f41a42 --name-only -- work/` and
  `git diff 8991fcc..148357b --name-only -- work/` are both **empty**. No roadmap,
  checklist, or status file is touched anywhere in this PR; no row is marked `DONE`.

## 4. `claim` behavior provably unchanged on the success path — `PASS`

Each sub-question checked directly against source and against a real CLI run, rather
than trusting `test_claim_success_output_unchanged_when_recovery_has_nothing_to_do`.

(a) **Is `claim`'s stdout/exit code derived solely from `store.claim_task(...)`?** Yes.
The branch is `result = store.claim_task(...)` … `return _emit(result)`. `_emit`
computes `payload = asdict(value)` and `ok = value.ok` from that `MutationResult`
alone; the recovery dict is never passed to `_emit` on this path.

(b) **Can a recovery failure leak into stdout or the exit code?** No. Verified
empirically with a fake `hcom` on `PATH` that sleeps 120s (see section 8): exit `0`,
exactly one unmodified claim JSON document on stdout (`ok=True`, `code=CLAIMED`,
`status=ACTIVE`), the failure on stderr only. (Narrow caveat: `except Exception` does
not cover `BaseException`, so a `KeyboardInterrupt`/`SystemExit` raised inside the pass
would escape. Catching `BaseException` would be worse; noted, not a defect.)

(c) **Does the recovery pass have any side effect on task truth?** No task truth.
`grep -nE "claim_task|submit_task|record_review|promote_ready|update_contract|INSERT INTO|UPDATE |sqlite|TaskStore" runtime/recovery/supervisor.py`
→ **0 hits**; `observe_silent_stops()` reads via `list_tasks(statuses=("ACTIVE",))`
only. It does have a non-task side effect — see F2.

(d) **Is the recovery pass skipped when the claim itself fails?** Yes — guarded by
`if result.ok:`, and `test_claim_does_not_trigger_recovery_when_the_claim_itself_fails`
asserts `fake.list_calls == []`. A failed `claim` is byte-identical to before.

On vacuity of the cited test: its control arm patches
`runtime.cli.run_recovery_tick_isolated` with a `MagicMock`, so `recovery['ok']` returns
a truthy MagicMock and no stderr is emitted — the control genuinely models "trigger
present, did nothing", and `never.assert_called_once()` proves the trigger was reached.
It is a real comparison. Its normalization is nonetheless incomplete — that is B1.

## 5. Source-level grep guard: real, not decoration — `PASS`

At `2d4fd0a` the `tokenize`-based stripping in `code_text()` was inspected in its actual
output (surfaced in an assertion message): every `STRING` token — including the module
docstring naming `threading`, `daemon`, `cron` — is genuinely removed, and identifiers
are lower-cased and space-joined so `time.sleep` becomes `time . sleep`, matched as
`"time . sleep"`. The stripping is correct.

**Tamper test at `2d4fd0a`** — inserting `import threading` into
`runtime/recovery/production.py` made the guard `FAIL` as it should
(`AssertionError: 'import threading' unexpectedly found in ...`). Reverted; tree clean.
That established the guard is real. Its evadability via `from threading import Thread`
was F4, now fixed and re-verified in section 9.

## 6. The six behavior-question answers — sound and honest

1. **Can a `recovery-tick` failure fail `claim`?** "No" — **verified true** (4b).
2. **Does `observe_silent_stops()` run alongside `tick()`?** "Yes, both, in that order"
   — **verified true**: a real CLI `claim` against a logging fake `hcom` produced
   exactly two `list --json --stopped --all` invocations, one per pass.
3. **What bindings does `observe_silent_stops()` get in production?** Nothing inferred;
   standalone accepts `--binding`, the `claim` path passes none. **Verified true and
   honestly stated.** With an empty mapping the
   `for worker_id, session_name in sorted(bindings.items())` loop body never runs, so
   no incident can be opened. The PR says so plainly and marks no roadmap row done.
   This is **not** a misleading impression that silent-stop detection now works in
   production — it is correctly framed as an unclosed gap. See F3 for one further
   limitation the PR does not mention.
4. **Output verbosity.** `claim` silent on stdout, one stderr line on failure;
   standalone emits JSON via `_emit` with exit `0`/`2`. **Verified true** empirically.
5. **`--db` / `--hcom-dir` / `--hcom-executable` plumbing.** **Verified true** —
   `HcomAdapter.__init__` defaults are `hcom_dir=".hcom"`, `executable="hcom"`,
   `timeout_seconds=30.0`, matching the module constants.
   `DEFAULT_RECOVERY_STATE_PATH` likewise matches `RecoveryStore.__init__`.
6. **Re-confirm the `harness_service` gap by grep.** Zero hits — **verified true** (3).

## 7. Independent bug hunt

- **`--binding` parser** — `value.partition('=')` with an explicit `ValueError` on a
  missing separator or an empty/whitespace side; a session name containing `=` is
  preserved. Malformed input becomes
  `MutationResult(False, 'INVALID_RECOVERY_BINDING', ...)` and exit `2`, matching every
  other subcommand's error shape. `PASS`.
- **argparse conventions** — hyphenated subcommand name matches `run-record`,
  `freeze-case`, `review-claim`. `action='append', default=[]` with a `KEY=VALUE` help
  string mirrors the existing `flow start --runtime-limit`. Bare `--hcom-dir` /
  `--hcom-executable` without `help=` is consistent with e.g.
  `flow_start.add_argument('--repo-root', default='.')`. `default=[]` is not a shared
  mutable because `build_parser()` builds a fresh list per call. `PASS`.
- **New module-level import in `runtime/cli.py`** — no circular import. It does widen
  the blast radius: `runtime/cli.py` now imports `runtime.communication` and
  `runtime.recovery.*` at module scope, so an import-time error in either breaks *every*
  subcommand, not just the two new paths. All first-party and already in-tree; noted,
  not blocking.

## 8. F1 (claim latency) — `RESOLVED`, verified

The author took the real fix, not documentation: `hcom_timeout_seconds` was threaded
through both helpers, with `DEFAULT_HCOM_TIMEOUT_SECONDS = 30.0` for the standalone
subcommand and `CLAIM_PIGGYBACK_HCOM_TIMEOUT_SECONDS = 3.0` for the `claim` path.

All four requested points verified against a fake `hcom` on `PATH` that hangs for 120s,
driving the **real** CLI (no mocks):

(a) **The timeout genuinely reaches the real `HcomAdapter` constructor**, not just a
variable — `production.py` now passes `timeout_seconds=hcom_timeout_seconds` into
`HcomAdapter(...)`, and the wall-clock proves it end to end:

```
=== claim with a HANGING hcom ===
EXIT=0
STDOUT ok/code: True CLAIMED ACTIVE
STDOUT doc count: 1
STDERR: recovery-tick failed (claim unaffected): HcomError: hcom command timed out: hcom list --json --stopped --all
ELAPSED=3.27 s
```

(b) **A timing-out hcom is still contained and still cannot fail the claim** — exit `0`,
one unmodified JSON document on stdout, task genuinely `ACTIVE`, failure on stderr only.
The 3.27s (not ~6s) also confirms the pass aborts after the *first* `hcom list`, so the
failure path costs one timeout, not two.

(c) **Is 3.0s a sane bound, or does it make the pass useless?** Measured real `hcom` on
this machine: `hcom list --json --stopped --all` steady-state is **0.01-0.04s** across
repeated runs — roughly 75x headroom. One cold first invocation took **2.28s**, driven
by hcom's own version-check, which is uncomfortably close to the 3.0s budget: on a slow
network a cold-start pass could time out spuriously. That fails safe (contained, claim
unaffected, one stderr line) and the alternative is the 30s default that F1 objected to,
so 3.0s is a defensible bound. Recorded as a caveat, not a blocker.

(d) **The standalone path really does keep the longer default** — same hanging hcom:
`recovery-tick` → `ELAPSED=30.13 s`, exit `2`; `recovery-tick --hcom-timeout-seconds 1`
→ `ELAPSED=1.12 s`. Both behave exactly as documented.

**The tradeoff I am approving with eyes open**, stated explicitly rather than left as a
generic note: `claim` was a pure-local SQLite operation and is now, on every success, an
operation that shells out to `hcom list --json --stopped --all` **twice** and rewrites
`.maps/state/recovery.json`. In the normal case that costs tens of milliseconds. In the
worst case — an unresponsive hcom — it adds up to about **6 seconds** (2 x 3.0s) of wall
time to a successful claim, and prints one stderr line. Task truth, stdout and exit code
are provably unaffected in every case I could construct. The design note deliberately
chose `claim` as the trigger, and I accept that cost as bounded and worth the trigger it
buys. I would not have accepted the original unbounded 2 x 30s.

Incidentally also fixed by this commit: **F6** — `test_subcommand_defaults_match_hcom_adapter_defaults`
now reads `inspect.signature(HcomAdapter).parameters` and asserts the module constants
equal the adapter's real defaults, instead of only hardcoding them. `F6` is `RESOLVED`.

## 9. F4 (guard evadable) — `RESOLVED`, verified

The guard now matches import *statements* by regex
(`(?:^|\s)(?:import|from)\s+(?:[\w.]+\s*\.\s*)?{module}\b`) over a `FORBIDDEN_MODULES`
tuple, keeping the non-import checks as `FORBIDDEN_SUBSTRINGS`. Coverage widened
(`concurrent`, `schedule` added); nothing from the old list was dropped.

**Tamper test against the real check** — inserting `from threading import Thread` into
`runtime/recovery/production.py`, the exact evasion F4 reported:

```
FAIL: test_no_daemon_scheduler_or_hook_machinery_in_trigger_source
AssertionError: <re.Match object; span=(48, 63), match=' from threading'> is not None
 : runtime/recovery/production.py must not import 'threading' (matched ' from threading')
```

Previously this passed silently. Reverted; `git status --porcelain` clean.

**Is the tightened pattern obviously evadable?** Probed the predicate directly. Every
import form tried is caught: `import threading`, `from threading import Thread`,
`import threading as t`, `from . import threading`, `import xyz.threading`,
`from concurrent.futures import ThreadPoolExecutor`,
`from apscheduler.schedulers.background import BackgroundScheduler`. The realistic
remaining gap is the **process-spawn family that needs no forbidden import**:
`os.fork()`, `os.system('nohup mapd &')`, `os.popen(...)`, `os.posix_spawn(...)` all
`MISS`, as do the contrived dynamic forms `importlib.import_module('threading')` and
`__import__('threading')`. Suggested narrowing: add `os . fork`, `os . system`,
`os . popen`, `os . posix_spawn` to `FORBIDDEN_SUBSTRINGS`. Non-blocking (F8).

**Correction to the fix's stated design:** the PR describes "a shared `guard_trips()`
predicate used by both the real check and two new meta-tests". That is **not** what the
code does — `test_the_guard_actually_trips` and `test_the_guard_does_not_trip_on_innocuous_source`
call `guard_trips()`, but the real check
`test_no_daemon_scheduler_or_hook_machinery_in_trigger_source` re-inlines its own copy
of the same regex and substring loop. The two copies are byte-identical today, so the
guard is correct now (independently confirmed by the tamper test above, which exercised
the real check, not the predicate), but the meta-tests could keep passing if the real
check drifted. Recommend the real check call `guard_trips(text)`. Non-blocking (F9).

## 10. B1 (timestamp flake) — `RESOLVED`, verified

### The finding, as raised at `9f41a42`

- **B1 — `heartbeat_at` was missing from `VOLATILE_TASK_KEYS`, making two of this PR's
  headline tests flaky.** `VOLATILE_TASK_KEYS` was
  `("task_id", "created_at", "updated_at", "claimed_at", "lease_expires_at")`, but a
  claimed task's payload also carries `heartbeat_at`, a wall-clock timestamp truncated
  to whole seconds by `now_z()`. `test_claim_success_payload_matches_direct_store_call`
  compares a control `store.claim_task(...)` against a CLI `claim` performed moments
  later; whenever the two straddle a one-second boundary the payloads differ and the
  test fails. `test_claim_success_output_unchanged_when_recovery_has_nothing_to_do`
  shares the same normalization and the same exposure. The `claim`-path recovery pass
  this PR adds widens the window between the two arms, so the PR both introduces the
  test and aggravates its timing sensitivity.
  Reproduced repeatedly: `python3 -m unittest tests.test_recovery_production_trigger`
  gave `Ran 24 tests / FAILED (failures=1)` on one run and `Ran 24 tests / OK` on the
  next; isolating the test showed 2 failures in 8 runs, then 2 in 8 again. A driver
  replicating the test body pinned the cause exactly on attempt 2 of 40:

  ```
  differing task keys (cli_value, direct_value):
      heartbeat_at: '2026-08-25T05:32:46Z' != '2026-08-25T05:32:45Z'
  VOLATILE_TASK_KEYS = ('task_id', 'created_at', 'updated_at', 'claimed_at', 'lease_expires_at')
  ```

  This is test-only — no production behavior is wrong, and every claim-contract
  assertion in section 4 holds. But it would intermittently red the suite for everyone
  afterward, and it is invisible on CI precisely because CI runs the whole suite in ~22s.
  A green CI run is not evidence against it. The fix is one word in `VOLATILE_TASK_KEYS`;
  per this review's mandate I did not apply it.

### The fix at `148357b`, and what I verified

Test-only, one file. `heartbeat_at` was added to the enumerated tuple, and
`normalize()` was widened to blank any key ending in `_at` so a timestamp column added
later cannot silently reintroduce the same flake. The enumerated tuple is kept with a
comment naming `now_z()`'s whole-second truncation as the root cause.

**Repeat-run check.** The two affected tests, loaded unmodified from the repo module
(the real `ClaimPiggybackTests` methods, not a reimplementation) and run in-process:

```
RESULT: 50 iterations x 2 tests = 100 test executions, 0 failing iterations
```

That is **100 consecutive executions of the two affected tests with zero failures**,
comfortably past the flake's pre-fix rate. For calibration, the same two tests before
the fix produced 2 failures in 8 runs, twice over, and a driver replicating the test
body hit the mismatch on attempt 2 of 40.
Independent single run of the whole module at `148357b`:
`Ran 24 tests in 118.715s / OK`; `python3 -m compileall -q runtime tests` clean.

**Non-vacuity check — the one that mattered more.** A flake "fixed" by blanking
everything would be worse than the flake, so the widened `normalize()` was measured
directly on a real claimed-task payload, using the repo's own
`ClaimPiggybackTests.normalize`:

- It blanks exactly **5** keys — `created_at`, `heartbeat_at`, `lease_expires_at`,
  `task_id`, `updated_at` — and preserves **27** task fields plus all three top-level
  fields (`ok`, `code`, `message`).
- The `endswith("_at")` widening blanks **nothing** beyond the enumerated tuple on the
  current schema (the set difference is empty). It is pure future-proofing at zero
  present cost, not a broadening of what the test tolerates today.
- Normalization is shallow, so nested values are still fully compared — confirmed by
  the `task.policy.paid_execution` perturbation below being caught even though
  `policy` itself contains an `approved_at` key.

Perturbing one field at a time and re-running the tests' own comparison
(`normalize(cli_payload) == normalize(direct)`), **13 of 13 meaningful perturbations
were still DETECTED**: `status`, `claimed_by`, `attempt`, `risk`, `owner`, `title`,
`review_required`, `output_paths`, `policy.paid_execution`, `agi_status`, and the
top-level `ok`, `code` and `message`. The only two tolerated were the deliberate
controls — `heartbeat_at` and `task_id`, which are supposed to be tolerated. The tests
still compare real, meaningful task content and would still catch an actual change to
`claim`'s success-path payload. **Not vacuous.**

## Non-blocking findings carried forward

- **F2 — every successful `claim` now creates/rewrites `.maps/state/recovery.json`.**
  `observe_silent_stops()` calls `self.store.save(state)` unconditionally, and `tick()`
  again at its end, so a claim in a fresh tree materializes
  `{"ambiguous_workers": {}, "incidents": {}, "last_live": {}, "terminal_sessions": {}}`
  — confirmed by `find` after a real CLI claim. Recovery state, not task truth, so it
  violates nothing, but the PR's answer 1 speaks only of stdout/schema/exit code and
  does not mention the new write.
- **F3 — silent-stop detection needs at least two invocations with the same binding,
  which the PR does not state.** `observe_silent_stops()` opens an incident only when
  `previous and not current`, where `previous` comes from `state["last_live"]`. The
  `claim` path supplies no bindings and so never populates `last_live` at all, and even
  `recovery-tick --binding` cannot detect a stop on its first run. Inherent to the
  pre-existing `observe_silent_stops()` design, not introduced here; recorded so the
  follow-up that supplies real bindings does not assume one pass suffices.
- **F5 — "string literals stripped" is not exactly true on Python 3.12+.** f-strings
  tokenize as `FSTRING_START`/`FSTRING_MIDDLE`/`FSTRING_END`, not `STRING`, so f-string
  text survives `code_text()` — visible in the tamper output as
  `f" { type ( exc ) . __name__ } : { exc } "`. This makes the guard *stricter* (a
  possible false positive), never weaker, so it is a documentation nit rather than a hole.
- **F8 — the hardened guard still misses process spawns that need no forbidden import**
  (`os.fork`, `os.system`, `os.popen`, `os.posix_spawn`). See section 9.
- **F9 — the real guard check duplicates the predicate instead of calling `guard_trips()`**,
  contrary to the PR's description. See section 9.

`F1`, `F4` and `F6` are `RESOLVED` in `9f41a42` and verified above.

## Test results

- **Full suite (CI, on the exact reviewed sha `148357b`)** — GitHub Actions
  `Runtime stack tests`, run id **32813805003**, conclusion `success`, running the
  command from `.github/workflows/runtime-stack-tests.yml`
  (`PYTHONWARNINGS: error::ResourceWarning`, `python -m unittest discover -s tests -v`).
  Final lines observed in that run's log: `Ran 806 tests in 27.504s` / `OK (skipped=5)`.
  (Earlier green runs: **32812139993** on `9f41a42`, `Ran 788 tests in 22.379s`;
  **32811283328** on `2d4fd0a`, `Ran 782 tests in 21.711s`; **32798079630** on
  `c286da7`.) A green CI run alone would **not** have cleared B1 — the repeat-run loop
  in section 10 is what clears it.
- **New module, locally, at `148357b`** — `Ran 24 tests in 118.715s / OK`, plus the
  repeat-run loop in section 10. At `9f41a42` the same module ran twice as
  `Ran 24 tests in 102.594s / FAILED (failures=1)` then `Ran 24 tests in 98.385s / OK`
  — that difference was B1.
- **`python3 -m compileall -q runtime tests`** — clean at `148357b`.
- **Targeted, against parent-commit `cli.py`** —
  `Ran 18 tests in 98.777s / FAILED (failures=3, errors=6)` (non-tautology, section 2).
- **Full suite locally** — started at `2d4fd0a` and abandoned when `9f41a42` superseded
  it; no local full-suite result is claimed. CI's run on the exact reviewed sha is cited
  instead, as above.
- **Fatal lint** — `ruff` is **not installed** here (`which ruff` empty,
  `python3 -m ruff --version` → `No module named ruff`), so
  `ruff check runtime tests --select E9,F63,F7,F82` could not be run and is explicitly
  **not** claimed. The repo's own CI lint job covers it on this branch.

## Applicable review lenses

- `[x]` Functional / acceptance — every design-note deliverable and all six behavior
  answers traced to code and to observed CLI behavior, not to prose; both fixes in
  `9f41a42` re-verified end to end against a real hanging subprocess; the `148357b`
  test fix re-verified by repeat runs *and* by a perturbation check proving the tests
  did not go vacuous.
- `[x]` Destructive / data-loss — zero task-truth mutation surface in the triggered path
  (grep, 0 hits); the only new write is `.maps/state/recovery.json` (F2).
- `[x]` Authority / permission boundary — `tick()` can call
  `hcom.resume(session_name, headless=True, go=True)`, so `claim` now carries authority
  to resume a *different* worker's session. That is exactly what the design note chose
  and justified, and `runtime/recovery/supervisor.py` is byte-identical to the
  merge-base, so no resume authority was widened here. The durable record of any such
  action is the incident bookkeeping in `.maps/state/recovery.json`; the returned action
  list is discarded on the `claim` path, which is what the design note's "silent on
  stdout" requirement mandates.
- `[x]` Scope discipline — three files across all three author commits, no roadmap or
  checklist edit, no `DONE` claim, no harness or validation-tier scope creep. The B1 fix
  is test-only and touches no production file.

## Reviewer limits

- `ruff` unavailable locally; lint result not claimed.
- Real `hcom` behavior was exercised through controlled fakes on `PATH` and through
  timing measurements of the real binary, never against a live multi-session hcom
  deployment.
- No local full-suite run is claimed at any sha; CI's run on the exact reviewed sha
  `148357b` is cited instead.
- The B1 repeat-run loop is a finite sample. It cannot prove the flake is impossible,
  only that the observed failure rate went from roughly 25% to zero across the sample
  in section 10, on a machine where the pre-fix rate reproduced readily. Combined with
  the root cause being understood and directly addressed, that is sufficient evidence.
