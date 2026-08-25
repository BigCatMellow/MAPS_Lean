reviewer: agent-a182f8acc9f220bde (independent reviewer, did not author this PR)
head_sha: fba8c4ff3113848ca1cbd765b0616896c466105d
independent: true
summary: APPROVED — PR #169 is a docs-only convention (three files, 612+ lines added, nothing under `runtime/`, `tests/`, or any roadmap/checklist file, verified by diff not by the note's own claim), and the two safety-relevant claims it makes about `scripts/check_review_evidence.py` are both true as read in the script: the checker resolves the literal path `work/reviews/pr-<N>-review-evidence.md` (line 97) and parses only that one file, so a sibling `pr-<N>-minority-report.md` can neither be mistaken for it nor inject a duplicate `head_sha`/`reviewer` line into the flat line-scan parser; and `_reviewed_code_head` walks back past any single-parent commit whose every changed path starts with `work/reviews/` (line 81), so a minority-report-only commit does not disturb the reviewed-code binding. Every non-goal is respected and every quoted source-document reference checks out verbatim (§24 "No Fake Dissent", §25 "The Tenth Seat Is Not a Professional Contrarian", Law 6, Law 7, Triggers C/D, §§10/15/18/28, and the literal "Fictional protocol inspired by real historical and institutional ideas." status line), as does master-roadmap §7.3's rejection of a fixed permanent agent roster, quoted word for word. Four non-blocking findings: the trajectory-check calibration cites pass #4 as having found a real defect when it found none (both cited defects are in pass #6 alone); the freshly-corrected "at most about eight" bound is not an upper bound because `nit` and `gap` are unanchored substrings that match `init`/`unittest`/`unit`/`Monitor`/`definition`/`sanity`, and a word-boundary rerun of the author's own grep returns 23, not 8; the Trigger 1 conjunction measured semantically rather than by literal string fires three times historically (#105, #111, #134) rather than once, which still leaves the "once per few dozen PRs" order of magnitude intact; and the §7 "signs this has gone wrong" list — the design's main answer to the source protocol's own §24 — has no assigned reader, after §6.3 dropped the source's §28 scoring as noise. None of the four changes the merge decision.

# Review: PR #169 — Tenth-Seat adversarial review convention

- Reviewer: `agent-a182f8acc9f220bde`, freshly dispatched, no authorship of this PR.
- Branch: `tenth-seat-protocol-design`. Base: `origin/main` @ `8923adb`.
- Reviewed code head: `fba8c4ff3113848ca1cbd765b0616896c466105d`.
- Verdict: `APPROVED`. Four non-blocking findings (N1-N4). No blocking finding.
- Worktree: reviewed in an isolated worktree at
  `/home/home/Projects/MAPS_Lean/.claude/worktrees/agent-a182f8acc9f220bde`;
  the shared clone was never touched.

## 0. Head movement during review

Review began at `151f0d3`. Mid-review the author pushed
`fba8c4ff3113848ca1cbd765b0616896c466105d`, which by that point had
independently self-caught part of what became finding N2 below: the original
text asserted "of 82 review-evidence files, exactly two record 'No findings'",
which was wrong in its denominator (82 is the count of *all* files in
`work/reviews/`; only 69 are `pr-*-review-evidence.md`, the other 13 being
`TASK-*` reports and `RUNTIME_INTEGRATION_REVIEW.md`). The new text says "82
files in `work/reviews/`", which is correct.

I re-fetched, reset to the new head, and re-ran every count from scratch rather
than accepting the corrected numbers. `git diff 151f0d3..HEAD` is two docs files
(`work/notes/2026-08-25-tenth-seat-protocol-design.md`,
`playbook/TENTH_SEAT_REVIEW.md`), 28 insertions / 9 deletions, no third file
introduced. All findings below are stated against `fba8c4f`.

## 1. Scope and non-goals (mandate item 3) — verified clean

`git diff --name-only origin/main..fba8c4f` returns exactly three paths:

```text
playbook/INDEX.md
playbook/TENTH_SEAT_REVIEW.md
work/notes/2026-08-25-tenth-seat-protocol-design.md
```

`--stat` confirms 612 insertions, 0 deletions across them. Nothing under
`runtime/`, nothing under `tests/`, nothing under `work/roadmaps/`, no
`.github/` workflow, no `scripts/` change. The `playbook/INDEX.md` delta is a
single added table row, read in full: it points at the new doc and its "not
this" column correctly disclaims both ordinary independent review and any veto
or second status-truth reading.

