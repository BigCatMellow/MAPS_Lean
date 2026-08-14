# TASK-321 Security-Framed Review

- reviewer: helper-security-task321-hiro (spawned by claude-lab-sumi)
- owner: rotation-replacement-fela-dune
- reviewed_at: 2026-08-10T03:40:15Z
- updated_at: 2026-08-10 (two post-remediation re-checks, same session)
- scope: Distinct adversarial pass on `MAP_System/scripts/map_authority.py`'s
  cgroup-v2 writer-service fallback (`_active_writer_services_from_cgroup_v2`,
  `_user_bus_unavailable`, and the updated `active_local_writer_services`),
  per `MAP_System/inbox/helpers/helper-security-task321.md`, following the
  functional review at `MAP_System/artifacts/reviews/task321_review.md`.
- verdict: Both BLOCKER-1 and REQUIRED-2 were fixed by the owner live during
  this review and **independently verified by me** (hashes, code read, and a
  full local test run for each fix — not taken on the owner's word). 2
  informational observations remain open as residual notes, not blockers.
  I am not approving/releasing this task myself; that call belongs to the
  functional reviewer's lane and the task owner, per my scope.

## Post-remediation verification (2026-08-10, same session)

While this review was being written, rotation-replacement-fela-dune pushed a
fix for BLOCKER-1 and reported hashes
`map_authority.py=abbd925a...e5168`, `test_map_authority.py=8350af69...18d2`.
Independently re-verified, not taken on faith:

- `sha256sum` on both files matches the reported hashes exactly.
- `_active_writer_services_from_cgroup_v2` (map_authority.py:750-754) now
  has `if not service_root.is_dir(): raise AuthorityError(...)` before the
  per-unit loop — the uid-scoped root is now required to exist, closing the
  exact `FileNotFoundError` → `continue` → `[]` fail-open path described
  below.
- New test `test_user_bus_failure_fails_closed_on_uid_mismatch`
  (test_map_authority.py:414-431) mocks `os.getuid` to `2000` against a
  fixture built for uid `1000` and asserts `AuthorityError` with
  `"not found for uid 2000"` — this is exactly the untested mismatch path
  the original finding called out, now covered and enforced.
- Re-ran the referenced suite myself:
  `MAP_System/.venv/bin/python -m unittest MAP_System.tests.test_map_authority
  MAP_System.tests.test_map_authority_notify` → `Ran 56 tests ... OK`,
  matching the owner's claim.

BLOCKER-1 is resolved.

A second remediation landed while the first verification was being sent:
the owner (now `rotation-replacement-nizu-zalu`) reported hashes
`map_authority.py=784f3b1d...2003a3d`, `test_map_authority.py=38a1f550...6616537`
fixing REQUIRED-2. Independently re-verified:

- `sha256sum` on both files matches exactly.
- `_probe_active_local_writer_services()` (map_authority.py:789-817) now
  returns `(active_units, source)` where `source` is `"systemctl"` on the
  normal path or `"cgroup_v2_fallback"` when the bus-unavailable branch
  fires; `active_local_writer_services()` wraps it for backward
  compatibility (map_authority.py:785-786).
- `authority_status()` (map_authority.py:198-233) threads this through as
  `writer_service_probe_source` in the status payload — `"provided"` when
  services are injected by a caller, `"unavailable"` on probe error,
  `"not_applicable"` outside mirror mode — without changing the fail-closed
  `topology_valid` logic, which still depends only on `services`/
  `writer_probe_error`, not on which source produced them. That's the
  correct shape: the new field is purely an audit signal, it doesn't change
  trust decisions.
- New tests `test_status_surfaces_cgroup_writer_probe_source` and the
  paired `"unavailable"`-source case (test_map_authority.py:826-872) cover
  both branches.
- Re-ran the suite myself again:
  `MAP_System/.venv/bin/python -m unittest MAP_System.tests.test_map_authority
  MAP_System.tests.test_map_authority_notify` → `Ran 59 tests ... OK`, and
  `python -m py_compile MAP_System/scripts/map_authority.py` → clean,
  matching the owner's claim (they additionally ran mirror validators I did
  not re-run).

REQUIRED-2 is resolved. The two INFO items below were not addressed by
either fix and remain open as residual notes, not blockers.

## Findings

### BLOCKER-1 — RESOLVED: unverified `os.getuid()` produced a silent fail-open on the exact invariant this task exists to protect

