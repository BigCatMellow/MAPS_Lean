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
| Scope/write boundary | AGI + helper/run boundary | OUTPUT RESERVATION + HELPER SCOPE ACTIVE; frozen run-manifest scope still separate follow-up |
| Pre-dispatch policy | `runtime/policy/` | PROMOTED — PR #10 |
| Halt state | `runtime/policy/halt.py` | PROMOTED — PR #10 |
| LangGraph routing | `runtime/routing/` | PROMOTED — PR #10 |
| LangGraph checkpoints | dedicated checkpoint DB | PROMOTED USING OFFICIAL SQLITE SAVER — PR #10 |
| Agent reconciliation | explicit worker/session bindings | OLD FIXED IDENTITY MODEL NOT PROMOTED |
| RnS / liveness / retry | `runtime/recovery/` | PROMOTED SMALLER FORM — PR #12 |
| hcom transport | `runtime/communication/` | PROMOTED — PR #11 |
| Ollama helper | `runtime/helpers/ollama.py` | PROMOTED BOUNDED FORM — PR #13 |
| Aider helper | `runtime/helpers/aider.py` | PROMOTED BOUNDED FORM — PR #13 |
| Installer | `scripts/install_maps.sh` | PROMOTED PREVIEW-FIRST FORM — TASK-014 |
| Fresh smoke | `runtime/smoke.py` | PROMOTED + CI VERIFIED — TASK-014 |

## P0 invariants preserved

1. **One claim winner.** Concurrent attempts cannot both acquire the same READY task.
2. **Lease recovery.** Stale claims can recover without stealing live work.
3. **No self-review.** Submission authorship is distinct from durable ownership.
4. **Explicit promotion gate.** AGI validation and READY mutation are one guarded transaction.
5. **Write boundary.** Active output paths reserve scope; bounded helpers enforce parent output scope.
6. **Policy before dispatch.** Consequential policy flags route to operator gate until explicit approval exists.
7. **Halt is durable and inspectable.** Halt state blocks lanes without rewriting task truth.
8. **Routing is not authority.** LangGraph emits recommendations; guarded TaskStore operations mutate truth.
9. **Communication is not task truth.** hcom state remains transport/session evidence only.
10. **Recovery does not invent work.** RnS verifies existing ACTIVE task + claimant + session binding before resume.
11. **Local models are bounded helpers.** Ollama/Aider cannot approve or complete parent work.
12. **Installer is reversible.** Preview first, project/user-local writes, no credentials, no WezTerm requirement.

## Verification

GitHub Actions run `31845946112` executed the full stacked tree on Python 3.12:

```text
64 tests
64 PASS
ResourceWarning treated as error
```

The configured run installed LangGraph and the SQLite checkpointer and passed the real checkpoint integration test. A separate disposable smoke passed the full SQLite task lifecycle to `DONE`, verified FK/WAL/busy-timeout settings, and proved LangGraph checkpoints use a separate database. Installer Bash syntax and preview execution also passed.

The first full-stack run found an incorrect test/smoke assumption about `MutationResult.data`. That was fixed to `.task`, propagated to the stacked branches, and then reverified green.

## Known legacy problems deliberately not reproduced

- multiple mutable task mirrors;
- fixed agent/window roster as authority;
- WezTerm-specific recovery destination;
- LangGraph checkpoint tables mixed into task truth DB;
- hcom state treated as task authority;
- blanket local-helper autonomy;
- giant legacy runner/policy surfaces where a smaller deterministic rule is sufficient.

## Remaining execution-integrity follow-ups

These were preserved by the archaeology pass but are intentionally separate from the first control-plane promotion:

- frozen run manifest for high-risk/resumable executions;
- continuity-lineage reviewer independence across session rotation;
- criterion-level evidence records beyond the current durable submission/review split;
- filesystem run-scope verification for general core agents, beyond current output reservation/helper enforcement;
- optional read models/metrics only when they earn their cost.

The migration snapshots remain until these decisions are closed and the reviewed stack reaches `main`.

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
- [x] core promoted regression equivalents pass as one integrated stack;
- [x] fresh-clone installer/smoke path executes without reading `legacy/` or migration source.

**Do not delete `legacy/` yet.** These boxes describe the stacked branch, not reviewed/merged `main`. Deletion still requires deferred independent review/merge, final reference/privacy sweep, and explicit operator removal approval.
