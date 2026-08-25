# Tenth Seat Review: Testing a Consensus That Nobody Argued Against

This is a **narrow extension of the review practices MAPS already runs**, not a
new review system. It adds one thing: when a consequential claim reaches
agreement that *nobody argued against*, one agent is assigned to construct the
strongest plausible case that the claim is wrong, and that case is preserved
whether or not it wins.

Everything else stays as it is. `EXECUTION_INTEGRITY.md` still governs reviewer
independence, `scripts/check_review_evidence.py` still gates merges, and
`ROADMAP_TRAJECTORY_CHECK.md` still governs arc-level steering.

## Attribution and honesty about the source

The mechanics here are adapted from **The Tenth Seat Protocol**, a document the
operator supplied. That document states plainly what it is, and this file
repeats it rather than laundering it into borrowed authority:

> **Status:** Fictional protocol inspired by real historical and institutional ideas.

It is **not** an established methodology, an industry standard, an authentic
Jewish legal procedure, or official Israeli intelligence doctrine. It is a
constructed protocol that draws on real precedents it cites directly:
Babylonian Talmud **Sanhedrin 17a** (a unanimous capital conviction is
procedurally defective, because nobody remained able to argue the other side),
**Mishnah Eduyot 1:5** (a rejected minority opinion is recorded anyway, because
a later court may need it), and the post-Yom-Kippur-War **Agranat Commission**
lineage of "devil's advocate" / alternative-analysis functions in Israeli
intelligence. The *precedents* are real; the *protocol* is a modern
construction on top of them, and its own "no fake dissent" section (§24) is the
part this file takes most seriously.

Cite it that way anywhere it is referenced. Do not upgrade it to VERIFIED
methodology — see `AGENT_GRADE_INSTRUCTIONS.md` on epistemic labels.

## 1. The rule

> When a consequential MAPS claim is accepted with **no articulated case
> against it**, one agent — not the author, and not necessarily the reviewer —
> must construct the strongest plausible case that the claim is wrong, and
> record it.

Two things this rule is **not**:

- It is not "disagree with the outcome." The Tenth Seat may conclude the
  consensus is right; the source protocol says so explicitly (§26), and that is
  a successful review, not a wasted one.
- It is not a veto. The decision-maker may proceed over the minority report and
  must simply record why (§ Law 6, and `DECISIONS_AND_SAFETY.md`).

## 2. When it activates — exactly two triggers

Both triggers are deliberately narrow. Volume is the enemy here: a step that
fires on everything becomes the ceremonial dissent the source protocol names as
its own worst failure mode.

### Trigger 1 — a status-flipping PR approved with zero findings

Activates when **both** hold for one PR:

1. The independent review-evidence file records a clean approval with **no
   findings at all** — not "approved with N non-blocking findings", literally
   nothing the reviewer could articulate against merging; **and**
2. the PR **changes a status claim** — flips a `CAPABILITY_CHECKLIST.md` or
   roadmap row to `DONE`, marks a design note implemented, or otherwise
   converts "we think this works" into a durable record that later sessions
   will read as settled and stop re-deriving.

Condition 1 alone is not enough. A zero-finding review of a five-line test
fixture fix is fine and needs nothing. Condition 2 alone is not enough either —
a status flip that a reviewer pushed back on has already been tested by
someone. It is the **conjunction** that matches Sanhedrin 17a: the claim with
the longest downstream half-life is exactly the one nobody could argue against.

