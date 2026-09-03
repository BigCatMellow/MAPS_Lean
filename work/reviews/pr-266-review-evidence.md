# PR #266 — review evidence (independent, verification-only)

reviewer: independent-review-agent (session 23 dispatch)
head_sha: b69f7cac611416e80132d37db34411b40fc11a0b
independent: true
summary: Verified the merge-authority doc rule + handoff-template block + AGENTS byte-budget bump against decision-batch item 2 and the sprawl invariant; doc + one test constant only, tests pass. APPROVE.

## Findings

1. Head SHA. `git checkout coordinator/merge-authority-rule-s23 && git rev-parse HEAD`
   == `b69f7cac611416e80132d37db34411b40fc11a0b` — matches the dispatched head.

2. Diff scope. `git diff origin/main...HEAD --stat` touches exactly 3 files:
   - `AGENTS.md` (+13 / -13 net +12 lines counted as 26 changed due to reflow)
   - `templates/handoff.md` (+6)
   - `tests/test_documentation_sprawl.py` (+4 / -1)
   No `runtime/` or `scripts/` changes. No runtime code. Confirmed doc + one
   test-constant only.

3. AGENTS.md rule text vs decision-batch item 2. The new `### Merge authority
   (operator-adopted 2026-09-02)` subsection has three bullets that map
   faithfully and non-expansively onto item 2's three parts:
   - "(b)" `gh pr merge` operator-only / designated coordinator  →  bullet 1
     ("`gh pr merge` is operator-only, or an explicitly designated coordinator
     seat.")
   - "(a)" longest-running peer lane owns merge-prep (rebase + evidence-bind +
     keep merge-ready/non-conflicting) but does NOT merge  →  bullet 2 ("No
     coordinator seat active → the longest-running peer lane keeps every
     APPROVED PR rebased, evidence-bound, and non-conflicting, but does not
     merge.")
   - "(c)" claim the rebase in-channel before force-pushing a shared branch  →
     bullet 3 (verbatim intent, quotes the "claiming the #N rebase" phrase from
     the item body).
   No new authority, machinery, or scope beyond the item. Faithful.

4. Handoff-template block. `templates/handoff.md` gains a "## Merge authority for
   this handoff" section: names the coordinator/merge seat, states the peer-lane
   fallback and that `gh pr merge` stays operator-only, and lists APPROVED PRs
   awaiting merge. Consistent with item 2's "into AGENTS.md + the session-handoff
   template" instruction. Non-expansive.

5. Paragraph reflow ("For important in-scope uncertainty..."). The escalation
   pipeline was converted from a fenced `text` block to inline prose and the
   trailing two sentences lightly reworded ("remains a separate narrow protocol"
   → "is a separate narrow protocol"). One substantive token dropped: the
   pipeline step "→ orchestration operator decides inside authority" became
   "→ operator decides inside authority" (the word "orchestration" removed).
   Assessment: formatting + wording change; the operative meaning (operator
   decides within their own authority; escalate to a human only for a true
   boundary crossing) is preserved. Minor, noted, not a blocker.

6. Byte-budget bump. `AGENTS_BYTE_BUDGET` 10_000 → 10_400 in
   `tests/test_documentation_sprawl.py`, with a 3-line explanatory comment
   citing PR #266 / decision batch item 2 and the anti-sprawl invariant's
   "a genuinely new global rule belongs in AGENTS.md itself" rationale.
   `wc -c AGENTS.md` at this head = 10289 bytes → 111 bytes (~1%) headroom.
   Minimal fit, not an oversized bump. Comment present as required.

7. Tests. `python3 -m pytest tests/test_documentation_sprawl.py -q` at this head
   → 22 passed.

## Disposition

APPROVE. All 6 dispatch verification points pass. The change is doc-only plus a
single minimally-sized, commented test constant; the new rule is a faithful,
non-expansive transcription of decision-batch item 2's three parts; the reflow
preserves meaning (one cosmetic token drop noted in finding 5); the budget bump
is the minimal value that fits and carries an explanatory comment; the sprawl
test suite passes at the reviewed head.
