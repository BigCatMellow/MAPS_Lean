# Public precommitment start prompt — protocol-effectiveness-v0

Use this prompt when the MAPS_L repository owner performs case selection
directly, under the public, beacon-anchored precommitment model
(`TARGET-WORK-SAMPLING-MANIFEST.md`, revision 3: public beacon selection with a pre-beacon frozen eligible-candidate ledger). It replaces the sealed independent-curator/custodian
model this file originally specified for **selection only** (Gates 0–3
below) — no independent custodian is required or used for selection.
Gate 4 (case construction) and Gate 5 (corpus/overlay review), and
`BENCHMARK-SPEC.md` §9.1–9.3's hidden-material handling, are **unaffected**
by this change and keep their own custody requirements, which remain a
distinct, still-open question (design note §5/§6) — this file's Gates 4/5
are unchanged.

---

This handoff has two distinct roles:

1. **Gate 1 independent reviewer** — a reviewer without a MAPS_L development
   stake independently validates the exact pre-authoring package and Arm C
   control. That reviewer does not perform selection.
2. **Gate 2/3 selection operator** — only after Gate 1 acceptance exists, the
   MAPS_L repository owner performs the public deterministic candidate freeze,
   future-beacon ranking, and publication steps. Selection itself needs no
   private custodian.

Do not collapse these roles by treating owner self-review as Gate 1 approval.

Neither role is authorized to execute A/B/C benchmark agents or spend money.
Case-construction hidden material (Gate 4/5) remains a separate later boundary.

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

Before any eligible-candidate enumeration, the **independent Gate 1 reviewer** verifies:

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

If all Gate-1 checks pass, the independent reviewer records:

`PRE-AUTHORING PACKAGE ACCEPTED FOR PUBLIC SELECTION`

with evidence bound to the exact package hash and exact Arm C control hash. Only after that independent acceptance exists may the repository-owner selection operator continue to Gate 2.

## Gate 2 — freeze the eligible population before the future beacon

The ranking pulse must not exist until every judgment-bearing eligibility
decision is frozen.

1. Under the already-reviewed eligibility rules, enumerate and adjudicate the
   complete eligible population from the 16 frozen repositories **before** the
   qualifying beacon pulse.
2. Assign domain and mechanical complexity before the pulse.
3. Create the canonical public TSV required by
   `TARGET-WORK-SAMPLING-MANIFEST.md` at
   `selection/ELIGIBLE-CANDIDATE-LEDGER.tsv`.
4. Compute `candidate_set_sha256` from the exact TSV bytes.
5. In the same git commit, create `selection/SELECTION-FREEZE.json` binding:
   - current pre-authoring package hash;
   - approved design head;
   - source-pool definition hash;
   - candidate-set hash/count and candidate-ledger git blob SHA;
   - operator identity;
   - immutable `candidate_ledger_freeze_timestamp`;
   - revision-3 selection/holdout formula identifiers; and
   - the exact qualifying-pulse rule.
6. The qualifying pulse is the first valid NIST Randomness Beacon 2.0 pulse with
   timestamp at least 600 seconds after
   `candidate_ledger_freeze_timestamp`.
7. Once that freeze commit exists, do not edit candidate membership, formulas,
   source-pool hash, or freeze timestamp and continue under the same ceremony.
   Any such change requires a new freeze and a later future pulse.

The complete frozen candidate ledger is public. The purpose of the beacon is not
secrecy; it makes the eventual ordering unknowable when the candidate set and
formula become immutable.

Record public pulse timestamp/index/output/certificate identifier where
available.

**Do not reroll.** A second freeze created after the first qualifying pulse's
result was knowable is a new ceremony and must be treated as such, with the old
freeze retained in history. Do not silently substitute it.

## Gate 3 — arithmetic selection from the frozen candidate ledger

After the qualifying pulse publishes:

- do **not** enumerate new issue IDs;
- do **not** re-adjudicate ordinary eligibility;
- recompute/verify the frozen candidate ledger hash;
- rank only frozen eligible rows with revision 3's formula, including
  `candidate_set_sha256`;
- select exactly 48 identities under 12/domain, 3/6/3 complexity/domain,
  max 4/repository;
- record `REPO_CAP` skips mechanically;
- assign 12 `SEALED_HOLDOUT` / 36 `FROZEN_STANDARD` with the revision-3
  holdout-rank formula;
- publish IDs, URLs, candidate-set hash, ranks, the complete ranking table, and
  holdout membership.

### Post-freeze defect handling

A frozen candidate may be invalidated only under the narrow rule in
`TARGET-WORK-SAMPLING-MANIFEST.md`: newly discovered objective contradiction
or source-availability failure, published evidence/discovery time, explanation
for why it was unavailable before freeze, and independent confirmation before
admitting the next-ranked replacement.

If that confirmation is unavailable, stop:

`SELECTION BLOCKED — POST-FREEZE DEFECT REVIEW REQUIRED`

Never reject or reinterpret a frozen candidate because of its observed rank,
MAPS mechanism/family properties, overlay needs, or expected arm performance.

Case-specific hidden contracts/oracles/answers remain governed entirely by Gate
4/5 and `BENCHMARK-SPEC.md` §9.1–9.3. Publishing selection identities does not
publish case content.

If the frozen ledger cannot fill required cells under the committed quotas:

`SOURCE POOL INSUFFICIENT`

Do not improvise new repositories or add post-pulse candidates.

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
candidate_set_sha256
candidate_count
candidate_ledger_freeze_timestamp (Gate 2, immutable once committed)
selection_freeze_commit_sha
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
- `SELECTION BLOCKED — POST-FREEZE DEFECT REVIEW REQUIRED`

`CUSTODY BREACH — SELECTION CONTAMINATED` and `INELIGIBLE CUSTODY
ENVIRONMENT` are retired for selection — there is no selection custody to
breach or be ineligible for under this model. (Gate 4/5 construction
custody keeps its own status vocabulary, unchanged, in
`CUSTODY-AND-EXPOSURE-PLAN.md`.)

Even `PUBLIC SELECTION COMPLETE...` does **not** authorize benchmark
execution.
