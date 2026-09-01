# Trajectory-check-#12 next-3 items #2 (6.21) and #3 (L6) — scoping pass

**STATUS: SCOPING / DESIGN ONLY. No runtime code, no schema, no checklist status
change.** Dispatched by @mono off trajectory-check-#12 (PR #214) §5. All code
citations re-verified against `origin/main` `5230c73` (rule 14).

Companion design note (this PR): `work/notes/2026-09-01-6.21-review-lifecycle-verbs-design.md`.

---

## Item #3 — L6 (`harness_config_hash` persistence): **BLOCKED on operator ask #1**

**This corrects trajectory-check-#12 §5, which listed L6 as independent of ask #1. It is not.**

### The CRITICAL question, answered against merged code

> Is there ANY production run-manifest-creation path that has a composed
> `HarnessService` in scope WITHOUT going through the `--enforce-canonical-run`
> opt-in?

**No.**

1. **`harness_config_ref(service)` needs a live `HarnessService`.**
   `runtime/harness/config_ref.py:72-101` — it reads `service.adapter_ids` and
   iterates `service.hooks.list_for(event)` for every `HookEvent`. There is no
   variant that hashes a *declared* (un-instantiated) configuration.
   `/usr/bin/grep -rn "harness_config_ref" runtime/ --include=*.py` → defined +
   re-exported in `runtime/harness/__init__.py`; **zero non-test callers.**

2. **`HarnessService(...)` is constructed in exactly one production place.**
   `/usr/bin/grep -rn "HarnessService(\|build_canonical_harness_service" runtime/
   --include=*.py` (excl. tests) → the only real constructor is
   `runtime/recovery/production.py:419` `return HarnessService([adapter], hooks=registry)`
   inside `build_canonical_harness_service` (line 350).

3. **`build_canonical_harness_service` is reached only via the ask-#1 opt-in.**
   `runtime/recovery/production.py:512-518`: `harness_service` starts `None`;
   it is assigned only `if harness_project_id is not None`. Docstring, lines
   471-474 verbatim: *"when it is None -- every caller that does not deliberately
   pass one, including the `maps claim` piggyback -- no `HarnessService` is
   constructed."* `harness_project_id` is surfaced only as
   `maps recovery-tick --enforce-canonical-run --harness-project-id P --repo-root PATH`.

4. **The run-manifest-creation paths have no `HarnessService` anywhere near
   them.** `/usr/bin/grep -rn "create_run_manifest" runtime/ --include=*.py`
   (excl. tests) → two production callers:
   - `runtime/flow_start.py:139` (`maps flow start`). Per
     `work/notes/2026-08-26-hook-enforcement-composition-root-design.md` §3a and
     re-verified: `flow_start` claims + plans + binds a manifest and **stops
     before provider launch**; `/usr/bin/grep -n "harness\|Harness" runtime/flow_start.py`
     → no hits. No `HarnessService`.
   - `runtime/integrity/cli.py:117` (`runtime.integrity.cli run-create`).
     `/usr/bin/grep -n "harness\|Harness" runtime/integrity/cli.py` → no hits.

5. **Even on the `--enforce-canonical-run` path, the two never meet.**
   `recovery-tick` *resumes* existing incidents; it does not call
   `create_run_manifest`. The `HarnessService` there is used for `.resume()`
   (`runtime/recovery/supervisor.py`), not manifest creation. So there is not
   even an *enforced-mode* path where a manifest is created with a service in
   scope.

### Why this is not just a wiring gap

L6's premise (checklist line 74) is *"each evaluated run can identify which
configuration produced it."* For `maps flow start` **no harness runs** — the
flow deliberately stops before provider/session launch — so there is no harness
configuration that "produced" the run to record. Recording a hash there would
be recording the config of a service that never executed anything: a
`duplicate truth` / speculative value with no consumer (rule 12).

The real unblock for L6 is the same as for 6.4/6.5/6.16/6.22: a production path
that **executes a task under a composed `HarnessService`**. That is exactly what
operator ask #1 authorizes (`--enforce-canonical-run` resume), or a future
decision to have `maps flow start` compose and launch a harness — which
`2026-08-26-hook-enforcement-composition-root-design.md` §3a explicitly
rejected for now.

### Verdict

**L6 = BLOCKED on operator ask #1** (or on a separate, not-yet-made decision to
compose a `HarnessService` in a manifest-creating flow). No design note is
written — there is nothing to specify until the blocking decision lands. When
ask #1 is answered and the first `--enforce-canonical-run` pass runs, the L6
slice becomes: on the enforced resume path, call `harness_config_ref(service)`
once and persist `.sha256` onto the incident's run evidence / a
`ExecutionBinding.harness_config_hash` — small, but not reachable before then.

**Trajectory-check-#13 should record that next-3 #3 was retracted here** and, if
it still wants a third independent item, pick from §5's 4th candidate (6.9/S6
progressive Skill-body loading) or another genuinely-independent row.

---

## Item #2 — 6.21 (`maps flow` review lifecycle verbs): **NEEDS DESIGN → done (companion note)**

### What the checklist claims and what the roadmap actually specifies

