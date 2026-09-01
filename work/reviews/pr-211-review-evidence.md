# PR #211 review evidence — SEC3/6.4 validate_ready destructive-envelope reauthorization rule

reviewer: maps-lean-nava
head_sha: f742116bbda83bbdeef9945af25d6beaf1fb9fa8
independent: true
summary: APPROVE — implements exactly the §4 "Smallest first slice" of the merged #208 design note; predicate correct for the 0/1 NOT NULL task_policy columns; all 5 mutations killed; targeted suites + runtime.smoke green (full suite is the CI gate); scope held to readiness.py + tests + one CAPABILITY_CHECKLIST.md evidence clause with no status flip.

## Criteria

| # | Criterion | Result |
|---|-----------|--------|
| 1 | Predicate `(destructive_action OR external_side_effect) AND NOT requires_operator_approval` | PASS. Exact code match. `task_policy` cols are `INTEGER NOT NULL DEFAULT 0 CHECK (IN (0,1))` (schema.sql:118-121) — never NULL, so 0/1 truthiness is the only case. Both disjuncts present. `policy is not None` guard handles a missing row. |
| 2 | Does NOT fire when `requires_operator_approval` set | PASS. `test_destructive_envelope_with_reauth_flag_passes_ready`: flag alone ⇒ `validate_ready.ok` and `promote_ready().ok`. |
| 3 | Does NOT fire for non-consequential tasks | PASS. `test_non_consequential_task_unaffected_by_reauth_rule` (both flags false) ⇒ ok. |
| 4 | Integrates with reason-list / NEEDS_SHAPING machinery (promotion actually blocked) | PASS. Reason appended to the same `reasons` list; `test_destructive_envelope_without_reauth_flag_fails_ready` asserts `agi_status == "AGI FAIL — NEEDS_SHAPING"` AND `promote_ready(task_id).ok is False`. Not cosmetic. |
| 5 | Scope discipline | PASS. Files = exactly `runtime/state/readiness.py` (+23/-0), `tests/test_policy_state.py` (+58/-0), `work/roadmaps/CAPABILITY_CHECKLIST.md` (+1/-1). No schema.sql / run_manifests / new policy field / authority store / operator-identity registry / DestructiveExternalActionGuard change / new HarnessService.stop() caller. |
| 6 | CAPABILITY_CHECKLIST.md SEC3 row | PASS. Status stays IN PROGRESS; one evidence clause added noting the run-manifest snapshot stays deferred. No flip. |
| 7 | Interaction with guard OPERATOR_REAUTHORIZATION_ABSENT branch; no double-gating | PASS. Guard logic untouched; `tests.test_destructive_external_action_guard` 20/20 green incl. `test_in_envelope_no_approval_needed_allows_with_evidence`. Readiness (promotion-time) and the guard (runtime action-time) are orthogonal; the rule makes the guard's reauth branch reachable for the class it targets rather than adding a second gate. |
| 8 | No existing test regressed | PASS (targeted). `tests.test_policy_state` 9/9, `tests.test_task_environment_contract` 10/10, `tests.test_destructive_external_action_guard` 20/20, `tests.test_routing_policy` 27/27. Full suite exceeds this env's 2-min ceiling — CI is the gate. `runtime.smoke` exit 0. |
| 9 | Min-5 mutation on new predicate | PASS. 5/5 killed by `tests.test_policy_state`. |
| 10 | `unittest tests.test_policy_state` green foreground; `runtime.smoke` exit 0 | PASS. `Ran 9 tests OK` (~50s, blocking foreground). `runtime.smoke` → `"ok": true`, exit=0. |

## Mutation log (new predicate in `runtime/state/readiness.py`)

| # | Mutation | Result |
|---|----------|--------|
| M1 | `OR` → `AND` between the two envelope disjuncts | KILLED — FAILED (failures=2) |
| M2 | Drop `destructive_action` disjunct | KILLED — FAILED (failures=1, `test_destructive_envelope_without_reauth_flag_fails_ready`) |
| M3 | Drop `external_side_effect` disjunct | KILLED — FAILED (failures=1, `test_external_side_effect_without_reauth_flag_fails_ready`) |
| M4 | Invert reauth check (`and not policy[...]` → `and policy[...]`) | KILLED — FAILED (failures=3) |
| M5 | Negate the whole guard condition | KILLED — FAILED (failures=5) |

Worktree restored (`git checkout -- runtime/state/readiness.py`, `git status --porcelain` clean) after each mutation and at end.

## Notes / non-blocking

- Design-note STOP conditions checked: no schema change needed; no production code sets `destructive_action` without meaning "needs approval"; no autonomous `update_contract` path surfaced. None triggered.
- Behavior change (destructive-enveloped tasks that currently promote will now fail `validate_ready` until approved) is disclosed in the PR body and is the intended tightening per the note's "Not an operator-only decision".

## Verdict

APPROVE.
