# MAPS_L implementation and collision-state findings

Status: **historical/current-state preservation note; volatile facts must be rechecked live**.

## Why this note exists

The conversation included a live recovery of where MAPS_L stood in its feature roadmap and a specific collision check before starting Durable Project Memory work. Those findings matter for later sequencing, but they are **not durable authority** because PRs, branches, roadmap counts, and blockers can change quickly.

Use this note to understand the trajectory and why implementation was deferred. Re-check live GitHub before acting.

## Earlier snapshot — 2026-09-01

At the first live recovery during this discussion, MAPS_L had advanced far beyond the older Aug-21 handoff.

The trajectory check then current (#16) reported:

```text
16 DONE
13 IN PROGRESS
6 NOT STARTED
```

The key interpretation was that MAPS_L had moved from foundational subsystem construction into an **integration/proof stage**:

```text
build foundations
  ↓
build isolated mechanisms
  ↓
compose mechanisms
  ↓
add enforcement
  ↓
CURRENT POSITION AT THAT TIME
actually exercise them in production-like flows
  ↓
verify exit gates
  ↓
mark roadmap capabilities DONE
```

Major clusters identified in that snapshot:

### Enforced/autonomous execution

Already-built mechanisms included combinations of:

- canonical run enforcement;
- worktree binding;
- destructive/external guards;
- validation gates;
- memory provenance gating;
- environment evidence;
- recovery behavior.

Several roadmap rows were waiting on the **first real enforced production exposure**, not on invention of the underlying mechanisms.

### `maps flow` workflow layer

Already present or advancing:

- flow start;
- review-start;
- review-record;
- handoff;
- release-check design/implementation path.

This indicated the project was moving from low-level primitives toward a coherent operator workflow surface.

### Skills/procedural memory

The observed chain had progressed toward:

```text
discovery
→ security gate
→ lifecycle
→ task-policy intersection
→ context selection
→ Skill body loading
→ execution-resource manifest
→ on-demand resource loading
```

This was specifically relevant to the AI Context Compilation discussion because MAPS_L was already implementing progressive, need-based loading rather than dumping all Skill content into context.

### Security / operator identity

The SEC4 work was entering a later stage. The then-missing `authorized_operators` piece was being unblocked by the operator decision batch.

### Environment awareness

Environment evidence had moved from caller-supplied concepts toward flow-generated immutable evidence consumed by routing.

## Operator decision batch and later implementation

PR #243 recorded operator answers that unblocked several lanes, including:

- first `--enforce-canonical-run` pass authorization;
- `flow release-check` persistence/behavior decisions;
- opt-in `authorized_operators` registry design;
- environment-evidence-writer ratification.

During the first collision check, the active implementation branches were:

- PR #244 — `maps flow release-check`;
- PR #245 — authorized-operator registry;
- PR #246 — frozen Skill-selection evaluation;
- PR #243 — decision record.

The collision finding was specific:

- #244 and #245 both edited `runtime/cli.py`, `runtime/state/schema.sql`, `runtime/state/store.py`, and roadmap/checklist surfaces;
- a naive Project Memory implementation would likely want the same CLI/state seams;
- therefore the safe action was **shape/preserve the feature but do not start central runtime/CLI implementation yet**.

This is why issues #247/#248 and the current note packet were created before runtime work.

## Current snapshot recovered for this packet — 2026-09-03

Before creating this notes branch, live GitHub was checked again.

At that moment only two PRs were open:

- **#269** — repair/design for an hcom `--stopped --json` defect blocking `recovery-tick` / the enforced canonical-run exposure;
- **#271** — roadmap trajectory check #20.

PR #271 reported that the top-level capability scoreboard had moved to:

```text
17 DONE
12 IN PROGRESS
6 NOT STARTED
```

and specifically described **6.9 / S6 as DONE**, with the frozen Skill-selection evaluation gate now satisfied.

PR #271 also reported that the enforced canonical-run pass was no longer blocked by an unanswered operator decision; instead it had encountered a concrete hcom integration defect tracked/fixed in #269.

This confirms the earlier interpretation that MAPS_L is increasingly in a **real-exposure / integration / proof / repair** phase rather than a greenfield architecture phase.

## Collision decision for this packet

The note packet itself is intentionally isolated:

- branch: `notes/pilot-memory-context-review-20260903`;
- created from live `main` as recovered on 2026-09-03;
- documentation-only;
- no `runtime/`, schema, CLI, state, test, roadmap-status, or coordination-rule changes.

Therefore it should not materially collide with the active runtime repair or trajectory-check lanes.

## Re-entry rule

Do not turn any PR number, branch name, roadmap count, or blocker in this note into future implementation authority.

When Durable Project Memory or AI Context Compilation is picked up later:

1. recover open PRs and changed-file overlap live;
2. recover current `main` and current capability checklist/roadmap owner;
3. determine which prior blockers are now resolved or superseded;
4. identify the smallest current seam rather than implementing against the historical CLI/state layout described here;
5. preserve accepted `main` behavior as the baseline.

The lasting finding is the **sequencing method**: design/preserve ideas early, but do not build a central feature on top of actively moving shared seams.
