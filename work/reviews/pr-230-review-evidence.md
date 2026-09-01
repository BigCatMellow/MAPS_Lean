# PR #230 review evidence — 6.9/S6 slice 2 (execution-level) scoping note

reviewer: maps-lean-luve
head_sha: 843f0021ea9ae873795d8cb1e039054e0d9d3923
independent: true
summary: Independent verification-only review by maps-lean-luve (did not author — gela did). DESIGN ONLY, 1 file (work/notes/2026-09-01-6.9-slice2-execution-level-design.md, +360), no runtime/schema/checklist change. All 6 verification points pass. (1) The dispatch correction is ACCURATE against format.py at HEAD: SkillDescriptor carries resource PATHS only (resource_paths / script_paths / reference_paths / asset_paths / example_paths, all tuple[str,...]); content_sha256 is a whole-directory digest; there is NO per-file sha256 or size field. The proposed fix (add resource_sizes at discovery via the existing file walk, defer per-resource sha256 to content_sha256 + load_skill_resource's whole-dir verification) holds together. (2) The smallest slice loads NO content in plan-assembly: item["execution_resources"] is a {path, kind, size} listing built from descriptor path tuples + resource_sizes (pure metadata); the single-file read is a new load_skill_resource(descriptor, relative_path) invoked by a downstream consumer, declared-path-only, _verified_snapshot hash-checked — the same shape as slice 1's load_catalog_skill body read, not search/retrieval; the 6.11 guardrail and wave12's "budget_class drives no loading" clause both hold. (3) No authority surface — a LOAD Skill already passed assess_skill's static script inspection; slice 2 loads no content and executes nothing; the gate is the unchanged control. (4) §4's body byte-budget ceiling is a RESTRICTION (omit item["body"], set body_withheld_reason) not an expansion; the flagged ~64 KB value is 2x the gate's 32 KB SKILL_BODY_TOO_LARGE REVIEW threshold (verified REVIEW not BLOCK) — reasonable, correctly flagged for reviewer judgement with §3 shipping independently. (5) NO checklist status flip, NO phase-1 runtime change. (6) smallest-slice + MAY/MUST-NOT + acceptance + verification + Resume prompt (with STOP conditions) all present; §8 does its own dispatch STOP-condition check (none triggered). VERDICT: APPROVE. 3 non-blocking review comments. NB: head_sha rebound by coordinator to the post-rebase commit (branch predated #228; rebase clean, design note only).

## Verification (rule 14)

### (1) dispatch correction — ACCURATE; proposed fix holds
`SkillDescriptor` fields: `resource_paths`, `script_paths`, `reference_paths`, `asset_paths`, `example_paths` — every one `tuple[str, ...]` of relative posix paths; plus `content_sha256: str` and `declared_capabilities` (#225). `_hash_snapshot` folds ONE sha256 over every file — a whole-directory digest. `_directory_hash` / `_verified_snapshot` `read_bytes()` every file. No per-file sha256, no per-file size field. The proposed remedy (add `resource_sizes` at discovery from the walk already done, defer per-resource sha256) is sound: `st_size` during the existing walk is no extra read; `content_sha256` + `load_skill_resource`'s whole-dir check is a sufficient integrity anchor for a single-file pull.

### (2) `_select_skills` loads NO content; not a guardrail violation
- The manifest branch builds `item["execution_resources"]` from descriptor path tuples + `resource_sizes` — pure metadata, no file read.
- `load_skill_resource(descriptor, relative_path) -> bytes` is a NEW `format.py` function, invoked by a downstream consumer, not by `_select_skills`: validates `relative_path ∈ descriptor` resource paths (rejects `SKILL.md`, traversal, absolute, undeclared), `_verified_snapshot` hash-check, returns one file's bytes. Deterministic named-file read — the same shape as slice 1's `load_catalog_skill` body read.
- 6.11 guardrail + wave12: the manifest is attached on the trust gate's `LOAD` decision (`context_builder.py:443`), exactly as slice 1's `item["body"]` — it does NOT make `budget_class` drive loading (wave12's escalation trigger). §3 MUST-NOT forbids content loading in `_select_skills` / `build_context_plan`, search, and `budget_class`-driven loading.

### (3) no authority surface — sound
A `LOAD`-classified Skill has already passed `assess_skill` at `register_skill_catalog` time — `gate.py` statically inspects every resource (`EXECUTABLE_RESOURCE_PRESENT`, `SCRIPT_NETWORK_ACCESS`, `NETWORK_PIPE_EXEC`, `_PRIVILEGE_RE`, `_DESTRUCTIVE_RE`); any BLOCK → `QUARANTINE` → not `LOAD`. Slice 2 attaches a listing only for gate-passed `LOAD` Skills, loads no content in plan-assembly, executes nothing. Gate unchanged. The dispatch STOP-condition ("execution-level loading needs an authority decision") does not fire.

### (4) §4 body-ceiling is a restriction; value reasonable
`gate.py` `_LARGE_SKILL_BODY_CHARS = 32_000`; `SKILL_BODY_TOO_LARGE` at `SkillGateSeverity.REVIEW` (not BLOCK) — so a large body on a VALIDATED Skill loads in full today. The proposed ceiling omits `item["body"]` and sets `body_withheld_reason = "BODY_EXCEEDS_BUDGET"` — same shape as slice 1's existing fail-closed path, a restriction not an expansion. ~64 KB (2x the gate's REVIEW threshold) is a sensible first value. Correctly flagged for reviewer judgement; §3 ships independently.

### (5) NO status flip, NO phase-1 runtime change
`git diff --stat`: 1 file, +360. STATUS: "DESIGN ONLY. Changes no runtime code, no schema, no checklist status."

### (6) slice structure complete
§3: concrete property; 5-item impl surface (`load_skill_resource` + `resource_sizes` field + identity checks; the `_select_skills` manifest branch + `skill_execution_resources_listed` counter; `flow_start` docstring; tests incl. end-to-end + ≥5 mutations; one 6.9/S6/6.11 checklist evidence clause). Explicit MAY / MUST NOT. Acceptance (6 items). Verification (blocking foreground unittest list + smoke + `git diff --stat`). Resume prompt with a MUST-NOT list + 2 STOP conditions. §8 self-check finds none triggered.

## Non-blocking review comments (do not gate merge)
1. §3 manifest key `"bytes"` holds the file *size* (an integer), not content. Recommend the impl name it `size_bytes` so a plan reader cannot misread it as file contents.
2. §4 ceiling as a constant — 64 KB is a fine first value; a later 6.11 slice may want it configurable.
3. §3 item 1's `stat().st_size` vs `resource_sizes` prose is tangled — conclusion is correct; worth the impl author tightening the reading before acting.

## Verdict: APPROVE
