# Protocol Effectiveness Benchmark

Status: **DESIGN APPROVED — PRE-AUTHORING FREEZE PACKAGE ACTIVE; NOT EXECUTED**

Primary question:

> Given otherwise equivalent capable agents, does applying an operating protocol such as MAPS_L improve objectively correct autonomous task completion enough to justify its cost, complexity, and failure modes?

MAPS_L is a treatment configuration, not the grading definition. Protocol adherence is diagnostic only.

## Current gate

The pre-corpus design gate was independently approved at exact head `369bccaf68b258c70eb6efec0c9f70115c8014cb`:

- [`../../reviews/pr-341-rereview-evidence-369bcca.md`](../../reviews/pr-341-rereview-evidence-369bcca.md) — r9: `APPROVED FOR CORPUS CONSTRUCTION`.
- J3/v5 safeguard resolved; I2–I4 and all B/M/N/F/G/H owner findings remain resolved.
- 512-state S4 verification carried forward: 0 ambiguous, 0 unhandled, 0 semantic mismatches.

The five normative owner documents remain frozen by the v5 whole-document safeguard:

- [`BENCHMARK-SPEC.md`](BENCHMARK-SPEC.md)
- [`CASE-DESIGN.md`](CASE-DESIGN.md)
- [`RUN-PROTOCOL.md`](RUN-PROTOCOL.md)
- [`SCORING-AND-ANALYSIS.md`](SCORING-AND-ANALYSIS.md)
- [`REPORT-TEMPLATE.md`](REPORT-TEMPLATE.md)

This README is navigation/status only. It does not redefine those owners.

## Pre-authoring freeze package

Current non-secret instantiation work is under [`pre-corpus/`](pre-corpus/):

- `TREATMENT-SURFACE-MANIFEST.md` — candidate tested ref, bundle surface, common bootstrap, injection/parity policy.
- `GENERIC-CONTROL.md` — candidate competent Arm C text; requires independent authorship/approval.
- `TARGET-WORK-SAMPLING-MANIFEST.md` — deterministic sampling method; concrete pools/reference model must be frozen by an independent curator before selection.
- `CUSTODY-AND-EXPOSURE-PLAN.md` — access-based custody boundary for primary/holdout material.

Parent task: [`../../tasks/protocol-effectiveness-benchmark.md`](../../tasks/protocol-effectiveness-benchmark.md).
Corpus child task: [`../../tasks/protocol-effectiveness-corpus-construction.md`](../../tasks/protocol-effectiveness-corpus-construction.md).

## Critical custody boundary

No selected `FROZEN_STANDARD` or `SEALED_HOLDOUT` case identity/content may be created in this repository or a user-visible MAPS_L-owner chat. The approved exposure rule is access-based: anyone able to modify MAPS_L or a successor must not have access to pristine primary case content before its permitted look.

The current repository/user context therefore cannot serve as the independent corpus custodian. An eligible curator/custodian with access-controlled storage is required before case selection/authoring.

## What remains prohibited

Nothing has been executed. No A/B/C candidate runs, Smoke, Standard, benchmark evaluator/model/API calls, spending, MAPS_L runtime/protocol changes, promotion, or merge are authorized by the design approval.

## Exact next phase

1. finish/freeze the non-secret treatment/Arm-C/sampling/custody package;
2. obtain independent pre-authoring freeze verification;
3. assign an eligible independent curator/custodian;
4. construct the unexposed primary corpus and sealed holdout outside MAPS_L-owner access;
5. return only hashes/counts/non-secret aggregate freeze evidence;
6. perform a fresh independent corpus/pre-freeze review.

Benchmark execution remains a later, separate pre-run gate.
