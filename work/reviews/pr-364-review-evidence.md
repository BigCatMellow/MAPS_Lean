reviewer: trajectory-check-fore
head_sha: 4dd22597568e75def140eedc05d87ba5a860be2d
independent: true
verdict: APPROVE
summary: Independent audit review of PR #364 (design-only note, "opcmd_merge.py evidence gate never wired into real merges", authored by rumi). Fresh clone (git remote set-url + own noreply identity), fetched refs/pull/364/head and separately the PR's real branch opcmd-merge-evidence-gate-hardening-2026-09-15 (same head 4dd2259), never touched ~/Projects/MAPS_Lean, no prior involvement authoring this note. All four requested checks independently verified against source, not the note's prose: (1) Three-gate claim -- read scripts/opcmd_merge.py (585 lines, matches claimed line count) and scripts/check_review_evidence.py (202 lines) in full. Every line citation in the note checked against the actual file and found exact: gate()'s standing-mode branch calls check_independent_review() at line 485 precisely as claimed; check_independent_review() spans 417-436 exactly as claimed and does raise GateError (via propagation to main()'s except GateError, exit 2, "MERGE REFUSED") on any failure -- a real hard gate, not advisory; _load_evidence_reviewer() spans 401-414 exactly; the reviewer==author string comparison is at 430-435 exactly. check_review_evidence.py's _reviewed_code_head() spans 82-112 exactly, _diff_is_empty() spans 115-134 exactly, check()'s head_sha comparison spans 163-181 exactly, and the "does NOT prove a distinct identity wrote the review" disclosure is verbatim at docstring lines 4-9 as cited. Ran both cited tests plus their full suites: `python3 -m unittest tests.test_opcmd_merge -v` 28/28 ok (including test_standing_authorization_refuses_when_reviewer_is_author and ..._when_evidence_check_fails by exact name); `python3 -m unittest discover -s tests -p "*review_evidence*" -v` 13/13 ok. Went beyond the note's own claim to independently confirm gate (c)'s real-world toothlessness: read four actual committed evidence files (pr-360/361/362/363-review-evidence.md) -- every `reviewer:` field is a free-text hcom agent name ("maps-work-zali", "rumi", "maps-review-bane", "maps-review-bane/rumi"), while `gh pr view --json author` for those same PRs returns GitHub login "BigCatMellow" for all of them -- confirms the note's §6 finding (reviewer field and author.login are structurally incompatible namespaces that can never collide) is not just theoretical, it matches every real evidence file in the repo today. (2) Empty-ledger claim -- `git log --all --full-history --oneline -- '**/merge-ledger.jsonl'` returns nothing; `find . -name merge-ledger.jsonl` (excluding .git) returns nothing; `git ls-tree -r origin/main --name-only \| grep merge-ledger` exit 1 (no match). Confirmed the file has never existed in this repo, in any branch, ever. `grep -rln opcmd_merge .github/` returns zero hits (exit 1) -- confirmed no CI workflow invokes the script; the two other repo-wide hits for "opcmd_merge" (check_direct_push.py:20, test_documentation_sprawl.py:36) are prose/comment references, not invocations. `gh pr list --state merged --limit 400` returns exactly 338, matching the note's count exactly. (3) Design-only claim -- `git diff --stat` against the merge-base with origin/main shows exactly one file changed, 259 insertions, 0 deletions: the note itself. scripts/opcmd_merge.py, CAPABILITY_CHECKLIST.md, and work/insights//work/ideas/ (the Emergence tracker) are all untouched -- confirmed by the diff stat directly, not the note's own claim. (4) Proposed-fix/check_direct_push.py claim -- read scripts/check_direct_push.py (156 lines) in full: find_violations() flags a commit iff it has exactly 1 parent (line 115) AND `_has_merged_pr` returns False (lines 117-118) -- matches the note's stated detection condition exactly. Verified the note's central technical claim directly: a `gh pr merge --squash` commit for a real, reviewed, CI-green PR (e.g. #359-362) has exactly 1 parent and IS associated with a merged PR via GitHub's commits/pulls API by construction (that's what "squash merge" means to GitHub), so `_has_merged_pr` returns True and the commit is skipped -- check_direct_push.py structurally cannot and does not claim to catch a PR that merged via the wrong tool, only a commit with zero PR at all. The note does not misdescribe this mechanism anywhere. Also independently re-verified the note's supporting evidence: docs/CHECKS_AND_BALANCES.md lines 91-93 quoted verbatim, confirmed exact byte match by reading those lines directly; `gh api repos/BigCatMellow/MAPS_Lean/branches/main/protection` live-checked -- enforce_admins.enabled=false, required_status_checks.contexts=["test","review-evidence"], strict=true, all matching; `gh api repos/BigCatMellow/MAPS_Lean --jq .permissions` confirms admin=true for the shared identity, matching. `python3 -m runtime.smoke` exit 0, ok:true. No fabrication, no line-citation error, no overclaim found anywhere in the note across all four requested checks plus the supporting evidence. Stop condition ("if any of the three gate claims don't hold up... REQUEST_CHANGES with the exact line") did not trigger -- every claim held up on independent re-derivation. APPROVE.
review_layer: DESIGN AUDIT REVIEW
verification: |
  Fresh clone of https://github.com/BigCatMellow/MAPS_Lean.git to a unique
  /tmp path (set-url to the GitHub remote, own noreply identity). Fetched
  both refs/pull/364/head and the PR's real branch
  opcmd-merge-evidence-gate-hardening-2026-09-15 -- both resolve to the
  same head 4dd2259, confirmed via `gh pr view 364 --json headRefOid`.

  Full read of all three cited source files (opcmd_merge.py 585 lines,
  check_review_evidence.py 202 lines, check_direct_push.py 156 lines) plus
  docs/CHECKS_AND_BALANCES.md's cited lines -- every one of the note's ~15
  specific line-range citations checked against the actual file content and
  found exact, not approximate. Ran both cited unit tests by exact name
  plus their full surrounding suites (28 + 13 tests, all green). Ran
  `python3 -m runtime.smoke` (exit 0). Independently confirmed the
  empty-ledger claim via three different methods (git log --all
  --full-history, find, git ls-tree) rather than trusting one. Went beyond
  the note's own evidence to check four real committed review-evidence
  files' `reviewer:` fields against their PRs' actual GitHub `author.login`,
  confirming the §6 namespace-mismatch finding against live repo data, not
  just the note's own reasoning. Confirmed via `git diff --stat` against
  origin/main's merge-base that this PR touches exactly one file (259
  insertions, the note itself) -- CAPABILITY_CHECKLIST.md,
  scripts/opcmd_merge.py, and work/insights//work/ideas/ all untouched.
limits: |
  Did not attempt to build or test the proposed §5 safeguard itself (out of
  scope -- design-only note, explicitly not building anything, per its own
  "Design-only" framing and this review's own output boundary: MUST NOT
  edit opcmd_merge.py). Did not independently re-verify the "gh pr review
  --approve fails for everyone this session, confirmed against PR #360"
  claim (a same-session transient CLI-behavior claim from the note's
  author) -- accepted as plausible background context since it restates a
  well-known, repo-independent GitHub platform constraint (no account can
  approve its own PR), not a claim this review's four requested checks
  needed to re-test. Did not re-litigate whether `enforce_admins` should be
  flipped -- the note itself correctly declines to recommend that, and this
  review agrees that's an operator-level call outside a design-only audit's
  authority.
