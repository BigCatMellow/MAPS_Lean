# Development checkpoint 3 — 2026-08-15

Status: `WORKING NOTES — NOT ACTIVE AUTHORITY`

This checkpoint supplements the earlier 2026-08-15 handoff/checkpoint notes. Canonical code/task/PR state remains authoritative.

## Harness / security stack

Draft stacked chain remains:

```text
main
→ PR #20 harness typed foundation
→ PR #21 hcom normalization + Hook registry
→ PR #22 HarnessService
→ PR #23 canonical run/lease/session guard
→ PR #24 agentic security adversarial baseline
```

All code tranches #20–#24 have successful full Runtime stack CI on their recorded implementation commits. All remain draft / independently reviewable; none should be self-approved or merged merely because downstream work continued.

PR #24:

- implementation commit: `e25baaa044a2f5bc9b969e59aeffb0036d9a5f05`
- full Runtime stack CI: `31895641637` — success
- task status updated to `READY_FOR_REVIEW`
- subsequent commits on the branch are task/working-note updates, not runtime changes

Key security invariant now mechanically covered:

`resume` is a continuation action and must pass current task revision + ACTIVE claimant + live lease + non-stale run/context + exact durable session binding. Provider liveness alone cannot revive authority.

## Skills Wave 2 stack

Current Skills chain:

```text
main
→ PR #25 agent/skills-format-wave2
→ PR #26 agent/skills-catalog-wave2
```

### PR #25 — Agent Skills format foundation

Implementation commit:

`0de3ac7535ba84b51a4b3d2a498473d4a0b8e384`

Full Runtime stack CI:

`31895948075` — success

Validation/task-record head:

`f2985f3dd510ee1679f19df45120afc316c15b6d`

Task:

`work/tasks/skills-format-wave2.md` → `READY_FOR_REVIEW`

Implemented:

- deterministic immediate-child Skill discovery;
- required `SKILL.md` frontmatter `name` + `description`;
- common scalar and YAML block-scalar description support without adding a general YAML dependency;
- custom/nested metadata tolerated but not interpreted as authority;
- compact descriptor discovery separate from body activation;
- deterministic whole-directory SHA-256 identity;
- resource inventory only, no execution;
- symlink rejection in v1;
- duplicate name rejection within one root;
- activation-time full hash drift check.

Boundary preserved:

This is not general YAML. If real ecosystem compatibility requires broader YAML semantics, evaluate a maintained parser dependency explicitly rather than growing an ad hoc parser indefinitely.

### PR #26 — Skills catalog / provenance read model

Implementation commit:

`cc30de70c170b2abaa61354ae775d8c9da2ec74d`

Full Runtime stack CI:

`31896101565` — success

Validation/task-record head:

`564498285be1519b10183247eab5f73a42f5cc6c`

Task:

`work/tasks/skills-catalog-wave2.md` → `READY_FOR_REVIEW`

Implemented:

- deterministic multi-source Skill catalog;
- factual provenance: source ID, source kind, source ref, optional **declared** revision, Skill ID/name, exact content hash;
- deterministic catalog fingerprint;
- same-name Skills across sources preserved as explicit ambiguity rather than source-order shadowing;
- exact unique lookup with explicit NOT FOUND / AMBIGUOUS failures;
- catalog construction does not load Skill bodies;
- activation reuses full-directory drift protection;
- v1 `SkillTrustState` contains only `UNASSESSED`.

Important authority decision:

> Discovery/provenance is not approval. The catalog currently has no mechanism to mark a Skill trusted/approved, because the reviewed trust lifecycle does not exist yet.

## Next safe Skills step

Before autonomous Skill routing, build the frozen Skill-selection evaluation corpus described in the Procedural Knowledge & Skills roadmap.

Required case classes:

- clear positives;
- clear negatives / no-Skill tasks;
- near misses;
- paraphrases;
- vocabulary-shift cases;
- hard negatives;
- multi-Skill / ambiguous cases.

Measure at minimum:

- precision;
- recall;
- false activation;
- missed activation;
- no-Skill abstention;
- ambiguity handling;
- context overhead when routing is eventually evaluated.

Do **not** add autonomous model-based Skill selection first and promise to evaluate it later. The historical MAPS retrieval failure is the reason the eval corpus comes first.

## Still intentionally unresolved

Durable late session attachment / replacement lineage remains unresolved by design.

Do not add mutable convenience state around immutable `run_manifests.session_id` until reconciliation semantics answer:

- initial session versus current session meaning;
- late attachment;
- replacement lineage;
- uniqueness/conflict handling;
- authority if records disagree;
- trace/recovery/review-independence consumption.

## Resume checklist after context loss

1. Read the three 2026-08-15 working notes plus the exact task files for PRs #20–#26.
2. Confirm current GitHub PR heads/review results before stacking more work.
3. If no upstream review materially changed the contracts, next implementation target is the frozen Skill-selection evaluation corpus.
4. Keep trust/approval, automatic routing, executable Skill resources, and durable session-lineage state out until their respective gates are explicitly satisfied.
