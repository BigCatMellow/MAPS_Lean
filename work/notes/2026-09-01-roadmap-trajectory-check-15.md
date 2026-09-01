# Roadmap trajectory check #15 — arc: `dbd786c..HEAD`

Fifteenth pass. Predecessor: `work/notes/2026-09-01-roadmap-trajectory-check-14.md`
(arc `8c5455b..HEAD`, PRs #221/#223–#227, action **CONTINUE**, scoreboard
16/13/6 — seventh consecutive pass; found §2 defect in `memory_trust_gate_note`).

## Arc derivation (commit range, per PR #212)

```
$ git log --oneline --grep='Roadmap trajectory check' main | head -1
dbd786c Roadmap trajectory check #14 (8c5455b..HEAD — PRs #221, #223-#227) (#228)

$ git log --oneline dbd786c..HEAD
5909169 6.21: maps flow handoff — same-task worker continuity link (#231)
2b57725 Design note: rule-20 safeguard for invariant-describing-prose drift (#232)
993d48b Design note: 6.9/S6 slice 2 — execution-level Skill resource loading (#230)
e0d4717 context_builder: correct memory_trust_gate_note after #225 capability DENY (#229)
```

Arc = **4 PRs: #229, #230, #232, #231**. 1 code-fix (#229 — closes check #14's
§2 finding), 2 design notes (#230, #232), 1 impl (#231 — `maps flow handoff`).
HEAD `5909169`.

Method (rule 14): no claim taken from a PR title/body/review summary; every
consequential claim re-checked against `git show`, `/usr/bin/grep` over
`runtime/` excluding `tests/`, a read of the merged code, and a test run.

## 0. Situational awareness

- `python3 -m runtime.smoke` → **exit 0 at `5909169`** (`sqlite_task_lifecycle`
  ok, WAL / foreign_keys=1 / busy_timeout=5000).
- `python -m pytest -q` **from the repo root fails collection** — 42 errors in
  `migration/legacy-runtime-source/tests/` (un-importable legacy code, not the
  MAPS_Lean suite; CI uses `python -m unittest discover -s tests`). See §1e for
  the scoped test evidence.
- **Scoreboard recounted** from `work/roadmaps/CAPABILITY_CHECKLIST.md` §7 table
  (6.1–6.35 = 35 rows, Status column):
  - **DONE 16** — 6.1, 6.2, 6.3, 6.6, 6.7, 6.8, 6.13, 6.14, 6.15, 6.18, 6.23,
    6.26, 6.27, 6.28, 6.29, 6.30.
  - **IN PROGRESS 13** — 6.4, 6.5, 6.9, 6.10, 6.11, 6.16, 6.19, 6.20, 6.21,
    6.22, 6.24, 6.33, 6.35.
  - **NOT STARTED 6** — 6.12, 6.17, 6.25, 6.31, 6.32, 6.34.
  - **Identical to passes #8–#14. Eighth consecutive pass at 16/13/6.**
  - Derivation matched against the arc: #229 is verification-only (PR body +
    diff: `runtime/context_builder.py` prose + one test assertion, "No checklist
    status change"); #230/#232 are design notes; #231's own checklist clause
    ends "6.21 stays IN PROGRESS" (verified in the row text). **No PR in the arc
    flips a status; the recount agrees with 16/13/6.** (Dispatch STOP (c) not
    triggered.)

## 1. Re-verification of arc claims against merged code

### 1a. #229 — `memory_trust_gate_note` correction (closes check #14 §2). Confirmed accurate.

`git show e0d4717 --stat`: `runtime/context_builder.py +21/-6`,
`tests/test_skill_capability_manifest.py +21`, `work/reviews/pr-229-review-evidence.md`.
Read the merged note string (`runtime/context_builder.py`, the
`"memory_trust_gate_note"` value):

> "every memory-like item **that reaches the trust gate** passes
> `admit_memory_evidence()`; its MemoryTrustClass alone decides **that item's**
> bucket membership … **One DENY is decided earlier and outside the trust
> gate**: SEC4 capability-manifest slice 2 (#225) … `SKILL_CAPABILITY_OUTSIDE_TASK_ENVELOPE`
> … recorded in the same tally … distinguishable by its reason code."

The check-#14 §2 over-claim ("**every** memory-like item passed
`admit_memory_evidence()` … **MemoryTrustClass alone** decides") is gone; the
capability-envelope DENY is named and correctly described as same-tally /
distinguishable-by-reason-code. **No behavior change** (the diff is prose + one
`test_skill_capability_manifest.py` assertion that the note no longer
over-claims). #229's own choice to fold the DENY into the existing tally rather
than add a `capability_envelope_denied` counter is defensible and matches
check-#14 §2's recommendation of "acceptable either way". **The check-#14
finding is closed.**

### 1b. #230 — 6.9/S6 slice-2 design note. Confirmed design-only.

`git show 993d48b --stat`: `work/notes/2026-09-01-6.9-slice2-execution-level-design.md`
only, +360. STATUS line present. Scopes an `execution_resources` manifest
(path/kind/bytes, no content) + a `load_skill_resource(descriptor,
relative_path)` deterministic single-file loader; §7 "OPERATOR DECISION: none";
§8 no STOP condition; verdict DISPATCHABLE. Impl not yet started (dispatched
session 17). No status flip.

### 1c. #232 — invariant-prose-drift safeguard design note. Confirmed design-only.

`git show 2b57725 --stat`: `work/notes/2026-09-01-invariant-prose-drift-safeguard-design.md`
only (the merge includes the review-fold commit reconciling it with #229 — §2
now reads "3 of 4 `*_note` unpinned; `memory_trust_gate_note` pinned by #229's
test"). Safeguard = a `test_context_builder.py` consistency test (Part A) + an
optional `scripts/check_coverage_note_pins.py` (Part B); explicitly does **not**
close `feedback_checklist_edit_repeatedly_skipped` (§6). No status flip. Impl
not yet started (dispatched session 17).

### 1d. #231 — `maps flow handoff` impl. Verified; one prose-precision finding (§2).

`git show 5909169 --stat`: `runtime/flow_handoff.py +100` (new),
`runtime/cli.py +19`, `tests/test_flow_handoff.py +289` (new),
`work/roadmaps/CAPABILITY_CHECKLIST.md +2/-1`. Read the merged
`runtime/flow_handoff.py` + `runtime/cli.py` diff + `tests/test_flow_handoff.py`:

- **Pure composition, no new primitive / schema / authority** — confirmed.
  `flow_handoff(store, task_id, *, from_worker, to_worker, reason)`:
  `store.get_task` → `NOT_FOUND` if absent; guard
  `task.get("status") != "ACTIVE" or task.get("claimed_by") != from_worker`
  → `HANDOFF_NOT_CLAIMANT` (a read-check against `get_task`, not a lookup;
  deliberately no lease-liveness check — matches design note
  `2026-09-01-6.21-flow-handoff-design.md` §3); `store.record_continuity_link(
  from_worker, to_worker, reason=reason)` (the **existing** primitive —
  `/usr/bin/grep -n "def record_continuity_link" runtime/state/integrity.py`
  → line 479, unchanged in this arc), errors surfaced verbatim; return
  `next_step: {"state": "STOPPED_BEFORE_REPLACEMENT_CLAIM", "reason": …}`.
- **Review-independence consequence is automatic** — `flow_handoff` touches no
  review table; `_continuity_component_conn` (`runtime/state/integrity.py:520`)
  walks the new link on every `claim_review` / `record_review` call.
  `tests/test_flow_handoff.py::test_continuation_worker_cannot_claim_independent_review`
  asserts it end-to-end (`claim_review(task, "worker-b")` →
  `CONTINUITY_REVIEW_FORBIDDEN`; `claim_review(task, "reviewer-c")` still ok).
- **nava's review caught a real mutation survivor** during #231 review — the
  `record_continuity_link(from_worker, to_worker)` → `(to_worker, from_worker)`
  swap passed all 11 original tests (undirected component + no direction
  assertion). Fixed by a direct `SELECT predecessor_id, replacement_id FROM
  continuity_links` assertion. **That was the #231 review doing its job**, not
  this trajectory pass; recorded for completeness.
- CLI: `maps flow handoff TASK --from-worker --to-worker --reason` on the
  existing `flow` subparser (`runtime/cli.py:347`), dispatched at `:712`.
- **6.21 stays IN PROGRESS** — the row clause verified: `recover` / `release`
  still unimplemented, correctly deferred.

### 1e. Test evidence at HEAD (`5909169`)

- **`python3 -m runtime.smoke` → exit 0** (§0).
- **All 4 arc PRs merged with green CI.** CI (`.github/workflows/*`) runs
  `python -m unittest discover -s tests` and gates every merge; `HEAD` is
  `origin/main`, so the `tests/` suite is green at `5909169` by construction of
  the merge gate. Each PR body also records its own foreground run (#231: "OK
  66"; #229: "green"; #230/#232 design-only + `runtime.smoke` 0).
- **Local corroboration** (machine under heavy load — 5+ concurrent sessions
  including an active 6.9/S6 slice-2 impl lane, so a full local `pytest tests/`
  run did not complete in a reasonable window and was abandoned; targeted
  modules run instead):
  - `python3 -m unittest tests.test_flow_handoff
    tests.test_skill_capability_manifest` → **Ran 43 tests, OK**.
  - (this lane's earlier work, same HEAD family) `tests.test_context_builder`,
    `tests.test_skills_format`, `tests.test_skills_catalog`,
    `tests.test_policy_state` were run green during the #225/#229 arcs.
- **`python -m pytest -q` from the repo root is not a valid suite command** —
  it fails collection on `migration/legacy-runtime-source/tests/` (42 errors,
  un-importable legacy). Recorded for check #16 (see §6).

## 2. Substantive finding — `flow_handoff`'s review-independence scope is described as task-scoped, but the mechanism is global

`runtime/flow_handoff.py`'s docstring:

> "the review-independence consequence (`to_worker` … can no longer claim
> independent review of **this task's lineage**)"

and its `next_step.reason`:

> "`{to_worker}` … cannot claim independent review of **its lineage**"

and the `CAPABILITY_CHECKLIST.md` 6.21 clause (#231):

> "the continuation identity's `claim_review` is `CONTINUITY_REVIEW_FORBIDDEN`
> [for] **its lineage**"

**The `continuity_links` table has no `task_id` column** (`runtime/state/schema.sql`
— `predecessor_id, replacement_id, reason, created_at`, PK on the pair), and
`_continuity_component_conn(conn, identity)` walks **all** `continuity_links`
rows globally. `claim_review` / `record_review` check `reviewer_id in
_continuity_component_conn(conn, submission["author_id"])`.

**Effect:** after `maps flow handoff` A→B for task T, B cannot claim independent
review of **any task whose submission author is A or anyone else in A's
continuity component** — not just T. The prose in three places ("this task's
lineage" / "its lineage") describes a task-scoped disqualification that the
code does not implement.

- **Severity: LOW.** The actual behavior is the **conservative** direction
  (it over-restricts review eligibility, never under-restricts), and it is
  exactly how `record_continuity_link` is used everywhere else
  (`test_agentic_security_baseline.py::test_sec_adv_006` links
  `author`→`helper-continuation` with the same global effect). `flow_handoff`
  introduces **no new semantic** — it wraps the existing primitive at its
  existing (global) scope. Nothing computes wrong.
- **It is a prose-precision issue**, in `runtime/` code (the docstring +
  `next_step.reason` string) and the checklist clause — the *same class* the
  #232 safeguard (merged this very arc) is being built to catch. A neat, if
  minor, confirmation that the pattern is live: a claim narrower than the code
  landed in the arc that scoped the safeguard for it.
- **Not a correctness defect** — dispatch STOP (b) is about a *shipped
  correctness defect*; this is documentation precision with safe behavior, so
  no mid-pass STOP. Flagged to @mepo in the pass summary regardless.

**Recommended fix (next-3 #1 candidate):** a one-line prose correction in
`flow_handoff.py` (docstring + `next_step.reason`) and the 6.21 checklist clause
— "cannot claim independent review of **any task in `from_worker`'s continuity
component**" (or "of this task's — and, because a continuity link is a global
identity relationship, any of `from_worker`'s — lineage"). Small; could fold
into the #232 safeguard impl PR or the `flow_handoff` follow-up, or a standalone
one-liner. It is a legitimate candidate for the #232 Part-A consistency test's
*scope* to eventually cover (docstrings that describe an invariant, not just
`coverage` note strings) — but that widening is explicitly deferred in #232 §5
and should stay deferred.

## 3. Tenth-Seat / §7 duty (`TENTH_SEAT_REVIEW.md` §2 Trigger 2, §7)

Trigger 2 arms when a pass reports "**no substantive finding** — no stale row,
no mislabeled status, **no changed picture**" and passes #8–#14 each found
something. As of #15 the tripwire **is armed** (dispatch confirms; #14 found the
`memory_trust_gate_note` defect).

**It does not fire.** §2 is a substantive finding: a claim in merged `runtime/`
code (and the checklist) that is narrower than what the code does — a "changed
picture" in the §7 sense (a foundational-adjacent statement about how the
review-independence guarantee is scoped is imprecise), surfaced by reading the
`continuity_links` schema and `_continuity_component_conn` against the
`flow_handoff` prose, which a shallow pass skips.

§7 "signs this has gone wrong" checked (no minority reports have ever accumulated
— Trigger 2 has never fired):

- *"same conclusion every pass regardless of evidence"* — scoreboard identical
  for an 8th pass, but the **content** differs: #13 three fixes, #14 a
  coverage-note defect, #15 a scope-precision defect in the arc's one impl. The
  action has been CONTINUE for #13–#15, but each rests on a fresh verification
  and a fresh finding, not inertia.
- *"verdict drifting toward reassurance"* — this pass is not reassuring: it
  names a prose/scope imprecision in a just-merged impl and observes the #232
  safeguard's target pattern recurring in the very arc that scoped it.
- *"no one has run the full check"* — arc range-derived; all 4 PRs read at the
  code level; the §2 finding needed the `continuity_links` schema + the
  component-walk source, not the checklist.
- *"the seat challenges detail and never a foundational claim"* — §2 is
  arguably foundational-adjacent (the *scope* of a security guarantee), not
  "should this row say DONE".

**No Tenth-Seat sub-agent dispatched** (flagged to @mepo; Trigger 2 negative).

## 4. Friction-log consumption (standing duty)

Log walked in full (5 entries; **no new entries** since #14).

| # | Entry | `verified:` | Disposition this pass |
|---|-------|-------------|-----------------------|
| 1 | self-clear resume prompt dropped | END-TO-END | **Closed.** This session (`gela`, session 17) received `MAPS_Lean_Handoff_2026-09-01-session16.md` as SessionStart context, no operator nudge. 6th confirmation. |
| 2 | coordinate-via-helper-lanes preference | verified | **Closed.** In active use — `mepo` (session 17) dispatching lanes; `rozo` ran the full session-16 arc the same way. |
| 3 | context-rotation checkpoint too small | **VERIFIED (per #14)** | **Closed — no re-open.** #14 applied `PARTIAL → VERIFIED`. Session 16 (`rozo`) ran a 16-PR arc; session 17 continuing. No disruptive rotation. Nothing further. |
| 4 | triage loop procedure-only | VERIFIED | **Closed.** This section is the consumption duty discharged for a 6th consecutive pass (#10–#15). |
| 5 | orchestrator tool-use burned ~30–40k context | n/a (behavioral), `countermeasure: none yet` | **Consumed — no recurrence across the #229–#232 arc; stays open.** #229 was a ~25-line prose fix; #230/#232 (this lane's design notes) used targeted `/usr/bin/grep`, path-scoped `git show`, `sed -n` ranges, `Read` offset/limit — no large dumps or whole-doc re-reads. #231's lane likewise (its PR body shows scoped verification). 4th consecutive no-recurrence arc. Follow-up line appended. |

Nothing in the log needs escalation to trajectory work or an operator decision.

## 5. Trajectory action: **CONTINUE**

Reasoning:

- All 4 arc PRs verify against merged code. #229 correctly closes check #14's
  §2 finding. #231 is a real, verified, ask-#1-independent capability addition
  (the `maps flow handoff` verb) — one of check #14's next-3.
- The one new finding (§2) is LOW severity (a prose/scope imprecision with safe,
  conservative behavior) with a one-line fix.
- Check #12's REPRIORITIZE keeps delivering: check #14's next-3 landed
  (`memory_trust_gate_note` fix #229, prose-safeguard design #232, flow-handoff
  impl #231, 6.9/S6 slice-2 design #230); the two impls dispatched this session
  (safeguard, 6.9/S6 slice 2) are the natural continuation.
- **No status flip warranted or missed** (§0, §1). Scoreboard 16/13/6 is the
  designed shape — each IN PROGRESS row's DONE gate is "full capability + first
  production exposure + all sub-slices", and the arc advanced 6.21 (a verb) and
  closed a defect without any row reaching its gate.
- **Operator asks #1 / #2 (`work/notes/OPERATOR_ASK_2026-08-31-session13.md`) —
  still open.** Ask #1's cluster is **7 rows** (6.4 / 6.5 / 6.16 / 6.22 / H5 /
  E4 + L6). This is the **5th+ consecutive pass** with the ask unanswered.
  **Re-escalation framing:** the independent-work runway (6.9/S6, SEC4 manifest,
  6.21 verbs, the prose safeguard) is real but finite — checks #12–#15 have
  consumed most of it. If ask #1 is not answered before check #16 / #17, the
  next trajectory pass should treat "no independent slices left AND ask #1
  still open" as a genuine RESEARCH/STOP-level signal (check #12's original
  tripwire, re-armed). @mepo should carry ask #1 to the operator now with that
  timeline stated.

**No REPRIORITIZE** (independent work is still flowing — two impls dispatched
this session), **no CUT SCOPE / RESEARCH / STOP / ADD**.

### Proposed next-3 for check #16

1. **The two impls dispatched this session land:** 6.9/S6 slice 2 (execution-
   resource manifest, per #230) and the invariant-prose-drift safeguard (Part A
   + optional Part B, per #232). Check #16 verifies both merged and correct.
2. **The §2 `flow_handoff` prose/scope fix** — one line in `flow_handoff.py`
   (docstring + `next_step.reason`) and the 6.21 checklist clause: state the
   review-independence disqualification is `from_worker`-continuity-component-
   wide, not task-scoped. Trivial; fold into whichever PR touches nearby.
3. **6.21 `release` design note** OR **6.9/S6 slice 3** (execution-level
   *content* loading via `load_skill_resource`, once slice 2's manifest lands) —
   whichever the coordinator prefers. `recover` stays PARKED (operator +
   schema decision, unchanged).

## 6. Recorded for the next pass (check #16)

- **Arc anchor for check #16:** the squash commit of *this* PR. `git log
  --oneline --grep='Roadmap trajectory check' main | head -1` then `<that>..HEAD`.
- `python3 -m runtime.smoke` exit 0 at `5909169`.
- **Test-run note:** `python -m pytest -q` **must be scoped to `tests/`** —
  from the repo root it fails collection on `migration/legacy-runtime-source/tests/`
  (42 un-importable legacy modules). CI's `python -m unittest discover -s tests`
  is the authority. Recorded so check #16 does not mistake the collection
  errors for a regression.
- Scoreboard: 16 / 13 / 6 — **eighth** consecutive pass. Tenth-Seat Trigger 2
  armed, **did not fire** (§2 finding). Re-arms for #16 (passes #14, #15 both
  found something).
- **§2 defect** (`flow_handoff` review-independence scope prose): if the
  one-line fix has not landed by check #16, re-flag — a claim narrower than the
  code should not sit two passes (this is exactly what check #14 said about its
  own §2 finding, which #229 then fixed).
- Cluster blocked on operator ask #1: **7 rows** (6.4 / 6.5 / 6.16 / 6.22 / H5 /
  E4 + L6). Independent-work runway is nearly consumed — see §5. Verify all 7
  hard before any flip if the ask lands.
- SEC4 B1 `authorized_operators`: `/usr/bin/grep -rn "authorized_operators"
  runtime/` → **still absent** (verified at check-15 time). Design-pending on
  the operator trust-root decision.
- Zombie pid 3874 (session-8 orphan): **still alive** — `ps -p 3874 -o pid,etime`
  → `ELAPSED 1-10:00:57` (~34 h). Unchanged since #13/#14. Operator decision to
  kill, not a trajectory action; recorded in the operator-ask doc.
- Friction: entries 1–4 closed; entry 5 open (4th no-recurrence arc).

## Resume prompt

You are running roadmap trajectory check #16 for MAPS_Lean. Follow
`playbook/ROADMAP_TRAJECTORY_CHECK.md` (5-step + friction-log consumption) and
`playbook/TENTH_SEAT_REVIEW.md` §7 (read it before recording any clean result).
Worktree off `origin/main`; `git fetch origin main` first.

Arc: anchor = `git log --oneline --grep='Roadmap trajectory check' main | head -1`
(the check-#15 squash commit), then `git log --oneline <anchor>..HEAD`. Do NOT
hand-list (standing rule, PR #212).

Method (rule 14): no claim from a PR title/body/review summary; re-verify against
`git show`, a read of the merged code, `/usr/bin/grep` over `runtime/` excluding
`tests/`, and a test run. `python -m pytest -q tests/` (SCOPED to `tests/` —
the repo root fails collection on `migration/legacy-runtime-source/`) or
`python3 -m unittest discover -s tests`. `python3 -m runtime.smoke` must exit 0
— record the sha.

Specifically check: (a) **operator ask #1** — answered? 7-row cluster
(6.4/6.5/6.16/6.22/H5/E4/L6). The independent-work runway is nearly consumed
(§5) — if the ask is still open AND check #15's next-3 have landed with no new
independent slices identified, treat "no runway left + ask open" as a
RESEARCH/STOP-level signal, flag @coordinator. Confirm
`work/notes/OPERATOR_ASK_2026-08-31-session13.md` stayed tracked. (b) Did check
#15's next-3 land: 6.9/S6 slice-2 impl (#230), invariant-prose safeguard impl
(#232), the §2 `flow_handoff` prose/scope fix? (c) Re-derive 16/13/6 from the
§7 table — **Trigger 2 re-armed** (#14, #15 both found something); a genuinely
clean #16 fires it — flag the coordinator BEFORE dispatching a Tenth-Seat
sub-agent, then write `work/reviews/trajectory-16-minority-report.md`.
(d) Friction entry 5 (recurrence). (e) SEC4 B1 `authorized_operators`.
(f) Zombie pid 3874.

Deliverable: `work/notes/2026-XX-XX-roadmap-trajectory-check-16.md` (+
friction-log follow-up lines, + minority report iff Trigger 2). Update
`CAPABILITY_CHECKLIST.md` ONLY if a status genuinely moved (hard evidence) or a
clause is provably wrong (prose fix — flag the coordinator before any status
flip).

Workflow: own worktree; PR into `main` (never push); verification-only review;
do NOT spawn your own reviewer — ping the coordinator; no self-merge; report the
PR number to the coordinator.

STOP + flag the coordinator if: a status claim is wrong in a way that changes
the route to DONE and needs a flip you are not certain of; a shipped
correctness defect (not prose) in the arc; the trajectory action would be STOP
or an envelope-leaving REPRIORITIZE; `TENTH_SEAT_REVIEW.md` §7 signals the check
has gone shallow; or before dispatching the Tenth-Seat sub-agent.
