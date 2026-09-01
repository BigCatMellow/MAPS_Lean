# PR #225 review evidence — SEC4/6.10 capability-manifest slice 2 (runtime capability intersection)

reviewer: maps-lean-nava
head_sha: edacadd33d4007bd390c02d68a0469a771994499
independent: true
summary: APPROVE — implements the design §5 slice at the `_select_skills` seam: the `capabilities` parser + tokens move to `format.py` (acyclic: `gate`→`format`, never reverse) with slice-1 gate behaviour byte-equivalent; `capability_policy.py`'s `declared ⊆ permitted` check matches the §4 table exactly and fails closed on unrecognized tokens / missing policy; an out-of-envelope Skill is DENY'd from the `maps flow start` plan before the trust gate (so never body-loaded) and counted under `coverage.memory_trust_gate_reasons["SKILL_CAPABILITY_OUTSIDE_TASK_ENVELOPE"]`; no MUST-NOT violated; SEC4/6.10/6.24 stay IN PROGRESS with the seam + `paid_execution`/`broad_architecture` gap stated; 108 targeted tests + smoke green; 8/8 mutations killed. NB: head_sha rebound by coordinator to the post-rebase commit (branch predated #221–#224; rebase clean, no checklist conflict).

## Criteria

| # | Criterion | Result |
|---|-----------|--------|
| 1 | Parser move `format.py` ← `gate.py`; import graph acyclic; slice-1 behaviour byte-equivalent | PASS. `_CAPABILITY_MANIFEST_FILENAME`, `_CAPABILITY_TOKENS`, `_SECRET_USE_RE`, `_MANIFEST_MALFORMED`, `_parse_capability_manifest` moved verbatim to `format.py` (+ new `_declared_capabilities_tuple`); `gate.py` imports them. `format.py` imports only stdlib — no `gate` import (`/usr/bin/grep` confirms) — graph is `gate → format` only. `_MANIFEST_MALFORMED` is a module-level `object()` sentinel imported into `gate`, so the identity check in the unmoved `_apply_capability_manifest` still compares the same instance. `tests.test_skill_capability_manifest` (31) + `tests.test_skills_quality_gate` (15) green. The new `declared_capabilities != descriptor.declared_capabilities` identity check is inert for a stable Skill and a no-manifest Skill. |
| 2 | `capability_policy.py` — `declared ⊆ permitted` + §4 mapping exact; DENY at the `_select_skills` DENY point, counted under coverage | PASS. `_BASELINE` = `{filesystem-read, filesystem-write, shell, network-read, github-read, database-read}`. `_REQUIRES`: `network-general/github-write/database-write → (external_side_effect,)`, `process-stop → (destructive_action,)`, `external-deploy → (external_side_effect, destructive_action)`. `secret-use:*` → `(security_sensitive,)`. `broad_architecture`/`paid_execution` unmapped (commented). Unrecognized token → `_required_flags` returns `None` → offending (fail closed). `capabilities_within_envelope`: `pol = policy or {}`, `any(not pol.get(flag) for flag in flags)` → offending. In `_select_skills`, after `if not matched: continue` and before the trust gate: `if not within: tally.record(MemoryAdmission.DENY, "SKILL_CAPABILITY_OUTSIDE_TASK_ENVELOPE"); continue`. `coverage.memory_trust_gate_reasons` (dict) exposes the reason string. |
| 3 | Property e2e — out-of-envelope Skill (`process-stop`, `destructive_action=False`) DENY'd from the plan | PASS. `CapabilityIntersectionPlanTests.test_out_of_envelope_skill_denied_from_plan`: real `build_project_skill_catalog` + `build_context_plan`, `plan["skills"] == []` + the reason present. Companions: `test_in_envelope_skill_surfaces` (`destructive_action=True` + `requires_operator_approval=True` so PR #211's `validate_ready` rule doesn't block), `test_baseline_only_skill_unaffected_by_envelope`, `test_no_manifest_skill_unaffected_on_capability_axis`. DENY is before the trust gate and #221's body loading is in the post-trust-gate LOAD branch — an out-of-envelope Skill is never body-loaded. |
| 4 | MUST NOT — none violated | PASS. `task_policy` read only (`pol.get(flag)`), never written. `capability_policy.py` is frozen dicts + a pure function, no state, no store. Called from `_select_skills` (plan assembly), not a `HookRegistry` guard. `DestructiveExternalActionGuard` / `catalog.py` / `load_catalog_skill` not in the diff. No `SkillSourceKind`/`THIRD_PARTY` reference. `schema.sql` untouched. `_apply_capability_manifest` + slice-1 finding codes unchanged (only the parser moved). |
| 5 | Seam stated as `_select_skills` (luve note 2); `paid_execution`-unmapped gap line (luve note 3) | PASS. SEC4 row states the seam is `_select_skills` — not `load_catalog_skill`, which has no task context; slice-1's §5 assumed the wrong seam. 6.24 row + `capability_policy.py` docstring state the `paid_execution`/`broad_architecture` unmapped known gap. |
| 6 | Foreground unittest green + smoke 0; own min-5 mutation | PASS. Split foreground runs: `test_skill_capability_manifest` + `test_skills_format` + `test_skills_catalog` 67/67; `test_skills_quality_gate` 15/15; `test_context_builder` 26/26 = 108 (⊇ gela's 93). `runtime.smoke` → `"ok": true`, exit 0. |
| — | Checklist status flip | PASS — none. SEC4, 6.10, 6.24 all `IN PROGRESS` both sides. |

## Mutation testing (`capability_policy.py` + the `_select_skills` hook) — 8/8 KILLED

| # | Mutation | Result |
|---|----------|--------|
| M1 | `_BASELINE` drop `filesystem-write` | KILLED |
| M2 | `_REQUIRES["process-stop"]` → `("external_side_effect",)` | KILLED |
| M3 | `any(not pol.get(f) …)` → `all(…)` | KILLED |
| M4 | drop the `flags is None` guard | KILLED (TypeError; `test_unrecognized_token_is_offending_fail_closed` pins the correct return) |
| M5 | `return (not offending, …)` → `return (True, …)` | KILLED |
| M6 | `secret-use:` branch → `return ()` | KILLED |
| M7 | `_select_skills` hook `if not within:` → `if within:` | KILLED |
| M8 | drop the `continue` after the slice-2 `tally.record` | KILLED |

## Non-blocking notes

1. M4 manifests as a `TypeError` rather than a clean assertion failure — the guard is load-bearing and detected.
2. `secret-use:<name>` maps to `security_sensitive` for any `<name>` — coarse (design §4 acknowledges whole-class granularity).
3. A malformed-manifest Skill yields `declared_capabilities == ()` so it passes the slice-2 check, then is still DENY'd by the slice-1 `QUARANTINED` trust-gate path — no regression, design note states this.

## Verdict

APPROVE.
