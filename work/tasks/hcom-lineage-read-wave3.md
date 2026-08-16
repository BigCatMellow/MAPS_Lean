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
- [x] A bounded lineage result is treated as exact only when bare provider-local `event_id` values are unique across the configured hcom read; duplicate IDs fail closed even when `instance` metadata differs.
- [x] Optional `mentions`, `intent`, `thread`, `reply_to`, and `reply_to_local` are preserved only when present; absence is not defaulted/inferred.
- [x] Exact per-field presence is exposed so later correlation can distinguish absent from observed-null/default-like states.
- [x] Message text/body is never copied into the lineage projection.
- [x] Capability probe does not trust a version string; no-message state remains `UNKNOWN`.
- [x] Probe reports which optional correlation fields were actually observed rather than claiming universal support from version alone.
- [x] Malformed JSON, missing core metadata, duplicate provider-local event IDs, invalid structured intent, and invalid filter inputs fail closed.
- [x] Module has no task-store/policy/approval dependency and grants no authority.
- [ ] focused/full Runtime CI passes on the repaired exact feature head.
- [ ] independent exact-head re-review confirms the returned identity blocker is closed.
- [ ] synchronize the repaired four-file layer onto then-current accepted main before integration.
- [ ] fresh integrated-head Runtime CI and independent exact-head review required after synchronization.

## Verification and evidence

- Historical exact-head Runtime CI `31920612330` / #192 passed before any duplicate-identity repair.
- Independent review on old head `4e10f8dadcd64e7b91fb8d608b92f268fde00821` found one HIGH blocker: capability claimed stable event identity without proving provider-local uniqueness.
- First repair head `4a11203f1faf0f8b5d199d6af2643ab7b7205764` added uniqueness checking but incorrectly used `(instance, event_id)` as the identity. Runtime CI #343 / `31928993044` passed, but SENTINEL correctly returned CHANGES REQUIRED.
- Pinned upstream hcom source shows one configured SQLite `events` table with bare `id INTEGER PRIMARY KEY AUTOINCREMENT`; `instance` is separate event metadata and is not an event-ID namespace.
- Current repair changes `_require_unique_event_identities()` to enforce uniqueness of bare local `event_id` across one bounded configured-provider read. It still makes no global/project/cross-store persistence claim.
- Fake-provider adversarial coverage now returns two distinct rows with the same bare event ID while retaining different `instance` values and proves both reader and probe raise `HcomLineageProtocolError` rather than returning ambiguous lineage or `SUPPORTED` capability.
- Verification required on repaired head:
  - focused `tests.test_hcom_lineage` through Runtime CI;
  - full Runtime stack CI;
  - independent exact-head re-review;
  - final current-main synchronization and integrated-head independent review.
- Evidence to preserve: upstream release/commit, both historical blocker reviews, exact repaired head, focused/full CI, changed-file list, final independent review.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: MAPS Python runtime plus an hcom CLI compatible with the proven full-read interface.
- Ordered procedure: invoke bounded full message query → parse JSONL → validate core metadata → project metadata → validate bare provider-local event-ID uniqueness → preserve optional field presence → return metadata-only lineage evidence.
- Failure branches: no message events => capability `UNKNOWN`; malformed/full-field mismatch or duplicate local event ID => protocol error; unsupported optional field shape => fail closed when present.
- Rollback / recovery: revert isolated PR; no storage/schema/provider mutation exists.
- Security / privacy controls: lineages omit message text and raw provider transcripts; only structured identifiers/correlation metadata are returned. Duplicate errors do not echo message body or provider transcript.
- External side effects: read-only hcom CLI invocation.
- Effort limit: full message read/capability proof only; no task attribution/waits/lineage database/provider namespace persistence.
- Approved reference: hcom v0.7.25 source plus accepted authority boundaries.

## Stop / escalate

Stop rather than guess if:

- a provider field must be inferred from text/name/timestamps;
- hcom full output cannot prove unambiguous provider-local event identity/delivery metadata;
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
- For the pinned configured hcom store, bare `event_id` is the local identity because all events share one SQLite table. `instance` remains useful event metadata but does not qualify that ID. Later persistence work must add whatever project/provider store context it needs rather than silently changing the local identity proved here.
- This work supplies evidence needed by future A4; it does not perform request/thread/addressee-to-task correlation itself.

## Completion / handoff

- Completed in current repair layer: full-fidelity metadata reader/capability probe, bare provider-local event-ID duplicate rejection, and an adversarial different-instance/same-ID fake-hcom test.
- Not completed: repaired-head Runtime CI, independent exact-head re-review, current-main synchronization, integrated-head CI/review, task/run/request attribution, communication-complete trace, explainable waits.
- Current blocker: exact repaired feature head must pass Runtime CI and receive independent re-review. FOUNDRY cannot independently review its own repair.
- Next action if not DONE: freeze code after final task/note evidence, require exact-head Runtime CI, hand to SENTINEL for re-review, then leave synchronization/integration to SWITCHYARD.
