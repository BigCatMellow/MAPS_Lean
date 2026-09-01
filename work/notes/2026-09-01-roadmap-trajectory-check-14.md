# Roadmap trajectory check #14 — arc: `8c5455b..HEAD`

Fourteenth pass. Predecessor: `work/notes/2026-09-01-roadmap-trajectory-check-13.md`
(arc `4396b4f..HEAD`, PRs #215–#219, action **CONTINUE**, scoreboard 16/13/6 —
sixth consecutive pass unchanged).

## Arc derivation (commit range, per PR #212)

```
$ git log --oneline --grep='Roadmap trajectory check' main | head -1
8c5455b Roadmap trajectory check #13 (4396b4f..HEAD — PRs #215-#219) (#222)

$ git log --oneline 8c5455b..HEAD
e0c43c8 6.21: flow review-start -> review-record coherence + hardening (#226)
3540176 Design note: maps flow handoff (6.21, design only) (#227)
ab9fe74 SEC4/6.10: capability-manifest slice 2 — runtime capability intersection (#225)
f6f7096 Design note: 6.21 next increment after slice 1 (scoping) (#224)
e8fd97c Design note: SEC4 capability-manifest slice 2 — runtime capability intersection (#223)
88c112e 6.9/S6 slice 1: progressive Skill-body loading (#221)
```

Arc = **6 PRs: #221, #223, #224, #225, #227, #226**. 3 impl (#221 6.9/S6 body
loading, #225 SEC4 manifest slice 2, #226 6.21 increment-a), 3 design notes
(#223 SEC4 slice-2 design, #224 6.21 next-increment scoping, #227 flow-handoff
design). HEAD `e0c43c8`.

Method (rule 14): no claim taken from a PR title/body/review summary; every
consequential claim re-checked against `git show`, `/usr/bin/grep` over
`runtime/` excluding `tests/`, and a targeted test run.

## 0. Situational awareness

- `python3 -m runtime.smoke` → **exit 0 at `e0c43c8`** (`sqlite_task_lifecycle`
  ok, WAL / foreign_keys=1 / busy_timeout=5000).
