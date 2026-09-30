# Decision broker

MAPS_L uses this package for **bounded semantic judgments** that sit between
deterministic control and open-ended reasoning.

The caller does not decide ad hoc whether to use Jev. Once a decision provider
is enabled, MAPS runtime decision points invoke the broker automatically when
there are multiple already-eligible semantic choices.

## Current automatic decision points

Each routing cycle can use the broker for:

1. **next task selection** among already-routable implementation tasks;
2. **review task selection** among already-routable reviews;
3. **worker selection** among workers already allowed by MAPS policy; and
4. **reviewer selection** among already-independent eligible reviewers.

Review work retains deterministic priority over implementation work. Jev cannot
change that policy.

Other possible judgment classes (failure classification, context relevance,
evidence preflight) should be added only at a clear runtime seam with its own
evaluation/privacy boundary. Do not send arbitrary repository/file content to an
external provider merely because the broker exists.

## Authority boundary

Decision providers may rank choices that MAPS_L has already determined are
eligible. They MUST NOT:

- grant or widen task authority;
- bypass policy, environment, dependency, halt, or reauthorization gates;
- introduce a task/worker not supplied by deterministic code;
- mutate canonical task state;
- replace verification or independent review; or
- treat probability/confidence as proof.

Evidence and canonical state outrank provider judgment.

## Modes

- `off` — deterministic behavior only; no provider call.
- `shadow` — provider is called automatically, but deterministic choices remain
  active. Provider recommendations are returned as decision evidence.
- `active` — a provider recommendation may select among already-eligible
  choices when confidence meets the configured threshold. Errors, invalid
  responses, and low-confidence answers fall back deterministically.

The broker caches identical judgments in-process so repeated identical state does
not spend another provider call.

## Automatic configuration

Provider use is explicit because external calls may transmit bounded task
metadata and may cost money. Configure MAPS_L once; individual agents do not
need to remember to call Jev.

    MAPS_DECISION_PROVIDER=jev
    MAPS_DECISION_MODE=shadow
    MAPS_DECISION_MODEL=jev-latest
    MAPS_DECISION_MIN_CONFIDENCE=0.80
    TYPESAFE_API_KEY=...

When `MAPS_DECISION_PROVIDER=jev` is set and mode is omitted, MAPS_L defaults
to `shadow`. Move to `active` only after shadow results are acceptable.

Only bounded task metadata used for routing is sent by the current broker:
task identity/type/risk/objective/acceptance/output-path metadata and eligible
worker profiles. Repository file bodies are not sent by this integration.

## Jev adapter

`runtime.decision.jev.JevDecisionProvider` lazy-loads the official Python SDK,
so the core runtime remains provider-neutral.

Install:

    python -m pip install -r runtime/requirements-jev.txt

Set `TYPESAFE_API_KEY` outside the repository. Do not commit credentials.

A future local/open decision model should implement the same
`DecisionProvider` interface; routing code should not branch on provider names.
