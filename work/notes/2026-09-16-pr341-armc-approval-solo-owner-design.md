# PR #341 — Arm C's independent non-strawman approval under a solo owner: a different problem shape than custody

**Design only. No `GENERIC-CONTROL.md` edit, no selection/benchmark run, no
merge, in this note.**

## 0. Authorization and scope of this note

Relayed by coordinator `venu`, attributed to the operator directly: *"solo
owner, no trusted third party available for ANY of this, same as the
custody problem."*

That confirms the same underlying constraint (no eligible independent human
exists) applies to Gate 1's Arm C approval as it did to Gates 0–3's
selection custody. It does **not** by itself imply the same *fix*
transfers — the operator was asked to confirm the constraint, not to
pre-judge the mechanism. This note's job is exactly that judgment: is Arm
C's approval problem the same shape as custody (in which case
`work/notes/2026-09-15-pr341-custody-descope-design.md`'s public-beacon
mechanism, or something like it, should transfer), or a different shape
requiring a different fix. §2 below concludes it is different, and §3
proposes what a solo owner can actually do about it.

This note is scoped exactly as the custody-descope note's own §7 already
anticipated: that note lists `GENERIC-CONTROL.md` under "Scope boundary:
what stays exactly as-is" — *"still independently reviewed inputs, unrelated
to custody"* — correctly recognizing this as a distinct, untouched question
rather than silently assuming Gates 0–3's fix covers it. Confirmed directly:
neither PR #366 (`9fb1c67`) nor PR #369 (`19d3d36`) touches `GENERIC-CONTROL.md`
at all, or the "### Arm C" section of `INDEPENDENT-CURATOR-START-PROMPT.md`
(`git show <commit> -- <file> | grep "Arm C"` returns nothing for both). Gate
1 is byte-identical to before the custody descope.

## 1. What Gate 1's Arm C requirement actually says, read from source

`GENERIC-CONTROL.md` §"Independence requirement" (verbatim):

> Before issue enumeration/selection, an independent party without a MAPS_L
> development stake must either: 1. explicitly approve this exact text as a
> competent non-strawman control; or 2. reject it and return a
> public/non-secret correction finding before any sample exists.
>
> For `protocol-effectiveness-v0`, the eligible external curator/custodian
> may perform this pre-selection competence approval because they are
> independent from the MAPS_L owner. [...]
>
> Approval must assess whether a competent generic agent can reasonably
> plan, inspect evidence, self-verify, use helpers, respect scope, complete
> separable work, and stop without importing MAPS-specific machinery.

`INDEPENDENT-CURATOR-START-PROMPT.md` Gate 1, "### Arm C" (verbatim, lines
75–85 at current head):

> Independently judge the exact text in `GENERIC-CONTROL.md`.
>
> Approve it only if it is a competent non-strawman generic workflow that
> supports evidence inspection, proportional planning, self-verification,
> useful helper/tool use, scope respect, separable work, and genuine
> blocking without importing MAPS-specific machinery.
>
> If materially weak/biased/MAPS-shaped, stop before selection:
> `PRE-AUTHORING CORRECTIONS REQUIRED`. Do not privately substitute a new
> control and continue.

Both texts assign this job to a role — "independent party," "eligible
external curator/custodian" — that PR #366/#369 eliminated *for selection*
but that Gate 1 still names, unmodified, for Arm C approval. With no
curator/custodian of any kind now in the picture, **nobody currently
eligible under this file's own text can execute Gate 1** — not a gap this
note is introducing, but one PR #366/#369 left exactly where it found it,
correctly (per §0 above), pending this separate analysis.

**What has, and has not, already been independently checked.** Multiple
past independent reviews on this PR checked that the *design's rules*
require and structurally support Arm C being non-strawman-checkable and
capable of winning — this is real, existing evidence and this note does not
need to re-derive it:

- `work/reviews/pr-341-rereview-evidence-0aee65b.md`: *"G1 | RESOLVED | SPEC
  §3: mandatory for Standard/Full; competent generic behaviors; no MAPS
  concepts; independent author/approver [...]"* and *"Arm C credible
  generic comparator: yes."*
- `work/reviews/pr-341-rereview-evidence-dcc064b.md`: *"Arm C can outperform
  MAPS without artifact penalty."*
