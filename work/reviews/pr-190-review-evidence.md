# Review: PR #190 — SEC4/6.10 Half 2 design addendum (Q4–Q8)

reviewer: independent-reviewer-maps-lean-fido
head_sha: 523bf48a683d1d55f2d684c2d7132f0d9b4184c8
independent: true
summary: APPROVE. Design-only addendum, scope clean (one work/notes/ file + this evidence file, no runtime/ or tests/, git diff --check clean). Every factual claim in the note's "Re-verified facts at HEAD" section and its Q4–Q8 bodies was re-derived independently at the reviewed code commit 7b449f4 with git/grep — all TRUE. Q4–Q8 decisions are sound and the rule-12 collapse (delete SkillTrustState; strictly one-directional store → provenance → trust-class chain) is the correct resolution. Two non-blocking nits recorded in the Method section for the implementation PR to sweep. Reviewer did not author PR #190 or its parent note (2026-08-25-sec4-skill-lifecycle-persistence-design.md).

- Branch: `sec4-half2-authority-wiring-design`
- Reviewed code commit: `7b449f4` (`SEC4/6.10 Half 2 design addendum: authority wiring + first refusal (Q4-Q8)`); HEAD `971b27d` is the evidence-only placeholder commit.
- Base: `origin/main` `84cc3f7`
- Verdict: APPROVE (non-blocking nits only)

## 0. Method

Every claim below was re-derived at `7b449f4` with `git` / `/usr/bin/grep`, not
accepted from the PR body or the note's prose (rule 14). Two non-blocking nits
for the implementation PR:

1. Stale references to the to-be-deleted `skill_trust_class()` remain in prose
   that the Q6 scope table does not list: `runtime/policy/memory_trust_gate.py:47`
   comment and `runtime/skills/lifecycle.py` docstring. The impl PR should sweep
   comment/docstring references alongside the code deletion.
2. After the Q6 collapse every `SkillLifecycleState` member is mapped in
   `_SKILL_LIFECYCLE_STATE_TO_MEMORY_TRUST_CLASS` and the only unmapped input is
   `None` (guarded at the call site), so `context_builder`'s existing
   "unmappable trust_state → DENY / dropped-and-counted" branch becomes
   unreachable dead code. Harmless, but the impl PR should either remove it or
   note it as deliberately retained.

Neither nit affects the design decisions; both are implementation-PR hygiene.

## 1. Scope check — PASS

- `git diff --name-only origin/main...7b449f4` = exactly
  `work/notes/2026-08-31-sec4-half2-authority-wiring-design.md` (+402 lines).
  HEAD adds only `work/reviews/pr-190-review-evidence.md`.
- `git diff --check origin/main...HEAD` — clean.
- No `runtime/` code, no `tests/`, no `work/roadmaps/CAPABILITY_CHECKLIST.md`.

## 2. Factual claims — ALL VERIFIED TRUE at 7b449f4

- `build_skill_catalog()` — zero production callers. Outside `tests/`, only the
  definition (`runtime/skills/catalog.py:160`) and the `__init__.py` re-export.
- `SkillCatalog.fingerprint` — zero readers anywhere. Only the field definition
  and digest write (`catalog.py:98,128`) plus two test assertions
  (`tests/test_skills_catalog.py:92,104`). Unrelated `environment.fingerprint`
  hits are a different module.
- `runtime/cli.py:373` and `runtime/flow_start.py:80` call `build_context_plan`
  with no `skill_catalog` argument — confirmed; `_select_skills` gets `None` and
  returns `[]` in every production flow.
- Half-1 store methods (`record_skill_lifecycle_subject`,
  `record_skill_lifecycle_transition`, `get_skill_lifecycle_state`,
  `list_skill_lifecycle_decisions`, `list_skill_lifecycle_subjects`) — zero
  non-test callers; only definitions in
  `runtime/state/skill_lifecycle_storage.py` and docstring mentions.
- `SkillTrustState` (`catalog.py:30`) — exactly one member `UNASSESSED`.
  `SkillProvenance.trust_state` (`catalog.py:73`) defaults to it and is never
  reassigned; the only reads are `context_builder.py:356,372` and the fingerprint
  digest tuple at `catalog.py:121` (note says "~118" — actual line 121, trivial).
