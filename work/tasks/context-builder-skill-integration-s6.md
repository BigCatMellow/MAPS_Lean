# Task: Context Builder Skill selection integration (S6)

- Status: `READY_FOR_REVIEW`
- AGI status: `AGI READY`
- Type: `IMPLEMENTATION`
- Owner: `Claude / implementation agent`
- Risk: `MEDIUM`
- Goal: surface applicable, trust-labeled Skills as attributed evidence in `build_context_plan()`'s returned plan, with an explicit selection reason per Skill, without letting unrelated Skills enter context and without treating Skill content as authority or instructions.

## Inputs and source of truth

- Inputs: `AGENTS.md`; `work/roadmaps/agent-harness-capabilities/02-procedural-knowledge-and-skills.md` section 19 `S6` ("Load selected Skills progressively with selection reasons and trust labels. Exit gate: unrelated Skills demonstrably stay out of context."); `runtime/skills/catalog.py`; `runtime/skills/format.py`; `runtime/context_builder.py`; `tests/test_context_builder.py`.
- Authoritative sources: `runtime/skills/catalog.py` (`SkillCatalog`, `SkillCatalogEntry`, `SkillProvenance`, `SkillTrustState`) and `runtime/skills/format.py` (`SkillDescriptor`) are reused unmodified as the only source of Skill identity/provenance/trust metadata. `runtime/context_builder.py`'s existing `guidance`/`withheld_guidance` pattern (added for operational-learning lessons) is the structural precedent for how new attributed-evidence fields are added: a fail-closed helper, a new sibling key in the returned dict, never spliced into `boundaries` or instructions.
- Dependencies / preconditions: none blocking. `work/roadmaps/CAPABILITY_CHECKLIST.md` (PR #105) is not present on `main` as of this branch's base commit (`3b0ef8c`), so the S6/6.9 checklist-row update step is deferred rather than performed in this PR — see "Follow-up" below.

## Design note: selection heuristic and metadata gap

`SkillDescriptor` (from `runtime/skills/format.py`) intentionally exposes only `name`, `description`, resource path groupings, and `declared_metadata_keys` (a list of *frontmatter key names present*, not their values — the format layer deliberately does not interpret custom YAML fields, per its own docstring). Unlike operational lessons (`runtime/operational_learning.py`'s `applicability` block: `project_ids`/`task_types`/`risk_levels`/`path_prefixes`), Skills have **no structured applicability metadata yet**. That is out of scope for S6 (it would mean changing `format.py`'s parsing contract, which this task must not touch).

Given that constraint, selection uses a conservative token-overlap heuristic over the only metadata that exists:

- Task signal tokens: `task_type`, `project_id`, and each output path's directory/file-stem segments (lowercased, length >= 3).
- Skill signal tokens: lowercased words (length >= 3) extracted from the Skill's `name` and `description`.
- A Skill is selected only if the two token sets intersect; the plain-language `selection_reason` names the exact overlapping token(s), so the evidence is auditable rather than a black-box score.
- No catalog entry, no task signals, or no overlap => empty `skills` list. Any exception during matching fails closed to `[]` (mirrors `_lesson_guidance`'s fail-closed behavior) rather than breaking the rest of the plan.

This is a v1 production-facing selector, not the eval-harness scorer in `runtime/skills/evaluation.py` (`evaluate_skill_selection` grades precision/recall against a frozen corpus of *predictions already made*; it has no selection logic of its own to call). S4's routing-evaluation work can replace this heuristic later without changing the `skills` list's shape.

## Trust label handling

Every catalog entry currently carries `SkillTrustState.UNASSESSED` (catalog discovery cannot mark anything trusted — see `catalog.py`'s own comment). A matched Skill still surfaces, but its `trust_state` is reported honestly (`"UNASSESSED"`), never hidden and never upgraded to imply vetting that hasn't happened. This mirrors how `guidance` entries carry `"GUIDANCE_ONLY"` rather than being presented as authority. Downstream consumers (a worker prompt assembler, a reviewer) can choose how much weight to give an `UNASSESSED` Skill; the Context Builder's job is only to attribute it truthfully, not to decide trust policy.

## Change boundary

- MAY CHANGE: `runtime/context_builder.py` (add a new fail-closed selection helper + `skill_catalog` keyword parameter + new `skills` sibling key in the returned plan), `tests/test_context_builder.py`, this task file.
- MUST NOT CHANGE: `runtime/skills/catalog.py`, `runtime/skills/format.py`, `runtime/skills/evaluation.py` selection/scoring logic, `boundaries`/instructions shape, task/policy/review state, CLI contract beyond an optional additive parameter if touched.
- MAY CHANGE IF NECESSARY: `runtime/cli.py` — only if needed to keep the `context` command working; no new CLI flag is required for this task (no bundled/production Skills root convention exists on `main` yet, so wiring a real catalog into the CLI is left for a follow-up once S7/production Skill sources are established). `build_context_plan()`'s `skill_catalog` parameter defaults to `None` so existing callers (including the CLI) are unaffected.
- OPERATOR APPROVAL REQUIRED: any change that would let Skill content become authority/instructions, any change that grants trust/approval during selection, any persistence of selection state.

## Decision authority

- Owner may decide: exact token-overlap heuristic, exact `skills` entry shape, fail-closed behavior on malformed/absent catalog input.
- Owner must escalate: any design where an unmatched Skill leaks into context, where Skill body/procedure text is loaded into the plan (only descriptor-level metadata is surfaced — no `load_skill`/`load_catalog_skill` call here), or where `trust_state` is misrepresented.

## Acceptance criteria

- [x] `build_context_plan()` accepts an optional `skill_catalog: SkillCatalog | None = None` keyword parameter; omitting it preserves prior behavior (`skills: []`) and all pre-existing tests pass unmodified.
- [x] When a catalog is supplied, each Skill whose name/description tokens overlap the task's signal tokens (task_type, project_id, output-path segments) appears once in `plan["skills"]`, carrying `skill_id`, `name`, `description`, `source_id`, `trust_state`, `selection_reason`, `catalog_key`.
- [x] A Skill with no overlapping signal is demonstrably absent from `plan["skills"]` — test asserts non-presence (not just that the matching Skill is present), with two catalog Skills where only one matches.
- [x] Skill content/instructions are never merged into `boundaries` or any instruction-bearing field; `skills` is a new sibling key, same pattern as `guidance`.
- [x] `load_skill`/`load_catalog_skill` (procedure body activation) is never called by the selection path — only descriptor/provenance metadata is read.
- [x] Malformed/missing task signal data or an empty catalog fails closed to `skills: []` rather than raising.
- [x] `trust_state` in each surfaced entry is the real value from `SkillProvenance.trust_state` (`UNASSESSED` in all current cases) — never silently upgraded or omitted.
- [x] Full test suite passes.

## Follow-up (not in this PR)

- `work/roadmaps/CAPABILITY_CHECKLIST.md` is not on `main` as of this branch's base; the S6/6.9 row update is deferred until that file merges. Whoever lands it next should mark S6 evidence as this PR.
