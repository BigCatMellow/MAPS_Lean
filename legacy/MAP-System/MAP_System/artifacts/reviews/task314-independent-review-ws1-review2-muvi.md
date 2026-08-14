# Review: TASK-314 WS-1 Command Center Authority-Freshness Display

task_id: TASK-314
reviewer: ws1-review2-muvi
task_owner: rotation-replacement-mimi-koda
review_date: 2026-07-30
review_claim: REV-TASK-314-ws1-review2-muvi-ac19bf58
review_scope: Fresh Biggie-local review from canonical criteria and live behavior; no prior reviewer work was inherited.

## Verdict

APPROVED

TASK-314 satisfies its acceptance criteria. The template and live Biggie
CommandCenterUI files are byte-identical, the running localhost server exposes
the new read-only authority endpoint, the served page and assets contain the
badge implementation, and both required focused test files pass independently.
No BLOCKER or REQUIRED findings remain.

## Acceptance Criteria Check

| # | Result | Independent evidence |
|---|---|---|
| Command Center displays authority host, revision, last successful sync, and freshness classification | PASS | Live `GET http://127.0.0.1:8765/api/map/authority` returned `FRESH`, host `192.168.1.153`, a `sha256:` revision, and a current `last_successful_sync_at`. Served HTML contains `#authority-status`; served JavaScript maps `FRESH`/`STALE`/`UNAVAILABLE`/`INVALID` to badge classes and places host, revision, and sync time in the badge tooltip. |
| No remote Smalls write; cross-PC deployment/parity is deferred | PASS | The TASK-314 backup-to-live delta consists only of four additive local changes. The new server endpoint has no request parameters and invokes fixed argv ending in `map_authority.py status`; that command only reads and prints local mirror authority status. No deploy, sync, task mutation, POST route, or remote file operation was added. |
| Focused tests cover fresh/stale/unavailable; independent review before approval | PASS | `test_command_center_authority_freshness.py` independently passed 5/5, covering fresh, stale, gateway failure, malformed/missing freshness, and endpoint wiring. This review is outside the claude-lab-mimi / rotation-replacement-mimi-koda lineage and was atomically claimed through `map-authority`. |

## Files Reviewed

- `MAP_System/artifacts/recovery/ws1-command-center-consumer-local.md`
- `MAP_System/templates/install/command-center-ui/app/server.py`
- `MAP_System/templates/install/command-center-ui/src/orchestrator.html`
- `MAP_System/templates/install/command-center-ui/src/orchestrator.css`
- `MAP_System/templates/install/command-center-ui/src/orchestrator.js`
- `MAP_System/templates/install/command-center-ui/version.json`
- `MAP_System/tests/test_command_center_authority_freshness.py`
- `MAP_System/tests/test_command_center_deployment_parity.py`
- `MAP_System/scripts/run_tests.sh`
- `/home/mellow/Projects/CommandCenterUI/app/server.py`
- `/home/mellow/Projects/CommandCenterUI/src/orchestrator.html`
- `/home/mellow/Projects/CommandCenterUI/src/orchestrator.css`
- `/home/mellow/Projects/CommandCenterUI/src/orchestrator.js`
- `/home/mellow/Projects/.map-task314-backup-20260730T222819Z/`

## Functional Review

- The four template/live file SHA-256 pairs match exactly.
- The live listener is reachable only at the configured localhost surface,
  `127.0.0.1:8765`.
- The running Python process has loaded the new code: the new
  `/api/map/authority` handler returns HTTP 200 and a real authority payload.
  Merely changing files on disk could not add this handler to an old Python
  process.
- The live page still returns HTTP 200 and serves the new badge markup,
  polling code, and CSS state classes.
- Freshness remains a first-class value. `STALE` is displayed as a warning
  while a successful status call remains `ok: true`; transport or malformed
  authority data degrades to `UNAVAILABLE`.
- Host, revision, and last-sync values are presented in the badge tooltip,
  while the compact visible badge text presents the freshness classification.

## Backup Verification

