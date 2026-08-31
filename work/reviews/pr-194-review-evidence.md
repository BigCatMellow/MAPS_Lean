# PR #194 — SEC3/6.4 first destructive-action guard wiring — independent review evidence

reviewer: maps-lean-hemo
head_sha: ffd7bf3e4bb2a52d8bbf3d4fc52db5e0ea3a9740
independent: true
summary: APPROVE. The 3 in-scope changes match the design note (incl. its "Implementation correction"); all 5 mutations against the guard decision logic are caught by the test suite; the live-task policy-read deviation is an acceptable, note-documented interim (approval boundary integrity preserved, zero production exposure) — not an exploitable hole and not a STOP condition; diff is in-bounds; no MUST-NOT violated; 6.4/SEC3 stay IN PROGRESS.

## Method

Own detached worktree at PR #194 head `eb41869d9d2202318e81ad95d3bb79e0db7769de`
(rebased to `ffd7bf3` onto `origin/main` `fbe88bc` for merge; code identical).
`git fetch origin` first. Every callsite/grep claim re-verified at HEAD (rule 14).
Source of truth: `work/notes/2026-08-31-sec3-guard-impl-readiness-design.md`
(In-scope table + Resume prompt + "Implementation correction") and parent
`work/notes/2026-08-24-sec3-destructive-action-hook-guard-design.md`.

## 1. Three in-scope changes vs note

### (a) `runtime/policy/destructive_action_guard.py` — HOLDS

- `__init__(self, source)` added; `source` duck-typed `get_task(task_id)`.
- `context["binding"]` extraction via `_binding_text` (mirrors
  `CanonicalRunGuard._extract_binding` intent); consequential action with no
  `task_id`/`run_id` → DENY `CLASSIFICATION_BINDING_REQUIRED`. Matches note.
- Unconditional `ACTION_AUTHORITY_ABSENT` branch replaced by the Q1 table:
  `destructive` vs `policy["destructive_action"]` and `external` vs
  `policy["external_side_effect"]` → DENY `ACTION_OUTSIDE_TASK_ENVELOPE`;
  `task_needs_human_reauthorization(task)` and not `_approved(task)` → DENY
  `OPERATOR_REAUTHORIZATION_ABSENT`; else ALLOW `ACTION_WITHIN_TASK_ENVELOPE`
  with `evidence_refs=(task:<id>, run:<id>, action_classes:<...>)`. Reuses
  `runtime.policy.evaluator._approved` / `task_needs_human_reauthorization` as
  the note directs.
- `CLASSIFICATION_REQUIRED` (missing key) / `CLASSIFICATION_INVALID` (non-bool)
  unchanged. Both-false → ALLOW `ACTION_NOT_CONSEQUENTIAL`.
- No `HookDirective.REQUIRE_APPROVAL` anywhere. Confirmed.
- Extra fail-closed codes not in the note's table but consistent with its intent:
  `ACTION_POLICY_UNAVAILABLE` (task unreadable / `None`). Acceptable — strictly
  more fail-closed, no ALLOW path added.

### (b) `runtime/harness/service.py` — HOLDS

- `_require_destructive_enforcement(event, operation)` → `OperationResult.failure(
  "DESTRUCTIVE_GUARD_REQUIRED", …, retry=UNSAFE)` when
  `not self.hooks.has_enforcement(event, HookEnforcement.DESTRUCTIVE_EXTERNAL_ACTION)`.
- `stop()` calls it for `HookEvent.BEFORE_DESTRUCTIVE_ACTION` **before** the
  existing `_require_canonical_enforcement(SESSION_STOPPING, "stop")`, then
  `self.hooks.run(BEFORE_DESTRUCTIVE_ACTION, self._context("stop", …,
  destructive=True, external=False))` and `self._hook_block("stop", …)` on
  `not …permitted`. Booleans are fixed literals in the `stop` path (no inference).
- `_context` extended with `destructive`/`external` kwargs, only set when
  non-`None`.

### (c) `runtime/recovery/production.py` — HOLDS

- `register_destructive_external_action_guards(registry,
  DestructiveExternalActionGuard(task_reader))` added to
  `build_canonical_harness_service` right after the canonical-guard registration;
  same `task_reader`, no second store.
- Docstring corrected: the "fired by nothing in `runtime/`" claim retired for the
  destructive event; `BEFORE_EXTERNAL_ACTION` still noted as dormant.

## 2. Deviation scrutiny (vara-flagged, rule 14) — JUDGMENT: acceptable interim, NOT a hole

The guard reads **both** envelope booleans and approval state from the live
`source.get_task(task_id)["policy"]`, not from a run-manifest snapshot as Q1
originally proposed.

- **This is documented, not undisclosed.** The note's "Implementation
  correction" section re-verifies at HEAD that `get_run_manifest()` carries no
  `policy` key (`runtime/state/integrity.py::_task_definition_conn` builds
  `definition["policy"]` only as a task-revision-hash input, never a
  `run_manifests` column) and explicitly resolves to the live-task read,
  observing that adding a manifest snapshot would be the schema change the note's
  own STOP condition forbids.
- **The approval boundary keeps its integrity.**
  `runtime/state/policy.py::_apply_policy_contract_conn` unconditionally resets
  `approved_by = NULL, approved_at = NULL` on *any* `task_policy` contract
  update (event `TASK_POLICY_UPDATED`). So a task cannot widen its own envelope
  booleans **and** retain a recorded human reauthorization — any self-mutation
  of policy drops approval, and an `OPERATOR_REAUTHORIZATION_ABSENT`-class task
  is back to needing a fresh `maps approve`.
