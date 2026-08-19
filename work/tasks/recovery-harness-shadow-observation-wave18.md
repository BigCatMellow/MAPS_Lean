# Task: Recovery supervisor harness-resume shadow observation (Option B, shadow-only)

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `agent/recovery-harness-shadow-observation-wave18`
- Risk: `MEDIUM`
- Goal: add a purely observational, parallel `HarnessService.resume()` call
  inside `RecoverySupervisor.tick()`, alongside (never instead of) the real
  `HcomAdapter.resume()` call it already makes. This is the "explicit
  dry-run/shadow-mode... step" flagged as missing in
  `work/reviews/pr-119-review-evidence.md`'s "Second opinion on Option B
  recommendation" section, before RnS's automated retry loop is ever allowed
  to depend on the harness path.

## Why this task exists, and why it is deliberately narrow

`work/notes/2026-08-19-harness-production-wiring-gap.md` documents that the
Harness layer (`HarnessService`, `HcomHarnessAdapter`, `CanonicalRunGuard`)
has zero production callers anywhere, and recommends "Option B" — migrating
`RecoverySupervisor`'s hcom resume path through the harness — as the best
first production wiring target. `work/reviews/pr-119-review-evidence.md`'s
second-opinion review concurs with Option B but flags two caveats: (1) a
straight swap risks turning "the harness path is available" into "RnS's
safety-critical automated retry loop now silently depends on it," and (2) no
staged rollout mechanism (shadow-mode, feature flag, or canary call site) was
specified before cutover.

Independently verified before writing any code: `CanonicalRunGuard._base_evidence()`
(`runtime/policy/harness_guard.py`) fails closed with `RUN_NOT_FOUND` unless
`self.source.get_run_manifest(run_id)` returns a real manifest, and per
`runtime/README.md`'s "AGI and run integrity" section, run manifests are
**optional** — created only "for high-risk, resumable, or drift-sensitive
execution." Most ordinary ACTIVE tasks with a live hcom session have no run
manifest at all. A straight swap of RnS's real resume call to go through
`HarnessService.resume()` would therefore fail closed for most real resume
attempts today — a serious regression to recovery, not a safe migration.

This task does not attempt that swap. It adds **only** a parallel,
best-effort, purely observational harness-path resume attempt, modeled
directly on this file's own existing precedent —
`RecoverySupervisor._advisory_environment_evidence()` — which the docstring
already documents as "purely advisory context, never consulted by any branch
in `tick()` to make or change a recovery decision." The new method,
`_advisory_harness_resume_shadow()`, follows the identical shape: optional
constructor dependency (`harness_service: Any | None = None`), `None`
early-return when unconfigured, `try/except Exception: return None`-style
failure containment (here, a structured `{"attempted": False, "reason": ...}`
rather than bare `None`, since "why nothing was attempted" is itself the
evidence this task exists to collect), and threading the result into every
action dict `tick()` already builds as one more purely additive key.

## Change boundary

MAY CHANGE / ADD:
- `runtime/recovery/supervisor.py`:
  - `RecoverySupervisor.__init__` gains `harness_service: Any | None = None`
    (mirrors the existing `environment_reader: Any | None = None` parameter
    exactly, including its advisory-only docstring comment style).
  - New private method `_advisory_harness_resume_shadow(incident, session_name)`.
  - `tick()` calls the new method once per due incident, alongside (same
    line, same style comment as) the existing
    `_advisory_environment_evidence(...)` call, and threads its result into
    every `actions.append({...})` call site (`suppress` x2, `resolve`,
    `fail`, `resume`/`resume_failed`) as a new `"harness_resume_shadow"` key.
  - Import `ExecutionBinding`, `SessionRef` from `runtime.harness` (no
    circular-import risk: `runtime/harness/__init__.py` has no dependency on
    `runtime.recovery`, confirmed by reading every `runtime/harness/*.py`
    import block before adding this).
- `tests/test_recovery_supervisor.py`: new `RecoveryHarnessResumeShadowTests`
  class + `FakeHarnessServiceResume` fixture; additive `OperationResult`
  import.
