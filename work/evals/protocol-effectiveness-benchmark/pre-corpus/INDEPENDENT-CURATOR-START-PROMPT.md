# Public precommitment start prompt — protocol-effectiveness-v0

Use this prompt when the MAPS_L repository owner performs case selection
directly, under the public, beacon-anchored precommitment model
(`work/notes/2026-09-15-pr341-custody-descope-design.md`, revision 2,
reviewed by `rumi`). It replaces the sealed independent-curator/custodian
model this file originally specified for **selection only** (Gates 0–3
below) — no independent custodian is required or used for selection.
Gate 4 (case construction) and Gate 5 (corpus/overlay review), and
`BENCHMARK-SPEC.md` §9.1–9.3's hidden-material handling, are **unaffected**
by this change and keep their own custody requirements, which remain a
distinct, still-open question (design note §5/§6) — this file's Gates 4/5
are unchanged.

---

Act as the operator running **public deterministic selection** for
`BigCatMellow/MAPS_Lean` PR #341, benchmark line `protocol-effectiveness-v0`.

Your role is to independently validate the instantiated pre-authoring
package, publicly commit the exact selection rule before the qualifying
beacon pulse, apply it deterministically once the pulse exists, and
publish the full non-secret result. There is no sealed selection material
and nothing about which identities were selected is withheld from public
git history. Case-construction hidden material (Gate 4/5) is a separate
matter, still governed by its own sealing rules.

You are **not** authorized to execute A/B/C benchmark agents or spend
money.

## Exact package to review

Read repository root `AGENTS.md`, then:

- `work/tasks/protocol-effectiveness-benchmark.md`
- `work/tasks/protocol-effectiveness-corpus-construction.md`
- `work/reviews/pr-341-rereview-evidence-369bcca.md`
- the five normative owner files under `work/evals/protocol-effectiveness-benchmark/`
- `pre-corpus/PRE-AUTHORING-PACKAGE-MANIFEST.json`
- every file listed in that package manifest

Approved design head:

`369bccaf68b258c70eb6efec0c9f70115c8014cb`

Exact candidate pre-authoring package hash: see
`PRE-AUTHORING-PACKAGE-MANIFEST.json`'s current `package_hash` (recomputed
alongside this file's own change — the manifest's six inputs include
`TARGET-WORK-SAMPLING-MANIFEST.md`, which this revision also edits).

Recompute the package hash from the six `files` path/blob-SHA entries
inside `PRE-AUTHORING-PACKAGE-MANIFEST.json` using its declared rule. The
manifest file itself is not one of the six hashed inputs.

If it does not match, stop:

`STALE PRE-AUTHORING PACKAGE`

Do not silently review or curate another package.

## Gate 1 — independent pre-authoring validation

Before enumerating issue IDs, verify:

### Treatment

- tested protocol ref = `5f07b33e9fa09a5e091c6f0993092230c2faf308`;
- 45-file inventory matches the declared include/exclude rule;
- bundle hash recomputes to `7a944e3db3575c1f94df5872d8b15a644ecd7eb254893b10d9d1ebcd83aa3341`;
- neutral bootstrap and B/C injection position are common as declared;
- B uses only the frozen offline MAPS_L bundle/launcher, not mutable live MAPS sources;
- target-project authority stays common across arms;
- static instruction/context disclosure and dynamic B read-cost accounting are neutral.

### Arm C

Independently judge the exact text in `GENERIC-CONTROL.md`.

Approve it only if it is a competent non-strawman generic workflow that supports evidence inspection, proportional planning, self-verification, useful helper/tool use, scope respect, separable work, and genuine blocking without importing MAPS-specific machinery.

If materially weak/biased/MAPS-shaped, stop before selection:

`PRE-AUTHORING CORRECTIONS REQUIRED`

Do not privately substitute a new control and continue.

### Source pools / sampling

Verify `SOURCE-POOL-DEFINITION.json` hash:

`5101ed5b416f9c61b64d658a03864d77550489ba1a5eca1ba19f3f0352cc4fe6`

Verify each named repository is usable for the declared historical window and objective issue/PR metadata is available. Do not inspect candidates for MAPS-specific phenomena or expected winner while deciding whether pools are adequate.

