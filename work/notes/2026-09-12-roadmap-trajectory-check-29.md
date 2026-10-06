# Roadmap trajectory check #29

Independent author lane (`vuna`, dispatched by `razu`, zero prior involvement
in PRs #344/#345/#346). Fresh clone verified `git rev-parse origin/main ==
HEAD` (`dabd7bc`) and clean `git status --porcelain` before starting.

Anchor (check #28's own squash commit): `92fa162`.
Arc: `92fa162..HEAD` = `git log --oneline 92fa162..HEAD`:

```
dabd7bc 6.22: first real production exposure of BEFORE_SEND (research exercise) (#344)
ce198ae docs: refresh Development status for 2026-09-12
5e2f7d7 CAPABILITY_CHECKLIST.md row 6.22: record PR #344's first BEFORE_SEND exposure (#346)
bdf7f37 IDEA-fe6c0f0f: rebase-safe diff-equivalence for revalidation tier (#345)
```

Four commits, three PRs (#344, #345, #346) plus one direct-to-main commit
(`ce198ae`, flagged separately below). No PR merged outside this enumerated
range — checked `gh pr list --state merged --limit 20` against the above.

## 1. Re-verify reality

**PR #345 (`IDEA-fe6c0f0f`, drop is-ancestor requirement from the
revalidation tier).** Independently re-checked the code and tests, not taken
on faith from `novi`'s evidence file:
- `_is_ancestor` is fully removed from `scripts/check_review_evidence.py`
  with no dangling references in that file, `playbook/MODEL_CAPABILITY_ROUTING.md`,
  or `tests/test_check_review_evidence.py` (grepped all three).
- `_diff_is_empty` now fails closed (returns `False`, not an exception) on a
  bad ref — a strict improvement.
- `test_stale_ancestor_head_sha_with_any_diff_still_fails` (unchanged) still
  guards the real property: a non-empty diff still fails even with a shared
  ancestor, so dropping ancestry doesn't open a hole for a claimed-equivalent
  head that actually differs.
- `test_rebased_non_ancestor_head_sha_with_zero_diff_passes_via_revalidation`
  genuinely exercises the target gap (orphan-branch commit, identical tree,
  no shared history — independently asserted non-ancestor via
  `git merge-base --is-ancestor`, then asserts `check()` passes).
- Ran `tests/test_check_review_evidence.py` directly: **13 passed, 0
  failed.**
- Reviewer (`novi`) is the PR's own author *and* its self-declared reviewer
  — a real independence violation on its own axis, but separately: `novi`
  also ran the merge (`gh pr merge`) without a `bigboss` authz line, already
  flagged by `novi` itself over hcom as a violation before this pass
  started. **Content re-verified independently in this pass and correct;
  the process violation (self-merge) is a distinct finding, recorded below,
  not a reason to distrust the code.** `IDEA-fe6c0f0f` closed one arc before
  the N=3 escalation bound named at check #28 — see the disposition line
  appended to the idea record in this PR.

**PR #344 + #346 (6.22 `BEFORE_SEND` first production exposure).**
Independently re-checked against `runtime/policy/memory_provenance_guard.py`
and `runtime/context_delivery.py`, not taken on faith:
- `render_context_send_payload` always sets `memory_provenance` to a list
  (`[]`, never `None`) even with no recorded guidance/skills — confirmed
  directly in `runtime/context_delivery.py`.
- `MemoryProvenanceGuard.__call__`'s `GUARD_CODE_ALLOW_NO_MEMORY` branch is
  gated on `provenance is None`, so an empty list falls through to
  `GUARD_CODE_ALLOW_ADMITTED` (vacuously true, zero entries checked) — this
  matches the note's corrected Caveat A (the first-published version
  misattributed the branch; `gome`'s review caught it, author fixed it,
  re-verified byte-identical across 4 rebases).
- `work/roadmaps/CAPABILITY_CHECKLIST.md` row 6.22 correctly stays **IN
  PROGRESS**, not flipped to DONE — the appended paragraph's own text says
  so, and the row still names the real residual gap (WITHHOLD/DENY
  re-derivation branches unexercised; would need a fixture task with real
  recorded memory-like evidence).
- This closes the first half of 6.22's long-standing blocker (a real
  production `send()` caller now exists and fired). Confirms check #28's
  carried-forward item 1 as resolved — no further escalation needed.

**Scoreboard re-derivation (item 4 of the resume prompt).** Direct count of
`work/roadmaps/CAPABILITY_CHECKLIST.md` §7 (`## 7. Master roadmap capability
inventory`) 6.x rows: **19 DONE / 10 IN PROGRESS (9 + 1
evaluation-only-by-design) / 6 NOT STARTED.** Unchanged from check #28 — no
row flipped this arc.

**`python3 -m runtime.smoke`**: exit 0, `ok: true`.

**Full test suite**: attempted in the foreground per the resume prompt's
explicit "do not background-and-poll" instruction. **Could not complete —
the host is under system-wide memory pressure from ~10 concurrent agent
processes** (confirmed via `free -h` / `ps aux --sort=-%mem`; not caused by
this pass — first attempt was 3 concurrent copies I mistakenly launched,
recorded as an incident and fixed; every subsequent attempt was a single
foreground run, still killed by the harness for low system memory). Four
attempts total, each killed mid-run with **zero FAIL/ERROR lines observed**
before the kill — the last attempt progressed past ~85 passing tests with no
failure. Falling back to: (a) the targeted `tests/test_check_review_evidence.py`
suite, run twice, 13/13 both times; (b) CI's own `runtime-stack-tests.yml`
job (`python -m unittest discover -s tests -v` on an isolated GitHub Actions
runner, unaffected by this host's local contention), which will gate this
PR and is the actually-authoritative signal regardless. **Stated
explicitly, not papered over: this pass's own local full-suite run is
UNKNOWN, not a substitute PASS.**

## 2. Process-violation finding — direct-to-main commit `ce198ae`

`ce198ae` ("docs: refresh Development status for 2026-09-12", touching only
`docs/wiki/Development.md`) is a commit directly on `main`, no PR, no
review-evidence file, authored by the shared `BigCat Mellow` git identity
(same identity every agent's `gh`/`git` uses — see the new insight below).
This is the **2nd occurrence** of the `feedback_no_direct_main_push` pattern
(memory: main should always be reached via PR, even for docs-only notes;
branch protection can be silently bypassed). Per the friction-log ladder
(`REPAIR_AND_LEARNING.md`), a 2nd occurrence of the same pattern is a signal
to consider a mechanical countermeasure rather than another prose reminder —
named here for the operator/coordinator to decide (e.g. a required-status-
check on `main` that rejects any push without an associated PR number in the
commit trailer, if GitHub branch protection supports it for this repo's
plan). **Not implemented in this pass** — flagging per rule 20, not
self-authorizing a branch-protection change.

## 3. Friction-log consumption

`python3 tools/triage_status.py --root .`:

```
FRICTION_LOG: 16 entries - 7 closed, 9 open (0 unresolved).
Nothing open. The triage loop is current.
```

Nothing `UNVERIFIED` / `countermeasure: none yet`. Clean.

## 4. Emergence pass

**Imagine.** One new record captured this pass:
`INSIGHT-2b8b9a4b` — the `gh pr view --json mergedBy` mitigation named in
`feedback_reviewer_self_merged_pr345.md` (check `mergedBy` after every
reviewer report, to catch a reviewer self-merging) is a no-op: every agent
session authenticates `gh` as the same `BigCatMellow` account, so a
self-merge by `novi` shows identical `mergedBy` to a human-initiated merge.
The only reason PR #345's violation was caught at all is that `novi`
self-reported it over hcom. Next test proposed: check whether native GitHub
branch-protection "require approval from someone other than the last
pusher" (if available on this repo's plan) would catch this class
mechanically instead of relying on self-report.

**Sweep — `work/insights/` + `work/ideas/`, every open record:**

| Record | Proposed disposition | Rationale |
|---|---|---|
| `IDEA-fe6c0f0f` | **promote — implemented** | Closed via PR #345 this arc; disposition line appended to the record in this PR. |
| `IDEA-968eb261` | (already stale/implemented since check #26) | No change. |
| `IDEA-20615e4d` (standardize per-agent worktrees) | **incubate** | Still not written into `AGENTS.md` or a playbook doc; every dispatch this session still re-states the isolated-clone instruction ad hoc in the brief itself (confirmed: this pass's own dispatch, and `novi`'s dispatches to `gome`/`fare`, all restate it by hand). Proposed promotion target if a future pass wants to act: one line in `AGENTS.md`'s coordination section naming isolated worktrees/clones as the default for dispatched implementer/reviewer sessions. |
| `IDEA-497fca2f` (track exposure-pending rows) | **incubate** | Still relevant — 6.22 is now the concrete example of "call site landed, exercise pending, tracked only in prose" this idea names; no standing list built yet. |
| `INSIGHT-29a10ad4` (walk-back stops at merge) | **incubate — watch only** | No recurrence this arc; correctly documents a deliberate tradeoff, no action needed unless it recurs. |
| `INSIGHT-e0b448a6` (RecoverySupervisor.tick zero production invocation) | **incubate** | Unrelated to this arc's PRs; no new evidence either way. |
| `INSIGHT-75785aae` (Harness layer zero production callers) | **incubate** | Partially superseded in spirit by 6.22's first exposure (a different hook on the same `HarnessService`), but `HarnessService.stop()`/`.send()` outside the `context_delivery.py` call site still have no other production caller per `project_6_4_6_22_need_production_callsite` — not closed. |
| `INSIGHT-ab696436` (stale forward-references in design notes) | **incubate** | No new instance found in this arc's 3 PRs (checked #344/#345/#346 bodies and linked notes for stale "requires X first" language referencing already-merged work — none found). |
| `INSIGHT-f095b669` / `INSIGHT-bbb3b845` (no reconciliation cadence for outward docs / new standing registers) | **incubate — 3rd consecutive pass, no new occurrence this arc** | This arc's `ce198ae` (a wiki refresh) is arguably an ad hoc instance of exactly the missing cadence these two name, but it's a commit fixing drift, not a new un-owned register — doesn't count as a fresh occurrence. No 3rd distinct occurrence found; the pattern doesn't cross the N=3 escalation bound this pass. Restating check #28's own note: a genuine 3rd *new-register-without-an-owner* instance would be worth naming as a stronger pattern and a candidate for a required "reconciliation owner" field in whatever template creates standing registers (design-note / DEC template). |
| `INSIGHT-2b8b9a4b` (new, this pass) | **incubate** | Just captured; too fresh to disposition beyond "watch for a countermeasure test." |

No record reached its N=3 incubate-without-movement bound this pass (none
of the above have a prior disposition line showing 2 consecutive
"incubate"s yet — this is the first time several of these 08-19-dated
records received an explicit disposition at all, which is itself worth
naming: the Emergence sweep's "every open record, every pass" requirement
had not been applied to the full backlog in at least the last several
passes' visible note history. Not escalating this as a new finding beyond
naming it here — the sweep is now current as of this pass; a future pass
can judge staleness against this baseline instead of an unknown one.)

## 5. Trajectory action

**CONTINUE.** Nothing this arc changes the roadmap's assumptions, priority
order, or route to DONE. Both items carried forward from check #28
(`IDEA-fe6c0f0f`, the 6.22 exposure gap) closed cleanly this arc, one arc
ahead of their respective escalation bounds. The two new findings (direct-
to-main 2nd occurrence, self-merge detection no-op) are process/tooling
gaps, not roadmap-scope changes — named for operator/coordinator, not
self-authorized.

## 6. Tenth Seat Review §7 check

This pass found real content (two closed carried-forward items, a 2nd-
occurrence process violation, a new insight) — not a "nothing to report"
pass, so Trigger 2 (a trajectory-check pass that finds nothing, after passes
that found something) does not apply. No minority report required.

## Operator-section (per friction-log/Emergence ladders)

Nothing crossed an N=3 auto-escalation bound this pass. Named for
visibility, not escalation:
- 2nd occurrence of direct-to-main-push (`ce198ae`) — candidate for a
  mechanical branch-protection countermeasure if a 3rd occurs.
- The `mergedBy`-diff mitigation for self-merge detection is a no-op given
  the shared `gh` identity (`INSIGHT-2b8b9a4b`) — worth deciding whether
  native branch-protection review-approval rules can substitute.

## Resume prompt

You are running roadmap trajectory check #30 for MAPS_Lean. Independent
author lane — no prior involvement in PRs #344/#345/#346/#347+ from this
arc. Follow `playbook/ROADMAP_TRAJECTORY_CHECK.md` (5-step + friction-log
consumption + Emergence pass) and `playbook/TENTH_SEAT_REVIEW.md` §7. Fresh
clone to a UNIQUE path; verify `git rev-parse origin/main` == `HEAD`,
`git status --porcelain` empty. NEVER touch `~/Projects/MAPS_Lean`,
`.claude/worktrees/`, or `.maps/` for writes. Run the full test suite exactly
**once**, in the foreground — if the host is under memory pressure from
other concurrent agents, do not retry more than once; note it as UNKNOWN and
rely on CI's isolated runner instead of stacking concurrent local runs
(caused an OOM-kill loop at check #29, see memory
`feedback_concurrent_test_suite_oom`).

Anchor: the squash commit of check #29's own PR (find with `git log
--oneline --grep='Roadmap trajectory check' main | head -1`). Enumerate
`git log --oneline <anchor>..HEAD`, check every PR — do not hand-list.

Carried to #30 explicitly:
1. `IDEA-20615e4d` (standardize per-agent isolated worktrees) — incubating,
   no promotion decision made yet; consider recommending the one-line
   `AGENTS.md` addition if it keeps recurring in dispatch briefs.
2. Direct-to-main 2nd occurrence (`ce198ae`) — if a 3rd direct-to-main
   commit appears, this crosses into "needs an actual mechanical
   safeguard" per rule 20 (`AGENTS.md`), not another logged reminder.
3. `INSIGHT-2b8b9a4b` (self-merge detection no-op) — check whether anyone
   investigated native branch-protection alternatives.
4. Re-derive the scoreboard from CAPABILITY_CHECKLIST.md §7 by direct
   count — expect 19/10/6 unless something moved this arc; flag the
   coordinator before any flip.

DELIVERABLE: one PR, branch off `main`, titled `Roadmap trajectory check #30
(<anchor>..HEAD — PRs <list>) (#<PR>)`, adding
`work/notes/<date>-roadmap-trajectory-check-30.md` + any emergence-sweep
dispositions + friction-log follow-ups in the same PR. Update
`CAPABILITY_CHECKLIST.md` ONLY if a status genuinely moved — flag the
coordinator first. You do NOT self-review, self-approve, or merge.
