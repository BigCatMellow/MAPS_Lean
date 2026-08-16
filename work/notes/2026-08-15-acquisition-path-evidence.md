# Acquisition-path evidence — Layer 3 delivery verification

Date: 2026-08-15/16  
Owner: `agent/acquisition-evidence-wave3`  
Status: evaluation/read-model evidence only

## Why this capability exists now

Legacy reconciliation recovered one narrow release lesson: fixing source is insufficient when an operator/user can still acquire a stale archive, download, install target, or other visible result.

That stayed trigger-gated until frozen benchmark scenario `E2E-L3-001` required a real operator-visible delivery with:

- every material acquisition path checked against intended immutable content or explicitly N/A;
- no stale visible artifact;
- a result the intended operator/user can actually consume;
- separate real task/run/outcome and external-authority provenance.

This tranche validates acquisition evidence. It does **not** create a publisher, downloader, installer runner, release manager, crawler, or artifact registry.

## Core separation

Keep three facts separate:

```text
intended immutable result
        ↓
real acquisition-path observation
        ↓
real-world provenance / task authority
```

This module handles only the middle comparison plus observation-shape validation.

It can answer:

> For every path declared in scope, does the supplied observation match the intended immutable revision/content, and is the observed result usable?

It cannot prove by itself that the observation came from production or that the external action was authorized. Those remain benchmark/task provenance questions.

## Manifest first

The validator requires an explicit manifest so one successful primary path cannot hide an unchecked secondary path.

```json
{
  "version": "maps-acquisition-paths-v1",
  "release_id": "release-42",
  "paths": [
    {
      "path_id": "download",
      "kind": "DOWNLOAD",
      "expected_ref": "sha256:...",
      "operator_visible": true,
      "allow_not_applicable": false
    }
  ]
}
```

Supported descriptive path kinds:

- `DOWNLOAD`
- `INSTALL`
- `ARCHIVE`
- `OPERATOR_ARTIFACT`
- `SERVICE`

The kind never causes MAPS to fetch or execute anything.

At least one path must be operator-visible.

## Immutable identity

Expected and observed identities are intentionally narrow:

```text
sha256:<64 hex>
git:<40 or 64 hex>
```

Mutable filenames, URLs, branches, `latest`, or release labels are not accepted as content identity.

A URL may exist in external acquisition evidence, but correctness is decided against immutable result identity.

## Observation states

### `OBSERVED`

Requires:

- exact observed immutable ref;
- acquisition evidence ref;
- usability state;
- usability evidence when usability is `VERIFIED` or `FAILED`.

The validator compares `observed_ref` to `expected_ref` mechanically.

### `UNREACHABLE`

Requires failure evidence and no observed content ref.

This is an acquisition failure, but it does **not** prove stale content exists. For an operator-visible unreachable path, stale-content state remains `UNKNOWN`.

```text
could not reach path
≠
stale artifact observed
```

### `UNKNOWN`

Cannot carry an observed immutable ref or acquisition/usability evidence. Missing observations also remain `UNKNOWN` at aggregate level.

Incomplete coverage is never PASS.

### `NOT_APPLICABLE`

Requires both:

1. manifest permission for N/A on that path; and
2. an explicit N/A decision evidence ref.

An allowed N/A decision may satisfy **acquisition-path coverage** for that declared path. It does not mechanically prove anything about whether a previously operator-visible archive/download/install surface has been withdrawn or is no longer exposing stale content.

Therefore for an operator-visible allowed-N/A path:

- acquisition coverage = `PASS`;
- stale-visible state = `UNKNOWN` unless separate structured evidence proves the surface is gone/non-visible/non-applicable;
- usability for that path = `NOT_APPLICABLE`.

This v1 observation shape does not carry separate withdrawal/non-visibility evidence, so allowed operator-visible N/A remains stale-visible `UNKNOWN`.

If a caller claims N/A where the manifest does not permit it:

- acquisition coverage = `FAIL`;
- stale-content state = `UNKNOWN` for an operator-visible path;
- usability = `UNKNOWN`, because an invalid scope claim is **not** proof that the artifact itself is unusable.

This preserves the distinction between coverage correctness, stale-visible safety, and artifact usability.

## Stale and usable are separate dimensions

A stale artifact may work perfectly:

```text
expected sha256:A
observed sha256:B
artifact opens/installs successfully
```

Correct result:

```text
release.acquisition_paths_verified = FAIL
release.no_stale_visible_artifact = FAIL
operator.result_usable = PASS
```

Usability cannot wash out wrong content.

Conversely, current content may still be unusable. Content correctness and usability remain independent benchmark properties.

## Missing coverage

If the manifest declares:

```text
download
archive
install
```

and only `download` is observed, the unchecked paths remain `UNKNOWN`.

The validator does not infer that one good path means the release is verified.

## Operator-visible stale check

For an observed operator-visible path:

- expected ref == observed ref -> PASS;
- mismatch -> FAIL.

For missing, UNKNOWN, unreachable, or allowed-N/A operator-visible paths without separate withdrawal/non-visibility proof, stale-content state is `UNKNOWN`.

An N/A decision ref is evidence that the path was declared out of scope for acquisition coverage. It is **not** evidence that an old visible surface disappeared.

## Usability evidence

Usability states:

- `VERIFIED`
- `FAILED`
- `UNKNOWN`
- `NOT_APPLICABLE`

`VERIFIED`/`FAILED` require evidence refs. `UNKNOWN`/N/A cannot claim them.

