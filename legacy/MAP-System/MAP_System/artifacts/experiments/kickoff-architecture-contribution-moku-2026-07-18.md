# KICK-01 Architecture Contribution — Moku

- Status: `evidence-only`
- Scenario: `KICK-01` / `TASK-233`
- Contributor: `helper-review-steward-moku`
- Scope: later read-only coordination card; no implementation or authority change

## Independent conclusion

The smallest safe later change is a **new read-only coordination projection**
for live core agents and process-bound visible helpers. It must preserve four
separate observations—hcom presence, `status.json` durable status, SQLite claim
state, and event-log action history—rather than derive a synthetic "agent
status." This directly answers the frozen scenario's operator question.

The later task is **not ready to implement immediately**: TASK-227 remains
`CHANGES_REQUESTED`, and the active CommandCenterUI checkout identified by the
existing runtime-health record (`/home/home/Projects/CommandCenterUI`) is not
present in this environment. The installer template exists, but template/live
deployment parity is explicitly unverified. A task that edits only the template
could leave the operator's running card unchanged.

## 1. Smallest implementation boundary and seams

### Boundary

Add one `GET /api/map/coordination` read-model endpoint and one passive sidebar
card. The endpoint may read only these existing sources:

| Field | Source and authority | Required rendering rule |
|---|---|---|
| Live presence | `hcom list --json`, through existing `read_presence()` / `hcom_list_json()` | Include only process-bound live core agents and visible helpers; label it `live presence`. |
| Durable status | `MAP_System/agents/status.json` | Render durable `status`, `reason`, and `resume_after` separately with whole-file read age. No per-agent freshness may be inferred. |
| Active claim | `MAP_System/map.db`, opened read-only | `IN_PROGRESS` + claimant + unexpired lease is active. Expired lease is an attention reason, not owned work. Task JSON and graph do not decide claim liveness. |
| Latest durable action | `MAP_System/events/events.jsonl` | Render only the latest valid action-bearing event for the identified sender, retaining event timestamp/order. It is history, not liveness or completion proof. |
| Attention | Source-labelled set from hcom and SQLite | Preserve zero-or-more reasons; never collapse them into a single severity/status. |

Likely source/UI/test seams:

- `MAP_System/templates/install/command-center-ui/app/server.py`: add a pure
  snapshot builder plus `GET /api/map/coordination` beside the existing
  read-only `/api/presence`, `/api/attention`, and `/api/map/health` routes.
  Reuse `read_presence()` only for the live boundary; do not use
  `task_summary()` or `workflow/task_graph.json` for claim liveness. Open
  `map.db` read-only; never call `sync_rns_provider_limits()` or an action path.
- `MAP_System/templates/install/command-center-ui/src/chat.html`: add one
  named coordination section adjacent to, not merged into, `In the room` and
  `Needs you`.
- `MAP_System/templates/install/command-center-ui/src/chat.js` and `chat.css`:
  poll/render source labels, ages/timestamps, `unknown`, and conflict literally.
- `MAP_System/agents/README.md`: document field authority, file-level
  freshness, and conflict/unknown behavior only if the final task includes
  this documentation contract.
- `MAP_System/tests/test_coordination_surface.py` and
  `MAP_System/scripts/run_tests.sh`: add and register deterministic fixture
  tests.

This boundary is **ESSENTIAL**. A broad rewrite of presence, task queue,
attention inbox, watcher, or agent-status writers is not needed.

### Deployment source question

`artifacts/command-center-ui/task-182-map-health-cards.md` records an active
external CommandCenterUI checkout, while this workspace contains an
installer-bundled template. The expected external `app/server.py` path is
absent here. Before creating an implementation task, name the deployable
source, installer/update mechanism, and allowed output paths. This is an
**ESSENTIAL** precondition, not a reason to silently substitute a template
edit for a live UI change.

## 2. Minimal acceptance-test matrix

