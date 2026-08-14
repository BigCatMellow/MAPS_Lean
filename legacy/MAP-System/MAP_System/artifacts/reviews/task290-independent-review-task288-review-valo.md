# Review: TASK-290 (Orchestrator auto-spawns an independent reviewer for unclaimed SUBMITTED tasks)

## Verdict

CHANGES_REQUESTED

## Reviewer

task288-review-valo (visible Sonnet helper, reassigned from the TASK-288
review per `MAP_System/inbox/helpers/helper-review-task-290.md` — not
`lili-replacement-nisa` or `claude-lab-lili`/its lineage, so not disqualified
from reviewing the task that formalizes exactly that disqualification
logic). Owner: `lili-replacement-nisa`. Claimed cleanly via
`claim_review("TASK-290", "task288-review-valo")` (`True` on first call, no
stale-claim cleanup needed this time).

## Reviewed Files

- `MAP_System/scripts/review_routing.py`
- `MAP_System/tests/test_review_routing.py`
- `MAP_System/notes/command-center-orchestrator-lifecycle.md`
- `MAP_System/templates/install/bin/ai-command-center-lab-codex` (the `PROMPT` string)
- `MAP_System/tasks/TASK-290.json`
- `MAP_System/scripts/context_rotation.py` (`parse_master`, to verify `rotation_chain()`'s data model assumptions)

## Acceptance Criteria Check

| # | Criterion | Result | Evidence |
|---|---|---|---|
| 1 | Lifecycle doc documents the auto-spawn-on-`next_route=review` behavior | PASS | `command-center-orchestrator-lifecycle.md`'s "Auto-spawning an independent reviewer (TASK-290)" section states it clearly. |
| 2 | `ai-command-center-lab-codex` prompt updated, consistent in form with TASK-286's paragraph | PASS | New sentence in the same prose-paragraph style as the rest of the orchestrator-routing text; not a structurally different format. |
| 3 | Eligibility check excludes author + recorded predecessor/replacement identity, not just literal `agent_id` | PASS (code); see REQUIRED finding below for the doc/prompt/code gap | `disqualified_reviewers()`/`rotation_chain()` do this correctly and are tested (7/7 pass, reproduced myself). |
| 4 | No duplicate reviewer spawned when a live claim exists | PASS | `needs_reviewer()` wraps `get_open_review_claim` directly; referenced by that exact name in both the doc and the prompt, so this half is not just prose-reconstructed. |
| 5 | Additive to TASK-286: no new auto-start lane at boot | PASS | Spawn is purely reactive to `next_route=review` + `submitted_tasks`; boot lanes (Shell/Codex/Monitor) are unchanged by this task's diff. |
| 6 | At least one test/dry-run per: no-claim (spawn), live-claim (no duplicate), all-candidates-disqualified (escalate) | PASS | `test_needs_reviewer_true_with_no_claim`, `test_needs_reviewer_false_with_live_claim`, `test_eligible_reviewer_returns_none_when_every_live_agent_disqualified` cover exactly these three, plus 4 more (author-only, single-hop, multi-hop, exclude-and-pick). |

## Reproduce, don't trust

- `MAP_System/.venv/bin/python3 MAP_System/tests/test_review_routing.py` — 7/7 PASS, reproduced myself.
- `bash -n MAP_System/templates/install/bin/ai-command-center-lab-codex` — syntax OK. The packet's own note that this broke once already (a stray apostrophe in a single-quoted shell string) made this worth checking directly rather than trusting the report; confirmed clean.
- `MAP_System/.venv/bin/python3 MAP_System/scripts/review_routing.py TASK-288 --live-agent lili-replacement-nisa --live-agent claude-lab-lili --live-agent claude-lab-venu --db MAP_System/map.db` against live `map.db`:
  ```
  {"disqualified": ["claude-lab-lili", "lili-replacement-nisa"], "eligible_reviewer": "claude-lab-venu", "needs_reviewer": true}
  ```
  Matches the expected result exactly (both `lili` identities excluded, `venu` picked). `needs_reviewer: true` here just reflects that TASK-288's own review claim was released when I approved it — not a defect, since in production this function is only invoked for tasks the runner actually reports as `next_route=review`.

## `rotation_chain()` multi-hop and cycle-safety (item 3)

Read the implementation directly rather than trusting the docstring. The
loop is a standard fixed-point ancestor walk: `chain` only ever grows (an
iteration adds `old_agent` only when it is not already in `chain`), and the
outer `while changed` loop exits the first pass that adds nothing new. The
set of candidate `old_agent` values is bounded by `len(all_entries)` (a
static, finite list parsed once from the ledger file), so the loop
terminates after at most `len(all_entries) + 1` passes regardless of the
ledger's shape. A malformed cyclic entry (e.g. `old_agent == replacement`)
cannot cause an infinite loop because it would already be in `chain` and
the `old_agent not in chain` guard skips it — it degrades to a no-op, not a
hang. This reasoning holds independent of the one worked multi-hop test in
the suite (`test_rotation_chain_walks_multiple_hops`, zed→yod→alfa), which
passes. No gap found here.

## REQUIRED: the tested eligibility logic is never actually invoked by the orchestrator (items 5 + 6)

This is the substantive finding, and it's the same shape of gap TASK-288's
own review caught: docs/prompt describing something adjacent to, not
identical with, what the tested code does.

`review_routing.py` exists specifically because — per its own docstring —
"the DB-level no-self-review check only compares literal agent_id strings"
and a context-rotation replacement inherits its predecessor's full
context, so a prose-level "check if they're related" judgment call is not
reliable enough; `disqualified_reviewers()`/`rotation_chain()` were built,
tested (7 tests, including a two-hop case and `history`-array inclusion),
and independently verified above to be correct.

But neither `command-center-orchestrator-lifecycle.md` nor the
`ai-command-center-lab-codex` `PROMPT` string ever names `review_routing.py`
(`grep -c review_routing` on both files returns `0`). Both instead tell the
orchestrator to "use `get_submission_author` plus
`shared/context-continuity.md` to rule out the author and any recorded
predecessor/replacement identity" — i.e., re-derive the disqualification
set at review time from raw primitives and prose reasoning, the exact
failure mode `review_routing.py` was built to replace. Worse, the doc's own
prose describes only a **single hop** ("if one exists, the author's
predecessor identity is also disqualified") with no mention of chained
rotations or the `history` array — both of which the tested code correctly
includes. An orchestrator (or a future human) following the doc/prompt
literally, without noticing `review_routing.py` exists and choosing to use
it, would very plausibly reimplement a *less correct*, single-hop-only,
`rotations`-only check by hand — silently regressing exactly the gap this
task was built to close, the same night this session recorded INS-0053
("documentation quality did not change the outcome... an independent
second check did").

Notably, the *other* half of the same feature (the live-claim/no-duplicate
check) is **not** subject to this gap: both the doc and the prompt name
`MAP_System.db.claims.get_open_review_claim` explicitly by qualified
function name, and the code calls that same function directly. The
asymmetry — the simple check is wired by name, the complex/error-prone
check is left to prose reconstruction — is itself evidence this was an
oversight rather than a deliberate design choice.

**Required action**: update both `command-center-orchestrator-lifecycle.md`
and the `ai-command-center-lab-codex` `PROMPT` string to name
`scripts/review_routing.py` explicitly (its CLI, e.g. `python3
MAP_System/scripts/review_routing.py <task_id> --live-agent ...
--live-agent ...`, or `eligible_reviewer()` if invoked from Python) as the
mechanism for the disqualification check, the same way `get_open_review_claim`
is already named for the claim check. This is a documentation/prompt-text
fix only — no code change needed, since `review_routing.py` already does
the right thing.

## Answering item 6 directly

Given the above, my view is that the amount of mechanization chosen
(tested Python module for eligibility logic) was the right call — the
multi-hop/history-inclusive walk is exactly the kind of thing prose
guidance reliably gets wrong under context pressure, and the test suite
proves the code path is correct. The gap isn't "too little code, too much
prompt" — it's that the mechanized correctness work was built but not
actually wired into the prompt-driven trigger path. I'd go further than
"not necessarily a blocker": given this session's own INS-0053 is
literally about prose-only correctness failing silently, shipping a new
orchestrator instruction that reintroduces exactly that pattern one
paragraph after fixing it elsewhere is worth blocking on. The fix is a
two-file text edit, not a redesign.

## Forbidden Changes Check

`git diff --stat` against the working tree is not a reliable scope signal
in this repo (hundreds of files sit uncommitted across many concurrent
tasks, same caveat as my TASK-288 review). Checked scope by content
instead: `review_routing.py` imports `get_open_review_claim` (`db/claims.py`),
`get_submission_author` (`db/review_authorship.py`), and `parse_master`
(`scripts/context_rotation.py`) but does not modify any of them — these are
pre-existing shared infrastructure (`review_authorship.py` already backs
`scripts/validate_review.py`, used in TASK-288's own review, predating
TASK-290). `db/claims.py` shows locally modified in `git status`, but that
diff (adding `record_submission_author` plumbing to `release_task`/
`submit_task`) is unrelated infrastructure from earlier review-authorship
work, not something introduced by TASK-290's four registered files. No
scope violation found. `MAP_System/inbox/helpers/helper-review-task-290.md`
(and the now-`complete` `helper-review-task-288.md`) are process/
coordination artifacts, consistent with how the TASK-288 review handled
the same category.

## Findings

| Severity | File | Finding | Required Action |
|---|---|---|---|
| REQUIRED | `MAP_System/notes/command-center-orchestrator-lifecycle.md`, `MAP_System/templates/install/bin/ai-command-center-lab-codex` | Neither names `scripts/review_routing.py`; both describe the disqualification check via raw primitives and single-hop prose reasoning, which under-describes (and risks a future hand-reimplementation regressing) the tested multi-hop/history-inclusive logic that already exists and is correct. | Name `review_routing.py` (CLI or `eligible_reviewer()`) explicitly in both places, the same way `get_open_review_claim` is already named for the claim-duplication check. |

## Notes

Everything else here is solid: the eligibility code itself is correct
(verified independently, not just via the test suite — read the fixed-point
loop's termination argument myself), the live-data demonstration matches
the expected disqualification/selection outcome exactly, the shell prompt
is syntactically valid, and the feature is genuinely additive to TASK-286
(no new boot-time lane). The one REQUIRED finding is a text-only fix with
no code change needed — should be a fast turnaround back to APPROVE.
