# Environment-evidence-writer authority — re-decision after PR #204

Date: 2026-08-31
Owner: `/root`
Status: design-only. No runtime behavior changed by this note.
Trigger: `runtime/recovery/production.py` module docstring (HEAD `410d60c`,
lines ~78-85) — *"when a production writer of `run_environment_evidence` is
introduced, the authority question above must be answered again on its own
merits — who may write those rows, and whether their `validation.quick`
should run unattended — and not inherited from this note."*

PR #204 (`SEC/6.24` slice 1, merged) made `runtime/flow_start.py` step 4 that
writer. `laze` caught the trigger firing (rule 10/14). This note answers the
re-decision. The `#206` follow-up is a minimal factual doc correction only;
it does **not** make this decision.

**Bottom line: the security posture did NOT regress. No runtime behavior
change is required to keep it safe. This note is a ratification + a documented
defense-in-depth mechanism for later, not an urgent impl task.** (Per the
dispatch STOP condition: the honest answer does not require a runtime change,
so no urgent flag — see "Q3" for the proof.)

---

## Re-verified facts at HEAD `410d60c` (rule 14)

### The new writer — `runtime/flow_start.py`

- `flow_start()` step 4 runs **only** when `store.get_task(task_id)` returns a
  record whose `"environment"` key is not `None` (lines ~150-166). A task with
  no environment contract records nothing and behaves byte-identically to
  before #204.
- The write is `_record_environment_evidence(store, run_id, environment_contract,
  repo_root)`, which:
  - reads `spec_ref = str(contract["spec_ref"])` — the operator-authored value
    in the task's `environment` contract;
  - `spec = load_environment_spec(root / spec_ref)` — loads the
    **operator-authored, checked-in spec file** from `repo_root` verbatim;
  - `fingerprint = inspect_local_environment(spec, repo_root=root)` — the
    containment-checked E2 inspector that already ships (does not follow
    dependency inputs outside the repo); "adds no new probing capability" per
    its own docstring;
  - calls `store.record_run_environment_evidence(run_id, spec=spec,
    fingerprint=fingerprint, spec_ref=spec_ref, recorded_by="maps-flow-start")`.
- If that recording fails, the whole flow fails
  (`_failed("environment_evidence", evidence)`). The write path is
  fail-closed: a contracted task with a malformed / sensitive spec cannot
  complete `flow start`.
- `flow_start`'s `repo_root` defaults to `"."`; `maps flow start` passes
  `--repo-root` (also defaulting to `.`).

### The trust boundary — `runtime/state/environment.py::record_run_environment_evidence`

Unchanged by #204. It already:
- requires a non-empty `recorded_by` and stamps it on the row and on the
  `RUN_ENVIRONMENT_RECORDED` task event;
- fail-closes `spec_ref` and all three JSON snapshots
  (`EnvironmentSpec` / `EnvironmentFingerprint` / compatibility report)
  through `redact_sensitive_text(...) != ...` → `SENSITIVE_ENVIRONMENT_*`;
- fail-closes `fingerprint.environment_spec_hash != spec.sha256` →
  `ENVIRONMENT_SPEC_FINGERPRINT_MISMATCH`;
- requires an already-existing `run_manifests.run_id` (→ `RUN_NOT_FOUND`);
- rows are insert-only — an `UPDATE`/`DELETE` is refused by a DB trigger
  ("run environment evidence is immutable").

### The consumer — `runtime/recovery/production.py::RunBoundValidator`

- `validate_for_run(run_id)` reads
  `self.environment_reader.list_run_environment_evidence(str(run_id))`. It
  **does not read, filter on, or branch on `recorded_by`** — a row is a row.
- It re-derives safety before executing anything:
  - `spec_ambiguous` skip if the run's rows carry >1 distinct
    `environment_spec_hash`;
  - takes `rows[-1]`, requires `spec_snapshot` to be a `Mapping`, else
    `spec_unparseable`;
  - `parse_environment_spec(dict(snapshot))`, else `spec_unparseable`;
  - **re-hashes**: `if stored_hash and spec.sha256 != stored_hash:` →
    `spec_hash_mismatch`, **not executed**;
  - only then `run_validation_tier(spec, "quick", repo_root=root,
    executor=self._bounded_executor(...))`.
