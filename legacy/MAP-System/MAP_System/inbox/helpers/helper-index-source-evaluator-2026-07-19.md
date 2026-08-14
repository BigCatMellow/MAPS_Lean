# Helper Assignment - TASK-258 blinded source-index evaluator

- status: complete
- owner: codex-lab-kiri
- provider: codex
- created_at: 2026-07-19
- scope: evaluate nine fresh holdout questions using one compact packet at a time

## Start condition

Do not start until the owner records the independent author's truth event,
freezes the truth JSON, generates the index/packets with the already frozen
implementation, and changes this note to `status: active`.

Start condition satisfied:

- author truth: hcom event 7344
- truth frozen: 2026-07-19T18:43:47Z
- implementation SHA-256:
  `e595c4ba05e9adf8e271bceaceea5da3dd50d3aa831c18910ca764f961a6e5d9`
- packet set: S1 through S9 generated; evaluator receives them individually

## Evaluation protocol

1. Wait for the owner to name one packet file.
2. Read only that file.
3. Return one hcom `inform` response in the packet's required shape.
4. Select no more than two task IDs and two source paths.
5. `NO STRONG MATCH` is a valid and sometimes correct response.
6. Treat the packet's algorithm signal as advisory, not as truth.
7. Report confidence, ambiguity, and anything accessed outside the packet.
8. Wait for the next packet; do not pre-read it.

## Forbidden

- repository search;
- combined packet, JSON index, truth set, author note, regression, research
  summary, task files, or named evidence;
- following paths or opening a different packet;
- writes or task-state mutation;
- contacting the operator, author helper, or other evaluators.

## Stop

Stop after nine query responses and at most one owner-authorized confirmation
pass. The owner will preserve and score all reports.

## Completion record

- completed_at: 2026-07-19T18:51:45Z
- response events: S1 `7384`, S2 `7399`, S3 `7414`, S4 `7431`,
  S5 `7448`, S6 `7465`, S7 `7482`, S8 `7505`, S9 `7532`
- packet access: S1-S9 only, plus this required evaluator protocol note
- outside-packet access reported: none after the protocol note
- evaluator packet-context estimate: about 12,692 tokens total

| Query | Selected tasks | Selected evidence | Confidence |
|---|---|---|---|
| S1 | TASK-104 | research-artifact validator + focused tests | high |
| S2 | TASK-116 | graph runner + task-classification tests | high |
| S3 | TASK-130 | TASK-130 usage audit + task record | high |
| S4 | TASK-136 | export/import idea + ProjectUpdater validator | high |
| S5 | TASK-143 | task-mirror validator + focused tests | high |
| S6 | TASK-110, TASK-158 | human-interface guide + liveness reaper | medium |
| S7 | TASK-151, TASK-155 | kill-switch spec + durable-execution spec | high |
| S8 | TASK-153 | local-helper-lanes spec + task record | high |
| S9 | NO MATCH | none | high |
