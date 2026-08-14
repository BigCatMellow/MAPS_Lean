# TASK-321 Security Rereview

- reviewer: helper-security-task321-rereview-midi
- owner: rotation-replacement-dune-nizu
- reviewed_at: 2026-08-10T03:47:44Z
- scope: Bounded independent rereview of the remediations for BLOCKER-1 and
  REQUIRED-2 from `artifacts/reviews/task321_security_review.md`; no
  implementation or lifecycle mutation.
- verdict: APPROVED (security-framed verdict only; no lifecycle
  approval/release performed)
- current_blockers: none
- current_required_findings: none

## Reviewed Bytes

- `MAP_System/scripts/map_authority.py`:
  `784f3b1dce966bfcd29c6c69e7d68ba9a8278c33073a3e5197ac39b6e2003a3d`
- `MAP_System/tests/test_map_authority.py`:
  `38a1f55026f75e5fdcefc9031988b0af23aa39735d143476cc09b7c8e6616537`
- `MAP_System/artifacts/recovery/map2-phase0-trustworthy-baseline-2026-08-10.md`:
  `859a8371ec64b00b1c51b76778b51ccd29d8c41868c7fcf70f9a452a717dcc10`

The hashes independently matched the review packet supplied by the owner.

## Finding Disposition

### BLOCKER-1: resolved

`_active_writer_services_from_cgroup_v2()` now checks that the current UID's
`user@<uid>.service/app.slice` root exists before checking individual unit
cgroups. An absent root raises `AuthorityError`; it can no longer collapse to
an empty writer list. The mismatch regression test creates evidence for UID
1000, probes as UID 2000, and asserts the fail-closed error. This directly
closes the reported silent fail-open.

### REQUIRED-2: resolved

`_probe_active_local_writer_services()` returns both the writer list and the
evidence source (`systemctl` or `cgroup_v2_fallback`). `authority_status()`
surfaces that source as `writer_service_probe_source`, uses `unavailable` on
probe failure, and preserves fail-closed topology classification. The CLI
status payload exposes the same field. Tests cover both evidence sources and
the status-level fallback disclosure, so a clean fallback result is no longer
operationally indistinguishable from a clean primary probe.

## Security Checks

- Missing current-UID cgroup root: fails closed.
- Missing cgroup-v2 marker: fails closed.
- Malformed, duplicated, or unreadable `cgroup.events`: fails closed.
- Unrelated `systemctl` errors: do not enter the fallback.
- Populated maintenance writer: remains blocking.
- Recent RnS watcher collision: remains blocking; the quiet-window filter is
  shared by the primary and fallback paths.
- Timer coverage: the processless timer is omitted only in the cgroup path;
  its process-bearing maintenance service remains checked, while the primary
  path retains the timer check.

## Verification

```text
python -m unittest MAP_System.tests.test_map_authority
  MAP_System.tests.test_map_authority_notify
Ran 59 tests in 0.453s — OK

python -m py_compile MAP_System/scripts/map_authority.py
  MAP_System/tests/test_map_authority.py
PASS

validate_task_mirrors.py
Task mirror validation passed.

validate_shared_state_tasks.py
active-lane table matches map.db
```

## Residual Informational Observations

The original review's INFO-1 (the operational assumption that the visible
cgroup-v2 tree is authoritative kernel evidence) and INFO-2 (pre-existing
handling of `systemctl` return codes 3/4) remain informational. Neither is a
demonstrated regression in the reviewed remediation, and neither creates a
current BLOCKER or REQUIRED finding for TASK-321.

## Final Verdict

**APPROVED.** BLOCKER-1 and REQUIRED-2 are resolved in the reviewed bytes. No
current security BLOCKER or REQUIRED findings remain within this bounded
rereview scope.