- `VALIDATION_TIER = "quick"` is hard-wired; `normal`/`full` are unreachable
  from here.
- Bounded: `max_validations` per tick, per-tier and per-tick wall-clock
  budgets, `_ValidationBudgetExceeded`.
- Every return value is advisory: `{"attempted": ...}` under the key
  `resume_validation`. No branch of `tick()` consults it to allow/deny a
  resume **unless** the operator *also* passes `maps recovery-tick
  --enforce-validation` (default-off, itself requiring `--repo-root`).

### The unattended-execution gate — `runtime/cli.py` `recovery-tick`

- `--repo-root` is `default=None`, with an explicit comment: *"Deliberately
  unlike `context --repo-root` and `flow start --repo-root`, which both
  default to '.'. An ambient cwd default here would silently run declared
  validation commands... validation must be opted into by explicitly naming a
  checkout. Absent, no validator is constructed and no command runs."*
- The `maps claim` piggyback path calls `run_recovery_tick_isolated(store,
  hcom_timeout_seconds=CLAIM_PIGGYBACK_HCOM_TIMEOUT_SECONDS)` with **no**
  `validation_repo_root` — a `RunBoundValidator` is never constructed there.
- `run_recovery_tick_isolated(...)` builds a `RunBoundValidator` **iff**
  `validation_repo_root is not None`.

### Precedent

The `#204` design note
(`work/notes/2026-08-31-environment-report-production-source-cache-design.md`)
already states the authority model for exactly this write (Q3): *"The
authority to say 'this task must not route without a proven environment' is
the operator who authors the task contract — the same authority that already
sets `spec_ref` and `max_age_seconds`."* And its Q1c rationale: *"the
`task_environment` row is itself the opt-in."*

This is the same shape as the SEC3 `destructive: bool` / #198 `embedded: bool`
residuals **only** in that a structural field (`recorded_by`) names an
unauthenticated process actor. It differs in the consequential way: nothing
downstream treats `recorded_by` as an authority claim — `RunBoundValidator`
ignores it entirely.

---

## Q1 — Who may write `run_environment_evidence` rows via flow-start? Is `recorded_by="maps-flow-start"` sufficient authority?

**Yes, it is sufficient. The flow-start write needs no operator-gating flag
and no `--enable-environment-evidence` opt-in beyond the `environment`
contract it already requires.**

Reasoning:

1. **`recorded_by` is provenance, not authority.** It is stamped and stored
   as a fact about *who recorded* the row. No consumer — not
   `RunBoundValidator`, not routing's `select_recorded_environment_reports`,
   not `_advisory_environment_evidence` — reads it to decide whether to act.
   It unlocks nothing. Making it "sufficient authority" is a category
   question that doesn't arise: the row's *effect* is gated elsewhere.
2. **The row's content authority is the operator, twice over.** The
   `spec_snapshot` is `load_environment_spec(repo_root/spec_ref)` — a
   checked-in file, reviewed like any other code in that repo. Which spec is
   loaded is fixed by `contract["spec_ref"]`, set only through
   `store.update_contract(task_id, {"environment": {...}})`
   (`runtime/state/environment_contract.py`), which changes task
   revision/readiness validation — i.e. operator-authored, review-gated task
   state. flow-start **synthesizes nothing**; it copies an
   operator-authored file and hash-pins it.
3. **The `environment` contract is the opt-in.** Step 4 is unreachable for a
   task without one. This is the `--enforce-canonical-run` /
   `--enforce-validation` / `required_for_routing` model applied at contract
   granularity — a deliberate, per-task, default-off opt-in — exactly as the
   #204 note designed and as this codebase does everywhere else.
4. **The write path is fail-closed.** Hash mismatch, sensitive text, missing
   run, and any inspection failure all abort the row (and the flow).
5. **Symmetry with the deferred alternative.** The #204 note's rejected
   alternative was a `maps environment-probe <task> --repo-root` operator
   command. That would have carried *the same* `recorded_by` question with a
   *weaker* content guarantee (an operator could point `--repo-root` at an
   arbitrary tree). flow-start, tied to the run it just created in the
   checkout the flow ran in, is the tighter binding, not the looser one.

