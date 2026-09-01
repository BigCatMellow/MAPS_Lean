# PR #215 review evidence — Design note: SEC4 capability-declaration manifest (slice 1)

reviewer: maps-lean-luve
head_sha: 5699d882f5b554a26926bd07228da23ac22c5f7c
independent: true
summary: Independent design-note review by maps-lean-luve (did not author — gela did). DESIGN ONLY, 1 file (work/notes/2026-09-01-sec4-capability-declaration-manifest-design.md, +439). All 7 verification points PASS. The asserted enforcement chain — new UNDECLARED_CAPABILITY BLOCK finding in assess_skill → QUARANTINE disposition → initial_transition_from_gate_report → QUARANTINED subject state → (a) load_catalog_skill refusal and (b) _select_skills → skill_lifecycle_trust_class → admit_memory_evidence DENY → dropped from context plan — was traced end-to-end against merged code and is real; the "no schema/storage/authority/hook change" claim holds (the full SkillGateReport is already persisted as JSON in the existing gate_report column). ~15 file:line citations spot-checked, all accurate, no stale copy from another note. §6 "Smallest first slice" is concrete enough to dispatch. The third-party self-authored-manifest trust root is genuinely flagged (§7 OPERATOR DECISION REQUIRED, not answered). No rule-12 overlap: manifest feeds SkillLifecycleState only, MUST NOT be read by any runtime guard or written to task_policy. runtime.smoke exit 0. head_sha rebound by coordinator after a clean single-commit rebase onto main (4396b4f → 5699d88); no content change from the reviewed 92f2d12 tree. VERDICT: APPROVE. 3 non-blocking notes, none gate merge.

## Setup
Worktree `.claude/worktrees/rev-215` off `origin/sec4-capability-manifest-design`. `git status` after checkout: clean. Branch = `sec4-capability-manifest-design`. All cited runtime files verified byte-identical to `origin/main`.

## Verification

### (1) STATUS = DESIGN ONLY; diff = 1 file — PASS
Line 3: "STATUS: DESIGN ONLY. Changes no runtime code, no schema, no checklist status." PR commit = 1 file, +439, 0 runtime/schema/checklist lines.

### (2) "slice 1 needs NO schema/storage/authority/hook change" — traced, PASS
Chain verified against merged code:
- `runtime/skills/gate.py:387-391` — any BLOCK finding ⇒ `disposition = QUARANTINE`. A new `UNDECLARED_CAPABILITY` BLOCK rides this unchanged.
- `runtime/skills/catalog.py:264-294` `register_skill_catalog` — `report = assess_skill(entry.descriptor)` (290, imported from `.gate_hardened` at 284) then `store.record_skill_lifecycle_subject(entry, report, …)` (292).
- `runtime/skills/lifecycle.py:151-164` `initial_transition_from_gate_report` — `QUARANTINE → QUARANTINED`, else `VALIDATED`.
- `runtime/state/skill_lifecycle_storage.py:189-266` — starting state derived from the report, never caller-supplied; persists `json.dumps(report.to_dict())` into the existing `gate_report` column. New finding code needs no new column.
- `runtime/skills/catalog.py:297-334` — `_NON_ACTIVATABLE_LIFECYCLE_STATES = {QUARANTINED, RETIRED, SUPERSEDED}`; `load_catalog_skill` raises when state is in that set (328).
- `runtime/context_builder.py:328-397` `_select_skills` → `runtime/trust.py:107/115` (`QUARANTINED → MemoryTrustClass.QUARANTINED`) → `runtime/policy/memory_trust_gate.py:68/101` (`QUARANTINED → MemoryAdmission.DENY`) → entry dropped on `decision.admission is DENY` (387), recorded under `coverage`.
No schema, no `skill_lifecycle_*` table change, no new authority store, no new `HookEnforcement` type.

### (3) citation accuracy / rule 14 — PASS
~15 citations spot-checked within stated ranges, exact where a single line is cited: `gate.py:262/272/342-351/386-391`, `catalog.py:284/229/264/297-303/306-334`, `lifecycle.py:151-164`, `skill_lifecycle_storage.py:189-266`, `trust.py:107`, `memory_trust_gate.py:68`, `format.py::SkillDescriptor` fields, 1c detector-severity table. Re-verification stated at `5230c73`; no stale copy from an adjacent note.

### (4) §6 "Smallest first slice" dispatchable — PASS
Gives a single concrete exit property, a 4-item impl surface naming exact functions/constants, a "verify — likely no change" note on `format.py`, the specific test modules, a checklist evidence clause with explicit no-status-flip, a bundled-Skill migration analysis, a schema-change analysis, and a paste-ready resume prompt with MUST-NOT list + 3 STOP conditions.

### (5) OPERATOR DECISION callout genuinely flagged-not-answered — PASS
§7 states the problem (THIRD_PARTY Skill's manifest authored by the same untrusted party), gives a "Recommended answer (not adopted here)" (slice 1 = BUNDLED only; defer to SEC4 Half 3 operator-decision batch), closes "This design does not answer it."

### (6) no rule-12 authority overlap with SEC3 — PASS
`task_policy` + `DestructiveExternalActionGuard` = per-task runtime authority; the manifest = per-Skill gate-time supply-chain metadata feeding `SkillLifecycleState` only. Design rule (§5): manifest MUST NOT be read by any runtime guard, MUST NOT be written into `task_policy`. The compose-with-`task_policy` intersection is an explicit later slice at a different seam.

### (7) runtime.smoke — PASS
`python3 -m runtime.smoke` → `{"ok": true}`, exit 0.

## Non-blocking notes
1. Branch was behind current main; coordinator rebased at merge-prep (PR commit itself is 1 file).
2. §6 impl item 2 (`format.py` recognizing the `capabilities` sidecar) is stated as "verify — likely no change" and is also a STOP condition. Appropriate uncertainty flagging.
3. Impl seam is `gate.py::assess_skill`, but `catalog.py` imports `assess_skill` from `gate_hardened` (re-exports + monkeypatches). Note calls this out in §1b; the impl task should confirm the re-export path picks up the new finding code.

## Verdict: APPROVE