The path named in the review request,
`/home/mellow/Projects/CommandCenterUI/.map-task314-backup-20260730T222819Z/`,
does not currently exist. The backup was preserved one directory higher at
`/home/mellow/Projects/.map-task314-backup-20260730T222819Z/`, exactly as the
submission artifact discloses: keeping an unmanifested directory inside the
live bundle makes manifest generation fail.

The relocated backup is legitimate pre-edit evidence:

- it contains exactly the four expected relative files;
- all four timestamps are `2026-07-30 18:28:19 -0400`, before the live files'
  `19:52:22 -0400` timestamps;
- none contains TASK-314 endpoint/badge markers;
- backup-to-live diffs are pure additions: the summary function and GET route,
  one badge element, four CSS rules, and the JavaScript poller/init wiring;
- no existing line is deleted or modified by the isolated TASK-314 delta.

## Security Review Pass

This pass was performed separately because TASK-314 adds a network-facing
endpoint.

- **Authentication / exposure:** the live service is bound to
  `127.0.0.1:8765`, not a remote interface. The endpoint returns status only.
- **CSRF / drive-by:** the new route is a parameterless GET with no state
  change. A foreign-origin request returns no permissive CORS header, so normal
  browser same-origin policy prevents reading it cross-origin.
- **Injection:** subprocess argv is fixed; no URL/query/header value reaches
  the command. UI values are assigned through `textContent`, `className`, and
  `title`, not `innerHTML`.
- **Path traversal:** the endpoint takes no path or file input and performs no
  file resolution.
- **Identity attribution:** the endpoint exposes authority host/mode/revision
  reported by the existing `map-authority status` contract; it does not invent
  an owner, reviewer, or operator identity.
- **Malformed/failure behavior:** command failure and missing freshness degrade
  to `UNAVAILABLE`; the focused tests cover both.
- **Scope:** existing POST/write controls elsewhere in CommandCenterUI predate
  TASK-314. The isolated backup-to-live delta adds no POST handler or
  write-capable control surface.

## Findings

| Severity | File | Finding | Required action |
|---|---|---|---|
| RECOMMENDED | `MAP_System/artifacts/recovery/ws1-command-center-consumer-local.md` | The full-suite count says `82 pass / 1 fail / 83 total`, while `run_tests.sh` currently contains 84 checks and the submitter's final durable relay/snapshot reports `83 pass / 1 fail / 84 total`. This does not affect TASK-314's acceptance evidence because both required suites were reproduced directly. | Correct the historical count when the artifact is next maintained; no implementation change or rereview is required. |
| OPTIONAL | `MAP_System/artifacts/recovery/ws1-command-center-consumer-local.md` | The backup is no longer at the in-bundle path named in the review request. The artifact already records its legitimate relocation and the backup remains intact. | When citing the rollback location, use `/home/mellow/Projects/.map-task314-backup-20260730T222819Z/`. |

## Independent Verification

- `map-authority task show TASK-314` — PASS; canonical state was `SUBMITTED`,
  owner `rotation-replacement-mimi-koda`, with the three reviewed acceptance
  criteria.
- `map-authority claim-review TASK-314 ws1-review2-muvi` — PASS; canonical
  review claim created.
- `python3 MAP_System/tests/test_command_center_deployment_parity.py` — PASS,
  7/7.
- `python3 MAP_System/tests/test_command_center_authority_freshness.py` — PASS,
  5/5.
- `python3 -m py_compile .../app/server.py
  MAP_System/tests/test_command_center_authority_freshness.py` — PASS.
- `node --check .../src/orchestrator.js` — PASS.
- `MAP_System/scripts/map-git diff --check -- <TASK-314 paths>` — PASS.
- Live curl checks for `/`, `/api/map/authority`, `/orchestrator.js`, and
  `/orchestrator.css` — PASS.
- `ss -ltnp '( sport = :8765 )'` — PASS; listener on `127.0.0.1:8765`.

## Forbidden Changes Check

This review made no implementation, live CommandCenterUI, Smalls deployment,
task-owner, or direct database changes. Its only durable workspace change is
this independent review artifact. Canonical review claim/verdict mutations use
the sanctioned `map-authority` route.
