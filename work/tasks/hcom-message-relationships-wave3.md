# Task: hcom message relationships Wave 3

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `hcom-message-relationships-wave3`
- Risk: `MEDIUM`
- Goal: derive exact provider-local delivery/reply/thread/request/ack relationships from the body-free full-fidelity hcom metadata produced by PR #44, without task attribution, wait inference, or authority changes.

## Inputs and source of truth

- Inputs:
  - root `AGENTS.md`
  - PR #44 exact head `4e10f8dadcd64e7b91fb8d608b92f268fde00821`
  - `runtime/communication/hcom_lineage.py`
  - upstream hcom reply semantics where `reply_to_local` resolves the parent local event ID
- Authoritative sources: exact hcom event metadata for provider-local communication relationships only. Canonical task/run/policy/review state remains elsewhere.
- Evidence labels: thread grouping, delivery, reply, request, and ack are communication evidence; no relationship grants task authority.
- Dependencies / preconditions: full-fidelity body-free hcom message projection from PR #44.

## Change boundary

- MAY CHANGE:
  - `runtime/communication/message_lineage.py`
  - `tests/test_message_lineage.py`
  - this task file
  - `work/notes/2026-08-15-hcom-message-relationships.md`
- MUST NOT CHANGE:
  - hcom provider state
  - ordinary/full event reader behavior
  - task/run/session/policy/review authority
  - durable lineage/task stores
  - message bodies/transcripts
  - wait/pending state
  - PR #20-#44 branches
- MAY CHANGE IF NECESSARY: provider-local relationship projection only through explicit task amendment.
- OPERATOR APPROVAL REQUIRED: any later task/run attribution, wait semantics, or communication-driven authority behavior.

## Decision authority

- Owner may decide: deterministic body-free relationship projection, exact reply-link semantics, bounded-input coverage language, focused tests.
- Owner must escalate: task/run/request ownership joins, human intent inference, wait/resume semantics, durable storage, or using communication evidence as authority.

## Acceptance criteria

- [x] Exact `reply_to_local` creates a provider-local parent/child link.
- [x] A parent event outside the bounded input remains `PARENT_NOT_IN_INPUT`; no parent is guessed from sender/thread/time.
- [x] Same-thread messages without exact reply metadata do not count as responses.
- [x] Exact delivery edges preserve sender/recipient fan-out from `delivered_to`.
- [x] Thread groups use explicit thread metadata only.
- [x] Explicit `intent=request` events receive response/ack observations only from exact children in the input.
- [x] Absence of response/ack is `NOT_OBSERVED_IN_INPUT`, not global pending/wait state.
- [x] Duplicate event IDs, self-replies, invalid intents, and non-full/body-including inputs fail closed.
- [x] Input ordering does not change the derived projection.
- [x] Projection is explicitly non-authoritative and states task/run correlation and wait state are not included.

## Verification and evidence

- Verification:
  - `python -m unittest tests.test_message_lineage -v`
  - full PR Runtime stack CI
- Evidence to preserve: exact stacked base/head, changed-file list, CI run.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: repository Python runtime; input is normalized body-free hcom metadata.
- Ordered procedure: validate normalized event shape → sort by stable event ID → build exact delivery/reply/thread edges → summarize explicit request children/acks → report bounded coverage.
- Failure branches: malformed/duplicate/self-referential evidence fails closed; missing parent stays outside-input; absent ack stays not-observed-in-input.
- Rollback / recovery: revert isolated stacked PR; no mutation/storage exists.
- Security / privacy controls: inputs must already preserve `message_body_included=false`; projection carries only IDs/routing/correlation metadata.
- External side effects: none.
- Effort limit: provider-local relationships only; no task correlation or explainable waits.
- Approved reference: PR #44 full-fidelity lineage read output.

## Stop / escalate

Stop rather than guess if:

- a reply would need to be inferred from same-thread/time/sender similarity;
- task/run membership is needed;
- an absent ack must be interpreted as a real pending obligation;
- message text would need to be inspected or persisted.

Escalate to: future A4 task/run communication-correlation tranche after A1 lineage is accepted.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- Request/ack observations are bounded-window facts. `NOT_OBSERVED_IN_INPUT` deliberately does not mean pending, unanswered globally, or waiting.
- Explicit thread membership is useful grouping evidence but cannot substitute for exact reply metadata.
- This tranche advances future A4 without requiring the still-unsettled task/run lineage interface.

## Completion / handoff

- Completed: provider-local relationship resolver and adversarial tests.
- Not completed: task/run/request attribution, communication-complete trace, explainable waits, independent review.
- Current blocker: none for this bounded stacked tranche.
- Next action if not DONE: open draft PR stacked on PR #44 and run full Runtime CI.
