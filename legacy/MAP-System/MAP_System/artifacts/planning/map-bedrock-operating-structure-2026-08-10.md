# MAP Bedrock Operating Structure

- status: reviewed, ready for owner/operator disposition (independent review
  by helper-bedrock-review-data found 2 REQUIRED findings, both revised and
  confirm-pass verified closed 2026-08-10 - see revision notes in Sec 2/7)
- date: 2026-08-10
- drafted_by: helper-bedrock-charter-tide (spawned by claude-lab-sumi)
- reviewed_by: helper-bedrock-review-data (spawned by claude-lab-sumi)
- requested_by: rotation-replacement-nizu-zalu (hcom request 20631), routed via
  `inbox/helpers/helper-bedrock-charter.md`
- source_packet: `handoffs/HANDOFF-bedrock-governance-to-sumi-2026-08-10.md`
- extends: `artifacts/planning/map-2-research-adoption-implementation-program-2026-08-09.md`
  (not deleted/overwritten; that file's sec 5.1/5.2/5.3 role and helper design
  is the base this reconciles against role-not-session-name terms; owner
  decides rename vs. formal supersession)
- naming: working name for this program going forward is `MAP Bedrock`. The
  2026-08-09 plan is not renamed by this file; only new artifacts should use
  the `MAP Bedrock` label until the owner accepts a formal rename.
- authority: this is a draft governance packet, not a decision. It carries no
  authority until reviewed and accepted through the normal decision process
  (`shared/decisions.md`). It does not authorize any lifecycle mutation.
- constraints carried forward: Smalls sole write authority; no direct Biggie
  `map.db` writes; independent review required; no self-approval; preserve
  evidence/durable records; terse over grammar.

## 1. Role-based responsibility charter

Roles bind to whoever currently holds them, not to a fixed session name. This
table maps the map-2 plan's sec 5.1 roles onto the source packet's expanded
role list — no role is dropped, none is renamed away from what's already live.

| Role | Map-2 sec 5.1 equivalent | Responsibility | Cannot do |
|---|---|---|---|
| Operator | Operator | Direction, policy, scope, destructive/external/dependency approval, cutover acceptance | Delegate operator authority by implication |
| Program Coordinator | Program coordinator | Cross-phase dependency ledger, routing, checkpoint enforcement, drift surfacing | Own delivery tasks or approve own deliverables (DEC-039) |
| Phase Owner | (new, sub-role of coordinator) | Owns one phase's gate and completion evidence roll-up | Skip the phase's combined exit gate |
| Task Owner | Implementation lead / Architecture-eval lead (per deliverable, sec 5.3) | Delivers one claimed task | Self-review, self-release, bypass Smalls |
| Independent Reviewer | Architecture/evaluation lead (functional review role) | Verifies task without self-approval | Approve own or coordinator's own work |
| Security Reviewer | (functional split of same role, sec 5.3) | Adversarial/security-framed pass on authz, network, write surfaces | Substitute for functional review; approve/release |
| Verifier | Deterministic verifier | Reruns exact evidence path, frozen test/fault matrices | Render final judgment or mutate canonical state |
| E/I Curator | (implicit in "any core agent" per SELF_REPAIR_SYSTEM.md) | Routes emergence/insight items to disposition (promote/link/reject) | Auto-promote without a core agent decision |
| Librarian | Librarian | Source maps, backlink/citation/evidence integrity, artifact findability | Promote research or mutate core truth directly |

Rules (from source packet, unchanged):

- Roles are stable; names are replaceable bindings.
- Every active role needs an explicit current binding or an explicit vacancy
  — no silent gaps.
- No task may depend on one specific name staying active.
- One accountable Task Owner + a different Independent Reviewer is required
  for every substantive deliverable (per `AGENTS.md` Core Protocol #9 and
  map-2 sec 5.3). Security Reviewer is a separate, additional pass for
  authority/authz/network/write-surface work, not a substitute reviewer.

## 2. Live role bindings (as of 2026-08-10)