Against the master roadmap non-goals, read at their source rather than as the
PR quotes them — §7.1 "Large persistent `mapd` supervisor daemon — Rejected by default",
§7.3 "Fixed permanent agent roster — Rejected. Workers/capabilities should be
selected for work, not turned into a bureaucracy of named personalities", §7.9
"Continuous discovery/process-police agents — Rejected by default. Prefer
bounded audits and deterministic checks." The PR's §7.3 quotation is verbatim.
The design takes no roadmap capability number, adds no daemon or scheduler, and
adds no CI gate; the rotating-occupant rule keeps it clear of §7.3 in substance
and not merely in wording.

I specifically looked for a counter-example to §6.2's argument that playbook
conventions do not take roadmap numbers, since PR #122's title formalized
worktree isolation "as a playbook convention (E6/6.16)". It does not survive:
`CAPABILITY_CHECKLIST.md` rows E6 and 6.16 are backed by real runtime code
(`runtime/state/schema.sql`, `runtime/integrity/git_scope.py`,
`runtime/run_record.py`, and others) with a stated exit gate. E6 is a numbered
capability that a playbook doc contributed to, not a numbered playbook doc. So
§6.2's argument holds, and its supporting reason — that numbering this would
manufacture exactly the status row Trigger 1 exists to be suspicious of — is
sound rather than merely rhetorical.

## 2. `check_review_evidence.py` compatibility (mandate item 4) — both claims TRUE

I read the whole script (145 lines) rather than its docstring.

**Claim (a) — exact path resolution.** Line 97:
`evidence_path = repo_root / "work" / "reviews" / f"pr-{pr_number}-review-evidence.md"`.
There is no glob, no directory walk, no `iterdir`. `_parse_evidence` is called
once, at line 101, on that single file's text. A file named
`work/reviews/pr-169-minority-report.md` is therefore never opened, never
parsed, and cannot contribute a line to the flat scan in `_parse_evidence`
(which iterates `text.splitlines()` of that one file and lets the last match of
a key win). The recorded duplicate-key incident this claim is defending against
is genuinely out of reach for a differently-named sibling file. TRUE.

**Claim (b) — walk-back tolerance.** Line 81:
`if changed and all(path.startswith("work/reviews/") for path in changed)`.
The loop at 62-84 requires exactly one parent (line 71 returns early on a merge
or root commit), diffs parent-to-current by name, and continues walking when
every changed path is under `work/reviews/`. A commit adding only
`work/reviews/pr-<N>-minority-report.md` satisfies that predicate exactly as
one adding only the review-evidence file does, so it is skipped and the
resolved reviewed-code SHA is unchanged. TRUE.

One property worth stating explicitly since the playbook relies on it: the
guard is `all(...)`, so a minority-report commit that also touched anything
else would *not* be skipped and would break the binding — which is the correct
fail-closed direction, and the playbook's instruction to commit the report as
its own artifact under `work/reviews/` is consistent with it. The minority
report template's own `head_sha:` / `independent:` / `summary:` keys are inert
under the current script; they would only matter to some future checker that
globbed `work/reviews/*.md`, which none does today. Not a finding.

Because both claims hold, the proposed artifact convention is safe. This was
the only place a blocking finding could have come from.

## 3. Attribution honesty and source fidelity — verified

I read `/home/home/Documents/The_Tenth_Seat_Protocol.md` (1058 lines) and
checked every structural citation the PR makes:

- Line 4 of the source: `> **Status:** Fictional protocol inspired by real historical and institutional ideas.` — quoted exactly, in both the note (§1) and the playbook doc (attribution section), not paraphrased or softened.
- Line 1052: `## Historical Accuracy Note` — exists; the PR's summary of it (not authentic Jewish legal procedure, not official Israeli intelligence doctrine) matches.
- `# 24. The Most Important Rule: No Fake Dissent` (line 682) — section number correct.
- `# 25. The Tenth Seat Is Not a Professional Contrarian` (line 703) — correct.
- `## Law 6 — Dissent Does Not Create an Automatic Veto` (line 248) and `## Law 7 — The Minority Report Survives the Decision` (line 260) — both correct, and the PR's use of them (no veto; report preserved regardless of verdict) matches their titles and content.
- `### Trigger C — High Consequence` (line 280) and `### Trigger D — Extreme Confidence` (line 292) — correct, and the PR's reframing of each is labelled as a reframing.
- Sections dropped in §6.3: `# 10. Before Discussion: Independent Judgment` (319), `# 15. The Evidence Matrix` (474), `# 18. The Second Vote` (523), `# 28. Scoring the Protocol` (755) — all exist at the numbers cited.
- Laws 3, 4, 5 and 12 referenced in §2.1 — Laws 3/4/5 are at lines 216/226/238 with the titles the PR implies.

