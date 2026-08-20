# Portable Deployment D2c — Chain Shovel Pilot Plan

## Purpose and evidence boundary

This is the execution plan for a future `D3` pilot against Chain Shovel. It
does not access, inspect, initialize, or modify Chain Shovel, and it does not
implement D1's installer or D2b's adapter. The only target facts available
here are **REPORTED** by the 2026-08-19 operator decision record: Chain Shovel
is the selected real external game-development project, and its bounded pilot
task is an ES-module-split plus logger bug. Its checkout path, source files,
symptoms, reproduction, expected behavior, test command, branch/CI policy,
and reviewer are all **UNKNOWN** until D3 preflight.

Portable v1 remains: committed target-local Markdown under `.maps/`, a sibling
MAPS_Lean clone, a thin adapter with explicit roots, stack-agnostic execution,
and best-effort review evidence rather than a mandated CI gate.

## D3 entry gates

Do not create or run D3 until every gate has an observed result.

1. **Authority and access.** The operator/target owner supplies access to a
   specific Chain Shovel Git worktree and authorizes the intended target-local
   writes, source change, target command execution, PR publication, and any
   eventual merge. Target selection alone does not supply these permissions.
2. **Two-root validation.** D3 records canonical, distinct Git roots for
   `MAPS_CLONE_ROOT` (the MAPS_Lean sibling) and `TARGET_REPO_ROOT` (Chain
   Shovel). A missing root, non-Git directory, nested path, equality, or
   symlink escape is a refusal before any write, as D1/D2b require.
3. **Target convention inspection.** D3 reads only the target paths necessary
   to determine whether `.maps/` is absent or already present. Existing files
   are authoritative and are never overwritten or normalized. Any incompatible
   existing target convention is an operator/target-owner decision, not an
   adapter migration.
4. **Task truth.** An owner inspects Chain Shovel enough to turn the reported
   bug into a target task with affected paths, reproducible current behavior,
   expected behavior, bounded non-goals, and a target-native verification
   command. Until then, it is not permissible to infer the module layout,
   logger API, package manager, test runner, or CI system.
5. **Review/merge path.** Before implementation, the target owner identifies
   an independent reviewer and the target's PR/merge policy. If no reviewer or
   permissible merge path exists, D3 is `BLOCKED`; it does not substitute
   MAPS_Lean review evidence or self-approval.

## Exact target-local convention paths

After gates 1–3 pass, D3 may use only these target-local files for the pilot:

| Target path | D3 use |
| --- | --- |
| `.maps/README.md` | Create only if missing from the D2a convention; describe the target-local portable-v1 boundary. |
| `.maps/roadmap.md` | Create only if missing; add one row for the pilot task and its owner/evidence/blocker. |
| `.maps/tasks/chain-shovel-es-module-logger.md` | Create only if missing from `target-task.md`; the target task truth for the reported bug. |
| `.maps/reviews/chain-shovel-es-module-logger-review-evidence.md` | Create only after independent review; record reviewer, reviewed revision, inspections, verification, verdict, findings, and residual risk. |
| `.maps/handoffs/<execution-date>-chain-shovel-es-module-logger.md` | Create only if D3 pauses or transfers ownership; `<execution-date>` is the actual D3 date, not a guessed date. |

The target adapter may create missing Markdown convention files only beneath
`TARGET_REPO_ROOT/.maps/` in an explicit preview/apply operation. It must
report, not overwrite, any existing path. `MAPS_CLONE_ROOT` remains read-only
for templates/guidance; MAPS_Lean `.maps/state/`, `work/`, `.hcom`, SQLite,
LangGraph, halt, trace, and lease state are neither target task truth nor D3
output.

## D3 task framing and roles

The target task's initial framing is:

> Repair the reported Chain Shovel ES-module-split + logger bug with the
> smallest target-native source/test change that demonstrates the agreed
> expected behavior. Exact affected modules, APIs, tests, and acceptance
> criteria are `UNKNOWN` until target preflight.

The D3 task must name one accountable implementer, one independent reviewer,
and the operator/target owner as authority for scope, external actions, and
merge. The implementer may choose a minimal patch only after the task records
the reproduction and target-native acceptance criteria. The implementer must
escalate scope expansion, dependency/lockfile/CI changes, security/privacy
issues, destructive actions, target-wide refactors, failed reproduction, or a
need to change the recorded task framing.

## Allowed and refused D3 actions

Before the D3 task is `READY`, only the preflight reads above are permitted.
Once it is AGI-ready and target authority is explicit, D3 may:

- use D2b's explicit-root, preview-first adapter interface to initialize only
  missing target `.maps/` Markdown files;
- inspect the target files required to reproduce and verify the bounded bug;
- make the minimal source/test changes authorized by the shaped target task;
- run only the named, target-approved verification commands; and
- create a target PR and merge only under the target's stated authority.

D3 must refuse or stop on ambiguous roots; any write outside target `.maps/`
before the source-change task is ready; overwriting target `.maps/` files;
arbitrary commands/modules; target-stack inference; MAPS runtime state or
hcom use; hidden dependency/package/CI/Git configuration changes; target
readiness claims from `runtime.smoke`; review approval/independence inference;
auto-merge; or external publication without the required authority.

## Execution and evidence sequence

1. Complete and record all D3 entry gates; if any result is unknown or fails,
   mark the target task `BLOCKED` with the concrete next action.
2. Run the D2b adapter's guidance/preview operation with the two canonical
   roots. Confirm every prospective target write is one of the listed `.maps/`
   paths and every MAPS-side read is allowlisted.
3. In explicit apply mode, initialize only missing target convention files.
   Inspect the resulting target task and roadmap fields; do not treat this as
   target readiness or a successful fix.
4. Shape `.maps/tasks/chain-shovel-es-module-logger.md` from the portable task
   template. It must contain the observed reproduction, exact source/test
   boundary, acceptance criteria, owner, authority, verification, and stop
   conditions. Only an `AGI READY`/`READY` task may move to implementation.
5. Implement the bounded target fix and run the target-native verification
   named in the task. Preserve command output, commit/revision, changed paths,
   and any limitation as target evidence.
6. Obtain an independent target reviewer. The reviewer reads the target task,
   patch, and evidence; reproduces relevant verification where feasible; and
   writes the named target review-evidence artifact with a reviewed revision
   and `APPROVED`, `CHANGES_REQUESTED`, or `BLOCKED` verdict. Best-effort does
   not permit self-approval or a missing revision reference.
7. If approved and the target's policy/authority permits, publish and merge
   the target PR. Record the merged revision/PR and target review artifact.
   If merge authority is absent, leave the task `READY_FOR_REVIEW` or
   `BLOCKED`, as evidence supports.
8. Report D3 findings back to MAPS_Lean only after the actual target evidence
   exists. This is a separate MAPS_Lean follow-up; do not create duplicate
   target task truth in `work/`.

## D3 completion and stop conditions

D3 proves the pilot only when an inspectable Chain Shovel PR/merge shows the
bounded task went through shaped task truth, implementation, target-native
verification, independent review evidence bound to the reviewed revision, and
the target's permitted merge path. A MAPS sibling `runtime.smoke` result,
static `.maps/` inspection, or a synthetic substitute does not prove the
pilot.

Stop and escalate to the operator/target owner if access, root validation,
reproduction, scope, target commands, review identity, CI/hosting policy, or
merge authority is missing; if the work needs an adapter/installer feature not
designed by D1/D2b; or if the bug requires material unrecorded scope. D3 then
remains `NOT STARTED` or becomes `BLOCKED` only within its separately created
target task. No external pilot is attempted by D2c.
