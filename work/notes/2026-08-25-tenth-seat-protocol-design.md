# Design note: Tenth-Seat adversarial review for MAPS_Lean testing/review

Date: 2026-08-25. Author: dispatched agent `aa8bbf4112c1d17ed`. Base:
`origin/main` @ `8923adb`.

## 0. What this proposes, in one sentence

A **testing/review methodology extension** — one narrow, rotating "construct
the strongest case this is wrong" step on two specific high-consensus moments —
delivered as a playbook procedure (`playbook/TENTH_SEAT_REVIEW.md`, added in
this same PR) and **no runtime code, no CI gate, no daemon, and no new roadmap
capability number**.

## 1. Source and its honesty about itself

The operator supplied `The_Tenth_Seat_Protocol.md`, which labels itself:

> **Status:** Fictional protocol inspired by real historical and institutional ideas.

It is a constructed protocol, not an established methodology. Its own
"Historical Accuracy Note" says it should not be presented as authentic Jewish
legal procedure, official Israeli intelligence doctrine, or a historical system
of that name. Its cited *precedents* are real and load-bearing for the design:

- **Sanhedrin 17a** — a unanimous capital conviction is procedurally defective,
  because nobody remained able to argue the other side. The derived principle
  the protocol states is the one this design actually uses: *a decision process
  may be defective when nobody can seriously articulate the other side.* Note
  what it is **not** claiming — unanimity is not evidence the conclusion is
  false, only evidence the process stopped testing itself.
- **Mishnah Eduyot 1:5** — a rejected minority opinion is preserved because a
  later court may need it. Decision and memory are separated.
- **Agranat Commission / Israeli "devil's advocate" alternative-analysis
  functions** after 1973 — dissent should be built into the institution rather
  than depend on one brave individual.

Per `playbook/AGENT_GRADE_INSTRUCTIONS.md`'s epistemic labels: the precedents
are **REPORTED** (cited by the source, not independently verified here); the
protocol itself is **explicitly fictional** and is being adopted as a *design
input*, not as authority. This note and the playbook doc both say so on their
face rather than quietly borrowing institutional weight the source disclaims.

## 2. What MAPS_Lean already does, and precisely where the gap is

This matters more than the protocol does. Most of the Tenth Seat Protocol is
already implemented here under other names, and proposing it wholesale would
duplicate working machinery.

### 2.1 Independent review — already strong, already mechanical

Every PR requires a freshly-dispatched independent reviewer producing
`work/reviews/pr-<N>-review-evidence.md`, gated by
`scripts/check_review_evidence.py`. The gate binds evidence to the exact
reviewed commit SHA, walks back past evidence-only commits, refuses to walk
past a merge, and fails closed on stale evidence. The script's own docstring
discloses what it cannot prove (that a distinct identity wrote the review) —
the committee review singled this self-disclosure out as unusual and to the
project's credit.

The quality bar is genuinely high. `pr-165-review-evidence.md` reverts to the
parent commit to prove the new tests are non-tautological, tamper-tests a
source-grep guard to prove it actually trips, runs 100 executions to clear a
flake, and then runs 13 perturbations to prove the flake fix did not make the
tests vacuous. That is adversarial verification of a real kind.

**This already covers the protocol's Laws 3, 4, 5 and 12 for ordinary PRs.**
Anything proposing "add adversarial review to PRs" would be relabeling.

### 2.2 The blind committee review — structurally close, but different

`/home/home/MAPS_Lean_Committee_Review_2026-08-19.md` is the project's one
existing exercise of the same *shape*: a fresh agent with zero context read the
whole project and graded it like a thesis committee. It found real things —
the recovery subsystem's total absence of a production trigger, the gap between
"independent review" as a label and what the gate mechanically guarantees, the
absence of any external validation, and it worked a target statement backward
into a milestone chain.

Where it matches a Tenth Seat pass: fresh occupant, no stake in the consensus,
foundational rather than detail-level challenge, written up durably.

Where it **differs**, precisely:

- **Trigger.** It was a one-off, essentially periodic/on-request. It was not
  triggered by unanimity or by the absence of articulated dissent. Nothing
  causes a second one to happen.
