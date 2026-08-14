# TASK-313 WS-1 Path Ownership Prerequisite

- task_id: TASK-313
- owner: codex-lab-vumo
- status: recommendation_pending_command_center_disposition
- date: 2026-07-30
- scope: record the authoritative before-state and recommend a bounded disposition for `MAP_System/graph/runner.py` and `MAP_System/templates/install/command-center-ui/app/server.py`
- excluded_scope: no TASK-304 implementation, TASK-306 deployment, TASK-308 work, acceptance-criteria changes, direct SQL, or silent task-file edits

## Evidence Sources

- Risa hcom request `map-recovery-task313 #47654`: Sequence Amendment 1 approved by operator and independent reviewer; TASK-313 canonical on Smalls; codex-lab-vumo assigned owner.
- `MAP_System/.venv/bin/python MAP_System/scripts/map_authority.py claim TASK-313 codex-lab-vumo`: returned `claimed=true`.
- `MAP_System/.venv/bin/python MAP_System/scripts/map_authority.py heartbeat TASK-313 codex-lab-vumo`: returned `renewed=true`.
- `map_authority.py task show TASK-304`, `TASK-306`, `TASK-310`, and `TASK-313`: authoritative task rows used below.
- Task mirror scan across `MAP_System/tasks/TASK-*.json` for the two exact paths.
- The referenced recovery-copy review artifact `MAP_System_Recovery_2026-07-29/03_kickoff/MAP_RECOVERY_SEQUENCE_AMENDMENT_1_REVIEW.md` was not available in this filesystem under `/home/home/Projects/MultiAgentProject` or a shallow `/home/home` search. This recommendation therefore cites the hcom routing/approval statement for amendment validity, not the missing file content.

## Authoritative Before-State Rows

| Task | Status | Owner | Claimed by | Dependencies | Relevant output ownership | Approval gates |
|---|---|---|---|---|---|---|
| TASK-304 | READY | command-center | none | TASK-303 | `MAP_System/graph/runner.py`; `MAP_System/templates/install/command-center-ui/app/server.py` | `requires_operator_approval=true`; `decision_class=AUTHORITY`; `risk_class=PROCESS`; `risk_severity=STRUCTURAL`; `canonical_map_mutation=true`; `final_review=true` |
| TASK-306 | CHANGES_REQUESTED | claude-lab-nene | none | none | `MAP_System/templates/install/command-center-ui/app/server.py` | `requires_operator_approval=true`; `decision_class=ARCHITECTURE`; `risk_class=SECURITY`; `risk_severity=STRUCTURAL` |
| TASK-310 | IN_PROGRESS | codex-lab-risa | codex-lab-risa | none | no current ownership of either contested path | `requires_operator_approval=false`; `decision_class=AUTHORITY`; `risk_class=DATA`; `risk_severity=STRUCTURAL` |
| TASK-313 | IN_PROGRESS | codex-lab-vumo | codex-lab-vumo | none | `MAP_System/artifacts/recovery/ws1-path-ownership-prerequisite.md` only | `requires_operator_approval=false`; `decision_class=OWNERSHIP`; `risk_class=PROCESS`; `risk_severity=STRUCTURAL`; `canonical_map_mutation=true` |

## Exact Path State

| Path | Current nonterminal owner rows | Collision state | Implication |
|---|---|---|---|
| `MAP_System/graph/runner.py` | TASK-304, READY, owner `command-center` | One existing active owner; TASK-310 does not yet own it | TASK-310 cannot truthfully register or edit runner freshness until TASK-304 is dispositioned or the Command Center explicitly reserves the path for TASK-304 and keeps TASK-310 off it. |
| `MAP_System/templates/install/command-center-ui/app/server.py` | TASK-304, READY, owner `command-center`; TASK-306, CHANGES_REQUESTED, owner `claude-lab-nene` | Two existing active owners | This path is already conflicted before TASK-310. Adding TASK-310 would create a three-way collision unless TASK-304/TASK-306 are dispositioned first. |

