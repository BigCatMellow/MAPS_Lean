# RnS harness validation call-site design

Date: 2026-08-21
Owner: `/root`
Status: design complete; no runtime behavior changed

## Finding

H4/E4/6.5 still lack a production validation call site.

VERIFIED current state:

- `runtime/environment/validation.py` can run `EnvironmentSpec.validation`
  tiers and can build a hook callback with `make_validation_hook()`.
- `work/roadmaps/CAPABILITY_CHECKLIST.md` still marks H4, E4, and 6.5
  `IN PROGRESS` because the executor exists but no production caller invokes
  it.
- `work/notes/2026-08-19-harness-production-wiring-gap.md` already identifies
  the shared root cause: `HarnessService` and `ExecutionBinding` exist, but no
  production runtime path constructs and uses them.
- `runtime/recovery/supervisor.py` remains the closest existing
  session-lifecycle-shaped caller, but it still calls the communication-layer
  hcom adapter directly rather than `HarnessService.resume()`.
- `runtime/harness/adapters/hcom.py::HcomHarnessAdapter.resume()` is already
  implemented. It preserves the current hcom resume intent by calling
  `backend.resume(..., headless=True, go=True)` and maps results to
  `SESSION_RESUMED`, `INVALID_ARGUMENT`, or provider-failure outcomes.

Do not treat validation-tier wiring as a standalone shortcut. The prior
production-wiring note recommends RnS harness migration as the first real call
site because RnS already deals with resumable hcom sessions. This design keeps
that sequencing.

## Decision: base RnS harness resume call site first

The next implementation task should not wire validation tiers yet. It should
first make RnS resume go through the already-implemented harness resume
boundary.

Recommended implementation boundary:

1. Reuse the existing `HcomHarnessAdapter.resume()` semantics; do not
   re-normalize or re-implement adapter result codes in the RnS wiring task.
2. Construct an `ExecutionBinding` inside `RecoverySupervisor.tick()` only when
   the supervisor can resolve the incident/session/run relationship it already
   uses for advisory environment evidence.
3. Route the resume attempt through `HarnessService.resume(binding,
   session_ref)` instead of direct hcom resume.
4. Preserve the existing RnS safety contract:
   - no task-truth mutation;
   - no new recovery trigger loop;
   - no daemon/cron/always-on process;
   - no automatic environment inspection;
   - no validation-tier command execution.
5. Explicitly test that activating `BEFORE_RESUME` / `CANONICAL_RUN` does not
   silently suppress a resume that the current direct path would have attempted
   unless the canonical-run guard has a concrete mismatch.

This task is the first behavior-changing production call-site task. It should
be separate from validation-tier hook-in so failures can be attributed to either
base harness routing or validation policy, not both.

## Validation-tier fast-follow

After base RnS harness resume wiring lands, a separate H4/E4/6.5 task may attach
validation tiers to that call site.

Recommended validation placement:

- Use the already-declared `EnvironmentSpec.validation.quick` tier as the first
  candidate.
- Register the validation hook at a resume-adjacent harness event only after
  the base call site has a real `ExecutionBinding`, `SessionRef`, and
  `HarnessService`.
- Source the `EnvironmentSpec` from explicit task/run evidence, not from a
  universal default. If no spec is bound, validation must be skipped or reported
  as missing according to the task's acceptance criteria, not guessed.
- Preserve existing compatibility semantics: missing validation evidence should
  not imply environment incompatibility unless a later policy task explicitly
  makes it mandatory.

Non-goals for the validation fast-follow:

- no report cache;
- no default `EnvironmentSpec`;
- no external project pilot;
- no always-on validation daemon;
- no mandatory validation gate by default.

## Behavior questions the implementation task must answer

Do not guess these inside a broad implementation:

- What should RnS record when `HarnessService.resume()` denies because of
  `CANONICAL_RUN`? The result must be observable without mutating task truth.
- Should missing run binding skip the harness path and preserve the current
  direct behavior, or fail closed for that incident? That is a behavior-change
  decision and should be explicit in the implementation task.
- Which exact existing RnS session/run lookup should construct
  `ExecutionBinding` and `SessionRef`, and how should ambiguous/missing lineage
  be surfaced?
- Where should the eventual validation result be persisted or surfaced:
  recovery action evidence, Run Record coverage, or both?

## Bounded follow-up implementation

Recommended next task: `RnS harness resume production call site`.

Allowed implementation scope:

- Reuse the already-implemented `HcomHarnessAdapter.resume()` behavior for
  RnS's current direct resume call.
- Construct the required `ExecutionBinding` and `SessionRef` from existing RnS
  incident/session/run evidence.
- Route RnS resume through `HarnessService.resume()`.
- Preserve direct-path behavior except for explicit canonical-run denial.
- Add tests for:
  - successful resume path still reaches hcom with `headless=True, go=True`
    through the existing harness adapter;
  - canonical-run mismatch denies and is surfaced as recovery evidence;
  - missing/ambiguous binding follows the implementation task's explicit
    chosen behavior;
  - no validation-tier commands run in the base task;
  - no task-state mutation occurs;
  - existing advisory environment evidence behavior is unchanged.

Must not do in that follow-up:

- run validation tiers;
- add production report caches;
- add daemon/cron/always-on recovery invocation;
- wrap helpers as harness adapters;
- create a new worker-loop/orchestrator entrypoint.

## Roadmap impact

This design does not complete H4, E4, or 6.5. It identifies the prerequisite
production call site and keeps validation-tier wiring as a bounded fast-follow
after base RnS harness resume wiring exists.
