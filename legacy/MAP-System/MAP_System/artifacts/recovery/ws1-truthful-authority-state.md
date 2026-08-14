# TASK-310 — Truthful MAP Authority State Contract

- status: implementation planning
- owner: codex-lab-risa
- parent: TASK-309
- decision evidence: hcom thread `map-recovery-ws1-gate`, message 5785
- independent security/structure review:
  `MAP_System_Recovery_2026-07-29/03_kickoff/MAP_RECOVERY_PLAN_REVIEW.md`
- authority topology: Smalls/RUKI writable; Biggie/KUDU mirror-only

## Problem

Biggie can currently run the local graph and validators against its last
installed mirror and report internally consistent results without proving that
the mirror is current relative to Smalls. Internal consistency is useful, but
it is not evidence of global freshness.

The recovery must make that distinction explicit in every operator-facing MAP
state view.

## Contract

Every operator-facing state payload must include an `authority` object with:

| Field | Meaning |
|---|---|
| `mode` | `authority`, `mirror`, or fail-closed `unknown` |
| `authority_host` | Configured authority host; `null` only on the authority itself |
| `authority_revision` | `sha256:<digest>` of the consistent online-backup `map.db` installed or served |
| `authority_observed_at` | UTC time the authority produced that consistent snapshot |
| `last_successful_sync_at` | Mirror-local UTC time the entire snapshot was atomically installed |
| `freshness` | `AUTHORITATIVE`, `FRESH`, `STALE`, `UNAVAILABLE`, or `INVALID` |
| `freshness_age_seconds` | Non-negative age of the last successful install, when trustworthy |
| `freshness_threshold_seconds` | Explicit configured/default threshold used for classification |
| `last_error` | Bounded current sync error, never a secret-bearing transcript |
| `topology_valid` | False if a mirror is writable or local writer services are active |

The authority revision is derived from the database bytes produced by SQLite's
online backup path. It is not a Git revision, local file mtime, task-graph
timestamp, or hash of a hot ordinary file copy.

## Classification

1. `AUTHORITATIVE`
   - mode is `authority`;
   - the production database is writable on the designated authority;
   - no mirror claim is implied.
2. `FRESH`
   - mode is `mirror`;
   - topology is valid and the database is read-only;
   - a complete snapshot install succeeded;
   - the installed database hash equals `authority_revision`;
   - successful-sync age is within the declared threshold.
3. `STALE`
   - a valid last-good snapshot exists;
   - its age exceeds the threshold, or a later sync has failed;
   - views may remain readable but must not say current, green, or globally
     healthy.
4. `UNAVAILABLE`
   - no valid successful snapshot record exists;
   - authority/sync metadata is absent or unreadable;
   - the installed mirror revision cannot be established.
5. `INVALID`
   - mirror database is writable;
   - local writer services are active on a mirror;
   - timestamps are materially in the future or otherwise inconsistent;
   - recorded and installed revisions disagree.

`UNKNOWN` is not a green state. If a consumer cannot parse this contract, it
must present `UNAVAILABLE` or `INVALID`.

## Time and Failure Rules

- The default freshness threshold must be derived from the configured mirror
  interval with a bounded grace window and displayed in the payload.
- Clock skew beyond the documented tolerance fails closed as `INVALID`.
- A failed sync never destroys the last-good revision or successful-sync time.
- A later failure changes a previously valid mirror to `STALE`; it cannot
  overwrite `last_successful_sync_at`.
- A successful atomic rollback retains the prior last-good metadata. A failed
  install cannot advertise the staged revision.
- Error text is bounded and comes from the sync result only; credentials,
  request envelopes, SSH key paths, and transcripts are excluded.

## Required Consumers

- `map-authority status`: canonical machine-readable authority/freshness view.
- LangGraph runner result: embeds the same authority object and cannot emit a
  green/current recommendation when freshness is `STALE`, `UNAVAILABLE`, or
  `INVALID`.
- Generated/current state: records revision and freshness rather than an
  unqualified snapshot claim.
- Command Center health: authority freshness is a first-class source and
  participates in overall severity.

Consumers must share one classification implementation. They may not each
invent different thresholds or reinterpret a failed connection.

## Verification Matrix