- Targeted run at `e0c43c8`: `tests.test_context_builder`
  (arc-touched by #221 + #225), `tests.test_skill_capability_manifest`,
  `tests.test_skills_format`, `tests.test_flow_review` → **OK** (see §1).
- **Scoreboard recounted from the master-inventory §7 table**
  (`work/roadmaps/CAPABILITY_CHECKLIST.md`, 6.1–6.35 = 35 rows, Status column):
  - **DONE 16** — 6.1, 6.2, 6.3, 6.6, 6.7, 6.8, 6.13, 6.14, 6.15, 6.18, 6.23,
    6.26, 6.27, 6.28, 6.29, 6.30.
  - **IN PROGRESS 13** — 6.4, 6.5, 6.9, 6.10, 6.11, 6.16, 6.19, 6.20, 6.21,
    6.22, 6.24, 6.33, 6.35.
  - **NOT STARTED 6** — 6.12, 6.17, 6.25, 6.31, 6.32, 6.34.
  - **Identical to passes #8–#13. Seventh consecutive pass at 16/13/6.**
- `work/roadmaps/00-MASTER-MAPS-CAPABILITY-ROADMAP.md` header still
  `PLANNING MASTER — NOT ACTIVE AUTHORITY`; CAPABILITY_CHECKLIST.md is canonical.
  No second tracker introduced this arc.

## 1. Re-verification of arc claims against merged code

### 1a. #221 — 6.9/S6 slice 1, progressive Skill-body loading. Confirmed.

`git show 88c112e --stat` (`runtime/context_builder.py +54`,
`runtime/flow_start.py +5`, 3 test files, `CAPABILITY_CHECKLIST.md +8/-8`). grep:

- `runtime/context_builder.py:445` — inside `_select_skills`, `document =
  load_catalog_skill(entry, store)` runs **only** under
  `if decision.admission is MemoryAdmission.LOAD and store is not None:`
  (line 443); `item["body"]` / `item["body_sha256"]` attached (`:449-450`);
  `except (SkillCatalogError, SkillParseError)` → `item["body_withheld_reason"]`
  fail-closed (`:447`).
- `_select_skills` signature is now `(skill_catalog, task, store=None)` (`:330`);
  `build_context_plan` threads `store` (`:535`).
- `coverage.skill_bodies_loaded = sum(1 for item in skills if "body" in item)`
  (`:612`).
- **No** change to `load_catalog_skill` / `load_skill` / `admit_memory_evidence`
  (grep: those files not in `88c112e --stat`). `maps context` passes no catalog
  → `_select_skills` returns early → body-free.
- CI-caught follow-up commit: `tests/test_memory_trust_gate.py::test_context_builder_never_loads_skill_bodies`
  (a **non-goal test** asserting `'load_catalog_skill(' not in context_builder.py`)
  was renamed + rewritten — a legitimate obsolescence, same class as memory
  `feedback_review_test_set_too_narrow` (the tests/ grep sweep for now-false
  assertions was incomplete; CI caught it).

6.9 / S6 correctly **NOT flipped**: "execution" level (scripts/references/
examples) unloaded; progressive-disclosure value not yet shown in a frozen eval.
The S6 row carries the slice-1 clause accurately.

### 1b. #225 — SEC4 manifest slice 2, runtime capability intersection. Confirmed, ONE inaccuracy found (§2).

`git show ab9fe74 --stat` (`runtime/context_builder.py +16`,
`runtime/skills/capability_policy.py +80` NEW, `runtime/skills/format.py +85`,
`runtime/skills/gate.py +10/-56`, 2 test files, `CAPABILITY_CHECKLIST.md +6/-...`).
grep + read:

- `runtime/skills/format.py:72` `_declared_capabilities_tuple`, `:112-149` the
  §5.1 vocabulary + `_parse_capability_manifest` **moved here from gate.py**;
  `runtime/skills/gate.py:13-16` now `from .format import (…
  _parse_capability_manifest …)` — the import cycle is avoided (verified
  `format.py` has no `import … gate`).
- `runtime/skills/format.py:119` `SkillDescriptor.declared_capabilities:
  tuple[str, ...] = ()`; populated in `_descriptor_for_root` (`:359`) and
  `load_skill`'s identity rebuild (`:423`); added to the `SkillChangedError`
  identity checks in `load_skill` (`:433`) and `assess_skill`
  (`gate.py` identity block).
- `runtime/skills/capability_policy.py::capabilities_within_envelope` — pure,
  `_BASELINE` (read/`shell`/`filesystem-write`), `_REQUIRES` (network-general/
  github-write/database-write → `external_side_effect`; process-stop →
  `destructive_action`; external-deploy → both), `secret-use:*` →
  `security_sensitive`; unknown token / missing policy map → fail closed. No
  I/O, no store, no state.
- `runtime/context_builder.py:398-406` — in `_select_skills`, **after signal
  match, before the trust gate**, `within, _ = capabilities_within_envelope(
  descriptor.declared_capabilities, task.get("policy"))`; `if not within:
  tally.record(MemoryAdmission.DENY, "SKILL_CAPABILITY_OUTSIDE_TASK_ENVELOPE");
  continue`. Order verified in merged code: match → capability DENY → trust
  gate → body load. An out-of-envelope Skill is never trust-gated or
  body-loaded.
- `task["policy"]` is read (`store.get_task` attaches all 6 booleans), never
  written. No `schema.sql` change, no `task_policy`/`skill_lifecycle_*` change,
  no `HookRegistry` guard, `DestructiveExternalActionGuard` untouched.
  `BUNDLED`-only. §7 third-party trust root not re-touched.
- Checklist SEC4 / 6.10 / 6.24 rows carry accurate slice-2 clauses; **no status
  flip** (verified: all three still `IN PROGRESS`).

**Inaccuracy — see §2.** The DENY at `:404` records into the **same**
`memory_trust_gate` tally, so `coverage["memory_trust_gate_note"]`'s claim
"every memory-like item passed `admit_memory_evidence()` … MemoryTrustClass
alone decides … Denied items are dropped … and counted here" is now
contradicted by this code path.

### 1c. #226 — 6.21 `flow_review_record` coherence + hardening. Confirmed.

`git show e0c43c8 --stat` (`runtime/flow_review.py +33/-8`,
`tests/test_flow_review.py +133`, `CAPABILITY_CHECKLIST.md +2/-2`). grep:

- `flow_review_record` success return now carries `next_step: {"state":
  "REVIEW_RECORDED", "reason": …}` (matches the `{state, reason}` shape
  `flow_start` / `flow_review_start` use).
- `_review_by_id` removed; `_latest_completed_review_for(reviews, reviewer_id)`
  replaces the pre-call open-review handle lookup (which is `None` on the #220
  non-owner path). `/usr/bin/grep -n "_review_by_id" runtime/` → gone.
- **No** change to the verdict path, the rederivation preflight, or any
  `record_review` / `_validate_review_approval_conn` / review-binding call
  (`runtime/state/review*.py` not in `--stat`). Verdict→status unchanged.
- 6.21 row: one clause appended, still `IN PROGRESS`. Accurate.
- PR body's own mutation note is honest: "7 mutations, 6 killed; 1 survivor
  (M2 … a true equivalent mutant)". luve APPROVE.

### 1d. #223 / #224 / #227 — design notes. Confirmed design-only, no status flip.

- **#223** (`e8fd97c`): `work/notes/2026-09-01-sec4-capability-manifest-slice2-design.md`
  only. Its central re-verification (the activation seam `load_catalog_skill`
  has no task context; the reachable seam is `_select_skills`) is what #225
  implemented — self-consistent.
- **#224** (`f6f7096`): `work/notes/2026-09-01-6.21-next-increment-scoping.md`
  only. §1a `recover` PARKED (operator + schema); §1b `release` PARKED (own
  design note); §1c `handoff` → design decision only. #226 implemented its §2/§3
  increment (a).
- **#227** (`3540176`): `work/notes/2026-09-01-6.21-flow-handoff-design.md`
  only. Verdict DISPATCHABLE; corrects #224 §1c (review-independence is
  `continuity_links` identity→identity, verified against
  `test_sec_adv_006`; `record_run_recovery_link` is run→run same-task, cannot
  link a fresh task). `recover`/`release` stay PARKED.

