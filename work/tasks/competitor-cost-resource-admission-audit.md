# Task: competitor-derived cost/resource admission audit

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `RESEARCH / DESIGN AUDIT`
- Owner: orchestration operator
- Risk: `MEDIUM`

## Goal

Determine whether MAPS_L currently has a pre-launch resource/cost admission mechanism equivalent to the reservation semantics highlighted by LiteLLM and the Pilot borrow-before-build corpus, without confusing permission-to-spend, runtime limits, and actual monetary accounting.

## Inputs / source of truth

- `AGENTS.md`
- `runtime/integrity/budget.py`
- `runtime/integrity/README.md`
- `runtime/policy/evaluator.py`
- `runtime/policy/models.py`
- `work/roadmaps/CAPABILITY_CHECKLIST.md`
- upstream evidence: `BigCatMellow/Pilot_Projects@f6d584465e15b0fcf3cd09fea9e056bc23852e94`, especially `P0-COST-RESOURCE-ADMISSION.md` and LiteLLM failure evidence.

## Boundary

This task is audit-only. It must not add a spend ledger, provider integration, billing API, reservation table, paid execution, or capability-status change.

## Result

`DESIGN GAP IDENTIFIED`.

Current run-budget code freezes/checks `max_attempts`, `max_tool_failures`, and `runtime_seconds` after measured use. It is intentionally deterministic/non-authoritative and does not reserve resources before launch. Current worker `cost_rank` is a relative routing preference, not a monetary budget. The inspected assignment evaluator does not perform monetary admission.

Therefore current MAPS_L does not yet express the stronger invariant:

`authorized spend envelope -> conservative next-operation estimate -> atomic reservation -> admit/reject -> launch -> settle/refund/reconcile`.

Detailed evidence: `work/notes/2026-09-09-cost-resource-admission-audit.md`.

## Acceptance criteria

- [x] distinguish runtime-count limits from monetary/resource reservation;
- [x] distinguish cost preference from hard monetary ceiling;
- [x] identify whether current checks happen before or after measured usage;
- [x] route the gap without inventing a second task authority;
- [x] state a smallest future proof before implementation.

## Review

Independent review should challenge whether another existing MAPS owner already provides pre-dispatch monetary reservation and whether any current field has stronger semantics than this audit attributes to it.