| Scenario | Required result |
|---|---|
| Authority host, valid writable database | `AUTHORITATIVE` |
| Mirror just atomically synchronized | `FRESH`, matching revision |
| Smalls disconnected after a prior success | `STALE`, last-good revision retained |
| Smalls unavailable before any valid success | `UNAVAILABLE` |
| Sync age exceeds threshold | `STALE` |
| Mirror database writable | `INVALID` |
| Mirror writer service active | `INVALID` |
| Health timestamp materially in future | `INVALID` |
| Installed DB hash differs from recorded revision | `INVALID` |
| Snapshot install fails and rolls back | prior revision retained; not `FRESH` |

Focused tests must cover every row. Independent review must reproduce the
disconnect/failure cases, not only inspect happy-path fixtures.

## Ownership Gate

Before existing implementation files are added to TASK-310, Smalls must report
their nonterminal output owners. Candidate paths include:

- `MAP_System/scripts/map_authority.py`
- `MAP_System/scripts/map_authority_notify.py`
- `MAP_System/graph/runner.py`
- `MAP_System/templates/install/command-center-ui/app/server.py`
- focused authority and Command Center tests

No candidate path will be edited or registered while another nonterminal task
owns it. New uniquely named implementation/test paths may be registered only
after the same authoritative collision check.

## Rollback

- Keep the old status fields during a compatibility window.
- New fields are additive until every consumer is migrated.
- Reverting a consumer must never restore an unqualified green state; absence
  of the authority object is treated as `UNAVAILABLE`.
- No rollback changes Smalls' one-writer designation or makes Biggie writable.

## Core Implementation Progress

Implemented on collision-free TASK-310 paths:

- `map-authority status` now emits the shared authority object.
- Mirror sync identifies the validated installed database as a
  `sha256:<digest>` revision.
- New authorities attach their online-backup revision and observation time to
  snapshot responses.
- A reported/validated revision mismatch fails before snapshot installation.
- The watchdog records revision, observation time, and last-success time; a
  later failure preserves the last-good fields for truthful `STALE`
  classification.
- `map-authority route` on Biggie injects the mirror freshness contract into
  the live authority route response without changing `graph/runner.py`.

Observed Biggie probe after implementation:

```text
mode=mirror
authority_host=192.168.1.153
database_writable=false
freshness=FRESH
topology_valid=true
authority_revision=sha256:85c6672dfc6ac871ca36b36c896bd10cadb12be36c3d4fc58c239dee0432675a
```

`authority_observed_at` remains `null` until the reviewed snapshot-response
change is deployed to Smalls. This is visible rather than fabricated.

Focused verification:

```text
python -m unittest MAP_System.tests.test_map_authority \
  MAP_System.tests.test_map_authority_notify

Ran 33 tests
OK
```

Covered cases include fresh, stale-after-failure, unavailable, writable-mirror
invalidity, future clock, revision mismatch, authority online-backup revision,
rollback preservation, and mismatch rejection before install.

Runner-source and Command Center-source integration remain intentionally
unmodified because TASK-304 and TASK-306 currently own those paths. See
`MAP_System_Recovery_2026-07-29/03_kickoff/MAP_RECOVERY_SEQUENCE_AMENDMENT_1.md`.

## Continuation (claude-lab-mimi, 2026-07-30) — Fail-Closed Route Gate

- owner: claude-lab-mimi (reassigned from codex-lab-risa; risa unreachable
  during a Codex outage, operator directed a coordinator handoff -- see
  `MAP_System/shared/decisions.md` DEC-036)
- prerequisite: TASK-313 (approved "A1" disposition) retired TASK-304,
  releasing `MAP_System/graph/runner.py` with zero active owners. Registered
  it on TASK-310 via `map-authority task add-output-path` after confirming no
  other nonterminal task references it (`grep -l` across `MAP_System/tasks/`).
  `templates/install/command-center-ui/app/server.py` remains owned by
  TASK-306 (`CHANGES_REQUESTED`) and was not touched.

The remaining "Required Consumers" gap was the fail-closed rule: "LangGraph
runner result... cannot emit a green/current recommendation when freshness is
`STALE`, `UNAVAILABLE`, or `INVALID`." `map-authority route` already attached
the authority object (prior session); it never gated the recommendation
itself.

