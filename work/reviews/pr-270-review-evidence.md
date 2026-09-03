# PR #270 review evidence

reviewer: independent-review-agent (session 23, PR #270)
head_sha: 8b654f2e854e40aaa2f6dc9ec45578cd07269d22
independent: true
summary: APPROVE — diff is genuinely note-only (1 new file, +466, zero applied changes to AGENTS.md/playbook/templates/tests/FRICTION_LOG) and the design is sound. One load-bearing quantitative estimate (§5.1/§7.2 AGENTS.md byte delta) is understated by ~290 bytes and must be re-measured before slice-1 implementation; it does not block merging a design note.

## Method

- Fresh clone in scratchpad (`/tmp/tmp.WBFjskdYo5/MAPS_Lean`), branch `design/triage-core-standard`,
  `git rev-parse HEAD` = `8b654f2e854e40aaa2f6dc9ec45578cd07269d22` (matches expected). Main worktree untouched.
- `git diff 828d5e7...HEAD --name-status` and `--stat`.
- Spot-checked every factual claim in the note against the actual repo files listed in its "Source of truth".
- `python3 -m unittest tests.test_documentation_sprawl`.

## Findings

1. **Diff scope — PASS.** `git diff 828d5e7...HEAD --name-status` = exactly one line:
   `A work/notes/2026-09-03-triage-core-standard-design.md` (+466). No `AGENTS.md`,
   `playbook/*`, `templates/*`, `tests/*`, or `work/coordination/FRICTION_LOG.md` hunk.
   All proposals live inside the note. No applied change → not a REJECT on this axis.

2. **`test_documentation_sprawl` — PASS.** 22 tests OK on this branch. The note changes
   nothing executable, as claimed.

3. **FACTUAL ERROR (moderate) — `work/notes/2026-09-03-triage-core-standard-design.md:216`
   and `:373-380` (§5.1 / §7.2): the AGENTS.md byte-delta estimate is understated.**
   Note says the additions are "~430 bytes over budget" and "`AGENTS_BYTE_BUDGET` → 10800 …
   leaves ~80 bytes headroom after the change." Measured from the note's own proposed text:
   proposed invariant 13 block = 311 bytes, the "Work records and changes" capture sentence
   = 407 bytes, total ≈ 718 bytes (both are pure additions; the second is explicitly "add
   one sentence after the task-record paragraph"). Current `AGENTS.md` = 10289 bytes
   (`AGENTS_BYTE_BUDGET` = 10400, `tests/test_documentation_sprawl.py:31`). Post-change size
   ≈ 11007 bytes, so the proposed budget **10800 would fail**
   `test_always_read_entry_surfaces_have_explicit_size_budgets`. The note's fallback of
   11000 (§7.2) is also marginal (~11007). Recommendation to operator: at slice-1
   implementation, measure the final wording exactly and set the budget to ≈ 11150+, or
   trim the capture sentence. This estimate is the load-bearing input to operator
   decision §7.2 — flagging so §7.2 is decided on a correct number.

4. **MINOR — `…design.md:49-50` (§1.3): "eight consecutive … follow-up lines".**
   `work/coordination/FRICTION_LOG.md` entry "2026-08-31 — orchestrator tool-use burned
   ~30-40k context" has **6** follow-up lines (labeled "3rd" through "8th consecutive
   arc"), spanning trajectory checks #14–#19 (the "#14–#19" range in the note is correct).
   The 8th arc is reached, but there are 6 lines, not 8. Cosmetic; the argument ("open
   across many passes, should have closed at N=3") is unaffected. The rest of §1.3 is
   accurate: entry is still open with `verified: n/a (behavioral)`
   (`FRICTION_LOG.md:156`); the "2026-09-02 — agent edited the shared coordinator checkout"
   entry's rule-20 countermeasure is "proposed — pending operator adoption via #253 item 2"
   (`FRICTION_LOG.md:261`) and check #19 records "#253 item 2 **still** [unanswered]"
   (`FRICTION_LOG.md:276`) — verbatim match.

5. **Prior triage branches — NOT a conflict, small transparency gap.**
   `origin/agent/stalled-work-triage-protocol` and
   `origin/chore/friction-log-triage-loop-20260831` are **both already merged to `main`**
   (`84cc3f7 Friction-log triage loop … (#187)`; `work/coordination/README.md:95`
   "## Stalled-work triage"; `playbook/REPAIR_AND_LEARNING.md:54` §"Operator-friction and
   request capture"; `playbook/ROADMAP_TRAJECTORY_CHECK.md:48` §"Friction-log consumption
   (every pass)"; `templates/handoff.md:55` §"Before finalizing / self-clearing").
   The note builds directly on all four of these merged sections (cites each) and its
   proposal is strictly a *tightening* of that landed foundation — no contradiction, no
   duplication. Finding: the note never names PR #187 / those branches as the base it
   extends; citing it would make the "amendment not new owner" argument (§4) stronger.
   The two now-stale remote branches are housekeeping to prune, out of scope for this PR.

6. **Factual claims spot-checked TRUE:**
   - `playbook/` at 24/24: 25 `playbook/*.md` files − `INDEX.md` (excluded by
     `active_playbook_files()`) = 24; `PLAYBOOK_SURFACE_BUDGET = 24`
     (`tests/test_documentation_sprawl.py:27`).
   - `AGENTS_BYTE_BUDGET = 10_400` (`:31`); `AGENTS.md` = 10289 bytes.
   - `playbook/REPAIR_AND_LEARNING.md` owns: severity table Cosmetic/Drift/Blocking/
     Structural (`:6-13`), repair records, regression-case freezing via
     `runtime/evaluation/regression_case.py` (`:74-99`), the `FRICTION_LOG` capture
     pointer (`:54-72`), and "if a failure repeats add a durable countermeasure" in prose
     (`:46-48`). The note's ownership claim is accurate.
   - `playbook/ROADMAP_TRAJECTORY_CHECK.md:48` §"Friction-log consumption (every pass)" is
     a soft "close / verify / escalate" standing duty with no pass-count staleness bound —
     matches the note's §1.4 / §5.4 characterization.
   - `templates/task.md:118` "Completion / handoff" block has no triage-capture line;
     `templates/handoff.md:55` §"Before finalizing" points at `FRICTION_LOG.md` without
     naming §2 triggers or an Nth-occurrence clause. Both match the note.
   - `work/notes/2026-08-18-stalled-dispatched-worker-repair.md` and
     `work/notes/2026-08-18-dispatched-worker-stall-recurrence.md` both exist; the latter
     records the pattern recurring "three separate times in a row" with "an explicit
     prompt instruction … in place" on attempts 2 and 3 — the note's §1.2 wording is
     faithful (the source itself labels the count `REPORTED`, not `VERIFIED`).
   - Merge-authority budget-raise precedent is real (`tests/test_documentation_sprawl.py:28-30`
     "Raised 10_000 -> 10_400 for the operator-adopted merge-authority rule").
   - `AGENTS.md` has exactly 12 hard operating invariants, style `N. **Title.** prose`
     (`:55-76`); proposed invariant 13 (`…design.md:225`) matches that register and
     numbering. Note: the merge-authority rule itself lives in a `### Merge authority`
     subsection (`AGENTS.md:141`), not as a numbered invariant — so it is precedent for
     "new global rule + budget raise" but not precisely for "new numbered hard invariant".
     This does not undermine invariant 13, which the sprawl invariant ("new global rules
     belong here") independently supports.

7. **Internal soundness — SOUND.**
   - Fold-into-`REPAIR_AND_LEARNING.md` vs new `playbook/TRIAGE_STANDARD.md` (§4): valid
     against the anti-sprawl invariant. `playbook/` is at budget; all four candidate jobs
     (mandatory capture, recurrence ladder, live-verify close, enforcement wiring) are
     tightenings of a concept `REPAIR_AND_LEARNING.md` already owns, not a distinct
     reusable job. The rejected-alternative reasoning (`…design.md:203-208`) is honest
     about the strained non-overlap statement a new file would need.
   - "Advisory script, reject CI-blocking for now" (§5.5): JUSTIFIED, not hand-waved —
     concrete failure mode (CI-blocking unrelated PRs on an unrelated stale friction item
     → pressure to close/delete entries prematurely), cites
     `REPAIR_AND_LEARNING.md` §"Diagnostics do not grant repair authority" as the
     governing pattern, and applies rule 20 to the backstop itself (escalate to blocking
     only on evidence the advisory form is insufficient).

8. **§7 operator-decision completeness — adequate, one gap.** Seven decisions, each with a
   recommendation; the four choices the note "recommends" (fold vs new file, N=3,
   advisory vs CI, which doc owns the dispatch clause) are all surfaced in §7 rather than
   silently decided. Gap: the §2 mandatory-capture trigger taxonomy and the
   "NOT in scope" list are presented as settled policy, as is the "capture before the fix
   PR opens" timing rule — these are substantive and arguably operator calls. Low-stakes
   (the entire note is an operator-reviewed proposal), but §7 could add a line asking the
   operator to ratify the §2 trigger list. Not blocking.

9. **Proportionality (invariant 7) — self-guarded.** §8 carries an explicit
   "Proportionality check (invariant 7)" paragraph and a kill-criterion: "If slice 1
   turns out to add friction without catching anything over ~5 arcs, that is itself a §2
   signal and the standard should be trimmed." Adequate acknowledgement and guard.

## Disposition

**APPROVE.** This is a design-note-only PR: the diff is exactly one new file with zero
applied changes to `AGENTS.md`, `playbook/`, `templates/`, `tests/`, or `FRICTION_LOG.md`,
so it cannot be a REJECT on the "proposals must be in the note, not applied" axis. The
design is internally sound, the "fold, don't add a playbook" call is correct against the
anti-sprawl invariant, the CI-vs-advisory reasoning is justified, and the note self-guards
proportionality. Factual claims about the current system are accurate except:

- **Finding 3 (must fix before slice 1):** the §5.1/§7.2 AGENTS.md byte-delta estimate
  (~430 bytes / budget 10800) is ~290 bytes low — the real additions measure ~718 bytes,
  putting the file at ~11007 bytes, which the proposed 10800 budget would fail. Re-measure
  and set the budget from the final wording (≈ 11150+) at implementation time.
- **Finding 4 (cosmetic):** "eight consecutive follow-up lines" is 6 lines reaching an
  8th arc.
- **Finding 5:** prior triage work (PR #187) is already merged and is the foundation this
  note extends, not a conflict; the note should cite it.

None of these block merging the design note. They are inputs the operator needs when
answering §7 and when the slice-1 implementation PR is written (which itself needs
independent review, per the note's own resume prompt).
