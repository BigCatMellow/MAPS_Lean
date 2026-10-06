# Roadmap trajectory check #28 — 2026-09-12

Twenty-eighth pass. Author lane (`zuma`, dispatched by coordinator `bila`).
Method per `playbook/ROADMAP_TRAJECTORY_CHECK.md` (5-step + friction-log
consumption + Emergence pass) and `playbook/TENTH_SEAT_REVIEW.md` §7.

**Trajectory action: `CONTINUE` with one named finding (6.22).** No
roadmap/status claim is wrong in a way that changes the route to DONE.
Scoreboard **unchanged: 19 / 10 / 6** — re-derived by direct count of the §7
6.x table (35 rows), not copied from #27. No row flipped this arc. The 6.22
BEFORE_SEND WATCH carried from #26/#27 **becomes a finding this pass** (see
§4.1) — this is the "something found" that keeps Trigger 2 from firing a
2nd consecutive time.

## Setup / base verification

- Fresh clone `/tmp/trajcheck28work` (distinct from the coordinator checkout
  at `~/Projects/MAPS_Lean`, never touched for writes). `git rev-parse
  origin/main` == `HEAD` == **`1c35470`** at clone; `git status --porcelain`
  empty.
- Anchor: `git log --oneline --grep='Roadmap trajectory check' main | head -1`
  → `25c7729` is check #26's squash; check #27's own squash (`7ee1e33`,
  PR #332) is the correct anchor for this pass per #27's own §8 "Arc anchor
  for #28: the squash commit of this PR". Used `7ee1e33`.
- Arc `git log --oneline 7ee1e33..origin/main`:
  ```
  1c35470 Track durable handoff acknowledgment and continuation (#340)
  bfae290 Enforce canonical task history retention (#342)
  cabf344 Design canonical task/history retention (#338)
  7110fa9 Audit trusted reviewer execution producer (#337)
  4819c4a Design trusted reviewer execution lineage (#336)
  82f6373 Fail closed on UNKNOWN recovery resume before direct fallback (#335)
  5f07b33 Refresh Development status for 2026-09-11 (docs-refresh, no PR)
  344b4ae Refresh Development status for 2026-09-10 (docs-refresh, no PR)
  7dfcbd0 Close 2026-08-18 stalled-dispatched-worker repair record (#334)
  9ec5d6a Record operator KEEP disposition on INSIGHT-45727354 and -68a53a28 (#333)
  ```
  **6 PRs** (#333, #334, #335, #336, #337, #338/#342 — #342 supersedes #338's
  content per its own body, since #338's base branch was deleted by an
  intervening merge) + 2 docs-refresh commits with no PR number. `grep -cE
  '\(#[0-9]+\)$'` over the arc → 6, matching the enumerated PR count
  one-for-one. No PR silently dropped.
- `git diff --stat 7ee1e33..origin/main` outside `work/`: only
  `runtime/recovery/supervisor.py`, `runtime/state/schema.sql`,
  `tests/test_recovery_external_effect_ambiguity.py`,
  `tests/test_task_history_retention.py`. `work/roadmaps/CAPABILITY_CHECKLIST.md`
  diff = **0 lines** — no capability row touched this arc.

## 0. Situational awareness

- `python3 -m runtime.smoke` → **exit 0** (`{"ok": true}`,
  `sqlite_task_lifecycle` DONE). No status-truth emergency.
- `python3 -m unittest tests.test_exp_b_skill_routing -v` → **3 OK**.
  `selection_f1` **0.8666666666666666**, `false_activation_cases` **0**,
  `selection_precision` **1.0**, `selection_recall` 0.7647, exact 19/25,
  `corpus_sha256` **`2cff0e405c2f0201759ad8d23ed84fbb60bc1ec7d5513be2ad9b4c54fe5f4565`**
  — **byte-identical to check #27's pinned values.** 6.9/S6 DONE not
  regressed.
- Full `python3 -m unittest discover -s tests` run in foreground — see §9.