Historically rare, by design. Across the 82 review-evidence files on `main` as
of 2026-08-25, exactly two record "No findings", and exactly one of those
(PR #134, flipping portable-deployment D0 to `DONE`) also flips a status row.
Expect this to fire on the order of once per few dozen PRs.

### Trigger 2 — a trajectory-check pass that finds nothing, after passes that found something

Activates when a `ROADMAP_TRAJECTORY_CHECK.md` pass reports **no substantive
finding** — no stale row, no mislabeled status, no changed picture — and the
**two immediately preceding passes each found at least one real issue**.

That pattern is the source protocol's Trigger D (extreme confidence) combined
with documented recent evidence of the opposite. Passes #4 and #6 both caught
real defects (a note-numbering collision; a wrong roadmap tag). A sudden clean
pass is more likely to mean the check got shallower than that the project got
perfect, and that is a hypothesis worth writing down rather than assuming away.

### Not a trigger

- An ordinary PR. Independent review already covers it, and
  `check_review_evidence.py` already gates it.
- A review that returned findings, of any severity. Someone already articulated
  the other side; the seat's whole purpose is already served.
- Docs, notes, and navigation fixes that flip no status.
- Operator decisions. The operator is the accountable party, not a consensus to
  be tested.

## 3. Who sits in the seat

Rotating and temporary. **The seat is permanent; the occupant is not.**

- **Not the PR author.** Same non-self-certification rule the project already
  enforces everywhere.
- **Preferably not the independent reviewer either.** The reviewer is the party
  whose zero-finding verdict is the thing being tested; asking them to
  steelman against their own conclusion is weaker than a fresh agent, though it
  is acceptable when dispatching a third agent is disproportionate.
- **Freshly dispatched, with zero prior context**, in its own worktree
  (`WORKTREE_ISOLATION.md`). This is the same shape as the one-off blind
  committee-style review the project has already run once, and it is the
  cheapest way to get an occupant with no stake in the consensus.

This mirrors — and must not violate — master-roadmap **§7.3, "Fixed permanent
agent roster: Rejected"**. There is no standing "dissenter" agent, no named
personality, no roster entry. The role is a task assigned for one review and
then gone. The source protocol arrives at the same place from the other
direction (§25: a permanent contrarian gets tuned out); the resonance is worth
noting because it means adopting this does not require relaxing a project
non-goal.

## 4. What the Tenth Seat actually does

Answer these, in the minority report. This is the source protocol's §13 list,
trimmed to what a code/roadmap review can actually support:

1. **State the consensus so it could be proven wrong.** Not "the PR is good" —
   "the D0 audit's classification of the installer's state-root behavior is
   accurate, and D0 is therefore complete."
2. **List what must be true for it to hold.** The assumptions, including the
   ones nobody wrote down.
3. **Name the weakest one.** Do not attack everything equally.
4. **Build the strongest alternative** under which the consensus is wrong, that
   a capable person could actually defend. Steelmanned — an obviously silly
   objection fails the protocol on its own terms (§ Law 3).
5. **Say what evidence should exist if the alternative is true**, and go look
   for it. This is where a code review differs from a debate: the seat can run
   the tests, revert to the parent commit, grep for the caller that supposedly
   exists.
6. **Say what would disprove the alternative.** If nothing could, it is not a
   hypothesis.
7. **Estimate the cost of being wrong** — specifically, how far the false claim
   propagates before anything would catch it.

Concretely, per trigger:

- **On a PR (Trigger 1):** construct the strongest case the PR should **not**
  be merged as-claimed, even if you end up concluding it should be. Usual
  shapes: the tests pass against the parent commit too (tautological
  verification — a failure mode this project already checks for by reverting);
  the status row being flipped to `DONE` is broader than what the PR actually
  built; the thing built has no production caller and the row implies it does.
- **On a trajectory check (Trigger 2):** construct the strongest case the
  **scoreboard is wrong** — that a `DONE` row is stale, that the clean pass
  sampled the easy rows, that a row's evidence is a document rather than merged
  code. Re-verify against `main` rather than re-reading the checklist, per
  `ROADMAP_TRAJECTORY_CHECK.md` §2.1.

Evidence belongs to the investigation, not to a side (§ Law 4): the seat must
record evidence that weakens its own alternative, and the author must not
withhold evidence that weakens the consensus.

## 5. The minority report artifact

Reuse the existing review-evidence convention. Do not invent a parallel one.

**Path:** `work/reviews/pr-<N>-minority-report.md` for Trigger 1, or
`work/reviews/trajectory-<N>-minority-report.md` for Trigger 2.

A distinct filename, deliberately — `check_review_evidence.py` looks for
`work/reviews/pr-<N>-review-evidence.md` exactly, so a minority report can
never be mistaken for the review-evidence file, and can never introduce a
duplicate `head_sha:`/`reviewer:` key into the flat line-scan parser that
reads it. It also lands under `work/reviews/`, which the checker's walk-back
already treats as evidence-only, so a minority-report-only commit does not
disturb the `head_sha` binding of the PR it accompanies. Both properties were
checked against the script, not assumed.

Same key-value header shape as review evidence, so the two read alike:

```text
tenth_seat: <agent id -- not the author, ideally not the reviewer>
head_sha: <exact commit the challenge was constructed against>
independent: true
verdict: GREEN | YELLOW | ORANGE | RED
summary: <one-paragraph statement of the alternative and how it resolved>
```

Then, in prose:

```text
# Minority report: <PR / trajectory pass>

## Consensus challenged
## Assumptions it depends on
## Weakest assumption
## Strongest alternative hypothesis
## Evidence that would exist if the alternative is true (and whether it does)
## Evidence against the alternative
## Cost if the consensus is wrong
## Conclusion and verdict
## Reopening indicators
```

**Verdicts**, adapted from the source protocol's five (BLACK is dropped — MAPS
has no decision that cannot wait, and `DECISIONS_AND_SAFETY.md` already owns
genuine hard-wall escalation):

