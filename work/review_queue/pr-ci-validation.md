# Review packet: Pull-request CI validation

- Status: `QUEUED`
- PR: `#19`
- Change: `.github/workflows/runtime-stack-tests.yml`

## Intended behavior

Add the normal `pull_request` trigger to the existing Runtime stack tests while
keeping the existing push/manual triggers and test steps unchanged.

## Why

The runtime previously validated only `main` and a hard-coded list of branch
names. New review branches could therefore contain tests that never executed.
After this change, PR revisions automatically run the same legacy-dependency,
compile, Ruff, Bandit, dependency, unit-test, LangGraph-smoke, and installer
checks.

## Evidence

The change immediately enabled PR CI. Runs including `31886183653`,
`31886288275`, and `31886431884` completed successfully on subsequent review
tranches.

## Review questions

- Does `pull_request` introduce any unwanted write permission or deployment
  behavior? It should not: workflow permissions remain `contents: read`.
- Are the existing push/manual triggers still useful and unchanged?
- Should path filters be added later only if CI cost becomes material?