## 1. Per-PR reality check (arc = #333–#338/#342, excl. #339 folded into #342)

### #333 — Record operator KEEP disposition on INSIGHT-45727354/-68a53a28

`git show 9ec5d6a`: appends a dated `## Promotion` disposition line to each
insight — "Operator disposition 2026-09-10 (via bigboss): KEEP both — stay on
the insight register as live observations, no promotion to a task, no kill."
This is exactly the N=3 auto-escalation item named by check #27 §6 item 1.
**Resolved before this pass began** — verified the disposition lines are
present in both files at HEAD (§5 below). No further action.

### #334 — Close 2026-08-18 stalled-dispatched-worker repair record

`git show 7dfcbd0`: adds a genuine `## Regression case` section to
`work/notes/2026-08-18-stalled-dispatched-worker-repair.md` pointing at
`scripts/run_tests_sharded.py` (PR #288) + its test coverage
(`tests/test_run_tests_sharded.py`) + the triage-response rule
(`work/coordination/README.md`, PR #95) + CLAUDE.md rules 19/20, plus a dated
operator-closure line. This is exactly check #27 §6 item 3's recommended
option (b)/(c) — operator confirmed the record adequately discharged and a
real regression-case pointer was added, rather than fixing the script's
generic substring-scan weakness. Verified `python3 tools/triage_status.py
--root .` at HEAD reports **0 unresolved, nothing open** — and this time the
record is genuinely closed (real `## Regression case` heading present), not
a keyword coincidence. See §3.

### #335 — Fail closed on UNKNOWN recovery resume before direct fallback

`git show 82f6373`: real `runtime/` change. Before this PR, `tick()`'s direct
hcom-resume fallback treated any non-canonical-denial resume outcome the same
way, including one whose `RetryDisposition` was `UNKNOWN` (an ambiguous
external effect — the harness attempt may or may not have actually resumed
the session). The fix adds `_PRE_DISPATCH_RESULT_CODES` (canonical denials +
`CANONICAL_GUARD_REQUIRED`, which keep their existing handling) and
classifies anything else with `retry == UNKNOWN` and `not result.ok` as
`ambiguous_external_outcome`, suppressing the same-tick direct fallback so an
already-ambiguous harness attempt is never doubled by an unconditional retry
through the legacy path. `tests/test_recovery_external_effect_ambiguity.py`
(160 lines, mostly new/rewritten) exercises both the suppressed and
not-suppressed branches. Independent review `vivo` APPROVE (`work/tasks/
recovery-unknown-same-tick-fallback.md` scopes it; a design note records the
policy rationale). No `CAPABILITY_CHECKLIST.md` row references this precise
mechanism by name — it is recovery-supervisor hardening under the existing
RnS/E-series lineage, not a new capability. No status claim to correct.

### #336 / #337 — Trusted reviewer execution lineage (design + audit)

`git show 4819c4a` / `git show 7110fa9`: both are `work/notes/` design and
audit documents plus review evidence — no `runtime/` or `tests/` change,
confirmed via `git show --stat`. #336 designs a lineage record for which
agent/session actually produced a given review-evidence file (motivated by
the reviewer-self-claim / clone-provenance friction recorded in earlier
FRICTION_LOG entries); #337 audits the current `check_review_evidence.py`
producer path against that design and finds no code gap requiring immediate
correction (its own text: an audit, not an implementation authorization).
Neither claims a capability-status change; neither touches
`CAPABILITY_CHECKLIST.md`. Consistent with their own scope statements.

### #338/#342 (via #339) — Canonical task/history retention design + enforcement

`git show cabf344` (#338, design) + `git show bfae290` (#342, enforcement,
folds in #339's regression-repair commits): `runtime/state/schema.sql` gains
retention-guard schema (+23 lines); `tests/test_task_history_retention.py`
is new (101 lines) asserting three retention guards over the canonical task/
event history. #339's commits (visible inside #342's history) show the
assertion first used the wrong READY event name, then omitted the
`TASK_POLICY_UPDATED` shaping-hook event — a real drift between the test's
assumed event sequence and the actual lifecycle-hook vocabulary, **not** a
defect in the three retention guards themselves (which passed throughout).
This was captured as a FRICTION_LOG entry same-arc (see §3) and closed
same-arc with a verified repair — a clean example of the mandatory-capture
rule working as intended, not a carried-forward item.

**PR title note:** #342's title says "supersedes closed #339 -- same content,
base-branch was deleted by #338's merge" per its own body — verified: #339
does not appear as a separate arc entry above because its commits are
folded into #342's commit history (`git log --oneline` shows #339's
individual commit messages — "Record task-history test assumption repair",
"Capture task-history event-sequence drift", "Reconcile retention task with
CI repair evidence" — inside 342's range). No PR was double-counted or
dropped; this matches the dispatch brief's own annotation.

### #340 — Track durable handoff acknowledgment and continuation

`git show 1c35470`: `AGENTS.md` (+4), `templates/handoff.md` (+17),
`work/README.md`, new `work/handoffs/README.md` (83 lines) establishing a
register for durable session-handoff acknowledgment/continuation — a
governance/process doc, no `runtime/` or `tests/` change, no
`CAPABILITY_CHECKLIST.md` touch. Same category as #319 (arc #27) and
#336/#337 above: a playbook/process-surface addition, reviewed
independently, not a capability-status change.

## 2. Scoreboard re-derivation

Direct count of `work/roadmaps/CAPABILITY_CHECKLIST.md` §7 6.x table
(`^\| *6\.\d+ *\|` rows), Status column:

| Status | Count | Rows |
|---|---|---|
| DONE | **19** | 6.1 6.2 6.3 6.5 6.6 6.7 6.8 6.9 6.13 6.14 6.15 6.16 6.18 6.23 6.26 6.27 6.28 6.29 6.30 |
| IN PROGRESS | **10** | 6.4 6.10 6.11 6.19 6.20 6.21 6.22 6.24 6.35 + 6.33 (evaluation-only, by design) |
| NOT STARTED | **6** | 6.12 6.17 6.25 6.31 6.32 6.34 |
| **Total** | **35** | |

**19 / 10 / 6 — unchanged from check #27.** No flip; none warranted by this
arc's evidence (arc touched zero checklist lines, confirmed §"Setup").

## 3. Friction-log consumption

Walked `work/coordination/FRICTION_LOG.md` in full + ran
`python3 tools/triage_status.py --root .`:

```
# Triage status (advisory - read-only)

FRICTION_LOG: 16 entries - 7 closed, 9 open (0 unresolved).

Nothing open. The triage loop is current.
```

- **16 entries now** (was 15 at #27): the new 2026-09-10 "exact task-event
  sequence assumption drifted from shaping hooks" entry (from #339/#342, see
  §1) is present, `countermeasure` named, `verified:` line present ("Runtime
  stack #1651 passed on repaired head `977a6a6…` on 2026-09-10"), `follow-up:
  none; first occurrence" — **CLOSED** by its own text, same-arc. No pass
  action owed.
- **2026-08-18 stalled-dispatched-worker record — genuinely resolved this
  time.** #27 flagged that `triage_status.py`'s "Nothing open" for this
  record was a **false negative** (the naive `"regression" in text.lower()`
  substring scan matched coincidental prose, not a real `## Regression case`
  section). #334 (this arc, per operator disposition 2026-09-10) added an
  actual `## Regression case` heading with concrete pointers. Read the file
  directly at HEAD: the heading exists, is not coincidental, and the
  disposition matches. **The specific masking instance named at #27 is
  closed for real, not by keyword coincidence.**
- **The general `parse_repair_note` naive-substring-scan weakness** (any
  future record whose disposition prose happens to contain the word
  "regression" would pass the check without a real `## Regression case`
  heading) **was not fixed at the script level — by explicit operator
  choice**, per the 2026-09-10 disposition (session-41 handoff, item 2):
  "operator chose 'confirm the record closed' over 'change the script'."
  This is an explicit, dated operator decision, not an oversight. **This
  pass's disposition: closed as a known, accepted residual risk — no further
  carry-forward.** If a *different* record is masked this way in the future,
  that is a new occurrence with its own recurrence count under the
  Nth-occurrence ladder (§REPAIR_AND_LEARNING.md), not a re-open of this one.
  See §6 "carry-forward dispositions" for the formal record.
- **0 unresolved, 0 OVERDUE.** No entry needs a disposition this pass beyond
  what is recorded above.

## 4. Named findings

### 4.1 6.22 BEFORE_SEND — WATCH becomes a FINDING (3rd unexercised arc)

Per check #26 §8 / #27 §4 item 2 / #27 §8: "if a 3rd arc passes with call
sites but no exercise, that is itself a finding." Verified at HEAD:

- `work/roadmaps/CAPABILITY_CHECKLIST.md` row 6.22 (line 131) is **unchanged
  since its 2026-09-05 update** — this arc's diff confirms zero touch to
  that file. The row's own text still states the blocker verbatim: "Still
  needs a production `send()` caller emitting a `memory_provenance`
  payload."
- `git diff --stat 7ee1e33..HEAD` touches `runtime/recovery/supervisor.py`,
  `runtime/state/schema.sql`, and two test files — **no**
  `runtime/context_delivery.py`, `runtime/harness/hooks.py`, or
  `runtime/policy/memory_provenance_guard.py` change, and no
  `send-context --deliver-context` invocation recorded anywhere in `work/`
  for this arc.
- `work/reviews/pr-307-review-evidence.md` (independently re-read this pass)
  confirms #307 was a **design-note scoping review**, not an operator ruling
  on the "no organic `send()` caller" question raised by #307 itself — no
  operator ruling has landed since.
- **Call-site landed arc #26 (#310). Arc #27 passed unexercised. Arc #28
  (this pass) passes unexercised. That is 3 consecutive arcs — the
  threshold check #26/#27 set is now met.**

**Disposition: FINDING, not an emergency.** This does not change the route
to DONE (6.22 correctly stays `IN PROGRESS`; nothing was overclaimed), but
the design-note→call-site→deferred-exercise cadence for this row has now
stalled 3 arcs running, matching exactly the pattern `IDEA-497fca2f`
(captured #27) exists to track. **Recommendation (propose, not authorize):**
the coordinator either (a) open the bounded assembler-PR task #307 already
scoped (`render_context_send_payload` + one delivery call site + a
default-off `--deliver-context` flag — #307's review evidence §4
characterizes it as a bounded impl PR, not a subsystem), or (b) get an
explicit operator ruling on #307's "no organic caller" question if the
operator judges the exercise not worth building deliberately. Either closes
the stall; leaving it to a 4th arc without one of these would itself need a
stronger justification than "still watching."

### 4.2 IDEA-fe6c0f0f — 2nd arc since promotion, still no follow-up opened

Check #26 promoted (recommended) the diff-equivalence acceptance idea for
`scripts/check_review_evidence.py`'s revalidation tier (rebase-safe
diff-equivalence instead of literal `is-ancestor`). Checked `work/tasks/` +
`git log --all` for any equivalence/ancestor/revalidation task or PR this
arc: **none found** (same result as #27's check). This is the **2nd
consecutive arc since promotion with no movement**. The N=3
incubate-without-movement escalation bound (per ROADMAP_TRAJECTORY_CHECK.md
§"Emergence pass") would land at check #29 if arc #29 also passes with
nothing opened.

**Disposition this pass: promote (still), named as an operator/coordinator
item, 1 arc from the escalation bound.** Not yet an auto-escalation — but
close enough that the coordinator should treat opening this task (or an
explicit deferral record) as a priority candidate for the next work slot,
to avoid an unforced N=3 escalation at #29.

## 5. Emergence pass

### Phase 1 — Imagine

Ran against this arc + the accumulated backlog. This arc is smaller and more
homogeneous than #27's (6 PRs, one real runtime hardening PR + one
schema/test PR + four governance/design docs) — imagining against it
directly surfaces less than #27's cross-root reconciliation wave did.
Cross-root synthesis pass (per EMERGENCE.md "Cross-root synthesis"):
compared this arc's governance-surface additions (#336/#337 reviewer
lineage, #340 handoff register) against `INSIGHT-f095b669` (captured #27:
"outward-facing representations have no reconciliation cadence like the
roadmap has"). Candidate: #336/#337/#340 are all *new* standing registers
(reviewer-lineage record, handoff register) created without an explicit
periodic-reconciliation owner analogous to this trajectory check — the same
shape of gap `INSIGHT-f095b669` named for the wiki/Pilot-evidence bundle,
now recurring for two more artifacts. This clears the Capture bar (source A
= `INSIGHT-f095b669`, source B = #336/#337/#340's new registers, connection
= same missing-reconciliation-owner shape, implication = the gap generalizes
beyond outward docs to any new standing register, falsifier = check whether
either register accumulates drift by the next arc with no reconciliation
step). **1 record captured**:

- **`INSIGHT-bbb3b845`** — *New standing registers (reviewer-execution
  lineage, handoff register) are created without a named reconciliation
  cadence, the same gap `INSIGHT-f095b669` named for outward docs.* Captured
  via `scripts/emergence.py capture` (file added in this PR:
  `work/insights/2026-09-12-new-standing-registers-created-without-a-named-reconciliatio-INSIGHT-bbb3b845.md`).
  Next test: check at #29 whether either register (handoff acks, reviewer
  lineage) has drifted from actual review-evidence/handoff practice with
  nobody assigned to notice.

Zero-record outcomes are valid but did not occur here — 1 substantive record
filed, so the "nothing worth imagining, arc after arc" §7 signal does not
apply to this pass either.

### Phase 2 — Sweep (`work/insights/` + `work/ideas/`)

| Record | Disposition | Rationale |
|---|---|---|
| `INSIGHT-e0b448a6` (tick zero prod invocation) | **kill / keep-as-history** | Already STALE 2026-09-03, reaffirmed #27. No new evidence this arc changes it. |
| `INSIGHT-75785aae` (harness layer zero prod callers) | **kill / keep-as-history** | Already STALE 2026-09-03, reaffirmed #27. No new evidence this arc changes it. |
| `INSIGHT-102296b5` (`--enforce-canonical-run` structurally unreachable) | **stale (already disposed)** | Unchanged since #26. |
| `INSIGHT-651d8c62` (7-row cluster one step from DONE) | **stale (already disposed)** | Unchanged since #26; 6.22 now a named finding (§4.1), consistent with this record's original observation. |
| `INSIGHT-29a10ad4` (`check_review_evidence.py` head_sha walk-back stops silently) | **incubate (pass 3)** | Still tied to `IDEA-fe6c0f0f` cluster (§4.2), which is itself not yet opened. Not at N=3 on its own separate count — first incubated #23-ish per its cluster, tracked jointly. |
| `INSIGHT-ab696436` (design notes carry stale forward-refs) | **incubate (pass 3)** | No new occurrence this arc (#335/#336/#337/#338/#340 all reference real, current state — none of the "blocked on X where X is merged" pattern). Continues incubating. |
| `INSIGHT-a6406800` (`triage_status.py` earned its keep) | **stale / keep-as-history** | Unchanged; the over-reporting counter-fact from #27 is itself now resolved (§3). |
| `INSIGHT-45727354` (friction-log behavioral entry path lets repeats slip) | **KEEP (operator disposition, 2026-09-10, PR #333)** | N=3 bound reached and resolved by explicit operator KEEP before this pass began. Verified present in file at HEAD. No longer an open incubation. |
| `INSIGHT-68a53a28` (trajectory check has become part of the process) | **KEEP (operator disposition, 2026-09-10, PR #333)** | Same as above. |
| `IDEA-582cc671` / `IDEA-968eb261` | **stale — implemented; residual = `IDEA-fe6c0f0f`** | Unchanged since #26/#27. |
| `IDEA-20615e4d` | **stale — superseded** | Unchanged. |
| `IDEA-bc6cd243` / `IDEA-a134ad7c` / `IDEA-9e7014fa` | **stale — promoted → PR #283 (MERGED)** | Unchanged. |
| `IDEA-fe6c0f0f` | **promote (still), 2nd arc unopened** | §4.2. Operator/coordinator item, 1 arc from N=3. |
| `IDEA-497fca2f` (standing first-exposure-exercise tracking list) | **incubate** | Not yet built; #4.1's 6.22 finding is exactly the case this idea would have made cheaper to track. Next test unchanged from #27. |
| `INSIGHT-f095b669` (outward reps have no reconciliation cadence) | **incubate (pass 2)** | This arc's Imagine phase (above) found a 2nd instance of the same shape (#336/#337/#340 registers), strengthening rather than closing it. Not yet N=3. |
| `INSIGHT-bbb3b845` (captured this pass) | **incubate** | Fresh; next test named above. |

No record is at the **N=3 incubate-without-movement** auto-escalation bound
this pass (the two that reached N=3 — INSIGHT-45727354/-68a53a28 — were
resolved by operator KEEP before this pass began, per §5 table).

## 6. Carry-forward dispositions (explicit, per dispatch)

1. **6.22 BEFORE_SEND WATCH → FINDING.** See §4.1. Not an emergency; named
   and a concrete two-option recommendation given.
2. **`INSIGHT-e0b448a6` / `INSIGHT-75785aae`** — both remain **kill /
   keep-as-history**, unchanged since 2026-09-03. No new evidence this arc
   reopens either; both zero-caller conditions they named were closed by
   #165 / #277 respectively and 6.4/6.22 exercise activity since has not
   disturbed that.
3. **`IDEA-fe6c0f0f` + `triage_status.py` substring-scan observation** — both
   given explicit disposition this pass:
   - `IDEA-fe6c0f0f`: still promoted, 2nd arc since promotion with no task
     opened (§4.2). Named as an operator/coordinator priority item, 1 arc
     from the N=3 escalation bound (would land at #29).
   - `triage_status.py` substring-scan: the specific 2026-08-18 masking
     instance is **genuinely closed** this arc (§3, §1 #334). The general
     script weakness (any future record's disposition prose accidentally
     containing "regression") **stays unfixed by explicit operator choice**
     (2026-09-10) — closed as an accepted residual risk, not carried forward
     as an open item. A future masking incident on a *different* record
     would open fresh under the Nth-occurrence ladder, not reopen this one.

## 7. Operator-decision items

Nothing here blocks `CONTINUE`; named so the pass does not record a clean
result without listing them:

1. **6.22 `BEFORE_SEND` finding (§4.1)** — recommend the coordinator either
   open the already-scoped #307 assembler task, or get an explicit operator
   ruling on the "no organic caller" question. Not urgent, but the 3-arc
   stall pattern this check exists to catch has now fired once.
2. **`IDEA-fe6c0f0f` follow-up (§4.2)** — 2nd arc since promotion, 1 arc from
   N=3. Recommend prioritizing before #29.
3. **PR #341** (`eval/protocol-effectiveness-benchmark-v0`) is **OPEN, not
   merged** at time of this pass — not part of arc #28, noted only for the
   next pass's continuity (it predates nothing in this arc; unrelated topic).

Both items 1–2 are recommendations, not authorizations, per this playbook's
"propose vs. dispose" split (EMERGENCE.md Phase 3) and the AGENTS.md rule
that this pass MAY NOT create the task/PR itself.

## 8. TENTH_SEAT_REVIEW.md §7 — "signs this has gone wrong"

Read against minority reports accumulated since check #27
(`work/reviews/trajectory-27-minority-report.md`):

- *All GREEN, all short, all ten-minute* — **does not apply this pass**: #28
  is not a clean pass. It names a real finding (6.22, §4.1) and a
  near-escalation item (`IDEA-fe6c0f0f`, §4.2). **Trigger 2 does not fire a
  2nd consecutive time** — the "found nothing, after passes that found
  something" condition requires *this* pass to find nothing, and it does
  not.
- *Tenth Seat gets less context/evidence* — n/a; no Tenth Seat dispatch this
  pass (not required — Trigger 2 did not fire).
- *Challenges detail, never foundation* — n/a for the same reason.
- *Same agent keeps drawing the role* — n/a.
- *Report written after the merge to paper over* — n/a; no minority report
  needed or written this pass.
- *Reports accumulate, nothing reopens* — the #27 minority report's
  underlying question (was CONTINUE complacent) is answered by this pass's
  own finding: no, the practice caught something real one arc later,
  exactly as the cadence is supposed to work.

**No §7 alarm. No minority report required this pass** (Trigger 2 condition
not met — this pass found something).

## 9. Full test suite

`python3 -m unittest discover -s tests` run in foreground (auto-moved to
background by the harness after the 10-minute foreground limit; result
verified from the same run, not a separate re-run):

```
Ran 1356 tests in 2150.314s

OK (skipped=6)
```

**Exit 0. No failures, no errors, 6 expected skips.** No regression in the
full suite this arc.

## Resume prompt

You are running roadmap trajectory check #29 for MAPS_Lean. Independent
author lane. Follow `playbook/ROADMAP_TRAJECTORY_CHECK.md` (5-step +
friction-log consumption + Emergence pass) and `playbook/TENTH_SEAT_REVIEW.md`
§7. Fresh clone to a UNIQUE path; verify `git rev-parse origin/main` ==
`HEAD`, `git status --porcelain` empty. NEVER touch `~/Projects/MAPS_Lean`,
`.claude/worktrees/`, or `.maps/` for writes.

Anchor: the squash commit of check #28's own PR (find with `git log --oneline
--grep='Roadmap trajectory check' main | head -1`). Enumerate
`git log --oneline <anchor>..HEAD`, check every PR — do not hand-list.

Carried to #29 explicitly:
1. **6.22 `BEFORE_SEND` finding fired at #28** (§4.1). Check whether the
   coordinator opened the #307 assembler task, got an operator ruling, or
   neither. If neither and a 4th arc has now passed unexercised, escalate
   more strongly than "finding" — this is the pattern repeating past its
   first flag.
2. **`IDEA-fe6c0f0f`** (§4.2) — 1 arc from N=3 at #28; check whether #29 is
   the 3rd consecutive arc with nothing opened. If so, this is now an
   auto-escalation item per the ladder — name it in the operator section,
   do not record clean without listing it.
3. **`INSIGHT-f095b669`** (outward reconciliation cadence gap, incubating
   pass 2 at #28 with a 2nd occurrence found) — a 3rd occurrence would be
   worth naming as a stronger pattern.
4. Re-derive the scoreboard from the §7 6.x 35-row table by direct count —
   expect 19/10/6 unless something moved; flag the coordinator before any
   flip.
5. `python3 -m runtime.smoke` must exit 0; run the full test suite in the
   foreground per CI's `python -m unittest discover -s tests -v` step — do
   not background-and-poll it.

DELIVERABLE: one PR, branch off `main`, titled `Roadmap trajectory check #29
(<anchor>..HEAD — PRs <list>) (#<PR>)`, adding
`work/notes/<date>-roadmap-trajectory-check-29.md` + any emergence-sweep
dispositions + friction-log follow-ups in the same PR. Update
`CAPABILITY_CHECKLIST.md` ONLY if a status genuinely moved — flag the
coordinator first. You do NOT self-review, self-approve, or merge.