- **Residual weakening (flagged, not blocking):** envelope-boolean integrity now
  rests entirely on `update_contract` caller authorization (pre-existing infra,
  explicitly out of scope for this PR per its MUST-NOT "no new authority
  field/store"). A task that can freely call `update_contract` to set
  `destructive_action=True` while keeping `requires_operator_approval=False`
  would self-authorize a destructive `stop()`.
- **Why this is not a STOP-condition security finding:** the guard is composed
  only inside the **default-off** `build_canonical_harness_service`, and its one
  firing site — `HarnessService.stop()` — has **no production caller** (verified:
  the only `service.stop(...)` / `self.service.stop(...)` calls added by this PR
  are in test files). There is zero live path today by which a task escapes
  enforcement. The theoretical escape depends on infrastructure that does not run
  in production and on `update_contract` authorization that predates this PR.
- **Recommended follow-up (for `miga` / roadmap):** before `HarnessService.stop()`
  gains a real production caller (the "recovery kill path" follow-up the note
  scopes out), either add the run-manifest `policy` snapshot (a deliberate,
  separately-authorized schema change) or confirm `update_contract` is
  operator-gated on the mutation path. Recorded here so it is not lost.

## 3. F1 fix — HOLDS

`runtime/routing/cli.py`: `approve.add_argument("task_id")` (positional),
`--approved-by` required, `--note` required; dispatched at `cli.py:138-141` as
`args.task_id` positional. Guard module docstring and the note both use
`maps approve <task_id> --approved-by <id> --note <why>` — matches the real
signature.

## 4. Checklist — HOLDS

`work/roadmaps/CAPABILITY_CHECKLIST.md`: SEC3 and 6.4 evidence text updated to
describe the second enforcement type + the `stop()` firing site + what is still
NOT built. **Both rows stay `IN PROGRESS`** — no status token changed
(`git show` on the checklist hunk: every changed row keeps `| IN PROGRESS |`).

## 5. MUST-NOT checks — ALL CLEAR

| Prohibition | Result |
|---|---|
| `BEFORE_EXTERNAL_ACTION` firing site added | NONE. Only `BEFORE_DESTRUCTIVE_ACTION` fired (in `stop()`). A guardrail test asserts `assertNotIn("HookEvent.BEFORE_EXTERNAL_ACTION", service_text)`. |
| Real production caller of `HarnessService.stop()` added | NONE. All added `stop(...)` calls are in test files. |
| Async approval bridge | NONE. DENY-only; `REQUIRE_APPROVAL` never returned. |
| `HookEnforcement.DESTRUCTIVE_EXTERNAL_ACTION` split | NO. Single combined member unchanged. |
| New policy field / authority store / `schema.sql` change | NONE. `git diff` touches no `runtime/state/schema.sql`, no new `POLICY_FLAGS`. |
| Inferred / static-analysis classification | NO. `stop()` sets fixed literal `destructive=True, external=False`. |

## 6. Mutation testing — 5/5 CAUGHT

Test module: `tests.test_destructive_external_action_guard` (20 tests, ~15s).
Each mutation applied to `runtime/policy/destructive_action_guard.py`, suite run,
then reverted.

| # | Mutation | Result |
|---|---|---|
| M1 | Destructive-envelope DENY inverted: `if destructive and not bool(policy.get("destructive_action"))` → drop `not` (allow when flag is False, deny when True) | **CAUGHT** — FAILED (failures=6) |
| M2 | External-envelope DENY inverted: `if external and not bool(policy.get("external_side_effect"))` → drop `not` | **CAUGHT** — FAILED (failures=1) |
| M3 | Binding-absent check neutralised: `if not task_id or not run_id:` → `if task_id and run_id and False:` (never deny `CLASSIFICATION_BINDING_REQUIRED`) | **CAUGHT** — FAILED (failures=1) |
| M4 | Operator-reauth check weakened: `if needs_reauthorization and not _approved(task):` → `and _approved(task)` (deny only when approved; allow the unapproved case) | **CAUGHT** — FAILED (failures=3) |
| M5 | Fail-closed broken: unreadable/missing task → instead of DENY `ACTION_POLICY_UNAVAILABLE`, synthesise `task={"policy":{"destructive_action":True,"external_side_effect":True}}` and proceed | **CAUGHT** — FAILED (failures=1) |

Guard file restored to `eb41869` state afterward (`git diff --stat` clean).

## 7. Suite + smoke

- `python3 -m runtime.smoke` → `{"ok": true}`, exit 0.
- `python3 -m unittest` (run per-module; full 5-module invocation exceeds the
  2-min shell cap, run individually):
  - `tests.test_destructive_external_action_guard` — 20 passed
  - `tests.test_harness_service` — 18 passed
  - `tests.test_harness_hooks` — 15 passed
  - `tests.test_recovery_composition_root` — 13 passed
  - `tests.test_recovery_supervisor` — 44 passed

## 8. Diff-in-bounds

`git diff origin/main...eb41869 --stat`: 3 runtime files
(`harness/service.py` +48, `policy/destructive_action_guard.py` +173/-…,
`recovery/production.py` +22), 3 test files, the design note (+37), and
`CAPABILITY_CHECKLIST.md` (+4/-4 evidence text). No `schema.sql`, no new
authority store, no `main` touch. Within the dispatch OUTPUT BOUNDARY.

## Verdict

APPROVE. No CHANGES REQUESTED. No mutation survived. The live-task policy read is
an acceptable, note-sanctioned interim with the approval boundary intact and no
production exposure; a follow-up to restore envelope tamper-evidence before
`stop()` gets a real caller is recorded for `miga`. STOP condition not triggered
— no live path lets a task escape destructive-action enforcement.
