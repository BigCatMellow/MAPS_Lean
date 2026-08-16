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
  - PR #38 execution-lineage design/A0 findings
  - upstream hcom v0.7.25 source at `79ebde134c4d29b5ba64e5c9839a12bedb7ee125`
- Authoritative sources:
  - current merged MAPS runtime for local adapter behavior;
  - configured hcom executable for runtime transport evidence;
  - upstream hcom source only for capability/interface evidence, not MAPS authority.
- Evidence labels: provider communication metadata is evidence/correlation only; it is never task ownership, scope, policy, lease, review, or approval authority.
- Dependencies / preconditions: none; this tranche deliberately avoids the draft harness stack and leaves ordinary `HcomAdapter.read_events()` unchanged.

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
  - PR #20-#43 branches
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
- [x] Stable event ID, timestamp, instance/sender, and `delivered_to` are required and validated.
- [x] Optional `mentions`, `intent`, `thread`, `reply_to`, and `reply_to_local` are preserved only when present; absence is not defaulted/inferred.
- [x] Exact per-field presence is exposed so later correlation can distinguish absent from observed-null/default-like states.
- [x] Message text/body is never copied into the lineage projection.
- [x] Capability probe does not trust a version string; no-message state remains `UNKNOWN`.
- [x] Probe reports which optional correlation fields were actually observed rather than claiming universal support from version alone.
- [x] Malformed JSON, missing core metadata, invalid structured intent, and invalid filter inputs fail closed.
- [x] Module has no task-store/policy/approval dependency and grants no authority.

## Verification and evidence

- Verification:
  - `python -m unittest tests.test_hcom_lineage -v`
  - full PR Runtime stack CI
  - upstream source evidence that v0.7.25 exposes `events --full` and streamlining removes `delivered_to`/message `reply_to`.
- Evidence to preserve: upstream release/commit, exact branch head, focused/full CI, changed-file list.
- Review required: `INDEPENDENT_REVIEW`

## Conditional execution rules

- Environment / target: MAPS Python runtime plus an hcom CLI compatible with the proven full-read interface.
- Ordered procedure: invoke bounded full message query → parse JSONL → validate core metadata → preserve optional field presence → project metadata-only lineage evidence.
- Failure branches: no message events => capability `UNKNOWN`; malformed/full-field mismatch => protocol error; unsupported optional field shape => fail closed when present.
- Rollback / recovery: revert isolated PR; no storage/schema/provider mutation exists.
- Security / privacy controls: lineages omit message text and raw provider transcripts; only structured identifiers/correlation metadata are returned.
- External side effects: read-only hcom CLI invocation.
- Effort limit: full message read/capability proof only; no task attribution/waits/lineage database.
- Approved reference: hcom v0.7.25 source plus PR #38 design boundary.

## Stop / escalate

Stop rather than guess if:

- a provider field must be inferred from text/name/timestamps;
- hcom full output cannot prove stable identity/delivery metadata;
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
- This work supplies evidence needed by future A4; it does not perform request/thread/addressee-to-task correlation itself.

## Completion / handoff

- Completed: full-fidelity metadata reader/capability probe and adversarial fake-hcom tests.
- Not completed: task/run/request attribution, communication-complete trace, explainable waits, independent review.
- Current blocker: none for this isolated read path.
- Next action if not DONE: open draft PR against current main and run full Runtime CI.
