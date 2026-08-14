<!-- hpom: file: artifacts/planning/phase1-architecture-decision-packet-2026-08-10.md -->
<!-- hpom: project: MAP -->
<!-- hpom: state_owner: claude-lab-sumi -->
<!-- hpom: status: DRAFT -->
<!-- hpom: last_verified: 2026-08-10 -->
<!-- hpom: confidence: MEDIUM -->

# Phase 1 architecture decision packet (P1.1)

Per `map-2-research-adoption-implementation-program-2026-08-09.md` §8
(P1.1). Recommended owner: Claude architecture lead (claude-lab-sumi,
Program Coordinator per DEC-042). Reviewer: Codex. Operator gate:
AUTHORITY/SCOPE approval tied to this exact document's hash (D1) — see
"Decision hash" at the bottom, computed after this draft is finalized
and before it is presented for approval.

This packet decides the ten points P1.1 requires, grounded in the
system as it actually exists today (verified against `map_authority.py`,
`map.db`'s live schema, and this session's own operational experience —
not a greenfield proposal).

## 1. `map-authority` is the sole production mutation seam

**Decision: yes, formalize what is already true in practice.**
`map_authority.py`'s `ALLOWED_TASK_VERBS` allowlist (`create, approve,
reject, rework, submit, release, recover-orphan, reassign-owner,
extend-attempts, retire, describe, amend-criteria, add-output-path,
show, log`) plus the top-level `claim`/`heartbeat`/`snapshot` operations
already form the only path this session ever successfully used to
mutate canonical task state — every attempt to write `map.db` directly
on Biggie fails closed (`authority_status()` requires the local
database be non-writable for mirror topology to validate). No second
writer exists today; this decision makes that structural fact an
explicit, reviewed contract rather than an emergent property of the
mirror check.

## 2. In-process command modules precede any Unix socket/daemon transport

**Decision: yes.** `map_authority.py` today is a CLI subprocess
dispatcher (`dispatch_authority()` shells out to `map_task.py` per
verb). Phase 2 (P2.1) proposes an in-process command layer
(commands/queries/lifecycle/authz/events/idempotency modules) callable
directly, without a new transport. A daemon/socket is out of scope
until Phase 2/3 evidence justifies it — this avoids installing a new
attack surface and a new failure mode (crash-while-holding-a-socket)
before the simpler in-process refactor is proven.

## 3. Current-state rows + transactional canonical events form the authority

**Decision: yes, with an explicit gap acknowledged.** Today `tasks`,
`events`, `approval_gates`, and related SQLite tables on Smalls *are*
the de facto authority — but writes are not currently transactional in
the sense P1.1/P2 mean (a single command committing both the state
mutation and its causal event atomically). `map_task.py` verbs mutate
`tasks` and append to `events` as separate steps today. P1.2/P2.1's
`map_events` table plus in-process command modules are what close this
gap. Decided here: the *target* authority model is current-state rows
+ transactional canonical events; the existing SQLite tables are the
right foundation to extend, not replace.

## 4. Task JSON, graph, current-state Markdown, and JSONL are projections

**Decision: yes, formalize what `MIRROR_FILES` already encodes.**
`workflow/task_graph.json`, `agents/status.json`,
`events/events.jsonl`, and `shared/current-state.md` are already
wholesale-overwritten on every mirror sync — i.e. already
non-authoritative, derived views. This session hit the sharp edge of
this directly: a fix applied to `events.jsonl` on the mirror (Biggie)
instead of the authority (Smalls) was silently reverted by the next
sync (REPAIR-0013). That incident *is* the argument for this decision:
projections must never be edited as if they were sources of truth, and
the fact that a manual mirror edit degraded silently — no error, no
warning — instead of failing loudly, is a P1.2 threat-model item (see
§9 below) and a P3.2 "deterministic projection contract" requirement,
not something P1 fixes on its own but must decide the direction of.

## 5. Workflow checkpoints and OTel are noncanonical

**Decision: yes.** No workflow/LangGraph checkpoint or trace span should
ever be treated as authoritative for task/authority state — they are
diagnostic only. This matters concretely for `MAP_System/graph/runner.py`
(the LangGraph pipeline already in use for `scan_role_bindings`,
`scan_helper_notes`, etc.): its outputs are advisory findings for a
human/coordinator to act on through the real authority seam (§1), never
a second path that mutates state directly. This is already how it's
built; this decision fixes it as a boundary that must not erode as the
pipeline grows in Phase 6.

## 6. Authenticated server context supplies actor identity

**Decision: yes, and this is presently the weakest link.** Today, actor
identity for `map-authority` commands is an `--actor`/`--reviewer` CLI
flag — a client-supplied string, not something the server independently
authenticates. Nothing today stops a client from typing
`--actor bigboss` or `--actor <any other agent's name>`. This session
relied entirely on process/protocol discipline (agents self-reporting
honestly, review routing conventions) rather than a technical
guarantee. Decided: this must change under the Phase 2 command layer —
actor identity must be derived from an authenticated server-side
session/context, never trusted from client input. This is the single
highest-priority item in this packet; §9's threat model (spoofing) is
this gap, named directly, not a hypothetical.

