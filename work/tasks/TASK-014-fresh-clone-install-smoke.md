# Task: Add fresh-clone installer and smoke path

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `implementation-agent`
- Risk: `MEDIUM`
- Goal: Add a reversible fresh-clone setup script and self-contained smoke checks for the active Lean runtime without reading or executing `legacy/` or migration snapshots.

## Inputs and source of truth

- Inputs: `docs/CONTROL_PLANE_SETUP.md`, active `runtime/**`, preserved installer safety lessons.
- Authoritative sources: active runtime requirements and current setup docs.
- Dependencies: stacked active runtime through bounded helpers.

## Acceptance criteria

- [x] Installer defaults to preview/dry-run; writes only with explicit `--apply`.
- [x] Installer creates project `.venv`, local state directories, installs active runtime requirements, and can optionally install hcom separately.
- [x] Installer never automates credentials/API keys and does not require WezTerm.
- [x] Installer/smoke path contains no execution dependency on `legacy/` or `migration/`.
- [x] Smoke test creates disposable SQLite state and proves AGI READY/claim/review lifecycle without touching live project DB.
- [x] Smoke optionally checks LangGraph checkpoint isolation when dependency exists.
- [x] Smoke checks hcom binary/version when requested without changing sessions.
- [x] Static/install tests are included.

## Verification and evidence

- GitHub Actions run `31845946112` on Python 3.12: `64 tests`, `64 PASS`, with `PYTHONWARNINGS=error::ResourceWarning`.
- Configured LangGraph integration passed with `langgraph 1.2.11` and `langgraph-checkpoint-sqlite 3.1.1` installed by the workflow.
- Disposable smoke passed: SQLite task lifecycle reached `DONE`; `foreign_keys=1`; `journal_mode=wal`; `busy_timeout=5000`; LangGraph returned `wait_or_reconcile` and created a separate checkpoint DB.
- Installer passed `bash -n scripts/install_maps.sh` and preview execution. Preview printed project-local `.maps/state`, `.hcom`, `.venv`, pip requirements install, and performed no writes.
- First CI run exposed incorrect test/smoke use of `MutationResult.data`; fixed to the actual `.task` contract and propagated down the stacked branches before final green run.
- Review required: `INDEPENDENT_REVIEW` — intentionally deferred by operator instruction.

## Stop / escalate

Stop if installation would overwrite tracked files, automate credentials, or require destructive system changes.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Completion / handoff

- Completed: preview-first Bash installer, separate optional hcom installation, disposable runtime smoke, static/install tests, fresh-install docs, and full-stack GitHub Actions verification.
- Not completed: independent review and merge of stacked PRs #9 onward; Windows native installer remains manual setup rather than this Bash helper.
- Last verified result: full active stack `64/64 PASS`; disposable LangGraph/SQLite smoke PASS; installer syntax/preview PASS in GitHub Actions run `31845946112`.
- Exact next action: preserve reviews for later as requested; finish documentation/removal-gate bookkeeping and open the final stacked draft PR.
