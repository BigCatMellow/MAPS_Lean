# Roadmap trajectory check #21 — arc: `f303d79..HEAD`

Twenty-first pass. Predecessor: `work/notes/2026-09-03-roadmap-trajectory-check-20.md`
(PR #271, arc `8cf99c2..HEAD` = 6 PRs #263–#268, action **CONTINUE**; scoreboard
16/13/6 → **17/12/6** — first move in twelve passes, 6.9/S6 → DONE on a valid
§17.3 operator sign-off. Substantive #20 finding: item-5's enforced pass is
blocked by an hcom 0.7.25 `list --stopped --json` defect that aborts all of
`maps recovery-tick`; fix in flight as PR #269, Part A folded, Part B scoped.)

## Arc derivation — standard anchor

```
$ git log --oneline --grep='Roadmap trajectory check' main | head -1
f303d79 Roadmap trajectory check #20 (8cf99c2..HEAD — PRs #263–#268) (#271)

$ git log --oneline f303d79..HEAD
f2e57b9 Capture Pilot/MAPS_L conversation-derived architecture findings (#272)
4ca8af5 research: organize Claude/Codex mechanism scans (#274)
9a884c2 Item 5 / option C: rebuild stopped-session records from `hcom events` (#276)
ea76854 Docs: session-24 FRICTION_LOG backlog (scratchpad contamination + hcom env leak) (#275)
a6ad820 Record + design fix: hcom 0.7.25 --stopped --json defect blocks recovery-tick (item 5 blocker) (#269)
```

Arc = **5 PRs: #269, #275, #276, #274, #272** — exactly the expected set, within
the 3–6 window. HEAD `f2e57b9` at check start. `gh pr list --state merged`
confirms merge times: #269 14:29Z, #275 15:14Z, #276 15:35Z, #274 15:40Z, #272
18:01Z (all 2026-09-03).

**PR #277 (`a4f2dc8`, "Item 5: first `--enforce-canonical-run` pass results")
merged to `main` during this check's review cycle** — it is *not* in the
`f303d79..HEAD` arc (it branches from a later point), but it directly touches
this pass's central finding (the item-5 enforced pass) and this note's
CAPABILITY_CHECKLIST correction, so it is spot-checked here and this PR (#278)
was rebased onto `a4f2dc8`. #278 carries no checklist edit (§1).

Method (rule 14): every consequential claim re-checked against `git show`, a read
of the merged files, `/usr/bin/grep` over `runtime/`, targeted `unittest`
modules, and `python3 -m runtime.smoke`. No claim taken from a PR title / body /
review summary alone.

## 0. Situational awareness

- `python3 -m runtime.smoke` → **exit 0 at `f2e57b9`**.
- `python3 -m unittest tests.test_exp_b_skill_routing` → **3 OK**, numbers
  reproduce DEC-002 / the checklist **exactly**: `corpus_sha256`
  `2cff0e40…4565` (frozen), `selection_f1` 0.8667, `exact_cases` 19/25,
  `false_activation_cases` **0**, `selection_precision` 1.0, per-category
  DIRECT/PARAPHRASE/MULTI_SKILL/NO_SKILL/HARD_NEGATIVE **1.0**,
  VOCABULARY_SHIFT/AMBIGUOUS **0.0**. 6.9/S6 DONE is not regressed — no
  status-truth emergency.
- `python3 -m unittest tests.test_hcom_adapter tests.test_recovery_supervisor
  tests.test_harness_hcom_adapter` → **Ran 90 tests, OK** (~89 s foreground).
  The #20 blocker (`maps recovery-tick` dead against hcom 0.7.25) is cleared in
  code and under regression test.
- Each arc PR merged with an independent `work/reviews/pr-2NN-review-evidence.md`
  (`independent: true`): #269 (evidence committed in-PR, reviewer session
  `0156amnKLwucxFkwh136YLhT`), #275 / #274 / #272 zonu (`docs-reviewer-zonu`),
  #276 duro (`pr276-reviewer-duro`). Merges were `gh pr merge --squash` under
  the `BigCatMellow` account via the `gule` merge-runner seat (Mode A, session
  26) — consistent with the merge-authority rule (#266) and friction entry 7's
  runner-side gate.
- **Scoreboard unchanged — 17 / 12 / 6.** No arc commit touches
  `work/roadmaps/CAPABILITY_CHECKLIST.md` at all (`git show <c> --
  work/roadmaps/` empty for all five). Section 2 phases S1–S6 DONE, S7 NOT
  STARTED. **PR #277 (`a4f2dc8`, "Item 5: first `--enforce-canonical-run` pass
  results", merged to `main` during this check's review cycle)** advanced the
  H5 / 6.16 evidence prose and added an enforced-pass-results clause to all 7
  security-cluster rows — **no status flip** (verified against `origin/main`
  below). This PR was rebased onto `a4f2dc8` and now touches **no checklist
  file** — 2 files only (`FRICTION_LOG.md` + this note).

## 1. Per-PR verify column (rule 14)

| PR | What | Verified at `f2e57b9` | Status impact |
|----|------|-----------------------|---------------|
| **#269** `a6ad820` | Record + tolerate the hcom 0.7.25 `list --stopped` non-JSON defect. Part A folded: `HcomAdapter.list_sessions(include_stopped=True)` degrades to alive-only `hcom list --json` when `--stopped` output is not JSON. Review nits addressed in a follow-up commit (warn-once `logging.warning`; catch narrowed to `json.JSONDecodeError`; fail-closed tests). | Diff = `runtime/communication/hcom_adapter.py` (+`_parse_session_list` static, `_warned_stopped_nonjson` flag, JSONDecodeError-guarded fallback), `tests/test_hcom_adapter.py`, `work/coordination/FRICTION_LOG.md` (tool-gap entry), `work/notes/2026-09-03-hcom-list-stopped-nonjson-repair.md` (BLOCKING repair record). No `runtime/recovery/`, no `run_lineage.py`, no schema. `pr-269-review-evidence.md` present, `independent: true`, APPROVE, crux recorded: "option D unblocks the recovery-tick abort but not a routable `LEASE_EXPIRED` denial (option C required first)". 90-test targeted suite green here. | none (evidence prose — H5/6.16 "open PR #269" clause superseded by #277, see below) |
| **#275** `ea76854` | Session-24 FRICTION_LOG backlog — two dated entries (cross-agent fresh-clone contamination; coordinator hcom env leak into `maps recovery-tick`). | Diff = `work/coordination/FRICTION_LOG.md` (+33) + `work/reviews/pr-275-review-evidence.md` (+20). Both entries carry the file's 5-field shape; append-only respected. Phase-1 review finding (`class: race-condition` off-enum) fixed in-PR to `process-gap`. zonu APPROVE, `independent: true`. | none (coordination log) |
| **#276** `9a884c2` | Item 5 / option C (Part B) — `HcomAdapter._stopped_records_from_events()` synthesizes stopped-session records from the `hcom events` JSONL stream; the non-JSON `--stopped` fallback now returns `alive + events-derived stopped` (alive wins on name collision). `_STOPPED_EVENTS_LOOKBACK = 2000`. | Diff = `runtime/communication/hcom_adapter.py` (+151), `tests/test_hcom_adapter.py` (+78), `FRICTION_LOG.md` (+22), 2 impl notes, `pr-276-review-evidence.md`. `/usr/bin/grep` confirms `_stopped_records_from_events` (L218), `_STOPPED_EVENTS_LOOKBACK` (L30), `read_events(last=_STOPPED_EVENTS_LOOKBACK)` (L243), warn-once flag (L86/185/196), events merged only inside the `except json.JSONDecodeError` branch (L213). Helper wraps `read_events` in `except HcomError` → `[]` (never raises). Subagent `exit:idle` (`session: null`) events dropped. Existing option-D test kept; its call-sequence assertion loosened (an `events` call now follows the alive fallback — a real, justified contract change), behavioural assertions unchanged. Frozen regression test `test_list_sessions_include_stopped_reconstructs_from_events`. duro APPROVE, `independent: true`, test-the-test performed (`return []` → new test fails), 90-test suite green foreground. | none — but **CLOSES the #20 blocker** (the `maps recovery-tick` abort) |
| **#274** `4ca8af5` | `work/research/` reorg into topic folders (agent-harness / skills-and-tools / evaluation-and-reliability / security-and-authority) + routing README. | Diff = 5 new docs (+908), README `NAVIGATION — NOT ACTIVE AUTHORITY`, each note `RESEARCH — NOT ACTIVE AUTHORITY`. No `runtime/`, no roadmap, no coordination contract. zonu APPROVE, `independent: true` — all relative links resolve, no duplicate-truth. | none (research navigation) |
| **#272** `f2e57b9` | Pilot/MAPS_L conversation-derived architecture note packet — 8 docs under `work/notes/2026-09-03-pilot-memory-context/`. | Diff = 8 new docs, all self-marked non-authoritative; README defers repo-wide ownership to `INFORMATION_LIFECYCLE.md` / `work/README.md` / `AGENTS.md`; the Prime note is framed "MAPS_L should evaluate incorporating…", not authorize. zonu APPROVE, `independent: true`, programmatic link check, no second-contract language. | none (deferred design capture, issue #248) |

**Checklist status corrected by PR #277 (`a4f2dc8`), verified here (evidence
clause only, no status flip):** H5 and 6.16 both carried an "Updated 2026-09-03
(trajectory check #20)" clause reading the blocker as "**open** PR #269". PR
#269 merged 2026-09-03T14:29Z (`a6ad820`) and PR #276 (Part B / option C) merged
2026-09-03T15:35Z (`9a884c2`), both with independent review, and the
`maps recovery-tick` abort is verified cleared here (90-test suite green) — so
that clause was stale. **PR #277 (merged to `main` during this check's review
cycle) already corrected it:** both rows now record #276 (option C, superseding
the #269 tolerate approach) as landed, the first `--enforce-canonical-run` pass
as *run* 2026-09-03 (`work/notes/2026-09-03-item5-enforced-pass-results.md`), and
the result — 0 opened incidents / 0 denials via runbook §8 OPTION A (the synthetic
`bind-session` session was never a live hcom session, so `observe_silent_stops`
saw no live→stopped transition and opened no incident). **H5, 6.16, 6.22 all
stay IN PROGRESS** — a real `resume_denied` still needs the lineage-bootstrap
wiring (`work/notes/2026-09-02-lineage-bootstrap-wiring-scoping.md`, runbook §8
OPTION B). This note's PR (#278) was rebased onto `a4f2dc8` and drops its own
checklist edit — #277's clause is strictly more current. Verified: `git diff
origin/main -- work/roadmaps/CAPABILITY_CHECKLIST.md` is empty.

## 2. The #20 blocker is cleared — is that genuinely true?

**Yes.** #20 named one hard blocker on the 7-row security/harness cluster (6.4 /
6.5 / 6.16 / 6.22 / H5 / E4 / L6): `HcomAdapter.list_sessions(include_stopped=
True)` runs `hcom list --json --stopped --all`; hcom 0.7.25 ignores `--json` for
`--stopped` and emits human text; `json.loads` raised `HcomProtocolError` and
`RecoverySupervisor.observe_silent_stops` / `tick` /
`HcomSessionAdapter._session_records` call it unconditionally, so **all** of
`maps recovery-tick` was dead.

Re-verified at `f2e57b9`:

- Part A (#269): the `except json.JSONDecodeError` branch in `list_sessions`
  falls back to `hcom list --json` (alive-only). Narrowed catch — a structurally
  valid JSON payload that fails the type check still raises `HcomProtocolError`
  (not masked). Warn-once breadcrumb on the module logger.
- Part B (#276): `_stopped_records_from_events()` rebuilds stopped-session
  records from `hcom events` (JSONL default). `name → session_id` from the most
  recent status event carrying non-null `data.session`; stop signal from `life
  action:stopped` / `status new_status:inactive`; subagent `exit:idle` dropped.
  Synthetic record keys mirror the alive `hcom list --json` shape the recovery
  path reads — `pr-276-review-evidence.md` traces every downstream consumer
  (`_resolve_run_id`, `session_is_live`, `_find_by_session_id`, harness
  `_STATUS_MAP`) and confirms "no downstream change".
- Residual gap (documented, accepted): a session that started **and** stopped
  entirely outside the 2000-event (~6 h) lookback window still yields a record
  with no `session_id` → unresolved `run_id` — the same gap Part A already
  accepts, over a smaller exposure window.
- Tests: `tests.test_hcom_adapter` + `tests.test_recovery_supervisor` +
  `tests.test_harness_hcom_adapter` = **90 OK** foreground here.

**#276's LEASE_EXPIRED-vs-HOOK_DENIED reviewer verdict** (duro, item-8 flag):
the guard-veto path fires — `CanonicalRunGuard._require_live_claim` →
`_deny("LEASE_EXPIRED", …)` returns a `DENY` directive with `guard_code:
LEASE_EXPIRED` as an *annotation only*; `HarnessService._hook_block` maps any
`DENY` to `OperationResult.code = "HOOK_DENIED"`; `RecoverySupervisor`
`_CANONICAL_DENIAL_CODES = {"HOOK_DENIED", "APPROVAL_REQUIRED"}` → `action =
"resume_denied"`, `canonically_denied = True`, incident parked in the distinct
routable `denied` state. **Conclusion recorded by the reviewer: option C alone
is sufficient for the enforced pass to emit a routable `resume_denied` on
`LBW-EXERCISE-1`** once option C restores `session_id` so `_resolve_run_id`
binds the run.

## 3. Named new evidence

1. **The #20 blocker is resolved in one arc.** #269 (Part A) + #276 (Part B /
   option C) both merged 2026-09-03 with independent review; `maps recovery-tick`
   is reachable against the installed hcom again (90-test suite green here). The
   #18/#19 lineage-bootstrap deadlock is done (#258/#261); the control plane at
   `~/Projects/MAPS_Lean` carries real routable state (`LBW-EXERCISE-1`,
   lease-expired, EXPLICIT lineage). The route to DONE for the 7-row cluster now
   has exactly one step left: run the enforced `--enforce-canonical-run` pass,
   then the per-row HARD verification.

2. **The enforced pass ran — PR #277 (`a4f2dc8`) merged during this review
   cycle.** `work/notes/2026-09-03-item5-enforced-pass-results.md` records it:
   `maps recovery-tick --enforce-canonical-run --harness-project-id maps-lean
   --binding nava-worker-1=hcom-sess-nava-lbw-1` was run against the live
   `~/Projects/MAPS_Lean/.maps/`. Result: **0 opened incidents / 0 actions / 0
   routable bindings / 0 denials** (runbook §8 OPTION A). What it *did* achieve
   (first-time, real): `build_canonical_harness_service` composition
   instantiated by a production enforced pass (`HarnessService(...)` /
   `HookRegistry()` exercised outside a test); option C (#276) exercised on the
   production path (non-JSON `hcom list --stopped` fallback warn fired, `hcom
   events` reconstruction ran, no crash); `recovery.json`
   `last_live["hcom-sess-nava-lbw-1"] = false` recorded; task truth
   byte-identical before/after (`CanonicalRunGuard` READ_ONLY, no resume
   attempted). #277 also advanced the evidence prose on all 7 cluster rows — no
   status flip.

3. **The #276-review-vs-0-denials point is resolved, not a contradiction.**
   #276's reviewer (duro) concluded "option C alone is sufficient for a routable
   `resume_denied` on `LBW-EXERCISE-1`" — but that conclusion was **conditional
   on an incident opening with a resolvable `session_id`**. #277's evidence note
   §"Why 0 incidents / 0 denials": `nava-worker-1` / `hcom-sess-nava-lbw-1` was
   never a real live hcom session (synthetic `maps run bind-session`, #261), so
   the first `last_live = false` observation is a **baseline, not a live→stopped
   transition** — `observe_silent_stops` opens no incident, `tick()` has nothing
   reprocessable, `_resolve_harness_binding` / `CanonicalRunGuard.__call__` never
   run. Lineage *is* resolvable read-only (`resolve_session_run(...)` →
   `RUN-6d536476…`), so option C + #261's link do work together — a real
   `resume_denied` just needs a genuinely-live-then-stalled session with an
   `EXPLICIT` `run_session_links` row, i.e. the lineage-bootstrap wiring
   (runbook §8 OPTION B, `work/notes/2026-09-02-lineage-bootstrap-wiring-scoping.md`,
   out of Ask #1 scope). **Reconcile item CLOSED this pass — no #22 deferral.**

4. **No status moved.** Scoreboard 17/12/6, unchanged. Four of the five arc PRs
   (#272/#274/#275, plus #269's record half) are docs / research / friction /
   tolerate-only with explicit "no status flip"; #276 clears a blocker without
   itself advancing a row; #277 (the enforced-pass results, merged during this
   review cycle) advanced evidence prose on 7 rows with an explicit "NO status
   flip" — a real `resume_denied` (the H5/6.16/E6 exit criterion) remains
   unreached.

## 4. Trajectory action: **CONTINUE**

Not REPRIORITIZE — the item-5 dependency chain **shortened** this arc: the one
PR #20 inserted (#269) landed, plus Part B #276, plus the first enforced pass
itself ran (#277). Nothing about the roadmap's item ordering is wrong. Not STOP
— the #20 STOP-watch was "PR #269 stalled AND the enforced pass has not run AND
no new ask-independent slice"; **#269 merged and the enforced pass ran**, so the
condition is firmly not met. The next lever (a real `resume_denied`) is already
scoped as runbook §8 OPTION B / `work/notes/2026-09-02-lineage-bootstrap-wiring-scoping.md`.

Reasoning:

1. **The arc shipped cleanly and did real work.** 5 PRs, each independently
   reviewed; the #20-named hard blocker on a 7-row cluster is resolved and under
   regression test in a single arc.

2. **The Ask #1 sequence is complete.** Operator GO (decision batch item 5,
   #265) → adapter defect fixed (#269 + #276) → first `--enforce-canonical-run`
   pass run and evidenced (#277, runbook §8 OPTION A). The composition root and
   option C are now exercised by a real production enforced pass.

3. **Runway is healthy:** runbook §8 OPTION B (lineage-bootstrap wiring for a
   genuinely-live-then-stalled session — the path to a real `resume_denied`,
   already scoped in `work/notes/2026-09-02-lineage-bootstrap-wiring-scoping.md`)
   → then the 7-row HARD verification (6.4 / 6.5 / 6.16 / 6.22 / H5 / E4 / L6)
   against `work/notes/2026-09-02-ask1-control-plane-runbook.md` §6 per-row unmet
   conditions → 6.21 slices past 3b → 6.4 / 6.5 / E4 each have a named next step
   independent of the pass.

**No CUT SCOPE / ADD.** The roadmap points at DONE. This PR carries no checklist
edit — #277 (`a4f2dc8`) already landed the H5/6.16/7-row evidence advance during
this review cycle; the friction-log dispositions (§6) are the only program-state
change here.

## 5. Tenth-Seat / §7 duty (`TENTH_SEAT_REVIEW.md` §2 Trigger 2, §7)

Trigger 2 is **armed** (passes #17, #18, #19, #20 each found a substantive
finding).

**It does not fire this pass.** §2–§3 are a substantive finding: the #20-named
blocker on a 7-row cluster is *resolved* this arc (#269 + #276, verified in
code + 90 tests), the first `--enforce-canonical-run` pass *ran* (#277), and the
checklist's H5 / 6.16 "open PR #269" prose (stale once #269/#276 merged) was
corrected by #277, verified against `origin/main` here. A pass that verifies a
blocker cleared, an enforced pass run, and a program-truth correction landed is
not "nothing substantive". No @mika pre-flag for a Tenth-Seat sub-dispatch, and
none is initiated.

`TENTH_SEAT_REVIEW.md` §7 "signs this has gone wrong", read against this and the
prior passes:

- *"same conclusion every pass regardless of evidence"* — the picture keeps
  moving on evidence: #18 "unscoped code change" → #19 "code merged, exercise in
  flight" → #20 "exercise landed, batch answered, one adapter defect (PR #269)
  between here and the enforced pass" → **#21 "defect fixed (#269 + #276), first
  enforced pass RAN (#277) with 0 denials (runbook §8 OPTION A); the next lever
  is the OPTION B lineage-bootstrap wiring for a real `resume_denied`"**.
- *"verdict drifting toward reassurance"* — this pass does not gloss the 0-denial
  result: it records that the pass reached OPTION A only (composition + option C
  instantiated, but `CanonicalRunGuard.__call__` never fired because no incident
  opened for the synthetic bind), and that H5/6.16/6.22 correctly stay IN
  PROGRESS with a real `resume_denied` still unreached. The #276-review point is
  reconciled in §3.3 (conditional on an incident opening — none did), not
  deferred.
- *"no one has run the full check"* — arc range-derived (5 PRs, clean base
  confirmed `git rev-parse origin/main`); all five read at file level; EXP-B +
  the 90-test hcom/recovery suite re-run here; the blocker traced through
  `list_sessions` → `_stopped_records_from_events` → the guard-veto chain in the
  #276 review; #277's evidence note read in full and cross-checked against the
  runbook §8.
- *"challenges detail, never a foundational claim"* — §2/§3 are foundational
  (the route to DONE for a 7-row cluster and what the first enforced pass
  actually achieved vs. what #243 pictured), not a row-label quibble.
- *"the same agent keeps drawing the role"* / *"reports accumulate and nothing
  reopens"* — no minority report exists to have accumulated; Trigger 2 negative
  this pass in judgment.

No Tenth-Seat sub-agent dispatched.

## 6. Friction-log consumption

`work/coordination/FRICTION_LOG.md` walked in full (12 entries + follow-up
lines). Entries 1–4 (self-clear drop; coordinate-via-helper-lanes;
context-rotation checkpoint; triage-loop-was-procedure-only) are `verified:`
END-TO-END / VERIFIED and closed — no re-open. Open / behavioral items:

| Entry | `verified:` / countermeasure | Disposition this pass |
|-------|------------------------------|-----------------------|
| **orchestrator tool-use burned context** (2026-08-31) | `n/a (behavioral)`, `countermeasure: none mechanical` | **CLOSED.** 10th consecutive no-recurrence arc (passes #10–#20 each recorded clean; this arc + trajectory lane used scoped `git show` / `git show --stat` / `/usr/bin/grep` / `sed -n` line ranges / `Read` offset+limit — no 100KB+ dumps, no whole-doc re-reads). The playbook's rule is explicit: *a behavioral "watch-if-it-recurs" entry with 3 clean arcs is CLOSED, not carried a 4th time* — this is far past that. Follow-up line appended marking it closed; if the pattern recurs in a future coordinator session it is a fresh entry (with the scratchpad-orientation-digest countermeasure the entry already sketches), not a re-open. |
| **stale slice-boundary NonGoalTests asserts** (2026-09-01) | `END-TO-END (×4)` | **Consumed — no clean test case this arc.** None of #269–#276 was a scope-expanding `_select_skills` / `context_builder` slice with `NonGoalTests` substring-assert risk. #276 loosened its *own* option-D `test_list_sessions_include_stopped_survives_nonjson_stopped_output` call-sequence assertion in the same PR (tail-pinned → index-ordered, a justified contract change; behavioural asserts unchanged) — no CI-red boundary trip. Discipline holding (2nd post-discipline arc with no trip). Stays open (close condition: 3 clean post-discipline arcs, or a 3rd CI-red trip re-opens the mechanical-safeguard discussion). Follow-up line appended. |
| **coordinator merge marks treated as merge authorization (recurrence)** (2026-09-03) | `verified: UNVERIFIED` | **Consumed — pass 1 of ≤3; no 3rd occurrence.** This is the entry's first trajectory pass since it landed (session 25). All five arc merges ran through the `gule` merge-runner seat under Mode A (session 26 handoff: `gule` merges only on an explicit operator PR-number instruction; coordinator marks alone are insufficient). No coordinator-mark-only merge occurred this arc. The runner-side gate's *refusal* behaviour cannot be mechanically verified from a clone — that needs a live observation of `gule` blocking or quoting an operator authorization. Stays `UNVERIFIED`, pass 1 of the N=3 ladder; **not** an escalation this pass. Follow-up: #22 checks (a) `gule` was observed enforcing the gate, (b) still no 3rd occurrence. |
| **hcom 0.7.25 `list --stopped` ignores `--json`** (2026-09-03) | defect reproduced; Part A test green; Part B was open | **CLOSED.** Part A merged (#269, `a6ad820`) + Part B / option C merged (#276, `9a884c2`), both with independent review (`pr-269` / `pr-276` evidence, `independent: true`). Defect tolerated (JSONDecodeError-narrowed fallback + warn-once) and lineage rebuilt from the `hcom events` stream; `tests.test_hcom_adapter` + `tests.test_recovery_supervisor` + `tests.test_harness_hcom_adapter` = 90 OK re-run here. Residual (session outside the 2000-event lookback → unresolved `run_id`) documented and accepted, smaller exposure than Part A alone. The route-to-DONE consequence (§1–§3) is recorded here; the H5/6.16 evidence prose was corrected by #277 (`a4f2dc8`), verified against `origin/main`. Follow-up line appended marking closed; the remaining item-5 step (a real `resume_denied` via runbook §8 OPTION B) is tracked on H5/6.16, not this entry. |
| **cross-agent scratchpad / fresh-clone contamination** (2026-09-03) | `n/a (behavioral, root cause unresolved)`, no mechanical safeguard | **Consumed — pass 1; no recurrence.** First trajectory pass since it landed (#275). This trajectory lane cloned to a unique `/tmp/traj21-$$/MAPS_Lean` path per the dispatch discipline and the clone landed **clean** — `git rev-parse origin/main` matched HEAD, no foreign staged files, no stray `main` tip (a positive data point vs. the session-24 observation). Stays open (behavioral, root cause unresolved; a 3rd occurrence *under* the unique-path discipline scopes an investigation into clone/worktree path allocation). Follow-up line appended. |
| **coordinator hcom env leaks into `maps recovery-tick`** (2026-09-03) | `n/a (behavioral)` | **Consumed — pass 1; countermeasure exercised.** First trajectory pass since it landed (#275). Countermeasure = `env -i` in the item-5 run recipe (session-24 handoff). #277's evidence note shows the enforced pass was run exactly under `env -i HOME=$HOME PATH=$PATH HCOM_DIR="$PWD/.hcom"` and the tick observed the target `.maps/` routable state (`recovery.json` `last_live["hcom-sess-nava-lbw-1"]` recorded, no coordinator-session context leaked) — the recipe worked as designed on its first real use. Stays open (behavioral, one data point). Follow-up line appended. |

**No entry is `UNVERIFIED` across N=3 consecutive passes** — the merge-marks
entry is at pass 1, the two #275 behavioral entries at pass 1. **No auto
operator-escalation item from the friction log this pass.**

(The committed `FRICTION_LOG.md` follow-up lines — reviewed and approved by tuba
on the pre-rebase head — carry a parenthetical noting the enforced-pass results
PR "was not open at check #21"; PR #277 (`a4f2dc8`) merged during the review
cycle, so that timing note is superseded by this note's §2–§3 and §6 table. The
dispositions themselves (CLOSED / open pass-1) are unchanged and correct.)

New friction this arc: **none captured.** The arc's five PRs shipped cleanly
with no observed stall, race, or contract break in the trajectory lane; #269's
review round-trip (nits applied in a follow-up commit, evidence re-bound) is
already covered by the "fix commit lands on top of review-evidence" entry
(2026-09-03) — its follow-up asks #21 to note whether a **3rd** occurrence lands;
**#269 is arguably a 3rd** (reviewer nits applied post-record), but the record
commit / evidence commit ordering held (evidence bound to the final head
`2f46281`, no escaped stale bind), so it does **not** trip that entry's re-open
condition (which requires an *escaped* stale bind). Noted here, no re-open.

## 7. Operator-decision / escalation items

**None require operator action this pass.** For visibility:

1. **The first `--enforce-canonical-run` pass ran and is evidenced** (#277,
   `a4f2dc8`, `work/notes/2026-09-03-item5-enforced-pass-results.md`) — runbook
   §8 OPTION A, 0 incidents / 0 denials, composition + option C instantiated on
   the production path. **No STOP-watch** — Ask #1's sequence is complete. The
   next lever toward a real `resume_denied` (H5/6.16/E6 exit criterion) is
   runbook §8 OPTION B, already scoped in
   `work/notes/2026-09-02-lineage-bootstrap-wiring-scoping.md` — an
   ask-independent slice, not an operator decision.

2. **The #276-review-vs-0-denials point is resolved** (§3.3): duro's conclusion
   was conditional on an incident opening; none did for the synthetic
   `bind-session` case (no live→stopped transition). Closed this pass, no #22
   deferral.

3. **`gule` runner-side merge-authority gate** (friction entry 7) is
   `UNVERIFIED` — needs a live observation of the seat enforcing it. Pass 1 of
   N=3; #22 and #23 close it or it auto-escalates at #24.

## 8. Full suite

Foreground evidence run at `f2e57b9` + this PR's doc/checklist edits (which
touch no `runtime/` or `tests/` code): `python3 -m runtime.smoke` exit 0;
`tests.test_exp_b_skill_routing` 3 OK (f1 0.867, numbers reproduce DEC-002);
`tests.test_hcom_adapter` + `tests.test_recovery_supervisor` +
`tests.test_harness_hcom_adapter` **90 OK**. This PR (#278) touches no `runtime/`
or `tests/` code — 2 files, `FRICTION_LOG.md` + this note. `python3 -m unittest
discover -s tests` (CI `test`) is delegated to CI on this PR — it is heavily
I/O-bound in this environment (the "dispatched worker stalls on its own full
suite" friction), and each arc PR (plus #277) already merged green.

## 9. Recorded for the next pass (check #22)

- **Arc anchor for #22:** the squash commit of *this* PR (#21). NOTE: #277
  (`a4f2dc8`, first enforced-pass results) merged *during* this check's review
  cycle — it is **not** in the #21 arc (`f303d79..HEAD` = #269/#275/#276/#274/
  #272) but is spot-checked here; #22's arc (`<#21 squash>..HEAD`) picks up #277
  and #278.
- `python3 -m runtime.smoke` exit 0 at `f2e57b9`; EXP-B 3 OK, f1 0.867,
  `false_activation_cases` 0 — a regression here is a status-truth emergency
  (6.9/S6 are DONE).
- Scoreboard **17 / 12 / 6** — unchanged (#277 advanced 7-row evidence prose, no
  status flip).
- Tenth-Seat Trigger 2 armed (#17–#21 all found something); **did not fire**
  (§5). Re-arms for #22: a genuinely clean #22 fires it — flag @mika BEFORE
  dispatching a Tenth-Seat sub-agent, then write
  `work/reviews/trajectory-22-minority-report.md`.
- **Next 3 (verify at #22):**
  1. **Runbook §8 OPTION B** (`work/notes/2026-09-02-lineage-bootstrap-wiring-scoping.md`)
     — is the lineage-bootstrap wiring for a genuinely-live-then-stalled session
     scoped into a slice / dispatched? This is the path to a real `resume_denied`
     and the H5/6.16/6.22/E6 exit criterion.
  2. **7-row HARD verification** (6.4 / 6.5 / 6.16 / 6.22 / H5 / E4 / L6) against
     `work/notes/2026-09-02-ask1-control-plane-runbook.md` §6 per-row unmet
     conditions — only once OPTION B produces a real denial. Confirm no
     impl/review agent ran an `--enforce-*` pass autonomously; #277's pass was
     coordinator-run and evidence-noted.
  3. **6.21** — any slice past 3b (composite verdict recording)? Still IN
     PROGRESS is correct until then.
- **STOP-condition watch for #22:** if runbook §8 OPTION B has not been scoped
  into a slice by #22 **and** no other ask-independent security-cluster slice is
  identified — that is a genuine STOP-condition on the security cluster; #22 says
  so plainly. (The #20/#21 "PR #269 stalled" STOP-watch is discharged — #269
  merged, the enforced pass ran.)
- **Friction:** entries 1–4 closed; **orchestrator-context-burn now CLOSED**
  (10th clean arc); **hcom-`list --stopped` now CLOSED** (#269 + #276 landed,
  enforced pass ran #277); merge-marks entry UNVERIFIED pass 1 of ≤3; two #275
  behavioral entries (fresh-clone contamination; hcom env leak — recipe
  exercised on #277's pass) consumed pass 1, no recurrence.

## Resume prompt

You are running roadmap trajectory check #22 for MAPS_Lean. Follow
`playbook/ROADMAP_TRAJECTORY_CHECK.md` (5-step + friction-log consumption) and
`playbook/TENTH_SEAT_REVIEW.md` §7 (read it before recording any clean result).
Fresh clone to a UNIQUE path (`git clone <repo> /tmp/traj22-$$/MAPS_Lean`);
`git fetch origin main`; verify `git rev-parse origin/main` matches your base
(check #20 was tripped by a stray local `main` tip). Never touch
`~/Projects/MAPS_Lean` or `.maps/`; do NOT run `maps recovery-tick`.

Anchor: `git log --oneline --grep='Roadmap trajectory check' main | head -1` →
the check-#21 squash; then `git log --oneline <that>..HEAD`, check every line.

Method (rule 14): no claim from a PR title/body/review summary; re-verify against
`git show`, merged code, `/usr/bin/grep` over `runtime/`, targeted `unittest`
modules foreground (full suite is CI's; ~7–8 s/test). `python3 -m runtime.smoke`
must exit 0. `python3 -m unittest tests.test_exp_b_skill_routing` must stay 3 OK
at f1 0.867, `false_activation_cases` 0 (6.9/S6 are DONE — a regression is a
status-truth emergency).

Context: check #21 confirmed #269 + #276 cleared the hcom `list --stopped`
blocker and **PR #277 (`a4f2dc8`) — the first `--enforce-canonical-run` pass
results — merged during #21's review cycle** (runbook §8 OPTION A: 0 incidents /
0 denials; composition root + option C instantiated on the production path;
`CanonicalRunGuard` never fired because the synthetic `bind-session` opened no
incident; #276's "option C sufficient for a routable `resume_denied`" was
conditional on an incident opening — resolved, not a contradiction). #277
advanced 7-row evidence prose, no status flip. Scoreboard 17/12/6.

Specifically check: (a) **Runbook §8 OPTION B**
(`work/notes/2026-09-02-lineage-bootstrap-wiring-scoping.md`) — the
lineage-bootstrap wiring for a genuinely-live-then-stalled session, the path to
a real `resume_denied` — has it been scoped into a slice or dispatched? (b) If
OPTION B produced a real denial → verify 6.4 / 6.5 / 6.16 / 6.22 / H5 / E4 / L6
(7 rows) HARD against `work/notes/2026-09-02-ask1-control-plane-runbook.md` §6
before any flip; confirm no impl/review agent ran an `--enforce-*` pass
autonomously. (c) Re-derive the scoreboard — should be 17/12/6 unless OPTION B
advanced a row. (d) **Trigger 2 re-armed** (#17–#21 all found something) — a
genuinely clean #22 fires it: flag @mika BEFORE dispatching a Tenth-Seat
sub-agent. (e) Friction: `gule` runner-side merge-authority gate (UNVERIFIED,
pass 2 of ≤3 — needs a live observation of the seat enforcing it); the two #275
behavioral entries (fresh-clone contamination; coordinator hcom env leak — pass
2).

**STOP + flag @mika if:** runbook §8 OPTION B has not been scoped into a slice
by #22 AND no other ask-independent security-cluster slice is identified
(STOP-condition — record it plainly); a status claim is wrong in a way that
changes the route to DONE; the trajectory action would be STOP or an
envelope-leaving REPRIORITIZE; §7 signals the check has gone shallow; or before
dispatching the Tenth-Seat sub-agent.

Deliverable: one PR, branch `analysis/roadmap-trajectory-check-22`, adding
`work/notes/2026-XX-XX-roadmap-trajectory-check-22.md` (+ friction follow-up
lines, + minority report iff Trigger 2). Update `CAPABILITY_CHECKLIST.md` ONLY
if a status genuinely moved (hard evidence) or a clause is provably wrong — flag
@mika before any status flip. Two-phase review: do NOT push your own review
evidence, do NOT spawn your own reviewer — report the PR number + head SHA to
your coordinator when open + CI `test` green. Author email
`201203536+BigCatMellow@users.noreply.github.com`.
