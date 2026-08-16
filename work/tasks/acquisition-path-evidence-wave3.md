# Task: acquisition-path evidence Wave 3

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `EVALUATION`
- Owner: `agent/acquisition-evidence-wave3`
- Risk: `MEDIUM`
- Goal: Validate externally observed operator/user acquisition-path evidence against explicit immutable refs so the Layer-3 benchmark can distinguish a real current delivery from stale, missing, unreachable, or unverified paths without creating publication authority or a general artifact registry.

## Trigger / source of truth

This capability is now justified by frozen Layer-3 scenario `E2E-L3-001`, which requires:

- real external/operator-visible delivery;
- all material acquisition paths checked against intended immutable revision/content or explicitly N/A;
- no stale visible artifact;
- a result the operator/user can actually consume;
- separate real provenance and external authority.

Inputs:

- root `AGENTS.md`;
- PR #40 frozen end-to-end benchmark protocol;
- PR #42 benchmark result validator at exact head `beeef987e25509136ff3de5b79263c984cc501da`;
- merged `scripts/install_maps.sh` only as an example of an operator-consumable install surface; it is preview-only unless `--apply` is explicit.

## Change boundary

MAY CHANGE:

- `runtime/acquisition_evidence.py`
- `tests/test_acquisition_evidence.py`
- `work/tasks/acquisition-path-evidence-wave3.md`
- `work/notes/2026-08-15-acquisition-path-evidence.md`

MUST NOT CHANGE:

- installer behavior;
- release/publishing behavior;
- network access;
- external systems;
- benchmark truth/protocol;
- task/review/policy authority;
- SQLite schema/state;
- any active lineage/communication/Skills/Environment branch.

## Core contract

The validator consumes:

1. an explicit release/acquisition manifest listing every in-scope path;
2. externally supplied observations from actual or controlled acquisition attempts.

Each manifest path declares:

- stable `path_id`;
- kind (`DOWNLOAD`, `INSTALL`, `ARCHIVE`, `OPERATOR_ARTIFACT`, `SERVICE`);
- exact expected immutable ref (`sha256:` or `git:`);
- whether the path is operator-visible;
- whether an explicit N/A decision is allowed.

Each observation declares:

- acquisition state (`OBSERVED`, `UNREACHABLE`, `UNKNOWN`, `NOT_APPLICABLE`);
- exact observed immutable ref when observed;
- acquisition evidence ref;
- usability state/evidence;
- explicit N/A decision ref when applicable.

The validator performs no acquisition itself.

## Derived properties

The report emits #42-compatible fragments for:

- `release.acquisition_paths_verified`;
- `release.no_stale_visible_artifact`;
- `operator.result_usable`.

Rules:

- exact observed ref match -> content PASS;
- immutable-ref mismatch -> acquisition FAIL and visible-stale FAIL for operator-visible paths;
- missing/UNKNOWN observation -> UNKNOWN, never PASS;
- unreachable path -> acquisition FAIL but stale-content state remains UNKNOWN unless stale content was actually observed;
- N/A only passes when manifest allows it and an explicit decision ref is supplied;
- usability does not erase content mismatch (a stale artifact may be usable and still fail release correctness).

## Provenance / authority boundary

A deterministic acquisition report can be an evidence reference, but this validator does **not** prove that the supplied acquisition evidence came from a real production path.

PR #42 still requires verified Layer-3 provenance for:

- real task;
- real run;
- real outcome;
- operator-visible result;
- existing external authority.

This validator also does not:

- download URLs;
- run installers;
- publish artifacts;
- verify DNS/network identity;
- create or mutate an artifact registry;
- authorize external effects;
- automatically pass the benchmark.

## Acceptance criteria

- [x] Manifest path set is explicit and duplicate-free.
- [x] Expected/observed refs are immutable `sha256:` or `git:` identities.
- [x] Missing observations preserve UNKNOWN.
- [x] Stale-but-usable artifacts fail content/stale checks without falsely failing usability.
- [x] Unreachable paths fail acquisition without inventing a stale-content claim.
- [x] N/A requires both manifest permission and an explicit decision ref.
- [x] Observation schema rejects contradictory evidence states.
- [x] Report identity is deterministic regardless of observation input order.
- [x] Report emits property fragments compatible with #42.
- [x] One valid E2E-L3-001 report cannot make the entire benchmark complete while other scenarios are missing.
- [x] Report explicitly denies acquisition/provenance/publication authority.
- [x] No network, shell, installer, publishing, or state mutation is added.

## Verification

Focused:

```text
python -m unittest tests.test_acquisition_evidence -v
```

Full PR Runtime CI is the repository validation gate.

Review required: `INDEPENDENT_REVIEW`.

## Stop / escalation

Stop rather than claim verification if:

- the real acquisition path has not actually been observed;
- the expected immutable identity is unavailable;
- a URL/install/service would require this module to perform external mutation or unsafe network fetching;
- real-world provenance cannot be independently established;
- scope would expand into publication, artifact registry, or release authority.

## Continuation

After acceptance:

1. use this report shape for a real authorized E2E-L3-001 sample;
2. preserve the real acquisition evidence outside this validator and bind it through accepted benchmark provenance adapters;
3. record the real post-completion outcome;
4. evaluate the full Layer-3 scenario through #42;
5. add direct acquisition tooling only if repeated evidence shows the pure observation/validation split is insufficient.
