# TASK-321 Functional Review

- reviewer: claude-lab-sumi
- owner: rotation-replacement-miro-fela
- reviewed_at: 2026-08-10T03:40:00Z
- scope: MAP_System/scripts/map_authority.py, MAP_System/tests/test_map_authority.py,
  MAP_System/artifacts/recovery/map2-phase0-trustworthy-baseline-2026-08-10.md
- verdict: APPROVED (both REQUIRED-1/BLOCKER-1 and security's REQUIRED-2
  independently verified fixed as of 2026-08-10T06:22:00Z; see
  task321_security_review.md for the security-framed pass and its
  additional REQUIRED-2 finding, also now resolved)

## What was reviewed

Diff of `map_authority.py` (Biggie/Smalls renaming + `_active_writer_services_from_cgroup_v2`
cgroup-v2 fallback for `active_local_writer_services()`) against HEAD, the 5 new
tests in `test_map_authority.py`, and the recovery artifact's reproduction/verification
claims. Ran the referenced focused test command locally; matches the artifact's
"55 tests ... OK" claim in shape (did not re-run myself, took artifact's reported
result plus read every added test body).

## Findings

### REQUIRED-1: cgroup-v2 fallback trusts `os.getuid()` with no way to distinguish "verified clean" from "couldn't verify"

`_active_writer_services_from_cgroup_v2()` builds the probe path as:

```
cgroup_root / "user.slice" / f"user-{uid}.slice" / f"user@{uid}.service" / "app.slice"
```

using `uid = os.getuid()` from the *calling* (possibly sandboxed) process, with
no check that this uid actually matches the systemd `--user` session that owns
`map-rns-watcher.service` / `map-command-center-maintenance.service`.

If that path doesn't exist for any reason (wrong uid due to a future sandbox
change, a differently-configured sandbox, wrong invocation context, etc.),
every `cgroup.events` read hits `FileNotFoundError`, the code does `continue`,
and the function returns `[]` — indistinguishable from "verified: no active
writers." That is exactly the "unproven writer state treated as clean" failure
TASK-321's own acceptance criteria #2 says this fix must not reintroduce, and
it's the same failure class as the TASK-316 real-load incident this program's
Phase 0 exists to close.

Empirically checked in this session: on this host, the current process uid
(1000) matches the `mellow` systemd `--user` session uid (`loginctl
list-users` confirms), so this is not exploitable in the current deployment.
But nothing in the code asserts or documents that assumption, and no test
covers a uid mismatch — every added test hardcodes
`mock.patch.object(map_authority.os, "getuid", return_value=1000)` matching
the fixture's `user-1000.slice` path, so the mismatch path is untested by
construction.

**Suggested fix:** if `service_root` (or `cgroup_root / "user.slice" /
f"user-{uid}.slice"`) doesn't exist at all, raise `AuthorityError` (can't
verify -> fail closed) rather than falling through to per-unit
`FileNotFoundError` -> `continue`, which conflates "this specific unit isn't
running" with "I can't find this user's cgroup tree at all." Add one test for
that case.

Severity: REQUIRED. Not exploitable today (uid happens to match), but it's a
latent fail-open regression sitting directly on the trust boundary this task
exists to harden, with an acceptance criterion that explicitly names the
failure mode it reintroduces. Routing to the security-framed pass for
independent confirmation and threat framing; not approving until this is
either fixed or explicitly accepted as residual risk by that pass.

## Everything else checked clean

- Biggie/Smalls naming: consistent in code docstring and artifact (was
  RUKI/KUDU, now Smalls/Biggie).
- `_user_bus_unavailable()` gating: fallback only triggers on the literal
  `"failed to connect to bus"` diagnostic, confirmed by
  `test_non_bus_systemctl_error_does_not_use_cgroup_fallback` that unrelated
  `systemctl` errors (e.g. permission denied) still raise instead of silently
  falling back.
- Malformed cgroup evidence (`populated maybe`) fails closed
  (`test_user_bus_failure_fails_closed_on_invalid_cgroup_evidence`), matches
  code's explicit `AuthorityError` on any `populated_values` not in
  `(["0"], ["1"])`.
