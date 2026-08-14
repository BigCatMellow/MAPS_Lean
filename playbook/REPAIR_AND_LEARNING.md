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

## Learning loops

- **In-line repair:** one incident, repaired and verified.
- **Emergence:** a reusable insight or idea surfaced by the incident.
- **Retrospective:** at a project phase or multi-task cycle, examine patterns:
  what happened, why, what worked, what did not, and which change to make.

If a failure repeats, do not merely create another repair note. Add a durable
countermeasure: validator, template field, test, default, checklist, or
decision. Test the countermeasure against the failure that motivated it.
