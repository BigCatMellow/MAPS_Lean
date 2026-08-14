# KICK-01 Discovery Contribution — Zero

- scenario: `KICK-01`
- role: discovery / contradiction
- scope: frozen-frame evidence only; no implementation or policy proposal
- context beyond shared packet: none

## Findings

### D-01 — “latest durable action” overstates what the stated source can prove

- classification: **essential**
- observation: The purpose calls the field “latest durable action”
  (scenario lines 22-25), while the evidence packet calls MAP events
  *historical action evidence* (lines 55-58). A historical event neither proves
  current liveness nor establishes that the event remains the agent's present
  work.
- implication: The later card could make an old event look like current agent
  activity, recreating the status conflation that the success condition forbids
  (lines 29-33).
- smallest testable response: Name the field **“latest recorded MAP action”**;
  display its event timestamp and source, and state “historical; not live
  presence or an active claim.” Add one assertion in the action-newer-than-
  durable fixture: a newer recorded action must not overwrite durable status or
  imply a live session.

### D-02 — hcom's degraded-read behavior is not named in the frozen contract

- classification: **essential**
- observation: The frame says hcom is the live-presence authority (lines
  55-58) and requires freshness/unknown treatment (lines 39-42), but does not
  say what the card renders when live hcom is unavailable, stale, or supplied
  by a fallback rather than a process-bound read.
- implication: A fallback result could be labelled “live” without the operator
  knowing its authority is degraded. That would contradict the required
  separately rendered facts (lines 72-75), even if no synthetic status is
  created.
- smallest testable response: Require a `presence_source`/`presence_freshness`
  label with three display states: process-bound live, degraded fallback, and
  unavailable/unknown. A deterministic unavailable/fallback subcase may be
  attached to an existing mixed-state fixture; it need not create another
  state store or a fourth main fixture.

### D-03 — the membership rule for “visible helper” is underspecified

- classification: **likely**
- observation: The purpose names “live core agent or visible helper” (line 22)
  and scope says “currently running helpers” (lines 37-38), but the frozen
  frame does not define the source predicate that distinguishes a helper from a
  capability identity, historical session, or UI shortcut.
- implication: A later implementation could quietly broaden the card's scope
  through name heuristics, increasing noise and defeating the bounded
  operator-question requirement.
- response: The later brief should name an existing, read-only inclusion
  predicate and test one included core agent, one included running helper, and
  one excluded non-session identity. Do not promote a naming convention or a
  new identity registry in this scenario.

### D-04 — “actionable exception” needs a non-escalation rule

- classification: **likely**
- observation: The card promises an actionable exception (lines 22-25), while
  the scenario excludes policy/authority decisions (lines 45-51, 72-76). The
  frame does not distinguish “operator must decide” from “a factual condition
  requiring the claim owner or reviewer to act.”
- implication: A warning card could create false operator work or look like a
  directive without an authority basis.
- response: Label each exception as a factual reason plus its source; reserve
  “operator decision needed” for an existing request or approval-gate source.
  Other reasons remain coordination facts. This is a display-boundary rule,
  not a new escalation policy.

### D-05 — visual controls are not a kickoff requirement

- classification: **reject**
- observation: The frozen scope requests a read-only card and acceptance
  evidence (lines 35-43), while non-goals exclude styling changes (lines
  45-49). No evidence requires terminal controls, hover details, visual role
  taxonomy, or a historical-agent view.
- implication: Treating these as requirements would make the smallest
  reversible boundary slower and over-scoped.
- response: Keep them out of the later brief; reconsider only after the card
  can answer the stated coordination question with its four labelled fields.

## Supported convergence

- The frozen frame correctly retains source separation, existing sources only,
  three staged fixtures, and no new state store or policy decision (lines
  27-51, 68-76). I found no supported reason to expand those boundaries.
- The immediate operator question should remain limited to separately shown
  durable state, live presence, claim, recorded action, and factual exception;
  it must not become a general agent-management dashboard.

## Frame impact and measurement note

- required frozen-frame refinements: **2** (`D-01`, `D-02`)
- likely later-brief clarifications: **2** (`D-03`, `D-04`)
- rejected scope additions: **1** (`D-05`)
- unresolved authority conflicts introduced: **0**

This contribution used only the shared kickoff packet; its context-cost count
beyond that packet is therefore `0`. The coordinator can record the two
essential refinements as rework to the frame without treating any conclusion
as a policy or implementation decision.
