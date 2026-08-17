# Task: hcom message relationships Wave 3

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `hcom-message-relationships-wave3`
- Risk: `MEDIUM`
- Goal: derive exact provider-local delivery/reply/thread/request/ack relationships from the body-free full-fidelity hcom metadata produced by PR #44, without task attribution, wait inference, or authority changes.

## Inputs and source of truth

- Inputs: root `AGENTS.md`, accepted PR #44 full-fidelity projection contract, `runtime/communication/hcom_lineage.py`, upstream hcom reply semantics where `reply_to_local` resolves the parent local event ID.
- Authoritative sources: exact hcom event metadata for provider-local communication relationships only. Canonical task/run/policy/review state remains elsewhere.
- Evidence labels: thread grouping, delivery, reply, request, and ack are communication evidence; no relationship grants task authority.
- Dependencies / preconditions: PR #44 is accepted from merge `main@70843f24a3fb55fe3999964639c448862d1d97fe`. Its configured-store identity check requires bare provider-local `event_id` uniqueness; `instance` is preserved metadata and is not an event-ID namespace. The current owner rebuild baseline is later accepted `main@eccdddaa37e42c93982bedf20d19e4f5096dbcff`, which also contains accepted PR #48 and must be preserved unchanged outside this four-file layer.

## Change boundary

- MAY CHANGE: `runtime/communication/message_lineage.py`, `tests/test_message_lineage.py`, this task file, `work/notes/2026-08-15-hcom-message-relationships.md`.
- MUST NOT CHANGE: hcom provider state, ordinary/full event reader behavior, task/run/session/policy/review authority, durable lineage/task stores, message bodies/transcripts, wait/pending state.
- MAY CHANGE IF NECESSARY: provider-local relationship projection only through explicit task amendment.
- OPERATOR APPROVAL REQUIRED: any later task/run attribution, wait semantics, or communication-driven authority behavior.

## Decision authority

- Owner may decide: deterministic body-free relationship projection, exact reply-link semantics, provider-field-presence validation, bounded-input coverage language, focused tests.
- Owner must escalate: task/run/request ownership joins, human intent inference, wait/resume semantics, durable storage, or using communication evidence as authority.

## Acceptance criteria

- [x] Exact `reply_to_local` creates a provider-local parent/child link only when #44 presence evidence says that field was observed.
- [x] A parent event outside the bounded input remains `PARENT_NOT_IN_INPUT`; no parent is guessed from sender/thread/time.
- [x] Same-thread messages without exact reply metadata do not count as responses.
- [x] Exact delivery edges preserve sender/recipient fan-out from `delivered_to`.
- [x] Thread groups use explicit thread metadata only when `field_presence.thread=true`.
- [x] Explicit `intent=request` events receive response/ack observations only when provider presence proves the intent field and exact children exist in input.
- [x] Absence of response/ack is `NOT_OBSERVED_IN_INPUT`, not global pending/wait state.
- [x] `coverage.field_presence` is required with exactly the #44 optional keys and boolean values.
- [x] presence=false requires the corresponding projected optional value to be `None`; contradictory values fail closed rather than being repaired or trusted.
- [x] presence=true preserves #44 semantics: `mentions`/`intent` require valid observed values, while explicit null remains allowed for `thread`, `reply_to`, and `reply_to_local` without inventing relationships.
- [x] Duplicate event IDs, self-replies, invalid intents, malformed presence evidence, and non-full/body-including inputs fail closed.
- [x] Input ordering does not change the derived projection.
- [x] Projection is explicitly non-authoritative and states task/run correlation and wait state are not included.
- [x] rebuild onto accepted #44 and the latest accepted current main using real merge ancestry while carrying only the four authorized #45 paths.
- [ ] fresh exact-head Runtime CI and independent exact-head re-review required after final rebuild.

## Verification and evidence

- Historical exact-head Runtime CI `31920742408` / #196 passed before the presence-evidence repair.
- Independent review on old head `803db6e404a7a5256acda1c4b90648afb8e17933` found one HIGH blocker: optional values were trusted even when `coverage.field_presence` said the provider had not observed them.
- Repaired feature head `b78de03a9e05fe19846d0c0629a55e54427fa587` validates exact presence-map shape/types and value/presence consistency before any relationship derivation; Runtime CI #346 / `31929065504` passed and SENTINEL review `4945554935` was CLEAN IN-LAYER on the historical stack.
- Accepted PR #44 entered main at `70843f24a3fb55fe3999964639c448862d1d97fe` and proves bare provider-local `event_id` uniqueness within the configured bounded read; `instance` does not qualify event identity.
- FOUNDRY first rebuilt #45 onto that accepted #44 main with merge head `27ad98c4b197b27267a9bbf9f768927a5a575a6b`; Runtime CI #474 / `31971734287` passed on that exact intermediate rebuild.
- While CI #474 was running, PR #48 merged and advanced accepted main to `eccdddaa37e42c93982bedf20d19e4f5096dbcff`. The owner therefore forward-synchronized again before review, using the newer accepted main as the tree baseline and preserving its #48 changes wholesale outside the four authorized #45 paths.
- Adversarial tests cover contradictory `intent`, `reply_to_local`, and `thread` values; missing/incomplete/non-boolean `field_presence`; and explicit-null provider fields that remain relationship-free.
- Evidence to preserve: old blocker review, repaired historical head, accepted #44 merge, both owner synchronization points, exact final base/head and four-file changed list, fresh full CI, final independent review.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: repository Python runtime; input is normalized body-free hcom metadata from #44.
- Ordered procedure: validate normalized event shape and body-free/full-read coverage → validate exact optional-field presence evidence → validate values according to observed presence → sort by event ID → build exact delivery/reply/thread edges → summarize explicit request children/acks → report bounded coverage.
- Failure branches: malformed/contradictory/duplicate/self-referential evidence fails closed; missing parent stays outside-input; absent ack stays not-observed-in-input.
- Rollback / recovery: revert isolated stacked PR; no mutation/storage exists.
- Security / privacy controls: inputs must preserve `message_body_included=false`; projection carries only IDs/routing/correlation metadata.
- External side effects: none.
- Effort limit: provider-local relationships only; no task correlation or explainable waits.
- Approved reference: accepted PR #44 full-fidelity lineage read output.

## Stop / escalate

Stop rather than guess if a reply would need same-thread/time/sender inference, task/run membership is needed, absent ack must become pending, message text is required, or #44 optional-field evidence cannot be made mechanically consistent.

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
- `field_presence` is provider evidence, not decorative metadata. An inconsistent mapper must be rejected rather than allowed to manufacture exact relationships.
- Provider-local event identity follows accepted #44: bare `event_id` within the configured store/read boundary; `instance` remains metadata only.
- This tranche advances future A4 without requiring the unsettled task/run lineage interface.

## Completion / handoff

- Completed in feature layer: provider-local relationship resolver, exact #44 optional-field-presence validation, adversarial tests.
- Completed in owner rebuild: genuine merge ancestry onto accepted #44, then forward-synchronization onto latest accepted `main@eccdddaa37e42c93982bedf20d19e4f5096dbcff` after #48 merged, while preserving only the four authorized #45 paths as the main-to-head delta.
- Not completed: fresh exact-head Runtime CI on the final synchronization, independent exact-head re-review, task/run/request attribution, communication-complete trace, explainable waits.
- Current blocker: fresh exact-head CI and independent review are required before returning the branch to SWITCHYARD.
- Next action if not DONE: run fresh Runtime CI on the final rebuilt exact head, obtain independent review without further branch mutation, then hand the unchanged reviewed head to SWITCHYARD for integration/merge gating.