Confirming and escalating `task321_review.md`'s REQUIRED-1. The cgroup probe
path is built entirely from the *calling* process's own `os.getuid()`, with
no cross-check against the systemd `--user` session that actually owns
`map-rns-watcher.service` / `map-command-center-maintenance.service`:

```python
uid = os.getuid() if uid is None else uid
service_root = (
    cgroup_root / "user.slice" / f"user-{uid}.slice"
    / f"user@{uid}.service" / "app.slice"
)
```

If `service_root` doesn't exist for *any* reason — uid drift from a future
sandbox change, a different container/namespace uid mapping, a
differently-configured mirror host — every `cgroup.events` read hits
`FileNotFoundError`, `continue`s, and `_active_writer_services_from_cgroup_v2`
returns `[]`. That `[]` is indistinguishable downstream from "verified: no
active writers," so `install_snapshot()` proceeds to overwrite mirrored files
and `map.db` with no evidence the writer services are actually idle.

Why this is a BLOCKER, not a REQUIRED-with-residual-risk:

- This is the identical failure class as the TASK-316 incident that this
  entire Phase 0 program (`map2-phase0-trustworthy-baseline-2026-08-10.md`)
  exists to close, reproduced verbatim in the new code it introduces.
- TASK-321's acceptance criterion #2 is explicit: unproven writer state must
  never be treated as clean. This path treats "I couldn't find the cgroup
  tree" as "clean." That's not an edge case outside the criterion — it's the
  criterion, failing.
- "Not exploitable today" rests entirely on an environmental coincidence
  (sandbox uid == host session uid on this host, confirmed via `loginctl`)
  that the code neither asserts nor documents as a hard requirement. Nothing
  stops it from silently drifting in a future sandbox/container change,
  and when it does, there will be no error, no test failure, no log line —
  just a quietly wrong "clean" result on the authority write path.
- Every added test hardcodes `getuid() == 1000` matching the fixture path
  by construction, so CI cannot catch a regression here; the mismatch path
  is untested because it's un-testable-by-accident, not because it's been
  verified safe.

**Recommended fix (same as functional review):** if the uid-scoped
`service_root` (or its `user-{uid}.slice` ancestor) doesn't exist at all,
raise `AuthorityError` — "can't verify" must fail closed, not fall through
per-unit `FileNotFoundError` → `continue`. Add a test asserting a uid
mismatch raises rather than returning `[]`.

**Status: FIXED and independently verified** — see "Post-remediation
verification" above. `service_root.is_dir()` is now checked and a uid
mismatch raises `AuthorityError` with a message naming the mismatched uid;
covered by `test_user_bus_failure_fails_closed_on_uid_mismatch`.

### REQUIRED-2 — RESOLVED: no signal distinguishes "verified via systemctl" from "verified via cgroup fallback" in status/audit output

Reviewed `active_local_writer_services()`'s caller path (`status`,
`install_snapshot()` around map_authority.py:200-210, 827-833). When the
function returns `[]`, nothing downstream records *which* probe produced
that answer — only `writer_probe_error` is captured, and only when the probe
raises. A `[]` from the cgroup fallback looks byte-for-byte identical, in
every log and status field, to a `[]` from a normal `systemctl --user
is-active` check on a fully-trusted host bus.

This matters specifically because of BLOCKER-1: if the uid-trust assumption
ever silently breaks, there will be no operational signal — not even a
"topology_valid: true but verified via fallback" marker — for anyone to
notice that the "clean" result came from the weaker, less-verified path.
Given this program's stated goal is a *trustworthy, auditable* baseline
after a real fail-open incident, the fallback being invisible in its own
output undermines that goal even independent of BLOCKER-1.

**Suggested fix:** surface which probe path executed (e.g., a
`writer_probe_source: "systemctl" | "cgroup_v2_fallback"` field in status
output, or at minimum a log line when the fallback triggers) so operators
can audit every time the less-verified path was used to authorize a sync.

**Status: FIXED and independently verified** — see "Post-remediation
verification" above. `writer_service_probe_source` now appears in the
status payload with values `systemctl` / `cgroup_v2_fallback` /
`unavailable` / `provided` / `not_applicable`, without altering the
fail-closed `topology_valid` logic.

### INFO-1: cgroup-v2 evidence integrity assumes `/sys/fs/cgroup` is the genuine, unwritable kernel view

