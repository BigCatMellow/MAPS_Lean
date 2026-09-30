# Decision providers

This package is a narrow semantic-judgment seam between deterministic MAPS_L
eligibility and worker execution.

## Authority boundary

Decision providers may rank or score choices that MAPS_L has already determined
are eligible. They MUST NOT grant or widen task authority, bypass policy or
environment gates, add an ineligible worker, mutate canonical task state,
replace required verification or independent review, or treat confidence as
proof.

The default decision mode is off.

## Modes

- off: existing deterministic cheapest-competent behavior only.
- shadow: query a provider and return its recommendation as evidence while
  preserving the deterministic selection.
- active: permit a valid provider recommendation to choose among already
  eligible workers. Invalid/error responses fall back deterministically.

Production activation should follow shadow evaluation against MAPS_L outcomes.

## Jev

runtime.decision.jev.JevDecisionProvider is an optional TypeSafe Jev adapter.
It lazy-loads the SDK so the core runtime has no Jev dependency.

Install the optional dependency with:

    python -m pip install -r runtime/requirements-jev.txt

Set TYPESAFE_API_KEY outside the repository. Do not commit credentials.

Jev is a provider, not a MAPS authority source. A future local or open decision
model should implement the same DecisionProvider interface instead of adding
provider-specific branching to the router.
