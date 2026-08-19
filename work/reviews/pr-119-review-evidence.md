reviewer: SENTINEL
head_sha: cf24f30f616e14c6406b1081525e90445b495420
rebase_note: original review was at code head c4f7537bfc200f6746aabe2391e8e5ba29761877; head_sha updated to merge commit cf24f30f616e14c6406b1081525e90445b495420 (merges origin/main to bring the branch up to date after PR #118 merged) because merge commits are never walked past by the review-evidence check. git diff 07995b0 cf24f30 --stat for every file this review covers (work/notes/2026-08-19-harness-production-wiring-gap.md, work/tasks/harness-production-wiring-gap-wave14.md) is empty -- byte-identical, independently confirmed.
base_sha: 697729c7081ef95a662a1957b3894198a1d0af9c (main)
independent: true
summary: APPROVE (CLEAN, docs-only). Second opinion: concur with Option B with two caveats (see below).

## Job 1 — standard PR verification

**Setup.** Reviewed in an isolated worktree (`/tmp/pr119-review-worktree`, created via
`git fetch origin pull/119/head:pr119-review && git worktree add`, removed at the end of
this review), never touching the shared checkout. `git rev-parse HEAD` in the worktree
confirmed `c4f7537bfc200f6746aabe2391e8e5ba29761877`, matching `gh pr view 119`'s
`headRefOid` exactly.

**1. Diff-stat is docs-only.** `git diff main...HEAD --stat` against `main` at
`697729c7081ef95a662a1957b3894198a1d0af9c` (merge-base confirmed identical to `main`'s
tip) shows exactly two files, both additions, zero deletions:

```
 .../2026-08-19-harness-production-wiring-gap.md    | 486 +++++++++++++++++++++
 work/tasks/harness-production-wiring-gap-wave14.md | 146 +++++++
 2 files changed, 632 insertions(+)
```

No `runtime/`, `tests/`, or `work/roadmaps/CAPABILITY_CHECKLIST.md` file appears. Matches
the PR description's claim exactly.

**2. Independently re-ran the core factual claim.** From the worktree root:

```
$ grep -rln "ExecutionBinding(" runtime/ --include=*.py
(no output, exit 1)
$ grep -rln "HarnessService(" runtime/ --include=*.py
(no output, exit 1)
```

Both commands return zero matches under `runtime/`, confirmed with explicit exit-code
checks (both `1`, i.e. grep found nothing). For contrast, the same greps against `tests/`
return 7 and 6 files respectively (`test_agentic_security_hook_context.py`,
`test_harness_types.py`, `test_harness_adapter_contract.py`, `test_harness_service.py`,
`test_agentic_security_baseline.py`, `test_recovery_supervisor.py`,
`test_harness_canonical_guard.py`, `test_harness_config_ref.py`). The note's root-cause
claim is accurate and reproduced independently, not just copy-checked from the PR body.

**3. RnS's direct-`HcomAdapter` claim, verified against the actual file.** Read
`runtime/recovery/supervisor.py` in full. `RecoverySupervisor.__init__` (line 36) takes
`hcom: HcomAdapter` — the raw communication-layer adapter from `runtime/communication/`,
not `HcomHarnessAdapter`. It is called directly in three places:

- `observe_silent_stops`, line 124: `self.hcom.list_sessions(include_stopped=True)`
- `tick`, line 182: `self.hcom.list_sessions(include_stopped=True)`
- `tick`, line 270: `self.hcom.resume(session_name, headless=True, go=True)`

Nowhere in the file is `runtime.harness` imported or `ExecutionBinding`/`HarnessService`
constructed. This matches the note's description in its "Recovery-and-supervision (RnS)"
section verbatim — the note is not overstating or misdescribing RnS's current wiring.

**4. `HcomHarnessAdapter.resume()`'s real current state.** Read
`runtime/harness/adapters/hcom.py` in full. `resume()` (lines 384–390):

```python
def resume(self, binding: ExecutionBinding) -> OperationResult:
    project_error = self._project_error(binding.project_id)
    if project_error is not None:
        return project_error
    return self._unsupported(
        "hcom resume mode is not normalized yet; no headless/terminal behavior is guessed."
    )
```

Confirmed: `resume()` is an explicit `_unsupported()` stub today, same as `start()`,
`heartbeat()`, and `collect()`. The note does **not** gloss over this — it states it
plainly in the "Recovery-and-supervision" section ("`HcomHarnessAdapter.resume()`... is
implemented as an explicit `_unsupported()` stub today"), repeats it as an explicit risk
item in Option B's own write-up ("This is blocked immediately on a prerequisite this
option must also do"), and lists "implement `HcomHarnessAdapter.resume()` for real" as
sub-step (1) of the "Recommended path" — i.e. it is scoped as real, first-class,
un-deferred work, not a footnote. Also confirmed `HarnessService.resume()`
(`runtime/harness/service.py` lines 281–311) does fire `HookEvent.BEFORE_RESUME` and, if
`self.hooks.has_enforcement(event, HookEnforcement.CANONICAL_RUN)` is true, gates on it —
and `runtime/policy/harness_guard.py` line 200 confirms `BEFORE_RESUME` is one of the
events actually registered under `CANONICAL_RUN` enforcement today. So the note's claim
that Option B "gives SEC3 a real, already-consequential call site" for an
already-built-and-tested guard is accurate, not aspirational.

**5. No code changed, so no test suite run — per instructions, this is stated explicitly
rather than run.** `git diff main...HEAD --stat` (step 1) is sufficient: zero `.py`/`.sql`
files changed, only two `.md` files added. There is nothing for a test suite to validate.

### Job 1 verdict

**APPROVE.** All of the note's load-bearing factual claims were independently
re-derived and hold: the root-cause grep evidence, RnS's direct-`HcomAdapter` call sites
(with exact line numbers), and — most importantly for this PR's own stated risk —
`HcomHarnessAdapter.resume()`'s current `_unsupported()` state, which the note discloses
rather than hides. The diff is exactly the two files claimed, docs-only, no
`CAPABILITY_CHECKLIST.md` or code touched.

## Second opinion on Option B recommendation

**Conclusion: (c) — concur with Option B, with two caveats for whoever scopes the
follow-up implementation task.**

**Does RnS's "long-lived/resumable" framing hold up given `resume()` is unbuilt?** Yes,
but the framing is slightly stronger in the note's prose than in RnS's actual mechanics.
The underlying hcom *session* is genuinely long-lived and resumable — that part of the
argument is sound and is a real structural difference from helpers (a helper's
"session" is the `subprocess.run()` call itself; it ceases to exist the instant the call
returns, so there is nothing later to resume). But RnS's own interaction with that
session is a series of independent, stateless poll-then-nudge calls (`list_sessions` on
every `tick()`, `resume()` fired again on backoff) — it does not hold an open handle or
maintain session state between ticks any more than a helper maintains state between
`.run()` calls. So the fit is real at the level of "the target concept (an addressable,
resumable session) exists and is exactly what `HarnessService`/`resume()` model," but
weaker at the level of "RnS's code shape already resembles a harness-driven lifecycle" —
it doesn't; it resembles polling. That distinction doesn't change which option is best
(Option A's helpers genuinely have no resumable concept at all, which is the sharper
disqualifier), but the note's phrasing risks reading as "RnS already looks like a
harness caller" when the more precise claim is "RnS is polling something that a harness
caller's primitives can correctly describe, if `resume()` is built to describe it."
Worth a one-line sharpening in the follow-up task's own framing, not a reason to change
direction.

**Blast radius: is RnS a riskier first target than helpers or Option D?** Yes, and the
note says so plainly ("a live-production-behavior-changing module in the retry/backoff/
recovery path — a subtle bug here has direct operational consequences"). I agree with
that risk assessment and with the note's conclusion that the payoff (first live traffic
for the already-built `CANONICAL_RUN`/`BEFORE_RESUME` guard, plus unblocking four of the
five checklist rows instead of one or two) outweighs it *if* the rollout is deliberately
staged — but the note's "Recommended path" doesn't specify a staging mechanism (e.g.
shadow-mode, a kill-switch, or running the new path alongside the old one before cutting
over) beyond "verify does not silently suppress recoveries that should succeed" as a
post-hoc check. For a module whose own docstring says "never mutate task truth" and
whose failure mode is silently-missed or duplicated recovery attempts, I'd want the
follow-up implementation task to specify *how* it will be verified safe before full
cutover (e.g. dry-run/log-only mode for the `CANONICAL_RUN` gate for a period, or a
feature flag), not just "verify it doesn't regress" as an acceptance criterion after the
fact. This is a caveat on execution, not a disagreement with the choice of Option B.

**Does migrating RnS require changing its own decision logic, or is it a pure transport
swap?** The note handles this adequately — it is not a gap. "Recommended path" sub-step
(3) explicitly separates "route the resume call through `HarnessService.resume()`" from
RnS's existing backoff/attempt/claim logic (untouched), while separately and honestly
flagging that activating `CANONICAL_RUN`/`BEFORE_RESUME` gating is itself "a real
behavior change" layered on top of the transport swap, not hidden inside it. That is the
right way to describe it: mostly a transport swap, plus one deliberately-flagged new
gate. I don't think this needs correction, only reinforcement in the caveat above about
staging that new gate's rollout.

**A real option the note may have under-weighted:** the note's Option D (narrow
validation-only call site) is scoped only against H4/E4. A structurally identical
narrower option exists for SEC3 specifically and isn't named: a small, dedicated
"canary" call site that constructs a real `ExecutionBinding` and calls
`HarnessService.resume()` (once built) from a location decoupled from RnS's actual
recovery decision path — e.g. a manual/CLI-triggered resume, or a non-blocking shadow
call made alongside RnS's existing direct `HcomAdapter.resume()` rather than replacing
it — purely to give `CANONICAL_RUN`/`BEFORE_RESUME` live traffic without putting the
guard in the critical path of automated recovery on day one. This wouldn't fully resolve
H5 (RnS would still call `HcomAdapter` directly for its real decisions), but it would de-
risk "first live traffic for the guard" from "first live traffic in a safety-critical
automated retry loop." The note doesn't consider this middle ground; I'd flag it as
worth a sentence in the follow-up task's design rather than a reason to prefer a
different top-level option.

