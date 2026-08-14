# Task: Add fresh-clone installer and smoke path

- Status: `READY`
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

- [ ] Installer defaults to preview/dry-run; writes only with explicit `--apply`.
- [ ] Installer creates project `.venv`, local state directories, installs active runtime requirements, and can optionally install hcom separately.
- [ ] Installer never automates credentials/API keys and does not require WezTerm.
- [ ] Installer/smoke path contains no execution dependency on `legacy/` or `migration/`.
- [ ] Smoke test creates disposable SQLite state and proves AGI READY/claim/review lifecycle without touching live project DB.
- [ ] Smoke optionally checks LangGraph checkpoint isolation when dependency exists.
- [ ] Smoke checks hcom binary/version when requested without changing sessions.
- [ ] Static/install tests are included.

## Verification and evidence

- Verification: shell static checks + Python smoke/unit tests on configured clone.
- Review required: `INDEPENDENT_REVIEW`

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

- Completed: task shaped.
- Not completed: installer/smoke/tests/docs.
- Next action: implement safe preview-first installer.
