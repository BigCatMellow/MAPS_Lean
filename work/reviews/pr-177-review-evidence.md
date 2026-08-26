# Independent review evidence — PR #177

Three review passes are recorded here, in order.

- **Pass 1** reviewed code commit `37fde1b`, the original design note, and
  returned APPROVED with six non-blocking findings.
- **Pass 2** reviewed `076d59d`, the author's corrections commit answering those
  findings. It accepted five of the six, **retracted pass-1 Finding 1 as a false
  positive of my own making**, and held at CHANGES_REQUESTED because the
  correction made in response to that bad finding had introduced a false claim
  into the note's §1.
- **Pass 3** reviewed `e01bcf4`, which reverts that one passage. It is the final
  pass and the one this file's fields are bound to.

Read the two re-review sections at the end before the pass-1 body: pass 1's
Finding 1 is withdrawn and must not be acted on.

reviewer: independent-review-agent a951dc9e23a86177e (did not author PR #177)
head_sha: e01bcf40f44d44994a2b31054cb6c497b5166724
independent: true
summary: APPROVED — design-only note; all three priority claims independently re-derived at source, the sole blocking defect (a false grep claim I had myself caused by a bad finding) is reverted at e01bcf4, corrections 2-6 verified intact, non-goals respected, full suite and smoke both green.

## Pass 1 — scope reviewed (at 37fde1b)

PR branch `hook-enforcement-composition-design`, reviewed at code head
`37fde1b`. Diff versus `origin/main` at that point:

```
$ git diff --stat origin/main...HEAD
 ...-26-hook-enforcement-composition-root-design.md | 470 +++++++++++++++++++++
 1 file changed, 470 insertions(+)
```

One added file, `work/notes/2026-08-26-hook-enforcement-composition-root-design.md`.
No `runtime/`, no `tests/`, no `work/roadmaps/` path is touched. Non-goal 8
("no roadmap row flipped to DONE") is therefore satisfied mechanically, as are
non-goals 1-7 (all of which constrain runtime code this PR does not contain).

## Pass 1 verification runs

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

FINDING 1 — **RETRACTED in pass 2; see the re-review section. It was a false
positive and should not be acted on.** Original text follows for the record.

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

## Pass 1 verdict (at 37fde1b)

**APPROVED.** The design is sound, the three priority claims survive independent
re-derivation, the non-goals are respected mechanically, and both verification
runs are green. None of the six findings changes a design decision or a
recommendation in the note. Findings 4 and 5 are wrong statements about the
current codebase and should be corrected when the implementation PR lands
(Finding 5 in particular, because an implementer reasoning about blast radius
could act on it); Findings 1, 2, 3 and 6 are accuracy defects that do not
propagate. Nothing here is blocking, and nothing was fixed by this reviewer —
the note is unmodified.

---

## Re-review at 076d59d

The author pushed `076d59d` on top of this evidence commit, acting on all six
pass-1 findings. It touches only
`work/notes/2026-08-26-hook-enforcement-composition-root-design.md`
(70 insertions, 21 deletions); the branch's full diff versus `origin/main` is
now that note plus this evidence file, and no `runtime/`, `tests/`, or
`work/roadmaps/` path is touched. Non-goals still respected.

Each correction was re-verified against source at `076d59d` rather than read
from the author's summary.

### Correction 1 — NOT ACCEPTED, and my original finding is retracted

This is the one item blocking a clean approval, and the fault for it is mine.

Pass 1 claimed that `grep -rn ... .` emits paths without a `./` prefix, so that
S1's `| grep -v '/tests/'` filtered nothing. That claim was **wrong**. The
`grep` I invoked resolves to a shell *function* wrapper in this harness
environment (`command -v grep` -> `grep`, `declare -f grep` shows a function
body), and that wrapper strips the leading `./`. Real GNU grep does not.
Re-run through `/usr/bin/grep` (GNU grep 3.11), bypassing the wrapper:

- `/usr/bin/grep -rn "HarnessService(\|HookRegistry(\|register_canonical_run_guards(" --include=*.py .`
  emits `./tests/...`, `./runtime/...` — 61 lines.
- piping that through `/usr/bin/grep -v '/tests/'` — the note's **original**,
  unanchored form — yields exactly the two lines the note pasted:
  `./runtime/harness/service.py:27` and `./runtime/policy/harness_guard.py:194`.
- piping it through `/usr/bin/grep -v "^\./tests/"` — the new anchored form —
  also yields exactly those two lines.

So the original S1 command was correct and reproducible all along, and pass-1
Finding 1 was a false positive. I retract it without reservation.

The consequence for `076d59d` is that the correction made in good faith on the
strength of that finding now states something false. The new parenthetical in
S1 reads: "an unanchored `grep -v '/tests/'` filters nothing here, because
`grep -rn ... .` emits paths as `./tests/...`". Those two clauses contradict
each other — `./tests/foo.py` contains the substring `/tests/`, which is
precisely why the unanchored filter *does* work. The anchored pattern itself is
harmless and produces identical output, but the justification for it is wrong,
and it is wrong in a note whose S1 exists specifically to demonstrate careful
re-derivation.

Requested change (author's call which way): either revert S1's grep pipeline and
parenthetical to the pre-`076d59d` text, or keep the anchored pattern and
replace the parenthetical with an accurate one — e.g. that the anchor is
belt-and-braces against a path containing `/tests/` below the top level, and
noting that the pasted output lines carry a `./` prefix under real GNU grep that
the transcript omits. Not fixed here: reviewers do not edit the artifact under
review.

### Corrections 2-6 — all accepted, all verified at source

**2 (S2 deny-code counts).** Now reads 28 `_deny(...)` call sites, 23 distinct
codes, nine `SESSION_*`. Matches my independent count exactly. The three added
codes are real and were genuinely missing: `RUN_TASK_MISMATCH`
(`harness_guard.py:67-68`), `RUN_WORKER_MISMATCH` (`:69-70`),
`UNSUPPORTED_OPERATION` (`:164-165`). Accurate.

**3 (S2b revision rows).** Accurate, and the reasoning is now right rather than
merely patched. `supervisor.py:172-176` is exactly where
`_resolve_harness_binding` sets `task_revision` from
`compute_task_revision(task_id)`; `harness_guard.py:73-76` is exactly the
`require_current_revision` branch that recomputes and compares against it, so
"a comparison of a value against itself" is a fair description of this path. The
new `RUN_REVISION_MISMATCH` row cites `harness_guard.py:71-72`, which is exactly
the manifest-versus-binding comparison, and it is genuinely unfiltered by
`_resolve_harness_binding`. Both line ranges exact.

**4 (S3d event firing).** Accurate. Nothing in `runtime/` fires either event: the
only five `hooks.run(...)` sites in `runtime/` are `service.py:181, 197, 253,
300, 333`, carrying `RUN_STARTING`, `RUN_STARTED`, `BEFORE_SEND`,
`BEFORE_RESUME`, `SESSION_STOPPING`, and neither destructive event is among
them. The two acknowledged test sites are real and correctly cited
(`tests/test_harness_hooks.py:68`,
`tests/test_destructive_external_action_guard.py:132`). The parallel fix in S5
item 1 and in the Resume prompt is present and consistent.

**5 (S3c project scoping).** Accurate, and this was the important one. Verified
each link: `service.py:294` `_require_canonical_enforcement`, `service.py:300`
`hooks.run(BEFORE_RESUME, ...)`, `service.py:311` `return adapter.resume(binding)`
— guard strictly before adapter. `adapters/hcom.py:294-299` is exactly
`_binding_session` calling `_project_error` first, so the adapter's project check
really is downstream of the guard. `supervisor.py:170-171` is where `project_id`
is read off the task record (the assignment itself is on 171), and
`supervisor.py:199-207` covers both the `ExecutionBinding(project_id=project_id)`
at 200 and the `SessionRef(project_id=project_id)` at 207 — so all three
project_ids do come from one `task` record and neither
`_validate_binding_session` nor `_base_evidence` can fire. The conclusion —
enforcement is not scoped to `--harness-project-id`, out-of-project incidents are
fully subject to canonical denial, and this strengthens the S2c gate argument —
is correct as written. The pointer added to the Resume prompt is appropriate.

**6 (line cite).** `supervisor.py:459-465` is exactly the seven-line
"else: harness attempt failed for a non-canonical reason" comment block. Correct.

### Re-verification runs at 076d59d

Full suite re-run the same way (blocking, redirected to `/tmp/pr177-suite2.txt`,
not piped): `Ran 898 tests in 1259.659s`, `OK (skipped=6)`, exit code 0. Smoke
(`python3 -m runtime.smoke`) exit code 0 at this head as well. The pass-1
substantive verifications in the sections above were re-checked against
`076d59d` and none of them changed — the corrections are confined to the note's
prose and no cited source file moved.

## Pass 2 verdict (at 076d59d)

**CHANGES_REQUESTED**, narrowly, and only on the S1 parenthetical described
under Correction 1. Everything else in this PR is sound: the design conclusion,
the three priority claims, the five accepted corrections, the non-goals, and
both verification runs. The gate conclusion I was asked to rule on is unchanged
and I still agree with it — an explicit opt-in feature gate is required for
first production exposure, and correction 5 makes that case stronger than the
original note did. Once S1's grep justification is reverted or reworded to
something true, this is an approve with no further conditions.

---

## Final pass at e01bcf4

`e01bcf4` reverts the one passage pass 2 held on. It touches only
`work/notes/2026-08-26-hook-enforcement-composition-root-design.md`
(2 insertions, 6 deletions); the branch's full diff versus `origin/main` remains
that note plus this evidence file. No `runtime/`, `tests/`, or
`work/roadmaps/` path is touched at any point in the branch's history.

**Item 1 — S1 is clean.** Verified two ways rather than by reading the revert
message. First, `git diff 076d59d..e01bcf4` on the note contains exactly one
hunk, and it is the S1 hunk: the anchored `grep -v "^\./tests/"` is replaced by
the original `grep -v '/tests/'`, and the five-line parenthetical asserting that
the unanchored form "filters nothing here" is deleted rather than reworded. The
false claim is gone from the file. Second, `git diff 37fde1b..e01bcf4` on the
note produces **no hunk anywhere before line 107**, which means S1 is now
byte-identical to the originally-reviewed `37fde1b` text — there is no residue
of the bad correction.

The restored pipeline is the reproducible one. Re-confirmed through
`/usr/bin/grep` (GNU grep 3.11), deliberately bypassing this harness's `grep`
shell-function wrapper that caused my original error: the recursive grep emits
61 lines with a `./` prefix, and piping it through `/usr/bin/grep -v '/tests/'`
yields exactly the two lines S1 pastes — `./runtime/harness/service.py:27` and
`./runtime/policy/harness_guard.py:194`. The note's claim of "Two hits, 61
total" is correct, and the transcript is genuinely reproducible from the command
printed above it. Taking the revert rather than a reworded anchor was the right
call: with the premise false there was no distinction left to explain.

**Item 2 — corrections 2-6 are intact.** Established mechanically rather than by
re-reading prose: the diff from `076d59d` to `e01bcf4` on the note has that one
S1 hunk and nothing else, so no correction region was touched by the revert. As
a cross-check, the diff from `37fde1b` to `e01bcf4` on the note has exactly six
hunks, at the six correction sites and nowhere else — S2's deny-code counts
(@@ -107), the S2b revision rows (@@ -144), S3c's project-scoping rewrite
(@@ -292), S3d's event-firing wording (@@ -311), S5 item 1 (@@ -360), and the
Resume prompt (@@ -454). All six were verified against source during pass 2 and
none has moved since.

**Verification runs at e01bcf4.** Full suite, blocking, redirected to
`/tmp/pr177-suite3.txt`, not piped: `Ran 898 tests in 1284.598s`,
`OK (skipped=6)`, exit code 0. Smoke (`python3 -m runtime.smoke`) exit code 0.
Third consecutive green pair across the three reviewed heads.

## Final verdict

**APPROVED.** No conditions outstanding.

The design is sound and its three priority claims survive independent
re-derivation at source: the zero-caller finding (61 hits, exactly two outside
`tests/`), the `CanonicalRunGuard` fail-closed analysis (no `ALLOW` and no
`REQUIRE_APPROVAL` constructed anywhere in the file; every failure path denies,
the one success path annotates), and the traced RnS consequence chain through
`HOOK_DENIED` to `resume_denied` and on to `retry_budget_exhausted`. Non-goals
are respected mechanically — the branch never touches runtime, test, or roadmap
files, and no checklist row is flipped. Corrections 2-6 improved the note's
accuracy in five real places, S3c materially so.

On the question this review was asked to rule on: **a feature gate is required
for first production exposure.** Fail-closed in the authority sense — the guard
can only narrow, is registered `READ_ONLY` + `FAIL_CLOSED`, and grants nothing —
but strict in the availability sense, and on the RnS path a denial is terminal
for that pass with no fallback, burns an attempt, and drives the incident toward
`failed`. `LEASE_EXPIRED` is close to the expected case for the very population
RnS serves. Correction 5 strengthens this: enforcement is not scoped by
`--harness-project-id`, so out-of-project incidents are exposed too. Default-off
with an explicit operator opt-in is correct.

One process note worth carrying forward, since it cost a round trip: pass-1
Finding 1 was wrong because I trusted the `grep` on my `PATH` without checking
what it resolved to. In this harness `grep` is a shell function that rewrites
output, and a claim about grep's output is exactly the kind of claim that needs
`/usr/bin/grep`. The author was right to act on the finding as reported and
right to revert once it was withdrawn; the failure was mine and is recorded here
so the next reviewer of a grep-derived claim checks the tool before the claim.
