# Repair Record: review-evidence re-sync cycle triggers self-approval classifier friction and full-effort re-review churn

- Severity: `DRIFT`
- Owner: operator-directed session, 2026-08-18
- Trigger and evidence: PR #109 (`Surface Skill selection as attributed evidence in build_context_plan() (S6)`,
  merged 2026-08-18T23:45:54Z). Its actual commit history shows four separate
  `Add SENTINEL independent review evidence for PR #109` commits:
  `fe7e9b9` (22:36:53Z, initial evidence at head `f84ce2c`), `690bda9` (23:02:42Z, post-sync re-review at head
  `d5f6eb4`), `4fbd016` (23:23:40Z, post-sync re-review at head `e75a504`), and `5445513`
  (23:44:39Z, titled "Rebind PR #109 review evidence to the merge-updated head", post-sync re-review at head
  `70b52aa`) -- interleaved with three separate `Merge branch 'main' into agent/context-builder-skill-integration-s6`
  commits (`d5f6eb4`, `e75a504`, `70b52aa`). Each merge was a required branch-update sync
  (`gh api -X PUT .../pulls/109/update-branch`), needed because `main`'s required `test` check runs in strict
  mode and PR #109's branch kept falling behind as concurrent work landed on `main` faster than the
  review-evidence-then-merge cycle could complete.

## Finding

Two related but distinct pieces of friction surfaced across these four passes:

**1. Classifier flags on a known-legitimate pattern (the main finding, DRIFT).** Every review-evidence commit in
this repo's convention is authored under the same shared bot identity (`BigCatMellow` / `claude`) that also
authors the code commits -- that is the repo's sanctioned convention for how a dispatched fresh-clone,
zero-context reviewer records its findings, not a sign of self-certification. On two of the four re-review
passes here, the auto-mode classifier flagged the commit pattern (same identity, in-lineage with the code it
approves) as "self-approval" risk. The flag is not wrong about the raw signal it is reading -- same identity,
in-lineage -- but it cannot distinguish that from the case that actually happened each time: a fresh clone with
zero inherited context doing a full independent re-verification (diff read, full test suite, boundary check)
against the new head, exactly as `commit 4fbd016`'s message documents ("Independent re-review after branch
resync ... Confirmed the sync is a pure main-merge (zero diff on PR's own files vs prior head), re-verified all
S6 skill-integration claims directly against code and tests"). The underlying reviews were genuinely sound each
time; nothing here indicates a masked defect. What is real and recurring is the friction itself: this is the
third-or-fourth time in one PR's lifecycle that a correct, independent review got flagged as risky purely
because of identity reuse that is this repo's own established convention, not evidence of a shortcut.

**2. Full-effort re-review on zero-diff re-syncs (minor, folded in here rather than filed separately -- see
below for why).** Each of the three post-sync re-review passes re-ran the entire independent review from
scratch: full diff read, full test suite (626 then 629 tests, ~10-15 minutes each per the commit bodies), even
though the first two steps of each of those three passes -- confirm the sync merge brought zero changes to the
PR's own files, confirm nothing under the MUST-NOT-CHANGE boundary moved -- are checkable in seconds from `git
diff <old-head>..<new-head> -- <PR's changed files>` being empty. Only the *conclusion* (does the prior
verification still hold) needed re-attesting once zero-diff is confirmed, not the full review from a blank
slate. This is not a defect -- nothing wrong shipped -- just an efficiency observation.

Folded into one record because both stem from the same root cause (PR #109 racing a fast-moving `main` under
strict branch protection, forcing repeated review-evidence cycles) and the second is explicitly framed by the
task brief as "minor... roll into #2's Prevention... not a rule to implement here," i.e. an observation riding
on the same incident rather than a separate defect.

## Change or proposal

No code, classifier, or policy change is made in this record. Two things are explicitly **not** proposed,
per this session's own already-settled position: do not disable or loosen the self-approval classifier (it is
correctly reading a real signal in general; loosening it would create a real hole for the cases where identity
reuse *is* actual self-certification) and do not treat this as a defect to "fix" in the classifier's logic.

What is proposed, as a proposal only (not implemented here):

- **Primary**: a merge-queue / serialization convention for when multiple concurrent sessions are landing PRs
  against the same fast-moving `main` under strict-mode branch protection -- e.g. a lightweight "one PR merges
  at a time, others wait their turn / re-check before starting their own update-branch+review cycle" habit, so
  a PR does not need N independent review-evidence passes purely because it lost N races against unrelated
  concurrent merges. This addresses the actual structural cause (contention on `main`), not the classifier's
  reading of the resulting commit shape.
- **Secondary (folds in incident #3)**: per `playbook/MODEL_CAPABILITY_ROUTING.md`'s effort-level routing
  section (added 2026-08-18, PR #103), a zero-diff-confirmed re-review after a pure main-sync merge is a lower
  effort tier than a first-pass independent review -- worth naming as a distinct routing case (e.g. "re-review
  after confirmed zero-diff sync = low-effort/fast re-attestation, not full-effort review") rather than treating
  every re-review pass identically to a first pass. Not a rule to implement in this PR; an observation for
  whoever next revisits that routing section.

## Verification and rollback

- Verification: the four review-evidence commits and three merge-sync commits on PR #109 are directly visible
  in `gh pr view 109 --json commits` (see hashes above) and on the merged PR at
  `https://github.com/BigCatMellow/MAPS_Lean/pull/109`. No config or code changed, so no re-run is needed beyond
  re-reading that commit history.
- Rollback: none needed; documentation-only record with no applied change.

## Prevention

Neither proposal above is implemented here by design -- the merge-queue/serialization idea changes how
concurrent sessions coordinate landing PRs (process/authority-adjacent, warrants its own task + review rather
than being slipped in as part of a repair-record PR) and the effort-routing note is explicitly framed as an
observation, not a rule. If this pattern (classifier flag on a legitimate re-review, or repeated full-effort
re-review churn) recurs on a future PR, that is the trigger to convert one or both proposals into an actual
task doc rather than filing a third repair note for the same root cause.
