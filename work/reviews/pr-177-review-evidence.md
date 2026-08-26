# Independent review evidence — PR #177

reviewer: independent-review-agent a951dc9e23a86177e (did not author PR #177)
head_sha: 37fde1b832917db561d027abc28e4f77d827e3a8
independent: true
summary: APPROVED — design-only note, all three priority claims re-derived and confirmed at source; six non-blocking accuracy findings, two of them substantive (S3d "tests included" is false, and S3c's "out-of-project incidents are unaffected by enforcement" is contradicted by the guard/adapter ordering).

## Scope reviewed

PR branch `hook-enforcement-composition-design`, reviewed at code head
`37fde1b`. Diff versus `origin/main`:

```
$ git diff --stat origin/main...HEAD
 ...-26-hook-enforcement-composition-root-design.md | 470 +++++++++++++++++++++
 1 file changed, 470 insertions(+)
```

One added file, `work/notes/2026-08-26-hook-enforcement-composition-root-design.md`.
No `runtime/`, no `tests/`, no `work/roadmaps/` path is touched. Non-goal 8
("no roadmap row flipped to DONE") is therefore satisfied mechanically, as are
non-goals 1-7 (all of which constrain runtime code this PR does not contain).

## Verification runs

- Full suite: `python3 -m unittest` over every `tests/test_*.py` module, blocking
  foreground run, output captured to `/tmp/pr177-suite.txt`. Exit code: 0.
  `Ran 898 tests in 1259.138s` / `OK (skipped=6)`.
  (`python3 -m pytest` is not usable here — pytest is not installed in this
  environment — and plain `unittest discover -s tests` fails with "Start
  directory is not importable" because `tests/` has no `__init__.py`, so the
  modules were loaded explicitly by name with `.` and `tests` on `sys.path`.)
- Smoke: `python3 -m runtime.smoke > /tmp/pr177-smoke.txt`. Exit code: 0,
  terminal JSON `"ok": true`.

Both green, as expected for a docs-only change.

## Priority item 1 — the zero-caller finding

Re-derived at `37fde1b`, not taken from the note.

`grep -rn "HarnessService(\|HookRegistry(\|register_canonical_run_guards(" --include=*.py .`
returns **61** matches. Exactly **two** are outside `tests/`:

- `runtime/harness/service.py:27` — `self.hooks = hooks or HookRegistry()`, the
  internal empty-registry fallback, confirmed by reading the line.
- `runtime/policy/harness_guard.py:194` — the definition of
  `register_canonical_run_guards`, confirmed by reading the file.

The other 59 are under `tests/`. The note's substantive claim is correct.

FINDING 1 (minor, methodological). The command pasted in S1 and described as
reproduced "verbatim" ends in `| grep -v '/tests/'`. Run from the repo root,
`grep -rn ... .` emits paths of the form `tests/test_foo.py:87` — no leading
slash — so that filter matches nothing and the pasted command actually prints
all 61 lines, not the 2 shown. The pasted block therefore cannot be literal
output of the command above it. The conclusion is unaffected (I confirmed it by
inspecting all 61 hits), but a note whose stated purpose is "not trusted;
re-run" should not paste a transcript its own command does not produce.

The second grep in S1 is accurate: within `runtime/`,
`DestructiveExternalActionGuard` / `register_destructive_external_action_guards`
appear only in `runtime/policy/destructive_action_guard.py` (definition plus
helper) and `runtime/policy/__init__.py` (re-export).

## Priority item 2 — the CanonicalRunGuard safety analysis

Read from `runtime/policy/harness_guard.py` directly.

Confirmed:
- `CanonicalRunGuard.__call__` spans lines 158-191. Every failure path returns
  `self._deny(...)`, which constructs `HookOutcome(HookDirective.DENY, ...)`
  (line 36-37). The single success path is line 186-191, an
  `HookDirective.ANNOTATE` outcome with `guard_code="CANONICAL_RUN_VERIFIED"`.
- `HookDirective.ALLOW` occurs **zero** times in the file;
  `REQUIRE_APPROVAL` occurs **zero** times. Fail-closed by construction: correct.
- S2a's claim about registration constraints holds:
  `HookRegistry._register_enforcement` (`runtime/harness/hooks.py:193-212`)
  raises unless `failure_policy == FAIL_CLOSED` (line 207-208) and
  `side_effect == READ_ONLY` (line 209-210).

FINDING 2 (minor, factual). S2 says "There are 17 distinct deny codes ... and
six `SESSION_*` lineage denials." Counted from source: **28** `_deny(...)` call
sites, **23** distinct codes, of which **9** are `SESSION_*`
(`SESSION_REF_REQUIRED`, `SESSION_REF_INCOMPLETE`, `SESSION_PROJECT_MISMATCH`,
`SESSION_ADAPTER_MISMATCH`, `SESSION_NOT_DURABLY_BOUND`,
`SESSION_ADAPTER_UNPROVEN`, `SESSION_LINEAGE_INVALID`,
`SESSION_LINEAGE_UNPROVEN`, `SESSION_BINDING_MISMATCH`). Both numbers are wrong
and both understate the guard's strictness, so the direction of the error is
toward the note's own conclusion rather than against it.

### S2b table

Verified against `runtime/recovery/supervisor.py::_resolve_harness_binding`
(lines 148-211). It does pre-filter: `run_id` present, task existence,
non-empty `project_id`, resolvable `compute_task_revision`, and lineage
`state == "EXPLICIT"` with a non-empty `session_id` and `adapter_id == "hcom"`.
It does **not** check `task.status`, `task.claimed_by`, `lease_expires_at`,
`check_run_stale`, or the binding-versus-current revision comparison. All five
"No" cells in the table are correct as written.

FINDING 3 (moderate, S2b). The `TASK_REVISION_STALE` row is technically true but
practically misleading. `_resolve_harness_binding` sets the binding's
`task_revision` from `compute_task_revision(task_id)` at bind time, and the
guard's `require_current_revision` branch (`harness_guard.py:73-76`) compares
`compute_task_revision(task_id)` against that same value moments later — a
tautology on this path, so `TASK_REVISION_STALE` is effectively unreachable via
RnS. The denial that actually fires for the same underlying drift is
`RUN_REVISION_MISMATCH` (`harness_guard.py:71-72`, manifest revision versus the
freshly computed one), which the table omits entirely. Net first-exposure
exposure is unchanged or slightly larger, not smaller.

### The traced consequence chain

Every link checked at source and correct:

1. Guard `DENY` -> `HookRunResult.denied` -> `permitted` False.
2. `HarnessService.resume` returns `self._hook_block("resume", before)` at
   `runtime/harness/service.py:310` (the note cites 309; the `if not
   before.permitted:` test is at 309 and the return at 310 — close enough to be
   a pointer, not an error). `_hook_block` (lines 114-140) yields
   `OperationResult.failure("HOOK_DENIED", ...)` when `result.denied`.
3. `supervisor.py:24` defines
   `_CANONICAL_DENIAL_CODES = {"HOOK_DENIED", "APPROVAL_REQUIRED"}` — exact.
4. `supervisor.py:447` is the `elif str(result.code) in _CANONICAL_DENIAL_CODES:`
   branch, setting `action = "resume_denied"` and `resolved = True` — exact, and
   there is genuinely no fallback: the `if not resolved:` direct-resume block
   below is skipped.
5. `supervisor.py:384` `if attempt >= len(self.backoff_seconds):` sets
   `state = "failed"`, `last_error = "retry_budget_exhausted"` — exact.

### S2c, the shadow-mode impossibility

Confirmed. `HarnessService.resume` calls `_require_canonical_enforcement(
HookEvent.BEFORE_RESUME, "resume")` at line 294 and `self.hooks.run(...)` at
line 300 — enforcement check strictly first. With no `CANONICAL_RUN` enforcement
registered, `has_enforcement` is False and the method returns
`CANONICAL_GUARD_REQUIRED` (`service.py:69-76`) before the guard is ever
invoked, so a non-enforcement registration cannot produce annotations.
`CANONICAL_GUARD_REQUIRED` is indeed **not** in `_CANONICAL_DENIAL_CODES`, so
that outcome falls through to the direct resume — which does make an
empty-registry `HarnessService` a pure no-op, as the note says.

### Verdict on the conclusion under review

**Agreed, independently.** "Fail-closed in the authority sense, strict in the
availability sense; an explicit opt-in feature gate IS required for first
production exposure" is the correct reading of this source. My reasoning, not
the note's: the guard cannot grant, so composing it creates no privilege; but on
the RnS path a denial is not observational — it is terminal for that pass, burns
an attempt, and has no fallback, and `LEASE_EXPIRED` is close to the expected
case for exactly the population RnS operates on (sessions that stopped
silently). No shadow mode is reachable without changing `tick()` or the
service's enforcement-before-run ordering, both correctly declared non-goals. And
Finding 4 below makes default-on strictly worse than the note itself estimates.
Default-off with an explicit operator opt-in is the right call.

## Priority item 3 — non-goals

Satisfied. Diff is one added file under `work/notes/`. No runtime, test, or
roadmap file is modified; no checklist row is flipped.

## Secondary checks

**S3b, `TaskStore` satisfies `CanonicalRunSource` by duck typing.** All five
protocol members verified present, both by source line and by
`hasattr(TaskStore, ...)`: `get_task` (`runtime/state/base.py:249`),
`get_run_manifest` (`runtime/state/integrity.py:378`), `compute_task_revision`
(`runtime/state/integrity.py:108`), `check_run_stale`
(`runtime/state/integrity.py:402`), `resolve_run_session`
(`runtime/state/run_lineage.py:227`). Every cited line number is exact.

**S3d, event coverage.** `HarnessService` does fire exactly five events —
`hooks.run(...)` appears at `service.py:181, 197, 253, 300, 333` and nowhere
else in `runtime/`, carrying `RUN_STARTING`, `RUN_STARTED`, `BEFORE_SEND`,
`BEFORE_RESUME`, `SESSION_STOPPING` respectively. Confirmed exact.
`register_destructive_external_action_guards` registers on
`BEFORE_DESTRUCTIVE_ACTION` and `BEFORE_EXTERNAL_ACTION`
(`destructive_action_guard.py:129`). Confirmed.

FINDING 4 (moderate, S3d). "A repo-wide grep finds **no code anywhere, tests
included**, that fires either event through a registry" is **false**. Two test
sites fire them through a registry: `tests/test_harness_hooks.py:68`
(`registry.run(HookEvent.BEFORE_EXTERNAL_ACTION)`) and
`tests/test_destructive_external_action_guard.py:132`
(`registry.run(HookEvent.BEFORE_DESTRUCTIVE_ACTION, {})`), plus further
registrations at `test_destructive_external_action_guard.py:100-153`. The
load-bearing half — that nothing in `runtime/` emits either event — is true, and
the recommendation to leave `DestructiveExternalActionGuard` out of this slice
stands unchanged on that basis. The "tests included" overreach should be dropped
if the note is ever revised, and the same wording is repeated in S5 item 1 and
in the resume prompt.

FINDING 5 (moderate, S3c — the one I would most want the implementer to read).
"Out-of-project incidents are therefore unaffected by enforcement" does not
follow from the source. The ordering in `HarnessService.resume` is:
`_validate_binding_session` (which compares `binding.project_id` against
`session_ref.project_id` only — both are set from the *same* task's
`project_id` by `_resolve_harness_binding`, so they always agree), then
`_get_adapter`, then `_require_canonical_enforcement`, then `hooks.run(...)`
running `CanonicalRunGuard`, and only then `adapter.resume(binding)` at line
311. `HcomHarnessAdapter._project_error` (`adapters/hcom.py:93-100`) is reached
via `_binding_session` (`adapters/hcom.py:294-299`) **inside** `adapter.resume`
— i.e. strictly after the guard has already run. The guard's own
`PROJECT_MISMATCH` (`harness_guard.py:62-63`) compares the binding's project to
the task's project, which on this path is a tautology and never fires.

Consequence: an out-of-project incident is fully subject to canonical
enforcement. If it fails any guard check (an expired lease being the likely
one), it returns `HOOK_DENIED` and is denied with no fallback, exactly like an
in-project incident. It reaches `PROJECT_MISMATCH` and the fallback *only* if it
passes every single guard check first. So the fallback set is materially
narrower than S3c describes. This does not change the design — if anything it
reinforces the gate and the `--harness-project-id` requirement — but it is a
wrong statement about production behavior that an implementer could reasonably
rely on when reasoning about blast radius, and it deserves correcting in the
implementation PR. The note's accompanying operator caveat ("must not read a
clean enforced pass as 'every project was checked'") remains valid.

The remainder of S3c is accurate: `HcomHarnessAdapter` is bound to a single
non-empty `project_id` (`adapters/hcom.py:49-66`), `PROJECT_MISMATCH` is not in
`_CANONICAL_DENIAL_CODES`, and `recovery-tick`'s existing `--repo-root` really
does have `default=None` with a comment explaining why an ambient cwd default
was rejected (`runtime/cli.py:176-191`).

**S6, checklist impact.** Re-read all four rows at this head; S6 characterises
each correctly. H5 (`CAPABILITY_CHECKLIST.md:26`) states the constructor
"deliberately passes `harness_service=None`" and that "`HarnessService(...)` has
zero non-test callers anywhere in the repo". E4 (line 48) states "no
`HookRegistry` in production carries a validation callback". 6.16 (line 125)
carries the composition-layer finding as E6(b). 6.5 (line 114) is written as
"= H4/E4" and does not restate it. None is falsified by a design-only note, so
"no edit warranted" is the right call, and deferring the edit to the
implementation PR matches pass #8's own process finding.

## Citation spot-checks

Checked well beyond the requested eight. Exact and correct:
`runtime/cli.py:290` (`store = TaskStore(args.db)`), `cli.py:376` and
`cli.py:387` (the two `run_recovery_tick_isolated(` call sites, piggyback and
explicit), `cli.py:249` (`flow start` help text, verbatim),
`cli.py:176-191` (`--repo-root`, no default), `cli.py:53-68`
(`_parse_bindings`, "No binding source is inferred"),
`runtime/recovery/production.py:382-392` (the `RecoverySupervisor(...)`
construction) and `:391` (the omission comment, quoted verbatim),
production.py's module docstring ("the single production construction site for
`RecoverySupervisor`", and the harness-service scope statement — the note's
reading of it as a scope statement rather than a policy objection is fair),
`supervisor.py:24`, `:384`, `:422`, `:447`, `harness_guard.py:158-191`, `:194`,
`service.py:181/197/253/300/333`, `hooks.py:193-212`,
`tests/test_recovery_supervisor.py:765-769` (the composition precedent S3b says
to mirror — matches exactly), and the four `runtime/` `main()`-bearing modules
S1a names (`cli.py`, `smoke.py`, `routing/cli.py`, `integrity/cli.py`) — there
are exactly four, so "three other" is right.

FINDING 6 (trivial). S3c cites the supervisor's fallback comment as
`supervisor.py:461-466`; it actually spans 459-465. Off by two, points at the
right block.

## Verdict

**APPROVED.** The design is sound, the three priority claims survive independent
re-derivation, the non-goals are respected mechanically, and both verification
runs are green. None of the six findings changes a design decision or a
recommendation in the note. Findings 4 and 5 are wrong statements about the
current codebase and should be corrected when the implementation PR lands
(Finding 5 in particular, because an implementer reasoning about blast radius
could act on it); Findings 1, 2, 3 and 6 are accuracy defects that do not
propagate. Nothing here is blocking, and nothing was fixed by this reviewer —
the note is unmodified.