- No operator-identity registry — `grep` for `operator_identity` /
  `OperatorIdentity` / `operator_registry` / `authorized operator` returns only
  prose in `skill_lifecycle_storage.py:14` and `skills/lifecycle.py:124`.
- `runtime/trust.py` holds three read-only mappings:
  `_SKILL_TRUST_STATE_TO_MEMORY_TRUST_CLASS` (1 entry, `:84`),
  `_SKILL_LIFECYCLE_STATE_TO_MEMORY_TRUST_CLASS` (all 7 `SkillLifecycleState`
  members: DISCOVERED/VALIDATED/QUARANTINED/APPROVED/ACTIVE/SUPERSEDED/RETIRED,
  `:123-131`), `_OPERATIONAL_LEARNING_STATUS_TO_MEMORY_TRUST_CLASS` (`:166`).
  `skill_lifecycle_trust_class()` (`:134`) is a real-enum-only projection.
- `load_catalog_skill()` (`catalog.py:187`) — zero production callers; re-export
  + docstring mentions only.
- Half-1 schema (`runtime/state/schema.sql`) — `skill_lifecycle_subjects`
  immutable with `initial_state IN ('VALIDATED','QUARANTINED')` and
  no-update/no-delete triggers; `skill_lifecycle_decisions` append-only,
  `REFERENCES skill_lifecycle_subjects(catalog_key)`, actor CHECK on
  `-> APPROVED`. Matches the note's summary; no schema change proposed.

## 3. Decision soundness — Q4–Q8

- **Q4** (subject creation at catalog-build time via a new idempotent
  `register_skill_catalog`): sound. Matches the parent note's gate-driven design;
  correctly rejects first-activation (the activation path is unreachable) and an
  operator command (subject creation records a fact, it is not the `-> APPROVED`
  decision that needs an operator).
- **Q5** (actor stays structural; read side owns enforcement; operator identity
  deferred to a named Half 3): sound. Matches the `promote_operational_lesson`
  precedent verbatim and respects the rule 9/10 scope boundary — an operator
  registry is genuinely unbounded and not required for "persisted state gates
  something".
- **Q6 / rule 12** (delete `SkillTrustState`; `SkillProvenance` carries
  `lifecycle_state: SkillLifecycleState | None`; single one-directional chain
  store → provenance → `MemoryTrustClass`): correct and the strongest part of the
  note. It removes a genuinely redundant, independently-editable second
  vocabulary rather than adding a fourth mapping. The `None → OBSERVATION`
  call-site guard preserves today's unassessed-Skill admission outcome exactly.
- **Q7** (keep lifecycle state OUT of the fingerprint; stop hashing the trust
  field): sound, and the load-bearing reason is right — folding store-derived
  state into the fingerprint would make it non-reproducible from a filesystem
  checkout alone, breaking the one property it exists for. Zero consumers means
  no downstream breakage. The round-trip test still holds; the content-change
  test still holds via `content_sha256`.
- **Q8** (no `superseded_by` column/FK; successor `catalog_key` in `decision_ref`
  free text): sound, confirms the Half-1 choice, avoids the first edge of a
  knowledge graph (roadmap §7.6 non-goal).

## 4. Other checks

- In-scope / out-of-scope table is concrete and each row names a file. The
  out-of-scope list correctly fences off the operator-identity registry, the
  capability-declaration manifest, any schema change, `runtime/skills/lifecycle.py`,
  and committing `cli.py`/`flow_start.py` to build a catalog.
- The note is honest that finishing Half 2 still leaves SEC4 partially complete
  and the "first real refusal" has no production caller yet.
- Resume prompt is self-contained, second-person imperative, names every file to
  touch and every file not to touch, carries a foreground-only verification
  command and explicit stop conditions. Paste-ready.
- No `CAPABILITY_CHECKLIST.md` change in this PR is correct (design-only, no
  status flip); the note correctly defers the 6.10/SEC4 evidence-text edit to
  the implementation PR.

## 5. Verdict

**APPROVE.** Scope-clean design-only addendum; all factual claims independently
verified at `7b449f4`; Q4–Q8 decisions and the rule-12 collapse are sound. The
two nits in §0 are non-blocking implementation-PR hygiene.