- **Method.** It was **open critique** — "find what's weak" — not a
  *steelmanned alternative hypothesis*. It never states "the consensus is X;
  the strongest coherent way X is wrong is Y; here is the evidence we would
  expect if Y, and here is what would disprove Y." That falsifiable-alternative
  structure is the protocol's actual contribution over ordinary critique.
- **Scope.** Whole-project, once. Not attached to any individual decision, and
  so not preservable as a minority report against a specific claim.

So: same spirit, different mechanism. It is precedent for the practice being
culturally acceptable here, not a reason to consider it already covered.

### 2.3 Trajectory checks — careful re-verification, not dissent-forcing

`playbook/ROADMAP_TRAJECTORY_CHECK.md` is a real periodic self-audit and it
demonstrably works: pass #6 caught two genuine review-cycle defects (a
note-numbering collision, a wrong roadmap tag), and pass #7 independently
re-confirmed the zero-production-caller gap for `RecoverySupervisor.tick()`
*before* reading the design note that also claimed it. Passes #4 and #5 found
nothing and recorded "continue, no pivot" — which is useful calibration for
§3's Trigger 2, not a criticism of them.

But read §2 of that doc carefully. Its instruction is "**re-verify, don't
re-read**" — spot-check rows against real `main`. That is careful
re-verification, which is a **weaker property than assigned dissent**. Nobody
is tasked with constructing a competing account of the scoreboard. The check
asks "is each row true?" and never asks "what is the strongest story under
which this whole scoreboard is misleading even though each row is defensible?"
There is no assigned role, no alternative hypothesis, and no artifact that
survives a failed challenge.

### 2.4 The gap, stated exactly

Every mechanism above tests **whether a claim is true**. None of them tests
**whether anyone was ever able to argue it was false**. Those come apart in one
specific place: an approval that produces no findings at all. The gate is
satisfied, the reviewer was independent, the evidence is SHA-bound — and the
process has produced zero articulated case against the claim. That is precisely
the Sanhedrin 17a condition, and it is the only thing in the protocol that
MAPS_Lean does not already do somewhere.

## 3. The two trigger points

Chosen to be rare and non-redundant. Both are specified operationally in
`playbook/TENTH_SEAT_REVIEW.md`; the justification is here.

### Trigger 1 — a status-flipping PR whose independent review returned zero findings

Fires only on the **conjunction** of (a) review-evidence recording literally no
findings, and (b) the PR converting a claim into durable settled status —
flipping a `CAPABILITY_CHECKLIST.md`/roadmap row to `DONE`, or marking a design
note implemented.

Why both conditions:

- **(a) alone is too broad and too weak.** `pr-135-review-evidence.md` is a
  clean zero-finding approval of a five-line test-fixture date change. There is
  nothing there worth steelmanning, and firing on it would be pure ceremony.
- **(b) alone is already covered.** A status flip that drew reviewer findings
  has, by definition, had the other side articulated.
- **Together they are rare and consequential.** Measured over `work/reviews/`
  on `main` @ `8923adb` — 82 files in total, of which **69** are
  `pr-*-review-evidence.md` and the other 13 are older `TASK-*` reports and
  `RUNTIME_INTEGRATION_REVIEW.md`. Method stated so it can be rechecked rather
  than trusted; an earlier draft of this note got two of these numbers wrong
  and the independent review of this very PR caught both, which is a fair
  illustration of the point:
  - Files whose text literally records **"No findings"**: **2** — `pr-134` and
    `pr-135`.
  - Files containing *none* of
    `finding|\bgap|\bnit\b|caveat|concern|recommend|non-blocking|limitation|however`
    (no critique-shaped language at all): **23**. The word-boundary anchors on
    `gap` and `nit` matter — without them the same grep returns 8, but only
    because `nit` matches `init`/`unit`/`Monitor`/`definition`/`sanity`, which
    wrongly excludes files like `pr-117` whose summary reads "No bugs found …
    Verdict: CLEAN, no changes required". 8 was not an upper bound; 23 is a
    loose one.
  - Condition (a) alone therefore describes somewhere between 2 and 23 of 82 —
    roughly **2-28%**, i.e. common. Neither end is exact, because "did the
    reviewer articulate a case against?" is a judgment, not a string match.
    That is the whole reason condition (b) carries the load and detection stays
    a reading task rather than a grep (§5).
  - **The conjunction is what is rare.** Read semantically — the house forms
    `APPROVE (CLEAN)` / `No bugs found` / `No findings`, 26 of the 69 PR files
    — and intersected with merge commits adding a `DONE` line under
    `work/roadmaps/`, it holds for **three**: **#105** (`39fa0ec`, which
    created `CAPABILITY_CHECKLIST.md` with 35 `DONE` lines in a single commit),
    **#111** (`f6a4e57`, S1 → `DONE`), and **#134** (`46d3c5d`,
    portable-deployment D0 → `DONE`). Three in 69 is about **one per 23 PRs** —
    inside the "roughly once per few dozen" band, and the right order of
    magnitude for a step this heavy. **#105 is the sharpest motivating case**:
    35 status rows created at once under a review that articulated nothing
    against them.