## 2. Substantive finding — `memory_trust_gate_note` is now inaccurate (introduced by #225)

`runtime/context_builder.py:633-641`, `coverage["memory_trust_gate_note"]`:

> "every memory-like item passed `admit_memory_evidence()`; its **MemoryTrustClass
> alone** decides bucket membership and budget_class (LOAD/WITHHOLD/DENY) …
> Denied items are dropped from the plan and counted here"

After #225 this is **false for the Skill bucket**: a matched Skill DENY'd by
`capabilities_within_envelope` (`:398-406`) hits `continue` **before**
`admit_memory_evidence()` is ever called, and its DENY is recorded into the
*same* tally (`memory_trust_gate_denied` +1, `memory_trust_gate_reasons`
gains `SKILL_CAPABILITY_OUTSIDE_TASK_ENVELOPE`). A consumer reading
`{memory_trust_gate_denied: 1, memory_trust_gate_reasons:
{SKILL_CAPABILITY_OUTSIDE_TASK_ENVELOPE: 1}}` next to that note gets a direct
contradiction: not every counted item passed `admit_memory_evidence()`, and
`MemoryTrustClass` did not decide that DENY.

- **Severity: LOW.** It is a coverage-note *string*; no behavior is wrong, the
  DENY itself is correct and intended.
- **Not caught by review.** nava's #225 review ran 8/8 mutations on the logic;
  this is prose drift in an *adjacent* function, the same failure shape as
  #221's obsoleted non-goal test (memory `feedback_review_test_set_too_narrow`)
  — except CI caught #221's and nothing caught this.
- **This is why Tenth-Seat Trigger 2 does NOT fire this pass** (§4).

