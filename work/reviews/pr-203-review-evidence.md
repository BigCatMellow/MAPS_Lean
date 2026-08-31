reviewer: maps-lean-rev-gina
head_sha: 83a417bef257272cfde670babb97f6312677a688
independent: true
summary: APPROVE. Independent design review of PR #203 (SEC4 operator-lifecycle-transitions + operator-identity Half 3 design note, docs-only). Every existence/callsite claim in the note re-verified with /usr/bin/grep against the PR-head worktree and confirmed accurate. Item A (thin `maps skill` CLI over the existing store method) is sound and genuinely the smallest entrypoint; Item B (append-only `authorized_operators` registry, compose-authorized-now, opt-in-by-registry-non-empty, default byte-identical) is house-consistent with the operational_lessons / SEC3-opt-in patterns. MUST-NOT bars complete, OPERATOR-DECISION callout correctly left unpicked, STOP conditions and A1+A2 / B1 slicing appropriate. Diff in-bounds: the note + one CAPABILITY_CHECKLIST annotation line, no runtime code, no status flip. Three minor non-blocking findings recorded below.

# PR #203 — independent design review

**Verdict: APPROVE** (REQUEST-CHANGES not warranted; findings are minor/optional)

Reviewer: maps-lean-rev-gina — independent, did not author (pogo authored).
Coordinator: niko. Method: `reference_committee_review`, docs-only (no mutation testing).
Bound to note commit `83a417bef257272cfde670babb97f6312677a688`.

## Method

- Detached worktree at PR #203 head (`83a417b`); `git fetch origin main` first.
- `git diff --stat main...HEAD`: 2 files — `work/notes/2026-08-31-sec4-operator-lifecycle-transitions-and-identity-design.md` (+528, new) and `work/roadmaps/CAPABILITY_CHECKLIST.md` (+1/-1). No `runtime/` code. Confirmed in-bounds.
- Re-verified every existence / callsite / signature / schema claim in the note with `/usr/bin/grep` and `sed` against the worktree tree (rule 14).

## Per-claim verification

