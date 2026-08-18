# Independent-review enforcement on `main` — design note

Date: 2026-08-17
Owner: `agent/independent-review-enforcement-design`
Status: planning evidence only

## Why this lane exists

Issue #61's mechanical controls (PR-only, required Runtime CI, no force-push/delete) are implemented and merged. Its own acceptance criteria include a fifth item this session deliberately did not attempt:

> independent-review enforcement strategy is documented honestly, including the current same-GitHub-identity limitation ... if a custom review check is used, it binds exact base/head and does not trust stale review text or a mutable PR description.

The issue explicitly forbids the shortcut: "Do **not** solve this by pretending same-identity COMMENT reviews are independent approvals." This note is the design-only step that AGENTS.md rule 5 ("do not confuse capability with permission") and this session's own working convention (design before implementation on authority questions) both require before any implementation task touches this.

## Ground truth: what independence enforcement already exists (verified by direct read)

Two *separate* mechanisms currently claim to prevent self-review, and they do not talk to each other:

**1. Internal MAPS task-truth DB (`runtime/state/review.py`, `runtime/state/integrity.py`).** `claim_review()` mechanically forbids a reviewer from claiming a task whose submission author is in their own *continuity component* — a graph of `continuity_links(predecessor_id, replacement_id)` built by `record_continuity_link()`, walked transitively by `_continuity_component_conn()`. This is real, tested (`tests/test_execution_integrity.py`), and enforced at the SQL-transaction level (`SELF_REVIEW_FORBIDDEN` / `CONTINUITY_REVIEW_FORBIDDEN`). But it operates entirely on the **local SQLite task DB** (`.maps/state/*.db`), which is per-machine runtime state, not committed to git, and not visible to a GitHub Actions runner or to GitHub's branch-protection API at all.

**2. GitHub PR review evidence (`work/coordination/agents/SENTINEL.md`).** SENTINEL posts a `MAPS REVIEW CLAIM — SENTINEL-<label>` comment, then findings, on the PR. This is GitHub-visible but is **plain comment text**: nothing binds it mechanically to the exact head SHA at review time, nothing prevents the same GitHub identity from posting it, and nothing stops it from surviving a later force-push unreviewed (the exact class of bug this session already found and fixed in `coordination_housekeeping.py`'s handoff-evidence matching — see PR #84). GitHub itself additionally rejects a same-identity formal `APPROVE`/`REQUEST_CHANGES` review, which is why SENTINEL reviews are COMMENT-only in the first place.

**Conclusion**: MAPS already has a mechanically real, tested anti-self-review graph. It is just invisible to GitHub. The gap issue #61 flags is not "MAPS has no concept of reviewer independence" — it does — it's "GitHub's merge gate cannot see that concept," and the thing that *is* GitHub-visible (COMMENT text) is not mechanically bound to anything.

## Area 1 — What GitHub actually offers here

Confirmed by direct API/product-behavior knowledge, not assumed:

- **Native required-approving-review rules** need a formal `APPROVE` review from an identity distinct from the PR author (or a CODEOWNERS-based reviewer). GitHub blocks a PR author from approving their own PR; it does not block a *different* human/bot account from approving.
- **A required custom status check** can be produced by any CI job (including one this repo controls) and set to whatever pass/fail logic that job computes, bound to the exact commit SHA it ran against (this is exactly how the current `test` required check works).
- Neither option is blocked by tooling; both are blocked only by **identity**: MAPS currently has exactly one GitHub-authenticated identity (`BigCatMellow`), which is simultaneously the repo owner, the sole PR author, and the only account available to review.

## Area 2 — Candidate designs

**Option A — Second GitHub identity/App reviews formally.** Create a genuinely distinct GitHub identity (a second personal account acting as reviewer, a machine/bot account, or a GitHub App installed with review permission) that submits real `APPROVE`/`REQUEST_CHANGES` reviews. This is the only option that satisfies GitHub's *native* required-approving-review rule, and the only option that produces cryptographic-identity-level independence (a different account's OAuth/App credential actually posted the approval). It requires operator action outside this repo: creating/maintaining the second identity, and deciding who or what actually operates it (a second Claude session under separate credentials? a human? a scripted policy bot with narrow, auditable approval logic?). This note does not assume an answer.

