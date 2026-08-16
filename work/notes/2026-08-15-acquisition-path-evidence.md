# Acquisition-path evidence — Layer 3 delivery verification

Date: 2026-08-15/16
Owner: `agent/acquisition-evidence-wave3`
Status: evaluation/read-model evidence only

## Why this capability is now justified

Earlier legacy reconciliation recovered one narrow release lesson: for operator-visible work, fixing source is not enough if the user/operator can still reach a stale archive, install path, or download.

That idea stayed deliberately trigger-gated because MAPS did not yet have a real Layer-3 benchmark requiring it.

The frozen `E2E-L3-001` scenario now creates that trigger. It requires a real external/operator-visible delivery whose actual acquisition paths are checked against the intended immutable content and whose result can actually be consumed through the real path.

This tranche therefore validates acquisition evidence. It does not create a publisher, crawler, release manager, or artifact registry.

## Core separation

Three facts must stay distinct:

```text
intended immutable result
        ↓
real acquisition-path observation
        ↓
real-world provenance / task authority
```

This module handles only the middle comparison plus evidence-shape validation.

It can answer:

> For every path the caller says is in scope, did the supplied observation show the intended immutable revision/content, and was the observed result usable?

It cannot answer on its own:

> Did that observation really come from production?

or:

> Was the external action authorized?

Those remain benchmark/task provenance questions.

## Manifest: define the paths before judging observations

The validator requires an explicit manifest so a successful primary path cannot hide an unchecked secondary path.

Conceptually:

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
    },
    {
      "path_id": "archive",
      "kind": "ARCHIVE",
      "expected_ref": "sha256:...",
      "operator_visible": true,
      "allow_not_applicable": true
    }
  ]
}
```

Supported path kinds are deliberately descriptive:

- `DOWNLOAD`
- `INSTALL`
- `ARCHIVE`
- `OPERATOR_ARTIFACT`
- `SERVICE`

The kind does not cause MAPS to execute or fetch anything.

At least one path must be operator-visible, because the capability exists to verify a real user/operator-facing result rather than merely internal build products.

## Immutable result identity

Expected and observed identities are intentionally narrow:

```text
sha256:<64 hex>
git:<40 or 64 hex>
```

A mutable filename, URL, branch name, "latest", or release label is not accepted as content identity.

A URL may be part of external acquisition evidence elsewhere, but correctness is decided against immutable content/revision identity, not URL spelling.

## Observation states

### OBSERVED

The external process says the path was reached and supplies:

- exact observed immutable ref;
- acquisition evidence reference;
- usability state;
- usability evidence when usability is asserted VERIFIED/FAILED.

The validator compares `observed_ref` with `expected_ref` mechanically.

### UNREACHABLE

The path could not be acquired and carries failure evidence.

This is an acquisition failure.

It does **not** prove stale content exists, because nothing was retrieved. The stale-visible-artifact dimension therefore remains `UNKNOWN` unless stale content was actually observed.

This distinction prevents:

```text
could not reach path
→ therefore stale artifact exists
```

### UNKNOWN

No usable observation exists.

UNKNOWN cannot carry an observed immutable ref or acquisition/usability evidence. That prevents a caller from claiming content identity while simultaneously disclaiming observation quality.

Missing observations are treated the same way at aggregate level: incomplete coverage remains `UNKNOWN`, never PASS.

### NOT_APPLICABLE

A path may be explicitly N/A only when:

1. the frozen manifest allows N/A for that path; and
2. an explicit decision evidence reference is supplied.

This turns N/A into an auditable scope decision instead of letting callers silently omit inconvenient paths.

## Stale versus usable are separate dimensions

One of the most important failure modes is a stale artifact that still works perfectly.

Example:

```text
expected sha256:A
observed sha256:B
install succeeds
```

Correct result:

```text
release.acquisition_paths_verified = FAIL
release.no_stale_visible_artifact = FAIL
operator.result_usable = PASS
```

Usability cannot wash out wrong content.

Likewise, a current artifact can be unusable:

```text
expected == observed
installer fails
```

That should preserve content correctness while failing usability.

Keeping these dimensions separate is why the Layer-3 benchmark does not use a single weighted score.

## Missing coverage is not success

Suppose the manifest declares:

```text
download
archive
install
```

and only `download` was checked.

The validator must not say "one good path passed, therefore release verified." The unchecked paths stay `UNKNOWN`, making aggregate acquisition/stale/usability evidence incomplete as appropriate.

This is the main reason the path manifest is separate from observations.

## Operator-visible stale check

`release.no_stale_visible_artifact` concerns operator/user-visible paths.

For an observed operator-visible path:

- expected ref == observed ref -> PASS;
- mismatch -> FAIL.

For an unreachable or missing operator-visible path, stale content is `UNKNOWN`, not automatically PASS or FAIL.

An explicitly permitted N/A path is not counted as a stale visible artifact, because the manifest/decision evidence says that path is outside the current acquisition surface.

## Usability

Usability is also externally observed evidence.

States:

- `VERIFIED`
- `FAILED`
- `UNKNOWN`
- `NOT_APPLICABLE`

VERIFIED/FAILED require an evidence ref. UNKNOWN/N/A cannot claim one.

The validator does not define one universal usability test because path kinds differ:

- a download might require successful open/hash/parse;
- an installer might require a bounded smoke run;
- an operator artifact might require successful consumption/opening;
- a service might require an accepted endpoint/result check.

The real task/benchmark must define what makes the path consumable. This layer only ensures the evidence state is explicit and internally consistent.

## Report identity

The report ID is deterministic over:

- normalized manifest;
- normalized observations sorted by path ID;
- label.

Input observation order therefore does not change evidence identity.

The report also records a deterministic manifest SHA-256.

This makes it possible for later benchmark/run evidence to reference one exact acquisition evaluation without turning the report into an artifact registry.

## Benchmark bridge

The report emits three #42-compatible property fragments:

```text
release.acquisition_paths_verified
release.no_stale_visible_artifact
operator.result_usable
```

PASS/FAIL fragments reference the deterministic acquisition report. UNKNOWN fragments carry no evidence refs, matching #42's evidence contract.

That bridge is deliberately limited. A complete `E2E-L3-001` result still separately needs:

- `external.authority_preserved` evidence;
- real task provenance;
- real run provenance;
- real outcome provenance;
- verified operator-visible result provenance;
- verified external-authority provenance;
- `outcome.real_observation_recorded`.

So a synthetically constructed acquisition report cannot satisfy Layer 3 merely because its internal hashes match.

## Why the validator performs no download/install itself

It would be easy to make this module accept a URL and fetch it. That would silently expand an evidence validator into an external-action tool and create several new authority/security questions:

- Is network access authorized?
- Are redirects trusted?
- May an installer execute?
- Which credentials may be used?
- Does fetching mutate rate limits or external systems?
- Is the target private/sensitive?
- Who decides the correct install smoke test?

None of that is necessary to establish the evidence contract.

The safer split is:

```text
authorized real task/test procedure
        ↓
