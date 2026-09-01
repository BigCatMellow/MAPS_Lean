# PR #219 review evidence — SEC4/6.10 capability-declaration manifest for Skills, slice 1

reviewer: maps-lean-nava
head_sha: 48e62bf262ccf4d759565e4edc254988385bb913
independent: true
summary: APPROVE — implements exactly the design §6 slice: a `capabilities` sidecar parsed in `assess_skill` emitting the five §3-table findings at the specified severities, riding the unchanged gate→disposition→lifecycle→refusal/DENY chain; e2e test proves an undeclared-capability Skill is QUARANTINED and dropped from the flow-start plan; no MUST-NOT violated; no status flip; targeted suites + smoke green; 8/8 core-logic mutations killed (1 low-value end-anchor mutation survived — non-blocking). NB: head_sha rebound by coordinator to the post-rebase code commit (branch predated #217/#218).

## Criteria

| # | Criterion | Result |
|---|-----------|--------|
| 1 | Findings emitted exactly per §3 table; declared → INFO, undeclared → BLOCK | PASS. `_apply_capability_manifest` emits `DECLARED_CAPABILITY_USE` (INFO, replaces the detector finding), `UNDECLARED_CAPABILITY` (BLOCK), `CAPABILITY_MANIFEST_ABSENT` (REVIEW, only when a detector fired and no manifest exists), `CAPABILITY_MANIFEST_MALFORMED` (BLOCK), `OVER_DECLARED_CAPABILITY` (INFO). `_DETECTOR_CAPABILITY` is the 1c REVIEW-tier table inverted; BLOCK-tier detectors (`NETWORK_PIPE_EXEC`, `SENSITIVE_*`) deliberately excluded (comment + `test_block_tier_detector_is_not_downgradable_by_manifest`). Undeclared escalates REVIEW→BLOCK only when a manifest is present; absent → REVIEW, detector findings left at native severity. |
| 2 | Enforcement chain UNCHANGED; e2e test present | PASS. `assess_skill` disposition logic untouched — `_apply_capability_manifest` only adds findings before the existing dedup/sort/disposition block. `initial_transition_from_gate_report` / `record_skill_lifecycle_subject` not in diff. e2e `test_undeclared_capability_skill_is_quarantined_and_dropped_from_plan`: real `build_project_skill_catalog` → state `QUARANTINED`, then `build_context_plan(..., skill_catalog=catalog)` → `plan["skills"] == []`, `coverage.memory_trust_gate_denied >= 1`. Companion `test_declared_capability_skill_survives_into_plan_metadata` passes. |
| 3 | MUST NOT — none violated | PASS. Diff = `runtime/skills/gate.py` (+176), `tests/test_skill_capability_manifest.py` (+286), `work/roadmaps/CAPABILITY_CHECKLIST.md` (+2/-2). No `schema.sql` / `skill_lifecycle_*`. No `SkillDescriptor` field (sidecar from `by_relative` bytes). Manifest read only inside `assess_skill` — no runtime guard, not written to `task_policy`. `DestructiveExternalActionGuard` / `initial_transition_from_gate_report` untouched. No `THIRD_PARTY` reference. SEC3 + SEC4 rows both stay IN PROGRESS. |
| 4 | `gate_hardened` re-export picks up the new code | PASS. New logic lives inside `gate.assess_skill`; `gate_hardened` wraps `from .gate import assess_skill` and re-assigns `_gate_module.assess_skill`, so `catalog.py`'s `from .gate_hardened import assess_skill` gets it transparently. Confirmed by the e2e test reaching the gate via `build_project_skill_catalog` → `register_skill_catalog` → `gate_hardened.assess_skill`. |
| 5 | `_CAPABILITY_TOKENS` matches §5.1; `secret-use:` validator bounded | PASS. `_CAPABILITY_TOKENS` = the exact 11 §5.1 tokens. `_SECRET_USE_RE = ^secret-use:[a-z0-9][a-z0-9-]*$` — bounded charset, no backtracking shape. `test_malformed_secret_use_is_malformed` covers uppercase-reject. |
| 6 | Foreground unittest green; smoke exit 0 | PASS. Split foreground runs: `test_skill_capability_manifest` 18/18; `test_skills_quality_gate` + `test_skills_catalog` 51/51; `test_context_builder` + `test_cli_skill` 40/40; `test_flow_start` 12/12; `test_skills_quality_gate_metadata` 3/3. `runtime.smoke` → `"ok": true`, exit 0. |
| 7 | Own min-5 mutation pass (all killed) | PASS with 1 non-blocking survivor. 8 mutations on new logic, all killed by `test_skill_capability_manifest`: M1 BLOCK→REVIEW; M2 `detected - covered` → `covered - detected`; M3 `_declared_covers` → `return True`; M4 unknown-token malformed → `continue`; M5 always-suppress ABSENT; M6 MALFORMED BLOCK→INFO; M8 invert declared-downgrade; M9 DECLARED_CAPABILITY_USE INFO→REVIEW. Survivor M7: dropping the `$` end-anchor from `_SECRET_USE_RE` — `re.match` still start-anchors so `secret-use:UPPER` still rejected; only escape is a valid-prefix + trailing garbage. Low impact (BUNDLED-only, in-repo). Follow-up: add `secret-use:foo!` case or `re.fullmatch`. |

## Non-blocking notes

1. M7 survivor — `_SECRET_USE_RE` end-anchor untested; add a malformed case or use `re.fullmatch`.
2. Two `shell` detectors firing with `shell` declared → both downgraded to INFO; if `path` differs dedup keeps both. Cosmetic INFO noise, no disposition effect.
3. `assess_skill` is source-agnostic; "BUNDLED only" scope upheld by production reachability, not an explicit guard. Worth an explicit check when `THIRD_PARTY` sourcing lands.

## Verdict

APPROVE.