Sampling reference:

```text
provider = OpenAI
model = gpt-5.6-sol
documented knowledge cutoff = 2026-02-16
```

If a pool must change, stop before selection. Return only the non-secret pool-level reason; changing the pool requires a new package hash/review.

### Public operation

There is no sealed custody for selection. Record only:

- operator identity (the MAPS_L repository owner, openly — there is no
  eligibility gate to satisfy for selection itself);
- confirmation that `CUSTODY-AND-EXPOSURE-PLAN.md`'s remaining
  case-construction custody requirements (Gate 4/5, unaffected by this
  change) are understood and will be addressed separately — that file's
  "Acceptable curator/custodian class" section now covers construction
  only, and whether the operator satisfies it for holdout construction is
  the open question named in the design note's §5, not settled here.

If all Gate-1 checks pass, record:

`PRE-AUTHORING PACKAGE ACCEPTED FOR PUBLIC SELECTION`

and continue to Gate 2.

## Gate 2 — public rule precommitment + future public beacon

1. Publicly commit, to git, timestamped, **before the qualifying pulse
   exists**: the exact selection-rank and holdout-rank formulas
   (`TARGET-WORK-SAMPLING-MANIFEST.md`'s "Public deterministic selection"
   section, verbatim as checked-in text) and `source_pool_freeze_timestamp`.
   This commit is the pre-registration; nothing about the eventual result
   is knowable from it yet, because the pulse it depends on does not exist.
2. **`source_pool_freeze_timestamp`, once committed, is final.** A later
   change to it is not a private do-over — it requires a new package hash
   and a fresh independent review, the same rule that already governs a
   pool-*content* change. See "Reroll" below for why this matters even
   without a secret.
3. Use the first valid NIST Randomness Beacon 2.0 pulse at or after
   `source_pool_freeze_timestamp + 600 seconds`. This rule for *which*
   pulse counts is itself fixed and public before any qualifying pulse
   exists — there is no room to pick a favorable pulse among several.
4. Record public pulse timestamp/index/output/certificate identifier where
   available.
5. Apply the exact formula committed in step 1 to the pulse output. There
   is no private seed to derive — the pulse output feeds the public
   formula directly, once it exists.

**Do not reroll.** Re-running this ceremony under a *new*
`source_pool_freeze_timestamp` after seeing an unfavorable result from an
earlier attempt is a reroll like any other, whether or not a secret is
involved — the pool content did not need to change, only the timestamp
that determines which pulse qualifies, which is enough by itself to
produce a completely different 48-case draw from the same frozen pool.

