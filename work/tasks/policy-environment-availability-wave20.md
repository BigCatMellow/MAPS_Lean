# Task: `evaluate_assignment` gains environment-availability as an intersected dimension (wave20)

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `agent/policy-environment-availability-wave20`
- Risk: `LOW`
- Goal: close part of roadmap `6.24` ("Least-privilege capability intersection" —
  `work/roadmaps/00-MASTER-MAPS-CAPABILITY-ROADMAP.md`, "usable authority =
  worker capability ∩ task scope ∩ policy ∩ operator approval ∩ environment
  availability"). `runtime/policy/evaluator.py::evaluate_assignment` already
  intersects worker capability, task scope/risk, and policy/operator approval.
  Environment availability was the one dimension the function had no way to
  consult at all. This task gives it that capability, additively.

## Why this task exists, and why it is deliberately narrow

`runtime/environment/fingerprint.py::evaluate_environment_compatibility`
already produces a `CompatibilityReport` describing whether an observed
execution environment satisfies an `EnvironmentSpec` — `COMPATIBLE`,
`COMPATIBLE_WITH_WARNINGS`, `DRIFTED`, `INCOMPATIBLE`, or `UNKNOWN`. Nothing in
`runtime/policy/` could consume that evidence before this task; the
least-privilege intersection the roadmap describes was missing its fifth
term entirely.

This task adds only the capability: an optional `environment_report` keyword
parameter on `evaluate_assignment`, defaulting to `None`. It does **not** wire
a real environment report into the one production caller
(`runtime/routing/router.py::recommend_route`). That caller has no existing
mechanism to determine which `EnvironmentSpec` a given task requires or to
source/cache a fresh `CompatibilityReport` for it — deciding that is a
separate design question (where does the spec come from per task? is the
report computed per routing pass, cached, or streamed from a background
inspector?) explicitly out of scope here. Leaving the parameter unused by the
router keeps this task's blast radius to "policy can now express this rule
when given the evidence," not "routing enforces it."

## Change boundary

MAY CHANGE / ADD:
- `runtime/policy/evaluator.py`:
  - `evaluate_assignment(task, worker, *, environment_report: CompatibilityReport | None = None)`
    — new keyword-only parameter, default `None`.
  - When `environment_report is not None` and
    `environment_report.state == CompatibilityState.INCOMPATIBLE`, adds
    `"environment_incompatible"` to the same `reasons` list the function's
    other checks already append to, so it flows through the existing
    `require_approval` / `reject` / `allow` decision logic unchanged.
  - `DRIFTED` and `UNKNOWN` states are deliberately **not** treated as
    rejection grounds — see "Design decision" below.
  - Docstring updated to describe the new parameter and its role in the
    intersection. No other restructuring of the function.
- `tests/test_routing_policy.py`: new test cases (see "Tests" below) plus a
  small `compatibility_report(state)` helper to construct a minimal
  `CompatibilityReport` directly (it's a plain frozen dataclass — no real
  environment inspection needed).
- `work/roadmaps/CAPABILITY_CHECKLIST.md`: `6.24` row evidence text updated
  to reflect that the environment-availability parameter now exists, while
  keeping the row `IN PROGRESS` (see "CAPABILITY_CHECKLIST.md" below).
- this task doc.

MUST NOT CHANGE:
- `runtime/routing/router.py` — the one real production caller of
  `evaluate_assignment`. It is not modified to pass `environment_report`;
  wiring a real environment-evidence source into routing is a distinct,
  larger follow-up task (deciding per-task `EnvironmentSpec` sourcing and
  report freshness/caching).
- `runtime/environment/fingerprint.py` — read-only dependency. Not touched.
- Default-`None` behavior of `evaluate_assignment` for any existing caller:
  byte-identical to before this task. Verified by keeping all pre-existing
  `tests/test_routing_policy.py` tests unmodified and green.
- `evaluate_review` and the rest of `runtime/policy/evaluator.py` — untouched
  apart from the one new parameter and its guard clause on
  `evaluate_assignment`.

## Design decision: why only `INCOMPATIBLE` blocks

`CompatibilityState` has five values. Only `INCOMPATIBLE` is a *proven*
mismatch between what the task's environment spec requires and what was
observed (e.g. a required runtime is missing, a required secret capability is
unavailable, a required network domain is unreachable — see
`evaluate_environment_compatibility`'s `incompatible` accumulation in
`runtime/environment/fingerprint.py`). `DRIFTED` and `UNKNOWN` mean
"something could not be confirmed compatible" — a spec-hash mismatch, an
unobserved runtime version, a network mode that was never checked — which is
categorically different from "confirmed incompatible." Rejecting on
`DRIFTED`/`UNKNOWN` would turn every gap in environment-evidence collection
into a false-positive assignment block, which is worse than the status quo of
not consulting environment evidence at all. `COMPATIBLE` and
`COMPATIBLE_WITH_WARNINGS` are, by `CompatibilityReport.compatible`'s own
definition, passing states and are not rejection grounds either.

## Tests

`tests/test_routing_policy.py`:
- `test_no_environment_report_is_unchanged_behavior` — no `environment_report`
  passed: `evaluate_assignment` allows a task exactly as before this task.
- `test_incompatible_environment_report_rejects` — `INCOMPATIBLE` report:
  decision is not `allowed`, `environment_incompatible` is in `reasons`.
- `test_drifted_environment_report_does_not_reject_on_environment` — `DRIFTED`
  report: `environment_incompatible` is absent, decision still `allowed`
  (task/worker otherwise clean).
- `test_unknown_environment_report_does_not_reject_on_environment` — same for
  `UNKNOWN`.
- `test_compatible_environment_report_does_not_reject` — `COMPATIBLE` and
  `COMPATIBLE_WITH_WARNINGS` both leave `environment_incompatible` absent and
  the decision `allowed`.

All pre-existing tests in this file are unmodified and pass, demonstrating
the default-`None` path is unaffected.

## Verification

```text
python3 -m unittest discover -s tests -v
```

Run clean in an isolated worktree (`/tmp/policy-env-wave20`, branched from
`origin/main`), per `playbook/WORKTREE_ISOLATION.md`.

Review required: `INDEPENDENT_REVIEW`. Self-authored; owner is not eligible to
supply that review.

## CAPABILITY_CHECKLIST.md

`6.24`'s row stays `IN PROGRESS`. The evidence text now credits
`evaluate_assignment` with an environment-availability dimension it did not
have before, while being explicit that `runtime/routing/router.py` — the only
real production caller — does not source or pass an `environment_report`
yet, so no live routing decision is actually gated by environment evidence as
a result of this task. The roadmap's scope dimension (beyond canonical run
identity) also remains unproven; this task does not touch it.

## Stop / escalate — explicitly deferred, not decided here

This task does not decide how `runtime/routing/router.py` should source a
per-task `EnvironmentSpec` or a fresh `CompatibilityReport`, nor whether
compatibility should be computed per routing pass, cached with a TTL, or
streamed from a background environment inspector. That is a distinct,
larger follow-up: wiring real environment evidence into the one production
routing path. This task's job was making the policy layer able to express
and enforce the rule once given that evidence — proven by tests using
directly-constructed `CompatibilityReport` fixtures, not a live inspector.
