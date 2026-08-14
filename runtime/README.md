# MAPS Lean Runtime

This directory is the active provider-neutral MAPS runtime.

The first implemented slice is `runtime/state/`: SQLite task truth plus the
structural AGI `READY` gate. It intentionally does not import code from
`legacy/` or `migration/`.

## Mutable state

Default local database:

```text
.maps/state/maps.db
```

It is ignored by Git. SQLite connections enable foreign keys, WAL, and a
5-second busy timeout.

## First-slice lifecycle

```text
NEEDS_SHAPING
    │  AGI structural gate passes
    ▼
READY
    │  atomic claim + lease
    ▼
ACTIVE
    │  submit with evidence
    ▼
READY_FOR_REVIEW
    │
    ├─ APPROVED ─────────► DONE
    ├─ CHANGES_REQUESTED ► CHANGES_REQUESTED ─► ACTIVE
    └─ BLOCKED ──────────► BLOCKED
```

`owner` and `claimed_by` are separate. Recovering an expired lease changes the
claimant, not the accountable owner.

## AGI gate

`promote_ready()` checks the task contract and changes `NEEDS_SHAPING → READY`
in the **same `BEGIN IMMEDIATE` transaction**. This matters because output-path
reservation is part of readiness; two simultaneous promotions must not both
reserve the same active path.

The current validator is deliberately structural. It checks that required AGI
fields exist, dependency tasks are DONE, and active output paths do not
conflict. It does not pretend to judge whether prose is semantically good.

## CLI

From the repository root:

```bash
python -m runtime.cli init
python -m runtime.cli create --title "Example"
python -m runtime.cli shape TASK-0001 --contract-json task.json
python -m runtime.cli check TASK-0001
python -m runtime.cli promote TASK-0001 --actor shaper
python -m runtime.cli claim TASK-0001 codex --lease-seconds 900
python -m runtime.cli submit TASK-0001 codex --evidence "python -m unittest ...: PASS"
python -m runtime.cli review-claim TASK-0001 claude
python -m runtime.cli review-record TASK-0001 claude APPROVED --summary "criteria verified"
```

All commands print JSON and use non-zero exit status for typed failures.

## Tests

```bash
python -m unittest discover -s tests -v
```

The first suite covers AGI promotion, atomic claims, lease recovery, owner vs
claimant separation, output-path conflicts, durable submission authorship,
independent review, rework, task-ID allocation, and SQLite safety settings.