Checklist line 130: *"Review record/recover/release/handoff flows remain
unimplemented."* This phrasing is looser than the canonical roadmap. The
roadmap's actual candidate flows
(`work/roadmaps/prime-agent-capability-roadmap.md` §12.3,
`00-MASTER-MAPS-CAPABILITY-ROADMAP.md` §6.21) are **task/run-scoped**, not
review-scoped:

| Roadmap §12.3 candidate | Sequence (roadmap) | Scope |
|---|---|---|
| `flow review` | …→ claim review → bind subject → **record verdict** | review — **verdict step is the gap** |
| `flow recover` | confirm ACTIVE → validate claimant/run/session → inspect session → **bounded RnS decision** → resume/replace | run / RnS |
| `flow release-check` | verify approved subject → validate artifact identity → **release-path smoke** → operator-visible summary | operator-visible release |
| `flow handoff` | freeze state → continuity link → review-independence consequence → **attach/start replacement session** | run / provider launch |

Re-verified primitives at `5230c73`:

- `runtime/state/review.py:12` `claim_review` — inserts a `reviews` row
  (`completed_at IS NULL`), enforces `READY_FOR_REVIEW` + independence
  (`_continuity_component_conn`). `idx_reviews_one_open` = one open review/task.
- `runtime/state/review.py:107` `record_review(task_id, reviewer_id, verdict,
  summary, *, rederived_artifact_refs=None)` — the **only** way an open review
  row closes. Enforces owner, `READY_FOR_REVIEW`, criterion verification, and
  the review-binding approval hook.
- `runtime/state/review_binding.py:496` `_validate_review_approval_conn` — for a
  `REDERIVED_AT_REVIEW` subject it **requires** `rederived_artifact_refs`
  (`REVIEW_REDERIVATION_REQUIRED` / `_MISMATCH`).
- `runtime/cli.py:247-251` `maps review-record` + `cli.py:615-620` dispatch —
  passes `task_id, reviewer_id, verdict, summary` **only**. **No
  `--rederived-artifact-ref` argument exists.**
- `runtime/flow_review.py:44` `flow_review_start` — composes preflight + claim
  (+ optional subject bind) and **stops before verdict**.
- **No review lease / heartbeat / expiry.** `/usr/bin/grep -rn "review.*lease\|
  reviews.*expire" runtime/state/*.py` → nothing. A reviewer who claims and
  disappears leaves the review permanently stuck; no primitive releases or
  reassigns it.

### The concrete, ask-#1-independent gap

For a **consequential task bound `REDERIVED_AT_REVIEW`**, `maps review-record
APPROVED` is **currently impossible via the CLI** — `record_review` always hits
`REVIEW_REDERIVATION_REQUIRED` because the CLI has no way to pass the re-derived
refs. This is a real, small, deterministic-composition gap that completes the
roadmap's `flow review` sequence (…→ record verdict) with no new authority and
no schema.

`recover` / `release` / `handoff` each need **new store primitives + a
semantics/authority decision** (there is no review lease, so "recover a stale
review" is a new authority; `release-check` is an operator-visible-release
surface; `handoff`'s final step is provider launch, which `flow start`
deliberately excludes). None is a clean "compose existing guarded ops" slice.

### Verdict

**6.21 = NEEDS DESIGN → specified in
`work/notes/2026-09-01-6.21-review-lifecycle-verbs-design.md`.**

That note's **smallest first slice**: `maps flow review-record` — a bounded
composition that preflights the bound subject's freshness mode, accepts
`--rederived-artifact-ref` when the mode is `REDERIVED_AT_REVIEW`, calls
`record_review(...)`, and stops. Pure composition over the existing guarded
primitive; no schema; no new authority; independent of operator ask #1. The
note defers `recover` / `release` / `handoff` with explicit rationale and the
decisions each needs.

---

## Summary table

| Item | Verdict | Where specified | Independent of ask #1? |
|---|---|---|---|
| **#2 — 6.21 review verbs** | **NEEDS DESIGN → done** | `work/notes/2026-09-01-6.21-review-lifecycle-verbs-design.md`; slice 1 = `maps flow review-record` | **Yes** |
| **#3 — L6 config-hash persistence** | **BLOCKED on operator ask #1** | n/a — nothing to specify until the blocking decision lands; trajectory-#12 §5 next-3 #3 retracted here | **No** — corrects the trajectory note |

## Resume prompt

You are acting on the trajectory-#12 next-3 scoping outcomes for MAPS_Lean.
Two results: (a) **6.21** has a dispatchable smallest slice —
`work/notes/2026-09-01-6.21-review-lifecycle-verbs-design.md` §"Smallest first
slice" specifies `maps flow review-record` as a bounded composition over
`record_review` (freshness-aware, accepts `--rederived-artifact-ref`, stops
before anything else); dispatch it as an impl task, worktree off `origin/main`,
PR into main, independent review, no self-merge. (b) **L6** is **BLOCKED on
operator ask #1** — do not dispatch it; when ask #1 is answered and the first
`--enforce-canonical-run` pass is authorized, the L6 slice is "persist
`harness_config_ref(service).sha256` on the enforced resume path". If a
replacement third independent item is wanted now, use trajectory-#12 §5's 4th
candidate (6.9/S6 progressive Skill-body loading).