- `work/roadmaps/CAPABILITY_CHECKLIST.md`: one narrow, additive sentence on
  the H5 row noting this shadow capability now exists in
  `runtime/recovery/supervisor.py`, **without** changing H5's status level or
  claiming the "remaining adapters" half of its exit gate is any more done —
  see "CAPABILITY_CHECKLIST.md" section below for the exact reasoning.
- this task doc.

MUST NOT CHANGE:
- Anything about what `tick()` actually does to resume a session: the real
  `self.hcom.resume(session_name, headless=True, go=True)` call, its
  `try/except HcomError` handling, `incident["state"]`/`attempt`/
  `next_attempt_at` transitions, and the real `action`/`error` values
  recorded are all byte-for-byte unchanged. Verified both by code reading
  (the shadow call is computed once, before any branch, from data available
  at loop-iteration start, and its result is never read by any `if`/`elif`
  in `tick()`) and empirically by test (c) below.
- `runtime/harness/service.py`, `runtime/harness/adapters/hcom.py`,
  `runtime/policy/harness_guard.py` — read-only inputs to this task; the
  shadow call uses `HarnessService.resume()` and `HcomHarnessAdapter.resume()`
  exactly as they exist today (both now implemented for real, per PR #123 —
  `HcomHarnessAdapter.resume()` is no longer the `_unsupported()` stub the
  2026-08-19 note originally found).
- No run-manifest requirement is added to the real recovery path. The
  shadow call independently discovers whether a run manifest / durable
  session lineage exists for an incident's bound `run_id`, and if not,
  reports `{"attempted": False, "reason": ...}` rather than forcing (or
  needing) one to exist.

## What the shadow method does

