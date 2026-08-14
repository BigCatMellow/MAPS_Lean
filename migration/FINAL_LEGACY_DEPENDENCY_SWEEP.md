# Final Legacy Dependency Sweep

- Date: 2026-08-14
- Scope: merged replacement runtime from PR #16 plus the final removal-readiness CI gate
- Status: **PASS**
- GitHub Actions evidence: run `31851301307`

## What is mechanically gated

`scripts/check_legacy_removal_readiness.py` scans active executable/configuration
surfaces:

```text
runtime/
tests/
scripts/
.github/
selected root build/dependency files
```

It fails when active code/config contains:

- Python imports from `legacy`;
- executable/path references to top-level `legacy/`;
- execution references to either curated migration snapshot;
- old `MAP_System` / `MultiAgentProject` runtime path markers; or
- active symlinks that target `legacy/`, escape the repository, or are broken.

Documentation is reported separately because historical/provenance discussion is
not an execution dependency. Negative test assertions such as
`assertNotIn("legacy/", source)` are also treated as proof rather than a dependency.

## Result

GitHub Actions run `31851301307` reported:

```text
active executable/config files scanned: 50
ACTIVE LEGACY DEPENDENCIES: PASS
- no active runtime/test/script/workflow import or path dependency found
```

The same checkout then passed:

```text
Python compile
Ruff fatal-error checks
Bandit medium/high security scan (with separately audited B608 exclusion)
pip dependency consistency
93/93 unit tests
SQLite/LangGraph disposable smoke to DONE
installer Bash syntax
installer preview execution
```

The smoke again verified:

```text
foreign_keys = 1
journal_mode = wal
busy_timeout = 5000
LangGraph route = wait_or_reconcile
final disposable task status = DONE
```

## Historical references

The sweep reports a set of Markdown/review/task/report files that still mention
`legacy/`. Those are intentionally historical, provenance, migration, negative-test,
or operator-safety references. They are not imported or executed by the active
runtime.

The curated snapshots remain under:

```text
migration/legacy-runtime-source/
migration/legacy-knowledge-source/
```

They are retained evidence and are also mechanically excluded from active runtime
execution dependencies.

## First gate correction

The first version of the checker failed on:

- `runtime/README.md` stating that runtime does **not** import `legacy/`; and
- negative assertions in `tests/test_smoke_install.py` proving the installer/smoke
  does not contain old paths.

Those were classifier false positives, not dependencies. The checker was narrowed
to executable/config surfaces while preserving AST import checks, active path
checks, symlink checks, and test scanning. The corrected gate then passed before
the rest of the full suite ran.

## Conclusion

The current active runtime, tests, installer/scripts, workflows, and dependency
configuration no longer require top-level `legacy/` or either preservation
snapshot to execute.

This closes the final dependency/reference gate. It does **not** itself authorize
deletion of `legacy/`; that remains a distinct explicit operator-approved action.
