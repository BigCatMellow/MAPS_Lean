# Roadmap trajectory check #26 — 2026-09-07

Twenty-sixth pass. Independent analysis lane (`traj26-sofa`, dispatched by
coordinator `nipe`, session 38). Method per
`playbook/ROADMAP_TRAJECTORY_CHECK.md` (5-step + friction-log consumption +
Emergence pass) and `playbook/TENTH_SEAT_REVIEW.md` §7.

**Trajectory action: `CONTINUE`.** No roadmap/status claim is wrong in a way
that changes the route to DONE. Scoreboard moved this arc: **19 / 10 / 6**
(was 18/11/6) — row 6.16 flipped IN PROGRESS → DONE on a real, independently
reviewed worktree-binding-guard exercise (#303/#304). Re-derived by direct
count of the §7 6.x table, not copied. Single earned flip, already landed in
merged #304 — not an edit made by this pass.

## Setup / base verification

- Fresh clone (`/tmp/traj26-work`, distinct from the coordinator checkout at
  `~/Projects/MAPS_Lean`, never touched for writes).
  `git rev-parse origin/main` == `HEAD` ==
  **`bb65efad11b910132c18c277778f065c9f787f33`**. `git status --porcelain`
  empty at clone.
- Anchor: `git log --oneline --grep='Roadmap trajectory check' main | head -1`
  → `cbc1846` ("Roadmap trajectory check #25 … (#299)").
- Arc `git log --oneline cbc1846..HEAD` = exactly **14 PRs**, merge order
  #300, #301, #303, #304, #305, #306, #307, #308, #309, #310, #311, #312,
  #313, #314. `git log --oneline cbc1846..HEAD | grep -cE '\(#[0-9]+\)$'` →
  **14** — matches this write-up's coverage. (#302 is deliberately excluded —
  operator split it at session 37; not in this arc.)

## 0. Situational awareness

- `python3 -m runtime.smoke` → **exit 0**.
- `python3 -m unittest tests.test_exp_b_skill_routing` → **3 OK**,
  `corpus_sha256` `2cff0e40…4565` (frozen, unchanged), `selection_f1`
  0.8666…, `exact_cases` 19/25, `false_activation_cases` **0**,
  `selection_precision` 1.0. 6.9/S6 DONE not regressed — no status-truth
  emergency.
- Targeted foreground re-run of the modules this arc's PRs touch:
  `tests.test_check_stale_no_caller_docstrings`, `tests.test_context_delivery`,
  `tests.test_hcom_adapter`, `tests.test_documentation_sprawl`,
  `tests.test_check_review_evidence` → **88 OK**.
- Full suite delegated to CI's `test` check (not backgrounded, not polled).

## 1. Re-verify reality (arc = 14 PRs)