**No operator-identity registry is needed here** (contrast SEC4 Half 3, which
gates *state transitions* an operator asserts). Environment evidence is a
mechanical observation of a checked-in spec against the local tree; there is
no operator *assertion* to authenticate.

---

## Q2 — Can `maps recovery-tick --repo-root` now run `validation.quick` unattended against a flow-start-sourced row? Does the `validation_repo_root` gate still suffice?

**Yes it can, and yes the gate still suffices. A flow-start-sourced row does
NOT need to be distinguishable from an operator-sourced one before quick-tier
runs against it.**

What actually changed: before #204, `record_run_environment_evidence` had
zero production writers, so `RunBoundValidator.validate_for_run` returned
`no_spec_bound` for *every* real incident and `--repo-root` was a latent,
inert capability. After #204, contracted tasks that went through `flow start`
have a row, so `maps recovery-tick --repo-root X` on such an incident will
parse the snapshot and execute the spec's `quick`-tier commands (shell=True)
in checkout `X`.

Why the gate still suffices:

- **The operator explicitly authorizes the execution site.** `--repo-root` has
  no default, is never inferred from cwd, and is never set on the `maps claim`
  piggyback. Running `maps recovery-tick --repo-root X` *is* the operator
  saying "run each about-to-be-resumed incident's declared quick-tier commands
  in X." The flag's help text says precisely this.
- **The executed commands are operator-authored and double-checked.** They are
  the `validation.quick` block of the checked-in spec, captured verbatim,
  hash-pinned at write time (`ENVIRONMENT_SPEC_FINGERPRINT_MISMATCH`) and
  **re-hashed at read time** (`spec_hash_mismatch` → not executed). A party
  who tampers with the stored snapshot gets a skip, not an execution.
- **The tier and blast radius are bounded.** `quick` only; per-tick count cap;
  per-tier and per-tick wall-clock budgets; advisory unless
  `--enforce-validation` is *also* explicitly passed.
