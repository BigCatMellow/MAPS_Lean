# Portable v1: read-only external target preflight

Status: ACTIVE — implementation candidate, review required
Owner: MAPS_L implementation operator
Parent: [Roadmap 06](../roadmaps/agent-harness-capabilities/06-portable-deployment.md), D1/D2b designs
Authority: User request (2026-11-04) to resume improving MAPS_L; **no target-repo write or pilot execution authorized**

## DONE
A small, reproducible, read-only command checks two explicitly supplied Git worktree roots, rejects unsafe or ambiguous roots, and reports the current portable target layout without changing either repository. Regression tests demonstrate refusal and non-mutation. An independently reviewed PR is required before promoting this capability to main.

## Scope
- Add `scripts/portable_target_preflight.py` as an explicitly invoked, read-only diagnostic.
- Validate canonical MAPS clone and external target Git roots; reject same/nested/symlinked roots.
- Inspect only target `.maps/` convention paths and MAPS portable template existence.
- Print clearly labeled JSON (inspection only; no assertion of target readiness or approval).
- Add focused tests with disposable Git repos.

## Non-goals
No `install_maps.sh` changes, `--apply`, target writes, imports/builds/tests of target code, DB/hcom access, auto-approval/merge, external pilot, or other roadmap status promotions.

## Acceptance / verification
- Exact-root and non-Git refusals are deterministic.
- Empty external Git repo is reported as uninitialized, not a failure or an automatically prepared project.
- Symlink/path escape under `.maps/` fails closed.
- Existing target convention files are never written or overwritten.
- Unit suite and GitHub CI pass. Independent review remains mandatory.