| Note claim | Verified | Evidence |
|---|---|---|
| `record_skill_lifecycle_transition(catalog_key, to_state, *, decision_ref, decided_by=None, now=None) -> MutationResult` exists, replay-in-txn write-gate | ✅ | `runtime/state/skill_lifecycle_storage.py:284-299` — signature byte-exact; docstring confirms in-txn replay |
| Result codes: `INVALID_CATALOG_KEY`, `INVALID_TARGET_STATE`, `INVALID_DECISION_REF`, `SKILL_SUBJECT_NOT_FOUND`, `ILLEGAL_SKILL_TRANSITION`, `SKILL_DECISION_CONSTRAINT_VIOLATION`, `SKILL_TRANSITION_RECORDED` | ✅ | grep of the method body — all seven present at lines 309/314/320/334/343/367/373 |
| **Zero non-test callers** of `record_skill_lifecycle_transition` | ✅ | `/usr/bin/grep -rn` in `runtime/` → only the def (`:284`) and a docstring mention (`:12`). No production caller. |
| `transition()` requires non-empty `actor` **only** for `(VALIDATED,APPROVED)` and `(QUARANTINED,APPROVED)` | ✅ | `runtime/skills/lifecycle.py:87-92` `_ACTOR_REQUIRED_TRANSITIONS` frozenset = exactly those two tuples; `:142-145` enforcement |
| `APPROVED->ACTIVE`, `QUARANTINED->RETIRED`, `ACTIVE->SUPERSEDED`, `ACTIVE->RETIRED` need no actor; `SUPERSEDED`/`RETIRED` terminal | ✅ | `_ALLOWED_TRANSITIONS` `:95-108` — APPROVED→{ACTIVE}, QUARANTINED→{APPROVED,RETIRED}, ACTIVE→{SUPERSEDED,RETIRED}, SUPERSEDED→∅, RETIRED→∅ |
| Schema `skill_lifecycle_decisions` at `schema.sql:795`; append-only (no-update/no-delete triggers); `decision_ref NOT NULL CHECK len 1..512`; `decided_by TEXT` nullable, 1..128 when present; `CHECK(from_state<>to_state)`; APPROVED-actor CHECK; `trg_..._no_post_terminal` | ✅ | `runtime/state/schema.sql:795-838` — every constraint/trigger present as described |
| `catalog_key` = `"<source_id>:<skill_id>@sha256:<content_sha256>"`, subject PK; edited Skill is a new subject | ✅ | consistent with `schema.sql:753` subjects table + prior SEC4 notes / checklist evidence |
| **No `skill` subcommand in `runtime/cli.py`** | ✅ | `/usr/bin/grep -n "skill" runtime/cli.py` → no matches |
| `maps flow start` → `build_project_skill_catalog(repo_root, store)` → `register_skill_catalog` → `record_skill_lifecycle_subject` is the only production write to Skill tables | ✅ | `runtime/flow_start.py:8,84`; `runtime/skills/catalog.py:229,260,264,292` |
| **No operator-identity / authorized-operator source anywhere in `runtime/`** | ✅ | `/usr/bin/grep -rnE "authorized\|operator_registry\|OperatorIdentity\|operator_identity\|is_authorized_operator" runtime/` → only prose in the two SEC4 modules + `lifecycle.py:127` ("separate concern for a future") + unrelated router/acquisition hits. No registry. |
| `outcomes.py` `VALID_ACTOR_CLASSES = {OPERATOR, CORE_AGENT, HELPER, SYSTEM, UNKNOWN}`, `actor_id` required when class ≠ UNKNOWN, descriptive-only (nothing verifies the id names a real principal) | ✅ | `runtime/state/outcomes.py:13,37-38,59-69` — validates membership + non-empty only; no lookup against any registry |
| `maps promote --actor <str>` + `promote_operational_lesson(promoted_by=...)` both unverified free strings; `promote_operational_lesson` has zero production callers | ✅ | `runtime/cli.py:97,355` (`store.promote_ready(args.task_id, actor=args.actor)`); `runtime/state/operational_learning_storage.py:210` def only, no `runtime/` caller |
| Read methods `list_skill_lifecycle_subjects(state=None)`, `get_skill_lifecycle_subject`, `list_skill_lifecycle_decisions`, `record_skill_lifecycle_subject` exist | ✅ | `runtime/state/skill_lifecycle_storage.py:431-439` (state filter validated as `SkillLifecycleState`), `:405`, `:423`, `:187` |
| CAPABILITY_CHECKLIST: one-line "design-pending" annotation on the SEC4 row, **no status flip** | ✅ | diff = single appended sentence citing this note; row stays `IN PROGRESS` |

All claims accurate. "Re-verified facts at HEAD `98620e4`" in the note matches the current `origin/main` tip.

## Judgement