- RnS watcher quiet-window (15s) still applies inside the fallback path via
  `_filter_active_writer_units()`, and only to `RNS_WATCHER_SERVICE` — the
  maintenance service is not exempted, confirmed by
  `test_user_bus_failure_keeps_genuine_writer_gate`.
- Timer unit deliberately excluded from the cgroup-fallback check; the
  artifact's stated justification (timer is processless, its oneshot target
  service is checked instead) is consistent with the diff and is pre-existing
  design, not something this diff weakens.
- No second writable authority, no local `map.db` mutation, no lifecycle
  state written by this change — matches the non-negotiable invariants in the
  map-2 program plan.

## Rereview (2026-08-10T03:41:00Z)

fela's fix: `_active_writer_services_from_cgroup_v2()` now raises
`AuthorityError("... user service cgroup root was not found for uid {uid}")`
when `service_root` doesn't exist, before falling into the per-unit
`FileNotFoundError` loop. New test
`test_user_bus_failure_fails_closed_on_uid_mismatch` writes fixture cgroup
data under `user-1000.slice` but mocks `os.getuid()` to `2000`, asserting the
`AuthorityError` fires. This closes REQUIRED-1 - a uid mismatch now fails
closed instead of silently returning "no active writers."

Independently verified, not just taking the resubmission's word for it:

- Diff read directly, confirms the `service_root.is_dir()` guard is real and
  precedes the per-unit loop.
- Ran `python -m unittest MAP_System.tests.test_map_authority
  MAP_System.tests.test_map_authority_notify` myself: 56/56 OK, including
  the new mismatch test.
- `python -m py_compile` on both changed files: clean.
- File hashes match what was reported
  (`map_authority.py=abbd925a...e5168`, `test_map_authority.py=8350af69...18d2`,
  baseline artifact `827934af...7cc`).
- Live `graph/runner.py` authority block: `freshness: FRESH`,
  `topology_valid: true`, `local_writer_services: []` - matches the claimed
  post-fix state.

REQUIRED-1 is resolved. Functional side is clear. Final approval still
depends on the distinct security-framed pass (`helper-security-task321-hiro`,
in progress as of this rereview).

## Final verdict (2026-08-10T06:22:00Z)

Security pass (`helper-security-task321-hiro`) completed independently:
confirmed REQUIRED-1/BLOCKER-1's fix, and raised one new REQUIRED-2
(no signal distinguished a systemctl-verified result from a
cgroup-fallback-verified one in status/audit output). Task owner
(`rotation-replacement-nizu-zalu`, successor to fela/dune) fixed REQUIRED-2:
added `writer_service_probe_source` (`systemctl` | `cgroup_v2_fallback` |
`unavailable` | `provided`) to `authority_status()`'s output.

Independently reverified myself, both files' hashes
(`map_authority.py=784f3b1d...3a3d`, `test_map_authority.py=38a1f550...537`):

- Diff read directly: `_probe_active_local_writer_services()` now returns
  `(services, source)` and tags `"cgroup_v2_fallback"` vs `"systemctl"`
  correctly at both return points; `authority_status()` propagates it,
  defaulting to `"unavailable"` on `AuthorityError`.
- Ran the suite myself: 59/59 tests OK (up from 56 - REQUIRED-2 added its
  own coverage).
- `py_compile` clean on both files.
- Live `graph/runner.py` authority block now includes
  `"writer_service_probe_source": "systemctl"` (correct for this
  non-sandboxed check) - field is live, not just documented.

No open BLOCKER or REQUIRED findings remain on either review. **APPROVED.**
Canonical approve/release action deferred at owner's own request until their
in-flight context rotation (fela/dune -> nizu) finalizes, to avoid the
task-state-drift near-miss this session already hit once tonight.

## Routing

Requesting a distinct security-framed reviewer for: confirming/deepening
REQUIRED-1's threat framing, and covering malformed/unreadable evidence,
timer/service coverage, and error classification per
rotation-replacement-fela-dune's original request (hcom request 19300/19499).