- **No new privilege in kind.** The `recovery/production.py` docstring's
  escalation concern — "a party who can insert evidence rows can cause shell
  commands to run as the user running the pass" — is unchanged in *kind*.
  Post-#204, "a party who can insert rows" = "a party who can run `maps flow
  start` on a contracted task in a checkout whose `spec_ref` file they
  control." Such a party, to then get unattended execution, still needs an
  operator to run `recovery-tick --repo-root` against that run — and if the
  attacker *is* that operator (or controls that checkout and runs the pass),
  they already have shell there. The evidence row adds no reach.

The one real operational shift: an operator who runs `recovery-tick
--repo-root` **without realizing rows now exist** will now actually execute
quick-tier commands where before it was a no-op. That is an
operator-awareness matter, addressed by the doc correction (#206) and the
CAPABILITY_CHECKLIST annotation below — not a posture regression, because the
operator is still the one passing the flag that the help text fully
describes.

---

## Q3 — Is (1)+(2) safe by construction? Is the honest answer "posture did not regress, here is the proof"?

**Yes. Confirmed against the code, not `laze`'s preliminary read alone.**

The posture, stated precisely, is: *unattended `quick`-tier command execution
on the recovery path requires (a) a `run_environment_evidence` row bound to
the incident's run, AND (b) an operator explicitly naming a checkout via
`recovery-tick --repo-root`; the commands executed are the operator-authored
spec verbatim, hash-verified twice; only `quick` runs; the result is advisory
unless `--enforce-validation` is also explicitly passed.*

Every clause of that posture is **unchanged** by #204:

| Posture clause | Status after #204 | Evidence |
|---|---|---|
| (b) operator must pass `--repo-root`, no cwd default, never on `claim` piggyback | unchanged | `runtime/cli.py` `recovery-tick` `--repo-root default=None` + comment; `run_recovery_tick_isolated` builds validator iff `validation_repo_root is not None` |
| commands = operator-authored spec verbatim | unchanged | flow-start loads `repo_root/spec_ref`, synthesizes nothing |
| hash-verified at write | unchanged | `record_run_environment_evidence` `ENVIRONMENT_SPEC_FINGERPRINT_MISMATCH` |
| hash-verified at read, fail-close | unchanged | `RunBoundValidator` `spec_hash_mismatch` before `run_validation_tier` |
| `quick` tier only | unchanged | `VALIDATION_TIER = "quick"` |
| bounded budget | unchanged | `max_validations`, tier/tick wall-clock budgets |
| advisory unless `--enforce-validation` | unchanged | `tick()` gate is opt-in, default-off |
| rows insert-only, immutable | unchanged | DB trigger |
| sensitive text fail-close | unchanged | `SENSITIVE_ENVIRONMENT_*` |

What changed is **clause (a)'s frequency**: rows now commonly exist for
contracted tasks instead of never existing. That is not a weakening of a
gate — it is the intended activation of a capability the recovery module was
*explicitly built to accommodate* ("this wiring is deliberately inert until a
production writer of run-bound environment evidence exists", `RunBoundValidator`
docstring). The re-decision clause fired exactly as designed; answering it
confirms the design, it does not patch a hole.

---

## Q4 — If a distinction were ever needed: the smallest mechanism

Not needed now (Q1-Q3). Documented so a future stricter posture has a
pre-agreed shape and does not get designed inside a broad PR.

**If** an operator ever wants "unattended `quick`-tier may run only against
evidence a human deliberately recorded, not against auto-recorded
flow-start rows", the minimal mechanism is:

- **A `recorded_by` allowlist check at the `RunBoundValidator` read site.**
  `recorded_by` is already stamped and stored on every row. Add an optional
  `trusted_recorded_by: frozenset[str] | None = None` constructor arg to
  `RunBoundValidator`; when set, `validate_for_run` skips with a new reason
  `spec_source_not_trusted` if `row.get("recorded_by")` is not in the set.
  Default `None` = today's behavior (any row). Surfaced as an opt-in
  `maps recovery-tick --trusted-evidence-recorder <actor>` (repeatable),
  default-off.
- **No schema change. No new column. No new table.** The distinguishing datum
  exists.
- The allowlist would list the actors a human uses for deliberate recording
  (a future `maps environment-probe` command's `recorded_by`, or an operator
  id), explicitly *excluding* `"maps-flow-start"`.

This is strictly additive and default-off; it is a future item, not part of
answering the re-decision.

---

## MUST-NOT list for any eventual impl

- MUST NOT add operator-gating / an opt-in flag to the **flow-start write**
  itself — the `environment` contract is the opt-in (Q1). Adding a second
  gate would diverge from the #204 note and from the
  `required_for_routing` / `--enforce-*` model.
- MUST NOT make `RunBoundValidator` (or `tick()`) branch on `recorded_by` by
  default — the Q4 allowlist is opt-in, default-`None`, and inert until an
  operator names trusted recorders.
- MUST NOT add a schema column, table, or migration to distinguish row
  sources — `recorded_by` already distinguishes them.
- MUST NOT change the `--repo-root` gate, the `quick`-tier restriction, the
  budgets, or the advisory-by-default nature of `resume_validation`.
- MUST NOT make a flow-start-recorded row block routing or resume on its own
  — that still requires `required_for_routing` (routing) or
  `--enforce-validation` (resume), both operator-authored, both default-off.
- MUST NOT introduce an operator-identity registry for environment evidence —
  there is no operator *assertion* in an environment observation (contrast
  SEC4 Half 3).
- MUST NOT widen `RunBoundValidator` to `normal`/`full` tiers as part of this.

## Smallest-first-slice (only if the operator asks for defense-in-depth)

1. `RunBoundValidator(trusted_recorded_by=None)` + the
   `spec_source_not_trusted` skip reason. Pure addition; default path
   unchanged; covered by a unit test asserting `None` = any row and a set
   excludes `"maps-flow-start"`.
2. `maps recovery-tick --trusted-evidence-recorder <actor>` (repeatable,
   default empty = `None`). Threaded through
   `run_recovery_tick_isolated` → `RunBoundValidator`.
3. Docs: `docs/CONTROL_PLANE_SETUP.md` — when to use it.

Nothing in slices 1-2 changes behavior unless the flag is passed.

## STOP conditions for that impl

- If the allowlist check turns out to need `recorded_by` to be *authenticated*
  (rather than just matched as a string), STOP — that is the SEC4-Half-3
  operator-identity question bleeding in, and environment evidence was
  explicitly held to *not* need it (Q1). Flag `niko`.
- If implementing the skip reason requires `tick()` to learn about evidence
  sources (rather than `RunBoundValidator` owning it entirely), STOP — the
  #160 / #165 source guards that keep `supervisor.py` ignorant of validation
  types must keep passing.
- If the flag's absence would change any existing test's expected output,
  STOP — it must be inert until passed.

## OPERATOR DECISION REQUIRED (ratification, not a blocker)

The technical answer is "posture did not regress" (Q3). One acceptance is
nonetheless the operator's to record, because it is a threat-model
acceptance rather than a code fact:

> **Is a task's `environment` contract sufficient operator authority for
> that task's runs to have `run_environment_evidence` rows that become
> `quick`-tier-executable under an explicit `maps recovery-tick
> --repo-root`?**

Recommended answer: **yes** — it is the same authority that already sets
`spec_ref`, `max_age_seconds`, and `required_for_routing`, and the executed
commands are the operator-authored checked-in spec, hash-verified twice,
`quick`-tier only, under an explicitly-named checkout. The Q4 allowlist is
available as opt-in defense-in-depth if the operator wants flow-start rows
held to a lower trust tier than deliberately-recorded ones.

If the operator declines to accept this, the fallback is **not** a runtime
change to flow-start — it is to build the Q4 slice and default
`--trusted-evidence-recorder` to a value that excludes `"maps-flow-start"`,
making unattended execution require deliberately-recorded evidence.

## Roadmap impact

Does not change any capability status. Answers the re-decision the
`recovery/production.py` docstring demanded, with the conclusion "posture
unregressed, no runtime change required". Optional 1-line annotation on the
`CAPABILITY_CHECKLIST.md` E4 row (design-pending / re-decision answered) — no
status flip. The `#206` doc correction and this note together retire the
"must be re-decided later" clause: it has now been re-decided.

