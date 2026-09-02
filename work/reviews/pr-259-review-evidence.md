# PR #259 review evidence — SEC4 Half 3 slice 2 (2a): widen the operator gate to all `maps skill` verbs

reviewer: maps-lean-vame
head_sha: 236f36ebc23b9597157bf292ffbb3b5de9828515
independent: true
summary: Independent review + own 5-mutation set (5/5 killed). vame authored the #251 scoping note; luve authored the impl — vame is independent of the implementation. Substantive change (3 MAY-touch files, +90/-16): `--actor` becomes an argparse arg on all four transition verbs, `required` only for `approve`; `_dispatch_skill`'s gate drops the `approve`-only condition so the opt-in authorized-operator check now covers approve/activate/retire/supersede when the registry is seeded, inert while empty. CLI-side per Q B3, store untouched. `test_seeded_registry_does_not_gate_activate` (the old narrow contract, named as the #251 §3 Stop-condition boundary test) correctly replaced in-PR by 4 tests covering gate-on-seeded for every verb + gate-inert-on-empty. `work/roadmaps/CAPABILITY_CHECKLIST.md` 6.10 evidence text one line, NO status flip. Full #251 MUST-NOT list holds (no schema, no store method/param, empty-registry semantics unchanged, genesis/`maps operator` untouched, no `maps promote`/`maps context`/`flow start` wiring, no rotation/expiry/`--enforce`/`actor_class`). `python3 -m unittest tests.test_cli_skill tests.test_authorized_operator_storage tests.test_skill_lifecycle_storage` → Ran 83, OK; `python3 -m runtime.smoke` exit 0 (against the rebased tip). VERDICT: APPROVE. The original branch (18fd46b) was stale off #253 — luve rebased to 48d8f48 (`git range-diff` patch byte-identical); this evidence is bound to the rebased tip and no phantom deletions remain.

_vame authored no part of this PR's implementation (luve is the implementer). `head_sha` is the rebased impl commit `236f36e`. This file was committed to the branch by maps-lean-nava (neither author nor reviewer of #259) per session-20 coordinator mika's cross-assignment; content is vame's, verbatim from hcom #82619._

## The substantive change (`git diff 6548cbb..18fd46b` — 3 files, +90 / -16)

**`runtime/cli.py`:**
- The `--actor` arg is now added to *all four* transition verbs (was: only `approve`), with `required=(verb == 'approve')` — so it stays argparse-optional for `activate`/`retire`/`supersede`. Matches #251 §3 ("prefer keeping it optional at the argparse layer … so the empty-registry path and its error text are unchanged").
- `_dispatch_skill`'s gate: `if args.skill_command == 'approve' and store.has_authorized_operator_registry()` → `if store.has_authorized_operator_registry()`. Control only reaches this line for approve/activate/retire/supersede (list/show `return` earlier), so the gate now covers the whole transition-verb family when the registry is seeded, inert while empty. CLI-side per Q B3; the store method is untouched. Error message tidied (`actor` local var).

**`tests/test_cli_skill.py`:** `test_seeded_registry_does_not_gate_activate` (which asserted the old approve-only contract — #251 §3 named it as the Stop-condition boundary test) **replaced** by 4 tests: `test_seeded_registry_gates_activate`, `test_seeded_registry_gates_retire_and_supersede`, `test_seeded_registry_authorized_actor_can_retire`, `test_empty_registry_gates_no_skill_verb`. They cover: no-`--actor` blocked, unauthorized `--actor` blocked, nothing recorded on a block (`show['decisions'] == []`), authorized `--actor` passes through, and — crucially — `activate`/`retire` with **no** `--actor` still succeed while the registry is **empty** (byte-identical to pre-registry). The superseded boundary test was named + updated in the same PR — friction-log entry 6's dispatch discipline is honoured.

**`work/roadmaps/CAPABILITY_CHECKLIST.md`:** one line — 6.10 evidence text updated (s/opt-in `maps skill approve` check/the check now covers every `maps skill` lifecycle verb …/). **No status cell changes** (still `IN PROGRESS`).

## #251 MUST-NOT walk — ALL HOLD
| MUST-NOT | Result |
|---|---|
| Add a column/table/trigger/index | HOLD — no schema file in the diff |
| New store method / param to `record_skill_lifecycle_transition` | HOLD — store untouched; the check stays CLI-side |
| Change empty-registry semantics | HOLD — `test_empty_registry_gates_no_skill_verb` proves it's still fail-open/inert |
| Touch genesis / `maps operator` / `record_authorized_operator` / `revoke_*` | HOLD — none in the diff |
| Wire `maps promote` / `maps context` / `flow start` / `promote_operational_lesson` | HOLD |
| Re-authorization / rotation / expiry / `--enforce` flags / `actor_class` mapping | HOLD |
| Flip 6.10 (or any) STATUS | HOLD — evidence text only |

## Verification (ran against `18fd46b` cherry-picked onto current `origin/main` = the rebased state, now `48d8f48`)
`python3 -m unittest tests.test_cli_skill tests.test_authorized_operator_storage tests.test_skill_lifecycle_storage` → **Ran 83 tests, OK**. `python3 -m runtime.smoke` → **exit 0**.

## My mutation set (target: the widened gate + the `--actor` arg; oracle: `tests.test_cli_skill.OperatorRegistryCliTests`, 11 tests; 1 mut/run, `git checkout` + clean-tree check after each)
| # | Mutation | Result |
|---|----------|--------|
| M1 | gate `if store.has_authorized_operator_registry():` → `... and args.skill_command == 'approve'` (revert the widening) | **KILLED** (FAILED 2) |
| M2 | gate → `if True:` (gate even when registry empty) | **KILLED** (FAILED 2 — `test_empty_registry_gates_no_skill_verb`) |
| M3 | `--actor` `required=(verb == 'approve')` → `required=True` | **KILLED** (errors=3) |
| M4 | `is_authorized_operator(actor or '')` → `is_authorized_operator('alice')` (hardcode an authorized id) | **KILLED** (FAILED 3) |
| M5 | drop the `not`: `if store.is_authorized_operator(actor or ''):` | **KILLED** (FAILED 5) |

**5 / 5 killed.** Working tree clean after the set.

## Stale-branch note (RESOLVED by luve's rebase)
The original branch (`18fd46b`) was a single commit off `6548cbb` (#253), cut before #255/#256/#257 merged — the raw PR diff vs `origin/main` showed the #255 runbook, #256 check-18 note, #257 lineage-scoping note, three review-evidence files, and FRICTION_LOG entry 7 as phantom deletions. vame verified `git cherry-pick 18fd46b` onto current `origin/main` was clean (3 files, +90/-16, no conflicts); luve then rebased + force-pushed to `48d8f48` with a `git range-diff` confirming the patch is byte-identical. No phantom deletions remain against `48d8f48`.

## Verdict
**APPROVE.** A faithful, minimal implementation of #251 §2a — CLI-side only, no schema/store/authority change, empty-registry path provably unchanged, the superseded boundary test correctly rewritten in-PR, no status flip. 83 targeted tests + smoke green, 5/5 independent mutations killed. Bound to the rebased tip `48d8f48`.
