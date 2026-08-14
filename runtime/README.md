# MAPS Lean Runtime

This directory is the active provider-neutral MAPS runtime.

Implemented slices:

- `runtime/state/` — SQLite task truth plus the structural AGI `READY` gate.
- `runtime/policy/` — explicit task policy metadata, operator approvals, worker
  capability envelopes, and durable dispatch halt state.
- `runtime/routing/` — deterministic route selection wrapped by LangGraph with
  a separate SQLite checkpoint database.
- `runtime/communication/` — narrow hcom messaging/session adapter with
  project-local `HCOM_DIR`; transport state never grants MAPS authority.

Active runtime does not import executable code from `legacy/` or `migration/`.

## Mutable state

```text
.maps/state/maps.db                    canonical MAPS task truth
.maps/state/langgraph-checkpoints.db   LangGraph routing/checkpoint memory
.maps/state/halt.json                  inspectable dispatch halt state
.hcom/                                 hcom message/session/process state
```

These stores stay separate. Routing checkpoints and hcom communication state do
not grant task ownership, completion, review, or approval authority.

## Task lifecycle

```text
NEEDS_SHAPING
    │  AGI structural gate passes
    ▼
READY
    │  route recommendation + guarded atomic claim
    ▼
ACTIVE
    │  submit with evidence
    ▼
READY_FOR_REVIEW
    │  route to eligible independent reviewer
    ├─ APPROVED ─────────► DONE
    ├─ CHANGES_REQUESTED ► CHANGES_REQUESTED ─► ACTIVE
    └─ BLOCKED ──────────► BLOCKED
```

`owner` and `claimed_by` are separate. Recovering an expired lease changes the
claimant, not the accountable owner.

## AGI gate

`promote_ready()` checks the task contract and changes `NEEDS_SHAPING → READY`
in the **same `BEGIN IMMEDIATE` transaction**. Output-path reservation is part
of readiness, so two simultaneous promotions cannot both reserve the same
active path.

The current validator is structural. It checks required AGI fields,
dependencies, and active output-path conflicts. Semantic quality remains a
shaping/review responsibility.

## Routing contract

```text
read canonical task snapshots
→ read explicit worker profiles
→ read durable halt state
→ apply deterministic policy gates
→ choose cheapest competent available envelope
→ emit one recommendation
```

Routes:

```text
review
wait_for_agent
propose_helper
claim_or_assign
policy_gate
wait_or_reconcile
```

A recommendation is **not a mutation**. A caller must still use guarded
`TaskStore` operations such as `claim_task()` or `claim_review()`.

Worker profiles describe the actual execution envelope rather than provider
reputation. See `templates/worker-profiles.example.json`.

## Explicit policy flags

Machine routing uses explicit task policy state rather than guessing from prose:

```text
requires_operator_approval
destructive_action
external_side_effect
security_sensitive
broad_architecture
paid_execution
```

If an approval-triggering flag is true, dispatch stops at `policy_gate` until
operator approval is durably recorded. Reshaping the task clears prior approval.

## Halt modes

```text
halt_paid_dispatch
halt_all_dispatch
repair_only
```

Halts block routing lanes only. They do not rewrite task status, ownership, or
review records.

## hcom boundary

`runtime/communication/hcom_adapter.py` wraps current hcom CLI operations:

```text
list_sessions
read_events
send
spawn
resume
stop
```

Machine reads use `hcom list --json` and JSON event records. Side effects use
argv-based subprocess calls with `shell=False`. The adapter always sets its
configured project-local `HCOM_DIR` and has no import of the MAPS task store.

Important non-equivalences:

```text
message sent       != task assigned
session active     != task owned
agent says "done"  != task DONE
hcom intent        != MAPS authority
```

See `runtime/communication/README.md`.

## Dependencies

```bash
python -m pip install -r runtime/requirements.txt
```

LangGraph checkpoints use `.maps/state/langgraph-checkpoints.db`. The runtime
defaults `LANGGRAPH_STRICT_MSGPACK=true` unless explicitly overridden.

hcom is installed separately; see `docs/CONTROL_PLANE_SETUP.md`.

## CLI

Task state:

```bash
python -m runtime.cli init
python -m runtime.cli create --title "Example"
python -m runtime.cli shape TASK-0001 --contract-json task.json
python -m runtime.cli check TASK-0001
python -m runtime.cli promote TASK-0001 --actor shaper
python -m runtime.cli claim TASK-0001 codex --lease-seconds 900
python -m runtime.cli submit TASK-0001 codex --evidence "tests: PASS"
python -m runtime.cli review-claim TASK-0001 claude
python -m runtime.cli review-record TASK-0001 claude APPROVED --summary "criteria verified"
```

Routing/policy:

```bash
python -m runtime.routing.cli route --workers-json templates/worker-profiles.example.json
python -m runtime.routing.cli approve TASK-0001 --approved-by operator --note "approved exact action"
python -m runtime.routing.cli halt-show
python -m runtime.routing.cli halt-set halt_paid_dispatch --reason provider-limit --actor core --authority core
python -m runtime.routing.cli halt-clear --actor operator --authority operator --reason resolved
```

## Tests

```bash
python -m unittest discover -s tests -v
```

State tests cover AGI/claims/leases/review. Routing tests cover capability and
policy decisions. `tests/test_hcom_adapter.py` uses a fake hcom executable and
performs no live messaging, spawning, resuming, or killing.
