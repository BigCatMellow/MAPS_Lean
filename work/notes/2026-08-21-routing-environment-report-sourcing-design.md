# Routing environment-report sourcing design

Date: 2026-08-21
Owner: `/root`
Status: design complete; no runtime behavior changed

## Finding

Roadmap 6.24 is correctly still `IN PROGRESS`.

VERIFIED current state:

- `runtime/policy/evaluator.py::evaluate_assignment()` can reject a supplied
  `CompatibilityReport` only when its state is `INCOMPATIBLE`.
- `runtime/routing/router.py::recommend_route()` accepts an optional
  task-ID-keyed `environment_reports` mapping.
- `runtime/routing/service.py`, `runtime/routing/cli.py`, and
  `runtime/routing/langgraph_runtime.py` can forward or serialize those
  caller-supplied reports.
- Routing does not inspect an environment, select an `EnvironmentSpec`, compute
  a fingerprint, cache reports, or validate freshness.

That is the correct boundary today. The missing piece is not more rejection
logic; it is the evidence contract around which report is allowed to represent
which task.

## Decision: explicit task-contract association, not inferred defaults

The future implementation should source task-to-`EnvironmentSpec` association
from explicit task-contract evidence, not from a repository-wide default or
path heuristic.

Rationale:

- A single repo can contain tasks with different environment requirements.
- `runtime/environment/specs/maps-runtime-ci.json` is a real fixture for MAPS
  runtime CI, not proof that every task should route against it.
- Inferred defaults would turn absent evidence into false certainty.
- Explicit task-contract evidence is consistent with the existing MAPS rule
  that task authority comes from declared task inputs/sources/boundaries.

Recommended future field shape, for a later implementation task:

```text
environment:
  spec_ref: runtime/environment/specs/maps-runtime-ci.json
  report_ref: .maps/state/environment-reports/<task-id>.json
  max_age_seconds: 900
  required_for_routing: false
```

This note does not add that schema. It defines the intended contract so the
implementation task can do it without guessing.

## Freshness rules

A future routing report envelope should be considered fresh only if all of the
following are true:

1. The task explicitly names the `EnvironmentSpec` reference.
2. The report's `environment_spec_hash` matches the parsed spec's current
   `sha256`.
3. The report was produced at or after the task revision that routing is
   evaluating, or the task explicitly declares that older report evidence is
   acceptable.
4. The report age is within `max_age_seconds`.
5. The report was produced for the same project/repo root boundary as the task.
6. The envelope can be parsed without unknown critical fields or malformed
   timestamps.

If any freshness check fails, routing must treat the report as absent unless a
separate task explicitly decides to expose a non-blocking stale-report reason.
Stale evidence must not be converted into `INCOMPATIBLE`.

## Routing behavior preserved

The future implementation must preserve these existing rules:

- Missing report: preserve current routing behavior.
- `UNKNOWN`: do not reject on environment.
- `DRIFTED`: do not reject on environment.
- `COMPATIBLE` / `COMPATIBLE_WITH_WARNINGS`: do not reject.
- `INCOMPATIBLE`: route to `policy_gate/environment_incompatible`.

If a task later sets `required_for_routing: true`, absence of a fresh report
may become its own policy gate, but that is a separate behavior change and must
be reviewed independently. This design does not authorize making missing
reports blocking by default.

## Bounded follow-up implementation

Recommended next task: `Routing environment-report evidence envelope`.

Allowed implementation scope:

- Add a small parser/value object for caller-supplied routing environment
  evidence envelopes.
- Validate:
  - task ID;
  - `spec_ref`;
  - `environment_spec_hash`;
  - produced-at timestamp;
  - `max_age_seconds`;
  - embedded `CompatibilityReport`.
- Add a pure helper that returns either:
  - a fresh task-ID-keyed `CompatibilityReport` mapping for the router; or
  - a non-blocking stale/malformed/absent reason.
- Wire only the CLI/read boundary if the source is already an explicit JSON
  file supplied by the operator/caller.
- Keep the router pure: it should consume reports, not inspect environments.
- Add tests proving fresh incompatible reports still gate, stale reports are
  ignored, malformed reports fail closed, and missing reports preserve current
  routing behavior.

Must not do in that follow-up:

- Add a background inspector or daemon.
- Compute live fingerprints inside the router.
- Make missing reports blocking by default.
- Introduce schema migration or durable cache.
- Pick a universal default `EnvironmentSpec`.

## Roadmap impact

This design does not complete 6.24. It removes the main ambiguity blocking the
next implementation step: the source of task-to-`EnvironmentSpec` association
must be explicit task evidence, and freshness belongs in a caller-supplied
envelope before the pure router sees a `CompatibilityReport`.