---

## Resume prompt

You are (only if the operator explicitly asks for environment-evidence-source
defense-in-depth) implementing the Q4 slice of
`work/notes/2026-08-31-env-evidence-writer-authority-redecision-design.md`.
Work in a worktree off `origin/main`; `git fetch origin main`; re-verify
every callsite in this note's "Re-verified facts" section at your HEAD
(rule 14) first.

If the operator has NOT asked for that — there is nothing to implement. The
re-decision is answered: posture did not regress (this note's Q3 table).
Confirm the `#206` doc correction landed and stop.

If implementing Q4:

1. Add `trusted_recorded_by: frozenset[str] | None = None` to
   `RunBoundValidator.__init__` in `runtime/recovery/production.py`. In
   `validate_for_run`, after selecting `row = rows[-1]` and before parsing
   the snapshot, if `self.trusted_recorded_by is not None` and
   `str(row.get("recorded_by") or "")` not in it, return
   `self._skip("spec_source_not_trusted", ...)`. Add
   `"spec_source_not_trusted"` to `VALIDATION_SKIP_REASONS`.
2. Thread an optional `trusted_recorded_by` through
   `run_recovery_tick` / `run_recovery_tick_isolated` to the
   `RunBoundValidator(...)` construction (only when a validator is built).
3. `runtime/cli.py`: `recovery-tick --trusted-evidence-recorder` (append,
   default `[]`); pass `frozenset(x) or None`.
4. Docs: `docs/CONTROL_PLANE_SETUP.md`.

MUST NOT: any schema change; branch on `recorded_by` when the arg is unset;
change `--repo-root`, tier, budgets, or advisory-by-default behavior; teach
`supervisor.py` about evidence sources (keep the #160/#165 source guards
green).

Verification: one blocking foreground
`python3 -m unittest tests.test_recovery_production_trigger
tests.test_recovery_composition_root tests.test_recovery_supervisor
tests.test_flow_start tests.test_run_environment_evidence` — no Monitor, no
background. `python3 -m runtime.smoke` exits 0. Push before any full-suite
run; rely on CI.

Then: PR into `main` (never push to main). Independent review per
`reference_committee_review` (mutation testing min 5 for code; not needed if
docs-only). Reviewer commits `work/reviews/pr-<N>-review-evidence.md`. No
self-merge. Report the PR number to `niko`.

Stop conditions: this note's "STOP conditions for that impl".
