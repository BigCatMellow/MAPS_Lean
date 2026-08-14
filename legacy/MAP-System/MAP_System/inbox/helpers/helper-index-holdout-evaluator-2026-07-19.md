# Helper Assignment — TASK-257 Blinded Holdout Evaluator

- owner: codex-lab-kiri
- helper: helper-index-eval-mono
- status: complete
- started_at: 2026-07-19T18:10:00Z
- completed_at: 2026-07-19T18:14:00Z
- authority: read-only evaluation; no repository, task, index, or policy writes
- visibility: hcom-managed WezTerm tab required

## Purpose

Evaluate eight independently authored historical-retrieval questions using
only one generated compact packet at a time. The evaluator must not see the
truth set, full index, other packet files, or primary sources.

## Protocol

1. Wait for the owner to name one packet file.
2. Read only that one file.
3. Return one hcom `inform` response in the packet's required format.
4. Select no more than two task IDs and two source paths.
5. Report confidence, ambiguity, and `no strong match` when warranted.
6. State whether anything outside the named packet was accessed.
7. Wait for the next packet; do not pre-read it.

The owner records per-query delivery/response times and does not reveal scores
until all eight responses are complete.

## Forbidden

- repository search;
- reading the combined packet, JSON index, frozen query/truth file, task files,
  or named evidence;
- following links or opening another query packet;
- writing files or changing task state;
- contacting the operator, author helper, or another evaluator.

## Stop

Stop after eight query responses and at most one owner-authorized confirmation
pass. The owner preserves and scores the reports in the TASK-257 experiment
artifact.

## Outcome

- response events: H1 7055, H2 7066, H3 7081, H4 7097, H5 7113,
  H6 7129, H7 7147, H8 7171.
- packet access: H1 through H8 individually, only after owner delivery.
- evaluator-reported packet context: 8,894 estimated tokens total.
- scope: passed; no combined packet, index, truth set, task/evidence source,
  repository search, or write was observed.
- confirmation pass: not used; task and source misses were clear from the
  frozen responses.
