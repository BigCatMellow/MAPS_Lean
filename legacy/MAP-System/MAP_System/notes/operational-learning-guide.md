# Operational Learning Guide

Operational learning converts an incident note into future behavior without
loading all historical E/I records into every agent session.

## Lifecycle

1. Capture the observation as an E/I Insight.
2. Merge it with an existing Idea or create one only when the mechanism is new.
3. Review/promote the behavior-changing proposal through the normal E/I gate.
4. Add the adopted lesson to `agents/operational-lessons.json` with provenance,
   scopes, owner, activation time, review trigger, and optional review date.
5. Startup orientation calls `scripts/operational_lessons.py orientation` for
   its current scope and reads only active matching lessons.
6. When the trigger occurs, retire or supersede the lesson; never delete its
   E/I provenance.

## Commands

```bash
python3 MAP_System/scripts/operational_lessons.py validate --pretty
python3 MAP_System/scripts/operational_lessons.py orientation --scope startup --scope helper-routing --pretty
```

The JSON store is the canonical active-lesson source. Startup output is a
generated projection, not another authority. Raw insights, task notes, hcom
messages, and status notes do not become mandatory behavior until reviewed and
promoted.

## Safety

- Active lessons cannot create tasks, approve work, or change policy by
  themselves.
- `review_after` is a review prompt, not automatic expiry or mutation.
- Conflicting active titles, missing provenance, invalid timestamps, and broken
  supersession references fail validation.
- Every model-backed helper remains visible under `AGENTS.md`; operational
  learning cannot authorize headless agents.
