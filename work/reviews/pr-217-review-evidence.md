# PR #217 review evidence — Design note: 6.9/S6 progressive Skill-body loading (slice 1 scoped)

reviewer: maps-lean-nava
head_sha: 61765060c3deddb97461ed3a0c732398524ec342
independent: true
summary: APPROVE — verification-only review of a single design/scoping note; every load-bearing code citation checks out against origin/main HEAD (0056640) with only cosmetic ~1-line drift on two refs, the slice is a genuine deterministic increment (one param + one call in the existing LOAD branch, not a rewrite), the Resume prompt carries MAY/MUST-NOT + 7 acceptance criteria + verification commands, and the "strict subset of what load_catalog_skill permits" claim is verified true so no operator-authority question is opened.

## Criteria

| # | Criterion | Result |
|---|-----------|--------|
| 1 | Every code citation accurate against origin/main HEAD (rule 14) | PASS (2 cosmetic nits). `_select_skills` def at `context_builder.py:328`; its "load_skill/load_catalog_skill … never called" docstring ~335-338; call site `context_builder.py:533`; `plan["skills"]` at line 548; `if skill_catalog is None … return [], tally` at line 360; `load_catalog_skill(entry, store=None)` at `catalog.py:306-334` with QUARANTINED/RETIRED/SUPERSEDED refusal (`_NON_ACTIVATABLE_LIFECYCLE_STATES`, `catalog.py:297-303`); `load_skill`/`SkillDocument` in `format.py`; `flow_start.py` step-2 docstring at 108-109; `maps context` → `build_context_plan(store, args.task_id, repo_root=...)` at `cli.py:537`. Nit A: `build_context_plan` is line 416 not 415. Nit B: `admit_memory_evidence` in `_select_skills` is line 381 not 380. One-line drift, no effect on the argument. |
| 2 | Smallest slice is a genuine deterministic increment, not a rewrite | PASS. Slice: add `store` param to `_select_skills` (one call-site change at 533); in the `MemoryAdmission.LOAD` branch only, call pre-existing `load_catalog_skill(entry, store)` and attach `item["body"]`, fail-closed on `SkillCatalogError`/`SkillChangedError`/`SkillParseError`; one `coverage.skill_bodies_loaded` counter; one docstring fix. Every primitive consumed unchanged. |
| 3 | MAY/MUST-NOT scope + acceptance + verification present in the Resume prompt | PASS. §3c: explicit MAY-touch (5 files) + 11-item MUST-NOT. §3d: 7 pass/fail acceptance criteria. §3e: exact verification commands. Resume prompt restates MAY/MUST-NOT, the test set (one blocking foreground `unittest`), `runtime.smoke` exit 0, 3 STOP conditions. |
| 4 | No hidden operator-authority question — verify "strict subset of what load_catalog_skill already permits" | PASS. `load_catalog_skill` permits `{APPROVED, ACTIVE, VALIDATED, None}` (refuses `{QUARANTINED, RETIRED, SUPERSEDED}`). Slice calls it only for `MemoryAdmission.LOAD` Skills; lifecycle→trust→admission chain (`trust.py:105-109` → `memory_trust_gate.py:_ADMISSION_TABLE:57-68`) yields LOAD only for `{VALIDATED, APPROVED, ACTIVE}` — a strict subset; the refusal branch is never reached. Body prose is `content_sha256`-covered and SEC4/SEC5-linted at catalog-build. Plan is read-only/disposable. §5 "none required for slice 1" correct. |
| 5 | Diff scope | PASS. `git diff --stat origin/main...HEAD` = one file, the design note (+316). No runtime, no schema, no checklist. |

## Non-blocking

- Citation nits A/B (each one line off) — impl task should resolve `build_context_plan` / the `admit_memory_evidence` call by name at its own HEAD (Resume prompt already says re-verify).
- No mutation testing / no smoke run — correct: docs-only PR.

## Verdict

APPROVE.
