# Helper Assignment - TASK-260 blinded FTS holdout evaluator

- status: complete
- owner: codex-lab-kiri
- provider: codex
- created_at: 2026-07-19
- scope: evaluate eleven fresh holdout questions using one compact packet at a time

## Start condition

Do not start until the owner records the independent author's truth event,
freezes the truth JSON, generates packets from the already frozen retriever and
harness, and changes this note to `status: active`.

Frozen pre-author boundary:

- retriever SHA-256:
  `edd0b53ab6d9c480360e19f4d14d667f459fcaa3155748a9bd96e741b70cca27`
- holdout harness SHA-256:
  `65219824dc3c2d5f62b77923a0bd9cd3f6c21d3222ee9db9f3e5bcff723a83ff`

Start condition satisfied:

- author truth: hcom event `7726`
- truth frozen: 2026-07-19T19:27:55Z
- packet set: F1-F8 and N1-N3 generated from the frozen retriever/harness;
  evaluator receives them individually

## Evaluation protocol

1. Wait for the owner to name one packet file.
2. Read only that file.
3. Return one hcom `inform` response in the required shape.
4. Select no more than two task IDs and three source paths.
5. `NO MATCH` is valid and sometimes correct.
6. Treat the algorithm signal as advisory, not truth.
7. Report confidence, ambiguity, and anything accessed outside the packet.
8. Wait for the next packet; do not pre-read it.

## Forbidden

- repository search;
- combined packet, generated JSON, truth set, author note, development metrics,
  research, task files, or named evidence;
- following paths or opening a different packet;
- writes or task-state mutation;
- contacting the operator, author helper, or other evaluators.

## Stop

Stop after eleven query responses and one total packet-context estimate. The
owner will preserve and score all responses, update this note, and stop the
visible helper.

## Completion record

- completed_at: 2026-07-19T19:34:11Z
- response events: F1 `7753`, F2 `7766`, F3 `7779`, F4 `7792`, F5
  `7805`, F6 `7818`, F7 `7831`, F8 `7844`, N1 `7857`, N2 `7870`,
  N3 `7883`
- packet access: F1-F8 and N1-N3 only, plus this required protocol note
- outside-packet access reported: protocol note only
- evaluator packet-context estimate: about 16,012 tokens total

| Query | Selected tasks | Exact expected sources selected | Confidence |
|---|---|---:|---|
| F1 | TASK-214, TASK-212 | 2/3 | high |
| F2 | TASK-213, TASK-220 | 2/2 | high |
| F3 | TASK-221 | 2/3 | high |
| F4 | TASK-228 | 2/3 | high |
| F5 | TASK-231 | 1/2 | high |
| F6 | TASK-237, TASK-240 | 2/3 | high |
| F7 | TASK-249 | 2/2 | high |
| F8 | TASK-239, TASK-233 | 2/2 | high |
| N1 | NO MATCH | n/a | high |
| N2 | NO MATCH | n/a | high |
| N3 | NO MATCH | n/a | high |

Strict totals:

- task labels: 12 correct among 12 selections; 12/12 recall
- exact sources: 15 correct among 20 selections; 15/20 recall
- compound task sets: 4/4 complete
- no-match decisions: 3/3 correct
