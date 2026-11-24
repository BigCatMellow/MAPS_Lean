# PR #341 — descoping sealed custody: a public, beacon-anchored precommitment model

**Design only. No selection run, no case/corpus file touched, no owner
document edited by this note. Proposes exact replacement text inline for a
follow-up PR to apply after independent review.**

**Revision 2 (2026-09-16).** The first version of this note (reviewed by
`rumi`, `REQUEST_CHANGES`, `work/reviews/pr-366-review-evidence.md`) dropped
the NIST beacon along with the secret. That was wrong, and materially so —
§3 below is rewritten to correct it; the rest of this note is re-verified
against the correction in §8. Rumi's finding, quoted directly (full text in
the PR comment):

> The proposal (§3.1) drops the NIST beacon along with the secret,
> replacing the seed with `SHA256(fixed-namespace +
> already-public-frozen-inputs)`. But the beacon was doing separate work
> from the secret. [...] Two independent properties: **Secret** → stops an
> *outsider* from reproducing the result. **Beacon** → stops the *insider*
> from grinding over candidate results before committing, because the
> pulse genuinely doesn't exist yet at commitment time. PR #366's proposal
> keeps neither. Every input to the new `SHA256` formula [...] is already
> public and frozen *before* the formula itself is chosen. Nothing stops
> the operator (or anyone) from privately dry-running the proposed formula
> — or any number of textually-different-but-equally-defensible variants
> (different namespace string, field order, casing, delimiter) — against
> the already-known frozen pool, entirely offline, and only
> "pre-registering" [...] whichever variant produces the most favorable
> 48-case selection. §3.3's tamper-*evidence* argument doesn't reach this:
> grinding happens entirely before the first git commit and leaves no trace
> a git-history-divergence check could ever see. [...] **Possible fix
> directions**: keep some externally-generated, not-yet-existing-at-
> registration-time public entropy in the seed — e.g. retain the NIST
> beacon pulse as the sole namespace-differentiating input while dropping
> only the *secret* half of the scheme. The note conflates "we don't need
> secrecy, there's no custodian to protect" with "we don't need any
> external unpredictability at all" — only the first is actually supported
> by the solo-owner constraint.

This is correct and the fix direction is right. The corrected mechanism
below keeps the beacon, drops only the secret, and — importantly, worth
stating plainly rather than glossing past — the beacon is now **more**
load-bearing than it was in the original sealed design, not less: the
original design's anti-grinding guarantee rested on *two* independent
things, an untrusted-by-construction custodian (Gate 0) *and* the beacon's
timing discipline. Removing the custodian removes one of the two; the
beacon is now the **only** remaining technical safeguard against grinding,
with nothing else standing behind it. That is a reason to hold it to a
higher bar, not a reason it was safe to drop.

## 0. Authorization

Relayed by coordinator `venu`, attributed to the operator directly:

> the sealed-custody/independent-curator requirement is being descoped.
> Operator confirmed: solo owner, no trusted third party available or
> wanted, explicitly accepts running curation themselves and self-attests
> they will not tune case selection toward favorable outcomes.

