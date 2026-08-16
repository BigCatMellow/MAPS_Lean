# Task: hcom full-fidelity lineage read Wave 3

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `hcom-lineage-read-wave3`
- Risk: `MEDIUM`
- Goal: add a bounded read-only hcom event path that preserves structured message lineage metadata omitted by ordinary streamlined event reads, without changing task/session authority or copying message bodies.

## Inputs and source of truth

- Inputs:
  - root `AGENTS.md`
  - merged `runtime/communication/hcom_adapter.py`
  - historical PR #38 execution-lineage design/A0 findings
  - upstream hcom v0.7.25 source at `79ebde134c4d29b5ba64e5c9839a12bedb7ee125`
- Authoritative sources:
  - current merged MAPS runtime for local adapter behavior;
  - configured hcom executable for runtime transport evidence;
  - upstream hcom source only for capability/interface evidence, not MAPS authority.
- Evidence labels: provider communication metadata is evidence/correlation only; it is never task ownership, scope, policy, lease, review, or approval authority.
- Dependencies / preconditions: none; this tranche leaves ordinary `HcomAdapter.read_events()` unchanged.

## Change boundary

- MAY CHANGE:
  - `runtime/communication/hcom_lineage.py`
  - `tests/test_hcom_lineage.py`
  - this task file
  - `work/notes/2026-08-15-hcom-lineage-read.md`
- MUST NOT CHANGE:
  - existing `HcomAdapter.read_events()` behavior
  - task/state/policy/review/harness authority
  - hcom provider state
  - message bodies copied into lineage output
  - communication-to-task attribution logic
- MAY CHANGE IF NECESSARY: full-read metadata validation only through explicit task amendment.
- OPERATOR APPROVAL REQUIRED: none for this read-only implementation; any later communication-driven authority behavior requires separate approval/design.

## Decision authority

- Owner may decide: narrow subclass/read API, metadata projection shape, fail-closed protocol validation, capability-probe semantics, focused tests.
- Owner must escalate: durable lineage storage, task/run attribution, session authority, external hcom mutation, inferred human intent, or message-body persistence.

## Acceptance criteria

- [x] Ordinary streamlined hcom event reads remain unchanged.
- [x] Full lineage read invokes `hcom events --full --type message` with bounded existing-style filters.
- [x] Positive event ID, timestamp, instance/sender, and `delivered_to` are required and validated.
- [x] A bounded lineage result is treated as exact only when provider-local `(instance, event_id)` identities are unique; duplicate identities fail closed in both ordinary full reads and capability probing.
- [x] Optional `mentions`, `intent`, `thread`, `reply_to`, and `reply_to_local` are preserved only when present; absence is not defaulted/inferred.
- [x] Exact per-field presence is exposed so later correlation can distinguish absent from observed-null/default-like states.
- [x] Message text/body is never copied into the lineage projection.
- [x] Capability probe does not trust a version string; no-message state remains `UNKNOWN`.
- [x] Probe reports which optional correlation fields were actually observed rather than claiming universal support from version alone.
- [x] Malformed JSON, missing core metadata, duplicate provider-local identities, invalid structured intent, and invalid filter inputs fail closed.
- [x] Module has no task-store/policy/approval dependency and grants no authority.
- [ ] synchronize the repaired four-file layer onto then-current accepted main before integration.
- [ ] fresh exact-head Runtime CI and independent exact-head re-review required after synchronization.

## Verification and evidence

- Historical exact-head Runtime CI `31920612330` / #192 passed before the duplicate-identity repair.
- Independent review on old head `4e10f8dadcd64e7b91fb8d608b92f268fde00821` found one HIGH blocker: capability claimed stable event identity without proving provider-local uniqueness.
- Repair adds `_require_unique_event_identities()` after projection in both `read_message_lineage()` and `probe_lineage_capability()`. It validates the narrow evidence identity `(instance, event_id)` and makes no global/project persistence claim.
- Fake-provider adversarial coverage returns two distinct rows with the same provider-local identity and proves both reader and probe raise `HcomLineageProtocolError` rather than returning ambiguous lineage or `SUPPORTED` capability.
- Verification required on repaired head:
  - focused `tests.test_hcom_lineage` through Runtime CI;
  - full Runtime stack CI;
  - final current-main synchronization and independent review.
- Evidence to preserve: upstream release/commit, historical blocker review, exact repaired head, focused/full CI, changed-file list, final independent review.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: MAPS Python runtime plus an hcom CLI compatible with the proven full-read interface.
- Ordered procedure: invoke bounded full message query → parse JSONL → validate core metadata → project metadata → validate provider-local identity uniqueness → preserve optional field presence → return metadata-only lineage evidence.
- Failure branches: no message events => capability `UNKNOWN`; malformed/full-field mismatch or duplicate local identity => protocol error; unsupported optional field shape => fail closed when present.
- Rollback / recovery: revert isolated PR; no storage/schema/provider mutation exists.
- Security / privacy controls: lineages omit message text and raw provider transcripts; only structured identifiers/correlation metadata are returned. Duplicate errors do not echo message body or provider transcript.
- External side effects: read-only hcom CLI invocation.
- Effort limit: full message read/capability proof only; no task attribution/waits/lineage database/provider namespace persistence.
- Approved reference: hcom v0.7.25 source plus accepted authority boundaries.

## Stop / escalate

Stop rather than guess if:

- a provider field must be inferred from text/name/timestamps;
- hcom full output cannot prove unambiguous provider-local identity/delivery metadata;
- task/run/request ownership attribution is required;
- durable communication storage appears necessary.

Escalate to: execution-lineage A4 integration task after accepted upstream interfaces are known.

## AGI readiness

- Fresh-Agent Test: `PASS`
- No-Guess Test: `PASS`
- Scope Test: `PASS`
- Authority Test: `PASS`
- Completion Test: `PASS`
- Failure Test: `PASS`
- Continuation Test: `PASS`

## Notes / decisions

- Upstream v0.7.25 writes `delivered_to` on every message, but `mentions`, `intent`, `thread`, `reply_to`, and `reply_to_local` are conditional. The reader therefore must not require optional keys on an ordinary message.
- `probe_lineage_capability()` proves actual configured behavior from returned events rather than trusting `hcom --version`.
- `(instance, event_id)` is only the narrow provider-local identity this read surface can validate. It is not a global provider/project identity and must not be promoted into one by later persistence work.
- This work supplies evidence needed by future A4; it does not perform request/thread/addressee-to-task correlation itself.

## Completion / handoff

- Completed in repair layer: full-fidelity metadata reader/capability probe, duplicate provider-local identity rejection, adversarial fake-hcom tests.
- Not completed: current-main synchronization, fresh exact-head Runtime CI after integration, independent exact-head re-review, task/run/request attribution, communication-complete trace, explainable waits.
- Current blocker: the repair agent cannot independently review its own change. Final integration should wait for the earlier serialized state lanes, then rebuild this exact four-file layer on accepted main.
- Next action if not DONE: verify repaired-head CI, later synchronize from accepted main, run fresh exact-head CI, and hand the immutable packet to an independent reviewer before merging.