`_advisory_harness_resume_shadow(incident, session_name)`:
1. Returns `None` immediately if `self.harness_service` is not configured
   (mirrors `_advisory_environment_evidence`'s early-return shape exactly).
2. Returns `{"attempted": False, "reason": "no_run_id_bound"}` if the
   incident has no bound `run_id` — the common case today, since most tasks
   have no run manifest. Being honest about what could not even be tried is
   explicitly preferred over attempting (and inevitably failing) a doomed
   call.
3. Otherwise, attempts to gather the same evidence
   `HcomHarnessAdapter.attach()`/`CanonicalRunGuard` would themselves need:
   the task's `project_id` and current `compute_task_revision(task_id)`, and
   the run's durable session lineage via `task_reader.resolve_run_session(run_id)`
   (the same forward lookup `HcomHarnessAdapter._record_attach()` uses). If
   any of these is unavailable, returns a structured
   `{"attempted": False, "reason": "<specific reason>"}` rather than
   guessing.
4. If a durably-bound `hcom` session_id is found, constructs a real
   `ExecutionBinding`/`SessionRef` and calls
   `self.harness_service.resume(binding, session_ref)`, returning
   `{"attempted": True, "ok": ..., "code": ..., "summary": ...}` describing
   what the shadow attempt observed — this is the evidence a later
   trajectory check needs to decide whether Option B's full migration is
   viable (e.g. "what fraction of real incidents have durable lineage today,
   and does the canonical-run guard pass or fail for them").
5. The entire attempt is wrapped in `try/except Exception: return
   {"attempted": False, "reason": "shadow_lookup_error"}` — matching this
   file's existing `# noqa: BLE001 - advisory lookup must never break
   recovery` precedent and reasoning exactly: an advisory lookup must never
   break the real recovery decision it sits alongside, no matter what goes
   wrong inside it.

## Tests

`tests/test_recovery_supervisor.py`, new `RecoveryHarnessResumeShadowTests`
(uses a real `TaskStore` so `resolve_run_session` is actually exercised, not
faked):

- (a) `test_no_harness_service_configured_leaves_shadow_key_none` — not
  configured: `tick()` behaves identically to before this task,
  `harness_resume_shadow` is `None` in the action.
- (b) `test_no_run_id_bound_reports_not_attempted_real_resume_unaffected` —
  configured but no `run_id` bound: records
  `{"attempted": False, "reason": "no_run_id_bound"}`; real `self.hcom.resume`
  still fires exactly once.
- (c) `test_harness_path_raises_but_real_resume_completes_identically` — **the
  safety proof**. Runs the identical scenario (bound `run_id`, durable
  `hcom` session lineage attached via `HcomHarnessAdapter.attach()`) twice:
  once with no `harness_service`, once with a `harness_service` whose
  `resume()` raises. Confirms the shadow path was actually invoked and did
  raise (`len(failing_harness.calls) == 1`), then confirms the real
  `hcom.resume` calls, the resulting `action`/`error` values (aside from the
  `harness_resume_shadow` key and the per-run random `incident_id`), and the
  persisted incident state are byte-for-byte identical between the two runs
  — proving the "never gates a decision" property empirically, not just by
  code reading. Mirrors the existing
  `test_incompatible_evidence_never_changes_the_recovery_decision` pattern
  for `_advisory_environment_evidence`.
- A fourth test, `test_harness_resume_shadow_observes_success_without_affecting_real_path`,
  covers the successful-shadow-call case as additional, purely additive
  evidence.

## Verification

```text
python3 -m unittest tests.test_recovery_supervisor -v
python3 -m unittest discover -s tests -v
```

Both run clean in an isolated worktree (`/tmp/recovery-shadow-worktree`,
branched from `origin/main`).

Review required: `INDEPENDENT_REVIEW`. Self-authored; owner is not eligible
to supply that review (`work/reviews/pr-<N>-review-evidence.md` required
before merge per `scripts/check_review_evidence.py`).

## CAPABILITY_CHECKLIST.md

Per this task's explicit instructions: this task does **not** claim H5, SEC3,
L6, or L7 are any more `DONE` than before. It is shadow instrumentation only,
not the Option B migration itself — RnS's real recovery decision path is
byte-for-byte unchanged (see "Tests" (c) above for the empirical proof). The
H5 row's evidence text gets one narrow, additive sentence noting the shadow
capability now exists in `runtime/recovery/supervisor.py`, since H5's prior
text explicitly named `runtime/recovery/supervisor.py` as "remain[ing]
unwrapped" — that specific factual claim needed a footnote once this task
landed a (shadow-only) harness call inside it, even though the substantive
"remaining adapters" gap H5 tracks (helpers, and RnS's *real* decision path)
is unchanged. `SEC3`, `L6`, and `L7` rows are untouched: this task's shadow
call does exercise `CANONICAL_RUN`/`BEFORE_RESUME` if a `harness_service`
with those Hooks registered is ever wired in by a caller, but no such caller
exists yet in production (no code anywhere constructs a `RecoverySupervisor`
with `harness_service=` set) — so SEC3's "zero registered guards for
BEFORE_EXTERNAL_ACTION/BEFORE_DESTRUCTIVE_ACTION" and "no live call site"
findings, and L6/L7's "hash not yet persisted on real runs" findings, remain
exactly as accurate as before this task.

## Stop / escalate — explicitly deferred, not decided here

This task does **not** decide whether Option B's full migration (making the
harness path authoritative for RnS's real resume decision, and requiring
`CANONICAL_RUN`/`BEFORE_RESUME` enforcement to pass before a real resume
proceeds) is ever pursued. That decision is deferred until real
shadow-observation data accumulates from production incidents — i.e., until
enough `harness_resume_shadow` evidence exists across real `tick()` calls to
answer questions like "what fraction of real silent-stop incidents have a
run manifest and durable session lineage at all" and "when the guard is
exercised, does it pass or fail, and why." This mirrors the precedent already
set by `work/notes/2026-08-17-recovery-equivalence-authority-design.md`'s
"Option A only, for now" decision for environment-compatibility evidence:
build the advisory observation first, defer the authority question until
there is real evidence to reason from.

Also note: as of this task, no production code constructs a
`RecoverySupervisor` with `harness_service=` set — the constructor parameter
exists and is tested, but nothing wires a real `HarnessService` instance into
it yet. Actually observing shadow data in production requires a follow-up
task to construct and pass a real `HarnessService` (with a `HcomHarnessAdapter`
registered) into whatever assembles `RecoverySupervisor` today. That wiring
was intentionally left out of this task's scope — this task's job was the
shadow *mechanism* inside `tick()`, proven safe; wiring a real
`HarnessService` into the real supervisor construction path is a distinct,
smaller follow-up that does not touch `tick()`'s decision logic at all.