The validator intentionally does not define one universal usability procedure. A real task/benchmark must define what counts as consumable for the path:

- download: open/hash/parse or another accepted check;
- installer: bounded install/smoke check;
- operator artifact: actual open/consume/verify path;
- service: accepted endpoint/result check.

## Evidence identity

The acquisition report ID is content-derived from:

- normalized manifest;
- normalized observations sorted by path ID.

The human-readable `label` is **not** part of report identity. Two labels applied to the same manifest/observations resolve to the same report ID.

This prevents cosmetic naming from creating duplicate identities for one evidence fact.

The report separately records a deterministic manifest SHA-256.

## Benchmark bridge

The report emits the merged benchmark-result validator's compatible property fragments for:

```text
release.acquisition_paths_verified
release.no_stale_visible_artifact
operator.result_usable
```

PASS/FAIL fragments reference the deterministic acquisition report. UNKNOWN fragments carry no evidence refs, matching the benchmark-result contract.

A complete real `E2E-L3-001` result still separately requires:

- `external.authority_preserved` evidence;
- real task provenance;
- real run provenance;
- real outcome provenance;
- verified operator-visible result provenance;
- verified external-authority provenance;
- `outcome.real_observation_recorded`.

A synthetically constructed acquisition report therefore cannot satisfy Layer 3 merely because its internal hashes match.

## Why no network/install execution is included

Letting this validator fetch URLs or execute installers would silently add new authority/security questions:

- network permission;
- redirect trust;
- credential use;
- installer execution permission;
- external mutation/rate limits;
- private endpoints;
- path-specific smoke criteria.

None is needed to establish the evidence contract.

Preferred split:

```text
authorized real task/test procedure
        ↓
performs acquisition externally
        ↓
records sanitized evidence refs + immutable result identity
        ↓
pure validator checks completeness/correctness
```

Only repeated real benchmark evidence should justify a later acquisition tool.

## Relationship to `scripts/install_maps.sh`

The merged installer is conservative by default:

```text
preview only
--apply required for writes
```

That is a useful example of acquisition surface versus authority.

This validator never calls the installer. A separately authorized real Layer-3 task may execute an install/smoke workflow and supply its resulting evidence here.

## No artifact registry

The manifest describes one evaluation. It is not a global mutable release catalog.

There is no new durable truth for:

```text
current release
current URL
current archive
current install target
```

Those remain with their external owning systems. The report references exact evidence for the evaluated release/task.

## Key examples

### Fully verified

```text
download expected A, observed A, usable
archive  expected B, observed B, usable
```

Result:

```text
acquisition paths       PASS
no stale visible        PASS
operator result usable  PASS
```

Real-world provenance is still a separate requirement.

### Stale secondary artifact

```text
download expected A, observed A
archive  expected B, observed OLD
```

Even if both are usable:

```text
acquisition paths       FAIL
no stale visible        FAIL
operator result usable  PASS
```

### Allowed N/A without withdrawal proof

```text
archive NOT_APPLICABLE
not_applicable_decision_ref = decision:...
```

When the manifest explicitly permits N/A:

```text
acquisition paths       PASS
no stale visible        UNKNOWN
operator result usable  PASS if another operator-visible path is verified usable
```

The N/A decision does not prove the old archive/download/install surface was removed.

### Disallowed N/A

```text
acquisition paths       FAIL
no stale visible        UNKNOWN
operator result usable  UNKNOWN for that path
```

No artifact-usability conclusion is invented from a bad scope decision.

### Unreachable path

```text
acquisition paths       FAIL
no stale visible        UNKNOWN
operator result usable  FAILED or UNKNOWN according to actual usability evidence
```

### Missing observation

```text
acquisition paths       UNKNOWN
```

Relevant stale/usability aggregates also preserve UNKNOWN.

## Privacy

The validator consumes bounded identifiers and evidence refs. It does not ingest or persist:

- downloaded payload contents;
- credentials;
- arbitrary HTTP bodies;
- install logs;
- shell transcripts;
- private messages.

Those remain in their owning evidence systems, sanitized as appropriate.

## Tests locked into this tranche

The focused suite covers:

1. exact paths -> all three benchmark fragments PASS;
2. stale-but-usable -> content/stale FAIL, usability PASS;
3. missing observation -> UNKNOWN;
4. allowed operator-visible N/A with decision evidence -> acquisition coverage PASS but stale-visible UNKNOWN without withdrawal/non-visibility proof;
5. forbidden N/A -> acquisition FAIL while usability remains UNKNOWN;
6. unreachable path -> acquisition FAIL, stale UNKNOWN;
7. contradictory observation shapes fail closed;
8. unknown/duplicate observations fail closed;
9. report identity is stable across observation ordering and cosmetic labels;
10. explicit non-authority/provenance flags;
11. valid fragments fit the merged benchmark-result validator's `E2E-L3-001` property schema;
12. one valid Layer-3 scenario cannot complete the full benchmark while other required scenarios are absent.

## Real Layer-3 continuation

This branch does not execute `E2E-L3-001`.

A future real sample needs:

```text
real authorized task
real run
real external authority
real operator-visible result
real acquisition observations
this acquisition report
real post-completion outcome
```

Only the combined evidence can be evaluated as the actual Layer-3 scenario.

## Stop line

Do not widen this into network/install/publishing machinery simply because those systems are reachable.

Only real benchmark evidence that the observation/validation split is too costly or unreliable should trigger a separately authorized acquisition tool.
