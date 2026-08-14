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
