# TASK-303 Canonical Authority Hierarchy Alignment

task_id: TASK-303
owner: rotation-replacement-mudo-hera
operator_approval: bigboss/user “go for it,” relayed by codex-lab-rosa in hcom
request 30843 on 2026-07-29
risk: PROCESS / STRUCTURAL
decision_class: AUTHORITY

## Problem

TASK-302 correctly restored the fixed Command Center Lab roster, but the
visible roster did not carry one equally explicit authority view. Historical
TASK-286 language could therefore make an open Codex tab look like a permanent
coordinator, while context replacement could look like promotion instead of
session continuity.

## Canonical Contract

1. `bigboss` / operator / Command Center owns intent, priority, policy and
   scope decisions, high-authority approvals, veto, and stop control.
2. The operator may designate one coordinator per run from the eligible peer
   Codex and Claude core agents.
3. Each task has one accountable owner and a different independent reviewer
   for substantive work. These are parallel lifecycle roles bound by canonical
   SQLite claims/reviews.
4. Pi, Librarian, visible helpers, and local assistants are bounded support
   under a named owner, without task, review, release, routing, policy,
   coordinator, or operator authority.

Fixed-roster visibility, provider/model identity, terminal presence, RUKI
SQLite, LangGraph, hcom, and Command Center presentation do not confer
authority.

## Rotation Boundary

`prepare` freezes evidence and `ack` binds a live replacement; neither
transfers role authority. Successful `finalize` transfers only explicit frozen
claims and obligations. An existing coordinator designation continues only
when the snapshot records it and the operator has not revoked it.

## Changed Surfaces

- `AGENTS.md`: points readers to the canonical hierarchy.
- `MAP_System/AGENTS.md`: concise governing hierarchy and control-system
  boundary.
- `MAP_System/shared/project-brief.md`: canonical authority source.
- `MAP_System/notes/context-rotation-guide.md`: prepare/ACK/finalize authority
  semantics.
- `MAP_System/notes/command-center-orchestrator-lifecycle.md`: reconciles the
  TASK-286/TASK-302 history with the current fixed-roster contract.
- Fixed Codex, Claude, Pi, and Librarian launcher templates: role-aware startup
  instructions.
- WezTerm Lab template: presentation comment explicitly separates visibility
  from authority.
- `MAP_System/tests/test_authority_hierarchy_contract.py`: contradiction
  checks.

No scheduler, role registry, database schema, claim mechanism, or orchestration
subsystem is added.

## Verification

Focused verification completed on KUDU:

- `MAP_System/.venv/bin/python MAP_System/tests/test_authority_hierarchy_contract.py`
  — 5 tests passed.
- `MAP_System/.venv/bin/python MAP_System/tests/test_command_center_orchestrator_startup.py`
  — 12 tests passed.
- `MAP_System/.venv/bin/python MAP_System/tests/test_context_rotation.py`
  — 18 tests passed.
- `MAP_System/.venv/bin/python MAP_System/tests/test_command_center_lab_tab_titles.py`
  — 2 tests passed.
- `sh -n` on the Codex, Claude, Pi, and Librarian launcher templates — passed.
- `git diff --check` on every TASK-303 output — passed.
- The exact 12-file deliverable was checksum-staged and installed into RUKI's
  review tree after preserving `/tmp/task303-preinstall-20260729T0309Z.tar`.
- RUKI rerun: hierarchy 5 passed; startup 12 passed; rotation 16 passed; four
  launcher templates passed `sh -n`.

Independent review remains required before approval.

## Rollback

Revert TASK-303's documentation, prompt, presentation-comment, and test changes
together. Preserve TASK-302's fixed seven-pane roster.

## Residual Boundaries

- Existing operator, policy, security, privacy, destructive-action, ownership,
  and independent-review gates are unchanged.
- Prompt text explains authority but does not mechanically enforce designation;
  canonical SQLite claims/reviews and the continuity ledger remain the
  enforceable lifecycle records.
- Operator-facing friction closeout: no new operator-friction candidate found;
  TASK-303 directly resolves the reported ambiguity.
