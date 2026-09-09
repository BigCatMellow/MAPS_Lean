# PR #319 — independent review evidence

reviewer: maps-lean-rev319-mosa
head_sha: 277370194218f0f20bc0bd81dfa8b7db76f9e872
independent: true
verdict: APPROVE
summary: |
  Independent review of PR #319 (emergence supersession authority — the Change-2
  split of former #302, rebuilt on current main after Change 1 landed as #315).
  No prior involvement with #302/#315/#316/#319 or authors vena/mezu/viva/nezu.

  MECHANICS / CONTAINMENT — all pass:
  - Boundary: `git diff --name-only origin/main...HEAD` = exactly
    playbook/EMERGENCE.md, playbook/INDEX.md,
    work/notes/2026-09-07-emergence-supersession-authority.md. Nothing else.
  - No Change-1 duplication / no leakage: the EMERGENCE.md diff layers only the
    Change-2 hunks on top of already-merged Change-1 content. The cross-root
    synthesis section appears as context (already on main), not re-added. All 8
    Change-2 hunks present and only those: top-of-doc "not a design ceiling"
    clause; "cadence open to improvement" para; Phase-1 "which established
    mechanism survives mainly because established" question; 2 synthesis asks +
    "current baseline" Capture-bar line + "Established process is a legitimate
    root of inquiry" para; "incumbency is insufficient" edit; Phase-2 "candidate
    may target an existing MAPS_L process"; Phase-3 "under the current operating
    model" + "Promotion may also authorize ... supersede"; closing Rule line.
    No unrelated edits.
  - INDEX.md: single-row edit to the EMERGENCE row only. Design note is a new
    file, 104 lines.

  AUTHORITY BOUNDARY — preserved:
  - Top-of-doc clause states "Current authority continues to govern execution
    until deliberately changed; being established is not evidence that a
    mechanism should remain." Emergence proposes; Promote (deliberate,
    unchanged, never automated) still decides.
  - INDEX row: "the decision/authorization for such a change stays with
    DECISIONS_AND_SAFETY.md / AGENTS.md, and drift-driven repair stays with
    REPAIR_AND_LEARNING.md." Present, not contradicted elsewhere in the diff.
  - Phase-3 "Promotion may also authorize work whose purpose is to replace or
    supersede an existing mechanism" is consistent with the existing model
    (Promote already turns a captured record into real work); it widens the
    work's purpose, not the actor. No execution/ratification authority added.

  INDEX 5-POINT CHECK (§"Adding or changing a method"): the design note works
  each point explicitly and coherently — (1) EMERGENCE already owns
  elicit/capture/route; DECISIONS_AND_SAFETY owns deciding, REPAIR_AND_LEARNING
  owns drift-driven repair, neither owns deliberate generative questioning of a
  working mechanism; (2) one job unchanged, candidate space widened; (3) links
  to AGENTS.md/DECISIONS_AND_SAFETY.md rather than restating decision procedure;
  (4) one INDEX row states the non-overlap; (5) nothing retired, closing Rule
  line superseded in place. Satisfactory.

  DESIGN NOTE QUALITY: real justification, not a stub — "what changes / what does
  NOT change / 5-point check / risk-reversibility". Names the lineage-preservation
  requirement ("Preserve lineage and the reason for replacement"). Adequate.

  AGENTS.md / DECISIONS_AND_SAFETY.md CONSISTENCY: no conflict. DECISIONS_AND_SAFETY
  "Human reauthorization boundary" (changing a standing rule / materially expanding
  scope / irreducibly subjective preference) still governs any consequential
  mechanism replacement; the note defers to it explicitly. AGENTS.md anti-sprawl
  invariant is the checklist the note answers. No hard rule about who may change
  canonical methods is contradicted.

  CI: `test` passes (1m20s, run 34288294423). `review-evidence` fails only
  because this file did not yet exist — expected, resolved by this commit.

  NON-BLOCKING NITS (for the fixer / coordinator, not gating):
  - The design note's "## Stacking" section is stale: it describes this PR as
    stacked on branch emergence/cross-root-synthesis-c1only / "#302 head" and
    says "Land Change 1 first, then rebase." Change 1 already merged as #315 and
    this branch is already rebuilt on main (25c7729). Same stale present-tense
    framing in the opening paragraph ("ships separately on branch ..."). The
    note will persist as lineage record; recommend correcting before merge.
  - Phase-3 softening "only a promoted item may expand implementation scope
    under the current operating model" reads as slightly self-referential
    (implies the scope rule itself is superseble). Self-consistent with the
    thesis and still requires Promote today; flagged for operator awareness.

  OPERATOR SUBSTANCE RULING STILL PENDING: whether emergence *should* hold the
  power to propose redesigning/superseding established mechanisms (incl. the
  emergence lifecycle itself) is the operator's call and is queued separately.
  This review does NOT opine on that. Verdict APPROVE = the split is clean, the
  change is contained to 3 doc files, the authority boundary is preserved in the
  wording, the INDEX justification satisfies the "changing a method" checklist,
  and CI (test) is green. Merge remains gated on the operator's substance ruling.

  REVALIDATION 2026-09-09 (zina, note-fix helper; zero-diff tier): mosa's APPROVE
  and dula's YELLOW stand. The only changes since 4ed6ae3 are (i) dula's
  minority-report-only commit 25af349 under work/reviews/ and (ii) commit 2773701,
  a stale-lineage-wording fix to the design note (opening paragraph + "## Stacking"
  section retitled "## Split history"). No reviewed substantive content changed:
  playbook/EMERGENCE.md, playbook/INDEX.md, and the note's What-changes /
  What-does-NOT-change / 5-point-check / Risk sections are byte-identical to the
  reviewed state. `git diff 4ed6ae3 2773701 -- work/notes/2026-09-07-emergence-supersession-authority.md`
  shows only the two wording hunks. The "## Stacking" staleness nit raised in this
  evidence file's NON-BLOCKING NITS is now resolved by 2773701.

  OPERATOR SUBSTANCE RULING: delivered 2026-09-09 via hore — APPROVED NARROW &
  CONDITIONAL (redesign wording stays proposal-only; merge gate = independent
  review + a Tenth Man pass concluding it is genuinely a good idea). dula's
  minority report (verdict YELLOW, work/reviews/pr-319-minority-report.md) is
  that pass: #319 merges as-claimed, no return to mosa, no 3rd reviewer.
