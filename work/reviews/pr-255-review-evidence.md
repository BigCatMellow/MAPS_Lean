# PR #255 review evidence — Ask #1 control-plane setup runbook

Independent verification-only review by maps-lean-nava (gela authored).
Docs-only, 1 file (`work/notes/2026-09-02-ask1-control-plane-runbook.md`), no
runtime change. One REQUEST_CHANGES round (a missing table row), fixed, then
APPROVE. `head_sha` below is the rebased branch tip.

## The load-bearing claim (§3 / §8) — traced independently. CORRECT.

> "the first `--enforce-canonical-run` pass on a fresh `.maps/` is a NEAR NO-OP —
> `CanonicalRunGuard.__call__` never fires on a real incident because
> `RecoverySupervisor._resolve_harness_binding` requires
> `resolve_run_session(run_id).state == EXPLICIT` before routing a resume through
> the guarded `HarnessService`, and NO production path writes that first
> `run_session_links` row."

Traced end-to-end at `156f879`:

1. `CanonicalRunGuard.__call__` fires only inside `HarnessService.resume()` (via
   the hook registry). `RecoverySupervisor.tick()` (`supervisor.py:538`) calls
   `self.harness_service.resume(binding, session_ref)` **only when
   `binding is not None and session_ref is not None`** (`:534`); otherwise it
   falls through to a byte-identical unguarded `self.hcom.resume(...)` — no
   guard, no denial.
2. `_resolve_harness_binding` (`supervisor.py:208`) returns `(None, None, reason)`
   unless, in order: `run_id` set, task exists, `project_id` +
   `compute_task_revision` non-empty, **and `resolve_run_session(run_id)` is a
   Mapping with `.get("state") == "EXPLICIT"`** (`:244-245` →
   `"session_not_durably_bound"`), and `current.adapter_id == "hcom"` with a
   non-empty `session_id`.
3. `state == "EXPLICIT"` requires ≥1 `run_session_links` row forming a valid
   linear chain (`run_lineage.py::_resolve_run_session_conn`).
4. The sole non-test writer of `run_session_links` is
   `HcomHarnessAdapter._record_attach → self.lineage_writer.record_run_session_link(...)`
   (`harness/adapters/hcom.py:218`) — reached only from
   `HcomHarnessAdapter.start()` / `.resume()` → only from `HarnessService` →
   only constructed by `build_canonical_harness_service` (this pass) → and
   `RecoverySupervisor` calls **only `.resume()`** on it (never `.start()`).
5. `flow start` writes a run manifest but no session link
   (`flow_start.py:108/185/187` — "intentionally stops before choosing or
   launching a provider session").

**Deadlock confirmed:** to get `EXPLICIT` lineage you must run
`record_run_session_link`, which only runs inside the guarded
`HarnessService.resume/start`, which `_resolve_harness_binding` refuses to route
to without `EXPLICIT` lineage. On a fresh `.maps/` the pass yields **0
`resume_denied`**. The runbook's headline finding — Ask #1 as literally scoped
("first pass that converts working resumes into `resume_denied`") is not
reachable without a lineage-bootstrap code change — is accurate and is the
material thing the operator must hear before "going".

## Sub-checks

- **(i)** "any `maps` subcommand incl. `maps status` creates
  `.maps/state/maps.db` via `TaskStore`." VERIFIED — `runtime/cli.py:593`
  `store = TaskStore(args.db)` runs unconditionally before command dispatch;
  `BaseStore.__init__` does `mkdir(parents=True)` + `executescript(schema.sql)`.
- **(ii)** ".maps/ gitignored + `rm -rf .maps/` is a clean reset." VERIFIED.
  `.gitignore` has `/.maps/state/`; every path the control plane writes is under
  `.maps/state/`. The runbook's precision fix (rule is `/.maps/state/`, not
  `/.maps/`; a hypothetical future `.maps/`-level file would not be
  auto-ignored) is correct.
- **(iii)** §6 per-row table — accurate for all 7 rows after the fix. Each of
  6.4 / 6.5 / 6.16 / 6.22 / H5 / E4 / L6 verified against its
  `CAPABILITY_CHECKLIST.md` "still missing" clause. The **6.22 row was missing
  in round 1** and is now added with the correct framing: the pass instantiates
  `MemoryProvenanceGuard` in the composition
  (`register_memory_provenance_guards`) but `RecoverySupervisor` only calls
  `.resume()` never `.send()`, so `BEFORE_SEND` never fires — 6.22's real exit
  (a denied `send()` on a WITHHOLD item) is unreachable from `recovery-tick`,
  the same instantiation-only pattern as H5. The summary now synthesizes: three
  of the seven (6.16, H5, 6.22) share the guard-instantiated-but-callback-never-
  fired shape.
- **(iv)** Option (A) recommendation. Sound and does not overstep. Ask #1 was
  authorized as "one enforced pass", not a code change. The round-1 review
  flagged, and the delta sharpens, that because Ask #1's *literal* outcome is
  now known unreachable, the (A)-vs-(B) choice **is an operator decision** —
  §8 now states this explicitly and reframes the recommendation as (A)+(B)
  sequenced, with "the operator must be told: the pass will produce 0 denials;
  (B) is the code change for the outcome you meant."

## Other

- `python3 -m runtime.smoke` → exit 0.
- §9 command sequence consistent with the traced CLI wiring; §4 remediation
  matches `docs/CONTROL_PLANE_SETUP.md` §5 + the guard deny-code order.
- The "READ-ONLY INVESTIGATION, no `maps` command run, `.maps/` not created"
  boundary is honored — no `.maps/` in the tree, diff is 1 doc file.

## Verdict: APPROVE

reviewer: maps-lean-nava
head_sha: ce8344d8adbd20cebcc7312f005545509b3fa5af
independent: true
summary: APPROVE after a REQUEST_CHANGES round — the runbook's load-bearing finding (a fresh-.maps/ enforced canonical-run pass produces zero resume_denied because CanonicalRunGuard is only reachable through the same guarded HarnessService that is the sole writer of the run_session_links EXPLICIT row it requires — a genuine lineage-bootstrap deadlock) is traced and verified correct end-to-end against runtime/recovery/ + runtime/harness/ + runtime/state/; sub-checks (DB auto-creation, gitignore, remediation workflow) verified; the round-1 gap (the §6 "7-row verification" table had only 6 rows, missing 6.22) is fixed with the correct instantiation-only framing, and §8 is sharpened to state that the (A)-vs-(B) choice is an operator decision because Ask #1's literal outcome is now known unreachable.
