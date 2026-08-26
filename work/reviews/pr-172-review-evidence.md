reviewer: aac51c575c7af06ac (independent reviewer, did not author this PR)
head_sha: 4a35ad2caaa369c6370ab881e727b99021989223
independent: true
summary: APPROVED — no blocking code defect. Every claim was re-derived from source at the reviewed head rather than taken from prose: the `supervisor.py` change is purely additive (one keyword-only `resume_validator=None`, one call at line 407 after the retry-budget `continue` at 384-397 and before `resolved = False` at 421, one `resume_validation` key on all five action dicts), the observation is genuinely advisory (every occurrence of `resume_validation` in `runtime/` is a write or a comment — no branch reads it), the only spec source is `run_environment_evidence` rows bound to the incident's own `run_id` reparsed with `parse_environment_spec` (`load_environment_spec`/`rev-parse`/`Path.cwd`/`os.getcwd` appear nowhere in `runtime/recovery/`), `--repo-root` defaults to `None` not `'.'`, the #160 source guard is byte-unmodified and passing, no roadmap/checklist row is touched (H4/E4/6.5 all still `IN PROGRESS`), and Q2 holds by construction — the `claim` branch at `cli.py:375-378` passes no `validation_repo_root`, so no validator is constructed and `CLAIM_PIGGYBACK_HCOM_TIMEOUT_SECONDS` is not reopened. Seven mutations were applied to the implementation and every one turned the corresponding test RED (gating the resume; ambient file-loaded spec fallback; `--repo-root` default `'.'`; deleting the per-tick count cap; deleting the spec-hash check; reintroducing the forbidden literal in `supervisor.py`; hoisting the validation call above the suppress/resolve/fail branches) — the load-bearing tests are non-tautological, and all mutations were reverted before this file was written. Eight non-blocking findings (F1-F8); F1 is administrative but must be fixed before merge — the GitHub PR description for #172 is verbatim the description of a *different* PR (SEC4 skill-lifecycle durable storage) and describes none of the files in this diff. F2 records that the N4 authority argument, while present and largely sound, overreaches in two places: `HcomAdapter` runs `shell=False` with a fixed argv, so a party with write access to `maps.db` could not previously cause the recovery pass to execute an arbitrary shell command, and `EnvironmentSpec.setup_commands` is executed nowhere in the codebase — this PR creates the *first* production execution of spec-declared shell commands rather than widening an already-exercised boundary. Both are gated behind an explicit `--repo-root` and a table with zero production writers, so the risk is not live today, but the argument should be corrected before a production writer of `run_environment_evidence` lands.

# Review: PR #172 — Add advisory resume-path validation-tier hook-in (RnS)

