# MAPS Lean Runtime Integration Review

- Date: 2026-08-14
- Scope: replacement runtime represented by former stacked PRs #9–#15 plus integration hardening on `agent/runtime-integration-review`
- Intended merge target: `main`
- Review outcome: **PASS — MERGE CANDIDATE**
- Legacy deletion included: **NO**

## Independence statement

This review was performed as a fresh adversarial pass, but by the same assistant
continuity that participated in earlier implementation. It is therefore **not**
represented as an independent human/model review.

Independent verification comes from GitHub-hosted mechanical checks and
reproducible tests: compile checks, Ruff fatal-error rules, Bandit medium/high
security analysis, dependency consistency, the full unittest suite, real
LangGraph SQLite smoke, and installer syntax/preview.

The operator explicitly requested that the remaining work be completed so that
`legacy/` deletion becomes the final separate action.

## Material findings and corrections

The review did not rubber-stamp the original stack. It found and corrected these
material issues:

1. **Task contract + policy shaping were not atomic.** Policy flags and operator
   approval invalidation now occur inside the same SQLite write transaction as
   contract shaping.
2. **Output reservations matched exact strings only.** Parent/child filesystem
   scopes now conflict, and malformed absolute/`..` output paths fail AGI
   readiness.
3. **Git rename proof could hide the source path.** Scope verification now parses
   `--name-status -z` and preserves both rename/copy endpoints.
4. **Aider attribution was ambiguous on a dirty worktree.** Bounded Aider work
   now requires a clean worktree and validates every resulting changed path.
5. **Helper scope accepted malformed paths outside the repository.** The helper
   layer independently rejects repository escape even if malformed upstream task
   data is supplied.
6. **Worker boolean capabilities could be truthy strings.** Capability profile
   booleans are now type-checked rather than coerced.
7. **Project/task-scoped halts could omit a target.** Active scoped halts now
   require an explicit target.
8. **A blocked low-ID task could head-of-line block unrelated routable work.**
   Routing now keeps blocked tasks as fallbacks while searching for work that can
   actually progress.
9. **RnS worker→session bindings were ambiguous when one worker owned multiple
   ACTIVE tasks.** Recovery records the ambiguity and refuses to guess.
10. **Criterion claims/verdicts were described as append-only without SQLite
    enforcement.** UPDATE/DELETE are now mechanically rejected by triggers.
11. **Two proven legacy execution-integrity invariants were missing from Lean:**
    writable/forbidden scope overlap checks and declared run-budget enforcement.
    Both were restored in smaller active form.
12. **Budget escalation filenames could contain unsafe task/run identifiers.**
    Artifact filename components are sanitized and containment is regression
    tested.

## Preserved legacy behavior disposition

The replacement runtime now contains deliberate Lean homes for the high-value
legacy behaviors needed before removal:

- canonical SQLite task truth;
- transactional AGI READY gate and scoped claims;
- capability/authority separation and operator policy gates;
- read-first LangGraph routing with separate checkpoint DB;
- hcom as transport only;
- RnS recovery only for known current ACTIVE claims;
- bounded local helper lanes;
- immutable run/context binding and staleness proof;
- report-only writable/forbidden Git scope proof;
- run-budget proof/escalation evidence;
- continuity-aware reviewer independence;
- optional criterion-level implementer evidence/reviewer verdicts;
- preview-first fresh-clone installer and disposable smoke path.

A universal legacy `APPROVED → RELEASED` state machine remains deliberately
rejected. Actual deploy/destructive/external actions stay explicit policy-gated
tasks/actions.

## Static/security review

Current CI runs:

```text
python -m compileall -q runtime tests
ruff check runtime tests --select E9,F63,F7,F82
bandit -q -r runtime -ll -s B608
python -m pip check
python -m unittest discover -s tests -v
python -m runtime.smoke --with-langgraph
bash -n scripts/install_maps.sh
bash scripts/install_maps.sh
```

Bandit B608 is narrowly excluded after inspecting every reported occurrence.
Those queries interpolate only identifier/placeholder structures chosen from
hardcoded internal allowlists; externally supplied values remain SQLite `?`
parameters. No other medium/high Bandit category is disabled.

GitHub Actions run `31850795878` passed every step on the integration head.

## Privacy

`migration/PRESERVATION_PRIVACY_SWEEP.md` records PASS for the current curated
preservation set. That is a current-tree/snapshot audit, not a forensic scan of
all historical Git objects.

## Merge verdict

**PASS — MERGE CANDIDATE.**

The runtime is suitable to merge to `main` subject to the current head remaining
green. After merge, the remaining work is intentionally limited to:

1. verify the merged `main` CI run;
2. run a final active dependency/reference sweep on the merged tree;
3. update stale migration/current-state bookkeeping and remove only obsolete
   active references;
4. verify `main` again.

After those steps, deletion of top-level `legacy/` should be the only remaining
migration action, and that deletion still requires explicit operator approval.