**Recommended fix (next-3 #1, a small PR — NOT this trajectory PR, whose
MAY-TOUCH does not include `runtime/`):** either (a) reword the note to
"every memory-like item that reaches the trust gate passed `admit_memory_evidence()`;
Skills may first be DENY'd by the SEC4 capability intersection
(`SKILL_CAPABILITY_OUTSIDE_TASK_ENVELOPE`), also counted here", or (b) give the
capability DENY its own `coverage` counter
(`skill_capability_gate_denied` / `_reasons`) separate from `memory_trust_gate_*`
— (b) is cleaner (the two gates are genuinely different) but a slightly larger
change. Recommend (b).

## 3. Minor observation — 6.24 row framing (no action)

The 6.24 row's "Still missing before a status flip" clause is written entirely
around the **environment-report** end-to-end exposure (a `maps flow start` →
`maps route --environment-reports-from-recorded`). #225 added a least-privilege
capability intersection (`_select_skills` capability ∩ `task_policy`) that is
**enforced by default** in a real `maps flow start` — the first least-privilege
intersection with no opt-in (the CanonicalRunGuard and env-report ones are both
default-off). The row's slice-2 clause records this accurately, but the "before
a status flip" framing still reads as if the env-report path is the only gate.
**Not a flip** (6.24 legitimately spans all the intersection surfaces, and two
of three are still default-off), and not a prose error — just noting the row's
DONE-gate description trails its own evidence text. No edit.

## 4. Tenth-Seat / §7 duty (`TENTH_SEAT_REVIEW.md` §2 Trigger 2, §7)

Trigger 2 arms when a pass "reports **no substantive finding** — no stale row,
no mislabeled status, **no changed picture**" and the two preceding passes each
found a real issue. #12 was a REPRIORITIZE with concrete next-3; #13 found a
stale 6.10 clause + an L6 mis-categorisation + an untracked operator-ask doc.
So the tripwire **is armed** for #14.

**It does not fire.** This pass found §2 — a provably-wrong claim in merged
`runtime/` code that #225 introduced and no review caught. That is a "changed
picture" in the precise §7 sense (a foundational-adjacent claim about how the
Skill admission path works is now wrong), not "challenging detail". Plus §3
(6.24 framing observation) and the friction-entry-3 graduation (§6). This is not
a clean pass.

§7 "signs this has gone wrong" checked against the accumulated minority reports
(there are **none** — Trigger 2 has never fired, so `work/reviews/trajectory-*-minority-report.md`
does not exist):

