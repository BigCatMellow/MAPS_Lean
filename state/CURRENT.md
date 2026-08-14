# Current State

- Current goal: Promote the retained MAPS control plane into a small active,
  provider-neutral runtime without restoring legacy cockpit complexity.
- Active task: [TASK-009](../work/tasks/TASK-009-active-sqlite-agi-runtime.md)
  is `READY_FOR_REVIEW` on `agent/active-sqlite-agi-runtime`.
- Current implementation state: `runtime/state/` now provides the first active
  slice—SQLite task truth, structural AGI `READY` enforcement, atomic claims
  and leases, durable submission authorship, independent-review separation,
  rework, and task events.
- Verification: owner-side regression suite passes 15 tests, including
  simultaneous READY-promotion/output-path contention and simultaneous claim
  contention. SQLite smoke settings are foreign keys on, WAL mode, and a
  5000 ms busy timeout.
- Not promoted yet: LangGraph routing/checkpoints, hcom adapter/session
  transport, RnS recovery, and local-helper adapters. Their source remains
  preserved under `migration/` and `legacy/` while each layer is promoted and
  tested separately.
- Decisions that matter now: SQLite remains canonical mutable task state;
  LangGraph must remain routing/checkpoint state only; hcom remains transport;
  WezTerm remains optional presentation. DEC-001 is still a proposed broader
  operating-model decision and is not implicitly approved by TASK-009.
- Blocker: TASK-009 requires independent review before merge/completion.
- Next action: review the SQLite/AGI runtime PR against TASK-009 and the P0
  invariants. After approval/merge, continue with the next isolated runtime
  layer rather than bundling routing, transport, and recovery into one change.
