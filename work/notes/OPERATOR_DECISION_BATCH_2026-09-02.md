# Operator decision batch — MAPS_Lean, 2026-09-02

Paste-ready. Consolidates the operator questions that have accumulated since the
session-17 batch (`work/notes/OPERATOR_ASK_2026-08-31-session13.md`, answered in
PR #243). Same shape as that batch: **question → recommended answer → what it
unblocks → blocking?**

The operator prefers batched decisions (per the #243 precedent — *"Go ahead and
do all those things"*). A single **"proceed with the recommended answers"** on
this doc unblocks items 1–4; items 5–6 need a specific per-item nod.

All items re-verified against `origin/main` `e1e4467` (rule 14). Each cites its
source note (all merged).

---

## Item 1 — release-check 3b: make `composite == BLOCKED` an approval gate

**Source:** `work/notes/2026-09-02-release-check-3b-approval-gate-scoping.md` §1
(PR #249, merged `6cfa416`). The callout is drafted verbatim there; copied here.

**Question.** Make a `composite == BLOCKED` result from `maps flow
release-check` **hard-block `record_review` APPROVED** for an
`OPERATOR_VISIBLE_RELEASE_CHECK` task (today it is advisory only — shipped that
way in PR #244 per the #243 answer, which explicitly reserved 3b for "its own
callout"). Specifics:

- A non-empty `operator_ack_ref` on the latest `release_checks` row is the
  recorded, auditable override (no `--force`, no config flag).
- An `OPERATOR_VISIBLE_RELEASE_CHECK` task with **no** `release_checks` row is
  refused APPROVED (`RELEASE_CHECK_REQUIRED`) — the release check becomes
  mandatory for that review type, symmetric with the existing bound-subject
  gate.

**Recommended answer: YES to both.** The review type already means "the operator
must see this before the verdict"; making a recorded BLOCKED actually block —
with an explicit ack escape hatch — closes the gap between the name and the
enforcement. Cost: one ~8-line check in `_validate_review_approval_conn`, no
schema change, no CLI change (§3 of the source note). #234 §6 labels this "an
authority-model change", which is why it is an operator call and not a reviewer
one (rule 11).

**Unblocks:** the 3b impl slice (fully scoped in #249 §2–§5, ready to dispatch
on a YES).

**Blocking?** **No.** The advisory release-check already shipped (#244); 3a
stands if the answer is NO and #249 is shelved.

---

## Item 2 — adopt a merge-authority / merge-prep rule for coordinator-seat gaps

**Source:** `work/notes/2026-09-02-roadmap-trajectory-check-17.md` §1.5 (PR
#252). Three incidents in the session-17→19 arc: PRs #243/#244/#245/#246 sat
reviewed+APPROVED with `main` frozen for **5h+** with no coordinator seat; then
a concurrent-rebase race on #245 (two agents force-pushed the same branch
because merge-prep ownership was ambiguous during the gap — memory
`feedback_concurrent_rebase_race_pr245`).

**Question.** Adopt a standing rule (into `AGENTS.md` + the session-handoff
template):

- **(a)** a named fallback merge-prep order when the coordinator seat lapses —
  the longest-running peer lane owns rebasing + evidence-binding + keeping every
  PR merge-ready and non-conflicting, but **does not merge**;
- **(b)** `gh pr merge` stays **operator-only** (or an explicitly designated
  coordinator);
- **(c)** claim the rebase in-channel ("claiming the #N rebase") before
  force-pushing a shared PR branch.

Process rule only — no daemon, no new machinery (rule 13).

**Recommended answer: adopt all three.** This is the rule-20 countermeasure for
a 3-incident pattern; the alternative (another "be careful" instruction) is what
rule 20 explicitly rejects. It is an operator decision because (a)/(b) touch the
authority model.

**Unblocks:** nothing code-wise; prevents recurrence of the queue-stall and
rebase-race failure modes.

**Blocking?** **No.** But every coordinator-gap so far has cost hours; worth
answering this batch.

---

## Item 3 — SEC4 Half 3 2c: empty `authorized_operators` registry semantics

**Source:** `work/notes/2026-09-01-sec4-half3-slice2-scoping.md` §2c (PR #251,
merged `6b8e703`). Slice 1 (#245, merged) shipped the operator-chosen fail-open:
an empty `authorized_operators` table ⇒ identity checks disabled ⇒
byte-identical to pre-registry behaviour.

**Question.** Keep that, or harden it? Options:

- **(i) keep fail-open** (recommended) — empty registry = checks disabled, =
  today;
- **(ii) hard cutover** — empty registry = *all* gated approvals blocked
  (safer, but breaks every existing `maps skill` / CI invocation until a genesis
  row exists);
- **(iii) middle** — add a `--enforce-operator-identity` flag (default off) that
  turns fail-open into fail-closed *without* changing the empty-registry default
  (mirrors `maps recovery-tick --enforce-canonical-run`).

**Recommended answer: (i) keep fail-open now + (iii) add the opt-in flag as a
later slice.** Never (ii) — a hard cutover with no migration path is a
foot-gun.

**Unblocks:** SEC4 Half 3 completion planning (the last undecided sub-item of
Q B2).

**Blocking?** **No.** Slice 1 + the slice-2 scoping (#251) both stand as-is
under fail-open.

---

## Item 4 — 6.9 / S6: the path to DONE

**Source:** `work/notes/2026-09-02-6.9-s6-promotion-gate-step.md` (PR #250,
merged `e1e4467` — decision **NO FLIP**, 6.9/S6 stay IN PROGRESS; no status cell
changed, prose/evidence update only). The frozen selection eval now **exists**
(EXP-B, #246) and covers all six §6.9 categories, but the token selector scores
**1.00 on DIRECT / PARAPHRASE / MULTI_SKILL / NO_SKILL and 0.00 on
VOCABULARY_SHIFT / HARD_NEGATIVE / AMBIGUOUS** (f1 0.722) — it fails half its
own acceptance categories, so a DONE flip on "the eval exists" would be the
status-truth anti-pattern.

**Question.** Two paths to DONE (§5 of the source note):

- **(a)** a separate reviewed `_select_skills` quality PR closing the three
  0.00 gaps (near-synonym handling; a relevance threshold instead of
  any-token-overlap; optionally a confidence signal for `AMBIGUOUS`), re-running
  EXP-B as the acceptance test; **or**
- **(b)** an explicit §17.3 operator sign-off that the *characterised* selector
  behaviour (perfect on precise vocabulary; blind on synonym / hard-negative /
  ambiguity, with the downstream 6.22 trust-gate + SEC4 quarantine containment)
  is acceptable to promote as-is, recording that decision as the DONE evidence.

**Recommended answer: pursue (a).** Fall back to (b) only if the scoping work
concludes (a) needs semantic retrieval — which would be a separate
EVIDENCE-GATED roadmap item, not a 6.9 slice. gela is scoping (a) now.

**Unblocks:** a concrete 6.9/S6 DONE route.

**Blocking?** **No** — but the operator should know (b) is on the table so a
stalled (a) has an exit.

---

## Item 5 — Ask #1 enforced canonical-run pass: target + timing

**Source:** `work/notes/OPERATOR_ASK_2026-08-31-session13.md` (Ask #1,
**AUTHORIZED** in #243) + `work/notes/2026-09-02-roadmap-trajectory-check-17.md`
§2.3. One enforced `maps recovery-tick --enforce-canonical-run` pass is
authorized; two things still need the operator:

1. **Target** — recommended `~/Projects/MAPS_Lean`. **Prerequisite:** `.maps/`
   does **not** exist in this checkout, so there is no control-plane DB here.
   The coordinator must first establish the control-plane DB + register a
   `--harness-project-id` per `docs/CONTROL_PLANE_SETUP.md`. **This is a
   coordinator task, currently unowned** — trajectory check #17 flags it as the
   single highest-leverage item on the board.
2. **Timing** — the operator confirms "go" for the pass once the control plane
   is stood up. Expected first-run effect: some working resumes become
   `resume_denied` (`LEASE_EXPIRED` most likely), remediated per
   `docs/CONTROL_PLANE_SETUP.md` §5. No impl/review agent runs the enforced pass
   autonomously (per the #243 answer).

**Recommended answer:** confirm target = `~/Projects/MAPS_Lean`; authorise the
coordinator to stand up the control plane; the operator gives the final "go"
for the one pass after that.

**Unblocks:** **6.4 / 6.5 / 6.16 / 6.22 + H5 / E4 / L6 — 7 roadmap rows**
(each verified hard against real evidence before any status flip). Highest
leverage in the batch.

**Blocking?** **Partially.** The control-plane setup is dispatchable coordinator
work now (no operator input needed to start it); the *pass itself* needs the
operator's go.

---

## Item 6 — infrastructure carry-overs (still open from session 13/16)

**Source:** `work/notes/OPERATOR_ASK_2026-08-31-session13.md` Infra #2/#3 +
the session-15 worktree audit. None resolved.

1. **Worktree cleanup Bash permission** — ~70 classifier-blocked `git worktree
   remove` / `git branch -D` entries for merged/abandoned worktrees (the count
   has grown from 44). Either add a scoped Bash permission rule, or the operator
   runs the audited `remove.sh` (session-15 scratchpad). The 4 worktree locks
   from the now-dead pid 3874 are among these.
2. **5 stale remote branches** on `origin` (audit rows 24 / 33 / 39 / 47 / 48) —
   `gh api -X DELETE` set, audited, needs the permission or an operator run.
3. **`git push --force-with-lease origin <tmp-branch>:<ref>` permission rule** —
   classifier-blocked-then-retried on essentially every merge-prep this session
   (rebased-branch force-pushes). A scoped allow rule for force-pushing
   `vame/*` / `evtmp*` style throwaway rebase branches would remove the friction.

**Recommended answer:** add the three scoped Bash permission rules (they are all
low-risk, repo-local, and audited), OR schedule one operator cleanup pass.

**Blocking?** **No** — but it is friction on every merge and every worktree
lifecycle, and it compounds.

---

## Summary table

| # | Item | Recommended | Unblocks | Blocking? |
|---|------|-------------|----------|-----------|
| 1 | release-check 3b approval gate | YES | 3b impl slice | No (3a shipped) |
| 2 | merge-authority / merge-prep rule | adopt (a)(b)(c) | prevents queue-stall + rebase-race recurrence | No |
| 3 | empty-registry semantics | keep fail-open + opt-in flag later | SEC4 Half 3 completion planning | No |
| 4 | 6.9/S6 DONE path | pursue (a), (b) as fallback | 6.9/S6 DONE route | No |
| 5 | Ask #1 pass — target + timing | confirm target, authorise control-plane setup, then "go" | **6.4/6.5/6.16/6.22 + H5/E4/L6 (7 rows)** | Partial |
| 6 | infra permission rules | add 3 scoped Bash rules | merge + worktree friction | No |

---

## Resume prompt

You are surfacing the MAPS_Lean operator decision batch dated 2026-09-02
(`work/notes/OPERATOR_DECISION_BATCH_2026-09-02.md`). Present all 6 items to the
operator together, in the summary-table order, with the per-item recommended
answers. Items 1–4 can be accepted as a block ("proceed with the recommended
answers"); items 5 and 6 need a specific per-item response (5: target + a "go"
after the coordinator stands up `.maps/`; 6: yes/no on the three scoped Bash
permission rules). Record the answers back into this doc under a dated
"OPERATOR ANSWERED" heading (same as
`work/notes/OPERATOR_ASK_2026-08-31-session13.md`), then dispatch the unblocked
impl work: item 1 → the #249 3b slice; item 5 → the control-plane setup lane
then the enforced pass; item 4(a) → gela's selector-quality PR. Do not resolve
any item yourself — the operator is the accountable party.