**Deliberate scope decision: no edit to `MAP_System/graph/runner.py`.**
`runner.py`'s own `main()` has no authority/freshness concept and none was
added -- it stays task-graph-only and recommendation-only, matching TASK-304's
own acceptance criteria ("LangGraph remains recommendation-only... do not add
a second scheduler") and this contract's "Required Consumers" framing (the
runner is *a* consumer of the authority object, not its source). Registering
`graph/runner.py` as a TASK-310 output path was precautionary; the actual gap
lived entirely in `MAP_System/scripts/map_authority.py`, which was already an
unblocked, owned TASK-310 path.

Implemented `apply_freshness_gate(routed, authority)` in `map_authority.py`,
called from both the mirror-mode and authority-mode `route` dispatch paths
(previously each inlined `routed["authority"] = authority_status(config)`
directly, now both go through the shared gate). On `STALE`/`UNAVAILABLE`/
`INVALID`, it overrides `next_route` to `STALE_AUTHORITY` and
`recommended_action` to a message naming the freshness state and error,
while preserving the original recommendation under
`stale_authority_next_route`/`stale_authority_recommended_action` and leaving
all other fields (e.g. `ready_tasks`) untouched -- satisfies "views may
remain readable but must not say current, green, or globally healthy"
without discarding the underlying data.

Live probe (`map-authority route` on Biggie, mirror mode, real sync state):

```text
next_route: review
authority.freshness: FRESH (age 17s, threshold 180s)
stale_authority_next_route present: false
```

i.e. the gate is a true no-op on a fresh mirror -- confirmed by reading the
live output, not just the unit tests.

Added `FreshnessGateTests` (6 cases) to `test_map_authority.py`: fresh and
`AUTHORITATIVE` leave the recommendation untouched; `STALE`/`UNAVAILABLE`/
`INVALID` all gate and name the freshness state; a missing `last_error`
still produces a readable message; the original recommendation is preserved
verbatim; unrelated fields (`ready_tasks`) survive the gate.

```text
python -m unittest MAP_System.tests.test_map_authority \
  MAP_System.tests.test_map_authority_notify

Ran 39 tests
OK
```

## Continuation (claude-lab-mimi, 2026-07-30) — `shared/current-state.md` Consumer

Registered `MAP_System/scripts/render_active_state.py` and
`MAP_System/tests/test_render_active_state.py` on TASK-310 (no collision:
only prior reference was terminal `TASK-291`/`TASK-036`).

Added `authority_line(authority)` to `render_active_state.py`, threaded as an
explicit optional `authority` parameter through `build_projection` →
`render_text` → `render_file`, defaulting to `None` everywhere so every
pre-existing caller/test renders byte-identically to before -- confirmed by a
new `test_omitted_by_default_existing_callers_unaffected` test, and by the
fact all 7 pre-existing `test_render_active_state.py` tests still pass
unmodified. `main()` is the only caller that supplies a real value, computed
once per render from `map_authority.authority_status(load_authority_config())`
-- deliberately excludes the ticking `freshness_age_seconds` field from the
rendered text, so `--check` stays a true no-op between successive syncs
instead of reporting drift on every run (confirmed live: two consecutive
`--check` runs after a real render both report `unchanged`).

On `STALE`/`UNAVAILABLE`/`INVALID`, the line is an explicit bolded warning
naming the freshness state and error, matching the contract's "must not say
current, green, or globally healthy." Per the same contract's "`UNKNOWN` is
not a green state," a failure to even compute the authority object (e.g. an
import error) is itself caught and rendered as `UNAVAILABLE` with the
exception text, not silently omitted -- this caught a real bug during
development: the naive `from MAP_System.scripts.map_authority import ...`
failed with `No module named 'MAP_System'` when the script is invoked by
direct path (`python .../render_active_state.py`, the normal invocation) not
as a package module, because the repo root wasn't on `sys.path` yet. Fixed
with the same `sys.path.insert(0, str(ROOT.parent))` pattern
`graph/runner.py` already uses, and only found because the fail-closed
default surfaced it in the actual rendered file during a live check rather
than silently producing a blank/missing line.

Live probe after the fix:

```text
Authority freshness: `FRESH` — mode=`mirror` host=`192.168.1.153`
revision=`sha256:9e5ef1b1837f05896a42ba17efcd97200b5b9eef36ed8829e889dd84b3e051c5`
last_sync=`2026-07-30T13:24:07.055535Z`
```

`validate_shared_state_tasks.py` still passes after regeneration.

```text
python -m unittest MAP_System.tests.test_render_active_state \
  MAP_System.tests.test_map_authority MAP_System.tests.test_map_authority_notify

Ran 52 tests
OK
```

