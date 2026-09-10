# Minority report: PR #319 (emergence supersession authority)

tenth_seat: maps-319-tenthman-dula
head_sha: 94f9b5a28fa6292321e6c6c056e35a691c7b19ec
independent: true
verdict: YELLOW
summary: |
  Tenth Seat / Tenth Man pass on PR #319 (the "Change 2" split of former #302:
  emergence may question, compare, redesign, or propose replacement of an
  established MAPS_L mechanism, incl. the emergence lifecycle itself). No prior
  involvement with #302/#315/#316/#319 or authors vena/mezu/viva/nezu or
  reviewer mosa. The steelmanned alternative — that this invites mid-arc
  relitigation of settled mechanisms, erodes stability, and blurs the
  propose/execute line — was constructed and tested against the diff wording,
  the playbook, AGENTS.md, and DECISIONS_AND_SAFETY.md. It did not hold: every
  path this change opens still routes through Capture (filing is not endorsement)
  and a deliberate, never-automated Promote, the INDEX row explicitly parks
  decision/authorization with DECISIONS_AND_SAFETY.md / AGENTS.md, and a
  consequential mechanism replacement additionally hits the human
  reauthorization boundary ("changing a standing rule"). No execution-authority
  leak in the wording. On the operator's stronger bar, this IS genuinely a good
  idea, not merely "no fatal flaw": it closes a real gap (no method currently
  authorizes deliberate generative questioning of a mechanism that is working as
  designed — Repair is drift-driven, Decisions decides rather than generates,
  the trajectory check does route-correction not redesign), it is a minimal
  extension of an Imagine question EMERGENCE already asks, it is cheap and fully
  reversible, and it hard-codes resistance to incumbency bias that the project
  already opposes elsewhere. Verdict is YELLOW rather than GREEN because two
  real (non-fatal) uncertainties surfaced: (a) the top-of-doc clause scopes the
  new power to "any established mechanism" with no ceiling naming playbook
  methods as the target class, which an agent reading EMERGENCE.md on the
  common-case budget (AGENTS.md + roadmap + one method) could over-apply to an
  AGENTS.md hard invariant or the Promote gate itself; (b) the power is granted
  to a lifecycle that is currently near-dormant (E/I capture ~flatlined since
  2026-08-19), so real-world calibration is untested. Neither blocks merge.
  Recommendation: #319 merges; it does NOT go back to mosa and does NOT need a
  3rd reviewer. Record the reopening indicators below.

## Consensus challenged

The substantive claim (stated so it can be proven wrong): **Emergence SHOULD be
able to formally propose superseding an established MAPS_L mechanism — including
its own lifecycle — as a Promote-gated candidate, and `playbook/EMERGENCE.md` is
the right home for that power.**

`mosa`'s APPROVE deliberately did not opine on this; it covered mechanics,
containment, and whether the proposal-only boundary is preserved in the wording.
The operator ruled #319 "APPROVED NARROW & CONDITIONAL" and set the bar that a
pass here must find the change *genuinely good*, not merely un-fatal.

## Assumptions it depends on

1. There is a real gap: no existing method authorizes deliberate, generative
   questioning of a mechanism that is working as designed (not drifting, not
   incident-driven).
2. `EMERGENCE.md` is the least-bad owner of that gap — better than
   `DECISIONS_AND_SAFETY.md` (decides, does not generate),
   `REPAIR_AND_LEARNING.md` (drift/incident-driven), or
   `ROADMAP_TRAJECTORY_CHECK.md` (route correction, not redesign).
3. The propose/execute line holds *in practice*, not just on paper: a candidate
   that targets a mechanism still cannot become execution without Capture +
   deliberate Promote, and a consequential one still hits the human
   reauthorization boundary.
4. "not a design ceiling" / "being established is not evidence a mechanism
   should remain" does not contradict any standing hard rule.
