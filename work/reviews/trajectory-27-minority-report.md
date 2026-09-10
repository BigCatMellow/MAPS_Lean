# Minority report — Roadmap trajectory check #27

**Author:** `nena` (analysis lane, wearing the Tenth Seat — dispatch allowed the
same agent to write this rather than spawn a sub-agent).
**Date:** 2026-09-09.
**Assigned duty:** `playbook/TENTH_SEAT_REVIEW.md` §7 + check #26 §8 Trigger 2.
The main note records **`CONTINUE` / clean pass / scoreboard 19-10-6 unchanged**.
This report's job is to argue the **opposite**: that #27 is *not* clean and
`CONTINUE` is complacent. Where the argument fails, it says why.

---

## Verdict: **YELLOW** — proceed, but two items are being carried as
"housekeeping" that are one arc away from being real route-to-DONE findings, and
the pass's own cleanliness is partly an artifact of *what landed*, not of the
project being on track.

---

## Argument 1 — "The arc touched zero `runtime/`, so of course it's clean. That's not health, that's a stall."

**The case for NOT clean.** Seven PRs merged and the production code base did not
move. Two of the seven (#320, #324) are *exercises* of code that landed 1–3 arcs
ago; three (#321, #322, #323) are outward-doc reconciliation; one (#325) is a
design note that explicitly changes nothing; one (#319) edits a playbook. The
security/harness cluster has had **one row flip in three arcs** (6.16 at #26) and
**zero at #25's 6.5 and #27**. If a competent outsider looked at "arc after arc
of exercises, reconciliations, and design notes, no shipped capability," they
would not call that on-track — they would call it *circling*. The scoreboard
being unchanged is presented as reassurance; it is equally evidence of no
forward progress toward DONE this arc.

**Why the argument partly fails.** The exercises are not busywork — 6.4's
`BEFORE_DESTRUCTIVE_ACTION` callback and H4's `--enforce-validation` gate had
**never fired in a real pass** before this arc, and the project's own stated
discipline ("no row flips DONE on tests alone; needs first production exposure")
*requires* these exercise PRs. #320 and #324 are the correct, deliberate shape
for closing 6.4 and H4 eventually. And the arc anchor (25c7729, 2026-09-08) to
HEAD is ~24 hours of wall-clock — one arc is small. Judging "circling" on a
single ~1-day arc is an overreaction.

**Residual concern that survives:** the *cadence* is real and the main note
under-weights it. See Argument 3.

## Argument 2 — "E4 and 6.5 were flipped to DONE on the wrong evidence, and #27 just papered over it."

**The case for NOT clean.** E4 and 6.5's exit gate is *validation-tier outcome
enforcement* ("immediate deterministic validation" — enforced, not observed).
Both were flipped **DONE on 2026-09-05** citing the DEC-003 option-B exercise,
whose `resume_denied` came from `CanonicalRunGuard` / `LEASE_EXPIRED` — a
**canonical-run identity** denial, not a validation-tier denial. The
`--enforce-validation` gate did not get its first real exposure until **#324, on
2026-09-09** — four days *after* E4/6.5 were already marked DONE. So for four days
(and across check #26, which "re-derived the scoreboard" and accepted 19-10-6)
E4 and 6.5 claimed DONE on evidence that did not actually exercise their exit
gate. #27 "reconciling" this with a one-line annotation *ratifies* a flip that
was premature when made. The honest move would be to ask whether the 2026-09-05
flip should be reverted pending independent confirmation that #324's evidence
truly closes the gate.

**Why the argument mostly fails.** (a) The 2026-09-05 flip was independently
reviewed and merged, and check #26 independently re-derived the scoreboard with
E4/6.5 DONE — two prior independent gates accepted it. Re-opening now, on the
same facts those gates saw, needs a defect they missed, and this pass did not
find one: E4/6.5's *prose* already contained a defensible reading (the
canonical-run enforced pass converting a working resume into a denial *is* "a
first production exposure of an enforced pass," which is the literal clause both
rows cite). (b) #324 now *independently* satisfies the narrower
`--enforce-validation` reading too, so whichever reading you take, both rows are
now supported. (c) Reverting a DONE row on a 4-day-old independently-reviewed
flip, absent a concrete defect, would itself be a status-truth violation in the
other direction.

**Residual concern that survives:** the E4/6.5 rows carry **interleaved
contradictory prose** — "Still `IN PROGRESS` because…" fragments sitting next to
"Row flips **DONE** on this evidence." A future reader doing a fast scan can
genuinely misread these rows. The #27 annotation helps but does not clean the
history. **Recommendation: a future bounded pass should rewrite the E4/6.5 row
cells to a single coherent DONE justification**, deleting the stale IN-PROGRESS
fragments (history is preserved in git + the dated notes). Not this pass's
output boundary.

## Argument 3 — "`CONTINUE` is complacent: the design-note→call-site→deferred-exercise cadence is a process defect being tracked as a watch item instead of fixed."

**The case for NOT clean.** Check #26 *already* flagged this exact pattern as a
"new trajectory observation … watch item for #27." #27 arrives and the pattern
**continued**: 6.4 took #306 (call site) + #320 (exercise) across two arcs; 6.22
now has a call site (#310) and no exercise one arc later. A watch item that was
raised last pass and recurred this pass is, by the project's own rule-20 logic
("a failure that repeats gets a durable countermeasure, not just another
instruction"), **due a countermeasure now, not another "watch at #28."**
Default-off code (`--terminate-denied-sessions`, `--enforce-validation`,
`--deliver-context`) is accreting in `runtime/cli.py` faster than it is being
exercised, and each row's closure is now smeared across 2–3 PRs and 2–3 arcs.
Calling that `CONTINUE` with a clean bill is complacent.

**Why the argument partly fails.** The pattern is a *deliberate* safety choice —
land the mechanism default-off, then exercise it under controlled conditions
before flipping. That is slower but correct for a security cluster. And "3
arcs / call site but no exercise" is check #26's own stated finding threshold;
6.22 is at **1 arc**, not 3. Firing the countermeasure now would be jumping the
project's own ladder.

**Residual concern that survives — and this is the strongest one in this
report:** the main note's finding #2 correctly makes 6.22 an explicit WATCH with
an arc counter, but the note's *trajectory action* is still an unqualified
`CONTINUE`. **A more honest action label is `CONTINUE (with one WATCH that
converts to REPRIORITIZE at #28 if 6.22 is still unexercised).`** The captured
`IDEA-497fca2f` (standing "awaiting first-exposure exercise" list) is the right
countermeasure shape and should be promoted, not left to incubate, *if* #28
shows the pattern a third time. The main note's §8 says exactly this — so the
disagreement is one of emphasis, not substance.

## Argument 4 — "IDEA-fe6c0f0f was promoted last pass and nothing happened. The promotion process is broken."

**The case for NOT clean.** Check #26 "promoted" `IDEA-fe6c0f0f`. An arc passed.
No task, no PR, no operator disposition — it is byte-identical to its capture
state plus the #26 disposition line. If "promote" produces nothing an arc later,
either the emergence→task pipeline has no owner or "promote" is a euphemism for
"noted and forgotten." Two other ideas in the same family (`IDEA-968eb261`,
`INSIGHT-29a10ad4`) are also parked. This is a real process gap and #27 files it
as a mild "operator item" rather than a finding about the promotion mechanism
itself.

**Why the argument partly fails.** `EMERGENCE.md`'s Phase 3 authority split is
explicit that the trajectory pass *recommends* and the operator/coordinator
*disposes* — the pass genuinely cannot open the task itself (dispatch boundary
confirms this). One arc (~1 day) of latency on an operator disposition is not
evidence of a broken pipeline. And the idea is a small dev-tooling convenience
(`check_review_evidence.py` rebase tolerance), not a route-to-DONE item — low
cost if it slips another arc.

**Residual concern that survives:** if `IDEA-fe6c0f0f` is *still* undisposed at
#28, that is two arcs, and the finding shifts from "operator latency" to "the
emergence promotion step has no SLA / no owner." The main note's §8 sets the N=3
escalation at #29 — **that is too lenient for an item already promoted once**;
#28 should be the escalation point, not #29. (Minor.)

## Argument 5 — "Trigger 2 fired. Per §7, that means the practice may have failed. The pass should be questioning whether trajectory checks are still worth running, not writing a 9-section note."

**The case.** `TENTH_SEAT_REVIEW.md` §7: *"When a pass finds nothing substantive
after passes that found something, Trigger 2 activates and its §7 duty falls to
whoever runs the next pass."* One of the §7 failure signs is *"Minority reports
are all GREEN, all short, all written in ten minutes."* If #27 is genuinely
clean, the natural next question is whether the ~2-hour trajectory-check ritual
is still earning its cost, or whether it should drop to a lighter cadence
(every 2 arcs, or triggered rather than scheduled).

**Why the argument fails — for now.** (a) This is the *first* clean pass; §7's
"arc after arc" precondition is not met. (b) This minority report is neither
GREEN nor short nor ten minutes — Argument 3 lands a real residual concern. (c)
The pass *did* produce value: it executed the E4/6.5 reconciliation the #324
author explicitly handed off, it captured two emergence records, and it caught
`triage_status.py` over-reporting. A pass that produced those is not a
nothing-pass.

**Residual concern that survives — carried to #28:** if #28 is *also* clean, that
is two consecutive, §7's precondition **is** met, and the #28 pass must
seriously propose narrowing the cadence (the main note's §8 now says this). One
clean pass: keep going. Two: change the practice.

---

## Summary of residual concerns (what a reviewer should pressure-test)

| # | Concern | Severity | Disposition |
|---|---|---|---|
| 1 | E4/6.5 row cells carry contradictory interleaved prose (DONE justification next to stale "Still IN PROGRESS"); fast-scan misread risk | low | Recommend a future bounded row-cell rewrite. Not this pass. |
| 2 | Trajectory action is bare `CONTINUE`; 6.22 WATCH converts to REPRIORITIZE at #28 if still unexercised — the label should carry that condition | low-med | Emphasis disagreement; main note §8 already states the condition. |
| 3 | design-note→call-site→deferred-exercise cadence recurred after being flagged at #26; countermeasure (`IDEA-497fca2f`) should promote at #28 if it recurs a 3rd time | **medium** | Strongest concern. Carried to #28 must-check list. |
| 4 | `IDEA-fe6c0f0f` promoted at #26, undisposed an arc later; N=3 escalation at #29 is too lenient for an already-promoted item | low | Recommend #28 as the escalation point. |
| 5 | Trigger 2 fired; a 2nd consecutive clean pass at #28 obligates a "narrow the cadence" proposal | n/a | Carried to #28 (main note §8). |

**None of these five changes the `CONTINUE` decision for #27.** Concern 3 is the
one an independent reviewer should push on hardest — it is a process defect with
one prior flag, and the line between "watch it once more" and "fix it now" is
genuinely arguable.

## Foundational claims checked and NOT overturned

- Scoreboard 19-10-6: independently recounted from the 35-row §7 table. Correct.
- `runtime.smoke` exit 0; EXP-B f1 0.8666 / false_activation 0 / precision 1.0 /
  corpus sha `2cff0e40…4565` frozen. No regression.
- 6.4 (#320) and H4 (#324) correctly stayed IN PROGRESS. Verified against the
  merged notes + frozen cases, not the PR bodies.
- #321/#322/#323 changed no capability status or roadmap authority. Verified
  against the diffs + independent reviews.
- No row should be DONE that is IN PROGRESS, and no row is IN PROGRESS that
  should be DONE — including a direct check of the "nothing calls this in
  production" foundational objection against 6.4 (call site + exercise both now
  exist) and 6.22 (call site exists, exercise does not — correctly IN PROGRESS).