| PR | What it claims | Verified |
|---|---|---|
| **#300** (`3b8e343`) | Housekeeping: formally captures `IDEA-fe6c0f0f` (rebase replays commits so `check_review_evidence.py`'s is-ancestor revalidation check never fires on this repo's rebase-based merge-prep), and adds `work/notes/2026-09-05-dec003-known-bugs-followup.md` documenting 2 bugs found-not-fixed during #298's exercise (HCOM_DIR env override; tag-prefix/bare-name `run_id: null` mismatch). | `git show --stat`: 3 files, +120, all under `work/`. No `runtime/` touch. Idea record + bug note read in full — both accurate to what #298's results note recorded. Independent review `pr-300-review-evidence.md` APPROVE. |
| **#301** (`1afabce`) | Adds a "no-hype / earned-agreement" invariant to `AGENTS.md` (+7 lines). | `git show --stat`: 2 files, +15 (`AGENTS.md` +7, evidence +8). Read the added text — a prose invariant, no mechanism, no byte-budget breach (test threshold untouched). Independent review (`luno`) APPROVE. |
| **#303** (`371361a`) | DEC-003 row 6.16: first production-path firing of `CanonicalRunGuard._require_bound_worktree`. A `--require-worktree-binding --base-revision <sha>` worktree-bound run stalled and resumed via `recovery-tick --enforce-canonical-run` from a *different* worktree identity → `RUN_WORKTREE_MISMATCH` (linked `git worktree`) / `RUN_WORKTREE_UNAVAILABLE` (non-git dir), both as `resume_denied` / `HOOK_DENIED`. Frozen as `CASE-db2717314e8ec548…456e813`. Also documents Finding 0 (`--require-worktree-binding` inert without `--base-revision`). | `git show --stat`: 3 files, +777, all under `work/`. Regression case file present (347 lines) and routed. Exercise note read in full — the `guard_code` values are pinned by a *direct* `CanonicalRunGuard` repro (`--repo-root` varied) + a check-ordering inference, not read off `recovery-tick`'s own JSON (which flattens to `HOOK_DENIED`) — this limitation is stated honestly in the note and carried into the row text as Caveat A. Independent review `luna` APPROVE (`pr-303-review-evidence.md`; squash carries `reval-neso`'s zero-diff revalidation stub, original APPROVE by `luna` referenced). |
| **#304** (`f3b25b3`) | `CAPABILITY_CHECKLIST.md` row 6.16: IN PROGRESS → DONE, per #303. New `work/tasks/require-worktree-binding-needs-base-revision.md` scoping Finding 0. | `git show f3b25b3 -- work/roadmaps/CAPABILITY_CHECKLIST.md`: **exactly one row changed** (6.16 Status `IN PROGRESS`→`DONE`, dated 2026-09-06 update appended, prior history preserved, Caveats A+B kept in the row text per this row's twice-walked-back full-disclosure practice). No other row, no `runtime/` change. Independently re-counted the §7 6.x table Status column here (see §2). Review `lato` **APPROVE with merge-ordering condition** ("#303 must land first") — condition satisfied (#303 merged ahead). A reviewer-articulated condition = Trigger 1 does not apply (§6). |
| **#305** (`61ad8d7`) | Design-only note: a bounded production call site for `HarnessService.stop()` (6.4). Confirms zero production callers on `origin/main`; proposes the `canonical_denial_persistent` terminal branch in `RecoverySupervisor.tick()`, a default-off `--terminate-denied-sessions` opt-in. | `git show --stat`: 2 files, +396, nothing under `runtime/`. Zero-caller claim spot-checked: `/usr/bin/grep -rn "\.stop(" runtime/` shows no production `HarnessService.stop()` call pre-#306. Independent review APPROVE. |
| **#306** (`0996f70`) | 6.4: adds the single bounded default-off `.stop()` call from #305's design in `RecoverySupervisor.tick()`, gated behind `--terminate-denied-sessions` (requires `--enforce-canonical-run`). Explicitly **does NOT run the first-exposure exercise**; does not touch `CAPABILITY_CHECKLIST.md`. | `/usr/bin/grep`: `runtime/cli.py:358` flag, `:1010` the `requires --enforce-canonical-run` guard, `runtime/recovery/supervisor.py:280` `_maybe_terminate_denied_session`, `:668` its call site, `runtime/recovery/production.py:435` the plumbed kwarg. Row 6.4 **correctly NOT flipped** — call site exists, no exercise. Independent review APPROVE. |
| **#307** (`17a6679`) | 6.22 design-only note (mirror of #305): `HarnessService.send()` has zero production callers, `MemoryProvenanceGuard`'s `BEFORE_SEND` has never fired. Flags to coordinator that there is **no** bounded organic call site (larger-than-a-follow-up, stop condition #2). | `git show --stat`: 2 files, +536, nothing under `runtime/`. Independent review (original `kava`, revalidated `reval-neso`) APPROVE. |
| **#308** (`7aefd62`) | `flow start`: `--require-worktree-binding` now fails loud (`WORKTREE_BINDING_REQUIRES_BASE_REVISION`, no run persisted) without `--base-revision` — closes Finding 0 (the worktree-identity block in `create_run_manifest` was nested under `if base_revision is not None:`, so the flag was a silent no-op). `--help` rewritten. 2 new regression tests. | `git show --stat`: `runtime/cli.py`, `runtime/state/integrity.py`, `tests/test_execution_integrity.py`, task doc, evidence. `tests.test_execution_integrity` in the 88-OK targeted run. `reval-neso`'s evidence summary documents the non-trivial rebase (cli.py also touched by #306) and the patch-content-identical verification — a real diff-based revalidation, not is-ancestor (see §4.2, `IDEA-fe6c0f0f`). Original review `vima` APPROVE. |
| **#309** (`f57b475`) | DEC-003 known-bug 2: live repro (main @ c958cf6, hcom 0.7.25) confirming `hcom list --json` name is tag-prefixed while `events`/`list --stopped`/`batch_launched` are bare, so option-C `_stopped_records_from_events` keys on the bare name → dedup never fires for a tagged agent + `_resolve_run_id` misses → `run_id: null`. Docs only (shaped task contract + repro note). | `git show --stat`: 3 files, +427, all `work/`. No `runtime/` change (this PR is confirm+scope only; the fix is #313). Independent review `veki` APPROVE. |
| **#310** (`23ded5a`) | 6.22: `maps run send-context <run_id>` — first real `BEFORE_SEND` firing path. New `runtime/context_delivery.py::render_context_send_payload` (LOAD-only embedding), `runtime/harness/binding_resolution.py` (extracts `_resolve_harness_binding` body verbatim, rule 12), CLI subcommand default-off (no send, byte-identical dry run) / `--deliver-context` routes exactly one guarded send. Fail-closed on every branch. `tests/test_context_delivery.py`. **No exercise, no checklist row flip.** | `/usr/bin/grep`: `runtime/context_delivery.py:194`, `runtime/cli.py:181` the subparser, `runtime/harness/binding_resolution.py`. `tests.test_context_delivery` in the 88-OK run. Row 6.22 **correctly NOT flipped**. Original review `ledo` (found the #311 defect — see below), revalidated. |
| **#311** (`fd74f50`) | Hardens `scripts/check_stale_no_caller_docstrings.py` (rule 20, **3rd occurrence** of the stale-no-caller pattern; memory `feedback_stale_no_production_caller_docstrings`). `_symbol_for` did `token.split(".")[-1]` — dropped the class prefix, so `HarnessService.send()` resolved to bare `send` and matched every `.send(` in `runtime/`; with the blanket noqa #310 added, the check went blind and missed the real first caller `service.send(...)` in `runtime/cli.py`. Fix: keep the class on dotted symbols, match only receivers that plausibly name an instance. | `/usr/bin/grep -n`: `scripts/check_stale_no_caller_docstrings.py:89` `_symbol_for` now returns `(symbol, receiver_class)`, `:120` `parts = token.split(".")` keeps the class, `:245` the caller passes `receiver_class` through. `tests.test_check_stale_no_caller_docstrings` in the 88-OK run. Independent review `kela` APPROVE. **Rule-20 note: this is the 3rd occurrence and the fix is a *strengthening of the existing CI guard*, not another instruction — correct escalation.** |
| **#312** (`66787fd`) | DEC-003 bug 1 design note: `HCOM_DIR` vs `--hcom-dir` precedence (shell `HCOM_DIR` silently overwritten by `HcomAdapter.environment()`). 5 options, recommends **Option C** (explicit flag > inherited `HCOM_DIR` > `.hcom`, warn-once on resolved-path conflict). Operator product-behavior ruling required; docs only. | `git show --stat`: 2 files, +330, all `work/`. Per session-37 handoff the operator **already agreed Option C** — the fix PR is now unblocked (not in this arc). Independent review APPROVE. |
| **#313** (`9d73a6d`) | DEC-003 bug 2 **fix B**: normalize the tagged/bare match down to `base_name`. `_stopped_records_from_events` synthetic records carry `base_name`; option-C dedup compares on `name` AND `base_name`; new `supervisor._resolve_session_record` (exact `name` first, else single-candidate `base_name` fallback, two-collision → unresolved `{}`). Also softens an ASSUMED rationale in #309's repro note per `veki`'s nits. | `/usr/bin/grep -n`: `runtime/recovery/supervisor.py:72` `_resolve_session_record`, `:95-96` the `base_name` fallback with the endswith-`"-"+base_name` guard, `:390`/`:403` routed through it; `runtime/harness/adapters/hcom.py` `base_name`. `tests.test_hcom_adapter` in the 88-OK run. Original review + revalidation APPROVE. |
| **#314** (`bb65efa`) | Mirrors #308's corrected `--require-worktree-binding` / `--base-revision` `--help` wording into `runtime/integrity/cli.py`'s `run-create` subcommand (shares the fixed code path, kept stale strings). **No behavior change.** | `git show --stat`: `runtime/integrity/cli.py` +11/-2, evidence +6. Diff is help-string text only. Independent review `toto` APPROVE. |

