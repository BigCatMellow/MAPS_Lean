# PR #341 — descoping sealed custody: a public, no-secret precommitment model

**Design only. No selection run, no case/corpus file touched, no owner
document edited by this note. Proposes exact replacement text inline for a
follow-up PR to apply after independent review.**

## 0. Authorization

Relayed by coordinator `venu`, attributed to the operator directly:

> the sealed-custody/independent-curator requirement is being descoped.
> Operator confirmed: solo owner, no trusted third party available or
> wanted, explicitly accepts running curation themselves and self-attests
> they will not tune case selection toward favorable outcomes.

This note treats that as the authorizing decision for descoping
Gate 0–3 of `INDEPENDENT-CURATOR-START-PROMPT.md` (custody eligibility,
secret precommit + NIST beacon, private deterministic selection). It does
**not** extend that authorization to anything this note itself flags as a
separate, unaddressed question (§5, §6) — those are named for a fresh
decision, not assumed covered by the quote above.

## 1. What PR #341's r9 approval actually covers, re-read directly

`work/reviews/pr-341-rereview-evidence-369bcca.md` (head `369bcca`,
`APPROVED FOR CORPUS CONSTRUCTION`) approved the **five normative owner
documents** (`BENCHMARK-SPEC.md`, `CASE-DESIGN.md`, `RUN-PROTOCOL.md`,
`SCORING-AND-ANALYSIS.md`, `REPORT-TEMPLATE.md`) plus a mechanical
anchor-checker (`scripts/check_protocol_effectiveness_benchmark_anchors.py`,
49 findings / 107 semantic anchors / 13 pinned sections) that pins those
five documents against tampering. Its own scope line: *"Diff `fd2408f..369bcca`:
checker, FRICTION-PR341 carrier, package README, owning task, r8 evidence.
No owner document, manifest, or workflow change."*

`INDEPENDENT-CURATOR-START-PROMPT.md` and `CUSTODY-AND-EXPOSURE-PLAN.md` are
**not** among the five pinned owners and were not what r9's mutation matrix
exercised — that review is about the anchor checker's ability to catch
tampering in the five owners, not an endorsement of the custody-eligibility
prompt's specific mechanism. So this note's proposal does not contradict
r9's own finding. **But §6 of this note explains why a fresh review is still
required regardless.**

## 2. What Gate 0–3 currently do, and why they cannot execute for a solo owner

Walking the actual mechanism in `INDEPENDENT-CURATOR-START-PROMPT.md` +
`CUSTODY-AND-EXPOSURE-PLAN.md` + `TARGET-WORK-SAMPLING-MANIFEST.md`
("Non-derivable deterministic selection"), not paraphrased:

- **Gate 0 (custody eligibility).** Requires a party whose "private
  working storage and working transcript are inaccessible to the MAPS_L
  repository owner" — explicitly, *"a normal fresh chat under the same
  MAPS_L owner's account is not an eligible custody environment."* For a
  confirmed solo owner with no trusted third party, **no available party
  can ever pass Gate 0.** This is not a hard case to satisfy under the
  current design — it is structurally unsatisfiable, which is presumably
  why the operator is descoping it rather than working around it.
- **Gate 2 (secret precommit + beacon).** A curator generates a private
  256-bit `selection_secret`, commits only its hash, waits for a public
  NIST Randomness Beacon 2.0 pulse, and derives `selection_seed =
  HMAC-SHA256(selection_secret, design_head + pool_hash + pulse_data)`. The
  sampling manifest's own stated reason for the secret: *"A seed derived
  only from public repository state, source pools, and the approved design
  head would let a MAPS_L protocol modifier reproduce the selected issue
  IDs. That would violate the access-based exposure rule even if the IDs
  were never committed here."* — i.e., the secret exists **specifically**
  to stop the owner from reproducing the selection. Once the owner *is* the
  one computing the selection (no custodian), this justification is moot by
  construction, not weakened by oversight.
- **Gate 3 (private deterministic selection).** `selection_rank =
  HMAC-SHA256(selection_seed, "repo#issue")`, sorted ascending per stratum,
  quota-filled with `REPO_CAP` bookkeeping. The ranking function itself is
  fine and reusable (§3 below) — only the *secrecy of the seed* is the part
  that depends on a custodian that does not exist here.

## 3. Proposed replacement: public precommitment, deterministic, no secret