- **GREEN** — the alternative was tested and found no reason to change the
  conclusion. Merge/accept as planned. This is a success, not a null result.
- **YELLOW** — conclusion holds, but real uncertainty surfaced. Proceed and
  record the reopening indicators.
- **ORANGE** — the evidence cannot distinguish the two. Do not flip the status
  row yet; narrow the claim to what is actually proven, or collect the
  discriminating evidence first.
- **RED** — the alternative explains the evidence better. Reopen. The PR does
  not merge as-claimed.

**The report is preserved regardless of verdict** (§ Law 7 / Eduyot 1:5). A
GREEN minority report is not deleted for having lost — it is the durable record
that the claim was actually tested, and the thing a future session reads when a
reopening indicator fires. This is the same ethos as the project's existing
refusal to discard real evidence, and it creates no second source of truth:
`CAPABILITY_CHECKLIST.md` remains the only place status lives, and a minority
report never grants or changes authority.

## 6. Non-goals

- **No permanent assigned-dissenter role.** Rotating occupants only. Master
  roadmap §7.3 rejects a fixed agent roster; the source protocol §25 rejects a
  professional contrarian. Both bind here.
- **No mandatory step on routine PRs.** Two narrow triggers, or it becomes the
  checkbox theater the source protocol names as its own greatest danger (§24).
  If this starts firing on most PRs, the triggers are miscalibrated — fix the
  triggers, do not tolerate the ceremony.
- **No veto and no new authority.** A minority report is evidence, not a gate.
  The decision-maker may proceed over a RED verdict and records why. Nothing
  here changes who may merge.
- **No new daemon, scheduler, hook, or CI gate.** Trigger detection is a human
  or agent reading a review-evidence file, not machinery. Master roadmap §7.1
  and §7.9 reject exactly that machinery, and adding a CI check that fires on
  "no findings" would immediately teach reviewers to write a decorative finding
  to avoid it — a mechanical countermeasure that makes the failure mode worse.
- **No runtime code, no new roadmap capability number.** This is a review
  convention. It builds no capability and belongs to no H/E/SEC lane.

## 7. Signs this has gone wrong

Adapted from §24. If any of these are true, the practice has failed regardless
of what this file says, and it should be narrowed or dropped rather than
performed:

- Minority reports are all GREEN, all short, all written in ten minutes.
- The Tenth Seat gets less context or less evidence access than the reviewer.
- The seat challenges detail and never a foundational claim ("the row should
  say DONE (wired)" is detail; "nothing calls this in production, so no row
  should say DONE" is foundational).
- The same agent keeps drawing the role.
- A report is written after the merge, to paper it over.
- Reports accumulate and nothing ever reopens.

## 8. Relationship to the other review docs

```text
check_review_evidence.py     → does a head-bound review artifact exist at all?
EXECUTION_INTEGRITY.md       → was the reviewer independent of the author?
TENTH_SEAT_REVIEW.md         → did anyone ever articulate the case against?
ROADMAP_TRAJECTORY_CHECK.md  → is the roadmap itself still pointing right?
```

The first two ask whether review *happened*. This one asks whether the review
*found the consensus arguable* — a different property, and the one Sanhedrin
17a is actually about.