All 14 PRs have an independent review-evidence file under `work/reviews/`
(`pr-300` … `pr-314`), each `independent: true`. The squash-merged tree
carries `reval-neso`'s zero-diff revalidation stubs (the session-37 batch
pipeline); the original substantive reviewers are named in each stub's
`summary` (`luna`, `lato`, `luno`, `kava`, `vima`, `veki`, `ledo`, `kela`,
`toto`, …) — **no reviewer is this pass's author; no self-review observed.**
Minor evidence-trail note: the pre-squash substantive review bodies are not in
`main`'s tree, only the revalidation stubs — consistent with the zero-diff
tier design, not a divergence, but recorded for the next pass.

## 2. What changed (name it)

- **Row 6.16 (Git worktree isolation / E6) is DONE — a real, earned flip,
  the first scoreboard movement since the 6.5 flip at #25.** The
  worktree-binding seam (`_require_bound_worktree` / `RUN_WORKTREE_MISMATCH`)
  fired on the real `build_canonical_harness_service` → `HarnessService.resume`
  → `BEFORE_RESUME` path for a genuinely worktree-bound run (#303),
  independently reviewed (`luna` APPROVE), flipped in a boundary-clean
  one-row PR (#304, `lato` APPROVE w/ satisfied merge-order condition).
  Confirmed by direct re-read of the row diff and an independent re-count of
  the §7 table (§below), not the commit message. The row keeps two honest
  caveats (guard_code inferred not field-read; mismatch induced via
  `--repo-root` not organic supervisor operation) — neither withholds DONE
  because the gate is *the guard firing on the enforced path*, which it
  demonstrably does.
- **Scoreboard 18/11/6 → 19/10/6**, re-derived by direct count of the §7 6.x
  table Status column: **19 DONE / 10 IN PROGRESS (9 + 1 "evaluation-only, by
  design") / 6 NOT STARTED = 35 rows** (unchanged set). Only 6.16 moved.
  Reported to the coordinator (`nipe`) per #25's standing instruction (e) —
  this is a flip already landed in merged #304, recorded accurately here, not
  an edit by this pass.
- **The harness-enforcement cluster's remaining 2 rows (6.4, 6.22) each got a
  production call site this arc but NOT an exercise** — #306 wires a default-off
  `HarnessService.stop()` call behind `--terminate-denied-sessions`; #310
  wires `maps run send-context` for the first `BEFORE_SEND` path. Both
  correctly left IN PROGRESS (no checklist edit). **New trajectory
  observation (see §4.1):** the "design note → call site → deferred exercise"
  pattern is now spread across 2–3 PRs per row with the exercise never
  landing, while dead default-off code accretes. 6.16 by contrast took an
  actual exercise (#303) to flip. Worth watching that 6.4/6.22 do not sit
  indefinitely one-exercise-away the way the cluster did pre-#298.
- **DEC-003's two known bugs are converging fast**: bug 2 (tag-prefix/bare-name
  `run_id: null`) is **fixed** (#309 confirm/scope → #313 fix B, real
  `runtime/` change + tests); bug 1 (`HCOM_DIR` precedence) has an
  operator-agreed design (Option C, #312) with its fix PR unblocked. No
  `runtime/` regression — `_resolve_session_record`'s two-collision →
  unresolved `{}` behavior is a no-mis-bind design, not a new risk.
- **`INSIGHT-e0b448a6` / `INSIGHT-75785aae` (harness layer / `tick()` zero
  production callers) are increasingly stale** — #306 and #310 add the first
  real `.stop()` and `.send()` call sites, and `tick()` runs on the enforced
  `recovery-tick` path. The *exercise* gap remains, so they are not killed,
  but the "zero callers" framing no longer holds. Noted; dispositions carried
  (they had current dispositions at #24/#25).
- **`runtime/` behavior changes this arc**: #308 (`create_run_manifest` fails
  loud), #310 (new `send-context` subcommand + assembler + binding-resolution
  extraction), #313 (`_resolve_session_record` + `base_name` dedup), #311
  (CI-guard script), #314 (help strings), #306 (default-off `.stop()` call).
  Everything else is `work/`-only.

## 3. Friction-log consumption (mandatory)

Walked `work/coordination/FRICTION_LOG.md` in full + ran
`python3 tools/triage_status.py --root .`:

```
FRICTION_LOG: 15 entries - 7 closed, 8 open (0 unresolved).

## Drift+ repair records missing a countermeasure or regression case
- work/notes/2026-08-18-stalled-dispatched-worker-repair.md (severity DRIFT)
```

**No `verified: UNVERIFIED` / `countermeasure: none yet` entry, no OVERDUE
subset.** The 4-pass merge-marks escalation was CLOSED at #25 and stays
closed (no bare `gh pr merge` observed this arc — the 15-PR session-37
backlog merged via `scripts/opcmd_merge.py` under operator batch
authorization, per the session-37 handoff). The mechanical backstop is
authoritative here and it flags nothing overdue.

### 3.1 Open behavioral-watch entries — disposition this pass

| Entry | Disposition this arc |
|---|---|
| `stale slice-boundary NonGoalTests assertions` (2026-09-01) | **No new exposure.** No scope-expanding `_select_skills` / `context_builder` slice this arc; #310's `runtime/context_delivery.py` is a new module, not a `context_builder` boundary crossing. Stays open, no occurrence. |
| `fix commit lands on top of review-evidence` (2026-09-03) | **No silent occurrence.** Every evidence file this arc was re-bound by an explicit, correctly-named `reval-neso` zero-diff revalidation commit (the #297 mechanism working as designed) — not a silent staleness. Stays open, no occurrence. |
| `dispatched worker stalls on its own full unittest suite` (2026-09-03) | Countermeasure is "scoped-needed (rule 20)". No dispatched-worker stall observed this arc from the trajectory lane's vantage; not independently verifiable from a fresh clone. No status change. |
| `coordinate-via-helper-lanes is a standing operator preference` (2026-08-31) | In active use (this pass is a dispatched analysis lane under coordinator `nipe`). No change. |
| `context-rotation checkpoint too small for the coordinator role` (2026-08-31) | `verified: PARTIAL` per the log. Session-37 handoff self-cleared at ~220k with a written handoff — countermeasure in use. No change this pass. |
| `"triage" loop was procedure-only` (2026-08-31) | This pass is the consumption half; `triage_status.py` ran clean. Working as intended. |
| `coordination_housekeeping.py non-functional` (2026-09-03) | Unchanged this arc — `IDEA-9e7014fa` / `IDEA-bc6cd243` still open, no fix PR. Carried. |
| `circular import runtime/environment <-> runtime/state/environment` (2026-09-04) | `python3 -m runtime.smoke` exit 0 + 88 targeted tests OK — no import failure surfaced. Per the log this has a countermeasure; no regression this arc. |

### 3.2 Drift+ repair record `2026-08-18-stalled-dispatched-worker-repair.md`

Flagged by `triage_status.py` at **#23, #24, #25, and now #26** — 4
consecutive passes, no disposition. Prevention §1 (no mechanical
heartbeat/expected-duration convention for dispatched workers) is discharged
**in substance** by the session-24/25 Monitor-stall work
(`work/notes/2026-09-04-monitor-stall-mechanical-safeguard-design.md`, PR
#288 `scripts/run_tests_sharded.py` + the push-before-test / foreground-pytest
discipline; memory `feedback_subagent_monitor_polling_stall`) — a different
mechanism addressing the same failure mode, not the exact
"expected-duration-in-brief" idea. **This pass appends a dated disposition
line** to the record's Prevention section pointing at that work, breaking the
4-pass flag cycle (rule 20: a repeatedly-flagged bookkeeping gap gets closed,
not re-flagged a 5th time). Prevention §2 (EMERGENCE capture shape) is
superseded — `work/insights/` / `work/ideas/` now exist and are swept every
pass. Also listed in §7 for operator visibility.

## 4. Emergence pass (mandatory)

### 4.1 Phase 1 — Imagine → Capture

Bounded pass against the 14-PR arc (process-hardening + design notes + two
default-off call sites + DEC-003 bug convergence + one real capability
closure). **Zero new `scripts/emergence.py capture` records this pass.**

The one candidate worth naming is fully captured as this pass's §2 finding
rather than a new `work/insights/` record (no-duplicate-truth): **the
"design note → call site → deferred exercise" cadence for 6.4 and 6.22 is
spreading a single row's closure across 2–3 PRs while default-off code
accretes and the row stays IN PROGRESS.** This is a specific, checkable
observation about *this* arc's shape, not yet a durable structural pattern
(6.16 in the same arc closed cleanly with an exercise), so it is a
trajectory-note finding and a watch item for #27, not a captured insight.
A pass that keeps finding nothing worth imagining, arc after arc, is a
`TENTH_SEAT_REVIEW.md` §7 signal — noted; this pass did find something to
engage with (§2, §4.2), so the signal is not tripped.

### 4.2 Sweep — `work/insights/` + `work/ideas/` open records

`git diff --stat cbc1846..HEAD -- work/insights/ work/ideas/` → only
`IDEA-fe6c0f0f` added (by #300). Dispositions:

| Record | Disposition | Rationale |
|---|---|---|
| `IDEA-fe6c0f0f` (revalidation is-ancestor check never fires on a plain rebase) | **promote** → a bounded follow-up on `scripts/check_review_evidence.py` + `playbook/MODEL_CAPABILITY_ROUTING.md` "Revalidation review tier": accept **diff-equivalence** (pre-rebase patch vs post-rebase patch identical), not only `git merge-base --is-ancestor`. Evidence is now strong: `reval-neso` performed exactly this manual diff-equivalence check across **14 PRs** this arc (see `pr-308-review-evidence.md`'s summary for the worked example). The manual step is a recurring per-PR tax under strict branch protection. Pass recommends; operator/coordinator disposes per `EMERGENCE.md` Phase 3. | The "smallest next test" in the record's own text got run 14× this arc. |
| `IDEA-582cc671`, `IDEA-968eb261` (zero-diff / rebase-tolerant re-review tier) | **stale — implemented.** `#297` (merged pre-arc) is this idea; `IDEA-fe6c0f0f` is the identified residual gap, promoted above. This pass **appends a dated disposition line** to each record's `## Promotion` section (method §"stale"). | Direct: #297 shipped the tier; `IDEA-fe6c0f0f` scopes what's left. |
| `INSIGHT-651d8c62` (7-row cluster "one step from done for 13 passes"), `INSIGHT-102296b5` (criterion may be structurally unexercisable) | **stale — resolved.** `DEC-003`'s Result section (#298) + the 6.16 exercise (#303, this arc) answer both directly: the criterion was exercisable, and 5 of 7 rows are now DONE (6.5/H5/E4/L6 at #25, 6.16 at #26). This pass **appends a dated disposition line** to each. | Direct: DEC-003 Result + row 6.16 diff. |
| `INSIGHT-45727354`, `INSIGHT-68a53a28` | **incubate — past N=3, still no operator disposition.** Escalated at #23; carried #24, #25; 4th pass now. Not re-running the audit — checked both `## Promotion` sections directly, neither has a dated disposition line. **Operator-escalation item (§7).** | `## Promotion` sections unchanged since #23. |
| `INSIGHT-e0b448a6`, `INSIGHT-75785aae` (harness / `tick()` zero production callers) | **incubate — framing now partly overtaken by #306/#310** (first real `.stop()`/`.send()` call sites). Had current dispositions at #24/#25; not re-litigating. #27 should re-read these once 6.4/6.22 are exercised — likely kill then. | §2. |
| `INSIGHT-29a10ad4`, `INSIGHT-ab696436`, `INSIGHT-a6406800`; `IDEA-20615e4d`, `IDEA-bc6cd243`, `IDEA-a134ad7c`, `IDEA-9e7014fa` | **unchanged from #24/#25** — no touch this arc; re-litigating would duplicate already-correct dispositions. | `git diff` empty for these. |

## 5. DEC-003 status — cluster now 5 DONE / 2 IN PROGRESS

`work/decisions/DEC-003-harness-enforcement-cluster-exit-criterion.md` header
still reads `Status: ADOPTED` (stale prose relative to its own Result section,
as flagged at #25 — outside this pass's edit boundary, carried). Cluster
state after this arc:

- **DONE (5):** 6.5, H5, E4, L6 (#298, check #25) + **6.16 (#303/#304, this
  arc)**.
- **IN PROGRESS (2):** 6.4 (call site #306, no exercise), 6.22 (call site
  #310, no exercise). #307 flags 6.22 has no organic call site — a
  larger-than-a-follow-up decision the coordinator holds.

## 6. Tenth Seat / §7 (read before recording)

**Trigger 2 status: ARMED (both #24 and #25 found substantive things), did
NOT fire this pass.** This pass found: a real earned scoreboard flip
independently re-verified against the table (§2); a specific new trajectory
observation about the 6.4/6.22 call-site-without-exercise cadence (§4.1); and
promote-worthy evidence for `IDEA-fe6c0f0f` from the 14-PR revalidation batch
(§4.2). Not a shallow pass.

**Trigger 1 check (status-flipping PR approved with zero findings):** #304
flips row 6.16 → DONE (condition 2 met). Condition 1 is **not** met — the
review carried an articulated merge-ordering condition, and the #303 exercise
review negotiated two explicit caveats into the row text (a reviewer who
articulated nothing would not have done that). The conjunction does not hold.
Trigger 1 does not fire.

**§7 "signs this has gone wrong" checklist** (assigned reader duty; no
minority reports have accumulated since #25, so this is read against a nil
set): none present. This report is not written post-merge to paper anything
over (the flip landed in #304 days before this pass); this lane
(`traj26-sofa`) is a fresh dispatch, no repeat-role pattern; §2's flip is
re-verified by an independent table re-count, not trusted from the commit
message.

## 7. Operator-decision / escalation items

1. **`INSIGHT-45727354` / `INSIGHT-68a53a28`** — both past N=3 incubation
   (escalated at #23), still no operator disposition as of #26. Carried
   forward a 4th time. Needs an operator promote / stale / kill call.
2. **`work/notes/2026-08-18-stalled-dispatched-worker-repair.md`** — flagged
   by `triage_status.py` for 4 straight passes. This pass appends a dated
   pointer to the Monitor-stall countermeasure work (§3.2) to break the
   cycle; if the operator considers Prevention §1 not adequately discharged
   by that, a dedicated "expected-duration convention in task briefs" task is
   the open shape.
3. **`IDEA-fe6c0f0f` (promote recommendation, §4.2)** — diff-equivalence
   acceptance in `check_review_evidence.py` / `MODEL_CAPABILITY_ROUTING.md`.
   Strong evidence (14 manual checks this arc). Coordinator/operator to
   dispose — the pass recommends, does not authorize.
4. **`DEC-003` header `Status: ADOPTED`** is stale prose relative to its own
   Result section (5/7 rows DONE) — cosmetic, flagged since #25, for whoever
   holds `work/decisions/` write access.
5. **6.4 / 6.22 have no organic production call site for an exercise** (#307,
   stop condition #2) — a larger-than-a-bounded-follow-up decision the
   coordinator holds; not blocking CONTINUE.

Nothing here requires operator action *before work continues* — CONTINUE
stands.

## 8. Recorded for the next pass (check #27)

- **Arc anchor for #27**: the squash commit of *this* PR (#26).
- `python3 -m runtime.smoke` exit 0; EXP-B 3 OK, f1 0.8666…,
  `false_activation_cases` 0, precision 1.0 — a regression here is a
  status-truth emergency.
- **Scoreboard 19/10/6** — 6.16 flipped this arc. Re-derive from the §7 6.x
  table Status column directly (35 rows: count `DONE` / `IN PROGRESS`
  including the 1 "evaluation-only" / `NOT STARTED`); flag the coordinator
  before recording any further flip.
- **Cluster is now 5 DONE / 2 IN PROGRESS.** #27 checks: did **6.4** get its
  `--terminate-denied-sessions` `.stop()` / `BEFORE_DESTRUCTIVE_ACTION`
  first-exposure exercise? Did **6.22** get a `maps run send-context
  --deliver-context` / `BEFORE_SEND` exercise (or an operator ruling on the
  no-organic-call-site question from #307)? Watch the
  "design-note→call-site→deferred-exercise" cadence — if a 3rd arc passes
  with call sites but no exercise, that is itself a finding.
- **DEC-003 bug 2 fixed** (#313). Bug 1 (`HCOM_DIR` precedence) — operator
  agreed Option C; #27 checks whether the fix PR landed.
- **`IDEA-fe6c0f0f`** promoted this pass — #27 checks whether a
  diff-equivalence follow-up was opened.
- **`INSIGHT-45727354` / `INSIGHT-68a53a28`** — still no operator disposition
  as of #26. Don't re-run the audit — just check the `## Promotion` sections.
- **`INSIGHT-e0b448a6` / `INSIGHT-75785aae`** — re-read once 6.4/6.22 are
  exercised; likely kill then.
- **FRICTION_LOG**: this pass appended its own dated review line + the
  repair-record pointer in the same PR — keep doing that.
- **Trigger 2**: #24, #25, #26 all found substantive things — armed for #27.
  A genuinely-clean #27 FIRES it: flag the coordinator BEFORE recording a
  clean result or dispatching a Tenth-Seat sub-agent, then write
  `work/reviews/trajectory-27-minority-report.md`.

## Resume prompt

You are running roadmap trajectory check #27 for MAPS_Lean. Independent
analysis lane. Follow `playbook/ROADMAP_TRAJECTORY_CHECK.md` (5-step +
friction-log consumption + Emergence pass) and `playbook/TENTH_SEAT_REVIEW.md`
§7 (read before recording any clean result). Fresh clone to a UNIQUE path
(`git clone https://github.com/BigCatMellow/MAPS_Lean /tmp/traj27-work`);
verify `git rev-parse origin/main` == `HEAD`, `git status --porcelain` empty.
NEVER touch `~/Projects/MAPS_Lean`, `.claude/worktrees/`, or `.maps/` for
writes (read-only checks against the coordinator checkout are fine). Do NOT
run `maps recovery-tick` or any `--enforce-*` pass, and do NOT spawn a real
hcom session, unless explicitly authorized.

Anchor: `git log --oneline --grep='Roadmap trajectory check' main | head -1`
→ the check-#26 squash; then `git log --oneline <that>..HEAD`, check every
line. Confirm your write-up covers
`git log --oneline <that>..HEAD | grep -cE '\(#[0-9]+\)$'` PRs.

Method (rule 14): no claim from a PR title/body/review summary alone —
re-verify against `git show`, merged code, `/usr/bin/grep`, targeted
`unittest` modules foreground. `python3 -m runtime.smoke` must exit 0.
`tests.test_exp_b_skill_routing` must stay 3 OK, f1 0.8666…,
`false_activation_cases` 0, precision 1.0. Full suite is CI's — do NOT
background-and-wait, no Monitor on a test run, no `kill -0 <pid>; sleep` loop.

Context from #26: arc #300–#314 (14 PRs, #302 excluded) landed the no-hype
invariant (#301), the 6.16 worktree-binding-guard exercise + flip to DONE
(#303/#304), default-off call sites for 6.4 (#306) and 6.22 (#310) *without*
exercises, DEC-003 bug 2 fix (#313) + bug 1 design (#312), a rule-20 CI-guard
strengthening (#311, 3rd occurrence), and Finding-0 fixes (#308/#314).
**Scoreboard moved 18/11/6 → 19/10/6** (6.16, first movement since #25's 6.5
flip). Cluster now 5 DONE / 2 IN PROGRESS (6.4, 6.22). Trigger 2 ARMED, did
NOT fire.

Specifically check at #27: (a) did **6.4** get its `.stop()` /
`BEFORE_DESTRUCTIVE_ACTION` first-exposure exercise, or **6.22** a
`send-context --deliver-context` / `BEFORE_SEND` exercise? If a 3rd arc
passes with call sites but no exercise, that is a finding — write it up.
(b) is the merge gate still observed on every merge since #299 (spot-check
1–2 ledger entries if the coordinator checkout is reachable read-only), or
did a bare `gh pr merge` slip through (NEW friction entry, not a reopen)?
(c) did the `IDEA-fe6c0f0f` diff-equivalence follow-up get opened? Did the
`HCOM_DIR` Option-C fix PR land? (d) `INSIGHT-45727354` / `INSIGHT-68a53a28`
— operator disposition yet (don't re-run the audit, just check the
`## Promotion` sections)? (e) re-derive the scoreboard from
`CAPABILITY_CHECKLIST.md` §7 by direct count of the 6.x table Status column
— expect 19/10/6 unless 6.4/6.22 moved; flag the coordinator before any
further flip. (f) Trigger 2: a genuinely-clean #27 FIRES it — flag the
coordinator BEFORE recording a clean result or dispatching a Tenth-Seat
sub-agent, then write `work/reviews/trajectory-27-minority-report.md`.

DELIVERABLE: one PR, branch `roadmap/trajectory-check-27`, adding
`work/notes/2026-09-<DD>-roadmap-trajectory-check-27.md` (+ any `FRICTION_LOG`
follow-up lines — append them in this PR, don't just describe them — +
emergence sweep dispositions + minority report iff Trigger 2 fires). Update
`CAPABILITY_CHECKLIST.md` ONLY if a status genuinely moved (hard evidence) —
flag the coordinator first. Author email
`201203536+BigCatMellow@users.noreply.github.com`. Commit trailer
`Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>`. TWO-PHASE REVIEW:
do NOT push your own review evidence, do NOT spawn your own reviewer; when the
PR is open and CI `test` is green, report the PR number + full head SHA to the
coordinator via hcom (prefix every message with your name), then stand by for
review findings.