Why status flips specifically are the high-consequence class here (protocol
Trigger C, reframed for a docs-and-code project): the checklist is what future
sessions read *instead of re-deriving the truth*. `ROADMAP_TRAJECTORY_CHECK.md`
exists because rows go stale. A wrongly-flipped row is close to irreversible in
practice — not because it cannot be edited, but because nothing prompts anyone
to look at it again for many sessions, and downstream sequencing decisions get
made on top of it in the meantime. The committee review's central finding was
exactly a version of this: the README's capability bullets claim more than the
production wiring supports.

### Trigger 2 — a trajectory-check pass finding nothing, after two passes that each found something

Fires when a pass reports no substantive finding and the two preceding passes
each found a real issue. This is the protocol's Trigger D (extreme confidence)
*conjoined with documented recent evidence of the opposite* — which is what
makes it a signal rather than noise. A sudden clean pass is more plausibly a
shallower check than a suddenly perfect project, and that hypothesis deserves
to be written down and tested rather than assumed away.

The source protocol's own §28 scoring makes the same argument from the other
end: a consensus-reversal rate of zero is evidence the challenges are too weak,
not that the decisions are perfect.

This has **not yet fired**, and the current state matters: passes #4 and #5
found nothing, then **#6 and #7 each found real issues** — two consecutive
non-empty passes. The tripwire is therefore genuinely armed right now for
pass #8. Pre-registering it before it can fire is the honest time to write it.

### Explicitly rejected as triggers

Every routine PR (already covered by independent review, and blanket
application is the ceremony failure mode); any review that returned findings of
any severity (the other side was already articulated); docs/navigation PRs that
flip no status; operator decisions (the operator is the accountable party, not
a consensus).

## 4. Mechanics mapped onto existing artifacts

### 4.1 What "steelmanned alternative" means concretely

- **On a PR:** the Tenth Seat constructs the strongest case the PR should
  **not** merge as-claimed, even if it ultimately concludes it should. The
  realistic alternatives in this codebase are not exotic: the new tests pass
  against the parent commit too; the status row being flipped is broader than
  what was actually built; the thing built has no production caller while the
  row implies otherwise. Critically, the seat can *test* these — revert to the
  parent, run the suite, grep for the caller — so the protocol's "what evidence
  would exist if the alternative were true" step is executable here rather than
  rhetorical. The project already does exactly this kind of check in its best
  review evidence; the change is *who is required to attempt it and when*.
- **On a trajectory check:** the seat constructs the strongest case the
  **scoreboard is wrong** — a `DONE` row is stale, the clean pass sampled only
  the easy rows, a row's evidence is a document rather than merged code.

### 4.2 Minority report artifact — reusing the review-evidence convention

`work/reviews/pr-<N>-minority-report.md` (or
`work/reviews/trajectory-<N>-minority-report.md`), with the same `key: value`
header shape as review evidence (`tenth_seat:`, `head_sha:`, `independent:`,
`verdict:`, `summary:`) followed by prose sections.

Two properties were checked directly against `scripts/check_review_evidence.py`
rather than assumed:

