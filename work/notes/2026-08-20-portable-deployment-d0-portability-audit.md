# Portable Deployment D0 Portability Audit

Audit target: the current install/smoke path used by `scripts/install_maps.sh` and `runtime.smoke`.

Current revision: `886090b` (`main` after PR #131).

## Summary

The install/smoke surface is not yet target-repo-portable. It is safe and preview-first for MAPS_Lean itself, but it assumes the script lives inside the same repository as the runtime package and writes project-local state under that repository root.

The mandatory smoke lifecycle is mostly Python-stdlib-portable at execution time because it uses a temporary SQLite task database. The import-time surface is broader: `runtime.smoke` imports `TaskStore`, and `TaskStore` imports the full state mixin stack, including environment, integrity, operational-learning, outcome, review, and lineage modules. Optional smoke checks add real external boundaries: LangGraph dependencies/checkpoint storage and hcom CLI execution.

## Classification Legend

- `Python-stdlib-portable`: can run from ordinary Python/stdlib primitives when passed explicit paths and when its package import is available.
- `path-relative to MAPS_Lean only`: resolves paths from the MAPS_Lean clone/script/package layout or defaults to MAPS_Lean-local state.
- `needs a real interface boundary before another repo could import it`: usable only after a target-repo adapter/API decides how paths, state, side effects, or optional dependencies cross the MAPS_Lean/target-repo boundary.

## Installer Shell Surface

| Surface | Classification | Evidence | D1/D2 impact |
| --- | --- | --- | --- |
| `scripts/install_maps.sh` root discovery | `path-relative to MAPS_Lean only` | `ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"` binds setup to the clone containing the script. | D1 must design explicit target selection instead of overloading script location. |
| `.venv`, `.maps/state`, `.hcom` creation | `path-relative to MAPS_Lean only` | The script writes under `$ROOT/.venv`, `$ROOT/.maps/state`, and `$ROOT/.hcom`. | D1 must specify which paths belong to MAPS_Lean versus the target repo. |
| dependency installation | `path-relative to MAPS_Lean only` | The script installs `"$ROOT/runtime/requirements.txt"`. | Sibling-clone design must keep MAPS_Lean runtime dependencies separate from target-project dependencies. |
| `HCOM_SOURCE` install | `needs a real interface boundary before another repo could import it` | Optional `--install-hcom` mutates user-local hcom installation via `uv tool` or `$HOME/.local/share/hcom-venv`. | Portable v1 should not make hcom installation a hidden side effect of targeting an external repo. |
| `--run-smoke` invocation | `path-relative to MAPS_Lean only` | Smoke command is executed from `$ROOT` using `$ROOT/.venv/bin/python -m runtime.smoke`. | D1 should distinguish "verify MAPS sibling clone works" from "verify target repo is prepared." |

## Mandatory `runtime.smoke` Surface

| Runtime surface | Classification | Evidence | D1/D2 impact |
| --- | --- | --- | --- |
| `runtime.smoke` argument/JSON wrapper | `Python-stdlib-portable` | Uses `argparse`, `json`, `pathlib`, `tempfile`, and plain exceptions. | Can be reused as a MAPS-side health check. |
| disposable smoke root | `Python-stdlib-portable` | `run_smoke()` uses `tempfile.TemporaryDirectory(prefix="maps-smoke-")`, not the live `.maps/state`. | Good pattern for D1 target-safety checks. |
| `TaskStore(task_db)` lifecycle exercise | `needs a real interface boundary before another repo could import it` | Smoke constructs `TaskStore(root / "maps.db")` and drives create/update/ready/claim/submit/review/DONE. | For v1 file-convention-only deployment, D2a should not depend on importing `TaskStore` inside the target repo. |
| `runtime.state.store.TaskStore` import surface | `needs a real interface boundary before another repo could import it` | `TaskStore` imports all state mixins: base, environment, execution, helper recovery lineage, integrity, observability, operational learning, outcomes, policy, readiness, review, review binding, run lineage, trace, and submission lineage. | A future adapter should expose narrow operations instead of treating `runtime.state` as a portable package boundary. |
| `runtime.state.base` | `Python-stdlib-portable` | Uses `sqlite3`, `Path`, and schema file next to the module. | Portable only when the MAPS package is available and the DB path is explicit. |
| `runtime.state.readiness` | `Python-stdlib-portable` | Uses repository-style `PurePosixPath` validation and task contract validation. | The path-validation vocabulary can inform D2a templates. |
| `runtime.state.integrity` and `integrity_scope` | `needs a real interface boundary before another repo could import it` | These methods require explicit `repo_root` and inspect paths relative to a repository. | D2b must decide whether optional checks run against the target repo from the sibling clone. |
| `runtime.state.environment` | `needs a real interface boundary before another repo could import it` | Imports `runtime.environment`, which exposes fingerprint/spec/validation behavior. | Environment checks should remain MAPS-side until a target adapter declares what environment evidence means for the target. |
| `runtime.state.observability` | `Python-stdlib-portable` | Redaction and status helpers are stdlib-based, but trace text references `.maps/state/*` evidence locations. | Useful as guidance, not as a target-repo contract by itself. |
| other `runtime.state.*` mixins | `Python-stdlib-portable` for local SQLite operations, `needs a real interface boundary` for target use | They are stdlib/SQLite modules, but collectively model MAPS_Lean task truth, not the chosen file-convention-only v1 target discipline. | Do not port the SQLite store wholesale for D2a. |

## Optional `--with-langgraph` Surface

| Runtime surface | Classification | Evidence | D1/D2 impact |
| --- | --- | --- | --- |
| `runtime.policy.HaltRecord` / `WorkerProfile` | `Python-stdlib-portable` | Dataclass/model logic is stdlib-based. | Can inform target status vocabulary, but does not need to run in target repo. |
| `runtime.policy.HaltStore` default path | `path-relative to MAPS_Lean only` | Defaults to `.maps/state/halt.json`. | D1 must avoid silently reading/writing MAPS_Lean halt state for a target repo. |
| `runtime.routing.langgraph_runtime.run_checkpointed_route` | `needs a real interface boundary before another repo could import it` | Defaults checkpoint DB to `.maps/state/langgraph-checkpoints.db`, creates parent dirs, and requires LangGraph packages from `runtime/requirements.txt`. | Treat as MAPS_Lean control-plane verification, not target-project setup. |
| `runtime.routing.router` | `Python-stdlib-portable` | Deterministic routing over task dictionaries and worker profiles. | Could be reused later only if D2a defines compatible task dictionaries. |

## Optional `--with-hcom` Surface

| Runtime surface | Classification | Evidence | D1/D2 impact |
| --- | --- | --- | --- |
| `runtime.communication.HcomAdapter` | `needs a real interface boundary before another repo could import it` | Wraps `hcom` via `subprocess.run(shell=False)` and sets `HCOM_DIR` to a resolved path. | D2b must specify whether hcom state is MAPS_Lean-local, target-local, or explicitly passed. |
| default hcom state | `path-relative to MAPS_Lean only` | Adapter default is `.hcom`; installer creates `$ROOT/.hcom`. | Targeting an external repo must not accidentally share MAPS_Lean `.hcom` state. |
| hcom CLI executable | `needs a real interface boundary before another repo could import it` | Requires a real `hcom` binary on PATH or configured executable. | Portable v1 should make hcom optional or explicitly preconditioned. |

## Findings for Next Phases

1. D1 should design two explicit roots, not one: the MAPS sibling clone root that owns `runtime/`, and the target repo root that may receive `.maps/` file-convention state.
2. D1 should treat `runtime.smoke --with-langgraph` as a MAPS sibling-clone health check. It does not prove a target repo is ready.
3. D2a should use file-convention templates and status vocabulary rather than `TaskStore` or SQLite lifecycle fields as the target repo's v1 authority.
4. D2b needs a narrow adapter boundary for optional MAPS-side helpers: path resolution, optional review-evidence checks, optional hcom use, and refusal to write MAPS_Lean's own `.maps/state` for target work.
5. The safest first portable-deployment implementation path is not "make `scripts/install_maps.sh` target-aware" directly. It is: define target file conventions (D2a), define the sibling adapter contract (D2b), then implement a minimal target operation that cannot confuse MAPS_Lean state with target-project state.

## Verification

- Read `scripts/install_maps.sh`, `runtime/smoke.py`, `runtime/state/store.py`, `runtime/routing/langgraph_runtime.py`, `runtime/communication/hcom_adapter.py`, `runtime/policy/halt.py`, and relevant package `__init__.py` files.
- Ran `python3 -m modulefinder runtime/smoke.py` to inspect broad import behavior.
- Ran an AST import listing over `runtime/*.py` to confirm the local package imports used by `runtime.smoke` and its optional paths.
