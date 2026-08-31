# Review: PR #192 — SEC4/6.10 Half 2: wire durable Skill lifecycle store into real behavior

- Branch: `impl/sec4-half2-authority-wiring`
- Reviewed head: `PENDING` (fill with reviewed commit SHA)
- Base: `origin/main` (`PENDING`)
- Reviewer: `PENDING` — must not have authored this PR, PR #190, or the parent note
- Verdict: `PENDING`

## 0. Method

<!-- Re-derive every claim at the reviewed head with git / grep / a real
temp-file TaskStore. Do not accept anything from the PR body. -->

## 1. Scope check

<!-- `git diff origin/main...HEAD --name-only`: runtime/skills/catalog.py,
runtime/skills/__init__.py, runtime/trust.py, runtime/context_builder.py,
runtime/policy/memory_trust_gate.py, runtime/state/skill_lifecycle_storage.py
(docstring only), work/roadmaps/CAPABILITY_CHECKLIST.md, and the four test
files + this evidence file. NO change to runtime/skills/lifecycle.py,
runtime/state/schema.sql. `git diff --check` clean. -->

## 2. Claims to re-verify

- [ ] `SkillTrustState` is gone; `grep -rn SkillTrustState runtime/` returns only
      docstring mentions in `lifecycle.py` (untouched, known nit) + `trust.py`
      comment + `context_builder.py` comment.
- [ ] `register_skill_catalog` calls `assess_skill` + `record_skill_lifecycle_subject`,
      skips entries with an existing subject row, returns `MutationResult` list.
- [ ] `build_skill_catalog(store=None)` → every `lifecycle_state` is `None`;
      identical `SkillCatalog` behavior vs `origin/main` for the no-store path.
- [ ] `skill_lifecycle_trust_class` is the only Skill→`MemoryTrustClass` projection;
      derivation is one-directional (store → provenance → trust class, no write-back).
- [ ] `SkillCatalog.fingerprint` no longer depends on lifecycle/trust state;
      still changes on content edit (via `content_sha256`). Zero consumers repo-wide.
- [ ] `load_catalog_skill(entry, store)` raises for QUARANTINED/RETIRED/SUPERSEDED,
      allows VALIDATED/APPROVED/ACTIVE/None; `store=None` unconditional.
- [ ] `_select_skills` admission outcome for an unassessed Skill is unchanged
      from `origin/main` (OBSERVATION → ON_DEMAND + withheld_reason).
- [ ] `record_skill_lifecycle_transition` still has no non-test production caller.

## 3. Verification commands

<!-- python3 -m unittest tests.test_skills_catalog tests.test_trust
tests.test_context_builder tests.test_skill_lifecycle
tests.test_skill_lifecycle_storage tests.test_skills_selection_evaluation ;
python3 -m runtime.smoke -->

## 4. Findings

## 5. Verdict
