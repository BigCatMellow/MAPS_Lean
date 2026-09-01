# Roadmap trajectory check #11 — arc: PRs #194–#207

Eleventh pass. Predecessor: `work/notes/2026-08-31-roadmap-trajectory-check-10.md`
(covered PRs #185–#192, ended at head `ee342c5`; scoreboard held 16 DONE /
13 IN PROGRESS / 6 NOT STARTED across passes #8/#9/#10).

**Scope correction (recorded, flagged to `niko`).** The dispatch named the arc
as "6 PRs since check #10: #202–#207". The actual uncovered arc is **PRs
#194–#207** (14 PRs). Check #10's note explicitly covers #185–#192; #193 was
the check-10 PR itself; **#194–#201 were never trajectory-checked.** This pass
covers the full range. `git log fbe88bc..c5461c9` (i.e. everything after the
check-10 PR):

| PR | commit | kind | what |
|----|--------|------|------|
| #194 | `d810509` | impl | SEC3/6.4 — `HarnessService.stop()` fires `BEFORE_DESTRUCTIVE_ACTION`; `DestructiveExternalActionGuard` reads `task_policy` via a duck-typed source; fail-closed `_require_destructive_enforcement`. |
| #195 | `d5c99ed` | impl | Canonical `HOOK_DENIED` on the RnS resume path parks the incident in a distinct non-attempt-consuming `denied` state (own ceiling → `canonical_denial_persistent`). |
| #196 | `5b76458` | design | turn advisory resume-validation into an opt-in gate (6.5/H4/E4). |
| #197 | `24e0139` | design | first production Skill-catalog entrypoint (SEC4/6.10) + #192 nits. |
| #198 | `fae8251` | design | first memory-trust tool-call enforcement seam (6.22). |
| #199 | `294041f` | impl | SEC/6.5 — `maps recovery-tick --enforce-validation` (opt-in, default-off): a concretely-failing `quick` tier parks the incident in a disjoint `blocked_validation` state before the resume. |
| #200 | `98620e4` | impl | SEC4/6.10 — `build_project_skill_catalog(repo_root, store)` wired into `runtime/flow_start.py`; first production catalog-with-store. |
| #201 | `148889a` | design | routing environment-report production source & cache (6.24). |
| #202 | `306904c` | impl | SEC/6.22 slice 1 — `MemoryProvenanceGuard` on `BEFORE_SEND`; composed into `build_canonical_harness_service`. |
| #203 | `38c6f73` | design | SEC4 operator-driven lifecycle transitions + operator-identity (Half 3). |
| #204 | `e7d93ca` | impl | SEC/6.24 slice 1 — `flow_start` step 4 writes `run_environment_evidence` for contracted tasks; `select_recorded_environment_reports` + `maps route --environment-reports-from-recorded` (default-off) + a `policy_gate/environment_report_required` hold. |
| #205 | `410d60c` | impl | SEC4/6.10 A1+A2 — `maps skill list\|show\|approve\|activate\|retire\|supersede` CLI; first production caller of `record_skill_lifecycle_transition()`. |
| #206 | `c5461c9` | impl | SEC/6.24 test-hardening + `runtime/recovery/production.py` docstring drift correction (the re-decision clause). |
| #207 | `bb74c00` | design | env-evidence-writer authority re-decision — "no regression" confirmed. |

7 impl PRs, 6 design notes, 1 test/docs follow-up. Verification method
(unchanged, rule 14): no claim taken from a PR title/body/review summary;
every consequential claim re-checked against `git show --stat`,
`/usr/bin/grep` over `runtime/` excluding `tests/`, and a targeted test run.

## 0. Situational awareness

- `python3 -m runtime.smoke` → **exit 0 at `c5461c9`** (`sqlite_task_lifecycle`
  ok, WAL / foreign_keys=1 / busy_timeout=5000).
- Targeted test run at `c5461c9`: `tests.test_recovery_composition_root`,
  `tests.test_memory_provenance_guard`, `tests.test_cli_skill`,
  `tests.test_routing_environment_reports`,
  `tests.test_destructive_external_action_guard`, `tests.test_flow_start`
  → **108 tests, OK** (exit 0, 207s). (The `skill approve: --actor required`
  line in the output is an expected `SystemExit` assertion in
  `test_cli_skill`, not a failure.)
- **Scoreboard recounted from the master-inventory §7 table**
  (`work/roadmaps/CAPABILITY_CHECKLIST.md` lines 108–142, 6.1–6.35 = 35 rows,
  3rd column):
  - **DONE 16** — 6.1, 6.2, 6.3, 6.6, 6.7, 6.8, 6.13, 6.14, 6.15, 6.18,
    6.23, 6.26, 6.27, 6.28, 6.29, 6.30.
  - **IN PROGRESS 13** — 6.4, 6.5, 6.9, 6.10, 6.11, 6.16, 6.19, 6.20, 6.21,
    6.22, 6.24, 6.33 (`IN PROGRESS (evaluation-only, by design)`), 6.35.
  - **NOT STARTED 6** — 6.12, 6.17, 6.25, 6.31, 6.32, 6.34.
  - **Identical to passes #8 / #9 / #10.** No label moved across the
    #194–#207 arc.

## 1. Re-verification of checklist claims against merged code

Twelve claims spot-checked across the arc. All accurate; no status
materially false.

### 1a. SEC3 / 6.4 after #194 — `stop()` destructive firing. Confirmed.

`git show d810509 --stat` (`runtime/harness/service.py +48`,
`runtime/policy/destructive_action_guard.py +173`,
`runtime/recovery/production.py +22`) + grep:

- `runtime/harness/service.py:354` — `_require_destructive_enforcement(
  HookEvent.BEFORE_DESTRUCTIVE_ACTION, "stop")` runs **before** the
  canonical-run check (`:375`); `:361` fires
  `hooks.run(BEFORE_DESTRUCTIVE_ACTION, ctx(..., destructive=True,
  external=False))` — the two booleans are a fixed literal at the call site
  (declaration-at-the-operation, addendum Q2).
- `_require_destructive_enforcement` (`:78`) is **fail-closed**: absent a
  registered `HookEnforcement.DESTRUCTIVE_EXTERNAL_ACTION`, `stop()` returns
  `DESTRUCTIVE_GUARD_REQUIRED` / `RetryDisposition.UNSAFE`.
- `runtime/policy/destructive_action_guard.py:209`
  `register_destructive_external_action_guards(...)` registers over
  `BEFORE_DESTRUCTIVE_ACTION` **and** `BEFORE_EXTERNAL_ACTION`
  (`:228`); the guard reads the `task_policy` authority model via a
  duck-typed `source` (`:14`), DENY on a missing `destructive`/`external`
  key (fail-closed, mirrors `CanonicalRunGuard`).
- **Still default-off / no first production exposure.** `HarnessService` is
  constructed only by `build_canonical_harness_service`
  (`runtime/recovery/production.py`), reached only via the opt-in
  `harness_project_id` keyword (`maps recovery-tick --enforce-canonical-run
  --harness-project-id P --repo-root PATH`). The `maps claim` piggyback and
  `maps flow start` never construct a `HarnessService`, so
  `HarnessService.stop()`'s fail-closed gate is unreachable in a default
  flow. 6.4 row reflects this ("Capability-declaration manifest + write /
  credential guards not built"). **Label correctly IN PROGRESS.**

### 1b. #195 — canonical denial parks in a distinct `denied` state. Confirmed.

`git show d5c99ed --stat` (`runtime/recovery/supervisor.py +64`,
`runtime/recovery/store.py +7`) + grep:

- `supervisor.py:44` `_REPROCESSABLE_STATES = {"scheduled", "probing",
  "blocked_validation", "denied"}` — `denied` is a re-processable parked
  state, not terminal.
- `:595` on the consecutive-denial ceiling → `incident["last_error"] =
  "canonical_denial_persistent"`, `:609` sets `incident["state"] = "denied"`
  with the deny code carried in `last_error`; the transient retry `attempt`
  is untouched (design §5 Q4).
- This is disjoint from the validation-gate `blocked_validation` path
  (`:503`) and from `retry_budget_exhausted`. Matches the E4 / 6.5 / 6.16
  "Updated 2026-08-31 §2b" evidence text exactly. No status change (labelling
  refinement, not enforcement exposure).

### 1c. #199 — `--enforce-validation` opt-in gate. Confirmed.

`git show 294041f --stat` (`runtime/cli.py +23`,
`runtime/recovery/production.py +19`, `runtime/recovery/supervisor.py +102`,
`runtime/recovery/store.py +7`) + grep:

- `runtime/cli.py` `recovery-tick --enforce-validation` — `store_true`,
  help says "requires `--repo-root`, default off. Advisory recording is
  unchanged without this flag"; CLI refuses `--enforce-validation` without
  `--repo-root` (`cli.py:592`).
- `supervisor.py:486-509` — when the pre-resume `quick` tier concretely
  fails (`attempted` + not `passed`) and `validation_blocks_resume` is set,
  the incident is parked `blocked_validation` **before** any resume call;
  `{"attempted": false}` never blocks; ceiling →
  `validation_block_persistent`.
- 6.5 / H4 / E4 rows already carry this ("first slice of
  `2026-08-31-resume-validation-gate-design.md` is implemented … Still IN
  PROGRESS: no first production exposure of an enforced pass"). **Accurate.**

### 1d. #200 — `build_project_skill_catalog` → `flow_start`. Confirmed.

`git show 98620e4 --stat` (`runtime/flow_start.py +18`,
`runtime/skills/catalog.py +35`, `runtime/skills/__init__.py +2`,
`runtime/policy/memory_trust_gate.py +10`) + grep:

- `runtime/flow_start.py:84` `skill_catalog = build_project_skill_catalog(
  repo_root, store)` inside `flow_start()`; passed to `build_context_plan(...,
  skill_catalog=...)`.
- `runtime/skills/catalog.py::build_project_skill_catalog` — one `BUNDLED`
  source at `<repo_root>/.claude/skills/`, `register_skill_catalog(...)`
  first (gate-driven subject recording), then `build_skill_catalog([source],
  store=store)`. An absent `.claude/skills/` → empty catalog → byte-identical
  flow.
- SEC4 / 6.10 rows carry this. A matched `QUARANTINED` Skill is DENY'd out of
  a real `maps flow start` context plan — **the SEC4 refusal is reachable in
  a real run.** Label stays IN PROGRESS (operator-identity + manifest halves
  open). **Accurate.**

### 1e. #202 — `MemoryProvenanceGuard`. Confirmed default-off.

`git show 306904c --stat` (`runtime/policy/memory_provenance_guard.py +245`,
`runtime/policy/__init__.py +6`, `runtime/harness/hooks.py +1`,
`runtime/recovery/production.py +9`) + grep:

- `runtime/recovery/production.py:414`
  `register_memory_provenance_guards(registry, MemoryProvenanceGuard())` —
  **inside `build_canonical_harness_service`**, the same opt-in default-off
  composition root as `CanonicalRunGuard` and the destructive guards.
- So `MemoryProvenanceGuard` on `BEFORE_SEND` is composed **only** on the
  `maps recovery-tick --enforce-canonical-run` path; never `maps claim`,
  never `maps flow start`. **No first production exposure** — mirrors
  SEC3 / H5 / 6.16(b) wording exactly. 6.22 row must reflect this (see 1g).

### 1f. #204 — 6.24 production source/cache slice. Confirmed; "Still missing" narrowed but no flip.

`git show e7d93ca --stat` (`runtime/flow_start.py +48`,
`runtime/routing/environment_reports.py +155`, `runtime/routing/cli.py +40`,
`runtime/routing/router.py +21`, `runtime/state/environment_contract.py +5`)
+ grep:

- `runtime/flow_start.py::_record_environment_evidence` — step 4, runs only
  when `store.get_task(task_id)["environment"]` is not `None`; loads the
  operator-authored `spec_ref` file, `inspect_local_environment`,
  `store.record_run_environment_evidence(..., recorded_by="maps-flow-start")`.
  Fail-closed (aborts the flow on any recording failure).
- `runtime/routing/environment_reports.py:206`
  `select_recorded_environment_reports(...)` — projects each task's latest
  recorded evidence through the **same** `_freshness_diagnostic` helper the
  caller-supplied path uses (no copied logic).
- `runtime/routing/cli.py:83` `--environment-reports-from-recorded`
  (default-off); `:132` `--environment-reports-json` still wins when both
  given.
- `runtime/routing/router.py` — holds a task at
  `policy_gate/environment_report_required` when its contract sets
  `required_for_routing` and no fresh report projects (a hold that clears on
  the next flow start; no new `PolicyDecision` kind).
- **6.24 row "Still missing" clause did narrow** — it now reads "first real
  end-to-end production exposure (a `maps flow start` that records a report
  followed by a `maps route --environment-reports-from-recorded` that
  consumes it), and an optional fleet-wide `--enforce-environment-routing`".
  That is a genuine narrowing (the pieces exist; only the end-to-end
  exposure + the optional fleet flag remain) but **not a flip**: no
  `maps route` in production defaults to `--environment-reports-from-recorded`,
  and `required_for_routing = 0` routing stays non-rejecting. Label
  correctly IN PROGRESS.

### 1g. E4 after #206/#207 — re-decision answered; docstring drift fixed.

- `git show c5461c9 --stat` — `#206` touches `runtime/recovery/production.py
  +29/-` (docstring only, per the diff: the re-decision clause now reads
  "when a production writer … *has been* introduced" and points at the #207
  note) + `tests/test_routing_environment_reports.py +118`. No behavior
  change.
- `#207` (`bb74c00`) is the design note only
  (`work/notes/2026-08-31-env-evidence-writer-authority-redecision-design.md`
  + a 1-line E4 annotation). Verdict: **posture did not regress** — the
  `--repo-root` gate, `quick`-tier-only restriction, write-time + read-time
  hash checks, and advisory-by-default nature are all unchanged;
  `RunBoundValidator` never branches on `recorded_by`. Verified against code
  in that note; re-confirmed here: `runtime/recovery/production.py` still
  reads `list_run_environment_evidence(...)` with no `recorded_by` filter,
  still `VALIDATION_TIER = "quick"`, still `spec_hash_mismatch` before
  execution.

### 1h. #205 — `maps skill` CLI. Confirmed on `main`.

`git show 410d60c --stat` (`runtime/cli.py +151`, `tests/test_cli_skill.py
+236`, `tests/test_skill_lifecycle_storage.py` guard test rewritten). grep
at `c5461c9`: `runtime/cli.py` has the `skill` subparser group +
`_resolve_skill_catalog_key` + `_dispatch_skill`; `record_skill_lifecycle_
transition` is called from `runtime/cli.py` and
`runtime/state/skill_lifecycle_storage.py` only. **First production caller
confirmed.** SEC4 / 6.10 rows carry it; label IN PROGRESS (identity registry
Half 3 gated on an operator decision; capability-declaration manifest still
NOT STARTED).

## 2. What changed (materially)

1. **The single biggest unblock lever is unchanged and now even more
   concentrated.** Four IN PROGRESS items — **6.4, 6.5, 6.16, and (as of this
   arc) 6.22** — all now have their enforcement code merged, composed into
   the *same* production composition root (`build_canonical_harness_service`),
   and *all four* are blocked on the *same* thing: **the first operator-gated
   `maps recovery-tick --enforce-canonical-run` / `--enforce-validation`
   production pass.** #194 (destructive), #195 (denied-state labelling), #199
   (validation gate), #202 (memory-provenance) each added a guard to that
   root without exposing it. `niko` is surfacing the enforcement decision to
   the operator now — that is correct and remains the highest-leverage
   single action on the board.
2. **6.24 moved from "pieces designed" to "pieces built, end-to-end exposure
   pending."** #201 (design) → #204 (impl) → #206/#207 (harden + authority
   re-decision) is a clean, fully-verified slice. The re-decision trigger in
   `recovery/production.py` fired exactly as designed and was answered "no
   regression" — the safety argument held. 6.24's remaining gap is now a
   single end-to-end run plus one optional fleet flag.
3. **SEC4 / 6.10 is the most-advanced of the security-lifecycle items.**
   Provenance done, Half 1 store done, Half 2 wiring done, catalog entrypoint
   done, operator-transition CLI done. What genuinely remains:
   (a) **B1 operator-identity registry** (`authorized_operators` table +
   opt-in check) — *gated on an unmade operator decision* on trust-root /
   bootstrap policy (`work/notes/2026-08-31-sec4-operator-lifecycle-
   transitions-and-identity-design.md`, "OPERATOR DECISION REQUIRED");
   (b) **capability-declaration manifest for third-party Skills/tools** —
   still `NOT STARTED`, untouched, SEC4's other half.
4. **No scoreboard movement, and that is correct, not a stall.** Every impl
   PR this arc was deliberately "no status flip": each is a slice that adds a
   guarded, default-off capability. The threshold every one of them is short
   of is *first production exposure*, which is a single operator decision,
   not more code. Passes #8–#11 all reading 16/13/6 reflects a real
   property: the project has been building the last-mile enforcement
   surface, and the last mile is gated on the operator, by design.

## 3. Friction-log consumption (dispatch item — standing duty)

Log skimmed in full (5 entries). Status:

| # | Entry | `verified:` | Disposition this pass |
|---|-------|-------------|-----------------------|
| 1 | self-clear resume prompt dropped | END-TO-END (3 rotations) | **Closed** at pass #10. No action. Re-confirmed a 4th time: *this* session started with `MAPS_Lean_Handoff_2026-08-31-session12.md` injected as SessionStart `additionalContext` by the `maps-handoff-context` hook, no operator nudge. |
| 2 | coordinate-via-helper-lanes preference | verified, follow-up none | **Closed.** No action. |
| 3 | context-rotation checkpoint too small | **PARTIAL** | **Consumed — follow-up discharged + one new observation.** (a) Follow-up "check `limit_watcher` hcom-side threshold": `limit_watcher` messages this session report `soft=120000 rotate=150000` — i.e. the pre-#187 values; `limit_watcher`'s config was **not** raised alongside `context_rotation.py` (185k/0.78/0.90). Per memory `feedback_limit_watcher_hcom`, `limit_watcher`'s self-rotation demands "are not a real MAPS_Lean mechanism, ignore" — so this is cosmetic noise, not a live gap; recorded so the divergence is visible. (b) Behavioral bar (a coordinator arc completing under 185k without a disruptive mid-arc rotation): sessions 11→12→13 handoffs clean; still not *explicitly* logged as "an arc ran to completion without a disruptive rotation under the new threshold". Stays `verified: PARTIAL` — the code countermeasure is live and re-confirmed, the behavioral confirmation is a coordinator call, not a blocker. |
| 4 | triage loop procedure-only | VERIFIED (pass #10) | **Closed.** This pass performs the consumption duty (this section) — the loop is real for a 2nd consecutive pass. |
| 5 | orchestrator tool-use burned ~30–40k context | n/a (behavioral), `countermeasure: none yet` | **Consumed — no recurrence in this arc's implementer lanes; still open.** No mechanical countermeasure. The #194–#207 implementer lanes (this lane included) worked with targeted greps / `git show` line-ranges / `sed -n` — no 151KB dumps observed. `limit_watcher`'s repeated "rotation_due" spam at 220k–250k tokens this session is a *separate* nuisance (entry 3(a)), not this pattern. Leave open; if a future coordinator session repeats the ad-hoc-exploration blow-up, escalate to the durable countermeasure entry 5's follow-up names (a scratchpad status-digest script). |

Nothing in the log requires escalation to in-scope trajectory work or an
operator decision beyond the one already surfaced (entry 3(a) is explicitly
a "check-if-it-recurs" item per memory, not an escalation).

## 4. Tenth-seat / §7 warning-sign duty

`playbook/ROADMAP_TRAJECTORY_CHECK.md` routes a clean pass to
`TENTH_SEAT_REVIEW.md` Trigger 2 + §7 ("signs this has gone wrong"). This
pass is **not** clean-with-nothing-found — it found a real scope gap
(#194–#201 never checked) and consumed it. Checking §7 signs anyway:

- *"The same conclusion every pass regardless of evidence"* — the scoreboard
  number is identical across #8–#11, but §2.4 above establishes this reflects
  a real property (last-mile enforcement gated on one operator decision), not
  analytical inertia. The *content* of each pass differs materially: #10
  verified the E6 seam; #11 verifies four guards converging on one
  composition root.
- *"Verdict drifting toward reassurance"* — the verdict (CONTINUE) is the
  same, but this pass surfaces a concrete concern: **four IN PROGRESS items
  now single-threaded through one operator decision** is a fragility. If that
  decision stalls, the roadmap stalls on 6.4/6.5/6.16/6.22 simultaneously.
  That is named here as the thing to watch, not smoothed over.
- *"No one has run the full check"* — this pass caught that #194–#201 slipped
  the net. The countermeasure: the arc-boundary for the *next* check is
  `c5461c9` (recorded below), not "since the last note was written".

No sign that the check process itself has gone wrong. One process
improvement: **trajectory-check dispatches should compute the arc as
`<last-check-PR-merge-commit>..HEAD`, not a hand-listed PR set** — the
hand-listed set missed 8 PRs this time.

## 5. Trajectory action: **CONTINUE**

Reasoning:

- Every checklist claim across the 14-PR arc verifies against merged code.
  No status is materially false. No flip is warranted or missed.
- The scoreboard holding at 16/13/6 is a true reflection of the work: the
  arc built guarded, default-off enforcement slices, each deliberately short
  of first production exposure.
- The route to DONE for the security/enforcement cluster (6.4, 6.5, 6.16,
  6.22) is **not more design and not more code** — it is the operator's
  enforcement decision, which `niko` is surfacing. That is the correct next
  action and it is already in motion.
- 6.24 has a clean, fully-verified slice and a single well-defined remaining
  gap (end-to-end exposure + optional fleet flag).
- SEC4 / 6.10's remaining work is precisely scoped: B1 (gated on the operator
  trust-root decision) and the capability-declaration manifest (NOT STARTED).

**No REPRIORITIZE / RESEARCH / CUT SCOPE / STOP.** The one thing to watch
(named, not a blocker): 6.4/6.5/6.16/6.22 are now single-threaded through the
first-enforced-pass operator decision. If that decision does not land soon,
the next trajectory check should treat "four items blocked on one ungiven
decision" as a REPRIORITIZE trigger and consider whether any of the four has
an independent partial-exposure path.

## 6. Checklist update

**None.** No status moved. The evidence text for the affected rows (6.4,
6.5/H4/E4, 6.10/SEC4, 6.16/E6, 6.22, 6.24) was already updated by the
respective impl PRs in this arc (verified in §1). This note is evidence, not
a status change.

## 7. Recorded for the next pass

- **Arc boundary for check #12:** everything after `c5461c9` — use
  `git log c5461c9..HEAD`, not a hand-listed PR set.
- `python3 -m runtime.smoke` exit 0 at `c5461c9`.
- Scoreboard: 16 DONE / 13 IN PROGRESS / 6 NOT STARTED (35 rows, §7 table).
- Watch item: 6.4/6.5/6.16/6.22 single-threaded through the first-enforced-
  pass operator decision.
- Friction entry 3 stays `verified: PARTIAL` (behavioral bar open);
  entry 5 stays open (no recurrence this arc).

## Resume prompt

You are running roadmap trajectory check #12 for MAPS_Lean. Follow
`playbook/ROADMAP_TRAJECTORY_CHECK.md` exactly (5-step check + friction-log
consumption). Work in a worktree off `origin/main`; `git fetch origin main`
first.

Arc = `git log c5461c9..origin/main` (everything after trajectory check #11's
end commit — do NOT accept a hand-listed PR set; compute it from the range,
because check #11 found that #194–#201 had slipped an earlier hand-listed
dispatch).

Method (rule 14): take no claim from a PR title/body/review summary;
re-verify every consequential claim against `git show --stat`,
`/usr/bin/grep` over `runtime/` excluding `tests/`, and a targeted test run.
`python3 -m runtime.smoke` must exit 0 — record the sha.

Specifically check: (a) did the first operator-gated
`--enforce-canonical-run` / `--enforce-validation` production pass land? If
so, 6.4/6.5/6.16/6.22 may finally be flippable — verify hard before flipping.
(b) Re-derive the 16/13/6 scoreboard from the master-inventory §7 table
(`work/roadmaps/CAPABILITY_CHECKLIST.md`). (c) SEC4 B1 — did the operator
trust-root decision get made and did `authorized_operators` land?
(d) Friction entry 3 (behavioral bar) and entry 5 (recurrence).

Deliverable: `work/notes/2026-XX-XX-roadmap-trajectory-check-12.md` —
situational awareness, what-changed, a trajectory action with reasoning,
friction-log consumption results, recounted scoreboard. Update
`work/roadmaps/CAPABILITY_CHECKLIST.md` ONLY if a status genuinely moved
(with evidence).

Workflow: own worktree; PR into `main` (never push to main); independent
review per `reference_committee_review` (no mutation testing — analysis
note); do NOT spawn your own reviewer — ping `niko`; no self-merge; report
PR# to `niko`.

STOP + flag `niko` if: reality contradicts a checklist claim in a way that
needs a status flip you are not certain of, or the trajectory action would
be anything other than CONTINUE.