- Branch: `rns-validation-tier-impl`
- Reviewed head: `4a35ad2caaa369c6370ab881e727b99021989223` ("Add advisory resume-path validation-tier hook-in (RnS)")
- Base: `origin/main` (`d52885c`, the branch's first parent)
- Reviewer: `aac51c575c7af06ac` — did not author this PR, #168, #165 or #160
- Verdict: `APPROVED` — no blocking code defect; eight non-blocking findings (F1-F8)

## 0. Method

Everything below was re-derived at the reviewed head with `git diff`, `grep`,
`sed` and `Read`. No claim in the PR description, in a code comment, or in the
design note was accepted as evidence for itself. The test suite's load-bearing
claims were checked by deliberately breaking the implementation and confirming
the corresponding test fails (§4). All mutations were reverted and
`git status --porcelain` was empty before this file was created.

The contract is `work/notes/2026-08-25-rns-validation-tier-hookin-design.md`
(433 lines, merged via #168), read in full, plus the six non-blocking findings
N1-N6 from `work/reviews/pr-168-review-evidence.md` §13, which the
implementation was required to absorb (§5).

## 1. Output boundary — PASS

`git diff --name-only origin/main...4a35ad2` lists exactly five files:

```
runtime/cli.py                            |  15 +
runtime/recovery/production.py            | 289 +++++++++++++++-
runtime/recovery/supervisor.py            |  54 +++
tests/test_recovery_production_trigger.py | 531 +++++++++++++++++++++++++++++-
tests/test_recovery_supervisor.py         | 248 ++++++++++++++
```

`git diff --stat origin/main...4a35ad2 -- runtime/harness/ runtime/state/ work/roadmaps/ work/ scripts/` is
empty. `runtime/harness/hooks.py`, `runtime/harness/service.py`,
`runtime/environment/validation.py` and `runtime/state/schema.sql` are all
untouched. This is exactly the allowed scope of design-note §6.

## 2. Per-claim verification

### Claim 1 — `supervisor.py` change is minimal and purely additive: **VERIFIED**

The three-dot diff of `supervisor.py` contains **no deletions and no modified
lines** — every hunk is an insertion. Concretely:

- `resume_validator: Any | None = None` added at line 56, inside the existing
  keyword-only block (the `*` is already at line 47), alongside
  `environment_reader` (54) and `harness_service` (55).
- `self.resume_validator = resume_validator` at line 98, after a 22-line
  interface-only comment.
- `resume_validation: dict[str, Any] | None = None` initialised at line 318,
  immediately after the identical `harness_resume` initialisation.
- The key `"resume_validation": resume_validation` added to all five action
  dicts: suppress/terminal_session (331), suppress/task-reason (356),
  resolve (372), fail (395), and the resume outcome dict (500).
- Exactly one call site, at lines 407-419.

Placement is correct per §2.2. The retry-budget block is `if attempt >=
len(self.backoff_seconds):` at line 384, whose `continue` ends at 397. The
resume attempt begins at `resolved = False` (421) / `self.harness_service is
not None` (422), with the direct fallback `self.hcom.resume(...)` at 471. The
new block sits at 407-419 — after the budget `continue`, before the resume.
Confirmed by reading `tick()` in full (lines 297-503), not by trusting the
comment.

Unchanged by inspection of the same full read: `_CANONICAL_DENIAL_CODES`, the
`resume_denied` attribution branch, the `attempt += 1` / `next_attempt_at`
backoff computation (`self.backoff_seconds[min(attempt - 1, len(...) - 1)]`),
`_advisory_environment_evidence`, `_resolve_harness_binding`, and the
`environment_evidence` / `harness_resume` payload shapes.

One consequence worth stating explicitly rather than leaving implicit: the
action-dict *shape* does change for every consumer — all five dicts gain a
`resume_validation` key, `None` when unconfigured. That is what §2.2 asks for.
The `claim` path prints nothing on stdout, so `claim`'s machine-readable output
is unaffected; `recovery-tick`'s emitted JSON gains the key.

### Claim 2 — the observation is genuinely ADVISORY: **VERIFIED**

`grep -rn "resume_validation" runtime/` returns 12 hits. Classified by hand:

- `production.py:126`, `production.py:331`, `supervisor.py:82`,
  `supervisor.py:85` — comments/docstrings.
- `supervisor.py:318` — initialisation to `None`.
- `supervisor.py:331,356,372,395,500` — writes into action dicts.
- `supervisor.py:409,416` — assignment from the validator / from the
  containment handler.

**Zero reads.** There is no `if resume_validation`, no `.get("passed")`, no
`resume_validation[...]` anywhere in `runtime/`. The value is written and never
consulted. The retry budget (`attempt >= len(self.backoff_seconds)`, line 384)
is evaluated 23 lines *before* the validator is even called, so it is not
reachable by validation state. No `compatibility_state` is derived: `grep -rn
"compatibility" runtime/recovery/` returns nothing in the new code.

Mutation M1 (§4) confirms this is a property of the code and not of my reading:
inserting a gate makes two tests fail.

### Claim 3 — no default or ambient `EnvironmentSpec`: **VERIFIED**

`grep -rn "load_environment_spec\|rev-parse\|getcwd\|Path.cwd\|os.getcwd\|EnvironmentSpec" runtime/recovery/`
returns exactly one hit — `production.py:40`, prose inside the authority note.
No file loader, no cwd inference, no `git rev-parse`, no bundled spec, no
"last spec we saw", no synthesis from a fingerprint.

The only spec source is `RunBoundValidator.validate_for_run`
(`production.py:230-296`):
`self.environment_reader.list_run_environment_evidence(str(run_id))` →
`rows[-1]["spec_snapshot"]` → `parse_environment_spec(dict(snapshot))`
(line 265). `run_id` comes from `incident.get("run_id")` at `supervisor.py:410`
— the incident's own bound run, nothing ambient. Test
`test_validator_receives_the_incidents_own_bound_run_id` pins that the
validator sees `None` when the incident has no run, and
`test_no_ambient_spec_source_exists_in_the_composition_root` is a source guard
over `production.py` for the four forbidden tokens. Mutation M2 turns both red.

Q5 is implemented as recommended: `hashes = {…}` over all rows, `spec_ambiguous`
when `len(hashes) > 1`, otherwise `rows[-1]`. The `spec.sha256 != stored_hash`
backstop is at line 272.

### Claim 4 — `--repo-root` on `recovery-tick` defaults to `None`: **VERIFIED**

`runtime/cli.py`, the new `recovery_tick.add_argument('--repo-root',
default=None, …)`, carries a five-line comment naming the divergence from
`context --repo-root` and `flow start --repo-root` (both `default='.'`). It is
threaded through as `validation_repo_root=args.repo_root` at `cli.py:393`.
`run_recovery_tick` constructs a validator only `if validation_repo_root is not
None` (`production.py:361`). Mutation M3 turns
`test_recovery_tick_repo_root_defaults_to_none_not_cwd` red.

### Claim 5 — the remaining non-goals: **VERIFIED**

- **No report cache.** No memoisation anywhere in `RunBoundValidator`. The
  per-tick counter (`self.validations_run`) and wall-clock accumulator
  (`self.seconds_used`) skip work with a recorded `budget_exceeded` reason
  rather than reusing a prior result; no `ValidationTierResult` is retained.
- **No daemon/scheduler/thread/timer.** `grep -rn
  "threading\|multiprocessing\|asyncio\|sched\|Timer\|crontab\|while True\|time.sleep\|subprocess"
  runtime/recovery/` returns only pre-existing prose and the unrelated
  incident-state literal `"scheduled"`. `from time import monotonic` is a clock
  read, not a timer.
- **No `HookEnforcement` change, `runtime/harness/hooks.py` untouched.** Not in
  the changed-file list; `HookEnforcement` and `_CANONICAL_DENIAL_CODES` appear
  nowhere in the diff.
- **No task-truth mutation.** No `claim_task`/`submit_task`/`record_review`/
  `promote_ready`/`update_contract` in the diff. `task_reader` is used by
  `RunBoundValidator` only for `list_run_environment_evidence`, a read.
- **No writes to `run_environment_evidence`.** `record_run_environment_evidence`
  appears in `runtime/` only at its definition (`runtime/state/environment.py:44`)
  and in two `production.py` comments. Q7 is "action list only", as recommended.
- **No production `HarnessService` wiring.** `run_recovery_tick` still passes
  neither `harness_service` nor `environment_reader`;
  `test_an_explicit_repo_root_constructs_a_run_bound_validator` asserts
  `environment_reader` is not even in the captured kwargs.

### Claim 6 — the #160 source guard is unmodified and passing: **VERIFIED**

`git diff origin/main...4a35ad2 -- tests/test_recovery_supervisor.py` is
entirely an append after line 914; the only diff line mentioning
`test_no_validation_tier_commands_or_task_mutation_in_source` is a *reference*
to it inside the new test's docstring. The guard itself (its body at
`tests/test_recovery_supervisor.py:901-915`) is byte-identical to `origin/main`.
It passes at the reviewed head, and mutation M6 (adding the literal
`EnvironmentSpec` to a comment in `supervisor.py`) turns it red — so it is
still doing work.

### Claim 7 — no roadmap/checklist status field touched; the inertness is honest: **PARTLY VERIFIED**

No roadmap or checklist file appears in the diff. `work/roadmaps/CAPABILITY_CHECKLIST.md`
line 25 (`H4 — Immediate validation hooks`), line 48 (`E4 — Validation tiers`)
and line 114 (`6.5 | Immediate deterministic validation`) all still read
`IN PROGRESS`.

I independently re-confirmed the inertness premise:
`grep -rn "record_run_environment_evidence" runtime/ scripts/` finds the
definition and nothing else, so `run_environment_evidence` still has **zero
production writers** and every real incident today gets
`{"attempted": False, "reason": "no_spec_bound"}`. The code says so plainly in
two places (`production.py:161-165`, `production.py:330-336`), and a test
(`test_no_spec_bound_is_the_answer_when_no_evidence_exists`) pins it.

The "partly" is F1: the *PR description* is the description of a different PR
and says nothing about any of this. The code is honest; the pull request is not.

### Claim 8 — Q2: validation is OFF on the `claim` path by construction: **VERIFIED, and the latency bound is honest**

`runtime/cli.py:375-378`, unchanged by this PR:

```python
if result.ok:
    recovery = run_recovery_tick_isolated(
        store, hcom_timeout_seconds=CLAIM_PIGGYBACK_HCOM_TIMEOUT_SECONDS
    )
```

No `validation_repo_root` is passed, so it takes its `None` default through
`run_recovery_tick_isolated` (`production.py:393`) into `run_recovery_tick`
(`production.py:311`), where the `if validation_repo_root is not None`
conditional at line 361 constructs no validator. `resume_validator=None` reaches
the supervisor, `self.resume_validator is not None` at `supervisor.py:407` is
false, and no command runs. This is structural, not a flag default that a
future caller could trip over accidentally: enabling validation on the claim
path would require someone to add a new argument to that call.

`CLAIM_PIGGYBACK_HCOM_TIMEOUT_SECONDS = 3.0` and its ~6s worst case are
therefore untouched. Two tests cover it —
`test_claim_piggyback_never_enables_validation` (asserts the kwarg is `None`)
and `test_claim_runs_no_declared_command_even_with_run_bound_evidence` (patches
`production._default_executor` with a tripwire and asserts nothing executes).
See F6 on the second test's name.

**Worst-case latency on the opted-in `recovery-tick` path — I checked the
arithmetic rather than the prose.** `_bounded_executor` (`production.py:216-227`)
checks `self.clock() >= deadline` *before* starting each command and raises
`_ValidationBudgetExceeded`; it cannot interrupt a command already running.
`_default_executor` has `timeout=600` per command
(`runtime/environment/validation.py:57`). So per incident, at most one command
can start just inside the deadline and then run for up to 600s; every
subsequent command in that tier is refused. After that incident,
`self.seconds_used` (~660s) exceeds `DEFAULT_VALIDATION_TICK_BUDGET_SECONDS`
(120.0), so every later incident short-circuits to `budget_exceeded` at
`production.py:255-259`. Worst case for the whole tick is therefore roughly
`tier_budget + 600s ≈ 660s`, which is inside the docstring's stated bound of
"DEFAULT_VALIDATION_TICK_BUDGET_SECONDS across the whole tick plus at most one
in-flight command's own timeout (600s)". The admission is accurate and not
understated. Tightening the 600s ceiling genuinely does belong to
`validation.py`, not here.

### Claim 9 — N4 authority argument: **PRESENT, LARGELY SOUND, TWO OVERREACHES** (see F2)

The argument is at `production.py:35-61`. Its sound parts, each of which I
verified:

- Rows require an existing `run_manifests.run_id` FK
  (`schema.sql:482`) and carry `recorded_by`.
- Rows are insert-only: `UPDATE` is refused by a trigger, proven by
  `test_evidence_rows_cannot_be_tampered_with_in_place`, which I saw pass.
- Only `quick` is reachable: `VALIDATION_TIER = "quick"`, asserted by
  `test_the_declared_budget_constants_are_actually_bounded`.
- Blast radius is bounded by composition (Claim 8).

The two overreaches are F2. I judged the argument on soundness, not presence,
as instructed, and concluded it is good enough to land behind the current
gating but should not survive unchanged into the day a production evidence
writer exists.

### Claim 10 — N1/N2/N3/N5 absorption: **VERIFIED** (details in §5)

## 3. Test quality

The positive path, the negative path and the containment path are all covered,
and the reason vocabulary is pinned:

- **A *failing* validation does not block a resume** —
  `test_a_failing_validation_changes_nothing_about_the_resume` is the strongest
  test in the PR. It is not a "passing validation doesn't block" test: it runs a
  control tick with no validator, captures a 7-tuple of
  `(action, attempt, error, incident.state, last_error, next_attempt_at,
  incident.attempt)`, then runs an identical tick with a validator returning
  `passed: False` and asserts the tuples are equal *and* `hcom.resumes` is
  equal. That is exactly Q1's requirement, tested by differential comparison
  rather than by asserting a hardcoded expectation.
- **`no_spec_bound` when no evidence exists** —
  `test_no_spec_bound_is_the_answer_when_no_evidence_exists` builds a *real*
  `TaskStore` with a real task, claim and run manifest, records no evidence, and
  asserts the exact dict `{"attempted": False, "reason": "no_spec_bound"}`, that
  `passed` is absent, and that `validations_run == 0`.
- **A real claim-path test** — two, described under Claim 8.
- **A real latency/budget test** — `ValidationBudgetTests` covers the count cap,
  the per-tier wall clock (with a `FakeClock`, asserting the tier stopped after
  one of ≥2 declared commands rather than claiming a pass), and the per-tick
  wall clock.
- **Q8** — five separate tests assert `resume_validation is None` and
  `validator.calls == []` for suppressed / resolved / retry-exhausted /
  not-yet-due incidents.
- **Q6** — an exploding validator and an exploding reader are both contained;
  the supervisor-level one additionally asserts the caller's exception text
  (containing `sk-live-…`) does not appear in `repr(action)`.
- **Redaction** — `test_command_output_is_secret_redacted_in_the_recorded_result`
  asserts a leaked token is absent from `json.dumps(result)`.
- **Fixture non-vacuity** — the positive-path test asserts
  `self.assertTrue(self.spec.validation.quick, "fixture must declare commands")`
  and the tier-budget test asserts `len(self.spec.validation.quick) >= 2`, so
  neither can silently degrade into "the tier ran zero commands and passed".

## 4. Mutation testing (non-tautology check)

Seven mutations, each applied to the implementation only, each followed by
`git checkout` of the mutated file. Baseline before any mutation:
`python3 -m unittest tests.test_recovery_supervisor tests.test_recovery_production_trigger`
→ `Ran 93 tests in 377.202s / OK`.

| # | Mutation | Result |
|---|---|---|
| M1 | `supervisor.py`: added `if isinstance(resume_validation, dict) and resume_validation.get("passed") is False: continue` immediately before `resolved = False`, i.e. made a failing validation gate the resume | **RED** — `ResumeValidationAdvisoryTests` 2 errors: `test_a_failing_validation_changes_nothing_about_the_resume` and `test_a_hcom_resume_failure_still_records_the_validation` both `IndexError: list index out of range` (no action emitted) |
| M2 | `production.py`: replaced `if not rows: return self._skip("no_spec_bound")` with a fallback that `load_environment_spec`s `runtime/environment/specs/maps-runtime-ci.json` and synthesises a row | **RED** — 2 failures: `test_no_spec_bound_is_the_answer_when_no_evidence_exists` (got `validation_error`, not `no_spec_bound`) and `test_no_ambient_spec_source_exists_in_the_composition_root` (`'load_environment_spec' unexpectedly found`) |
| M3 | `cli.py`: changed `--repo-root` `default=None` to `default='.'` | **RED** — `test_recovery_tick_repo_root_defaults_to_none_not_cwd`: `AssertionError: '.' is not None` |
| M4 | `production.py`: deleted the `if self.validations_run >= self.max_validations` count cap | **RED** — `test_the_per_tick_count_cap_is_enforced`: `AssertionError: True is not false` (third validation ran) |
| M5 | `production.py`: deleted the `if stored_hash and spec.sha256 != stored_hash` check | **RED** — `test_a_snapshot_disagreeing_with_its_hash_is_rejected_rather_than_executed`: got `validation_error` instead of `spec_hash_mismatch`, i.e. the tampered `rm -rf /` command was dispatched to the executor rather than refused |
| M6 | `supervisor.py`: added the comment `# runs the EnvironmentSpec-declared quick validation tier` next to `self.resume_validator = ...` | **RED** — 2 failures: the #160 guard `test_no_validation_tier_commands_or_task_mutation_in_source` *and* the new `test_supervisor_source_never_names_the_declared_environment_spec_type`. Both guards are live; the new one is not vacuous |
| M7 | `supervisor.py`: hoisted the whole validation block from line 407 up to immediately after the `resume_validation = None` initialisation, i.e. broke the §2.2 placement | **RED** — 4 failures: `test_suppressed_incident_runs_no_validation`, `test_resolved_incident_runs_no_validation`, `test_retry_budget_exhausted_incident_runs_no_validation`, `test_not_yet_due_incident_runs_no_validation` |

No mutation passed silently. Every load-bearing claim I tried to break has a
test that notices.

After the last revert, `git checkout runtime/` followed by
`git status --porcelain` produced **no output**, and `git diff --stat HEAD` was
empty, before this evidence file was created.

## 5. N1-N6 absorption

- **N1 — absorbed.** `SupervisorSourceBoundaryTests.test_supervisor_source_never_names_the_declared_environment_spec_type`
  states in its docstring that the guard is "a lowercased substring scan over
  the *entire* source text -- code, comments and docstrings alike -- not an
  import check", and the 22-line comment at `supervisor.py:76-97` says the same
  in the implementation. Non-vacuity is handled explicitly: the test also asserts
  `EnvironmentSpec` *is* present in `production.py`, so the boundary would fail
  if the composition root stopped being the place that names it. M6 proves the
  assertion is live.
- **N2 — absorbed, no contradiction found.** `no_validator_configured` appears
  nowhere in `runtime/`. `VALIDATION_SKIP_REASONS` (`production.py:129-138`) has
  eight members and does not include it. The single contract is `None`, stated
  at `supervisor.py:85-87`, `production.py:127-129` and `production.py:331-335`,
  and pinned by `test_no_validator_configured_leaves_the_key_none_everywhere`.
  See F4 for the one residual soft edge in the *documented interface* (not in
  the behaviour).
- **N3 — absorbed by explicit specification.** The "Double-read note" at
  `production.py:167-179` states that in the production composition
  `environment_reader` stays `None` while the validator does its own read, so
  there is exactly one read per incident and no possible disagreement; and that a
  deployment configuring both gets two sequential reads whose only possible
  divergence is an appended row, both values being advisory. I verified the
  premise: `run_recovery_tick` passes no `environment_reader`
  (`production.py:365-374`), and
  `test_an_explicit_repo_root_constructs_a_run_bound_validator` asserts
  `assertNotIn("environment_reader", captured)`. The table is append-only, which
  I confirmed against `schema.sql` and the passing immutability test.
- **N4 — absorbed, with reservations.** See Claim 9 and F2.
- **N5 — cosmetic, about a line cite in the design note.** The note is not a file
  this PR may modify, so nothing was expected here and nothing was done.
- **N6 — absorbed.** `cli.py` carries the exact clause N6 asked for
  ("Deliberately unlike `context --repo-root` and `flow start --repo-root`,
  which both default to '.'"), and the behaviour has its own regression test
  whose docstring quotes N6. M3 proves it is live.

## 6. Full suite

Run as a blocking foreground call, whole suite, no subset, no short timeout:

```
python3 -m unittest discover -s tests
```

Verbatim result:

```
Ran 844 tests in 1831.284s

OK (skipped=6)
```

Exit code: **0**. Wall clock ~30.5 minutes. The 6 skips are pre-existing
(`sssss` plus one, visible in the dot stream at positions unrelated to the
recovery modules); no failures, no errors.

For reference, before any mutation was applied I also ran the two touched
modules alone: `python3 -m unittest tests.test_recovery_supervisor
tests.test_recovery_production_trigger` → `Ran 93 tests in 377.202s / OK`.
Of those 93, 55 are pre-existing and 38 are new (11 in
`ResumeValidationAdvisoryTests`, 2 in `SupervisorSourceBoundaryTests`, 13 in
`RunBoundValidatorTests`, 4 in `ValidationBudgetTests`, 3 in
`ValidationCompositionTests`, 5 in `ValidationCliWiringTests`).

CI-parity re-run of the two touched modules under the warning filter CI sets
(`PYTHONWARNINGS=error::ResourceWarning`, per
`.github/workflows/runtime-stack-tests.yml`):

```
Ran 93 tests in 292.602s

OK
```

Exit code **0** — so the new code raises no `ResourceWarning` under the setting
CI enforces. (The full 844-test discovery pass above was run with the default
warning filter; the CI-parity check covers the two modules this PR changes.)

## 7. Findings

**No blocking code defect.**

### F1 — non-blocking on the code, but must be fixed before merge: the PR description belongs to a different PR

The GitHub description of #172 is verbatim the description of the SEC4
skill-lifecycle durable-storage PR. It describes
`runtime/state/schema.sql` (+106 lines, two new tables),
`runtime/state/skill_lifecycle_storage.py`, `runtime/state/store.py` and
`tests/test_skill_lifecycle_storage.py` (35 tests) — **none of which appear in
this PR's diff**, which touches `runtime/cli.py`,
`runtime/recovery/production.py`, `runtime/recovery/supervisor.py` and two
recovery test modules. It resolves "8 behaviour questions" from a *different*
design note (`…-sec4-skill-lifecycle-persistence-design.md`), not the Q1-Q9 of
the note this PR implements.

Consequences: every substantive claim in the description is false with respect
to the code; the description contains no statement of the advisory contract, no
Q2 latency justification, and — the specific thing this review was asked to
confirm — **no disclosure that the feature is inert in production**. That
disclosure exists and is excellent in the code (`production.py:161-165`,
`330-336`) and in the design note, but a reader of the PR would never learn it.
It also means the PR's own "Full suite ... passing" claim is not a claim about
this code.

This is an administrative defect, not a code defect: rewriting the description
changes no tracked file and requires no re-review of the implementation. It
should nonetheless be corrected before merge, because the PR body is the
durable record future archaeology reads first.

### F2 — non-blocking: the N4 authority argument overreaches in two places

The argument (`production.py:35-61`) is present, structured and mostly sound
(Claim 9). Two of its load-bearing sentences do not survive checking:

1. *"an attacker who can insert rows there can already redirect the pass in
   worse ways."* I checked what the recovery pass can already be made to do from
   the task DB. The only other subprocess on this path is `HcomAdapter._run`
   (`runtime/communication/hcom_adapter.py:80-90`), which builds a fixed
   `argv = (self.executable, *args)` and passes **`shell=False`**. `grep -rn
   "shell=True" runtime/` returns exactly one hit in the whole repository:
   `runtime/environment/validation.py:54`. So before this PR, write access to
   `maps.db` bought control of task truth, claims and lineage — but *not*
   arbitrary local shell execution as the user running the pass. After this PR,
   with `--repo-root` supplied, it does. That is an escalation in kind, not in
   degree, and "already worse" is asserted rather than shown.
2. *"a deliberate, bounded widening of the trust boundary
   `runtime/environment/validation.py` already relies on for
   `EnvironmentSpec.setup_commands`."* `grep -rn "setup_commands" runtime/`
   shows `setup_commands` is only ever *declared*, parsed and serialised
   (`spec.py:145,178,249,306`) — nothing anywhere in the codebase executes it.
   `run_validation_tier` likewise had zero production callers before this PR
   (`production.py:281` is now the first). So there is no existing production
   trust boundary being widened; this PR *creates* the first production
   execution of `EnvironmentSpec`-declared shell commands.

Why this is not blocking: the path is unreachable today (zero production writers
of `run_environment_evidence`), requires an explicit `--repo-root` naming a
checkout, is off the `claim` path, and is capped to `quick`. The gating is
genuinely good. But the *reasoning* is what a future reader will inherit when a
production evidence writer lands and makes this live. Recommend rewriting those
two bullets to say what is true — that this is a new privilege, deliberately
accepted because it is opt-in and explicitly invoked — and that the authority
question be re-decided, not inherited, at the moment a production writer of
`run_environment_evidence` is introduced.

### F3 — non-blocking: the spec-hash check is conditional, which the authority note does not mention

`production.py:271-276` reads `if stored_hash and spec.sha256 != stored_hash:`.
A row whose `environment_spec_hash` column is the empty string skips the check
entirely and executes. `schema.sql:484` is `TEXT NOT NULL`, which permits `''`,
and the validator is duck-typed so the reader need not be the real store. The
authority note describes the check without qualification ("the snapshot's
`sha256` is re-derived and compared against the row's `environment_spec_hash`
column before anything runs"). Unreachable via `record_run_environment_evidence`
(which always writes `spec.sha256`), so this is a documentation/robustness nit,
not a live hole. Making the check unconditional — treat a missing hash as
`spec_hash_mismatch` — would cost one word and make the sentence true.

### F4 — non-blocking: the documented validator interface still admits the N2 ambiguity

`supervisor.py:78-79` documents the contract as `validate_for_run(run_id) ->
dict | None`, while `supervisor.py:85-87` (four lines later) defines `None` on
the action dict to mean "no validator configured". A duck-typed validator that
returns `None` therefore produces a `resume_validation` indistinguishable from
"unconfigured" — precisely the null-vs-dict confusion N2 asked to be eliminated.
`RunBoundValidator.validate_for_run` is correctly annotated `-> dict[str, Any]`
and every return path returns a dict, so no shipped code hits this. Narrowing
the documented interface to `-> dict` would close it.

### F5 — non-blocking: no end-to-end test through the CLI with `--repo-root` *and* run-bound evidence

The positive path is covered on both sides of the seam —
`RunBoundValidatorTests` proves `RunBoundValidator` runs the tier and produces
the payload, `ResumeValidationAdvisoryTests` proves the supervisor records
whatever the validator returns — but no test drives
`maps recovery-tick --repo-root <dir>` against a store holding real
`run_environment_evidence` and asserts a tier result lands in the emitted JSON.
`test_recovery_tick_passes_an_explicit_repo_root_through` stops at the kwarg.
Both halves being individually pinned makes this low-risk; the composition is
where an integration mistake would hide.

### F6 — non-blocking: one test's name and docstring overstate its setup

`test_claim_runs_no_declared_command_even_with_run_bound_evidence`
("End-to-end: a claim cannot be stalled by a run's declared validation tier")
calls `self.create_ready("task-a")` and claims it. It creates no run manifest
and records no environment evidence, so there is no run-bound evidence in the
scenario at all. The test is still meaningful — it is a tripwire on
`_default_executor` that fires if a validator is ever constructed on the claim
path — but it proves less than its name says, and a reader auditing Q2 coverage
would over-credit it. Either record evidence in the fixture or rename it.

### F7 — non-blocking: `production.py` now depends on a fragile module import order with nothing guarding it

The comment at `production.py:73-80` claims `runtime.state` must be imported
before `runtime.environment` or the import fails. I verified the claim rather
than trusting it: `python3 -c "import runtime.environment"` raises
`ImportError: cannot import name 'EnvironmentFingerprint' from partially
initialized module 'runtime.environment' (most likely due to a circular
import)`, while importing `runtime.state.observability` first succeeds. The
comment is accurate and the pre-existing circularity is genuinely out of scope.
But `runtime.recovery.production` is now the module that would break, and
nothing mechanically prevents an import sort from reordering those two lines —
CI's `ruff check --select E9,F63,F7,F82` does not include `I`. A one-line
`# isort: skip_file`-style marker, or a test that imports
`runtime.recovery.production` in a fresh interpreter, would make the constraint
enforceable rather than advisory. (The existing test suite does import the
module, so an accidental reorder would be caught by CI today — but only
incidentally.)

### F8 — non-blocking, cosmetic: cross-module import of a private name

`production.py:88`: `from runtime.environment.validation import
_default_executor`. Importing an underscore-prefixed name across module
boundaries is unusual, and the seven-line comment justifying it is sound (the
#165 source guard forbids `production.py` from importing `subprocess`, and
re-implementing the executor would duplicate the command-execution trust
boundary). Promoting `_default_executor` to a public export of
`runtime.environment` would be tidier, but that is a change to a module this PR
may not touch. Recording it so it is a known choice rather than an accident.

## 8. Reviewer limits

- The 844-test discovery pass used the default warning filter, not CI's
  `PYTHONWARNINGS=error::ResourceWarning`. I closed that gap only for the two
  modules this PR touches (§6, `Ran 93 tests / OK`), not for the whole suite, so
  a `ResourceWarning`-only regression *elsewhere* in the suite would not have
  been caught by me. Nothing in this PR is plausibly a cause — the new code opens
  no files or sockets of its own — and CI runs the full suite under that filter
  anyway.
- I did not run `ruff`, `bandit` or the LangGraph smoke step. `bandit -ll -r
  runtime` is the one I would most want: the new code adds no `subprocess`
  call of its own, but it is the first production caller of the one `shell=True`
  site in the repo. That site already carries `# nosec B602` and is unchanged, so
  bandit's verdict cannot have moved, but I am inferring rather than observing.
- I evaluated whether the authority argument for executing DB-sourced commands
  is *sound as written* (F2). I did not perform a threat model of the deployment
  as a whole, and I am not the right authority to decide whether the escalation
  F2 describes is acceptable policy once a production writer of
  `run_environment_evidence` exists. My position is narrower: it is acceptable
  *now*, because the path is unreachable and opt-in, and the written reasoning
  should be corrected before it stops being either.
- The mutation testing in §4 is targeted, not exhaustive. I broke the seven
  properties I judged load-bearing. A test elsewhere in the two new suites could
  still be tautological without my noticing; I read all 38 new validation tests
  but only proved seven claims by mutation.
- I reviewed the code, not the GitHub PR metadata beyond noting F1. I did not
  check CI status on the PR, and F1 was found only because the description
  contradicted the diff so obviously.
- `main` did not move during this review, so no rebase or `head_sha` rebind was
  required; the reviewed head `4a35ad2` is the branch tip and its first parent
  is `origin/main`.
