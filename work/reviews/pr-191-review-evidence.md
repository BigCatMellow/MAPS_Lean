# PR #191 review evidence

reviewer: maps-lean-lire (independent — did not author PR #191, the addendum it adds, or the parent SEC3 note; nova was assigned first but hit its session limit)
head_sha: 505227812374b1aa4a128c94cf83903ccb9b1440
independent: true
summary: APPROVE. Docs-only (`git diff --stat origin/main...HEAD` = the addendum + this evidence file; `git diff --check` clean). The addendum's central claim — that the parent note's behavior-question premises are stale because the guard, the enum member, the registration helper, the `task_policy` authority model, and `record_operator_approval` + a `maps approve` CLI all already exist — was re-derived at HEAD and is TRUE in every part. All six behavior questions carry an explicit decision and a named file/callsite for the impl PR. The flagged `HarnessService.stop()`-has-no-production-caller judgment call is honestly surfaced for gobi and its "include stop() now" recommendation is defensible (it mirrors how `.resume()` was wired ahead of a live caller in PRs #160/#180). Three non-blocking findings (F1–F3), none touching a decision or the scope boundary.

## Method

Fresh worktree at the PR head (`6709ca6`, whose only non-evidence commit is
`2562913`). Every existence claim in the addendum's "What already exists"
section and every line-number citation load-bearing for a decision was
re-derived with `grep`/`sed` against the working tree — nothing accepted from
the addendum's prose, the parent note, or the PR body. Scope checked first.

### Scope (pass)

- `git diff --stat origin/main...HEAD`: exactly
  `work/notes/2026-08-31-sec3-guard-impl-readiness-design.md` (+379) and
  `work/reviews/pr-191-review-evidence.md` (placeholder, +47). No `runtime/`,
  no `tests/`, no `runtime/state/schema.sql`, no
  `work/roadmaps/CAPABILITY_CHECKLIST.md`.
- `git diff --check origin/main...HEAD`: clean.

### Central "premises are stale" claim — re-derived at HEAD (all TRUE)

| Claim | Evidence |
|---|---|
| `HookEnforcement.DESTRUCTIVE_EXTERNAL_ACTION` is a real enum member | `runtime/harness/hooks.py:52`, directly below `CANONICAL_RUN` (`:51`) |
| Guard class + both-events registration helper exist, re-exported | `runtime/policy/destructive_action_guard.py:31` (`class DestructiveExternalActionGuard`), `:114` (`def register_destructive_external_action_guards`), `:129-130` (`for event in (BEFORE_DESTRUCTIVE_ACTION, BEFORE_EXTERNAL_ACTION): registry._register_enforcement(..., HookEnforcement.DESTRUCTIVE_EXTERNAL_ACTION)`); `runtime/policy/__init__.py:3,41` re-export |
| Current decision table: missing key → DENY `CLASSIFICATION_REQUIRED`; non-bool → DENY `CLASSIFICATION_INVALID`; `destructive or external` True → **unconditional** DENY `ACTION_AUTHORITY_ABSENT`; both False → ALLOW `ACTION_NOT_CONSEQUENTIAL` | `runtime/policy/destructive_action_guard.py:69-113` — verbatim match, including the `REQUIRE_APPROVAL`-deliberately-unused docstring note |
| `task_policy` authority model with the six booleans + `approved_by`/`approved_at`/`approval_note` | `runtime/state/policy.py:10-12,19,22` (`PolicyStateMixin`), `:66,81-82,101-114` (`task_policy` table, `get_task` default envelope) |
| Six booleans snapshotted into the run manifest, approval fields **not** | `runtime/state/integrity.py:58-79` — `SELECT requires_operator_approval, destructive_action, external_side_effect, security_sensitive, broad_architecture, paid_execution FROM task_policy`; `approved_by`/`approved_at` absent |
| `record_operator_approval` (+ `clear_operator_approval`) exists, event `HUMAN_REAUTHORIZATION_RECORDED` | `runtime/state/policy.py:163,210,222` |
| Reachable as a CLI `approve` command | `runtime/routing/cli.py:80-85` (subparser), `:138-142` (`record_operator_approval(args.task_id, approved_by=…, note=…)`) |
| `runtime/policy/evaluator.py` provides `_approved` + `task_needs_human_reauthorization` | `:19-21` (`_approved` = `bool(policy.get("approved_by") and policy.get("approved_at"))`), `:24-35` |
| `CanonicalRunGuard` is the pattern: `source` dep, `_extract_binding` → `BINDING_REQUIRED`, `_deny(code)` with `guard_code` annotation and no `evidence_refs`, ALLOW carries `evidence_refs=(task:…, run:…)` + `guard_code: CANONICAL_RUN_VERIFIED` | `runtime/policy/harness_guard.py:27-28,37,51,59-62,74,79,199,232-233` |
| `HarnessService` fires exactly five events, none destructive/external; each preceded by `_require_canonical_enforcement` | `runtime/harness/service.py:64` (`_require_canonical_enforcement`), `:175-198` (RUN_STARTING/RUN_STARTED), `:247-254` (BEFORE_SEND), `:294-301` (BEFORE_RESUME), `:327-334` (SESSION_STOPPING). `grep BEFORE_DESTRUCTIVE_ACTION\|BEFORE_EXTERNAL_ACTION runtime/harness/service.py` → no hits |
| `HarnessService.stop()` has no production caller | `stop` defined `service.py:313`; production `RecoverySupervisor` calls only `self.harness_service.resume(binding, session_ref)` (`runtime/recovery/supervisor.py:428`). No `harness_service.stop(` / `service.stop(` anywhere in `runtime/` |
| `build_canonical_harness_service` declines to register the destructive guard, docstring says so | `runtime/recovery/production.py:364-366` ("The destructive-external-action guard … the two Hook events it would subscribe to are fired by nothing in `runtime/`") |
| Evidence propagation for Q5 already wired | `runtime/harness/service.py:137` (`evidence_refs=result.evidence_refs`), `runtime/harness/hooks.py:162-164` (`HookRunResult.evidence_refs` aggregates), `runtime/run_record.py:93-98` (`destructive_action` / `external_side_effect` / `approved_by_present`) |

### Six behavior questions — each has an explicit decision + named file (pass)

- **Q1** — DECISION: consult `task["policy"]` via the guard's new `source` dep
  (envelope booleans from `source.get_run_manifest(run_id)["policy"]`, approval
  state from `source.get_task(task_id)["policy"]`); no new field, not
  `ExecutionBinding`. Replacement decision table specified
  (`ACTION_OUTSIDE_TASK_ENVELOPE` / `OPERATOR_REAUTHORIZATION_ABSENT` /
  `ACTION_WITHIN_TASK_ENVELOPE`). File: `runtime/policy/destructive_action_guard.py`
  (`__init__`, `__call__`). Sound — reuses `evaluator._approved` /
  `task_needs_human_reauthorization` rather than re-deriving, and the
  manifest-vs-live split is forced by the verified fact that the manifest
  snapshot omits approval fields.
- **Q2** — DECISION: `HarnessService.stop()` fires `BEFORE_DESTRUCTIVE_ACTION`
  with `{destructive: True, external: False}` as a fixed literal at the
  operation; add `_require_destructive_enforcement`; register the guard in
  `build_canonical_harness_service`. `BEFORE_EXTERNAL_ACTION` gets no firing
  site. Files: `runtime/harness/service.py`, `runtime/recovery/production.py`.
  Sound — `stop` is definitionally destructive so the hard-coded booleans are
  declaration-at-the-call-site, not inference, matching the parent note's
  non-goal on inferred classification.
- **Q3** — DECISION: keep the one combined enum member, no split. No impl
  change. Sound — the Q1 table branches per-flag against independent policy
  booleans, so one guard object does not conflate the two classes.
- **Q4** — DECISION: DENY `CLASSIFICATION_REQUIRED` (already in code, already
  unit-tested); add a service-path test. File: `tests/test_harness_service.py`
  (or composition-root test). Sound.
- **Q5** — DECISION: mirror `CanonicalRunGuard` — `evidence_refs` on ALLOW
  only, `guard_code` + `action_classes` annotations on DENY, no new evidence
  stream. File: `runtime/policy/destructive_action_guard.py`. Sound — parity
  with the verified `CanonicalRunGuard` behavior and the existing propagation
  chain needs no change.
- **Q6** — DECISION: DENY-only, code `OPERATOR_REAUTHORIZATION_ABSENT`; do NOT
  return `HookDirective.REQUIRE_APPROVAL`. Names the missing "X" (a
  hook-outcome → operator-prompt → resume bridge) as a separate roadmap item
  without designing it. File: `runtime/policy/destructive_action_guard.py`.
  Sound — the reasoning that `APPROVAL_REQUIRED` is currently in
  `_CANONICAL_DENIAL_CODES` and treated as a hard denial (so `REQUIRE_APPROVAL`
  would be a worse-labelled DENY with a non-existent escape hatch) is a correct
  read of the recovery supervisor's handling.

### In/out scope table + Resume prompt (pass)

The "In scope" table holds the impl to one guard + one (pre-existing) enum
member + one firing event, with a per-row Q mapping. "Out of scope" explicitly
excludes a `BEFORE_EXTERNAL_ACTION` firing site, a real `stop()` caller, the
async approval bridge, an enum split, any new policy field / authority store /
schema change, and inferred classification. The Resume prompt is a
self-contained second-person section with the file list, the MUST-NOT list, a
single blocking-foreground test command, and stop conditions.

## Non-blocking findings

**F1 (impl-PR accuracy).** The addendum's Q6 operator-workflow text and the
Resume prompt write the approval command as
`maps … approve --task-id <T> --approved-by … --note …`. The real CLI
(`runtime/routing/cli.py:83`) takes `task_id` as a **positional** argument:
`maps approve <TASK_ID> --approved-by … --note …`. The impl PR is told to
document this workflow in the guard docstring and PR description — it should use
the real syntax. Substance of Q6 is unaffected.

**F2 (citation drift, cosmetic).** A few line references have drifted by a line
or are approximate: the CLI `approve` dispatch is at `cli.py:138` (note says
`:137-142`); `HarnessService.stop()` is defined at `service.py:313` (note's
"`service.py:327-344`" points at the method body, not the `def`). Every
substantive mechanism the citations point to was verified present. The impl PR
is instructed to re-verify at its own HEAD (rule 14) regardless.

**F3 (judgment call — concur).** Wiring the gate into `HarnessService.stop()`
produces composed, tested code with no production caller (verified: production
calls only `.resume()`). The addendum flags this as UNKNOWN for gobi and
recommends including `stop()` now. I concur: it is the smallest honest firing
site, it keeps the guard from being dead code, and it mirrors the established
pattern in this repo where `.resume()`'s harness routing was wired in PRs
#160/#180 before a live caller existed. The alternative (guard policy wiring +
composition registration only, `stop()` firing as a follow-up) is also stated,
so gobi has a real choice. Not a blocker.

## Verdict

**APPROVE.** Docs-only, scope-clean, `git diff --check` clean. The premise the
whole addendum rests on — that the parent note is stale and the guard /
enum / registration helper / `task_policy` model / `record_operator_approval` +
`maps approve` all already exist — is verified true in full. All six behavior
questions have explicit, sound decisions with named files. F1–F3 are
non-blocking; F1 is worth fixing in the impl PR's documentation, F2 is cosmetic,
F3 is a judgment call the addendum already hands to gobi with a defensible
recommendation. Did not merge.