`_active_writer_services_from_cgroup_v2` treats `cgroup.events` content as
ground truth once `cgroup.controllers` is found. On a real kernel cgroup v2
mount, `cgroup.events` is kernel-generated and not writable by any userspace
process regardless of privilege, so this is sound *if* `CGROUP_ROOT` is
genuinely the host kernel's cgroupfs. The code never verifies that — it only
checks that `cgroup.controllers` exists as a file, which a synthetic/stub
filesystem could also satisfy. In a sandbox environment specifically built to
have a *restricted* view of the host (that's the whole reason this fallback
exists), it's worth explicitly confirming this bind-mount can't be a
container-local, writable, or otherwise non-authoritative view rather than
the real read-only kernel interface. Not a demonstrated bug — flagging
because it's the same category of "trust an environmental signal without
verifying it reflects host truth" as BLOCKER-1, and because it wasn't
explicitly covered in the recovery artifact's reproduction section (which
only shows the sandbox reading real cgroup data, not that the mount is
guaranteed read-only by construction). Suggest a one-line note in the
recovery artifact documenting this as an accepted operational assumption, if
it hasn't already been verified out-of-band.

### INFO-2 (pre-existing, not introduced by this diff): `systemctl` returncodes 3/4 are treated as "not active" without ever consulting `_user_bus_unavailable`

In `active_local_writer_services()`, the bus-unavailable check only runs in
the `elif probe.returncode not in {3, 4}` branch. If a broken systemd/D-Bus
environment ever returns exit code 3 or 4 *together with* a
bus-connection-failure diagnostic (rather than the generic exit code 1 this
diff's tests assume), that result is silently classified as "unit not
active" — never reaching either the raise-on-real-error path or the new
cgroup fallback. This logic predates this diff (the `{3,4}` allowlist was
already there for the plain "not active" cases), so it's not a regression
this change introduced, but the diff now builds a security-relevant fallback
directly on top of this unverified assumption without re-examining it. Low
severity: requires an unusual systemd version/config to trigger, and untested
either way. Worth a one-time check of what codes `systemctl --user is-active`
actually returns on this host stack when the bus is down, and a comment or
assertion if 3/4 are confirmed to never co-occur with bus failure.

## Checked and found clean

- **Malformed/unreadable evidence**: `populated_values not in (["0"],
  ["1"])` correctly fails closed via `AuthorityError` for any malformed,
  duplicated, or unexpected `cgroup.events` content — confirmed against
  `test_user_bus_failure_fails_closed_on_invalid_cgroup_evidence`. A generic
  `OSError` on read (permission error, I/O error) also raises rather than
  silently continuing; only the specific `FileNotFoundError` (a unit simply
  not running) is treated as "not active" — which is correct in isolation
  and, now that BLOCKER-1 is fixed, no longer combines with an unverified
  uid to produce a false-clean result.
- **Timer/service coverage**: the cgroup fallback deliberately excludes
  `map-command-center-maintenance.timer` and only checks the two
  process-bearing service units. This is sound: a timer's cgroup carries no
  process and thus no writer activity by definition — the actual write
  window is covered by `map-command-center-maintenance.service`'s cgroup
  being populated when it fires. No coverage gap found for the fallback's
  intended purpose (don't clobber an in-progress write).
- **Collision-gate (15s quiet window) bypass**: `_filter_active_writer_units`
  (RNS-watcher-specific quiet check) and the in-lock recheck immediately
  before `os.replace()` in `install_snapshot()` (map_authority.py:859-876)
  apply identically regardless of whether the initial writer list came from
  `systemctl` or the cgroup fallback — both funnel through the same
  `_recently_written()` gate on the same mirrored-write-target file. No new
  bypass path found specific to this diff.
- **Error classification (bus-vs-real-error split)**: confirmed via
  `test_non_bus_systemctl_error_does_not_use_cgroup_fallback` that unrelated
  errors (e.g. permission denied) still raise `AuthorityError` and do not
  silently divert to the fallback. See INFO-2 above for the one unverified
  edge in this classification.

## Routing

Original scope named rotation-replacement-fela-dune (task owner) and
claude-lab-sumi (functional reviewer) as recipients. During this review the
owner identity rotated twice more (fela-dune → dune-nizu → nizu-zalu,
confirmed via `hcom list` and the handoff snapshot chain); findings were
sent to the current owner, `rotation-replacement-nizu-zalu`.
claude-lab-sumi's session went inactive (system cleanup, not a finalized
rotation) with no successor registered on the active roster at review time
— flagged to the owner to relay onward. Not approving or releasing
TASK-321; per scope, this is a findings-only pass. `map_authority.py` was
not edited by me; both fixes described above were made and reported by the
task owner and independently re-verified by me, not applied by this
review.
