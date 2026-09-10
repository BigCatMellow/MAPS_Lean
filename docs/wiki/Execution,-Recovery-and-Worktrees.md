# Execution, Recovery and Worktrees

MAPS_L binds resumable execution to durable task/run/session identity, then
uses RnS (Rise & Shine) for bounded recovery. The recovery system does not
invent work, steal a live claim, or assume that a stopped session is safe to
resume.

Back to [[Home]]. See [[Task, Run and Flow Lifecycle]] for how runs and sessions
are created and linked.

## What is implemented

The current production path can:

1. create an immutable run manifest with `maps flow start`;
2. bind that run to a real provider/hcom session with
   `maps run bind-session`;
3. observe configured hcom sessions, including stopped-session reconstruction;
4. open and schedule bounded recovery incidents;
5. resolve a stopped session back to its canonical run;
6. perform optional pre-resume validation;
7. route an opted-in resume through `HarnessService.resume()` and the
   `CanonicalRunGuard`; and
8. record a real `resume_denied` instead of resuming when the canonical guard
   rejects the operation.

The real-stall exercise merged in PR #298 demonstrated a genuinely live hcom
session becoming stopped, resolving to its bound run, and producing
`HOOK_DENIED` with underlying `LEASE_EXPIRED`. That closed the core
canonical-resume exposure required by H5. It did **not** prove every Hook path.

## `recovery-tick`

`maps recovery-tick` runs one bounded pass and exits. Important options:

| Option | Effect |
| --- | --- |
| `--binding WORKER=SESSION_NAME` | explicitly identifies sessions to observe; without bindings it does not guess |
| `--repo-root PATH` | enables advisory quick-tier validation for resumes in that checkout |
| `--enforce-validation` | makes a concrete failed quick validation block the resume; default off |
| `--enforce-canonical-run --harness-project-id P` | routes resumes through the fail-closed canonical-run guard; requires `--repo-root`; default off |
| `--terminate-denied-sessions` | after persistent canonical denial reaches its terminal ceiling, attempts one guarded `HarnessService.stop()`; requires canonical enforcement; default off |

The ordinary `maps claim` piggyback does not enable these opt-in enforcement
paths.

## Canonical denial and lease expiry

The canonical guard checks that the task/run/session relationship remains
valid. A denial is recorded as `resume_denied` and placed in a distinct
`denied` incident state. It does not consume the ordinary transient retry
budget or get mislabeled as `retry_budget_exhausted`.

Repeated canonical denial has its own ceiling and becomes
`canonical_denial_persistent`. With `--terminate-denied-sessions`, that terminal
promotion attempts one bounded guarded stop. Failure to stop does not change
the denial result into a successful recovery.

An expired task lease is repaired through claim recovery under the manifest's
original worker identity. `maps heartbeat` cannot revive an already expired
lease. See
[`docs/CONTROL_PLANE_SETUP.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/docs/CONTROL_PLANE_SETUP.md)
for the current operator runbook.

## Stopped and tagged hcom sessions

The adapter supports hcom versions whose `list --stopped --json` output is not
actually JSON by reconstructing stopped sessions from hcom events. Alive and
reconstructed records are deduplicated.

Tagged hcom agents may have a display name such as `<tag>-<base_name>` while
other records carry the bare `base_name`. Resolution now compares both forms
and only accepts a unique match. Ambiguous base-name collisions are not
guessed.

## `HCOM_DIR` precedence

The effective hcom state directory follows this order:

```text
explicit --hcom-dir / hcom_dir
> inherited HCOM_DIR environment variable
> hcom's .hcom fallback
```

When an explicit directory conflicts with inherited `HCOM_DIR` after path
resolution, the adapter warns once and uses the explicit value. This behavior
was corrected in PR #317.

## Git worktree identity

When `maps flow start` receives `--base-revision`, the run manifest can record
the checkout's Git worktree identity. Passing `--require-worktree-binding`
makes readable worktree identity mandatory.

`--require-worktree-binding` also requires `--base-revision`. Passing it alone
now fails loudly with `WORKTREE_BINDING_REQUIRES_BASE_REVISION`; it is not a
silent no-op.

On the real enforced recovery path, a worktree-bound continuing operation can
be denied with:

- `RUN_WORKTREE_UNAVAILABLE` — the expected or current worktree identity cannot
  be read; or
- `RUN_WORKTREE_MISMATCH` — recovery is attempting to continue from a different
  worktree.

The production recovery result currently flattens Hook vetoes to
`HOOK_DENIED`; the specific worktree guard codes were verified through the
guard reproduction and check ordering documented in the capability evidence.
That caveat is preserved rather than presenting the command output as more
specific than it is.

Capability row 6.16 is **DONE**. This means worktree identity is bound and
enforced on the demonstrated recovery path. It does not mean MAPS_L creates,
cleans, snapshots, or rehydrates worktrees automatically. Sandboxes/snapshots/
rehydration remain **NOT STARTED**.

## Worktree practice for repository development

Writable dispatched work in a shared clone uses a separate Git worktree and
branch. The worktree prevents one agent from switching, cleaning, or resetting
another lane's checkout. It does not grant merge authority.

The procedural owner is
[`playbook/WORKTREE_ISOLATION.md`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/playbook/WORKTREE_ISOLATION.md).
Do not duplicate its command recipe here.

## Still incomplete

- Capability 6.4 remains **IN PROGRESS**: the production stop caller exists,
  but `BEFORE_DESTRUCTIVE_ACTION` still needs its first real exercised evidence,
  and planned write/credential guards are not complete.
- H4 remains **IN PROGRESS**: quick validation can be enforced, but the broader
  validation-hook exit gate and first row-specific real exercise are incomplete.
- Automatic provider health checks and helper resume remain unimplemented.
- Snapshot/rehydration support is not implemented.

Sources: current
[`runtime/recovery/`](https://github.com/BigCatMellow/MAPS_Lean/tree/main/runtime/recovery),
[`CanonicalRunGuard`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/runtime/policy/harness_guard.py),
and the
[`capability checklist`](https://github.com/BigCatMellow/MAPS_Lean/blob/main/work/roadmaps/CAPABILITY_CHECKLIST.md).
