# Design: hardening the merge-evidence gate for INSIGHT-2b8b9a4b

Dispatched by coordinator `venu` following the operator's decision (approach
#2) on closing `INSIGHT-2b8b9a4b` (the PR #345 self-merge gap trajectory
check #31 promoted): not enabling GitHub's `required_approving_review_count`
(would lock out the whole fleet, since every agent shares one GitHub login,
`BigCatMellow`, and `gh pr review --approve` already fails "can't approve
your own PR" for everyone this session — confirmed directly in this same
session against PR #360). Instead: audit whether the existing convention
(PR-comment verdict + committed `work/reviews/pr-N-review-evidence.md`) is
actually a mechanical gate, and if not, scope the fix.

Design-only. No `scripts/opcmd_merge.py` edits, no `CAPABILITY_CHECKLIST.md`
or Emergence-tracker changes, in this note.

## 1. The three requested checks, read from source, not from the docstrings

Read `scripts/opcmd_merge.py` (585 lines) in full and `scripts/check_review_evidence.py`
in full — not summarized, not inferred from either file's own docstring.

**(a) `work/reviews/pr-N-review-evidence.md` existing.** HARD-gated, when
this code path runs at all: `opcmd_merge.py::gate()`'s standing-mode branch
(`runtime` here means the script's own control flow, line 485) calls
`check_independent_review(pr, author, evidence_path)`
(`opcmd_merge.py:417-436`), which shells out to
`scripts/check_review_evidence.py <pr>` (`opcmd_merge.py:423-429`) and raises
`GateError` — refusing the merge — on any non-zero exit. `check_review_evidence.py::check()`
(`scripts/check_review_evidence.py:146-154`) returns `False` if the file is
missing. Real code, not a stub.

**(b) `head_sha` matching the PR's real code commit, walking back
evidence-only commits.** Also HARD-gated through the same call. Read
`_reviewed_code_head()` (`scripts/check_review_evidence.py:82-112`) directly:
it walks `HEAD` backward one commit at a time, stopping at any commit with
0 or 2+ parents (root/merge commits), and continues walking only while every
changed path in the current commit is under `work/reviews/` — i.e. it skips
past trailing evidence-only commits exactly as designed, and stops at the
first commit that touches anything else. `check()` (lines 163-181) compares
the evidence's claimed `head_sha` against this walked-back value, with an
`_diff_is_empty()` fallback (lines 115-134, 166-174) for a rebase-preserved
tree (used twice already this session for PR #361/#362's own rebases — see
this session's hcom log). This is real, correct, previously-exercised code,
not a docstring promise.

**(c) recorded `reviewer` field differing from the PR author.** HARD-gated
*in `opcmd_merge.py` itself*, not delegated —
`check_independent_review()` (`opcmd_merge.py:430-435`) loads the evidence
file's `reviewer:` field via `_load_evidence_reviewer()` (lines 401-414) and
raises `GateError` if
`reviewer.strip().lower() == (author or "").strip().lower()`. This exists
specifically because `check_review_evidence.py`'s own module docstring says
outright it "does NOT prove a distinct identity wrote the review — the same
GitHub account can commit the evidence file" (lines 4-9 of that file) —
`opcmd_merge.py` was written to add exactly the check its sibling disclaims.
All three gates are unit-tested in isolation:
`tests/test_opcmd_merge.py::test_standing_authorization_refuses_when_reviewer_is_author`,
`..._when_evidence_check_fails`, and the head_sha-mismatch path is exercised
via `check_review_evidence.py`'s own test suite.

**Conclusion on the code itself: all three gates are real, correct, and
tested.** The gap is not in this logic. It is everywhere this logic is
*not actually reached*.

## 2. The gap: `opcmd_merge.py` is not the real merge path today

`opcmd_merge.py`'s own module docstring says "Ships DORMANT: nothing in the
repo calls it" (line 25). Verified, not trusted at face value:

- `grep -rln opcmd_merge .github/` — zero hits. No workflow invokes it.
- `work/coordination/merge-ledger.jsonl` — **does not exist anywhere in the
  repo tree.** `append_ledger()` (`opcmd_merge.py:439-443`) is the only
  writer, called only on a real (non-dry-run) merge (`gate()` line 521,
  after the gate passes and before the actual `gh pr merge` call, line 524).
  Its total absence from the repo means **zero non-dry-run merges have ever
  gone through this script**, in this repo's entire history.
- Empirically, in this very session: PR #360 (`gh pr view 360 --json
  mergedBy` → `{"login": "BigCatMellow", ...}`) and #359/#361/#362 were
  merged by coordinator `venu` calling `gh pr merge <N> --squash
  --delete-branch` directly (visible in this session's own hcom event log) —
  the exact "bare `gh pr merge`" `AGENTS.md` line 160 explicitly forbids
  ("Every merge to `main` MUST go through `scripts/opcmd_merge.py`, never a
  bare `gh pr merge`"). This is not a hypothetical risk; it is what actually
  happened to the four PRs merged immediately before this audit was
  dispatched.
- Magnitude: `gh pr list --state merged` returns **338** merged PRs against
  a merge-ledger with **0** entries, ever.

So even though the in-script gates are correct, they currently provide
**zero actual protection**, because the script they live in is never
invoked by the real merge flow.

## 3. Why GitHub's own required-status-checks doesn't close this either

Branch protection on `main` (`gh api repos/.../branches/main/protection`)
does require `test` and `review-evidence` as status checks
(`required_status_checks.contexts: ["test", "review-evidence"]`,
`strict: true`) — in principle this would independently re-enforce (a)+(b)
for *any* merge path, including a bare `gh pr merge`, regardless of
`opcmd_merge.py`. But `enforce_admins.enabled` is `false`, and the fleet's
single shared GitHub identity (`BigCatMellow`) has `admin: true` on this
repo (`gh api repos/BigCatMellow/MAPS_Lean --jq .permissions` →
`{"admin": true, ...}`). GitHub's own semantics: when `enforce_admins` is
off, administrators are exempt from every branch-protection rule, required
status checks included. So the "test"/"review-evidence" requirement is
**not actually enforced against this fleet's own merges at all** — it is
advisory for the identity every agent in this fleet authenticates as.

**This is not a newly-discovered bug — it is a deliberately accepted,
already-documented tradeoff**, found in `docs/CHECKS_AND_BALANCES.md`
(lines 91-93): *"`enforce_admins=false` permits owner emergency bypass for
genuine recovery such as CI infrastructure failure. Routine work uses the
standard gate. Record any bypass so it is not mistaken for a normal
reviewed merge."* Flipping `enforce_admins` to `true` is therefore **not
recommended by this note** — it would override an operator-level decision
this note has no authority to revisit, per rule 9 (don't guess across a
material boundary). What this note *can* establish, from direct evidence:
the emergency-bypass path is currently being used as the **100% routine
default** (§2's 338-PR / 0-ledger-entry finding), not the exception
`CHECKS_AND_BALANCES.md` describes, and the "record any bypass" half of
that same sentence is not happening anywhere either — there is no bypass
log, ledger, or marker of any kind distinguishing a gated merge from an
ungated one. Both halves of the documented norm are currently unmet in
practice, independent of whether the `enforce_admins` setting itself should
change.

## 4. `check_direct_push.py` already solved an adjacent gap the same way — and named this exact root cause

`scripts/check_direct_push.py`'s own docstring (lines 1-11) already states,
independently of this audit: *"branch protection on this repo's plan can be
(and twice has been) bypassed by an admin identity, so this cannot be a
merge gate. It is instead a post-hoc, loud, best-effort alert."* That
script flags a `push` to `main` whose commit has zero associated *merged
PRs* (GitHub's `GET /repos/{owner}/{repo}/commits/{sha}/pulls` API) — it
catches a commit landing on `main` with **no PR at all**.

**It structurally cannot catch this note's finding.** A bare `gh pr merge
<N> --squash` on a real, reviewed, CI-green PR (exactly what happened to
#359-362) produces a squash commit that the associated-pulls API correctly
reports as belonging to PR `<N>` — `check_direct_push.py`'s detection
condition (`it has exactly one parent AND the associated-pulls API returns
zero merged PRs`) is false for every one of these merges, by design; they
are not "direct pushes," they are legitimate PR merges that simply skipped
the intended gate script. The two gaps (no-PR-at-all vs.
PR-merged-via-the-wrong-tool) are adjacent but disjoint, and only the first
has a safeguard today.

## 5. Recommended fix — extend the same established pattern, do not invent a new one

This project has already chosen, twice, the right shape of fix for
"branch protection can't stop an admin identity": a loud, post-hoc,
best-effort CI alert (`check_direct_push.py`, `scripts/check_handoff_receipts.py`'s
sibling safeguards, per `review-evidence.yml`'s own list of rule-20
mechanical safeguards). Per rule 20 (a failure that repeats gets a durable
countermeasure, not just another fix) — this is the second occurrence of
"branch protection is admin-bypassable" as a root cause, so a mechanical
safeguard is warranted, mirroring the first occurrence's own resolution
shape, not a fresh design.

**Proposed new safeguard** (not built in this note — design only):
a `push`-triggered check (same trigger shape as `check_direct_push.py`,
which already establishes this is the only trigger that can see a merge
after the fact) that, for every newly-merged-PR commit landing on `main`
(the case `check_direct_push.py` currently *skips* as "already PR-covered,
already gated by `review-evidence.yml`" — `check_direct_push.py` lines
26-28), additionally checks whether `work/coordination/merge-ledger.jsonl`
(once it starts being written at all, see below) contains a matching entry
for that PR number. No entry → loud red check, same shape as
`check_direct_push.py`'s existing alert, naming the PR number and the
`mergedBy` identity. This directly operationalizes
`CHECKS_AND_BALANCES.md`'s own "record any bypass so it is not mistaken for
a normal reviewed merge" sentence, which is not happening today.

**Precondition this fix depends on, named explicitly:** the ledger has
*never* been written to (§2), so this new check would fail on 100% of
history and (until adoption) 100% of new merges unless the fleet's merge
practice changes to actually invoke `opcmd_merge.py`. That adoption
question — whether to make `opcmd_merge.py` invocation itself easier/more
default (e.g. a thin `hcom`-aware wrapper, or updating the merge-seat's own
tooling/instructions) — is a separate, closely-related but distinct
question this note does not scope or decide; named here as the necessary
companion change, not attempted.

## 6. Disposition of INSIGHT-2b8b9a4b — evidence only, not a decision

Per this note's own dispatch instruction: **not flipping the insight's
promoted status here.** Supplying the evidence for the coordinator/operator
to decide:

- The PR #345 self-merge class of incident is **not** closed by
  `opcmd_merge.py` today, on two independent, compounding grounds: (1) the
  script is never actually invoked for real merges (§2), and (2) even when
  it is (in tests, or if adoption changes), its reviewer-vs-author identity
  check compares a free-text, self-reported `reviewer:` field (e.g.
  `"rumi"`, `"maps-review-bane"`) against the PR's GitHub `author.login`
  (always `"BigCatMellow"` for every PR in this fleet) — two values from
  structurally incompatible namespaces that can never collide by
  construction, so the check can never actually catch a same-GitHub-account
  self-review. This is the same limitation `check_review_evidence.py` and
  `review-evidence.yml` already both disclose in their own comments ("does
  NOT prove a distinct identity wrote the review") — `opcmd_merge.py`'s
  extra check narrows *which name* has to differ, not *which GitHub
  account* actually wrote it.
- This is therefore **not** "already substantially addressed via a
  different mechanism" (this note's §3 branch) — it is a real, open gap,
  matching this note's §2 branch: scope the fix. §5 above is that scoped
  fix (a post-hoc alert extending `check_direct_push.py`'s own established,
  already-precedented pattern), not a claim that the underlying identity
  problem itself is solvable within this fleet's shared-GitHub-account
  constraint — it is not; §5's fix makes *silent* bypass loud, it does not
  make bypass impossible, exactly the same honest limitation
  `check_direct_push.py` already states about its own mechanism.

## Operator-section

Named for visibility, not auto-escalated (nothing here crosses an N=3
bound — this is a first-occurrence-of-this-specific-finding note, and
`check_direct_push.py`'s root cause is genuinely adjacent, not identical):

- The emergency-bypass path (`enforce_admins=false`) that
  `CHECKS_AND_BALANCES.md` documents as being for "genuine recovery such as
  CI infrastructure failure" is, empirically, the path every one of this
  session's four merges (#359-362) actually took, with none of them
  recorded as a bypass per that same document's own stated norm. Whether
  that is an acceptable operating reality (the gate is simply not being
  used day-to-day) or a drift from intent worth correcting is a call this
  note does not make.
- §5's proposed safeguard requires `opcmd_merge.py` to actually start being
  invoked for the ledger check to have anything to compare against —
  without that adoption change, the new safeguard would just be a
  permanently-red check, which is worse than no check. Sequencing (adopt
  first, safeguard second, or build both together) is a coordinator/operator
  call.

## Resume prompt

You are auditing/implementing the follow-up to
`work/notes/2026-09-15-opcmd-merge-evidence-gate-hardening-design.md`. That
note found: `opcmd_merge.py`'s three gates (evidence exists, head_sha
matches via walk-back, reviewer≠author) are correctly implemented and
tested in isolation, but the script has **never** completed a real merge in
this repo's history (`work/coordination/merge-ledger.jsonl` does not exist;
338 merged PRs, 0 ledger entries) — every real merge, including PRs
#359-362 merged in the same session as this audit, went through a bare `gh
pr merge` instead, in violation of `AGENTS.md` line 160's own stated
convention. GitHub's required-status-checks don't independently close this
either, because `enforce_admins=false` (a deliberate, documented tradeoff
per `docs/CHECKS_AND_BALANCES.md` lines 91-93, not a bug — do not
recommend flipping it without new operator instruction) exempts the
fleet's single shared admin-privileged GitHub identity (`BigCatMellow`)
from those checks. The proposed fix (§5) is a `push`-triggered, best-effort
loud CI alert — mirroring `scripts/check_direct_push.py`'s own already-
precedented "can't be a gate, so make it loud" pattern — that flags any
newly-merged PR commit on `main` with no matching
`work/coordination/merge-ledger.jsonl` entry. Before building it: confirm
with the coordinator/operator whether `opcmd_merge.py` adoption (making it
the actual default merge path) is happening in parallel, since the
safeguard is meaningless against a permanently-empty ledger. Do not flip
`INSIGHT-2b8b9a4b`'s status yourself — that's the coordinator's/operator's
call given this evidence.