Both documents label the source as fictional on their face and route it through
`AGENT_GRADE_INSTRUCTIONS.md`'s epistemic labels (precedents REPORTED, protocol
explicitly fictional, adopted as design input not authority). I found no place
where institutional weight the source disclaims is quietly borrowed. This is
handled better than the average adaptation of an outside framework here.

The note and the playbook doc are internally consistent with each other: same
two triggers, same conjunction logic, same rejected-trigger list, same verdict
ladder with BLACK dropped for the same stated reason, same non-goals. The one
place they differ is depth, not substance — the note carries the justification
and the playbook carries the procedure, which is the split the project already
uses for `ROADMAP_TRAJECTORY_CHECK.md`.

## 4. Findings

### N1 (non-blocking, factual, load-bearing) — trajectory pass #4 found no defect

Both documents state that trajectory passes #4 and #6 each caught a real issue.
The playbook is specific: "Passes #4 and #6 both caught real defects (a
note-numbering collision; a wrong roadmap tag)." The design note §2.3 makes the
same attribution.

I read `work/notes/2026-08-20-roadmap-trajectory-check-4.md` in full. It is 39
lines, three sections, and records no defect: §1 is re-verification against
`main` @ `886090b`, §2 is "what changed the picture", §3 is
"Decision: continue, no pivot". Its only mention of a correction (line 11) is a
back-reference to an example-target wording fix made on 2026-08-21 by other
work — not something pass #4 found. The word "finding" does not appear.

Both of the cited defects are in pass **#6**, not split across #4 and #6:
`work/notes/2026-08-24-roadmap-trajectory-check-6.md` line 5 records the
note-numbering collision ("renumbered from a stale '#4' during review") and
line 189 records the roadmap-tag correction ("the master roadmap, not `P1` —
corrected from this note's first draft").

For completeness I also read pass #5, which likewise records no defect (§3
"Decision: continue, select D2a"), and confirmed pass #7's cited claim is
accurate — lines 47-58 of check-7 do independently re-grep
`RecoverySupervisor(` and `\.tick(` across `runtime/` and confirm zero
production callers, referencing the insight file afterward.

Why this matters rather than being a typo: Trigger 2 fires only when a clean
pass follows **two** passes that each found something, so the calibration story
is the trigger. The corrected record actually leaves the design in a *better*
position than the text claims — #6 and #7 are consecutive passes that both
found real issues, which means the tripwire is genuinely armed right now for
pass #8, whereas the claimed #4/#6 pair is not consecutive and would not arm
anything. Non-blocking because the conclusion survives, but the sentence should
say #6 and #7.

Suggested fix: in `playbook/TENTH_SEAT_REVIEW.md` §Trigger 2 and note §2.3/§3,
replace the #4/#6 attribution with #6 and #7, and note that passes #4 and #5
were clean re-verifications — which is itself useful context for how often the
"nothing found" state occurs.

### N2 (non-blocking, measurement method) — "at most about eight" is not an upper bound

The new text offers a grep so the reader can check rather than trust:
files containing none of
`finding|gap|nit|caveat|concern|recommend|non-blocking|limitation|however`,
reported as 8 (6 PR files, 2 `TASK-*`). I reproduced that exactly —
`grep -LiE` over `work/reviews/*.md` returns those 8 files
(`pr-103`, `pr-148`, `pr-150`, `pr-151`, `pr-152`, `pr-153`,
`TASK-005-independent-review.md`, `TASK-007-independent-review.md`), and the
literal `No findings` grep returns exactly `pr-134` and `pr-135`. The numbers
as stated are honest.

The problem is the word "upper bound". `nit` and `gap` are unanchored
substrings. `grep -oiE "[a-z]*nit[a-z]*"` over the excluded files shows the
matches are `init`, `unittest`, `unit`, `Monitor`, `definition`, `sanity` — not
the word "nit" at all. `pr-117-review-evidence.md` is excluded from the 8 by
exactly two hits, `init` and `unit`, despite its summary reading "No bugs found,
no scope creep beyond the stated wording fix, no stale/inaccurate claim
discovered. Verdict: CLEAN, no changes required" — a textbook instance of the
condition being measured. `pr-112` is excluded by ten `nit` hits and no other
cue at all.

Re-running the author's own grep with word boundaries on those two terms
(`finding|\bgap|\bnit\b|caveat|concern|recommend|non-blocking|limitation|however`)
returns **23** files, not 8. So the stated "2-10%" band for condition (a) should
be roughly **2-28%**.