1. The checker resolves exactly `work/reviews/pr-<N>-review-evidence.md`, so a
   differently-named file in the same directory can never be mistaken for it,
   and — importantly given the project's recorded duplicate-key incident — can
   never inject a second `head_sha:`/`reviewer:` line into the flat line-scan
   parser.
2. `_reviewed_code_head` walks back past any commit whose entire diff is under
   `work/reviews/`. A minority-report-only commit therefore does not disturb
   the reviewed-code binding of the PR it accompanies.

So the artifact reuses the existing convention without touching the existing
gate. Verdicts are the protocol's GREEN/YELLOW/ORANGE/RED; BLACK is dropped
(MAPS has no "cannot safely wait" decision class, and
`docs/CHECKS_AND_BALANCES.md` / `playbook/DECISIONS_AND_SAFETY.md` already own
genuine hard-wall escalation).

The report is **preserved regardless of verdict** — Law 7 and Eduyot 1:5. This
is compatible with, not a violation of, "no duplicate truth": a minority report
is durable human-readable evidence like a repair note or design note, grants no
authority, and `CAPABILITY_CHECKLIST.md` remains the single place status lives.
The same framing `ROADMAP_TRAJECTORY_CHECK.md` §3 already uses for trajectory
notes applies verbatim.

## 5. Non-goals (all load-bearing)