| Test | Fixture | Required assertion | Class |
|---|---|---|---|
| Normal read model | One process-bound live agent, matching durable entry, valid unexpired SQLite claim, valid sender event | Each field carries its own source and time/age; no write occurs. | ESSENTIAL |
| Stale durable disagreement | hcom `listening`; durable `standby/out_of_tokens` with passed `resume_after` | Show both observations plus `conflict/unknown`; do not assert capacity or replace either value. | ESSENTIAL |
| Newer action does not freshen durable state | Durable file mtime `T0`; sender event `T1 > T0`; live presence snapshot | Event time remains action evidence; durable field shows whole-file age and per-agent freshness `unknown`. | ESSENTIAL |
| Expired claim | `IN_PROGRESS` SQLite row with claimant and lease before read time | Report no active claim and source-labelled `expired claim` attention; do not render owned in-progress work. | ESSENTIAL |
| Bad/missing source | Malformed event or unavailable status/SQLite source | Render the affected field/reason as `unknown` or source error without borrowing another source's value. | LIKELY |
| UI contract | Render the three staged fixtures in the actual card | DOM/text assertions prove labels for live presence, durable status, claim, action, and attention are simultaneously visible. A staged screenshot is supporting evidence, not the only test. | ESSENTIAL |
| Read-only boundary | Test endpoint path with write-capable helpers mocked or forbidden | No write to `map.db`, `status.json`, events, hcom, or RnS sync; no control/action is exposed by the card. | ESSENTIAL |

The three mixed-state fixtures are mandatory. A happy-path card could look
correct while hiding the stale-state failure this scenario tests. A per-agent
`updated_at` migration, terminal-view polish, filtering/sorting preferences,
and caching are **OPTIONAL** after the contract is proven.

## 3. Scope risks, dependencies, and stop questions

| Item | Evidence / risk | Class | Required disposition |
|---|---|---|---|
| Source authority contract | Claims, live presence, durable board, and event history have distinct authorities. | ESSENTIAL | Include the contract in acceptance criteria; no synthetic status. |
| Deployment parity | The known live external checkout is absent; only installer sources are present here. | ESSENTIAL | Identify live/editable source and deployment verification before implementation. |
| TASK-227 ownership/rework | TASK-227 is `CHANGES_REQUESTED`, owned by `claude-lab-gome`; its review requires this same contract. | ESSENTIAL | Do not use KICK-01 to edit the plan or transfer ownership. |
| Identity matching | hcom base/session names, durable board entries, and claims may not share one identifier. | ESSENTIAL | Define and fixture the join key; unmatched rows remain explicit. |
| Meaningful-event predicate | Event log is append-only and file order is not wall-clock order; actions may be missing. | LIKELY | Define an action-bearing filter and fallback `unknown`. |
| Event/source performance | Four local reads are likely small, but event scan/poll cost is unmeasured. | INVESTIGATE | Measure only if live/fixture reads are slow; no cache/worker now. |
| Per-agent durable freshness | `status.json` has only file-level freshness. | INVESTIGATE | Do not change schema in the first task. |
| Incident roles / new policy | KICK-01 forbids policy adoption and the research is advisory. | ESSENTIAL boundary | Keep attention labels informational; add no role, authority, or automation. |

## 4. Later-task readiness recommendation

**INVESTIGATE / defer implementation.** The coordinator can use this report
to write an implementation-ready brief only after resolving the deployable
source boundary and carrying forward the four-source contract and fixtures.
The candidate task should be medium risk, read-only, independently reviewed,
and explicitly exclude new state storage, writer changes, background
automation, Pi, helper-authority changes, and incident-role policy.

## Evidence consulted

- `MAP_System/artifacts/experiments/map-kickoff-alignment-scenario-2026-07-18.md`
- `MAP_System/artifacts/experiments/coordination-surface-readiness-audit-2026-07-18.md`
- `MAP_System/artifacts/reviews/task227-review-lilo.md`
- `MAP_System/tasks/TASK-227.json`, `MAP_System/tasks/TASK-233.json`
- `MAP_System/agents/README.md`, `MAP_System/db/claims.py`
- `MAP_System/templates/install/command-center-ui/app/server.py`
- `MAP_System/templates/install/command-center-ui/src/chat.html`, `src/chat.js`, `src/chat.css`
- `MAP_System/artifacts/command-center-ui/task-182-map-health-cards.md`
- `MAP_System/scripts/run_tests.sh`