performs acquisition externally
        ↓
records sanitized observation refs + immutable result identity
        ↓
pure validator checks completeness/correctness
```

If repeated real benchmark work later shows that this split causes unacceptable friction, a separate acquisition tool can be designed with its own explicit authority and network/execution controls.

## Relationship to the current installer

Merged `scripts/install_maps.sh` is conservative by default:

```text
preview only
--apply required for writes
```

That is a useful example of the distinction between an acquisition surface and authorization.

This validator does not call the installer. A real Layer-3 test could, under an independently authorized task, execute an installation or preview/smoke workflow and provide the resulting acquisition/usability evidence to this validator.

The installer itself does not become publication authority merely because it is an operator-visible path.

## No artifact registry

The manifest is an input to one evaluation, not a global mutable release catalog.

There is no durable table of:

```text
current release
current download URL
current archive
current install target
```

Those would duplicate truths owned by external release systems and create synchronization problems.

The acquisition report should reference the exact external evidence available for the evaluated release/task and then remain append-only evidence wherever the accepted benchmark/run-record mechanism stores it.

## Example: fully verified paths

```text
manifest:
  download -> sha256:A
  archive  -> sha256:B

observations:
  download OBSERVED sha256:A + usability VERIFIED
  archive  OBSERVED sha256:B + usability VERIFIED
```

Result:

```text
acquisition paths       PASS
no stale visible        PASS
operator result usable  PASS
```

This still does not prove the observations were real production observations. Benchmark provenance must do that separately.

## Example: stale secondary archive

```text
download -> expected A, observed A
archive  -> expected B, observed OLD
```

Even if both open successfully:

```text
acquisition paths       FAIL
no stale visible        FAIL
operator result usable  PASS
```

This is exactly the class of defect the capability exists to expose.

## Example: explicitly removed archive path

If the manifest marks archive N/A-capable and the real release decision says the archive path is not part of this delivery:

```text
archive NOT_APPLICABLE
not_applicable_decision_ref = decision:...
```

The path does not poison coverage.

Without the manifest permission + decision ref, N/A is a failure rather than a convenient way to hide a path.

## Example: unreachable path

```text
archive UNREACHABLE
failure evidence present
```

Result:

```text
acquisition paths       FAIL
no stale visible        UNKNOWN
operator result usable  FAIL/UNKNOWN according to observed usability evidence
```

The system refuses to invent whether the unreachable path would have served current or stale content.

## Example: missing path observation

Missing path:

```text
acquisition paths       UNKNOWN
```

For an operator-visible missing path, stale/usability aggregates also preserve UNKNOWN as relevant.

Incomplete coverage is not a PASS.

## Privacy / evidence references

The validator stores only bounded identifiers and refs supplied by the caller. It does not ingest:

- downloaded payload contents;
- credentials;
- install logs;
- arbitrary HTTP bodies;
- private messages;
- shell transcripts.

Those may exist in their owning evidence systems, sanitized as appropriate. The report only needs stable evidence references plus immutable result identity and explicit state.

## Tests locked into this tranche

The focused suite covers:

1. exact paths -> all three benchmark fragments PASS;
2. stale-but-usable -> content/stale FAIL, usability PASS;
3. missing observation -> UNKNOWN rather than PASS;
4. allowed N/A with decision evidence -> PASS without silent omission;
5. forbidden N/A -> FAIL;
6. unreachable path -> acquisition FAIL, stale UNKNOWN;
7. contradictory observation shapes fail closed;
8. unknown/duplicate path observations fail closed;
9. deterministic report identity across observation ordering;
10. explicit non-authority/provenance flags;
11. valid fragments fit #42's E2E-L3-001 property schema;
12. one valid Layer-3 scenario cannot complete the full benchmark while other required scenarios are absent.

## What a real Layer-3 sample still requires

This branch does **not** run `E2E-L3-001`.

A future real sample needs an actual authorized task/run and an operator-visible result. The external acquisition procedure then supplies observations to this validator, and accepted provenance adapters bind:

```text
real task
real run
real external authority
real operator-visible result
acquisition report
real post-completion outcome
```

Only that combined evidence can be evaluated as the real Layer-3 scenario.

## Stop line

Do not widen this capability into network/install/publishing machinery simply because those systems are reachable.

The next expansion is justified only if real benchmark runs show that external observation capture is too error-prone or expensive to remain separate.