**Scope of that attestation, re-examined per rumi's finding.** The quote
above was given about "tuning case selection toward favorable outcomes" in
general, before this note had distinguished *rule-grinding* (choosing which
formula to commit by testing it against an already-known pool — technical,
fully preventable, and now closed by §3's correction) from *protocol-tuning-
after-seeing-the-selection* (reading the genuine, ungrindable 48-case result
and then shaping the protocol around it — not technical, has no available
fix, and is what §4 below is actually about post-correction). The operator
was not asked to separately accept the grinding attack surface, because
revision 1 of this note did not yet know it existed to ask about. With §3's
fix, grinding is closed by mechanism rather than by trust, so nothing further
needs to be asked of the operator on that specific point — but this
distinction is recorded here so a future reader does not conflate "the
operator accepted risk X" with "the operator accepted risk Y" when only X
was ever on the table.

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
r9's own finding. **But §8 of this note explains why a fresh review is still
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

## 3. Proposed replacement: public precommitment, deterministic, beacon-anchored, no secret

### 3.1 The rule (corrected — keeps the beacon, drops only the secret)

Reuse the sampling manifest's existing ranking shape, dropping the secret
but **keeping the NIST beacon as the sole source of unpredictability** —
per rumi's finding above, this is the load-bearing correction:

```text
selection_rank = SHA256(
  "MAPS_PROTOCOL_EFFECTIVENESS_V0_PUBLIC\n" +
  approved_design_head + "\n" +
  source_pool_definition_sha256 + "\n" +
  nist_pulse_timestamp + "\n" +
  nist_pulse_output_value + "\n" +
  lower(repository_full_name) + "#" + decimal(issue_number) + "\n"
)

holdout_rank = SHA256(
  "MAPS_PROTOCOL_EFFECTIVENESS_V0_PUBLIC_HOLDOUT\n" +
  approved_design_head + "\n" +
  nist_pulse_timestamp + "\n" +
  nist_pulse_output_value + "\n" +
  lower(repository_full_name) + "#" + decimal(issue_number) + "\n"
)
```

Sort ascending by `selection_rank` within each domain/complexity stratum;
take the first rows needed to fill the 3/6/3 per-domain quota, enforcing
`max_cases_per_repository = 4` and `REPO_CAP`/eligibility-rejection
bookkeeping exactly as the current manifest already specifies (§"Candidate
ranking", unchanged). Holdout: within each domain/complexity cell, the
smallest `holdout_rank` becomes `SEALED_HOLDOUT` (unchanged rule from the
current manifest, just recomputed without a secret).

**Plain `SHA256`, not `HMAC-SHA256`, and no menu of formulas.** `HMAC`'s
keyed construction exists specifically to make forgery hard for someone who
doesn't hold the key; with no secret key at all, a keyed MAC adds nothing a
plain hash doesn't already give here. Exactly one formula is committed —
not a small pre-approved set to choose among after the pulse — for the same
reason the original Gate 2 specified exactly one secret and one HMAC
construction, never several: a menu of pre-registered variants, applied
after the pulse and picked for favorability, would just be grinding wearing
a pre-registration costume.

### 3.2 The public commitment sequence — why order relative to the pulse is the entire mechanism

1. Source pool frozen (unchanged): `source_pool_definition_sha256` and
   `approved_design_head` already exist and are already public before any
   of this starts.
2. **Before the qualifying beacon pulse exists**, commit to git, publicly,
   timestamped: (a) the exact formula in §3.1, verbatim as checked-in
   text/code, and (b) the exact beacon-pulse selection rule, unchanged from
   the current design's own Gate 2 step 5 — *"the first valid NIST
   Randomness Beacon 2.0 pulse at or after `source_pool_freeze_timestamp +
   600 seconds`"*. This rule for *which* pulse counts is itself fixed and
   public before any qualifying pulse exists, so there is no room to pick a
   favorable pulse among several candidates either (same "may not choose
   among available pulses after seeing resulting samples" property the
   current manifest already states, now enforced by the same timing
   discipline rather than by curator discretion).
3. **Wait.** The qualifying pulse's `nist_pulse_output_value` does not
   exist yet at step 2 and cannot be predicted — this is NIST's own
   guarantee for the 2.0 beacon (signed, hash-chained, generated from a
   physical entropy source), independent of anything MAPS_L controls. This
   is what makes step 2's commitment *ungrindable*: there is no formula
   variant anyone could dry-run against the real future pulse value before
   it exists, because it doesn't exist to dry-run against.
4. Once the pulse publishes, record the same public evidence fields the
   current design already specifies (`nist_pulse_timestamp`,
   `nist_pulse_index_or_identifier`, `nist_pulse_output_value`,
   `nist_pulse_certificate_identifier_if_available`) — these are public
   from the moment NIST publishes them, so recording them is bookkeeping,
   not a disclosure.
5. Apply the §3.1 formula — already fixed at step 2, now with all its
   inputs public — to compute the 48 identities and holdout assignment.
   This step is mechanical and reproducible by anyone; there is nothing
   left to decide.

The eventual selection is therefore **determined the instant the qualifying
pulse publishes**, not whenever someone gets around to running step 5 —
delaying step 5 changes nothing about what it will produce, which closes
the "delay selection until a favorable protocol edit looks like it predates
it" concern §4 originally worried about (see §4's revised second paragraph).

### 3.3 Why this is tamper-*evident* for post-hoc swaps, and grinding-*resistant* by construction for the rule itself — name both mechanisms precisely, they are different

Two separate properties, previously conflated in revision 1:

- **Grinding resistance (the property revision 1 got wrong):** comes from
  §3.2's ordering — the formula is fixed *before* the one input that makes
  it unpredictable (`nist_pulse_output_value`) exists. Nobody, including
  the operator, could have selected this specific formula because it
  produces a favorable result, because at commitment time no result from
  it was computable yet. This is a real technical guarantee, not a promise.
- **Tamper evidence for a post-hoc swap (revision 1's original point,
  still valid and unaffected by the correction):** once the pulse is public
  and the formula (already committed) is applied, the result is
  reproducible by anyone — the operator, a future independent reviewer, an
  outside auditor. If the committed result in git ever diverges from what a
  fresh recomputation of the committed formula + published pulse produces,
  that divergence is visible, dated, and attributable in git history
  forever. This does not *prevent* someone from trying to swap a case after
  the fact; it makes the attempt permanently detectable.

Together: the *rule* can't be chosen to favor a known outcome (grinding
resistance, new in this revision), and the *result*, once computed, can't be
silently replaced without leaving a trace (tamper evidence, revision 1's
original argument, now resting on a mechanism that actually earns it).

## 4. Residual risk, stated plainly, and the compensating control

**What this model does not, and cannot, prevent — even with §3's
correction:** the operator reads the selection results as soon as §3.2
step 5 is computed (there is no custodian to prevent that — this is the
entire, intentional point of descoping custody), and nothing stops them
from then subtly tuning the MAPS_L *protocol* — not the case list, which is
now grinding-resistant per §3.3 — toward whatever the known 48 cases will
reward, before ever running the benchmark. This is a real, open leakage
path with no cryptographic countermeasure available in a solo-owner
design; it is the risk the operator's self-attestation in §0 actually
covers, now that §3's correction has separated it cleanly from grinding.

The narrower "delay selection to make a favorable protocol edit look like
it predates selection" concern raised in revision 1 is **better addressed
by the corrected mechanism than revision 1 gave it credit for**: because
the result is determined the instant the qualifying pulse publishes (§3.2),
not whenever step 5 is actually run, delaying step 5 cannot change what it
will produce or help disguise a protocol edit's timing relative to it — the
pulse timestamp, not the computation timestamp, is what anchors "when the
selection became fixed." What remains open is only the broader
protocol-tuning risk above, which is about the owner's *judgment* after a
genuine, undeniable, already-fixed result exists — not about timing or
grinding, and not something any commitment scheme can close.

**A third, separate residual risk, named explicitly per rumi's required
follow-up on this PR's implementation pass (revision 3): reroll.**
Formula-grinding (picking a favorable *formula*) is technically blocked by
§3.2's ordering. Rerolling the *ceremony itself* is not: nothing in §3.2
stops an operator from re-declaring a new `source_pool_freeze_timestamp`
after seeing an unfavorable draw from an earlier one, with byte-identical
pool content, to force a different qualifying beacon pulse and therefore a
different 48-case result. This is not a new mechanism gap this note failed
to consider before — the original sealed design carried the exact same
theoretical vulnerability and relied on the same two things this note
already names as retired or weakened: an independent, non-incentivized
custodian (Gate 0, now gone) and the "do not reroll... because you dislike
the sample" instruction (prose, always trust-based, never technically
enforced, even in the original design). What changes here is that the
custodian backstop is gone, so reroll now rests on self-discipline alone,
the same footing as protocol-tuning. The implementation PR
(`INDEPENDENT-CURATOR-START-PROMPT.md` Gate 2,
`TARGET-WORK-SAMPLING-MANIFEST.md`'s "Precommit fields") makes
`source_pool_freeze_timestamp` immutable-once-committed by the same rule
that already governs a pool-content change, which gives reroll the same
*tamper-evidence* property §3.3 gives a post-hoc case swap — a second
freeze-timestamp commit is a permanent, dated, attributable fact in git
history — but this is detection, not prevention, exactly like §3.3's
original argument, and the existing "do not reroll" prose survives that
edit intact (verified in the implementation PR, not silently dropped).

**Compensating control, per the authorization in §0, covering both
open residual risks (protocol-tuning and reroll):** there is no
technical fix for either within a solo-owner, no-third-party constraint —
the mitigation is the operator's own explicit self-attestation, recorded
here verbatim per this dispatch's instruction: *"solo owner, no trusted
third party available or wanted, explicitly accepts running curation
themselves and self-attests they will not tune case selection toward
favorable outcomes."* "Tune case selection toward favorable outcomes"
already reads naturally over reroll (choosing which *draw* to keep) as
much as over protocol-tuning (choosing how to respond to a fixed draw) —
this note records that reading explicitly rather than leaving it
implicit. This note does not treat that attestation as closing
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
   an HMAC-with-secret-seed construction with a plain `SHA256` construction
   keyed only by the same public beacon pulse the original design already
   used, dropping the secret half. That is a different cryptographic
   primitive serving a narrower purpose (grinding-resistance without an
   independent custodian, vs. secrecy-plus-grinding-resistance with one),
   not a superficial edit — revision 1 of this note got it wrong the first
   time by dropping the beacon along with the secret (rumi's finding,
   quoted in full above), which is itself the strongest evidence that this
   mechanism needs independent, not self-certified, verification. A
   reviewer needs to independently check, at minimum:
   - does dropping the secret introduce any way to bias the *frozen pool
     itself* before the rule is published (answer, per §3.1: no — the pool
     is already frozen at `source_pool_freeze_timestamp` before any
     selection rule applies, unchanged by this proposal);
   - does the hash-based rank have any exploitable structure an adversary
     (here, the operator against their own incentive) could favor by
     proposing new eligible candidates *after* seeing the rule (answer: no
     — the pool freeze happens first, and this proposal does not touch
     that ordering);
   - **could the formula/rule itself be selected from several
     equally-defensible variants to fit an already-known result** — the
     specific gap revision 1 missed. Answer under the corrected §3.2: no,
     because the formula is committed before `nist_pulse_output_value`
     exists, so no variant can be dry-run against the real future value —
     but a reviewer should independently verify the *ordering* in §3.2 is
     actually enforced (i.e., that the follow-up PR's process genuinely
     commits the formula before the pulse, not merely claims to) rather
     than trust this note's own account of it;
   - is `SHA256` the right primitive vs. something with different bias
     properties for this use, and is folding `nist_pulse_output_value`
     directly into each row's hash (rather than deriving an intermediate
     "seed" first, as the original HMAC construction did) equivalent in
     the properties that matter.
   This note states its own reasoning above but is not a substitute for an
   independent check of it — revision 1's own miss is the concrete
   demonstration of why.
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

- Rewrite `INDEPENDENT-CURATOR-START-PROMPT.md` Gates 0–3: delete Gate 0
  entirely; in Gate 2, delete steps 1–3 (generate/keep-private/commit-hash-
  of the secret) and steps 8–9 (keep the derived seed private, return only
  its commitment) as secret-specific, **keep** steps 4–7 (the beacon-pulse
  rule and its public evidence fields) per §3.2, replacing step 7's
  HMAC-seed derivation with §3.1's direct per-row formula; replace Gate 3's
  private-HMAC selection with §3.1's public `SHA256` rule, keeping the
  quota/REPO_CAP/no-reroll rules verbatim.
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