## 7. Optimistic `expected_version` + business `idempotency_key` semantics

**Decision: yes, adopt both, additively.** Neither exists today —
`tasks` has no version column, mutations are last-write-wins. Proposed:
add `tasks.runtime_version` (monotonic integer, bumped on every
mutating command), require commands that mutate to pass
`expected_version` and fail closed (not silently overwrite) on
mismatch. Separately, require an `idempotency_key` on business-meaning
commands (task submit/approve/release, not read verbs) so a client
retry after a lost response cannot double-apply a mutation — backed by
the proposed `command_dedup` table (P1.2). This directly targets a
real failure mode already named in this program's own history: this
session independently discovered and repaired data corruption
(REPAIR-0013) that traces back to a partial/interrupted append with no
idempotency guard at write time.

## 8. Operator approval object semantics

**Decision:** define an `operator_approvals` row (P1.2) as: `proposal_hash`
(sha256 of the exact artifact being approved — this packet's own
"Decision hash" below is the worked example), `scope` (what the
approval authorizes — task ID, decision ID, or a named gate), `expiry`
(approvals are not indefinite), `consumed_at`/single-use (an approval
is spent once acted on, not reusable), and `approver_identity` (must
resolve to the operator, not any core agent — see §6). This formalizes
a pattern already used informally and correctly in this program's own
decision log: DEC-039, DEC-041, and DEC-042 (this session's own
coordinator designation) all cite an operator quote/directive with a
date and are treated as single, scoped, non-reusable authorizations.
`approval_gates` (existing table) is a narrower, named-gate-only
precursor; `operator_approvals` generalizes it without breaking it.

## 9. Compatibility and rollback periods

**Decision:** every additive schema change (§7's `runtime_version`,
`command_dedup`, `operator_approvals`, `projection_cursors`) must be
purely additive — no column removed or repurposed, no existing verb's
behavior changed — for the duration of Phase 2's transactional-slice
pilot (through D2's crash-after-commit proof). Old readers (anything
not yet updated to check `expected_version`) must continue to function
unaware of the new columns. Rollback plan: because §1's mutation seam
is unchanged and §4's projections are already treated as disposable/
regenerable, rolling back is "stop writing the new columns, projections
regenerate from the unchanged core tables" — not a data-migration
event. This mirrors the same posture already used successfully in this
session's own REPAIR-0013/0014 pattern (evidence-preserving, additive,
reversible).

## 10. Per-project namespace decision

**Decision:** defer creating any new runtime-budget or telemetry
namespace scheme until Phase 8 (P8.2, budgets/circuit breakers) and
Phase 6 (P6.1, OTel spans) actually need one. Today's single
`project_id` column (`MAP-BOOTSTRAP-20260617` for the old recovery
epic, a separate ID for MAP Bedrock) is sufficient for Phase 1-3 scope.
Deciding this now, explicitly, prevents the namespace/budget machinery
from spreading ahead of the evidence P1's own "no production code
change yet depends on an unapproved external component" exit-gate
criterion requires.

## Threat model coverage (exit-gate requirement)

Per the plan's exit gate, this packet must show the threat model
covers: identity spoofing (§6 — the real, currently-open gap), stale
version (§7's `expected_version`), duplicate retries (§7's
`idempotency_key`/`command_dedup`), post-commit response loss (same
mechanism — a retried duplicate after a lost ack must be a no-op, not a
second mutation), partial projection (§4/§3 — projections regenerate
from authority, a partial regen must not be read as complete; ties to
P3.2's projection-cursor-recovery work), cross-host replay (Biggie is
read-only by construction per §1; a replayed old snapshot must be
rejected by `authority_revision` freshness/topology checks, which
already exist in `map_authority.py status`), malformed request
(existing `FORBIDDEN_TASK_FLAGS` check plus schema validation at the
new command layer), and approval substitution (§8's `proposal_hash` +
single-use `consumed_at` — an approval for one artifact cannot be
replayed against a different one).

## What this packet does not decide

Concrete SQL DDL, the exact `command_dedup` expiry window, and
migration scripting are P1.2's job (owner: Codex, per the plan), not
this packet's. This packet fixes the *shape* of the contract so P1.2
has a stable target.

## Decision hash

Computed after this file is finalized (sha256 of the file as approved).
Populate before presenting for D1 operator approval — the approval
must be tied to this exact hash, not a future edited version, per §8's
own single-use/scoped-artifact rule.

```
sha256: <TO BE COMPUTED AT APPROVAL TIME>
```
