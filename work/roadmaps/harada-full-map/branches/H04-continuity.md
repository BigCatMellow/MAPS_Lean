# H04 — Reproducible environments, recovery, and isolation

- **Record:** candidate success-condition branch, not a new task or authority source
- **Parent:** [Full MAPS_L goal map](../README.md) · **Dependencies:** [cross-branch graph](../DEPENDENCIES.md)
- **Coverage:** [45 checklist rows + 35 master capability areas](../COVERAGE.md)
- **Children stored separately:** [H04.3 — safety of resumption](H04.3-recovery.md)
- **Evidence checkpoint:** 2026-10-20, main `69879cd0375f687c1df753fb5a4b83dda76b562e`; current runtime and task evidence supersedes status prose

## Required outcome
An interrupted or transferred task resumes **only** when project/revision/authority/environment/workspace are compatible, with immutable lineage, bounded retries and no duplicated external effects.

## Recursive conditions
- **H04.1 — Environment requirements are explicit.** Spec, fingerprints, relevant dependency inputs and validation tiers identify compatible/drifted/incompatible/unknown. **Proof:** source, dependencies and toolchain changes produce correct classification.
- **H04.2 — Bind the observed execution environment to runs.** Manifest/Run Record shows actual source revision, environment and effective workspace, never guesses from timestamps. **Proof:** cross-source joins survive a restart.
- **H04.3 — Safe resumption and decision logic.** [Open H04.3](H04.3-recovery.md): claim/lease, environment compatibility, idempotence, actual denial and repair.
- **H04.4 — Isolate writable work.** When concurrent agents write, each gets a unique worktree/clone and write boundary. **Proof:** two-worker conflicting edit test leaves no accidental shared-worktree mutation.
- **H04.5 — Context and handoff continuity.** A replacement gets only relevant verified facts plus unresolved risks; never inherits stale permissions from a stopped session.
- **H04.6 — Snapshot/rehydration is conditional.** No snapshot infrastructure absent measured failure or overhead of reconstructing from spec/fixtures; no data-loss/deletion shortcuts.

## Observed baseline
Checklist **E1–E4 DONE**, **E5–E6 IN PROGRESS**, **E7 NOT STARTED**. A real lease-expiry denial was documented, but this does **not** prove every recovery path checks every environment constraint. Worktree guard code exists; actual placement remains material. [Environment owner](../../agent-harness-capabilities/03-environment-and-reproducibility.md).

## Required next distinction
Separate **can report environment incompatibility** from **will prevent incompatible continuation**. Inspect actual production composition; run a narrow synthetic/tested incompatible-resume attempt before closing E5. Reconcile skipped versus unknown and whether the approved task requires strict fail-closed behavior.