No sanctioned `map_task.py` verb removes an output path from a nonterminal task in place. Available sanctioned lifecycle verbs include `retire`, `rework`, `reassign-owner`, `extend-attempts`, and `add-output-path`. Therefore, path ownership cannot be reconciled by silently editing task JSON. A Command Center disposition is required before any lifecycle mutation.

## Bounded Disposition Options

### Option A: Retire TASK-304, keep TASK-306 active, reserve only `graph/runner.py` for TASK-310

- Action after explicit Command Center approval: use `map-authority task retire TASK-304 --actor codex-lab-vumo --reason <approved reason>`.
- Result: `graph/runner.py` has no active owner and can be added to TASK-310 if TASK-310 needs runner output; `server.py` remains owned by TASK-306.
- Preserves TASK-306's CCL alignment lane and avoids mixing authority-freshness work with CCL deployment/security work.
- Leaves coordinator-enforcement work from TASK-304 to be recreated later as a smaller follow-up with clean output paths and fresh approval gates.
- Risk: retires a READY authority task that may still represent desired future work.

### Option B: Retire TASK-306, keep TASK-304 active

- Action after explicit Command Center approval: use `map-authority task retire TASK-306 --actor codex-lab-vumo --reason <approved reason>`.
- Result: `server.py` collision between TASK-304 and TASK-306 is reduced, but `graph/runner.py` and `server.py` still remain reserved by TASK-304.
- Does not unblock TASK-310 if TASK-310 must edit runner or Command Center server surfaces.
- Risk: discards a security-framed CCL alignment task that is already in CHANGES_REQUESTED and likely still important for Biggie/Smalls CCL parity.

### Option C: Retire both TASK-304 and TASK-306, let TASK-310 register needed freshness paths

- Action after explicit Command Center approval: retire both TASK-304 and TASK-306 with explicit supersession reasons.
- Result: both contested paths are clear for TASK-310 if needed.
- Risk: overbroad. It collapses distinct coordinator-enforcement and CCL-alignment work into the freshness lane, increasing scope and review burden for TASK-310.

### Option D: No lifecycle mutation; keep TASK-310 limited to existing output paths

- Action: do not alter TASK-304 or TASK-306.
- Result: no ownership mutation risk.
- Risk: TASK-310 cannot satisfy its full operator-facing freshness contract if runner output or Command Center-facing server health needs changes. This likely defers the same collision to implementation time.

## Recommendation

Recommend Option A with a narrow follow-on rule:

1. Explicitly retire TASK-304 as superseded/deferred by the recovery sequence before TASK-310 registers or edits `MAP_System/graph/runner.py`.
2. Keep TASK-306 active and owning `MAP_System/templates/install/command-center-ui/app/server.py`; do not let TASK-310 edit Command Center server code unless a later independent disposition also resolves TASK-306.
3. Allow TASK-310 to add `MAP_System/graph/runner.py` only if its implementation proves runner output must carry the authority freshness fields.
4. Treat any Command Center UI/server implementation for freshness as a separate follow-up after TASK-306 is approved, retired, or otherwise dispositioned by the Command Center.

This is the smallest disposition that unblocks truthful authority freshness without absorbing CCL deployment/security scope into TASK-310. It also preserves review history: TASK-306 remains accountable for CCL parity and security, TASK-310 remains accountable for authority freshness, and TASK-304's broad coordinator-enforcement scope is deferred rather than silently rewritten.

## Required Command Center Decision Before Mutation

No TASK-304 or TASK-306 lifecycle mutation has been performed. The required decision is:

- approve Option A;
- approve a different option above; or
- reject lifecycle disposition and keep TASK-310 inside its current output paths.

If a lifecycle mutation is approved, it must use only `map-authority task ...` sanctioned verbs and must be followed by an independent core-agent review of the after-state before TASK-310 registers or edits either contested path.