### 3.1 The rule (concrete proposal, not a placeholder)

Reuse the sampling manifest's existing ranking shape exactly, dropping only
the secret:

```text
selection_rank = SHA256(
  "MAPS_PROTOCOL_EFFECTIVENESS_V0_PUBLIC\n" +
  approved_design_head + "\n" +
  source_pool_definition_sha256 + "\n" +
  lower(repository_full_name) + "#" + decimal(issue_number) + "\n"
)
```

Sort ascending by `selection_rank` within each domain/complexity stratum;
take the first rows needed to fill the 3/6/3 per-domain quota, enforcing
`max_cases_per_repository = 4` and `REPO_CAP`/eligibility-rejection
bookkeeping exactly as the current manifest already specifies (§"Candidate
ranking", unchanged). Holdout assignment reuses the same shape:

```text
holdout_rank = SHA256(
  "MAPS_PROTOCOL_EFFECTIVENESS_V0_PUBLIC_HOLDOUT\n" +
  approved_design_head + "\n" +
  lower(repository_full_name) + "#" + decimal(issue_number) + "\n"
)
```

Every input (`approved_design_head`, `source_pool_definition_sha256`,
`repository_full_name`, `issue_number`) is **already frozen and public**
before this rule is ever applied — `TARGET-WORK-SAMPLING-MANIFEST.md`
already requires the source pool frozen at `source_pool_freeze_timestamp`
before selection, and issue numbers are GitHub-assigned, immutable,
pre-existing historical facts nobody (including the benchmark owner) can
influence retroactively. No entropy source, no beacon, no secret is needed
because nothing here is being kept from anyone — the hash is not a
commitment device here, it is only a **fixed, auditable, non-obviously-biased
tie-breaking/ordering function** over already-public data (equivalent in
spirit to the dispatch's own suggested "sort by issue ID, take every Nth" —
a `SHA256`-based rank is preferred over a raw issue-ID sort specifically
because sorting by raw ID could systematically bias toward whichever repos/
eras happened to have lower issue numbers in the frozen window; hashing
decorrelates rank from any single field while remaining 100% reproducible
by any auditor with a pocket calculator and the four public inputs above).

### 3.2 The public commitment sequence (this is the actual integrity mechanism)

1. **Before computing any selection result**, commit to git, publicly,
   timestamped: (a) this exact selection-rank formula (verbatim, as
   checked-in text/code — not a description of it), (b)
   `source_pool_definition_sha256` (already exists), and (c) the frozen
   `approved_design_head`. This commit is the pre-registration.
2. **Only after that commit lands** (or as a fully separate, later step —
   see §4 on why order matters even without secrecy), apply the rule
   mechanically to the frozen pool and record the resulting 48 identities +
   holdout assignment.
3. **The formula never changes after step 1**, and reapplying it to the same
   frozen inputs always reproduces the identical result. Both the
   pre-registration and the eventual result are ordinary immutable git
   history.

### 3.3 Why this is tamper-*evident*, not tamper-*prevented* — name the mechanism precisely

The original design's integrity came from **exposure denial**: the owner
literally could not read the selection before it was fixed. The new
design's integrity comes from **reproducibility + irreversible public
record**: anyone — the operator, a future independent reviewer, an outside
auditor — can rerun step 2's formula against the same frozen public inputs
and get the identical 48 identities. If the committed result in git ever
diverges from what a fresh recomputation of the committed formula produces,
that divergence is visible, dated, and attributable in git history forever.
A silent post-hoc swap of an unfavorable case is not physically prevented,
but it cannot be made invisible — the discrepancy between "what the
pre-registered rule says" and "what actually got used" is a permanent,
checkable fact.

## 4. Residual risk, stated plainly, and the compensating control

**What this model does not, and cannot, prevent:** the operator reads the
selection results as soon as they compute them (there is no custodian to
prevent that), and nothing stops them from then subtly tuning the MAPS_L
*protocol* — not the case list — toward whatever the known 48 cases will
reward, before ever running the benchmark. This is a real, open leakage
path with no cryptographic countermeasure in this design. Also open, more
subtly: because the same non-custodied party controls the *timing* of
step 2 relative to any protocol edits, a determined actor could in
principle delay computing the selection until after making a protocol
change they already suspect would help, then claim the change predates
selection — the public commit timestamp on the *pool/rule* does not, by
itself, prove no protocol edit happened in between. (The design already has
a partial mitigant for this specific case — `approved_design_head` and the
treatment bundle hash are separately frozen and hashed at `369bcca`/the
package hash — but that only proves the treatment *artifact* didn't change
after selection, not that the *next* protocol version's authors, who are
the same solo owner, weren't influenced by having seen the cases.)

**Compensating control, per the authorization in §0:** there is no
technical fix for this within a solo-owner, no-third-party constraint —
the mitigation is the operator's own explicit self-attestation, recorded
here verbatim per this dispatch's instruction: *"solo owner, no trusted
third party available or wanted, explicitly accepts running curation
themselves and self-attests they will not tune case selection toward
favorable outcomes."* This note does not treat that attestation as closing
the risk — it treats it as the operator's informed, explicit acceptance of
a risk that has no available technical closure, which is a materially
different and more honest thing to record than silently weakening the
design without naming what was lost. Any future H1/H5 "MAPS_L wins" claim
produced under this model inherits this caveat and should say so in the
eventual `REPORT-TEMPLATE.md` output, not just in this design note.

## 5. Open question this note does *not* resolve: holdout still needs a non-protocol-modifying builder

`BENCHMARK-SPEC.md` §9.4 ("Holdout independence"): *"A holdout builder may
not hold a protocol-modifying role from the start of holdout construction
through the designated confirmatory look."* This requirement is **separate
from selection secrecy** — it's about who *builds the case fixtures* for
the 12 `SEALED_HOLDOUT` identities (Gate 4), not who selects which 48
identities exist. Descoping Gate 0–3's selection custody does not, by
itself, answer whether the solo operator satisfies §9.4 for holdout
*construction*. If the operator is also going to build holdout fixtures
themselves, that is a second, distinct trust-based descope this dispatch's
authorization quote does not obviously cover (it speaks to "case
selection," not "holdout construction/exposure"). **Flagging, not
deciding:** a follow-up design pass should explicitly ask the operator
whether §9.4's holdout-builder-role requirement is also being descoped, or
whether the `FROZEN_STANDARD`/`SEALED_HOLDOUT` split needs to be
simplified to a reporting-only distinction (both built and known by the
same solo owner, with the original "unexposed until confirmatory look"
property abandoned for holdout specifically) rather than silently assumed
either way.

## 6. Open question this note does *not* resolve: is "sealed" holdout membership even meaningful once selection is public?

A second-order consequence of §3 worth surfacing explicitly, not implied by
§0's authorization: once the full 48-identity selection is computed
publicly by the same party who will build and run everything, the
`holdout_rank` formula in §3.1 is equally computable by that same party at
the same moment — there is no remaining mechanism to keep even the
*12-of-48 holdout membership* from the operator, only the case *content*
(§9.1–9.3's storage/run-visible-boundary rules, which are genuinely
independent of selection secrecy and remain fully intact under this
proposal). Practically: the operator will know *which* 48 issues are the
corpus and *which* 12 of those are nominally "holdout" from the moment
selection runs, even though the *hidden contracts/oracles* for all 48 stay
protected by the unrelated §9.1–9.3 mechanism until case construction
chooses to reveal them. Whether that residual (knowing holdout *membership*
without knowing holdout *answers*) is an acceptable weakening of `SEALED_HOLDOUT`'s
definition in §8, or whether the holdout/standard split should be
re-labeled to reflect what it can still honestly promise, is named here for
the same fresh decision as §5 — not resolved by this note.

## 7. Scope boundary: what stays exactly as-is

- `CASE-DESIGN.md`, `RUN-PROTOCOL.md`, `SCORING-AND-ANALYSIS.md`,
  `REPORT-TEMPLATE.md` — untouched. Case construction, hidden-material
  storage (§9.1–9.3), canary rules, run-visible boundary, scoring/verdict
  logic are all independent of the selection-custody mechanism and this
  note does not propose changing any of them.
- `SOURCE-POOL-DEFINITION.json`, `GENERIC-CONTROL.md`,
  `TREATMENT-BUNDLE-INVENTORY.tsv`, `TREATMENT-SURFACE-MANIFEST.md` —
  untouched; still independently reviewed inputs, unrelated to custody.
- Gate 4 ("sealed case construction") and Gate 5 ("distinct overlay/corpus
  review") in `INDEPENDENT-CURATOR-START-PROMPT.md` — text unchanged by
  this proposal (subject to §5/§6's open questions above, which are about
  whether their *preconditions* still hold for a solo owner, not about
  changing their own wording).
- No selection is run. No corpus/case file is created or touched. No
  `PRE-AUTHORING-PACKAGE-MANIFEST.json` hash changes (the six pre-corpus
  inputs it covers are unchanged by this proposal; only
  `INDEPENDENT-CURATOR-START-PROMPT.md`, which is outside that manifest's
  six-file hash, and `TARGET-WORK-SAMPLING-MANIFEST.md`'s "Non-derivable
  deterministic selection" section, which *is* inside it, would need
  editing in a follow-up PR — see §8).

## 8. Why this needs a fresh independent review, not silent folding into "already approved"

Two independent reasons, either one sufficient on its own:

1. **Mechanism change, not just custody-status bookkeeping.** §3 replaces
   an HMAC-with-secret-seed construction with a plain `SHA256`
   construction over public inputs. That is a different cryptographic
   primitive serving a different purpose (public auditability vs. secrecy),
   not a superficial edit. A reviewer needs to independently check: does
   dropping the secret introduce any way to bias the *frozen pool itself*
   before the rule is published (answer, per §3.1: no — the pool is already
   frozen at `source_pool_freeze_timestamp` before any selection rule
   applies, unchanged by this proposal); does the hash-based rank have any
   exploitable structure an adversary (here, the operator against their own
   incentive) could favor by proposing new eligible candidates *after*
   seeing the rule (answer: no — the pool freeze happens first, and this
   proposal does not touch that ordering); is `SHA256` the right primitive
   vs. something with different bias properties for this use. This note
   states its own reasoning above but is not a substitute for an
   independent check of it.
2. **Hash changes.** If `TARGET-WORK-SAMPLING-MANIFEST.md`'s "Non-derivable
   deterministic selection" section is edited to match §3 in a follow-up
   PR, that file's blob changes, which changes the package hash the
   `PRE-AUTHORING-PACKAGE-MANIFEST.json` pins
   (`c0927f437e7a4d07d1a825eace7e3d061ad0bb9c6a8b8775c28b2e4bfd07e963`) —
   the manifest's own `package_hash_rule` requires exactly this, and its
   `owner_recompute_status: MATCH` field would need to flip to a fresh
   `MATCH` against the new hash, which by the manifest's own stated
   convention (`PRE-AUTHORING PACKAGE ACCEPTED FOR SEALED SELECTION` /
   `STALE PRE-AUTHORING PACKAGE`) requires a new review pass. r9's approval
   is bound to `369bcca` and the current six-file hash; it does not, and
   was never claimed to, cover a hash that does not yet exist.

## 9. Concrete follow-up-PR scope (not applied here)

A later PR, after this note is reviewed, would need to:

- Rewrite `INDEPENDENT-CURATOR-START-PROMPT.md` Gates 0–3 (delete Gate 0
  entirely; replace Gate 2's secret/beacon steps with §3.2's public-commit
  sequence; replace Gate 3's private-HMAC selection with §3.1's public
  `SHA256` rule, keeping the quota/REPO_CAP/no-reroll rules verbatim).
- Rewrite `CUSTODY-AND-EXPOSURE-PLAN.md`'s "Acceptable curator/custodian
  class" and "Sampling-secret custody" sections to describe the operator
  performing selection openly, or retire the file if §5's follow-up
  decides Gate 4 construction custody is also descoped (in which case the
  file's remaining content — §9.1–9.3 hidden-material handling — likely
  belongs merged into `BENCHMARK-SPEC.md` rather than deleted outright).
- Rewrite `TARGET-WORK-SAMPLING-MANIFEST.md`'s "Non-derivable deterministic
  selection" section (§3.1's formula) and recompute
  `PRE-AUTHORING-PACKAGE-MANIFEST.json`'s `package_hash`.
- Resolve §5/§6 explicitly (operator decision) before or alongside that
  edit, so the holdout-related language in the same files is edited once,
  correctly, rather than twice.
- Get a fresh independent review at the new head, mirroring r9's rigor
  (own mutation-style adversarial check of the new formula, not just a
  read-through), before `PRE-AUTHORING PACKAGE ACCEPTED FOR SEALED
  SELECTION` is claimed again.