Unlike formula-grinding (which is technically blocked — step 1's ordering
makes it impossible to know a formula's result before committing to it),
**a reroll of the freeze timestamp is not technically prevented by this
mechanism.** What step 2's immutability rule provides is *tamper evidence*,
not *tamper prevention*, for this specific attack: a second
`source_pool_freeze_timestamp` commit, dated after the first one's known
(unfavorable) result was computable, is a visible, permanent, and
attributable fact in git history — exactly the same kind of trace §3.3 of
the design note relies on for a post-hoc case swap. It does not stop
someone determined to reroll; it makes the attempt impossible to hide.
Whether a reroll actually happened, given that trace, is a judgment call
for whoever reviews the eventual git history — this file's job is only to
make sure the trace exists to review. The compensating control beyond that
is the same operator self-attestation the design note records for
protocol-tuning (design note §4): there is no available technical fix for
either inside a solo-owner, no-custodian model.

Early secret/seed exposure language from the prior version of this gate no
longer applies — there is no secret or seed to expose.

## Gate 3 — public deterministic selection

- enumerate objectively eligible rows from the frozen 16 repositories;
- assign domain and mechanical complexity only under frozen rules;
- rank with the public per-row formula from Gate 2 step 5;
- select exactly 48 identities under 12/domain, 3/6/3 complexity/domain,
  max 4/repository;
- preserve objective rejection and `REPO_CAP` records;
- never reject/reroll for expected arm performance;
- assign 12 `SEALED_HOLDOUT` / 36 `FROZEN_STANDARD` with the frozen public
  holdout-rank rule (`TARGET-WORK-SAMPLING-MANIFEST.md`).

**Publish IDs, URLs, ranks, the full ranking table, and holdout
membership.** There is no reason to withhold any of it — nothing about
selection is secret under this model, and pretending otherwise would just
recreate an unenforced, purely cosmetic version of the sealed design
without any of its actual technical protection.

Case-specific hidden contracts/oracles/answers for the selected identities
remain governed entirely by Gate 4/5 and `BENCHMARK-SPEC.md` §9.1–9.3,
unaffected by this change — publishing selection identities does **not**
publish case content. See the design note's §6 for the precise boundary
(holdout *membership* is now public; holdout *answers* are not).

If required cells cannot be filled:

`SOURCE POOL INSUFFICIENT`

Return only aggregate deficiency counts; do not improvise new repositories.

## Gate 4 — sealed case construction

Follow `work/tasks/protocol-effectiveness-corpus-construction.md` and the normative CASE/RUN/SPEC owners exactly.

Required outcomes include history-free pre-fix starts, task-derived fixtures, hidden checks rather than hidden requirements, exact run-visible boundaries, correct terminal truth, hidden canaries, resolution/provenance isolation, cutoff metadata, post-selection overlay/family assignment, approved counterweight semantics, and credible ability for A/C to outperform B.

Do not run benchmark agents.

## Gate 5 — distinct overlay/corpus review

Every primary overlay class requires the approved independent audit. If you authored a case/overlay, do not self-approve it. Use a distinct eligible sealed-access reviewer.

After construction, a **different independent corpus/pre-freeze reviewer** must review the sealed corpus/freeze package.

## Keep sealed (case construction only)

Selection is now fully public (Gate 2/3 above) — nothing about which
identities were selected, how, or their holdout assignment is sealed.

Keep private until the Gate 4/5 permitted reveal (case-construction
material only, governed by `BENCHMARK-SPEC.md` §9.1–9.3, unaffected by
this change):

- fixtures/starting-state packages;
- visible/private case records;
- hidden checks/answers/blocker classes;
- stress/counterweight records;
- canaries/resolution identifiers;
- answer-bearing provenance.

## Return package

Selection fields (Gate 2/3) are published in full — see Gate 3 above. No
aggregation or redaction applies to selection identities, ranks, or
holdout membership under this model.

Case-construction fields (Gate 4/5, unaffected by this change) remain
aggregate-only until the permitted reveal:

```text
pre_authoring_package_hash
protocol_bundle_hash
generic_control_hash + exact-text approval statement
source_pool_definition_sha256
sampling reference model/cutoff
operator identity
public NIST pulse evidence (Gate 2)
source_pool_freeze_timestamp (Gate 2, immutable once committed)
candidate attempt/accepted/rejected aggregate counts
aggregate rejection-reason counts
aggregate domain/complexity/project-origin/terminal-class counts
aggregate NONE/STRESS/COUNTERWEIGHT counts after overlay audit
aggregate seeded_stress prevalence
FROZEN_STANDARD_count
SEALED_HOLDOUT_count
corpus_hash
holdout_bundle_hash
confirmatory_look_count
exposure owners
freeze timestamp
```

Do not return information from which hidden case-construction material
(fixtures, answers, canaries) is trivially reconstructable — this
restriction is about construction content, not selection identities, which
are already fully public per Gate 3.

## Final status

Return exactly one:

- `PUBLIC SELECTION COMPLETE — READY FOR GATE 4 CASE CONSTRUCTION`
- `PRE-AUTHORING CORRECTIONS REQUIRED`
- `SOURCE POOL INSUFFICIENT`
- `STALE PRE-AUTHORING PACKAGE`

`CUSTODY BREACH — SELECTION CONTAMINATED` and `INELIGIBLE CUSTODY
ENVIRONMENT` are retired for selection — there is no selection custody to
breach or be ineligible for under this model. (Gate 4/5 construction
custody keeps its own status vocabulary, unchanged, in
`CUSTODY-AND-EXPOSURE-PLAN.md`.)

Even `PUBLIC SELECTION COMPLETE...` does **not** authorize benchmark
execution.