**Bottom line:** Option B is the right target — its reasoning (RnS's session concept is
the correct fit, the payoff of exercising the already-built guard, and honest disclosure
of the `resume()` prerequisite) holds up under independent scrutiny, and it is
meaningfully better than A (forced fit, more surface area touched for a worse semantic
match) or C (disproportionate scope). I would not block this PR on the disagreement
below, since it is a note recording a recommendation, not an implementation, and the
note's own "Left to the follow-up implementation task" section already leaves room for
exactly this kind of refinement:

1. Sharpen "RnS already fits the session-lifecycle shape" to acknowledge it's the
   *target concept* that fits, not RnS's current polling code shape.
2. The follow-up implementation task should specify a staged/shadow rollout mechanism
   for activating `CANONICAL_RUN`/`BEFORE_RESUME` on RnS's resume path (not just a
   post-hoc "verify it doesn't regress" check), given RnS's own safety-critical,
   "never mutate task truth" framing — and should at least consider the narrower
   "canary" call site described above as a lower-risk way to give the guard live traffic
   before cutting RnS's automated recovery loop over to it.

## Verdict

APPROVE. Diff is docs-only (two `.md` files, zero `.py`/`.sql`), every factual and
technical claim in the note independently re-verified true (root-cause grep, RnS's exact
call sites, `resume()`'s real `_unsupported()` state honestly disclosed, `CANONICAL_RUN`/
`BEFORE_RESUME` guard registration confirmed real). No changes required to land this PR.
The Option B recommendation itself is technically sound and I concur with it, subject to
the two caveats above for the follow-up implementation task's scoping — recorded here for
whoever picks that task up next, not as a blocker on this PR.
