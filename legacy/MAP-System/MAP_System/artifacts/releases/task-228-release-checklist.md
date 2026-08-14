# TASK-228 Release Checklist — Visible Non-Pi Local Ollama Advisory Lane

Date: 2026-07-18  
Release owner: codex-lab-lilo  
Independent reviewer: helper-librarian-rori
task_id: TASK-228

## Required release checks

- [x] Shared-file updates complete
- [x] Decisions recorded
- [x] Follow-up tasks created
- [x] Event log entry prepared
- [x] Emergence capture considered

No new governance decision or follow-up task is required by this bounded
repair. The release event is prepared by the release command. Existing
operator-friction evidence was considered in the closeout below.

## Scope released

- Health, runner, and Command Center inventory use loopback-only Ollama access.
- Only qwen3.5:4b is advertised as the current drilled, visible,
  draft-only advisory lane.
- The generic visible launcher is installed by the canonical installer.
- Pi remains outside this lane and has no operational authority.

## Verification

- PASS — focused local lane tests, including hostile inherited OLLAMA_HOST.
- PASS — focused local runner tests, including unapproved-model rejection.
- PASS — Python and shell syntax checks.
- PASS — isolated installer rendered an executable launcher and matched the
  template substitutions.
- PASS — task-mirror and shared-state validators.
- PASS — independent re-review at
  MAP_System/artifacts/reviews/task228-review-rori.md.
- KNOWN UNRELATED — the full MAP suite retains the pre-existing
  research-artifact filename validation failure documented in the test record;
  TASK-228 did not alter that artifact.

## Safety and operator closeout

- No model was downloaded or run by a hidden background process.
- No model gained task, review, approval, release, or decision authority.
- Operator-facing friction: no new candidate found. This task closes the
  already-observed friction of local model discovery/launch disagreeing with
  the actual local-only, visible lane; the repair is recorded in the TASK-228
  test and review artifacts.

## Release decision

Ready for MAP release after independent approval. The next reliability drill,
if any, must occur in an operator-visible terminal and be separately recorded;
this release does not infer three-run model reliability.
