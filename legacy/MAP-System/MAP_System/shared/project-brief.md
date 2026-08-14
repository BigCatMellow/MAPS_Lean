<!-- hpom: file: shared/project-brief.md -->
<!-- hpom: project: MAP -->
<!-- hpom: state_owner: command-center -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-22 -->
<!-- hpom: verified_against: DEC-028, TASK-205 release, TASK-267 alignment audit -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# Project Brief

## Objective

Create a reusable, operator-directed multi-agent delivery system where Codex and
Claude can turn real project goals into owned, reviewable, reversible work. MAP
uses durable files for human-readable truth, SQLite for atomic coordination,
LangGraph for routing, and the AI Command Center as the operator's attention and
control surface.

The first standing proving workflow is software delivery (DEC-028). MAP is not
successful merely because it has more framework components; it is successful
when those components help ship useful software with less operator coordination
cost and without losing ownership, evidence, or safety boundaries.

## Completion Condition

The system is working as intended when:

- one current project brief and current-state file orient every active agent;
- one accountable owner holds each active task and a different agent reviews
  substantive work;
- operator attention is reserved for decisions, approvals, blockers,
  conflicts, and safety/scope risks rather than routine progress;
- real software moves through intake, claim, implementation, verification,
  independent review, and release with durable evidence;
- helpers reduce bounded support load without gaining task, review, release, or
  policy authority;
- runtime state, task mirrors, decisions, handoffs, and executable behavior do
  not silently contradict one another.

## Operating Model

This is MAP's canonical authority hierarchy. More specific instructions may
constrain a role further, but may not reorder or expand these authorities.

0. **Operator — `bigboss` / Command Center.** Owns intent, priority, policy and
   scope decisions, high-authority approvals, veto, and stop control.
1. **One designated coordinator per run.** The operator may designate one
   coordinator to integrate work, route tasks, and account for helpers. Codex
   and Claude are the eligible peer core agents (DEC-008): Codex is normally
   implementation-led and Claude review/architecture-led, but capability,
   independence, and the explicit run designation control assignment. A
   provider, model, live terminal, or fixed-roster slot is not a designation.
2. **Task lifecycle — accountable owner and independent reviewer.** Every
   active task has one owner and a different reviewer for substantive work.
   These are parallel, conflict-separated work roles rather than permanent
   ranks. Canonical SQLite claims and review records—not chat or terminal
   presence—bind the assignments.
3. **Bounded support — Pi, Librarian, visible helpers, and local assistants.**
   These lanes provide scoped observations, retrieval, drafts, experiments, or
   checks under a named accountable owner. They gain no task, review, release,
   routing, policy, coordinator, or operator authority.

Session continuity is a separate axis from authority. A checksum-bound context
rotation preserves only the explicit obligations frozen in its snapshot. A
replacement continues an existing designated coordinator role only after the
old session finalizes the verified ledger transfer; prepare or ACK alone does
not transfer it. Rotation never creates a core seat, promotion, task claim,
review independence, or operator authority.

Control systems are not roles: RUKI SQLite stores canonical lifecycle state,
LangGraph recommends routes, hcom communicates, and Command Center exposes
operator controls. None becomes an owner or decision authority by storing,
moving, or displaying state.

Temporary helpers remain visible, bounded, durably recorded, and owned by a
core agent. Their model tier is selected by task difficulty (Haiku for explicit
checks, Sonnet for cross-file reasoning, Opus for unusually hard
architecture/security), not by habit or availability. Local/Ollama support
also requires a recorded bounded purpose and stays outside the control plane.

## Current Direction

- DEC-028 selected software delivery as the standing proving workflow.
- TASK-205 completed the first proving slice: ProjectUpdater full-fidelity JSON
  backup export/import.
- The 2026-07-22 recovery batch is discharged. Every item it named is now
  RELEASED: the RnS terminal-session repair (TASK-186), the orphan-recovery
  path (TASK-266), the CommandCenterUI source-of-truth/security lane
  (TASK-265, with DEC-029/030/033 settling the policy questions), and the
  proposal-only advisory monitor (TASK-236).
- SYN-0001 (one state, multiple readers, no declared authority) is no longer
  unshaped, but it is not closed either. Its authority contracts landed
  through TASK-268 (lifecycle authority seam), TASK-274/278 (durable
  submission authorship keying review separation), and TASK-279 (generated
  active state with separate annotations). What 2026-07-28 showed is that the
  remaining failures of this pattern are **cadence** failures, not missing
  contracts: `shared/current-state.md` drifted from canonical `map.db` for six
  days even though `validate_shared_state_tasks.py` already detected it and
  already ran in `run_tests.sh`. A control nobody runs is not a control.
  TASK-291 addresses that specific gap by making the check a standing startup
  habit. Expect the next instances of SYN-0001 to look the same: the detector
  exists, nothing invokes it.
- The live gap between this brief's Completion Condition and reality is the
  release backlog, not missing capability. Work is reaching APPROVED and
  stopping there. See `shared/current-state.md` for the current count and
  disposition.
- The next substantive move is an operator direction call, not an engineering
  one: choose the next real software slice rather than extending MAP
  infrastructure by default. That choice has been deferred through two
  recovery batches now and should be made deliberately rather than by drift.

## Non-Goals

- Building process or documentation that does not change agent behavior.
- Treating every available model or live session as a core authority.
- Replacing operator judgment with autonomous policy invention.
- Using chat transcripts, UI state, or helper output as canonical project truth.
- Expanding infrastructure indefinitely without proving it on real delivery.

## Source Baseline

The original source architecture remains
`general-purpose-multi-agent-project-system-v2.md`; approved decisions and
current executable state supersede it where the system has evolved.

The stress-test note `Story_logic_test.md` is preserved as a project artifact/source note and should not be treated as a runtime protocol document.