- **(a) Item A soundness / smallest entrypoint** — YES. Every other operator action in `runtime/cli.py` (`promote`, `outcome-record`, `review-record`, `create`) is a thin `_emit(store.<method>(...))` wrapper; a Skill approval is the identical shape. One-verb-per-legal-edge (not a generic `transition <from> <to>`) is the right call — it keeps the actor requirement visible and prevents illegal-edge typos. The CLI correctly does **not** pre-check the edge (store replay decides `from_state`), respecting rule 12 — composition stays in exactly one place. `maps flow start` correctly rejected as the home (that would be auto-approval).
- **(b) Item B soundness / house-consistency** — YES. Append-only `authorized_operators` + `authorized_operator_revocations` with no-update/no-delete triggers, "authorized as of now" composed (never a mutable `active` column), genesis sentinel `added_by="GENESIS"` — this is the exact `operational_lessons` / `skill_lifecycle_*` shape already in the codebase. Opt-in-by-registry-non-empty (slice B5.4) = byte-identical to today when empty, matching the SEC3 `destructive: bool` / #198 `embedded: bool` "keep the structural field, add opt-in real check at one site, default off" resolution pattern the note explicitly mirrors. Config-file-as-canonical-store correctly rejected (rule 12 / no audit trail / repo-writer-editable).
- **(c) MUST-NOT bars complete** — YES. Covers: no implicit/default-on enforcement (stated twice, lines 388-390 and 397-399), no login/session/credential machinery, no retroactive validation of existing `decided_by`/`promoted_by`/`actor` strings, no schema change for Item A, no config-file/IdP/OS-user/signed-payload registry, no auto-approve on any evidence, no `maps context` write-on-read wiring, no `superseded_by` column, no scope-creep into the capability-declaration manifest.
- **(d) OPERATOR DECISION callout correctly unpicked** — YES. Trust root, genesis mechanism (init-time vs. separate step; arg vs. env vs. config), and empty-registry semantics (checks-disabled vs. all-blocked) are all surfaced as explicit operator decisions with a recommendation stated but *not* treated as decided. The note is honest that Item B's design "is valid for the most likely answer" and flags where a different answer changes things.
- **(e) STOP conditions + slicing** — YES. Six STOP conditions, each tied to a concrete design-violation signal (CLI composing state itself; resolver growing past the 3 cases; B blocked on the un-made decision; registry acquiring scoping/expiry/delegation; opt-in check requiring a default/test change; genesis needing a migration the impl isn't comfortable pre-deciding). Slicing A1 (read-only) + A2 (transitions) in one PR, B1 separate and gated on the operator decision, with the stated dependency chain (A2 needs A1's resolver; B1 needs A2) is appropriate and genuinely smallest-first.

## Findings (all minor / non-blocking)

1. **[minor] Resume prompt under-specifies the checklist-evidence update for the A-impl PR.** Line 519-521 says "Optionally annotate the CAPABILITY_CHECKLIST SEC4 row … no status flip". Given the standing friction pattern (`feedback_checklist_edit_repeatedly_skipped` — three PRs in one arc shipped code without updating checklist evidence text), the A1+A2 impl PR — which *does* ship runtime code and *does* land the first `record_skill_lifecycle_transition` caller — should treat the checklist evidence-text update as a MUST, not "optionally". Recommend niko/the implementer dispatch tighten this. Does not block the design note.
2. **[minor] Internal tension between Q B3 and Q B5.4 on where the identity check lives.** Q B3 (line 327) explicitly leaves "store method vs CLI" as "low stakes, implementer may pick" and *recommends* CLI-side; Q B5 slice 4 (line 361-362) then hard-codes the CLI-side "when at least one operator row exists" behaviour as the slice content. Not wrong — B5 is consistent with B3's recommendation — but B5 effectively decides what B3 frames as open. A one-line reconciliation ("per B3's recommendation, the check is CLI-side") would remove the ambiguity for the implementer.
3. **[minor / informational] Two new CLI-level result codes introduced.** `MULTIPLE_REVISIONS` and `AMBIGUOUS_SHA_PREFIX` (Q A3 / A6) are new codes the CLI resolver would emit as `MutationResult(False, ...)`. The note flags them "(new, CLI-level)" so this is not a hidden change, but the impl PR's tests should assert their exact strings so they don't drift. Already implied by the note's test list (line 227); noting for the reviewer of the impl PR.

## Diff-in-bounds confirmation

`git diff --stat main...83a417b`:
```
 work/notes/2026-08-31-sec4-operator-lifecycle-transitions-and-identity-design.md | 528 +++++++++
 work/roadmaps/CAPABILITY_CHECKLIST.md                                           |   2 +-
```
No `runtime/` code. No status flip (SEC4 row stays `IN PROGRESS`). Matches the dispatch's docs-only expectation.

## Checker

`python3 scripts/check_review_evidence.py 203` — run from the reviewer worktree after commit; expected GREEN (evidence file bound to `83a417b`, the code/design state under review).
