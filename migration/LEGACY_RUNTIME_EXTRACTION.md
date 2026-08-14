# Legacy Runtime Extraction Plan

Status: `PROMOTED_IN_REVIEW_STACK`
Source commit: `77723d16f77efc5e1fe03a74adab920dc7534f16`
Source root: `legacy/MAP-System/MAP_System/`
Staging root: `migration/legacy-runtime-source/`

## Goal

Preserve the minimum proven implementation and tests needed to rebuild the MAPS Lean control plane before `legacy/` is removed.

The retained behavior has now been promoted into a provider-neutral **stacked review branch series**. These changes are not yet on `main`; independent review/merge is intentionally deferred by operator instruction.

## Classification

| Area | Lean target | Current disposition |
| --- | --- | --- |
| SQLite task lifecycle | `runtime/state/` | PROMOTED — PR #9 |
| Task allocator/transitions | `runtime/state/` + CLI | PROMOTED CORE LIFECYCLE — PR #9 |
| Review separation | state/review API | PROMOTED — PR #9 |
| Scope/write boundary | AGI + helper/run boundary | PROMOTED — task reservation, helper scope, immutable run scope |
| Pre-dispatch policy | `runtime/policy/` | PROMOTED — PR #10 |
| Halt state | `runtime/policy/halt.py` | PROMOTED — PR #10 |
| LangGraph routing | `runtime/routing/` | PROMOTED — PR #10 |
| LangGraph checkpoints | dedicated checkpoint DB | PROMOTED USING OFFICIAL SQLITE SAVER — PR #10 |
| Agent reconciliation | explicit worker/session bindings | OLD FIXED IDENTITY MODEL NOT PROMOTED |
| RnS / liveness / retry | `runtime/recovery/` | PROMOTED SMALLER FORM — PR #12 |
| hcom transport | `runtime/communication/` | PROMOTED — PR #11 |
| Ollama helper | `runtime/helpers/ollama.py` | PROMOTED BOUNDED FORM — PR #13 |
| Aider helper | `runtime/helpers/aider.py` | PROMOTED BOUNDED FORM — PR #13 |
| Installer | `scripts/install_maps.sh` | PROMOTED PREVIEW-FIRST FORM — PR #14 |
| Fresh smoke | `runtime/smoke.py` | PROMOTED + CI VERIFIED — PR #14 |
| Run manifest / staleness | `runtime/state/integrity.py` | PROMOTED SMALLER FORM — TASK-015 |
| Git run-scope proof | `runtime/integrity/` | PROMOTED REPORT-ONLY FORM — TASK-015 |
| Continuity-aware review | state + routing | PROMOTED — TASK-015 |
| Criterion evidence | state/review | PROMOTED OPTIONAL MODE — TASK-015 |
| Universal release state | none | REJECTED FOR LEAN CORE; use risk-tiered review summary + explicit policy-gated release/deploy tasks |

## P0 invariants preserved

1. **One claim winner.** Concurrent attempts cannot both acquire the same READY task.
2. **Lease recovery.** Stale claims can recover without stealing live work.
3. **No self-review.** Submission authorship is distinct from durable ownership; continuity successors are also disqualified when independent review is required.
4. **Explicit promotion gate.** AGI validation and READY mutation are one guarded transaction.
5. **Write boundary.** Active output paths reserve scope; helpers and frozen runs enforce parent output scope.
6. **Policy before dispatch.** Consequential policy flags route to operator gate until explicit approval exists.
7. **Halt is durable and inspectable.** Halt state blocks lanes without rewriting task truth.
8. **Routing is not authority.** LangGraph emits recommendations; guarded TaskStore operations mutate truth.
9. **Communication is not task truth.** hcom state remains transport/session evidence only.
10. **Recovery does not invent work.** RnS verifies existing ACTIVE task + claimant + session binding before resume.
11. **Local models are bounded helpers.** Ollama/Aider cannot approve or complete parent work.
12. **Installer is reversible.** Preview first, project/user-local writes, no credentials, no WezTerm requirement.
13. **A run is frozen evidence.** High-risk/resumable execution can bind task revision, context hashes, worker/session, scope, limits, and base revision immutably.
14. **Verification does not repair silently.** Git scope/staleness checks report drift and never reset/restore/clean user work.
15. **Evidence claim != independent verification.** Optional criterion mode stores implementer claims and reviewer verdicts separately.

## Verification

Latest integrated GitHub Actions run: `31847038026`.

```text
79 tests
79 PASS
ResourceWarning treated as error
```

The configured run installed LangGraph and the SQLite checkpointer and passed the real checkpoint integration test. The disposable smoke passed the full SQLite task lifecycle to `DONE`, verified FK/WAL/busy-timeout settings, and proved LangGraph checkpoints use a separate database. Installer Bash syntax and preview execution also passed.

TASK-015 additionally verified task/context staleness, temporary-Git run-scope reporting, transitive continuity review rejection, optional criterion verification, and raw-SQL immutability of run manifests/context hashes.

## Known legacy problems deliberately not reproduced

- multiple mutable task mirrors;
- fixed agent/window roster as authority;
- WezTerm-specific recovery destination;
- LangGraph checkpoint tables mixed into task truth DB;
- hcom state treated as task authority;
- blanket local-helper autonomy;
- giant legacy runner/policy surfaces where a smaller deterministic rule is sufficient;
- a universal `APPROVED → RELEASED` state machine that duplicates already-canonical task/review evidence.

## Execution-integrity disposition

The high-value second-pass items are now deliberately closed:

- immutable run manifest for high-risk/resumable execution — **IMPLEMENTED**;
- continuity-lineage reviewer independence — **IMPLEMENTED**;
- general Git run-scope verification — **IMPLEMENTED, REPORT-ONLY**;
- criterion-level evidence — **IMPLEMENTED AS OPTIONAL MODE**;
- universal separate release state — **REJECTED FOR LEAN CORE**;
- optional read models/metrics — **DEFER UNTIL EVIDENCE JUSTIFIES THEM**.

The migration snapshots remain until the reviewed stack reaches `main` and the final reference/privacy sweep is complete.

## Removal gate for `legacy/`

On the **current stacked branch**, the primary runtime homes now exist:

- [x] critical runtime source snapshot exists outside `legacy/`;
- [x] critical tests exist outside `legacy/`;
- [x] migration/install references exist outside `legacy/`;
- [x] active SQLite/state implementation exists under `runtime/`;
- [x] AGI readiness is enforced by the READY transition;
- [x] LangGraph router uses the active task store and separate checkpoint DB;
- [x] hcom adapter exists and has no authority side effects;
- [x] RnS works without mandatory WezTerm;
- [x] local helper wrappers are adapted to Lean task records/HPOM boundaries;
- [x] execution-integrity P0 behavior has active homes;
- [x] promoted regression equivalents pass as one integrated stack;
- [x] fresh-clone installer/smoke path executes without reading `legacy/` or migration source.

**Do not delete `legacy/` yet.** These boxes describe the stacked branch, not reviewed/merged `main`. Deletion still requires deferred independent review/merge, final reference/privacy sweep, and explicit operator removal approval.
