# Portable Deployment D1 - Installer Targeting Design

## Scope and sources

This note defines the planned explicit `--target-repo <path>` surface for a
successor or extension of `scripts/install_maps.sh`. It is a design contract,
not an implementation and not a change to the current installer.

It consumes the D0 audit and the D2a file convention:

- D0 establishes that the current script binds `ROOT` to the MAPS_Lean clone,
  and that MAPS runtime state, optional hcom state, and smoke verification must
  not be confused with target-repository state.
- D2a establishes that portable-v1 target state is committed, target-owned
  Markdown under `.maps/`; it is not a SQLite port or MAPS_Lean task store.
- The recorded v1 decisions require a sibling MAPS_Lean clone, a lightweight
  adapter in a later phase, stack-agnostic targets, and best-effort review
  discipline.

## Two explicit roots

The successor must use two separately named, canonical paths:

| Name | Source | Ownership and allowed state |
| --- | --- | --- |
| `MAPS_ROOT` | The directory containing the shipped MAPS installer/runtime, resolved from the script location. | MAPS_Lean's `.venv`, `runtime/requirements.txt`, optional `.hcom`, and any MAPS-side smoke artifacts. |
| `TARGET_ROOT` | The canonical Git worktree root selected by `--target-repo <path>`. | Only the portable target convention under `TARGET_ROOT/.maps/`. |

The existing no-target mode remains MAPS_Lean-local and uses only `MAPS_ROOT`.
Supplying `--target-repo` switches to target-aware mode; it must never silently
rebind `MAPS_ROOT`, or use `MAPS_ROOT/.maps/state` as the target's state.

## Command surface

The successor/extension retains the current flags and adds exactly one
target-selection flag:

```text
scripts/install_maps.sh [--apply] [--install-hcom] [--run-smoke]
                        [--target-repo <path>]
```

- `--target-repo <path>` is optional and takes exactly one non-empty path.
- The flag may occur once. A duplicate, missing value, unknown option, or
  positional argument is a usage error (exit `2`) before any write.
- Omitting the flag preserves the current MAPS_Lean-local behavior. It does
  not claim to prepare an external target.
- `--target-repo` does not select an alternate MAPS distribution, package
  manager, target-language runtime, or a target task. Those choices belong to
  later work or the target task contract.

## Target validation and refusal contract

Before displaying an apply plan or performing a target-aware action, the
successor must resolve and validate the supplied path in this order:

1. Resolve `<path>` to an existing directory without following an unresolved
   path component. If it is absent or not a directory, refuse with exit `2`.
2. Ask Git for the directory's worktree top level. If it is not inside a Git
   worktree, refuse with exit `2`; portable v1's committed `.maps/` convention
   depends on a target repository.
3. Canonicalize both that Git top level and `MAPS_ROOT`. The supplied path must
   name the Git top level exactly after canonicalization. A nested subdirectory
   is refused rather than silently redirecting writes to its parent.
4. Refuse if `TARGET_ROOT == MAPS_ROOT`. The portable target surface is for an
   external sibling project, not a disguised write to MAPS_Lean itself.
5. Print both canonical roots and the complete prospective write set before
   any mutation. A validation refusal must create no target or MAPS state.

An implementation may use platform-appropriate canonical-path primitives, but
must make these observable guarantees. It must not accept a merely plausible
directory, infer a target from the current working directory, or use a
symlink/nested-path ambiguity to redirect a write.

## Preview and apply semantics

Preview is the default in both modes. With `--target-repo`, preview must list
each target path under `TARGET_ROOT/.maps/` and each MAPS-side setup action
under `MAPS_ROOT`; it performs no writes.

`--apply --target-repo <path>` has two independent write domains:

1. **MAPS-side setup.** It may create or update only the MAPS clone's local
   environment needed to run MAPS-owned commands: `MAPS_ROOT/.venv` and its
   dependencies. This is never a target dependency install.
2. **Target convention initialization.** It may create only missing
   `TARGET_ROOT/.maps/` directories and D2a-conformant Markdown starter files.
   It must not overwrite any existing target `.maps/` file; report it as an
   existing file instead. The exact copy/render/validation mechanism is an
   adapter concern for D2b, so this D1 contract authorizes only the bounded
   target shape, not a particular implementation mechanism.

Target-aware apply must never create, read as target authority, or modify:

- `MAPS_ROOT/.maps/state`, `MAPS_ROOT/.hcom`, or MAPS SQLite/halts/checkpoints
  on behalf of the target;
- a target `.venv`, target dependency manifest, package lockfile, CI workflow,
  source file, or Git configuration;
- a user-local hcom installation unless the existing explicit `--install-hcom`
  flag is supplied and its user-local side effect is shown separately.

If any planned target write would fall outside canonical
`TARGET_ROOT/.maps/`, the command must refuse before writing. Existing target
state is authoritative: no target task, roadmap, handoff, or review evidence
may be regenerated or overwritten by targeting setup.

## Verification semantics

`--run-smoke` remains a MAPS sibling-clone health check. In target-aware mode
it runs with `MAPS_ROOT/.venv` from `MAPS_ROOT`, with the same optional
LangGraph/hcom additions as the existing script. Its success proves only that
the MAPS runtime setup can execute; it does not prove the target repository is
prepared, compatible, reviewed, or safe to mutate.

Target-aware setup may verify only static, non-mutating facts that D2a already
defines: the canonical target root and the intended `.maps/` paths. It must
not import target code, install target dependencies, execute target tests, or
infer a target stack. A future D2b adapter may add an explicit optional
validation command after its interface and evidence contract are designed.

`--install-hcom` stays opt-in and user-local. Targeting must neither make hcom
mandatory nor cause an implicit hcom invocation. A future adapter must pass
any hcom state path explicitly and must not share `MAPS_ROOT/.hcom` with the
target by default.

## Deliberate non-goals and follow-on boundary

D1 does not implement this flag, modify `scripts/install_maps.sh`, define the
sibling-clone adapter, create target files, port SQLite state, mandate CI, or
access any external target. In particular:

- D2b decides the adapter's actual target-local entry point and its template
  copy/render/optional-check interface.
- D2c decides the target/task selection gates, target layout instance,
  reviewer, and pilot proof.
- D3 executes the real external-project pilot only after D2a-D2c.

The implementation task that follows D2b must reproduce this design's
two-root, refusal, preview, and allowed-write contract with executable tests.

## Acceptance check for a future implementation

A future implementation satisfies D1's design only if all of the following
are demonstrable:

- `--target-repo` accepts one existing external Git worktree root and reports
  separate canonical `MAPS_ROOT` and `TARGET_ROOT` values.
- invalid, non-Git, nested, duplicate, and self-target paths fail before any
  write.
- preview lists only MAPS-side setup and target `.maps/` paths, with no writes.
- target-aware apply confines target writes to missing D2a-conformant
  `TARGET_ROOT/.maps/` paths and never overwrites target state.
- target-aware apply does not alter MAPS_Lean `.maps/state`, target source or
  dependency files, or user-local hcom state unless its explicit existing flag
  is supplied.
- a successful `--run-smoke` is reported as MAPS-clone health only, never as
  target-project validation.