| Role | Current binding | Evidence | Vacancy note |
|---|---|---|---|
| Operator | bigboss | `AGENTS.md` authority hierarchy | — |
| Program Coordinator | map-coordinator-hobo | DEC-039 (supersedes DEC-036's claude-lab-mimi) | — |
| Phase Owner (Phase 0) | vacant — no single owner; P0.1/P0.2/P0.3 have separate task owners per map-2 sec 7 | — | Assign explicitly before Phase 0 combined exit gate is claimed complete |
| Task Owner (per task) | bound at claim time via `db/claims.py` | `map_task.py status` / SQLite | Normal — this role rotates by design |
| Independent Reviewer (per task) | bound at review claim | task review artifact under `artifacts/reviews/` | Normal — rotates by design |
| Security Reviewer | no standing binding; spun up per authority/authz/network task (e.g. `helper-security-task321-hiro`, TASK-321) | `artifacts/reviews/task321_security_review.md` | Standby profile per map-2 sec 5.2, not vacant |
| Verifier | Pi fixed-roster identity (bounded); ad hoc human/agent rerun otherwise | map-2 sec 5.1 | No committed Pi binding right now — treat as vacant until a Pi instance is actually running |
| E/I Curator | vacant — no dedicated binding; curation currently happens ad hoc when a core agent notices `emergence_sentinel` `pending_candidates > 0` | `AGENTS.md` Core Protocol #11 | Known gap — see Sec. 7 |
| Librarian | helper-librarian (fixed-roster lane), most recently `helper-librarian-gare` | `inbox/helpers/helper-librarian.md` | Bounded read-only support, not a standing authority |

### Rotation-transfer rule

Revised 2026-08-10 after independent review (`helper-bedrock-review-data`)
found rules 1-6 below were unenforced policy prose — the same failure class
(rules existing but nothing checking them) that caused the DEC-036→039
churn this section is supposed to prevent. Two enforcement gaps closed:

1. A rotating agent must not silently drop a bound role. Before rotation
   finalizes, it records: open obligations, current blockers, and evidence
   pointers for every role it held.
2. Rotation transfer uses the existing continuity path (`context_rotation.py`
   prepare → ACK → remote transfer → finalize) as the primary mechanism.
2b. **Sanctioned fallback**: when that pipeline is itself blocked or
   structurally unavailable (DEC-039's actual precedent — the ACK/finalize
   path was blocked at the time), the operator may bind a role directly by
   durable decision entry (`shared/decisions.md`) plus an hcom broadcast.
   This is not an accidental workaround; it is rule 2's named alternate
   path, used exactly when rule 2 can't run.
3. On finalize, the successor identity inherits the role binding automatically
   for Task Owner / Independent Reviewer / Phase Owner *only if* the frozen
   snapshot explicitly names that binding (per `AGENTS.md`: "rotation never
   creates or elevates authority"). If the snapshot is silent, the role is
   vacant until the Program Coordinator or Operator rebinds it.
4. A superseded session does not resume a role after finalize — it hands off
   instead of taking the lane back (existing operator policy).
5. Program Coordinator rotation additionally requires an explicit DEC entry
   (per DEC-039 precedent), not just a snapshot transfer, because it is a
   cross-phase authority role.
6. **Enforcement, not habit**: rules 1/3/5 are checked by machine, not left to
   whoever remembers. `graph/runner.py` (already run at every core-agent
   startup per `AGENTS.md`) must report a `stale_role_bindings` field: for
   each Sec. 2 binding, resolve the bound identity against the live hcom
   roster (`hcom list --json`); any binding pointing to an identity absent
   from the roster is reported stale. This is the same pattern already used
   for `helpers_missing_model_tier` - it does not depend on the Program
   Coordinator noticing its own absence, which closes rule 5's circularity
   (previously: only the Coordinator role was positioned to catch a missed
   Coordinator-rotation DEC entry). Until this check exists in `runner.py`,
   treat Sec. 2's table as unverified as of its "as of" date, not current.
   Update the Sec. 2 table (or its successor ledger, Sec. 3) at the next
   checkpoint after any rotation regardless.

## 3. Canonical program ledger schema

One row per active gate-relevant unit of work. Fields:

| Field | Meaning | Source of truth |
|---|---|---|
| `phase` | Program phase number/name (map-2 sec 6.1, Phase 0–12) | map-2 plan |
| `gate` | Named exit gate or decision gate (map-2 sec 20 `D0`–`D7`, or phase exit gate) | map-2 plan |
| `task` | MAP task ID if promoted (`TASK-NNN`), else `none` (pre-promotion work) | `tasks/`, SQLite |
| `role` | Which charter role is accountable for this row right now | Sec. 2 binding table |
| `status` | One of: `not_started`, `in_progress`, `blocked`, `submitted`, `in_review`, `approved`, `released`, `deferred` | task/SQLite status where a task exists |
| `blocker` | Free-text blocker description, or `none` | must cite evidence path if non-`none` |
| `next_action` | Single next concrete step, owner-neutral phrasing | — |

This ledger does not replace `tasks/TASK-*.json`, SQLite, or
`workflow/task_graph.json` — it is a rollup view for phase/gate tracking, one
level above individual tasks. Store it at
`MAP_System/shared/bedrock-ledger.md` (create on first use) as a Markdown
table with the fields above, one row per phase/gate/task combination that is
currently active or blocked. Regenerate/update it at each checkpoint (Sec. 6),
not continuously — it is a durable snapshot, not a live projection.

Example row:

```text
phase: 0 | gate: combined P0.1+P0.2+P0.3 | task: TASK-321 | role: Task Owner
status: released | blocker: none
next_action: reconcile remaining Phase 0 baseline gaps (Sec. 7) before claiming Phase 0 exit gate met
```

## 4. Concise status protocol

- Default report shape, in order: **gate/phase — status — blocker (or none) —
  next_action.** One line where possible.
- No filler ("just checking in", restating the request back). State the
  fact.
- Use existing terse status vocabulary already in the codebase (`READY`,
  `CLAIMED`, `SUBMITTED`, `IN_REVIEW`, `CHANGES_REQUESTED`, `APPROVED`,
  `RELEASED`, `BLOCKED`) — do not invent parallel status words.
- Escalate to Operator only for: ownership ambiguity, novel irreversible
  action, or a gate listed in map-2 sec 20 (`D0`–`D7`). Routine fixes and
  coordination are handled without an operator message (existing operator
  delegation policy).
- Every checkpoint report (Sec. 6) uses the ledger fields verbatim: gate,
  blocker, owner, evidence, next action.

## 5. Task / event / E-I / triage logging and routing conventions

These reuse existing MAP_System mechanisms — nothing new is introduced.

### Task logging

- Claim/heartbeat/submit only through `db/claims.py` / `scripts/map_task.py`
  per `AGENTS.md` Task Claiming section. Never hand-edit task JSON to change
  lifecycle status.
- Every substantive deliverable needs one Task Owner + one different
  Independent Reviewer (Core Protocol #9); authority/authz/network/write work
  additionally needs a Security Reviewer pass (map-2 sec 3, sec 5.3).

### Event logging (`events/events.jsonl`)

- Append-only. Use the existing `type` vocabulary already present in the log
  (e.g. `PROGRESS`, `SUBMISSION`, `DECISION_RECORDED`, and other established
  types) — do not add a new `type` value without checking
  `scripts/validate_events.py` first.
- Every event should carry `task_id`, `sender`, `summary`, and
  `artifact_paths` where applicable; `actor`/`action`/`target` when the event
  represents a discrete transition.
- Do not rewrite or silently repair existing lines (see the known line-18,785
  NUL corruption — quarantine and repair through a reviewed procedure that
  preserves original bytes, per map-2 P0.2, never a silent rewrite).

### E-I (Emergence/Insight) logging

- Mechanism: `scripts/emergence_sentinel.py` (detection) and
  `scripts/map_emergence.py` (capture/promotion), writing under
  `MAP_System/emergence/{ideas,insights,synthesis,experiments,promotions}/`
  with ID prefixes `IDEA-####`, `INS-####`, `SYN-####`, `EXP-####`,
  `PROMO-####` (sequential, per-kind lock files already in `.locks/`).
- Routing: any core agent may capture a candidate; only a core agent may
  promote (no auto-promotion — `AGENTS.md` Core Protocol #11,
  `scripts/emergence_sentinel.py list`). The E/I Curator role (Sec. 1) is the
  accountable party for working the queue down, but capture itself stays
  everyone's job at startup per Core Protocol #11.
- Cadence: check `pending_candidates`/`scan_stale` at startup, every time
  `graph/runner.py` output is read — this is a standing habit, not optional
  follow-up (existing rule; this queue previously sat uncurated for 9 days).
- Severity/action framing for what gets captured reuses
  `SELF_REPAIR_SYSTEM.md`'s tiers (`COSMETIC`/`DRIFT`/`BLOCKING`/`STRUCTURAL`)
  where the finding is a repair rather than a new idea/insight.

### Triage

- Classify every incoming finding, request, or observation into exactly one
  of: `task` (promote/route to a MAP task), `blocker` (blocks an in-flight
  gate — log in the ledger, Sec. 3), `review item` (route to Independent or
  Security Reviewer), `decision` (route to `shared/decisions.md`), `E/I`
  (route per the E-I convention above), or `deferred note` (record, no
  immediate action — e.g. `shared/improvement-backlog.md`,
  `notes/command-center-later.md`).
- Unowned work and stale claims must be surfaced explicitly, not left
  ambiguous — this is what `scripts/advisory_monitor.py` already automates
  (orphaned/expired claims, aging `SUBMITTED`/`CHANGES_REQUESTED`, mirror
  drift); triage should check its output before assuming a fresh finding.
- A triage classification is not itself a lifecycle mutation — it's routing.
  The receiving lane (task claim, review claim, decision entry, E-I capture)
  still goes through its own normal gate.

## 6. Checkpoint cadence

- **Per-task**: heartbeat every ~15 min while `IN_PROGRESS` (existing lease
  rule); no separate Bedrock checkpoint needed at this grain.
- **Per-gate** (map-2 sec 20 `D0`–`D7`, or a phase's combined exit gate):
  Phase Owner (or Task Owner if no Phase Owner is bound) posts a ledger row
  update (Sec. 3) the moment the gate's evidence is ready for the accountable
  reviewer — not on a timer.
- **Rotation checkpoint**: mandatory at every rotation-transfer finalize (Sec.
  2 rule 1) — this is the minimum cadence and cannot be skipped.
- **Program Coordinator standing checkpoint**: at minimum, once per session
  start, the Program Coordinator (or whoever is filling that vacancy) scans
  the ledger for stale/blocked rows and surfaces them — this absorbs into the
  existing `current-state.md`/`advisory_monitor.py` startup habits rather than
  adding a new script.
- Accountable party for each checkpoint = whoever holds the role in Sec. 2 at
  that moment; if vacant, the Program Coordinator is accountable for flagging
  the vacancy rather than silently skipping the checkpoint.

## 7. Phase-0 gap reconciliation

Current state as of 2026-08-10 (per `artifacts/recovery/map2-phase0-trustworthy-baseline-2026-08-10.md`,
`tasks/TASK-321.json`, and this session's read of `shared/current-state.md`):

| Map-2 Phase 0 item | Status | Gap |
|---|---|---|
| P0.1 authority/rotation incident (TASK-316/317 chain, TASK-321 fix) | TASK-321 `RELEASED`, functional + security review + security rereview all `APPROVED` | Map-2's exit gate additionally requires "three consecutive scheduled sync cycles succeed under normal load" and "`map-authority status`/`route` agree" — not confirmed reconciled in this session's read. Needs an explicit check before Phase 0 is called done on this leg. |
| TASK-316/TASK-317 | both `APPROVED`, not yet `RELEASED` | Corrected 2026-08-10 (independent review caught the original citation was wrong: `HANDOFF-TASK-316-TASK-317-bume-blocked-on-deploy.md`'s own final section says deploy finished and the thread closed 2026-08-04, so "blocked on deploy" doesn't hold). No open-blocker event exists after their 2026-08-04 APPROVED events - they are simply part of the general 29-task release-ceremony backlog noted in `shared/current-state.md`, not individually blocked. |
| TASK-307/TASK-308 | both `APPROVED`, not yet `RELEASED` | New row (independent review flagged the omission): the register-agent/rotation-transfer gateway patch that this charter's Sec. 2 rule 2 leans on is itself unreleased. Same release-backlog bucket as TASK-316/317, not an independent blocker, but worth tracking since Sec. 2's primary rotation mechanism depends on it. |
| P0.2 durable validation debt (NUL corruption at events.jsonl:18,785, TASK-315 stale backlink, wikilink findings, helper capacity) | Per `helper-librarian.md` 2026-08-09 rerun: NUL corruption still unfixed, TASK-315 backlink still broken, 22 wikilink findings unchanged | These three items are explicitly still open per the most recent Librarian audit — not resolved by TASK-321. Phase 0's combined gate (map-2 sec 7) requires P0.1+P0.2+P0.3 together; P0.2 is not clear. |
| P0.3 lifecycle backlog inventory/disposition | Not confirmed complete in this session's read | Needs an explicit disposition record (released/deferred/superseded/blocked) for the listed APPROVED task set, if not already done elsewhere. |
| Program Coordinator designation (map-2 gate `D0`) | Bound: map-coordinator-hobo (DEC-039) | Satisfied. |
| E/I Curator role | No standing binding (Sec. 2) | Not a map-2 blocking gate, but a real gap this charter surfaces — recommend Operator either accepts ad hoc coverage (current de facto state) or assigns a binding. |
| Ledger (Sec. 3) | Does not yet exist as a file | Create `shared/bedrock-ledger.md` on first use; this charter defines the schema but does not populate it — that's a follow-up action, not done by this draft. |

**Bottom line**: Phase 0 is not through its combined exit gate. TASK-321
closes one authority-fallback bug inside P0.1 but does not, by itself, clear
the three-cycle sync proof, P0.2's validation debt, or a confirmed P0.3
disposition record. Treat "Phase 0 done" as false until those are separately
checked off with evidence, per map-2 sec 7's explicit no-partial-credit rule.

## 8. What this draft does not do

- Does not rename or edit `artifacts/planning/map-2-research-adoption-implementation-program-2026-08-09.md`.
- Does not create or claim any MAP task.
- Does not bind any role by fiat — Sec. 2 bindings are read from existing
  evidence, not assigned by this document.
- Does not populate `shared/bedrock-ledger.md` — schema only.
- Is not a decision; needs independent review and Operator acceptance (or a
  formal decision entry) before anything here is binding.
