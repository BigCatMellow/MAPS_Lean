# Legacy Knowledge Source Snapshot — Second Pass

This directory preserves the second tranche identified by the full legacy
knowledge audit before the top-level `legacy/` directory is removed.

It is **migration/reference source only**.

Active MAPS code MUST NOT import or execute modules from this directory.
Promote behavior by extracting the invariant, implementing the smallest Lean
version under `runtime/`, porting the relevant regression test, and verifying
it there.

## Why these files were selected

They contain behavior not fully protected by the first runtime extraction:

- run-time freezing of task/context/scope (`run_manifest.py`);
- criterion-level implementer evidence claims kept separate from reviewer
  verdicts (`submission_records.py`);
- continuity-aware reviewer independence (`review_routing.py`);
- disposable replay/read-model behavior (`session_replay.py`);
- intake/decomposition examples and tests, marked rewrite-required;
- structural context/decision/event/research/review validators;
- conflict-freeze and repo-lock examples, marked rewrite-required;
- optional cost-governance behavior;
- measured audits/experiments explaining why important rules exist.

## Rewrite-required sources

Do not promote these unchanged:

- `scripts/intake_request.py` — regex classification is reference behavior,
  not authority.
- `scripts/flag_conflict.py` — preserve conflict semantics; redesign record ID
  allocation/state integration for Lean.
- `scripts/git_operation_lock.py` — preserve the mutual-exclusion invariant;
  use a proven atomic locking primitive in Lean.
- `scripts/cost_governance.py` — optional until autonomous paid dispatch makes
  it materially useful.

## Evidence-only files

Selected audits and experiments are preserved because they contain measured or
incident-backed conclusions. They do not themselves authorize implementation.

See:

- `../LEGACY_KNOWLEDGE_AUDIT.md`
- `../LEGACY_PROMOTION_LEDGER.md`
- `../LEGACY_REMOVAL_CHECKLIST.md`