- **No permanent assigned-dissenter role.** Rotating, freshly-dispatched
  occupants, never the author, preferably not the reviewer. This is a genuine
  two-way resonance rather than a coincidence: master roadmap **§7.3 rejects a
  fixed permanent agent roster** ("workers/capabilities should be selected for
  work, not turned into a bureaucracy of named personalities"), and the source
  protocol **§25 independently rejects a professional contrarian** ("the seat
  is permanent, the occupant is temporary") because a standing dissenter gets
  tuned out. Adopting this requires relaxing no project non-goal.
- **No mandatory step on routine PRs.** Two narrow triggers only. The source
  protocol's **§24 "No Fake Dissent"** names performative dissent as the
  greatest danger to itself, and lists warning signs this design would trip
  immediately under blanket application. A design that becomes checkbox theater
  fails on the protocol's own terms, not merely on this project's minimalism
  norm.
- **No veto, no new authority.** Law 6: dissent forces examination, not
  paralysis. A RED verdict does not block a merge by itself; the decision-maker
  may proceed and records why. Nothing here changes who may merge or what
  `check_review_evidence.py` requires.
- **No daemon, scheduler, hook, or CI gate.** Master roadmap §7.1 (no large
  persistent supervisor daemon) and §7.9 (no continuous discovery/process-police
  agents) reject that machinery directly. There is also a specific reason a CI
  gate here would be actively harmful: a check that fires on "no findings"
  teaches reviewers to write one decorative finding to avoid it, degrading the
  evidence quality the project depends on. That is a mechanical countermeasure
  that makes the failure mode worse, so trigger detection stays a reading task.
- **No runtime code, no roadmap capability number.** See §6.

## 6. Judgment calls made here, and why

### 6.1 Playbook procedure, not runtime code — and not a work/notes recommendation either

This is fundamentally a convention about *who is asked to think what, when*.
There is no state to store, nothing to validate mechanically, and (per §5) a
deliberate decision that mechanizing the trigger would be counterproductive.
`playbook/` is exactly where this project keeps method-specific instructions of
this shape — `ROADMAP_TRAJECTORY_CHECK.md`, `EXECUTION_INTEGRITY.md` and
`PROGRAM_STEERING.md` are all process conventions with no runtime component.

I also chose to write the playbook doc **in this PR** rather than recommend a
follow-up. The design is small, fully specified, contradicts nothing existing,
and a note that only recommends a doc would be a second artifact for a
follow-up task to re-derive — which is itself the ceremony this design is
supposed to avoid. Rule: smallest change that satisfies the requirement.

### 6.2 No roadmap capability number

Deliberate, and I do **not** make the case for one. H/E/SEC numbers track
capability the system *builds* — code with tests and an exit gate. This builds
no capability, has no exit gate, and cannot be `DONE`. Numbering it would make
it a status row to flip, which is the exact artifact class Trigger 1 exists to
be suspicious of. `playbook/INDEX.md` gets a row; no roadmap file is touched.

### 6.3 Dropped from the protocol, on purpose

Kept out because MAPS_Lean's review is asynchronous, one-reviewer-at-a-time,
and small: §10 pre-registered independent judgments and §18 the second vote
(there is no group to anchor — the reviewer is already dispatched blind, which
achieves the same anti-anchoring end more cheaply); §15 the evidence matrix as
a required table (the prose sections carry it); §28 the scoring program
(measuring calibration across a handful of fires per year would be noise).
BLACK per §4.2. What remains is the falsifiable-alternative structure and the
preserved minority report — the parts that are not already present here.

## 7. Open questions for a follow-up, if one is ever warranted

None of these block adopting the playbook doc; all are better answered by the
first real firing than by more design.

1. **Does Trigger 1's conjunction fire at a usable rate?** Predicted ~1 per few
   dozen PRs from the 82-file sample. If it fires more than about once per ten
   PRs in practice, condition (b) is too loose. Revisit after the first three
   fires, not before.
2. **Who notices the trigger?** Currently whoever is about to merge. A merging
   session reading a "No findings" review is the natural detection point, but
   it is also the party least motivated to add a step. If detection turns out
   to be the failing part, the fix is a line in the merge checklist, not a CI
   check (§5).
3. **Is "no findings" the right operational reading of unanimity?** It is a
   proxy. A review with three cosmetic non-blocking findings and no substantive
   challenge is arguably the same condition, but "substantive" is not
   mechanically decidable and trying to define it invites gaming.
4. **Should a RED verdict on a status flip require the row to be narrowed?**
   Law 6 says no automatic veto. But a RED specifically about a status claim is
   unusual, since the remedy (narrow the row's wording) is cheap and the
   decision-maker keeps full discretion. Left unresolved until it happens.
5. **Should the committee-style whole-project review be re-run on a Tenth-Seat
   footing** — with a stated consensus and a required steelmanned alternative
   rather than open critique? Plausibly the highest-value single application,
   and the committee review's §8 backwards roadmap gives it a concrete
   consensus to challenge. Out of scope here; it is a task, not a convention.

## 7a. Independent review findings, and how they were resolved

Recorded here rather than only in `work/reviews/pr-169-review-evidence.md`,
because three of the four were factual corrections to *this note* and a reader
should not have to reconstruct which numbers moved.

- **N1 — pass #4 found nothing.** Correct; both cited defects were pass #6's,
  and pass #5 was also clean. Fixed in §2.3 and in the playbook. This *helps*
  Trigger 2: #6 and #7 are consecutive non-empty passes, so the tripwire is
  armed now, whereas the claimed non-consecutive #4/#6 pair would have armed
  nothing.
- **N2 — "at most about eight" was not an upper bound.** Correct; `nit` and
  `gap` were unanchored and matched `init`/`unit`/`Monitor`/`definition`.
  Word-anchored, the same grep returns 23, not 8. Re-run and confirmed
  independently before accepting. Fixed; the band is now 2-28%.
- **N3 — the conjunction fired three times, not once.** Correct; #105 and #111
  also qualify on a semantic reading. Re-verified (69 PR evidence files,
  `pr-105` reads `APPROVE (CLEAN)`). Fixed, and #105 promoted to the primary
  motivating example — it is a stronger one than #134.
- **N4 — §7's warning list had no assigned reader.** Fair, and the sharpest of
  the four, since an unowned checkbox is the failure mode this design claims to
  resist. Resolved by naming the next trajectory-check pass as the reader,
  inside `TENTH_SEAT_REVIEW.md` §7 — an existing owner on an existing cadence,
  with no new machinery, per §5.

None were blocking and none changed the design's shape. Two of them were
arithmetic offered as checkable that did not survive checking, which is the
argument for this whole convention made against the note proposing it.

## 8. Boundaries respected by this PR

- Touches `work/notes/`, `playbook/TENTH_SEAT_REVIEW.md`, and one row in
  `playbook/INDEX.md`.
- No `runtime/`, no `tests/`, no roadmap or checklist file, no status row
  flipped, nothing marked `DONE`.
- Creates no new authority surface, no second source of truth, and no runtime
  behavior of any kind.
