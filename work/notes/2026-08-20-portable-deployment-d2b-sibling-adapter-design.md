# Portable Deployment D2b — Sibling-Clone Adapter Design

## Purpose and boundary

Portable v1 uses a lightweight adapter committed in a target repository and a
separate sibling MAPS_Lean clone. This note defines the adapter's narrow
contract. It is not an adapter implementation, an installer change, a target
initialization, or authority to access Chain Shovel.

The adapter exists to make D2a's target-owned Markdown convention convenient
to use. It must not turn the sibling clone into a second target task store or
extend MAPS_Lean runtime control-plane state into the target.

## Explicit inputs and ownership

Every adapter invocation must require both canonical roots explicitly:

| Input | Meaning | Allowed authority |
| --- | --- | --- |
| `MAPS_CLONE_ROOT` | Canonical root of the sibling MAPS_Lean Git worktree. | Read-only access to portable templates, documented guidance, and an explicitly selected optional validation helper. |
| `TARGET_REPO_ROOT` | Canonical root of the target Git worktree containing the target-local adapter. | Creation of only missing, D2a-conformant Markdown files under `TARGET_REPO_ROOT/.maps/`; optional read-only inspection of those files. |

The two roots must be supplied as values, not inferred from the current
directory, the adapter's location, an environment default, or a prior run.
They must be different canonical Git-worktree roots. The adapter may discover
its own target-local entry point only after it has validated that the entry
point resolves inside `TARGET_REPO_ROOT`; that convenience must never replace
the explicit root inputs.

`MAPS_CLONE_ROOT` is the D1 `MAPS_ROOT` under an interface-specific name;
`TARGET_REPO_ROOT` is D1's `TARGET_ROOT`. D2b does not alter D1's planned
installer contract, including its preview-first and target-write limits.

## Allowed operations

A future adapter may expose a small allowlisted operation set. Each operation
must accept the two roots above, list its prospective paths before mutation,
and be explicit about whether it is preview or apply.

1. **Show portable guidance.** Read the sibling clone's D2a templates and
   linked playbook guidance and display their locations or rendered text. It
   does not copy or modify either repository.
2. **Initialize missing target convention files.** In explicit apply mode,
   create only missing D2a-conformant Markdown directories/files under:
   `TARGET_REPO_ROOT/.maps/{README.md,roadmap.md,tasks/,reviews/,handoffs/}`.
   Templates are read from `MAPS_CLONE_ROOT/templates/portable-deployment/`.
   Existing target files are authoritative and must be reported, never
   overwritten, regenerated, renamed, or normalized.
3. **Inspect target convention structure.** Read and report whether the D2a
   layout and required Markdown fields are present. A positive result means
   only that the inspected paths conform to the adapter's static contract.
4. **Optionally inspect target review evidence.** A separately named,
   read-only operation may examine a target `.maps/reviews/` artifact for the
   D2a-required fields and the named reviewed revision. It may reuse a
   MAPS-side helper only if that helper accepts explicit file/revision inputs
   and has no target-state or repository mutation path.

No operation may run by default merely because the adapter is invoked. In
particular, initialization is never implied by inspection or guidance.

## Write and execution boundaries

The adapter's only target write domain is `TARGET_REPO_ROOT/.maps/`, confined
to missing Markdown convention files. It must not write source code, tests,
dependency/lock files, CI workflows, Git configuration, hooks, credentials,
or user-home state. It must not write anywhere in `MAPS_CLONE_ROOT`.

The adapter may read only the selected templates/guidance in the sibling clone
and the target's `.maps/` files needed for its chosen allowlisted operation.
It does not need to import target code or inspect target source to establish
the v1 convention.

It must not execute target tests, builds, package managers, arbitrary shell
commands, target scripts, generated hooks, or arbitrary MAPS modules. Any
future command helper needs its own shaped implementation task and an
allowlisted command contract; passing a command/module/path supplied by the
caller is not a portable-v1 adapter feature.

## Required refusals

Before a write or optional check, the adapter must refuse without writing if:

- either root is missing, empty, non-canonical, not an existing directory, or
  not a Git worktree root;
- roots are equal, a supplied path is a nested subdirectory rather than the
  canonical worktree root, or a symlink/canonicalization result can escape the
  validated root;
- a requested target path falls outside canonical `TARGET_REPO_ROOT/.maps/`,
  a requested MAPS path falls outside its explicit read-only allowlist, or a
  write would cross from one root into the other;
- a target `.maps/` file already exists where initialization would write;
- requested behavior needs an unlisted command, module import, external
  network/service, credentials, target test/build, or target-stack inference;
- a review artifact lacks its reviewed revision, is stale relative to the
  revision named for review, or tries to infer reviewer identity,
  independence, approval, merge authority, or a status transition from its
  presence alone.

The adapter must report the failed validation and the relevant canonical roots
or path class, without claiming that no risk exists outside its inspected
scope.

## Control-plane and review limits

Portable v1 is D2a's Markdown convention, not an implicit MAPS runtime port.
The adapter must not create, read, write, or treat as target authority:

- `MAPS_CLONE_ROOT/.maps/state/`, any MAPS SQLite database, LangGraph
  checkpoint, halt record, trace, lease, or task state;
- `MAPS_CLONE_ROOT/work/`, MAPS review evidence, or `MAPS_CLONE_ROOT/.hcom/`;
- target SQLite, LangGraph, halt, hcom, or other hidden adapter state.

hcom remains optional and out of this adapter's v1 contract. The adapter must
not install hcom, mutate user-local hcom configuration, invoke hcom
implicitly, or share MAPS clone hcom state with the target.

Likewise, a successful `runtime.smoke` remains a sibling-clone health result
under D1. The adapter must not run it as target validation and must never
claim it proves target readiness, compatibility, test success, review
completion, or safety to mutate target code.

Review evidence remains best-effort under the recorded v1 decision. Optional
inspection may identify missing or stale evidence; it cannot approve a task,
attest reviewer independence, transition a task to `DONE`, satisfy a target
hosting provider's merge policy, or auto-merge anything.

## Future implementation acceptance checks

An implementation conforms to D2b only if tests or reproducible inspections
show that it:

- requires two distinct canonical Git roots and rejects ambiguity before any
  write;
- has no target write outside missing Markdown paths in target `.maps/` and
  no MAPS-clone write;
- uses an explicit, bounded operation rather than caller-supplied commands or
  modules;
- does not create or consume implicit SQLite, LangGraph, halt, hcom, or
  cross-repository task state;
- distinguishes static convention/review-evidence inspection from target
  readiness, execution, review approval, and merge authority; and
- preserves existing target `.maps/` files without overwrite.

## Non-goals and follow-on

D2b does not decide Chain Shovel's task, detailed target layout, CI/hosting,
or reviewer; those belong to D2c. It does not execute the pilot; that is D3.
It does not implement the adapter or D1's installer flag. Any implementation
must start with a new AGI-ready task that turns this contract into a limited
entry point with executable refusal and write-boundary tests.