**Option B — Custom required status check reads committed review-evidence, bound to exact head SHA.** Add a required check (e.g. `review-evidence`) that fails unless the exact PR head commit contains a review-evidence file (e.g. `work/reviews/pr-<N>.md`, committed *as part of the PR's own tree*, not a mutable GitHub comment) with a structured, machine-parseable record: reviewer identity, the exact head SHA it was written against (verified by the check against `git rev-parse HEAD`, so a stale file left over from a prior head fails automatically — no timestamp race like the comment-based approach), and an explicit independence statement. This directly generalizes the pattern this repo already used informally for PR #16 (`work/reviews/RUNTIME_INTEGRATION_REVIEW.md`), and reuses the *shape* of the exact-head-binding fix already proven this session in `coordination_housekeeping.py`. It is strictly stronger than the status quo (nothing is enforced today) but, used alone, does **not** prove a distinct identity wrote the file — the same GitHub account could commit it. It only proves *some* review-shaped artifact exists and is bound to the exact head, not that it is independent.

**Option C — Option B, strengthened by requiring the evidence file's authoring commit to have a different committer identity than the feature commits.** If Option A's second identity exists (even a lightweight one — a second git committer email/GitHub account used only for posting review-evidence commits), a custom check can mechanically verify `git log` shows the review-evidence commit was authored/committed by that distinct identity, not the PR-author identity. This combines A and B rather than choosing between them: B alone can't prove independence; A alone (without B) still requires trusting whoever operates the second identity actually did independent work, no different from a COMMENT review today. C is what actually closes the gap issue #61 describes, but it requires Option A's operator decision as a prerequisite.

**Option D — Status quo, documented honestly, indefinitely.** Keep exactly what merged this session (PR-only + required CI + no force-push/delete), and permanently document that independent-review enforcement beyond CI is **not** mechanically achieved — SENTINEL COMMENT reviews remain advisory evidence, not enforcement. This is not a failure state; it is a legitimate, honest choice if the operator judges that a second identity's operational cost (maintenance, credential management, deciding who/what operates it) isn't worth it for a single-operator project at this stage.

None of A/B/C/D is chosen by this note.

## Area 3 — Why Option B (or C) reuses, not duplicates, existing MAPS infrastructure

Roadmap law 4.7 ("derived views stay derived") and rule 6 ("do not create duplicate truth") both caution against inventing a second review-tracking system. Two ways to honor that if B or C is approved:

1. **Minimal**: the review-evidence file is genuinely new (a committed artifact), but its *content requirements* (reviewer identity, independence claim, exact-head binding) mirror the internal `runtime/state/review.py` model closely enough that a future task could make the file a rendered export of an actual internal-DB review record, rather than freehand text — closing the gap between mechanism 1 and mechanism 2 from the Ground Truth section instead of leaving them permanently parallel.
2. This note does **not** propose exporting the local SQLite DB to CI (a bigger, riskier change — it would need the DB or a signed export shipped somewhere a GitHub Actions runner can read, which is its own security question about what a CI runner should be able to see/trust from local operator state). That question is flagged below, not answered.

## Decision authority

### Owner (this task) may decide
- That MAPS already has two independence mechanisms that don't currently talk to each other (Ground Truth), and that this is the actual shape of the gap, not "MAPS has no independence concept at all."
- That GitHub's native required-review rule and a custom required status check are both technically available; the blocker is identity, not tooling (Area 1).
- That a comment-text-only review (the current SENTINEL practice) cannot be mechanically bound to an exact head the way a committed file can, mirroring the exact defect class already found and fixed in `coordination_housekeeping.py` this session.
- That no runtime/schema file or GitHub branch-protection setting is touched by this task.

### Requires an explicit operator decision (not resolved by this task)
1. **Option A vs. B vs. C vs. D (Area 2)** — is a second GitHub identity/App worth creating and operating for this project, and if so, who or what operates it (second human, second scripted/agent session under separate credentials, narrow bot with fixed approval logic)? This is an operational/cost/access decision outside what any task owner may assume.
2. **If B or C: what "review-evidence" must contain and who/what may write it** — e.g. must every merge to `main` carry one, or only ones above a risk threshold; can a task owner write their own file (weak) or must it come from a distinct reviewing identity (Option C); does the check verify only presence/shape, or something stronger.
3. **If A or C: how the second identity is credentialed and audited** — this is a real operational-security question (a bot with merge/approve rights is itself a privilege-escalation surface if compromised or misconfigured) that needs its own explicit scoping, not silent inheritance from "we already trust the primary identity."
4. **If D: for how long, and what would trigger revisiting it** — e.g. "revisit once a second contributor/agent identity exists for other reasons anyway," or "not revisited unless a concrete incident like #55/#58 recurs."

None of these four are resolved in this note.

## Continuation

```text
this design (Stage 0)
        ↓
operator decision 1 (and 2-4 as applicable)
        ↓
IF Option A or C chosen:
    Stage 1 — operator provisions the second identity/App (outside any
    task's authority to do unilaterally)
        ↓
IF Option B or C chosen:
    Stage 1' — implementation task: add the review-evidence file format +
    required status check that verifies exact-head binding (FOUNDRY,
    independently re-verified per this session's SENTINEL pattern, since
    it is automation acting on the live repo's merge gate)
        ↓
IF Option C: Stage 2 — required check additionally verifies committer
    identity distinctness on the evidence commit
ELSE IF Option D:
    stop here; document the limitation permanently in AGENTS.md /
    work/coordination/README.md rather than leaving it only in this note
```

Until an operator decision lands, independent-review enforcement beyond required CI is correctly **BLOCKED_ON_OPERATOR_DECISION** — issue #61 stays open, re-scoped to exactly this.

## Operator decision (recorded 2026-08-18)

Operator deferred entirely to task-owner judgment ("whatever you think is best, just do it"). **Option B chosen**: no second identity — operational cost/credentialing (questions 1/3 above) not worth it without a concrete driving need. Implemented: `scripts/check_review_evidence.py` + `.github/workflows/review-evidence.yml`, required status check `review-evidence`, verifying `work/reviews/pr-<N>-review-evidence.md` exists on the exact PR head with `reviewer`/`head_sha`/`independent: true`/`summary` fields (template: `templates/review-evidence.md`). Does not prove reviewer identity distinctness — documented as such in the script's own docstring. Question 4 (D's revisit trigger) is moot since D wasn't chosen. Option A/C (second identity) remains available as a future upgrade if a concrete need arises.