Remaining for a future task, not this one: Command-Center-facing display of
the authority object (blocked on TASK-306's separate disposition, per the
Ownership Gate above and Amendment 1). All other "Required Consumers" from
this contract are now implemented and tested.

## Codex takeover verification (zeno, 2026-08-01)

- Operator authorized Codex takeover after the original Claude session could
  not be resumed. The expired TASK-310 claim was atomically reclaimed through
  `map-authority`, and accountable ownership was reassigned to `zeno`.
- TASK-314 subsequently implemented the Command Center consumer and received
  an independent `APPROVED` review artifact, closing the consumer gap described
  above without adding Command Center files to TASK-310.
- Biggie now reaches Smalls through Tailscale at `100.127.80.108`; a live
  authority sync and route query report `FRESH`, a matching `sha256:` revision,
  a read-only mirror, no local writer services, and valid topology.
- Focused verification reran 52 authority, watchdog, rendered-state, and
  Command Center freshness tests; all passed.
- `validate_shared_state_tasks.py` reports one pre-existing unrelated drift:
  `shared/current-state.md` still lists TASK-254 as `IN_PROGRESS` while SQLite
  records `RETIRED`. TASK-312 owns `shared/current-state.md`, so TASK-310 did
  not modify that path or bypass its ownership boundary.

### Independent-review topology correction

- The first post-takeover reviewer ran on Smalls, whose checkout intentionally
  still contains the pre-publication code. It therefore issued
  `CHANGES_REQUESTED`: the transported delivery artifact described code that
  was not yet present in that checkout. This was a valid environment-mismatch
  finding, not evidence that Biggie's unpublished implementation lacked the
  contract.
- The correction is to review the actual task-owned Biggie files in place,
  while they remain unpublished and protected by TASK-315's rollback snapshot.
  The resulting independent review artifact must then be transported unchanged
  to Smalls and checksum-verified before canonical approval/release.
- This does not treat Smalls' older checkout as released source or bypass the
  eventual GitHub convergence. It separates pre-publication review from the
  later clean deployment of the reviewed Git commit.

### Independent-review required findings resolved

- Direct `MAP_System/graph/runner.py` output now calls the same shared
  `authority_status()` and `apply_freshness_gate()` functions as
  `map-authority route`. Normal summaries, resumed gate results, and interrupted
  gate responses all carry the authority contract; a non-fresh mirror replaces
  the direct recommendation with `STALE_AUTHORITY` while preserving the prior
  recommendation for inspection.
- Writer-service discovery now fails closed. Missing `systemctl` or an
  unexpected service-manager/probe error produces a bounded diagnostic and an
  `INVALID` mirror topology instead of an empty proven-clean service list.
  Snapshot installation also refuses to continue when that probe cannot prove
  writer inactivity.
- Added explicit classifier coverage for sync age beyond the 180-second
  threshold, active-writer invalidity, unavailable service-manager invalidity,
  and direct-versus-wrapped non-fresh route equivalence.
- The focused authority, notifier, rendered-state, and Command Center suite now
  runs 56 tests and passes. A live host-side probe confirmed both direct runner
  output and `map-authority route` expose `FRESH`, the same authority revision,
  a read-only database, no writer services, and valid topology.
- During review, `map-rns-watcher.service` was found active even though disabled;
  the topology guard correctly prevented mirror refresh. It was stopped and the
  mirror refreshed successfully. The watcher remains disabled so it cannot
  silently recreate a Biggie-side writer/topology collision.
- The complete release suite then exposed a fixture-only regression: an
  explicit scratch `--db` used by `integration_test.py` inherited Biggie's
  production mirror health and was blocked from exercising the isolated graph.
  `runner_authority_status()` now distinguishes the canonical production path
  from an explicitly supplied fixture path. Production still uses the shared
  mirror contract and fails closed; a writable standalone fixture is classified
  locally through the same `authority_status()` schema. The integration test is
  green again (11/11) without weakening production gating.
- Final release verification after that correction: `run_tests.sh` completed
  with `pass=84 fail=0 total=84`.
- A later auto-resumed Smalls reviewer produced another valid stale-checkout
  rejection against the intentionally old Smalls code. That review is retained
  as audit evidence, but the lane was told to stand down: implementation review
  remains Biggie-local until TASK-315 publishes the reviewed commit.