- *"the same conclusion every pass regardless of evidence"* — the scoreboard
  number is identical for a 7th pass, but the **content** differs materially:
  #12 REPRIORITIZE, #13 three fixes, #14 a code-prose defect. And the action has
  moved (#12 REPRIORITIZE → #13 CONTINUE → #14 CONTINUE-with-a-named-defect).
- *"verdict drifting toward reassurance"* — this pass is *less* reassuring than
  #13: it names a defect the review pipeline missed and flags a second
  documentation-drift incident in two arcs (pattern, §2).
- *"no one has run the full check"* — arc range-derived; all 6 PRs checked; the
  §2 finding required reading `_select_skills` end-to-end **and** the coverage
  assembly 200 lines away, which a shallow pass skips.

No Tenth-Seat sub-agent dispatched (flagged to @rozo; Trigger 2 negative).

## 5. Friction-log consumption (standing duty)

Log skimmed in full (5 entries; **no new entries** since #13).

| # | Entry | `verified:` | Disposition this pass |
|---|-------|-------------|-----------------------|
| 1 | self-clear resume prompt dropped | END-TO-END | **Closed.** This session (`gela`, session 16) received `MAPS_Lean_Handoff_2026-09-01-session14.md` as SessionStart `additionalContext`, no operator nudge. 5th confirmation. |
| 2 | coordinate-via-helper-lanes preference | verified | **Closed.** In active use — `rozo` ran 3+ implementer lanes (this one included) across the arc. |
| 3 | context-rotation checkpoint too small | **PARTIAL → VERIFIED (this pass)** | **Consumed — upgraded.** #13 recommended the upgrade after session 16's first full arc ran without a disruptive rotation; session 16 has since run an even longer arc (#221→#227 + checks #13, #14) with no disruptive mid-arc rotation. Both #13 follow-up bullets are discharged. Applying `verified: PARTIAL` → `verified: VERIFIED` (follow-up line appended). |
| 4 | triage loop procedure-only | VERIFIED | **Closed.** This section is the consumption duty discharged for a 5th consecutive pass (#10–#14). |
| 5 | orchestrator tool-use burned ~30–40k context | n/a (behavioral), `countermeasure: none yet` | **Consumed — no recurrence; stays open.** The #221–#227 implementer lanes (this lane included) used targeted `/usr/bin/grep`, `git show --stat` / path-scoped `git show`, `sed -n` ranges, `Read` offset/limit. No large dumps or whole-doc re-reads. Follow-up line appended noting the 3rd consecutive no-recurrence arc. |

Nothing in the log needs escalation to trajectory work or an operator decision.

## 6. Trajectory action: **CONTINUE**

Reasoning:

- All 6 arc PRs verify against merged code; the one defect found (§2) is LOW
  severity (coverage-note prose) with a clean follow-up.
- Check #12's REPRIORITIZE continues to bear fruit: the three impl slices this
  arc (6.9/S6, SEC4 slice 2, 6.21 increment-a) are exactly the independent,
  ask-#1-free work #12 redirected toward. The scoreboard not moving is the
  designed shape (each row's DONE gate is "full capability + first production
  exposure + all sub-slices"), not a stall — #12's own stall tripwire ("next-3
  untouched AND ask #1 unanswered") does not fire.
- No status flip is warranted or missed (§1, §3).
- Operator ask #1 is unchanged — 4th+ consecutive pass, cluster now **7 rows**
  (6.4 / 6.5 / 6.16 / 6.22 / H5 / E4 + L6). Its re-surface framing (check #13 §5
  / the operator-ask doc) is adequate; @rozo to carry it to the operator.

**No REPRIORITIZE** (independent work is flowing), **no RESEARCH / CUT SCOPE /
STOP / ADD IN-SCOPE WORK**.

### Proposed next-3 for check #15

1. **Fix the `memory_trust_gate_note` inaccuracy (§2)** — small PR to
   `runtime/context_builder.py`: give the SEC4 capability DENY its own
   `coverage` counter (`skill_capability_gate_*`) distinct from
   `memory_trust_gate_*`, and correct the note. Also: a rule-20-style CI
   safeguard for checklist/coverage-note drift when a PR touches
   `_select_skills` is worth scoping (this is the 2nd doc-drift-from-`_select_skills`
   incident in two arcs — memory `feedback_review_test_set_too_narrow`).
2. **`maps flow handoff` impl** — #227 design merged, verdict DISPATCHABLE, its
   Resume prompt is paste-ready. Same-task, `record_continuity_link` behind a
   claimant guard, stops before the incoming claim.
3. **6.9/S6 slice 2 OR the SEC4 activation-time intersection.** #221 gave
   `load_catalog_skill` a caller (`_select_skills`) but **not** a `task_policy`-aware
   one, so the SEC4 slice-2 design's "composes for free once 6.9/S6 lands a
   task-aware caller" is not yet true — a small follow-up could pass the
   declared-cap check through to `load_catalog_skill` for activation-time
   defense in depth. Alternatively 6.9/S6 slice 2 (execution-level resources, or
   the progressive-disclosure frozen eval that S6's exit gate needs).

## 7. Recorded for the next pass (check #15)

- **Arc anchor for check #15:** the squash commit of *this* PR. `git log
  --oneline --grep='Roadmap trajectory check' main | head -1` then `<that>..HEAD`.
- `python3 -m runtime.smoke` exit 0 at `e0c43c8`.
- Scoreboard: 16 DONE / 13 IN PROGRESS / 6 NOT STARTED — **seventh** consecutive
  pass. Tenth-Seat Trigger 2 armed and **did not fire** this pass (§2 defect
  found); it re-arms for #15 (passes #13, #14 both found something).
- **§2 defect** (`memory_trust_gate_note` false since #225): if next-3 #1 does
  not land before #15, re-flag it — a wrong claim in production code should not
  sit two passes.
- Cluster blocked on operator ask #1: **7 rows** (6.4 / 6.5 / 6.16 / 6.22 / H5 /
  E4 + L6). Verify all 7 hard before any flip if the ask lands.
- Check #12 REPRIORITIZE next-3: 6.9/S6 ✅ (#221), SEC4 manifest slice 2 ✅
  (#225), 6.21 next verb ✅ (#226 increment-a + #227 handoff design). All landed.
- SEC4 B1 `authorized_operators`: `/usr/bin/grep -rn "authorized_operators"
  runtime/` → **still absent**. Design-pending on the operator trust-root
  decision.
- Zombie pid 3874 (session-8 orphan): **still alive** at check-14 time —
  `ps -p 3874` → `ELAPSED 1-09:08:00`, an `--permission-mode auto` orchestrator
  running the session-8 prompt, idle. Surfaced as an infra ask in the
  operator-ask doc since #13; operator decision to kill, not a trajectory action.
- Friction: entry 3 now `VERIFIED`; entry 5 open (3rd no-recurrence arc).

## Resume prompt

You are running roadmap trajectory check #15 for MAPS_Lean. Follow
`playbook/ROADMAP_TRAJECTORY_CHECK.md` (5-step + friction-log consumption) and
`playbook/TENTH_SEAT_REVIEW.md` §7 (read it before recording any clean result).
Worktree off `origin/main`; `git fetch origin main` first.

Arc: anchor = `git log --oneline --grep='Roadmap trajectory check' main | head -1`
(the check-#14 squash commit), then `git log --oneline <anchor>..HEAD`. Do NOT
hand-list (standing rule, PR #212).

Method (rule 14): no claim from a PR title/body/review summary; re-verify against
`git show`, `/usr/bin/grep` over `runtime/` excluding `tests/`, and a targeted
test run. `python3 -m runtime.smoke` must exit 0 — record the sha.

Specifically check: (a) **§2 defect landed?** — `coverage["memory_trust_gate_note"]`
in `runtime/context_builder.py` should no longer claim "every memory-like item
passed `admit_memory_evidence()`" while the SEC4 capability DENY
(`SKILL_CAPABILITY_OUTSIDE_TASK_ENVELOPE`) bypasses it. If unlanded after two
passes, escalate. (b) **operator ask #1** — answered? 7-row cluster
(6.4/6.5/6.16/6.22/H5/E4/L6) — verify all 7 hard before any flip. Confirm
`work/notes/OPERATOR_ASK_2026-08-31-session13.md` stayed tracked and current.
(c) Did check-#14 next-3 land: the §2 fix, `maps flow handoff` impl, 6.9/S6
slice 2 or the SEC4 activation-time intersection? (d) Re-derive 16/13/6 from
the §7 table — **Trigger 2 re-armed** (passes #13, #14 both found something);
a genuinely clean #15 fires it — dispatch a fresh Tenth-Seat agent per §3,
write `work/reviews/trajectory-15-minority-report.md`, flag the coordinator
first. (e) Friction entry 5 (recurrence). (f) SEC4 B1 `authorized_operators`.
(g) Zombie pid 3874.

Deliverable: `work/notes/2026-XX-XX-roadmap-trajectory-check-15.md` (+
friction-log follow-up lines, + minority report iff Trigger 2). Update
`work/roadmaps/CAPABILITY_CHECKLIST.md` ONLY if a status genuinely moved (hard
evidence) or a clause is provably wrong (prose fix — flag the coordinator
before any status flip).

Workflow: own worktree; PR into `main` (never push); verification-only review;
do NOT spawn your own reviewer — ping the coordinator; no self-merge; report the
PR number to the coordinator.

STOP + flag the coordinator if: a status claim is wrong in a way that changes
the route to DONE and needs a flip you are not certain of; the trajectory action
would be STOP or an envelope-leaving REPRIORITIZE; `TENTH_SEAT_REVIEW.md` §7
signals the check itself has gone shallow; or before dispatching the Tenth-Seat
sub-agent.