5. The self-referential case ("supersede the lifecycle itself", "expand scope
   ... under the current operating model") is a bounded, gated hazard, not an
   open bootstrapping hole.
6. (Unwritten) Agents will read "any established mechanism" against the
   immediately following authority-clamp sentence and the INDEX non-overlap
   row, not in isolation.
7. (Unwritten) The emergence lifecycle will actually be exercised enough for
   this power to matter and to be corrected if miscalibrated.

## Weakest assumption

**#6** — that "any established mechanism" is read with its clamp. The top-of-doc
clause grants the power over "any established mechanism — including this
emergence lifecycle itself" with no sentence scoping the target class to
`playbook/` methods. AGENTS.md sets the common-case reading budget at "AGENTS.md
+ approved roadmap/task + one relevant playbook method"; an agent who loads
EMERGENCE.md as that one method, mid-arc, could take the clause as license to
put an AGENTS.md hard invariant, a `DECISIONS_AND_SAFETY.md` boundary, or the
Promote gate itself "on the table" as an emergence candidate. The clamp
("current authority continues to govern execution until deliberately changed")
and the INDEX row (decision stays with DECISIONS_AND_SAFETY / AGENTS) do
constrain it — but they constrain *execution*, not *what may be questioned*, and
they live one sentence away / one file away respectively.

Assumption #7 is a close second: the power is real but currently theoretical.

## Strongest alternative hypothesis

**#319 is a mistake because it converts a stability property into an explicit
invitation, and does so at the wrong altitude.**

- The project's working posture is that settled mechanisms stay settled unless
  something forces reconsideration: `SPIDERWEB_AUDIT.md` — "Do not reopen a
  settled decision merely because a newer file discusses it";
  `REPAIR_AND_LEARNING.md` — findings "do not silently become global policy";
  master-roadmap §7.3 rejects a permanent dissenter role. #319's "not a design
  ceiling" framing and its new Imagine question ("Which established mechanism
  survives mainly because it is already established...") point the other way:
  they make relitigating the incumbent a *standing prompt on every pass*.
- The propose/execute line is thinner in practice than on paper. Phase 3 now
  reads "only a promoted item may expand implementation scope **under the
  current operating model**" — i.e. the scope-expansion rule is itself flagged
  as superseble. A coordinator "acting under delegated authority for the bounded
  / low-risk cases" *disposes* captured records; if a mechanism-supersession
  candidate is mis-classified as bounded/low-risk, it could be Promoted without
  the operator, and the operator only re-enters at the human reauthorization
  boundary if someone correctly tags the change "consequential".
- The real owner is arguably `DECISIONS_AND_SAFETY.md` (a mechanism replacement
  is a decision) or nowhere (maybe the project does not need a generative
  "question the incumbent" function at all, given how little E/I is used).
- "supersede the lifecycle itself" is a bootstrapping hazard: a lifecycle that
  can propose removing its own gates is one Promote away from removing them.

## Evidence that would exist if the alternative is true (and whether it does)

- **A playbook hard rule directly contradicted by the diff.** Checked
  (`grep -riE 'incumben|stabilit|relitigat|settled|standing rule|precedent|
  continuity'` across `playbook/`). Result: `SPIDERWEB_AUDIT.md` line 174 is in
  *tension* with "being established is not evidence a mechanism should remain",
  but not a contradiction — SPIDERWEB forbids reopening on *mere discussion*;
  #319 requires *evidence of a better way* and still routes through Promote.
  `REPAIR_AND_LEARNING.md` line 115 ("Structural ... Do not silently apply; use
  a decision/change path") is *consistent* with #319, not broken by it. No hard
  rule contradicted. **Alternative not supported here.**
- **An execution-authority leak in the wording.** Checked every changed hunk.
  "Promotion may also authorize work whose purpose is to replace or supersede
  an existing mechanism" — the actor is *Promote*, which already authorizes
  work; purpose widened, authority not. "A candidate may explicitly target an
  existing MAPS_L process" — Phase 2, and "Filing is not endorsement ... a
  candidate, not a commitment" is the unchanged sentence directly above. Top
  clause verbs (challenge / compare / redesign / propose replacement) are
  clamped by "Current authority continues to govern execution until deliberately
  changed". INDEX row: "the decision/authorization for such a change stays with
  DECISIONS_AND_SAFETY.md / AGENTS.md". `EMERGENCE.md` line 4 ("must not hijack
  an assigned task") is unchanged. **No leak. Alternative not supported here** —
  this was the RED/ORANGE stop condition and it is clean.
- **"established mechanism" scoped too broadly.** Confirmed present: the diff
  says "any established mechanism" with no target-class ceiling. **Alternative
  partially supported** — this is the YELLOW driver, a wording-tightening
  opportunity, not an authority breach.
- **The lifecycle is not actually used, so this is speculative.** Confirmed:
  E/I capture is near-dormant (small handful of records, all one date in
  2026-08-19; a reframe is queued for a later arc). **Alternative partially
  supported** — low urgency, but the change is cheap and reversible, so "grant
  the boundary now, calibrate when used" is defensible.
- **The coordinator-dispose path lets a consequential change skip the
  operator.** Partially supported in principle (misclassification risk) but
  `DECISIONS_AND_SAFETY.md` "Human reauthorization boundary" explicitly catches
  "changing a standing rule" / "materially expanding scope", and #319 does not
  alter that text. Residual risk = a mislabelled disposition, which is a
  pre-existing risk of the Promote model, not created by #319.

## Evidence against the alternative

- The Imagine phase *already* asks "What did we decide once, long ago, that
  nobody has re-examined against current reality?" — questioning settled
  decisions is pre-existing EMERGENCE remit. #319 extends one existing question
  to the class of *mechanisms*; it is not a new job (INDEX 5-point check point
  2 holds).
- The design note's ownership analysis is sound: Repair is drift-driven,
  Decisions decides rather than generates, trajectory check corrects the route.
  None owns "deliberate generative questioning of a working mechanism". The gap
  is real and `EMERGENCE.md` is the coherent owner.
- Every consequential path has two independent catches: the deliberate Promote
  step (operator or delegated coordinator) *and* the human reauthorization
  boundary for standing-rule changes. A bad candidate wastes cycles; it does
  not change authority or execute anything.
- Fully reversible: revert three doc hunks, no code, no state, no migration.
- The change explicitly refuses novelty-preference ("The incumbent may still
  win; novelty receives no automatic preference either") and demands a named
  "current baseline when an established mechanism is challenged" in the Capture
  bar — it raises the evidentiary bar for a supersession candidate rather than
  lowering it.

## Cost if the consensus is wrong

Low blast radius. A bad propose-supersession candidate propagates:
`work/ideas/` file → surfaced in an Emergence pass → one-line proposed
disposition → coordinator/operator disposes. If wrongly Promoted → task
contract or `DEC-NNN` → implementation → independent review → for a standing-rule
or scope change, `DECISIONS_AND_SAFETY.md` human reauthorization. Catch points:
(1) the Promote deliberation itself ("promote deliberately" is unchanged and
never automated); (2) the dispose step; (3) independent review of any resulting
task; (4) the human reauthorization boundary for consequential mechanism
changes. Worst realistic outcome: wasted review/implementation cycles on a
mechanism change that should not have been entertained, caught at review or
reauthorization. Not a safety or authority breach, because the execute path is
structurally unchanged. The one genuinely new failure mode — an isolated reader
over-applying "any established mechanism" to an AGENTS.md invariant — still can
only produce a *proposal*, and AGENTS.md precedence (rank 1, "No other Markdown
file may create a competing set of global agent rules") plus the reauthorization
boundary catch it before it changes anything.

## Conclusion and verdict

**YELLOW.** The consensus holds and the change is genuinely a good idea on the
operator's stronger bar: it fills a real, currently-unowned gap with a minimal,
gated, reversible extension of an existing method, and it strengthens rather
than weakens the evidentiary bar for challenging an incumbent. The steelmanned
alternative — relitigation risk, stability erosion, a thin propose/execute line,
a bootstrapping hazard — was constructed and tested and did not survive contact
with the unchanged Capture→Promote gate, the INDEX non-overlap row, and the
human reauthorization boundary. No execution-authority leak (the RED/ORANGE stop
condition is clean).

It is YELLOW, not GREEN, because two real uncertainties surfaced that a future
session should be able to find: the unscoped "any established mechanism"
phrasing, and the grant of this power to a near-dormant lifecycle.

**Merge recommendation: #319 merges as-claimed.** It does not go back to `mosa`
and does not need a 3rd reviewer. The two items below are optional pre-merge
tightening for the coordinator, not merge blockers.

Optional tightening (coordinator's call, non-blocking):
- Add a half-sentence to the top-of-doc clause scoping the target class, e.g.
  "...any established MAPS_L *method or process* — including this emergence
  lifecycle itself...", to close the isolated-reader over-application path.
- `mosa`'s two non-blocking nits stand: the design note's `## Stacking` section
  and opening paragraph are stale present-tense (Change 1 already merged as
  #315, branch already rebuilt on main); correct before merge so the persisted
  lineage record is not false. The Phase-3 "under the current operating model"
  softening is self-consistent with the thesis and needs no change.

## Reopening indicators

Reopen / revisit this change if any of the following occur:
- An emergence candidate or Emergence-pass disposition cites the "not a design
  ceiling" clause to justify reopening a mechanism with no new evidence of a
  better way (i.e. incumbency-questioning becomes a standing ritual rather than
  an evidence-gated exception) — the `TENTH_SEAT_REVIEW.md` §7 "challenges
  detail and never a foundational claim" failure mode, inverted.
- A mechanism-supersession candidate is Promoted by a coordinator under
  delegated authority without the operator, on a change that later proves
  consequential (standing-rule or material-scope).
- Any agent applies "any established mechanism" to an `AGENTS.md` hard
  invariant, a `DECISIONS_AND_SAFETY.md` boundary, or the Promote gate itself.
- The emergence lifecycle remains dormant through the next 3 trajectory-check
  passes — in which case this power is unexercised ceremony and the clause
  should be trimmed rather than kept.
- Two or more Emergence passes in one arc spend attention relitigating the same
  incumbent mechanism.