- `work/reviews/pr-341-rereview-evidence-7ec7e1d.md`: independently caught
  a **regression** where a correction pass silently deleted the Arm C
  independence/competence requirement from the spec text (*"G1 — MATERIAL —
  Arm C independence/competence/disclosure deleted (M2 regression)"*), the
  **second** such regression, triggering `AGENTS.md` invariant 13.

That is all evidence that the *scoring/spec rules* don't structurally
handicap Arm C and that the *requirement to approve Arm C's text* has
survived repeated review pressure without being silently dropped a third
time. **None of it is evidence that the specific candidate text in
`GENERIC-CONTROL.md` has ever actually been judged non-strawman by anyone
but its author.** The five normative owner documents (SPEC/CASE/RUN/SCORING/
REPORT) are the ones pinned by the anchor checker
(`scripts/check_protocol_effectiveness_benchmark_anchors.py`, 49
findings/107 anchors/13 pinned sections, confirmed by re-reading the script
— `GENERIC-CONTROL.md` and `INDEPENDENT-CURATOR-START-PROMPT.md` are not
among the five). `GENERIC-CONTROL.md`'s own hash is pinned separately inside
`PRE-AUTHORING-PACKAGE-MANIFEST.json`'s `package_hash` — but a hash pin only
proves the text has not silently *changed* since some point; it says
nothing about whether that point was ever a genuine independent approval.
Today it was not: the file's own status line says *"REQUIRES INDEPENDENT
COMPETENCE APPROVAL BEFORE SELECTION"* and no review evidence anywhere in
this PR's history claims to have performed that specific approval act.

## 2. Is this the same problem shape as custody? No — name the difference precisely

**Selection custody's threat model:** given a large, already-known space of
possible seeds/formulas/timings, an adversary with private compute time
could dry-run many variants against the known candidate pool and commit to
whichever produces a favorable outcome (*grinding*), or could privately
re-roll a draw they dislike. The `2026-09-15-pr341-custody-descope-design.md`
fix works because this is fundamentally a **predictability/timing**
problem: inject genuine external unpredictability (a NIST beacon pulse that
does not exist yet at commitment time) so that at the moment the rule is
fixed, no one — including the owner — can know or compute the outcome. The
result is then **mechanically, publicly, and objectively verifiable** by
anyone: recompute the committed formula against the published pulse and
compare. No judgment call is needed to check the *output*; only arithmetic.

**Arm C approval's threat model is different in kind, not degree.** The
concern is not that the owner might search over many texts and pick a
favorable one at some unpredictable future moment — `GENERIC-CONTROL.md`'s
text already exists, is already fixed, hashed, and public
(`generic_control_sha256 = 1eb3382e...`). There is no future unpredictable
event whose timing could be exploited, and no beacon can make a
*already-written sentence* more or less competent. The actual concern is:
**is this one, already-fixed piece of natural-language prose a genuine,
competent effort, or a deliberately-weakened strawman** — a content-quality
judgment, structurally identical to ordinary peer review, not to a
commit-reveal protocol. Cryptographic unpredictability has no purchase on a
question like "does this text under-specify self-verification on purpose."

**The concrete consequence for what a fix can look like:** the custody fix
needed no independent human at all, only genuine external randomness plus
public verifiability of arithmetic. Arm C approval has no equivalent
external-randomness substitute — there is nothing unpredictable to inject
into a text-quality judgment. Whatever replaces "independent curator
approves the text" must therefore still produce a **disinterested reading**
in some form, not merely a public and reproducible **computation**. That
reading cannot come from a truly independent party (none exists, per §0),
but — and this is the load-bearing distinction from custody — **Gate 1
never required secrecy the way Gate 0 did.** Gate 0 explicitly excluded "a
normal fresh chat under the same MAPS_L owner's account" as an eligible
custody environment *because custody requires inaccessibility the owner
cannot have*. Gate 1 has no such requirement: nothing about judging whether
a prompt is a strawman requires the judge's reasoning to be hidden from the
owner. That means a fresh, differently-instructed session under the same
account — categorically disqualified for custody — is not categorically
disqualified for producing a useful, falsifiable piece of evidence about
text quality. It cannot provide independence of *interest* (same operator
ultimately directs it), but it can provide independence of *framing*, which
is the axis that actually matters for a quality judgment: does an
adversarially-incentivized read find anything, published in full for anyone
else to check.

## 3. What a solo owner can actually do: falsifiable evidence, not another self-attested read

A plain "the owner read it and it seems fine" approval is exactly the
self-certification Gate 1 exists to prevent, and would be no better than
skipping Gate 1 outright. The goal below is not to manufacture an
appearance of independence that isn't real, but to replace an
**unstructured, unpublished, unfalsifiable** judgment with a **structured,
published, falsifiable** one — consistent with how every other unresolved
gap in this project gets closed (mechanical anchors for the five owners,
public beacon for selection): make the residual trust surface as small and
as checkable as possible, and say plainly what's left over.

Three complementary pieces, in order of how much independent evidentiary
weight each actually carries:

### 3.1 Rules-level non-bias — already done, cite it, don't re-litigate it

As §1 documents, independent review has already confirmed the *scoring and
comparison rules themselves* do not structurally handicap Arm C ("Arm C can
outperform MAPS without artifact penalty," "Arm C credible generic
comparator: yes"). This is real, existing, independently-produced evidence
and should be cited as part of Gate 1's eventual record rather than
re-derived — it answers "could a fair generic control still lose fairly,"
which is a different and already-closed question from "is *this* text a
fair generic control."

### 3.2 A published, adversarially-framed self-critique against an explicit weakness taxonomy

The core proposal. Two structural changes turn "the owner thinks it's fine"
into something checkable:

1. **Invert the incentive before reading the text.** Task a fresh,
   differently-instructed session (same account — this is fine per §2,
   since no secrecy property is needed here) with constructing, *from
   first principles and before being shown `GENERIC-CONTROL.md`*, a
   taxonomy of concrete ways a generic-agent control text could be
   deliberately weakened while still looking plausible — e.g., omitting a
   stopping condition so the arm either quits too early or runs forever;
   omitting or hedging the evidence-inspection step so it never actually
   checks state; omitting proportionality so it either over- or
   under-plans by design; omitting tool/helper guidance so it can't use
   available leverage; adding scope language that quietly forbids
   completing separable work; omitting outcome verification so failures go
   unnoticed; smuggling in an implicit assumption that only makes sense for
   MAPS-shaped tasks. Publish this taxonomy *before* it is applied to the
   actual text, so the criteria cannot be retrofitted to whatever the text
   already says.
2. **Apply the taxonomy adversarially, publish the full attempt.** Run the
   taxonomy against `GENERIC-CONTROL.md` as a checklist, explicitly trying
   to find or construct the strongest case that the text exhibits each
   weakness — not a friendly skim. Publish the complete attempt (taxonomy,
   per-item verdict, and reasoning) as a `work/notes/` artifact, the same
   way `pr-341-rereview-evidence-*` publishes full adversarial-question
   sections rather than a bare verdict line. A future reader does not have
   to trust "APPROVE" on its own — they can independently judge whether the
   taxonomy is honest and whether the item-by-item reasoning actually
   defeats each weakness, exactly as this PR's own reviewers already do for
   every other artifact in this package.

This does not manufacture true independence — the same operator ultimately
controls who runs the adversarial pass and what taxonomy it starts from.
What it changes is falsifiability: an unstructured "I read it, it's fine"
cannot be checked by anyone else without redoing the whole judgment from
scratch; a published taxonomy applied item-by-item can be checked by
reading the artifact, the same way this PR's mutation matrices and
adversarial-answer sections let a fresh reviewer (like this note's own
author) re-verify a prior pass's work without re-deriving it independently
from nothing.

### 3.3 An external, non-MAPS-authored anchor, where one can be honestly identified

A second, weaker but genuinely disinterested-adjacent check: compare
`GENERIC-CONTROL.md`'s structure against a specific, citable, published,
non-MAPS-authored generic-agent-instruction pattern (e.g. from the agent
literature this benchmark already draws on in
`work/evals/protocol-effectiveness-benchmark/REFERENCES.md`), on the same
seven properties Gate 1 already names (evidence inspection, proportional
planning, self-verification, tool/helper use, scope respect, separable
work, genuine blocking). If `GENERIC-CONTROL.md` matches or exceeds an
external, non-owner-authored reference on each named property, that is
evidence anchored to something the owner did not write, narrowing "is this
good, by the owner's own sense of good" to "does this match an external
baseline on enumerated properties, checkable by anyone who reads both
texts." **Honesty check on this note's own claim:** no specific external
generic-agent-prompt exemplar is identified or verified here — `REFERENCES.md`'s
current five external sources are evaluation-*methodology* papers (HELM,
protocol-aligned agent evaluation, position bias, contamination), not
published generic-agent-prompt texts suitable for a direct structural diff.
Identifying a genuinely apt, citable exemplar (if one exists) is named here
as a candidate strengthening step for the follow-up pass (§7), not claimed
as already available.

### 3.4 A deferred, pre-registered empirical manipulation check (not run now)

The strongest possible evidence — does an agent that actually follows
Arm C's text behave meaningfully differently from one given no instructions
at all, on throwaway pilot tasks disjoint from the frozen 48-case pool —
is explicitly **out of scope for this note and this stage**: this task's
own output boundary prohibits running any selection or benchmark, and the
Gate-1 curator role itself is "not authorized to execute A/B/C benchmark
agents or spend money." Comparing Arm C against Arm B (MAPS_L) directly
would also pre-judge the very question the benchmark exists to answer and
would burn real evidence before selection even completes. Named here as a
**pre-registered future validity check**, not attempted: once tooling
exists, run Arm C's instructions against a null/no-instruction baseline on
a small number of disposable practice tasks (never the frozen pool or
holdout), and confirm Arm C measurably outperforms doing nothing — a
manipulation check, not a comparison to MAPS_L. This is confirmatory
evidence layered on top of §3.2/§3.3, not a substitute for them, and is not
something this note builds or schedules.

## 4. Residual risk, stated plainly

None of §3.1–§3.4 closes this the way §3 of the custody note actually
closed grinding with a real cryptographic guarantee. That closure was
possible there because the threat was predictability of a *future*
event; here the threat is the *quality of an already-fixed text*, and no
commitment scheme substitutes for a genuinely disinterested read. §3.2's
adversarial self-critique and §3.3's external anchor are real
improvements over an unstructured self-approval — they make the judgment
falsifiable and inspectable by a future reader instead of asserted — but
they do not eliminate the possibility that the owner (via whichever session
or taxonomy they direct) still ends up satisfied with a text that a truly
independent, motivated critic would have rejected. This is a structurally
narrower version of the same category of residual risk the custody note
named for post-selection protocol-tuning (§4 there): no technical fix
exists inside a solo-owner, no-third-party constraint, and the honest
position is to say so rather than to imply §3's mechanisms make the
approval "independent" in the sense Gate 1's own text originally meant.

**Compensating control, consistent with the custody note's own approach**:
the operator's explicit acceptance of this residual, recorded alongside
whichever `work/notes/` artifact eventually executes §3.2/§3.3 — not
assumed already covered by the general "solo owner" confirmation quoted in
§0, since that confirmation was about the constraint (no third party
exists), not a pre-judgment that a specific mechanism is acceptable. This
note recommends the operator be shown the concrete §3.2/§3.3 proposal
(taxonomy-first adversarial critique, published in full) and asked to
confirm it as sufficient before it is executed and treated as satisfying
Gate 1 — the same "authorize the specific mechanism, not just the general
constraint" discipline the custody note applied to its own beacon proposal.

## 5. Open question this note does not resolve: who runs the adversarial pass, and when

§3.2 needs a concrete assignment: which session (fresh clone/context,
explicitly instructed with the inverted-incentive framing before ever
seeing `GENERIC-CONTROL.md`) produces the taxonomy and the applied
critique, and whether the coordinator or the operator directly is the one
who dispatches it. This note proposes the *shape* of the exercise, not who
performs it or exactly when relative to Gate 1's other checks (source
pools, package hash) — that sequencing is a coordinator/operator call,
named here rather than assumed.

## 6. Scope boundary: what stays exactly as-is

- `GENERIC-CONTROL.md`'s candidate text, hash, and character/word counts —
  untouched by this note.
- `INDEPENDENT-CURATOR-START-PROMPT.md` Gate 1's wording — untouched; this
  note does not propose rewriting the gate text itself, only what
  satisfies it under a solo owner. (Contrast with the custody note, which
  did rewrite Gates 0–3's wording — this note explicitly does not do the
  equivalent for Gate 1, since §2 concludes the underlying mechanism, not
  just the custody-eligibility phrasing, needs to differ.)
- Gates 2/3 (public beacon selection) and Gates 4/5 (case
  construction/corpus review) — unaffected; this note is scoped to Gate 1
  only.
- The five normative owner documents, the anchor checker, and
  `PRE-AUTHORING-PACKAGE-MANIFEST.json`'s hash — untouched. No package hash
  changes as a result of this note (it proposes a *process* to run
  alongside the existing package, not an edit to any hashed input).
- No selection is run. No corpus/case file is created or touched.

## 7. Concrete follow-up-PR scope (not applied here)

A later pass, after this note is reviewed, would need to:

- Get the operator's explicit sign-off on the §3.2/§3.3 mechanism
  specifically (§4/§5), not just the general "no third party" constraint
  already on record.
- Dispatch a fresh, differently-instructed session to produce the
  weakness taxonomy *before* being shown `GENERIC-CONTROL.md`, then apply
  it adversarially and publish the full attempt as a new `work/notes/`
  artifact (e.g. `work/notes/<date>-armc-adversarial-critique.md`).
- Optionally strengthen §3.3 by identifying a specific, citable,
  non-MAPS-authored generic-agent-instruction exemplar from the literature
  and running the same structural diff against it, adding it to
  `REFERENCES.md` if used.
- Record the resulting disposition (`PRE-AUTHORING PACKAGE ACCEPTED FOR
  PUBLIC SELECTION` per Gate 1's existing text, or `PRE-AUTHORING
  CORRECTIONS REQUIRED` if the adversarial pass finds a real defect) as the
  actual Gate 1 Arm C approval — something that, per §1, has never yet
  happened for this candidate text.
- Get a fresh independent review of whichever artifact executes the above,
  mirroring this PR's established rigor (adversarial-question style
  re-verification, not a read-through) — this note's own proposal is not a
  substitute for someone else checking that the taxonomy and its
  application were done honestly, the same discipline
  `2026-09-15-pr341-custody-descope-design.md` §8 applied to its own
  cryptographic proposal.
