# Repair and Learning

Fix what is mechanical. Propose what is structural. Prevent the next
occurrence, not only this one.

## Repair triage

| Severity | Meaning | Action |
| --- | --- | --- |
| Cosmetic | Formatting or harmless stale detail | Correct and verify normally. |
| Drift | Recorded state differs from verified reality | Repair mechanically; record the cause and verification. |
| Blocking | Drift stops valid work | Repair directly only if mechanical; otherwise propose and escalate. |
| Structural | Repair changes authority, ownership, decisions, data shape, or approved behavior | Do not silently apply; use a decision/change path. |

For drift or worse, write a repair note with: trigger/evidence, severity,
change made or proposed, verification, rollback, and prevention follow-up.
Use [the repair-record template](../templates/repair-record.md) to capture that
evidence before applying a drift/blocking repair or proposing a structural one.

## Diagnostics do not grant repair authority

A validator, health check, replay index, monitor, or audit may detect a problem.
Detection does not authorize it to rewrite intent, policy, ownership, scope,
architecture, or other structural state.

Use:

```text
detect
→ classify
→ repair mechanically when already authorized
  OR propose/escalate
→ verify
```

A diagnostic surface should report drift clearly and remain read-only unless a
separate, bounded repair action is explicitly part of its contract.

## Learning loops

- **In-line repair:** one incident, repaired and verified.
- **Emergence:** a reusable insight or idea surfaced by the incident.
- **Retrospective:** at a project phase or multi-task cycle, examine patterns:
  what happened, why, what worked, what did not, and which change to make.

If a failure repeats, do not merely create another repair note. Add a durable
countermeasure: validator, template field, test, default, checklist, or
decision. Test the countermeasure against the failure that motivated it.

When a recurring lesson becomes startup/task guidance, keep it scoped and point
back to the evidence that justified it. Do not load the full incident archive
into every future agent session.

## Freezing a real incident as a regression case

When a real incident is severe enough, or has already repeated, to warrant a
permanent test (the "add a durable countermeasure" step above) rather than
only a repair note, convert it into a `MAPS_FROZEN_REGRESSION_CASE`
(`runtime/evaluation/regression_case.py`) instead of describing it in prose:

1. Produce or locate the exact portable Run Record for the task/run that
   exhibited the failure: `python -m runtime.cli run-record <task_id> <run_id>`.
2. Classify the incident into one `IncidentCategory`
   (`runtime/evaluation/regression_case.py`) -- e.g. `TOOL_FAILURE`,
   `CONTEXT_POISONING`, `AUTHORITY_VIOLATION_ATTEMPT`. `UNKNOWN` is accepted
   but should be revisited once the real cause is understood.
3. Write a sanitized fixture: the minimal reproducible input/state that
   exhibits the failure, with any secret-shaped text redacted -- `freeze-case`
   rejects a fixture that still contains text `redact_sensitive_text` would
   flag.
4. Name the specific expected properties the case should assert as short
   lowercase machine IDs (e.g. `no-secret-leak`, `hook-blocks-write`) -- these
   become the pass/fail contract future evaluation runs check against.
5. Freeze it: `python -m runtime.cli freeze-case <task_id> <run_id> --category
   <CATEGORY> --fixture-file <path|-> --expect <property-id> [--expect ...]
   --tag <tag> [--tag ...] --frozen-by <actor>`.
6. Store the emitted JSON at `work/regression-cases/<case_id>.json` (create
   the directory the first time it is used) and commit it alongside the
   repair note -- this is the durable countermeasure artifact the note should
   reference, not a description of one.
7. A frozen case's `promotion.automatic` is always `false`: it is evaluation
   evidence only and never self-authorizes a harness/policy/routing change on
   its own. A case passing or failing informs a human repair/change decision;
   it does not make one.

This adds the mechanical step; it does not change repair-note severity
triage above, and it does not itself decide when a countermeasure is
warranted -- that judgment still follows the triage table.