This does not damage the argument — a wider condition (a) makes the note's own
conclusion (that condition (b) carries the load, and that detection must stay a
reading task rather than a grep) *more* strongly supported, not less. But the
number was explicitly offered as checkable, and it does not survive checking.
The fix is one character class and one word: anchor `\bnit\b` and `\bgap`, and
call 23 a loose upper bound rather than 8.

### N3 (non-blocking, and it cuts toward the design) — the conjunction fired three times, not once

Both documents say exactly one historical PR satisfies the conjunction (#134).
That is true only of the literal-string reading. Measured semantically, using
this project's actual house style for a clean approval — the recurring
`APPROVE (CLEAN)` / `No bugs found` / `No findings` forms, 26 of the 69
`pr-*-review-evidence.md` files — and intersecting with PRs whose merge commit
adds a `DONE` line under `work/roadmaps/`, the conjunction holds for three:

- **#105** — `39fa0ec`, added `work/roadmaps/CAPABILITY_CHECKLIST.md` with 35 `DONE` lines in one commit.
- **#111** — `f6a4e57`, flipped `S1 — Information classification` to `DONE`.
- **#134** — `46d3c5d`, flipped portable-deployment D0 to `DONE` (the one the PR names).

Three out of the 69 PR evidence files is roughly one per 23 PRs, which lands
squarely inside the note's own "roughly once per few dozen PRs" and inside its
"right order of magnitude for a step this heavy" judgment. So the conclusion is
right and the supporting count is understated by 3x. #105 is the one worth
naming — a single zero-finding-reviewed commit that created 35 `DONE` rows
at once is the most extreme instance of the exact hazard §3 describes (a
scoreboard future sessions read instead of re-deriving), and it is a better
motivating example than #134.

Combining N2 and N3: the honest statement is that condition (a) is common
(roughly a quarter of reviews), condition (b) is common, and it is the
conjunction that is rare — which is precisely the design's own argument, just
with the arithmetic corrected.

### N4 (non-blocking, design) — the anti-ceremony machinery is a list nobody is assigned to read

Mandate item 2 asked whether §24 is taken seriously structurally or only
acknowledged. My honest read: partly structurally, and better than most
adaptations would manage, but with one real hole.

What is genuinely structural, not decorative:

- The triggers are narrow enough that volume — §24's actual mechanism of decay — stays near zero by construction. This is the strongest defense and it is built in, not asserted.
- §6's refusal of a CI gate carries a specific causal argument: a check that fires on "no findings" trains reviewers to write one decorative finding to avoid it, degrading the evidence quality the project depends on. That is an anti-ceremony argument that actively costs the design a convenience, which is the sign it is load-bearing rather than rhetorical.
- Rotation (§3) removes the standing contrarian the source's §25 warns gets tuned out, and is enforced by the same non-self-certification rule the project already runs.
- §6 states a falsification condition for the practice itself: "if this starts firing on most PRs, the triggers are miscalibrated — fix the triggers, do not tolerate the ceremony."

The hole: §7's six "signs this has gone wrong" are observable in principle
("minority reports are all GREEN, all short, all written in ten minutes"; "the
same agent keeps drawing the role"; "reports accumulate and nothing ever
reopens") but nothing in either document says *who looks at them, when*. §5
preserves every report regardless of verdict, so the corpus that would reveal
ceremony accumulates steadily with no assigned reader — and note §6.3 explicitly
dropped the source protocol's §28 scoring, the one mechanism the source itself
offers for detecting this, as "noise" over a handful of fires per year. The
result is that the design's answer to its own stated greatest danger is an
unowned checklist.

I am not asking for machinery — that would contradict §7.1/§7.9 and the
smallest-change rule, and the note is right that scoring a handful of events
would be noise. The cheap fix already exists in the project: the periodic
`ROADMAP_TRAJECTORY_CHECK.md` pass is a bounded audit with an owner and a
cadence, and Trigger 2 already couples this design to it. One line adding "read
`TENTH_SEAT_REVIEW.md` §7 against any minority reports accumulated since the
last pass" to that scope would close the hole at zero new machinery. Stated as a
recommendation, not a merge condition.

## 5. What I did not find

I looked for and did not find: any second source of status truth (the minority
report grants no authority and `CAPABILITY_CHECKLIST.md` remains the only place
status lives); any new authority surface (Law 6 is honored — a RED verdict is
explicitly non-blocking, and nothing changes who may merge or what the checker
requires); any misquotation of the source document; any inconsistency between
the note and the playbook doc; any claim in §8 "Boundaries respected by this PR"
that the diff contradicts; and any way the proposed artifact path could
interfere with the existing gate.

It is worth recording, given the subject matter, that the substantive findings
here are all arithmetic and attribution rather than design. A reviewer of a PR
about the danger of zero-finding reviews has an obvious incentive to manufacture
a finding, and I want the record to be clear that N1-N4 are things I counted or
read, each reproducible from the commands quoted, and that none of them is a
reason to withhold the merge. If they had not been there I would have said so
plainly.

## 6. Verification performed

- `git fetch origin`; reset to `origin/tenth-seat-protocol-design`; head confirmed `fba8c4ff3113848ca1cbd765b0616896c466105d`.
- `git diff --name-only origin/main..HEAD` → the three PR files, nothing else. `--stat` → 612 insertions, 0 deletions.
- `git diff 151f0d3..HEAD` read in full (two docs files, 28+/9-).
- Read `scripts/check_review_evidence.py` in full; verified lines 97 (exact path), 101 (single-file parse), 62-84 (walk-back), 81 (`all(... startswith("work/reviews/"))`), 71 (merge/root stop).
- Read `work/notes/2026-08-25-tenth-seat-protocol-design.md` and `playbook/TENTH_SEAT_REVIEW.md` in full.
- Read `/home/home/Documents/The_Tenth_Seat_Protocol.md`; grepped and confirmed every cited section number, law number, trigger letter, and the verbatim status line.
- `ls work/reviews/ | wc -l` → 82; `| grep -c review-evidence` → 69; the 13 non-evidence files enumerated.
- `grep -l "No findings" work/reviews/*.md` → `pr-134`, `pr-135` (2, as claimed).
- `grep -LiE "finding|gap|nit|caveat|concern|recommend|non-blocking|limitation|however" work/reviews/*.md` → 8 files (reproduces the author's count exactly).
- Same grep with `\bgap` and `\bnit\b` → 23 files. `grep -oiE "[a-z]*nit[a-z]*"` on the excluded files → `init`, `unittest`, `unit`, `Monitor`, `definition`, `sanity`.
- `grep -li "APPROVE (CLEAN)\|no bugs found\|no findings" work/reviews/pr-*-review-evidence.md | wc -l` → 26.
- For each of those 26 PRs, resolved the merge commit by `git log origin/main --grep="(#N)"` and counted added `DONE` lines under `work/roadmaps/` → non-zero only for #105 (35), #111 (1), #134 (1).
- Read trajectory checks #4, #5, #6, #7; grepped #6 for the two cited defects (lines 5 and 189); grepped #7 for the `RecoverySupervisor.tick()` re-verification (lines 47-58).
- Read master roadmap §§7.1-7.10 at source; confirmed the §7.3 quotation verbatim.
- Checked `CAPABILITY_CHECKLIST.md` rows E6 (line 50) and 6.16 (line 125) as a candidate counter-example to §6.2; it does not hold.
- `python3 scripts/check_review_evidence.py 169` run from the worktree root after committing this file.

## 7. Reviewer limits

- **No test run.** The diff contains zero executable lines, so there is nothing for a suite to exercise; I did not run the Python test suite and the diff-only verification above is the appropriate class of check here.
- **Precedents unverified.** Sanhedrin 17a, Mishnah Eduyot 1:5, and the Agranat Commission's alternative-analysis lineage are REPORTED by the source document. I verified the PR *cites them as the source states them*; I did not verify the underlying historical or halakhic claims, and neither did the PR, which says so.
- **N3's semantic count is a judgment, not a measurement.** I used `APPROVE (CLEAN)` / `No bugs found` / `No findings` as the operational reading of "zero findings" because it is this project's observed house style, and intersected with added `DONE` lines under `work/roadmaps/`. A different reasonable reading — for instance counting checkbox flips or "marks a design note implemented", which the trigger also admits — would give a different number. The note's own open question 3 already concedes that this property is not mechanically decidable, and I agree with it; my count should be read as "at least three", not "exactly three".
- **Status-flip detection was scoped to added `DONE` lines and `[x]` checkboxes** under `work/roadmaps/`. PRs that flip a status by rewording a row's evidence column without introducing the literal token would not have been caught, so N3 is a floor.
- **I did not review the PR's GitHub description or comments**, only the committed tree; a claim made only in the PR body is outside what I checked.
- **Single reviewer, single pass** at `fba8c4f`. If the branch head moves again, this evidence is bound to `fba8c4ff3113848ca1cbd765b0616896c466105d` and the checker will correctly fail closed until it is rebound.
