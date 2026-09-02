# PR #261 review evidence — lineage-bootstrap exercise note (`maps run bind-session` on a fresh `.maps/`)

reviewer: maps-lean-luve
head_sha: d2870df0dd6dd93fdf6aa46a65ed73511547012d
independent: true
summary: Independent verification review by maps-lean-luve (nava authored #261 and #258; luve authored #259 and reviewed #260 — independent of both #261 and #258). Note-only, +1 file (`work/notes/2026-09-02-lineage-bootstrap-exercise.md`, +273/-0), verification review (no mutation set — coordinator dispatch). All checked claims hold against `origin/main` `3a4b3a4`: (i) §2.3's `_resolve_harness_binding` precondition table matches `runtime/recovery/supervisor.py:208` — `resolve_run_session(run_id)["state"] == "EXPLICIT"` (supervisor.py:244-246), `current.adapter_id == "hcom"` (:251-253), non-empty `current.session_id` (:251-253), non-empty `project_id` + `compute_task_revision` (:231-238) are all real gate conditions, and a non-EXPLICIT state returns `(None, None, "session_not_durably_bound")` exactly as the note says; (ii) §3's "flips NONE / advances the shared precondition" is correct — the supervisor's harness path is `resume()`-only (supervisor.py:538 `harness_service.resume`, :629 `hcom.resume`; no `.send()` call anywhere in supervisor.py), so 6.22's `MemoryProvenanceGuard` `BEFORE_SEND` hook (`runtime/harness/service.py:270,276`, bound to `"send"`) is genuinely unreachable from `recovery-tick` — 6.22 is off this path as claimed; H5 and 6.16/E6(b) each still require the operator-gated `--enforce-canonical-run` pass to be run (and 6.16 additionally a `--require-canonical-run` worktree-bound run), neither of which this exercise did; (iii) every CLI verb/flag in §1 matches #258's as-merged argparse exactly — `run bind-session <run_id>` positional, `--worker-id`/`--session-id`/`--evidence-ref` required, `--adapter` default `hcom`, `--created-by` default `maps-run-bind-session`; (iv) boundaries honoured — `git diff --stat origin/main` = the one note file, no `runtime/` change, no schema change, no `CAPABILITY_CHECKLIST.md` edit, no `--enforce-*` pass. One non-blocking nit (below). VERDICT: APPROVE.

## What was verified (against `origin/main` 3a4b3a4)

**Diff scope** — `git diff --stat origin/main` on `nava/lineage-bootstrap-exercise` @ `d2870df` = `work/notes/2026-09-02-lineage-bootstrap-exercise.md` +273/-0, one file, note-only. No `runtime/`, no `runtime/state/schema.sql`, no `work/roadmaps/CAPABILITY_CHECKLIST.md`.

### (i) §2.3 precondition table vs `supervisor.py:208` `_resolve_harness_binding` — ACCURATE

`runtime/recovery/supervisor.py:208-272`. The gate returns `(None, None, reason)` unless all of:

| Note's table row | Code |
|---|---|
| `project_id` non-empty | `:231` + `:238` → `"task_binding_incomplete"` |
| `compute_task_revision(task_id)` non-empty | `:232-238` → `"task_binding_incomplete"` |
| `resolve_run_session(run_id)["state"] == "EXPLICIT"` | `:244-246` → `"session_not_durably_bound"` |
| `current` is a mapping | `:247-249` → `"session_not_durably_bound"` |
| `current.session_id` non-empty and `current.adapter_id == "hcom"` | `:251-253` → `"session_not_durably_bound"` |

The note's claim "before `bind-session` the `EXPLICIT` check would have failed → `_resolve_harness_binding` returns `session_not_durably_bound` → enforced pass falls through to a direct resume with no guard call — the deadlock" is exactly what the code does. `resolve_run_session` on a manifest with no links returns a non-`EXPLICIT` state, so the note's "`state` would be `UNBOUND`" is the right shape.

### (ii) §3 "advances the shared precondition, flips NONE" — CORRECT

- **6.22 is off this path.** `supervisor.py` calls only `harness_service.resume(...)` (`:538`) and `self.hcom.resume(...)` (`:629`). No `.send()` call in the file. `MemoryProvenanceGuard` fires on `HookEvent.BEFORE_SEND` (`runtime/harness/service.py:270,276`, string `"send"`). The RnS recovery path cannot reach it.
- **H5 / 6.16(E6b) still need the enforced pass.** §3's table lists each row's unmet condition (the `--enforce-canonical-run` pass run; for 6.16, additionally a `--require-canonical-run` run so the `worktree` branch is non-null). Consistent with `CAPABILITY_CHECKLIST.md` H5/6.16 exit text at `3a4b3a4`. No status flip; a separate evidence-prose PR is named as the follow-up.

### (iii) CLI sequence reproducible in principle — verb/flag names all exist in #258

`runtime/cli.py` as-merged: `run` subparser, `run bind-session` with positional `run_id`, `--worker-id` required, `--session-id` required, `--adapter` default `'hcom'`, `--evidence-ref` required, `--created-by` default `'maps-run-bind-session'`. Dispatch `if args.run_command == 'bind-session'`. The note's recorded output field `"created_by": "maps-run-bind-session"` matches the default.

### (iv) Boundaries — HONOURED

No `--enforce-*` run (STOP condition respected). No `runtime/` change. `maps init` is `CREATE TABLE IF NOT EXISTS` only, no schema change. No checklist status flip. `.maps/` gitignored + disposable.

## Non-blocking nit (does NOT block merge)

§2.3's first table row labels the run_id precondition "`incident["run_id"]` resolvable via `resolve_session_run`". `_resolve_harness_binding` actually reads `incident.get("run_id")` directly (`supervisor.py:222`); `resolve_session_run` (the reverse `(project, adapter, session) → run_id` lookup) is used in the sibling method `_resolve_run_id_from_session` (`:178`), which is how an incident that only carries a session acquires its `run_id` upstream. §2.2 does independently exercise `resolve_session_run` and shows it resolves, and the overall claim (all preconditions now satisfiable, a routable binding is constructible) is sound — a one-cell labeling imprecision, worth a wording fix if the note is touched again, not a correction that changes any conclusion.

## Verdict: APPROVE

The exercise note is an accurate record: the `run_session_links` ATTACH row is written on a fresh `.maps/`, both forward (`resolve_run_session` → `EXPLICIT`) and reverse (`resolve_session_run` → `run_id`) resolve, the §2.3 precondition table faithfully matches `_resolve_harness_binding`, §3 correctly states the exercise advances the shared precondition without flipping H5 / 6.16 / 6.22 (6.22 verified genuinely off the resume-only recovery path), all CLI names match #258 as-merged, and every boundary holds. Bound to `d2870df0dd6dd93fdf6aa46a65ed73511547012d`.

_Committed to the branch by session-20 coordinator maps-lean-mika (independent of author nava and reviewer luve). Content is luve's verbatim review, from hcom #82823._
