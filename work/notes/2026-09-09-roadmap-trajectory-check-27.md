# Roadmap trajectory check #27 — 2026-09-09

Twenty-seventh pass. Independent analysis lane (`nena`, dispatched by coordinator
`liro`, session 40). Method per `playbook/ROADMAP_TRAJECTORY_CHECK.md` (5-step +
friction-log consumption + Emergence pass) and `playbook/TENTH_SEAT_REVIEW.md` §7.

**Trajectory action: `CONTINUE`.** No roadmap/status claim is wrong in a way that
changes the route to DONE. Scoreboard **unchanged: 19 / 10 / 6** — re-derived by
direct count of the §7 6.x table (35 rows), not copied. No row flipped this arc.
The arc touched **zero `runtime/` and zero `tests/`** — it is entirely
notes / roadmap-prose / playbook / wiki. Three "first production exposure"
exercise PRs landed (6.4 → #320, H4 → #324, plus E5 Stage-0 design → #325) and
each correctly left its row `IN PROGRESS`.

**Trigger 2 (TENTH_SEAT_REVIEW §7): FIRED.** Checks #24, #25, #26 each found a
substantive thing (scoreboard flips / real blockers). #27 finds none — no flip,
no status-truth emergency, only housekeeping-grade items. Per check #26 §8 and
this pass's dispatch, `liro` was flagged **before** this result was recorded
(hcom request #95228 → reply #95231: "no objection — proceed … this is a genuine
clean pass"). Minority report written at
`work/reviews/trajectory-27-minority-report.md` (this pass, not a dispatched
sub-agent — dispatch allowed either). §7 warning-list read against accumulated
minority reports below (§7 of this note).

## Setup / base verification

- Fresh clone `/tmp/tc27` (distinct from the coordinator checkout at
  `~/Projects/MAPS_Lean`, never touched for writes). `git rev-parse origin/main`
  == `HEAD` == **`e7ec610`** at clone; `git status --porcelain` empty.
- Anchor: `git log --oneline --grep='Roadmap trajectory check' main | head -1`
  → `25c7729` ("Roadmap trajectory check #26 … (#318)").
- Arc `git log --oneline 25c7729..origin/main`:
  - **7 non-wiki PRs** — merge order **#320** (`e133a16`), **#319** (`69d6497`),
    **#324** (`b521536`), **#325** (`378468c`), **#321** (`5685fd5`),
    **#322** (`c7bf0c3`), **#323** (`e7ec610`).
  - **5 wiki commits** — `d042ab2`, `18b064c`, `60c0dbf`, `2377bf8`, `54869f5`
    (add a live Development status wiki page + nav + 3 same-day refreshes;
    `git show --stat` each → `docs/wiki/**` only).
  - `git log --oneline 25c7729..origin/main | grep -cE '\(#[0-9]+\)$'` → **7**
    (exactly the 7 arc PRs; **none of the 5 wiki commits carries a `(#N)`
    suffix**, so none matches). **No PR was dropped** — the count equals the
    enumerated arc-PR list above one-for-one; the check-#11 "a PR silently
    vanished from the arc" failure mode did not occur. Coverage below is all 7
    PRs, checked
    individually against `git show` / merged code / `/usr/bin/grep` / targeted
    foreground `unittest` — never a PR title/body/review summary alone (rule 14).
- `git diff --stat 25c7729..origin/main` (non-doc filter): **nothing** outside
  `work/`, `playbook/`, `docs/wiki/`. `playbook/EMERGENCE.md` (+40/-6),
  `playbook/PROGRAM_STEERING.md` (+37), `playbook/INDEX.md` (+2/-2) are the only
  playbook changes (#319 / #322). `work/roadmaps/CAPABILITY_CHECKLIST.md` diff =
  **exactly 2 lines** (H4 row + 6.4 row), both status cells unchanged
  (`IN PROGRESS`).

## 0. Situational awareness (must-check 1)

- `python3 -m runtime.smoke` → **exit 0** (`{"ok": true}`,
  `sqlite_task_lifecycle` DONE).
- `python3 -m unittest tests.test_exp_b_skill_routing` → **3 OK** (0.009 s).
  Report: `selection_f1` **0.8666666666666666**, `false_activation_cases` **0**,
  `selection_precision` **1.0**, `selection_recall` 0.7647, `exact_cases` 19/25,
  `corpus_sha256` **`2cff0e405c2f0201759ad8d23ed84fbb60bc1ec7d5513be2ad9b4c54fe5f4565`**
  (frozen, unchanged from #26). 6.9 / S6 DONE not regressed — **no status-truth
  emergency**.

## 1. Per-PR reality check (arc = #319–#325)

### #320 — 6.4 destructive-action first-exposure exercise (must-check 3)

- `git show e133a16`: **no `runtime/` or `tests/` change** — adds
  `work/notes/2026-09-09-6.4-destructive-action-first-exposure.md` (379 L),
  frozen case JSON
  `CASE-3da6464c1565c1b56915c181301cf57ec24c40253e6a2fe426843ee0276ad924.json`
  (340 L), `work/reviews/pr-320-review-evidence.md` (`bozo` APPROVE, 7 checks),
  and the 6.4 checklist-row annotation.
- The `.stop()` call site + `--terminate-denied-sessions` opt-in landed
  **earlier** in #306 (`0996f70`, arc #26). #320 is the *exercise*: three real
  untagged hcom sessions bound via `maps run bind-session`, killed, left past
  lease + `resume_after`; the third consecutive `CanonicalRunGuard` denial
  promoted each incident to `failed`/`canonical_denial_persistent`, and with
  `--terminate-denied-sessions` armed that promotion routed
  `HarnessService.stop()` → `HookEvent.BEFORE_DESTRUCTIVE_ACTION` →
  `DestructiveExternalActionGuard` **for the first time in a real pass**.
- Both guard branches captured: ordinary-task lane → `DENY`
  (`ACTION_OUTSIDE_TASK_ENVELOPE`) → `HOOK_DENIED`, fail-closed, session
  untouched; destructive-envelope + operator-approved lane → `ALLOW`
  (`ACTION_WITHIN_TASK_ENVELOPE`) → `SESSION_STOPPING` →
  `HcomHarnessAdapter.stop()`. Flag-omitted control → byte-identical `fail`
  action dict minus `harness_stop`.
- **§4c caveat verified present** in the 6.4 row: *"for an ordinary stalled task
  the recovery `.stop()` is always guard-`DENY`'d on the task envelope; it only
  terminates when the stalled task's own policy was authorized for destructive
  action."* — carried verbatim into the row's parenthetical for the next 6.4
  check.
- **Row correctly stays `IN PROGRESS`**: write/credential/scope guards + the
  capability-declaration manifest are still unbuilt. Correct — this closes only
  the "destructive-action guard callback has never executed" gap, not the row.

### #324 — H4 enforced-validation-gate first-exposure exercise (must-check 4)

- `git show b521536`: **no `runtime/` or `tests/` change** — adds
  `work/notes/2026-09-09-h4-validation-gate-first-exposure.md` (368 L), frozen
  case
  `CASE-559ff1df61eb6c829b55c641b3ae0a4450f8dca9bfcc218e76df84fd53332a22.json`
  (442 L), `work/reviews/pr-324-review-evidence.md` (`zuna` APPROVE), and the
  H4 row annotation.
- `maps recovery-tick --enforce-validation` run against a real stalled
  silent-stop incident whose bound `run_environment_evidence` spec made the
  `quick` tier concretely fail (`sh -c '… exit 1'`, `returncode: 1`). Gate
  parked the incident in `state: "blocked_validation"` /
  `action: "resume_blocked_validation"` on a genuine
  `resume_validation: {attempted: true, passed: false}` — `harness_resume: null`,
  `attempt` unchanged at 0; three consecutive blocks → `fail` /
  `validation_block_persistent`. `--enforce-validation`-omitted control on a
  byte-identical incident proceeded to `resume_failed` (`attempt` → 1). An
  `attempted:false` lane (`no_spec_bound`) was **not** blocked (design Q6).
- **Row correctly stays `IN PROGRESS`**: the H4 row text says so explicitly
  ("Status NOT changed") — `normal`/`full` tiers + the per-spec
  `EnvironmentSpec.validation.enforcement` field remain deferred.
- **Reconciliation handoff (executed this pass).** The H4 note (§ lines 332,
  363–364) explicitly asks a trajectory check to reconcile the **E4** and
  **6.5** rows, which share the "no first production exposure of an enforced
  pass" clause and were left unedited by #324's output boundary. Both E4 and 6.5
  are **already `DONE`** (flipped 2026-09-05 on the DEC-003 option-B
  canonical-run `resume_denied` evidence, `CASE-378fb326…`). #324 now *also*
  satisfies the narrower `--enforce-validation` outcome-gate clause their prose
  repeatedly named. **Action taken:** a one-line
  `**Updated 2026-09-09 (trajectory check #27 reconciliation)**` annotation
  appended to each of the E4 and 6.5 row cells pointing at #324 — **status cells
  untouched, NO flip** (verified: scoreboard still 19/10/6 by direct recount
  after the edit). Recorded so a future pass does not re-litigate the
  advisory-only wording still interleaved in those rows' history.

### #325 — E5 recovery-compat enforcement seam, Stage 0 (must-check 5)

- `git show 378468c`: adds
  `work/notes/2026-09-09-e5-recovery-compat-enforcement-seam-design.md` (188 L)
  + `work/reviews/pr-325-review-evidence.md` (9 L). **No code, no checklist
  change** — commit message: *"Stage 0 only — no code."*
- Note documents where a Stage-3 compat gate would sit in
  `RecoverySupervisor.tick()` (position 7.5, after the resume-validation gate)
  and **reaffirms** the work stays `BLOCKED_ON_OPERATOR_DECISION #1` (Option B
  not approved, 2026-08-17). It recommends an *advisory exercise*, not a Stage-3
  implementation task, and states the decision's precondition ("accumulate real
  operational experience with advisory environment evidence") is unmet — no
  production recovery tick has surfaced non-null `environment_evidence` yet.
- **E5 row (checklist L49) still `IN PROGRESS`**, unchanged by the arc. Its exit
  gate ("incompatible replacement cannot silently resume") remains unmet:
  evidence surfaced, not enforced. The note does **not** authorize Stage 3.
  Confirmed.

### #319 — Emergence may target established mechanisms for redesign/supersession

- `git show 69d6497`: `playbook/EMERGENCE.md` (+40/-6), `playbook/INDEX.md`
  (+2/-2), design note
  `work/notes/2026-09-07-emergence-supersession-authority.md` (108 L),
  `work/reviews/pr-319-review-evidence.md` (114 L) + **its own minority report**
  `work/reviews/pr-319-minority-report.md` (246 L). **No `runtime/` / `tests/`
  / `work/roadmaps/` change.**
- This is an authority-*surface* change to the Emergence playbook: it grants the
  Emergence pass explicit authority to *propose* challenge / redesign /
  replacement of any established mechanism (EMERGENCE.md line ~12 / ~124), while
  keeping "proposal authority distinct from execution/merge authority". Landed
  with `mosa` APPROVE + `dula` Tenth-Man **YELLOW** (= merges) per the
  session-39 handoff. Not a capability-status change. Recorded as an arc fact,
  not a finding.

### #321 / #322 / #323 — Wiki / Pilot-evidence / competitor-evidence reconciliation (must-check 12)

- All three are **docs/planning only**, independently reviewed (`zaru` on #321
  round 3; `moto` on #322 and #323), and spot-verified here:
  - **#321** (`5685fd5`): `git diff --name-only 25c7729..5685fd5` limited to
    `docs/wiki/*.md` (12 files) + `work/reviews/pr-321-review-evidence.md`.
    `zaru`'s evidence independently recounts the wiki "Canonical capability
    scoreboard" against `CAPABILITY_CHECKLIST.md` → **19 / 10 / 6**, all 35
    rows, 6.4 = IN PROGRESS, H4 = IN PROGRESS. No wiki claim exceeds its row.
    No new authority (corrected #319 text matches `playbook/EMERGENCE.md`).
  - **#322** (`c7bf0c3`): `playbook/PROGRAM_STEERING.md` +
    `work/notes/2026-09-09-pilot-evidence-roadmap-reconciliation.md` +
    `work/tasks/roadmap-reconciliation-27-pilot-evidence-bootstrap.md`. The
    PROGRAM_STEERING addition ("Borrow before build for reusable mechanisms")
    is a **conditional, explicitly-skippable evidence-quality check**, not a new
    approval gate — "then shape the task normally under AGI/task authority".
    Note states "No capability status changes are proposed" and "does not become
    the canonical capability status overlay". `moto` re-derived the 16
    unfinished 6.x capabilities and confirmed the note's KEEP/STRENGTHEN/DEFER/
    CHALLENGE table is internally consistent; 6.35 CHALLENGE bounded
    ("not supersession authority").
  - **#323** (`e7ec610`): 4 `work/research/**` topic notes + README + task +
    evidence. Every note header "RESEARCH — NOT ACTIVE AUTHORITY"; each ends
    "No new authority follows". `moto` confirms zero runtime/tests/wiki/
    checklist change; the one candidate incident-class
    ("CONFIG_RUNTIME_DIVERGENCE") is explicitly neutralised ("No new enum is
    proposed").
- **Conclusion:** none of the three silently changed capability status or
  roadmap authority. The reviews' claims hold up on spot-check. **Clean.**

### #317 — DEC-003 bug 1 (HCOM_DIR vs --hcom-dir precedence, Option C) (must-check 7)

- **Landed pre-arc** (`52794e3`, in `git log` before `25c7729`), confirmed
  present on `origin/main`: `git log --oneline | grep 52794e3` →
  *"DEC-003 bug 1: HCOM_DIR vs --hcom-dir precedence — Option C (#317)"*.
  DEC-003 bug 2 already fixed (`9d73a6d` / #313, also pre-arc). Both DEC-003
  known bugs are now resolved on `main`.

## 2. Scoreboard re-derivation (must-check 2)

Direct count of `work/roadmaps/CAPABILITY_CHECKLIST.md` §7 6.x table
(`^\| *6\.\d+ *\|` rows), Status column:

| Status | Count | Rows |
|---|---|---|
| DONE | **19** | 6.1 6.2 6.3 6.5 6.6 6.7 6.8 6.9 6.13 6.14 6.15 6.16 6.18 6.23 6.26 6.27 6.28 6.29 6.30 |
| IN PROGRESS | **10** | 6.4 6.10 6.11 6.19 6.20 6.21 6.22 6.24 6.35 + 6.33 ("IN PROGRESS (evaluation-only, by design)") |
| NOT STARTED | **6** | 6.12 6.17 6.25 6.31 6.32 6.34 |
| **Total** | **35** | |

**19 / 10 / 6 — unchanged from check #26.** No flip recorded; none warranted
(coordinator confirmed before recording).

## 3. Friction-log consumption (must-check 11)

Walked `work/coordination/FRICTION_LOG.md` in full + ran
`python3 tools/triage_status.py --root .`:

```
# Triage status (advisory - read-only)

FRICTION_LOG: 15 entries - 7 closed, 8 open (0 unresolved).

Nothing open. The triage loop is current.
```

**The 2026-08-18 record no longer appears in this report.** Earlier passes
(#23–#26) saw it flagged under "Drift+ repair records missing a countermeasure
or regression case". Its absence at HEAD is a **false negative, not a genuine
resolution.** `tools/triage_status.py::parse_repair_note` does a naive substring
scan — `has_regression_case = "regression" in text.lower()`. `nena`'s own
2026-09-09 disposition line appended to that record contains the word
"regression" (e.g. "missing a countermeasure or regression case", "add the
`## Regression case` heading"), so the substring check now passes **by
coincidence of the disposition prose**, not because the record's structure
changed. The record **still has no `## Regression case` section and no
machine-readable countermeasure field** — it is not genuinely resolved.

- **0 unresolved, 0 OVERDUE.** The 8 "open" entries are behavioral
  "watch-if-it-recurs" items with a countermeasure named (not `none yet`) and a
  non-`UNVERIFIED` disposition; none needs a disposition this pass. The
  previously-`UNVERIFIED` "coordinator merge marks treated as merge
  authorization (recurrence)" entry **CLOSED at check #25** (live
  gate-refusal-path observation, PR #298 merge-ledger entry); its header
  `verified: UNVERIFIED` line is stale (log is append-only) but the last
  follow-up is `CLOSED`.
- The 2026-09-03 "coordination_housekeeping.py fully non-functional" entry was
  addressed by **PR #283** ("coordination tooling fixes", MERGED pre-arc at
  check #22) — its `countermeasure:` names that branch; not carried as open.
- **`tools/triage_status.py` now reports "Nothing open" for
  `work/notes/2026-08-18-stalled-dispatched-worker-repair.md` — but only by
  keyword coincidence, not because the record was resolved.** Check #26's
  in-prose §1 disposition ("discharged in substance by the session-24/25
  Monitor-stall countermeasure, PR #288 + `scripts/run_tests_sharded.py`")
  remains prose the script cannot parse. What changed at HEAD is that `nena`'s
  own 2026-09-09 disposition text contains the substring "regression", which
  the script's `has_regression_case = "regression" in text.lower()` scan
  accepts. The record still genuinely lacks a `## Regression case` section and a
  machine-readable countermeasure field. So the substring-scan is now satisfied
  by coincidence (**masking risk**), the underlying disposition mechanism is
  still not machine-readable (§4 item 4), and this remains **operator-decision
  item 3** (§6) — this pass does **not** record it as resolved. A
  `2026-09-09 disposition (trajectory check #27, nena)` line was appended to
  that record in this PR confirming no substantive change + naming the false
  negative.
- **This pass's dated review line:** recorded here (§3) + the repair-record
  pointer line appended in the same PR, per check #26 §8's instruction.

## 4. Named findings (all housekeeping-grade — none changes the route to DONE)

1. **E4 / 6.5 reconciliation** — executed this pass (one-line annotation each,
   no flip). Handoff from the #324 H4 note. Both rows already DONE. Done.
2. **6.22 BEFORE_SEND — explicit WATCH.** `maps run send-context
   --deliver-context` production call site landed **#310 (arc #26)**; **1 arc
   has now passed with the call site and no first-exposure exercise.** 6.4
   completed the same pattern this arc (call site #306 arc #26 → exercise #320
   arc #27 = spread across 2 arcs). Per check #26 §8: *"if a 3rd arc passes with
   call sites but no exercise, that is itself a finding."* Not yet a finding —
   **becomes one if trajectory check #28 also passes without the 6.22
   `BEFORE_SEND` exercise** (or an operator ruling on the
   no-organic-`send()`-caller question from #307). Carried to #28's must-check
   list (§8).
3. **IDEA-fe6c0f0f — promoted #26, no follow-up opened.** Check #26 promoted
   (recommended) the diff-equivalence acceptance idea for
   `scripts/check_review_evidence.py`'s revalidation tier. **No task doc or PR
   was opened in arc #27** (`grep` of `work/tasks/` + `git log --all` for
   equivalence/ancestor/revalidation → nothing new; sibling `IDEA-968eb261`
   also still open). Recorded as an **operator / coordinator disposition item**
   — this pass does **not** open the task (dispatch boundary). Not yet an
   escalation (1 arc since promotion).
4. **`triage_status.py` disposition mechanism is not machine-readable — and at
   HEAD is now silently satisfied by coincidence.** `parse_repair_note` decides
   `has_regression_case` by a bare `"regression" in text.lower()` substring
   scan. That check now passes for
   `2026-08-18-stalled-dispatched-worker-repair.md` **only because its own
   2026-09-09 disposition prose uses the word "regression"** — the record still
   has no `## Regression case` section and no machine-readable countermeasure
   field. The script has flipped from over-reporting (5 passes, #23–#27 quoted
   above in earlier drafts) to a **false negative / masking risk** without the
   record's substance changing. Candidate bounded fix (not this pass, and
   outside this PR's boundary): teach `triage_status.py` to recognise a dated
   `disposition (trajectory check #N)` line as an explicit disposition, **or**
   the operator confirms
   `2026-08-18-stalled-dispatched-worker-repair.md` §1 is adequately discharged
   so the record can carry a real `## Regression case` pointer to the #288
   shard-runner tests. Still open — operator-decision item 3 (§6).
5. **INSIGHT-45727354 / INSIGHT-68a53a28 still have no operator disposition**
   (2nd trajectory pass since 2026-09-03 capture; #26 flagged them). Named in
   §6 operator section. Not yet at the N=3 auto-escalation bound.

## 5. Emergence pass (must-check 10)

Phase 1 (Imagine) run against the arc + project; sweep of `work/insights/` +
`work/ideas/` open records.

### Phase 1 — Imagine → Capture

**2 records captured** (`scripts/emergence.py capture`):

- **`IDEA-497fca2f`** — *Track rows awaiting a first-exposure exercise in a
  standing list.* Across #25–#27, rows 6.5 / H5 / E4 / L6 / 6.16 / 6.4 / H4 each
  closed or advanced via a discrete "first real production exposure" exercise
  PR, separate from both the design-note PR and the default-off call-site PR.
  "Which rows are call-site-landed / exercise-pending" lives only in
  trajectory-note prose and is re-derived by hand each pass. Next test: add an
  "Awaiting first-exposure exercise" subsection to §7; measure rediscovery cost
  at #28.
- **`INSIGHT-f095b669`** — *Outward-facing representations have no reconciliation
  cadence like the roadmap has.* Arc #27 contains a 3-PR reconciliation wave
  (#321 Wiki / #322 Pilot evidence / #323 competitor evidence) + 5 wiki-refresh
  commits, all correcting outward artifacts that drifted from actual behavior.
  The internal roadmap has a standing periodic reconciliation mechanism (this
  check); the wiki / Pilot-evidence bundle / research owners have none. Same
  failure mode this check exists to prevent, on the outward surface. Next test:
  add a one-bullet outward-doc spot-check to the #28 trajectory cadence.

Non-trivial imagining occurred → the "nothing worth imagining, arc after arc"
§7 signal does **not** apply.

### Phase 2 — Sweep (`work/insights/` + `work/ideas/`)

| Record | Proposed disposition | Rationale |
|---|---|---|
| `INSIGHT-e0b448a6` (tick has zero prod invocation) | **kill / keep-as-history** | Already STALE-dispositioned 2026-09-03; `run_recovery_tick` calls `tick()` since #165; 6.4 now exercised (#320). Nothing left to act on. |
| `INSIGHT-75785aae` (harness layer has zero prod callers) | **kill / keep-as-history** | Already STALE 2026-09-03; `build_canonical_harness_service` is the prod root; first exercised #277; 6.4/H4 now exercised. Interface-first risk it named did not materialise. |
| `INSIGHT-102296b5` (`--enforce-canonical-run` may be structurally unreachable) | **stale (already disposed)** | #26 disposed: exit criterion was exercisable, not structurally blocked (#298 + #303). |
| `INSIGHT-651d8c62` (7-row cluster one step from DONE for 1 month) | **stale (already disposed)** | #26 disposed: 5/7 DONE; 6.4/6.22 remain, each now with a call site. |
| `INSIGHT-29a10ad4` (`check_review_evidence.py` head_sha walk-back stops silently) | **incubate** | No disposition yet. Related to the revalidation-tier / `IDEA-fe6c0f0f` cluster; ripe to fold into whatever task disposes `IDEA-fe6c0f0f`. Not yet at N=3. |
| `INSIGHT-ab696436` (design notes carry stale forward-refs) | **incubate (pass 2)** | Incubate-pass-1 at #22 ("3rd stale 'blocked on X where X is merged' promotes it"). Arc #27 produced **no** new occurrence (#325 reaffirms a real operator gate, not a merged one). Continues incubating. |
| `INSIGHT-a6406800` (`triage_status.py` earned its keep) | **stale / keep-as-history** | Positive retro note. Live counter-fact this pass: the script over-reports (§4 item 4) — but that is a new, separately-captured concern, not a reason to re-open this. |
| `INSIGHT-45727354` (friction-log behavioral entry path lets repeat failures slip) | **incubate → operator-section** | No operator disposition (2nd pass). §6. |
| `INSIGHT-68a53a28` (trajectory check has become part of the process) | **incubate → operator-section** | No operator disposition (2nd pass). §6. Cross-links `INSIGHT-f095b669` captured this pass. |
| `IDEA-582cc671` / `IDEA-968eb261` (zero-diff / rebase-tolerant re-review) | **stale — implemented; residual = `IDEA-fe6c0f0f`** | #26 disposed both. |
| `IDEA-20615e4d` (standardize per-agent worktrees) | **stale — superseded** by `playbook/WORKTREE_ISOLATION.md` (disposed 2026-09-03). |
| `IDEA-bc6cd243` / `IDEA-a134ad7c` / `IDEA-9e7014fa` (coordination tooling) | **stale — promoted → PR #283 (MERGED)**. |
| `IDEA-fe6c0f0f` (revalidation ancestor check never fires on rebase) | **promote — follow-up still owed** | See §4 item 3. Promoted #26; no task opened arc #27. Operator/coordinator to dispose. |
| `IDEA-497fca2f` / `INSIGHT-f095b669` (captured this pass) | **incubate** | Fresh; next test named in each. |

No record is at the **N=3 incubate-without-movement** auto-escalation bound this
pass.

## 6. Operator-decision items

Nothing here blocks `CONTINUE`; these need a human/authority call and are named
so the pass does not record a clean result without listing them:

1. **`INSIGHT-45727354` + `INSIGHT-68a53a28`** — captured 2026-09-03, flagged by
   check #26, **still no operator disposition** (2nd pass). Auto-escalation bound
   is N=3 (i.e. check #28). Recommend the operator/coordinator dispose (promote /
   stale / kill / incubate-with-reason) before #28.
2. **`IDEA-fe6c0f0f` follow-up** — promoted (recommended) by check #26; **no
   diff-equivalence follow-up task or PR opened in arc #27**. Recommend the
   coordinator either open the bounded task
   (`scripts/check_review_evidence.py` rebase-safe diff-equivalence acceptance,
   folding in `INSIGHT-29a10ad4`) or record why it is deferred.
3. **`2026-08-18-stalled-dispatched-worker-repair.md`** — `triage_status.py`
   flagged it for 4 consecutive passes (#23–#26); at HEAD it **no longer
   appears in the report**, but only because the substring scan
   (`"regression" in text.lower()`) matches the word "regression" in the
   record's own 2026-09-09 disposition prose — a **false negative**, not a
   genuine resolution. The record still has no `## Regression case` section and
   no machine-readable countermeasure field, so the underlying disposition
   mechanism is still not machine-readable and this pass does **not** treat the
   record as resolved. Recommend the operator either (a) make
   `triage_status.py` recognise a dated `disposition (trajectory check #N)`
   line, (b) confirm §1 is adequately discharged so a real `## Regression case`
   pointer to PR #288's `tests/test_run_tests_sharded.py` can be added, or
   (c) add that pointer directly. Until one of those lands this stays open.
4. **PRs #326–#330** (`BigCatMellow` "harden invariants" wave) are **OPEN, not
   merged**, pending an operator ownership call. **Not part of arc #27** and not
   evaluated here — noted only so the next pass knows they predate its anchor.
5. **E5 `BLOCKED_ON_OPERATOR_DECISION #1`** (Option B, recovery/setup
   equivalence authority) — unchanged since 2026-08-17; #325 reaffirms it and
   recommends an advisory exercise first. No new ask, listed for continuity.

## 7. TENTH_SEAT_REVIEW §7 — "signs this has gone wrong"

Read against minority reports accumulated since check #26
(`work/reviews/pr-319-minority-report.md`, and
`work/reviews/trajectory-27-minority-report.md` written this pass):

- *All GREEN, all short, all ten-minute* — **no.** The #319 minority report is
  246 lines and argued a real YELLOW. This pass's minority report (below)
  engages the actual clean-vs-not question at length.
- *Tenth Seat gets less context/evidence* — **no.** Same fresh clone, same
  commands, same access as the analysis lane (they are the same agent here, by
  dispatch design).
- *Challenges detail, never foundation* — the #27 minority report is required by
  its brief to attack the foundational claim ("is CONTINUE complacent / is any
  'minor' item actually a route-to-DONE finding"), not row-wording detail.
- *Same agent keeps drawing the role* — `nena` is new this session; prior passes
  were `sofa` (#26), etc. Not a pattern.
- *Report written after the merge to paper over* — **no.** This note + the
  minority report are in the same unmerged PR, pre-review.
- *Reports accumulate, nothing reopens* — the #319 YELLOW was acted on
  (merged with the caveat recorded); this pass's minority report feeds the
  independent reviewer's brief.

No §7 alarm.

## 8. Recorded for the next pass (check #28)

- **Arc anchor for #28**: the squash commit of *this* PR (#27).
- `python3 -m runtime.smoke` exit 0; `tests.test_exp_b_skill_routing` 3 OK,
  f1 0.8666…, `false_activation_cases` 0, precision 1.0,
  `corpus_sha256` `2cff0e40…4565` — regression here is a status-truth emergency.
- **Scoreboard 19 / 10 / 6** — re-derive from the §7 6.x 35-row table directly;
  flag the coordinator before recording any flip.
- **6.22 `BEFORE_SEND` — 2nd arc of the WATCH.** Call site landed #310 (arc #26);
  arc #27 passed with no first-exposure exercise. **If arc #28 also passes with
  no `send-context --deliver-context` / `BEFORE_SEND` exercise and no operator
  ruling on the no-organic-caller question (#307), that is a finding** — the
  design-note→call-site→deferred-exercise cadence has then stalled a row's
  closure across 3 arcs. (`IDEA-497fca2f` proposes the standing tracking list.)
- **`IDEA-fe6c0f0f`** — check whether the diff-equivalence follow-up task/PR was
  opened (2nd arc since promotion; N=3 escalation bound at #29 if still nothing).
- **`INSIGHT-45727354` / `INSIGHT-68a53a28`** — check `## Promotion` sections for
  an operator disposition. **N=3 auto-escalation bound reached at #28** if still
  none — name in the operator section and do not record clean until listed.
- **`INSIGHT-ab696436`** — incubate pass 2; a 3rd stale "blocked on X where X is
  merged" occurrence promotes it. #325's `BLOCKED_ON_OPERATOR_DECISION #1` is a
  real gate, not an occurrence.
- **`triage_status.py`** no longer lists
  `2026-08-18-stalled-dispatched-worker-repair.md` — but only because its
  substring scan now matches "regression" in that record's own disposition
  prose (**false negative / masking risk**, not a resolution; §4 item 4). The
  record still owes a real `## Regression case` pointer or an explicit operator
  closure. Operator-decision item 3 (§6) is still open — either the bounded
  script fix (recognise a dated `disposition (trajectory check #N)` line) or
  the operator confirmation should land before #28 records this area clean.
- **E4 / 6.5** — reconciliation annotation added this pass; both DONE, no action
  owed. Do not re-litigate the advisory-only wording in their history.
- **PRs #326–#330** — were OPEN at #27; check their disposition.
- **Trigger 2** — **FIRED at #27** (clean pass, coordinator flagged first,
  minority report written). #28: if it fires again (2nd consecutive genuinely-
  clean pass), read TENTH_SEAT_REVIEW §7 hard — two clean passes in a row is
  itself the "narrow or drop the practice" signal, not just a quiet result.

## Resume prompt

You are running roadmap trajectory check #28 for MAPS_Lean. Independent analysis
lane. Follow `playbook/ROADMAP_TRAJECTORY_CHECK.md` (5-step + friction-log
consumption + Emergence pass) and `playbook/TENTH_SEAT_REVIEW.md` §7 (read before
recording any clean result — **Trigger 2 fired at #27**, so a clean #28 is the
2nd consecutive and a strong "narrow/drop the practice" signal). Fresh clone to a
UNIQUE path (`git clone https://github.com/BigCatMellow/MAPS_Lean /tmp/traj28-work`);
verify `git rev-parse origin/main` == `HEAD`, `git status --porcelain` empty.
NEVER touch `~/Projects/MAPS_Lean`, `.claude/worktrees/`, or `.maps/` for writes.
Do NOT run `maps recovery-tick` / any `--enforce-*` pass, and do NOT spawn a real
hcom session, unless explicitly authorized.

Anchor: `git log --oneline --grep='Roadmap trajectory check' main | head -1` →
the check-#27 squash; then `git log --oneline <that>..HEAD`, check every line
(PRs **and** wiki commits — arc #27 had 5 wiki-only commits). Confirm coverage
against `git log --oneline <that>..HEAD | grep -cE '\(#[0-9]+\)$'`.

Method (rule 14): no claim from a PR title/body/review summary alone — re-verify
against `git show`, merged code, `/usr/bin/grep`, targeted foreground `unittest`.
`python3 -m runtime.smoke` must exit 0; `tests.test_exp_b_skill_routing` must
stay 3 OK, f1 0.8666…, `false_activation_cases` 0, precision 1.0,
`corpus_sha256` `2cff0e40…4565`. Full suite is CI's — do NOT background-and-wait,
no Monitor on a test run, no `kill -0 <pid>; sleep` loop.

Context from #27: arc = 7 PRs (#319–#325) + 5 wiki commits, **zero `runtime/`
and zero `tests/` touched**. Scoreboard **unchanged 19/10/6** (no flip since
6.16 at #26). 6.4 (#320) got its `BEFORE_DESTRUCTIVE_ACTION` `.stop()`
first-exposure exercise, H4 (#324) got its `--enforce-validation` gate
first-exposure exercise — **both rows correctly stayed IN PROGRESS**. E5 (#325)
was a Stage-0 design note only, still `IN PROGRESS` + `BLOCKED_ON_OPERATOR_DECISION
#1`. #321/#322/#323 were docs/planning reconciliation, changed no capability
status or authority. E4/6.5 got a no-flip reconciliation annotation. **Trigger 2
FIRED** (clean pass) — coordinator flagged first, `work/reviews/trajectory-27-
minority-report.md` written.

Specifically check at #28: (a) **6.22 `BEFORE_SEND` — 2nd arc of the WATCH.** If
arc #28 passes with no `send-context --deliver-context` exercise and no operator
ruling on #307's no-organic-caller question, **write it up as a finding** (3-arc
cadence stall). (b) `IDEA-fe6c0f0f` diff-equivalence follow-up task/PR — opened
yet? (2nd arc since promotion.) (c) `INSIGHT-45727354` / `INSIGHT-68a53a28` —
operator disposition yet? **N=3 bound is #28** — if still none, name in the
operator section, do not record clean until listed. (d) Re-derive the scoreboard
from the §7 6.x 35-row table by direct count — expect 19/10/6 unless 6.22 moved;
flag the coordinator before any flip. (e) `triage_status.py` still re-flagging
`2026-08-18-stalled-dispatched-worker-repair.md` (6 passes) — bounded fix or
operator confirmation should land. (f) PRs #326–#330 disposition. (g) Trigger 2:
a 2nd consecutive clean pass — flag the coordinator BEFORE recording, write
`work/reviews/trajectory-28-minority-report.md`, and take the §7 "narrow or drop"
question seriously in it.

DELIVERABLE: one PR, branch `roadmap/trajectory-check-28`, adding
`work/notes/2026-09-<DD>-roadmap-trajectory-check-28.md` (+ any `FRICTION_LOG`
follow-up lines appended in that PR + emergence sweep dispositions + minority
report). Update `CAPABILITY_CHECKLIST.md` ONLY if a status genuinely moved (hard
evidence) — flag the coordinator first. Author email
`201203536+BigCatMellow@users.noreply.github.com`. Commit trailer
`Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>`. TWO-PHASE REVIEW: do
NOT push your own review evidence, do NOT spawn your own reviewer; when the PR is
open and CI `test` is green, report the PR number + full head SHA to the
coordinator via hcom (prefix every message with your name), then stand by for
review findings. You do NOT merge it.
