# DEC-001: Target Operating Model and WezTerm-Decoupling Plan

- Date: 2026-08-13
- Status: `PROPOSED`
- Owner: Operator
- Decision class: Architecture / operations

## Context

The original MAP project contains a mature method library and a control plane:
SQLite task state, LangGraph route selection, RnS (Rise & Shine) recovery, and
hcom messaging/session control. The current implementation couples some of
those capabilities to a WezTerm Command Center Lab and a fixed startup roster.

Codex and Claude can now spawn and manage agents in native windows. The goal is
to retain the durable coordination and recovery capabilities while making
WezTerm an optional operator presentation layer rather than a prerequisite.

## Proposed target model

| Component | Proposed role |
| --- | --- |
| Native Codex and Claude agent windows | Default interactive agent surface. |
| hcom | Retained cross-provider message and session-control transport. Current RnS uses it for session listing, resume, and nudging. |
| SQLite | Canonical mutable task lifecycle ledger: atomic claims, leases, submissions, independent-review authorship, and checkpoints. |
| LangGraph | Read-first dispatcher: evaluates task/dependency/policy/availability state and recommends the next route. It does not author roadmaps or make product decisions. |
| RnS | Deterministic, reboot-safe recovery supervisor for limits/stale sessions. Durable handoffs remain the recovery foundation. |
| Markdown roadmap and ProjectUpdater | Markdown remains the durable plan; ProjectUpdater is a tracked visual projection/import target. |
| WezTerm and fixed roster | Optional cockpit/presentation. Neither grants authority or should be required for normal operation. |
| Command Center UI | Requires a separate decision: retain as an operator dashboard, simplify, or retire. |

## What must be designed before removing WezTerm

1. **RnS resume adapter:** specify how a resumed hcom session opens or reaches
   an agent when `wezterm-tab` is unavailable, and prove the recovery prompt
   reaches the right session.
2. **Reachability contract:** define how the operator can inspect, interrupt,
   approve, and stop native-window helpers without relying on a WezTerm pane.
3. **Runtime manifest:** name the canonical live code/configuration locations,
   required services, source-of-truth files, and test/installation entrypoints.
4. **Operator runbook:** give one short procedure for startup, task lifecycle,
   review, provider limits, restarts, expired leases, recovery, and helper
   retirement.
5. **ProjectUpdater data policy:** define Markdown as durable source, backup /
   export behavior, import cadence, and reconciliation of UI checkbox changes.
6. **Canonical context stack:** establish the minimal files an agent reads at
   startup, and prevent broad legacy documents from loading by default.

## Migration roadmap

## Phase 0 — Establish truth and safety
- [ ] Inventory live runtime code, configuration, services, launchers, and
  authoritative SQLite/file state.
- [ ] Create the active-runtime manifest and backup/recovery plan.
- [ ] Define the native-window reachability and RnS resume contract.
- [ ] Decide the future role of Command Center UI.

## Phase 1 — Decouple recovery from WezTerm
- [ ] Implement a tested RnS terminal/resume adapter that does not require
  `--terminal wezterm-tab`.
- [ ] Preserve hcom session identity, transcript access, resume, and nudge
  behavior.
- [ ] Update helper spawning and limit/restart documentation to the new
  reachability contract.
- [ ] Preserve a reversible WezTerm fallback through the transition.

## Phase 2 — Promote the retained control plane
- [ ] Move or clearly expose active SQLite, LangGraph, RnS, hcom, validators,
  and operational scripts outside the ambiguous `legacy/` boundary.
- [ ] Keep historical artifacts and the WezTerm cockpit separately archived.
- [ ] Update the installer and active runtime manifest.

## Phase 3 — Prove the operating model
- [ ] Two agents race for one task; only one atomic SQLite claim succeeds.
- [ ] A submitted task routes to an independent reviewer; self-review is
  rejected.
- [ ] An agent hits a limit, a handoff exists, RnS wakes/nudges it, and work
  resumes without WezTerm.
- [ ] Machine/session restart preserves current task, owner, next action, and
  recovery path.
- [ ] A Markdown roadmap imports to ProjectUpdater and can be restored from its
  durable source.
- [ ] A helper completes, reports, and retires without becoming stale active
  capacity.

## Phase 4 — Retire the mandatory cockpit assumption
- [ ] Make WezTerm optional in docs, installers, launchers, and tests.
- [ ] Retire only obsolete cockpit code after the Phase 3 scenarios pass and a
  rollback path is recorded.

## Acceptance criteria for this decision

- [ ] A single active-runtime manifest identifies all live control-plane code
  and sources of truth.
- [ ] RnS recovery works with no WezTerm process or `wezterm-tab` terminal.
- [ ] SQLite, LangGraph, RnS, and hcom retain their tested responsibilities.
- [ ] The operator can inspect and stop active native-window helpers.
- [ ] The minimal agent context stack is documented and usable without opening
  the historical MAP corpus.
- [ ] ProjectUpdater has a documented durable roadmap/backup policy.

## Risks and constraints

- Removing WezTerm before a proven hcom resume adapter could make RnS wake an
  agent without making it operator-reachable.
- Native agent UI behavior must be verified in actual recovery scenarios; it
  cannot be inferred from normal agent spawning.
- SQLite/file mirrors must retain a single canonical writer for lifecycle
  facts; a new dashboard or Markdown file must not become a competing mutable
  truth source.
- This migration should not weaken review separation, destructive-action
  safeguards, or handoff durability.

## Next action

Start Phase 0 by producing the active-runtime manifest and a read-only
inventory of all WezTerm-coupled entrypoints.

## Reconciliation note — 2026-08-26

This record's historical checklist is **not** the current MAPS capability
scoreboard. Much of the proposed target model has since been adopted in active
Lean architecture: WezTerm/fixed-roster behavior is optional presentation,
SQLite remains canonical task truth, hcom remains transport/session control,
and RnS/Harness/Context work has advanced substantially.

Formal `Status: PROPOSED` is intentionally left unchanged by the reconciliation
maintenance pass because changing the decision's authority state should be an
explicit operator/decision action, not inferred from implementation drift.
Future workers should use the current capability checklist and current-state
handoff for implementation status rather than reopening this plan's unchecked
boxes as new work.

## Connections

- Current operating contract: [AGENTS.md](../../AGENTS.md)
- Active playbook index: [playbook/INDEX.md](../../playbook/INDEX.md)
- Current capability scoreboard: [CAPABILITY_CHECKLIST.md](../roadmaps/CAPABILITY_CHECKLIST.md)
- Current handoff: [2026-08-26 project reconciliation and Proof Phase](../handoffs/2026-08-26-project-reconciliation-and-proof-phase.md)
- Supersedes: `none recorded`
- Superseded by: `none formally recorded`

