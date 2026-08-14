# KUDU–RUKI Orchestration Plan

- status: proposal_for_command_center_review
- date: 2026-07-28
- requested_by: operator
- scope: cross-PC MAP orchestration, source convergence, workload routing, health, and recovery
- authority_effect: none until reviewed and promoted through MAP
- proposed_control_plane: RUKI
- proposed_compute_plane: KUDU

## 1. Outcome

Operate KUDU and RUKI as one MAP installation with two machine roles:

- **RUKI is the always-on control plane.** It owns writable task state,
  coordination services, integration state, and cross-host health.
- **KUDU is the compute and implementation plane.** It owns GPU-backed local
  inference, heavier development work, and compute-intensive validation.
- **Git is the program source of truth.** Both PCs run approved commits from
  the same repository instead of evolving through independent file copies.
- **RUKI's SQLite database remains the only writable production MAP state.**
- **SSH is the machine-to-machine transport.** `peer_link.py` is not part of
  the target architecture.
- **Boot starts infrastructure, not the Command Center UI or paid agents.**
  The operator opens the CCL when interactive work is wanted.

The system must continue operating when Codex, Claude, or another subscription
agent runs out of context or is closed. Cloud agents perform work; they are not
the network, scheduler, state authority, or boot mechanism.

## 2. Current Verified Baseline

| Capability | Current state |
|---|---|
| RUKI identity | `home@192.168.1.153`, hostname `MediaCenter` |
| KUDU identity | `mellow@192.168.1.177` |
| MAP SQLite authority | RUKI only |
| KUDU database | Read-only mirror, refreshed once per minute |
| Authority transport | Restricted Ed25519 SSH key with forced command |
| Administrative transport | Separate key-only SSH path |
| Boot persistence | User lingering enabled on both hosts |
| RUKI background services | Authority watcher and maintenance timer enabled |
| KUDU background services | Authority mirror timer enabled |
| Mirror failure reporting | Health JSON plus rate-limited desktop alerts and recovery notice |
| KUDU firewall | OpenSnitch rules installed for RUKI SSH and hcom |
| Program convergence | RUKI was converged to the KUDU program snapshot |
| CCL launch | Fixed seven-tab roster installed and verified on both PCs |
| KUDU GPU | RTX 2060 SUPER, 8 GB VRAM; Ollama is using CUDA successfully |

The baseline proves cross-PC state authority and transport. It does **not** yet
prove safe, automatic source-code synchronization or intentional workload
routing between the machines.

## 3. Target Topology

```text
                         Operator
                            |
               manually opens CCL on either PC
                            |
                   one MAP intake contract
                            |
          +-----------------+-----------------+
          |                                   |
          v                                   v
  RUKI — control plane                KUDU — compute plane
  --------------------                --------------------
  writable map.db                     read-only map.db mirror
  LangGraph route                     GPU/Ollama
  task/review authority               implementation lanes
  maintenance timers                  heavy tests/builds
  integration/release lane            local helper drafts
  health aggregation                  host health publisher
          |                                   |
          +--------- restricted SSH ----------+
          +------------- hcom ----------------+
                            |
                            v
                shared Git repository history
```

### Authority boundary

RUKI's control-plane role does not make every agent running on RUKI an
approver. MAP task ownership, independent review, human gates, and model-tier
rules still apply.

KUDU's greater compute capacity does not give its local model authority.
Local-model output remains bounded, recorded, and core-reviewed.

## 4. Machine Responsibilities

### RUKI: control plane

RUKI should own:

- the writable production `MAP_System/map.db`;
- task claims, leases, events, reviews, approvals, and exported mirrors;
- LangGraph route calculation;
- deterministic maintenance and liveness services;
- cross-host health aggregation;
- release/integration coordination;
- the authoritative record of which Git revision each host should run;
- durable alerts when KUDU is unreachable, stale, or on the wrong revision.

RUKI should avoid:

- sustained local inference;
- duplicate implementation of a task already owned on KUDU;
- serving as a second independently writable source tree;
- depending on an open Codex/Claude session for background coordination.

### KUDU: compute and implementation plane

KUDU should own:

- Ollama and GPU-backed local inference;
- Codex-led implementation and precise file changes;
- expensive test, build, indexing, and analysis jobs;
- bounded local-model summaries, classifications, drafts, and suggestions;
- publishing host health and job results back to RUKI;
- a read-only view of production task state plus restricted remote lifecycle
  commands against RUKI.

KUDU should avoid:

- direct writes to its mirrored `map.db`;
- final approval of its own implementation;
- treating local-model output as canonical;
- automatic source updates over a dirty working tree.

## 5. One Program, Not Two Versions

The program source and the runtime database need different synchronization
models:

| Data | Authority | Distribution rule |
|---|---|---|
| Program source | Shared Git history and an approved revision | Both hosts fetch; each activates the same approved commit |
| Production task state | RUKI SQLite | KUDU uses restricted commands and read-only snapshots |
| File-backed task/status mirrors | Exported from RUKI | Included in validated KUDU authority snapshots |
| Host-local configuration | Each host | Generated from tracked templates plus explicit machine role |
| Logs, caches, virtual environments | Each host | Never synchronized as source |
| Work in progress | Task branch/worktree | Pushed for review; never copied over another host's dirty tree |

### Proposed source release flow

1. A task owner works on a task branch or isolated worktree on either host.
2. The owner pushes the branch to the shared Git remote.
3. A different eligible agent reviews the exact commit.
4. The integration owner merges the approved change.
5. RUKI records the approved revision as the desired MAP revision.
6. Each host runs a deterministic source-sync check.
7. A host activates the revision only when:
   - the repository identity and remote match;
   - the working tree is clean or all local work is in a protected worktree;
   - required tests pass;
   - host-specific install rendering succeeds.
8. Both hosts report the active revision to the health surface.

The sync process must fail closed. It must never reset, overwrite, clean, or
discard local work automatically. Divergence creates an alert and a visible
reconciliation task.

Periodic `rsync` of the live project tree is not the normal source workflow.
It remains a bounded migration/recovery tool only.

## 6. Work Routing

### Default routing matrix

| Work shape | Default machine | Default worker class | Review |
|---|---|---|---|
| Intake, task shaping, architecture, risk | RUKI | Claude/core | Separate core agent |
| SQLite, orchestration, scripts, precise code | KUDU | Codex/core | Claude/core or eligible helper |
| GPU inference, bounded summaries, draft packets | KUDU | Local helper | Owning core agent |
| CPU-light validators and maintenance | RUKI | Deterministic service | Reported to CCL |
| Heavy test suite, indexing, build | KUDU | Deterministic job or core owner | Task-specific |
| Task claims, review claims, release state | RUKI | Authority gateway | Existing MAP gates |
| Git integration and host activation | RUKI-coordinated | Deterministic tool plus accountable owner | Release checks |

Routing is based on task fit and authority, not on which machine happens to
have an open terminal.

### Local-model rule

Ollama may start at boot as infrastructure. A model-backed MAP job must still
have:

- a bounded packet;
- an accountable core owner;
- input and output paths;
- a recorded model identity;
- a visible CCL status and stop control, or a visible terminal;
- core review before its output affects canonical state.

Until CCL exposes that status and stop control, operational local-model jobs
remain visible terminal sessions. There should be no hidden autonomous LLM
agent.

## 7. Boot and Runtime Behavior

### Start automatically

RUKI:

- SSH;
- hcom relay support;
- MAP authority watcher;
- command-center maintenance timer;
- deterministic cross-host health supervisor;
- optional Git revision monitor in report-only mode.

KUDU:

- SSH client capability;
- hcom relay support;
- MAP authority mirror timer;
- Ollama;
- deterministic host-health publisher;
- optional compute worker in report-only/idle mode until explicitly enabled.

### Do not start automatically

- the Command Center UI;
- the AI Command Center Lab window;
- Codex, Claude, Pi, Librarian, or temporary agents;
- paid-model requests;
- a hidden local-model reasoning loop;
- automatic Git merge, reset, checkout over local changes, or release.

### Recovery behavior

- Services retry after network loss with bounded backoff.
- KUDU keeps its last valid read-only state snapshot if RUKI is unavailable.
- No task-state writes are redirected to KUDU during an outage.
- RUKI records KUDU as degraded after a defined heartbeat threshold.
- Recovery produces one notification and clears the active incident.
- Rebooting either host does not require recreating agent identities.

## 8. Health and Alerts

Create one deterministic health contract with these fields per host:

```yaml
host: KUDU | RUKI
role: compute | authority
timestamp: ISO-8601
ssh: pass | fail
hcom: pass | fail | not_required
map_authority: pass | stale | fail
source_revision:
desired_revision:
working_tree: clean | dirty | unknown
services:
gpu: available | unavailable | not_present
ollama: pass | fail | not_required
last_success:
active_incident:
```

Alert conditions:

- RUKI authority unreachable for more than the allowed retry window;
- KUDU mirror older than the freshness threshold;
- host active revision differs from the approved revision;
- required boot service inactive;
- KUDU Ollama unavailable when a local job is queued;
- GPU missing or inference unexpectedly using CPU;
- disk space below a defined threshold;
- dirty working tree blocks an approved activation;
- authentication or snapshot validation failure;
- repeated worker crash or job timeout.

Alert destinations:

1. Durable JSON incident state.
2. CCL **Needs You** / health surface.
3. Rate-limited local desktop notification when a graphical session exists.
4. One recovery event when the condition clears.

Alerts must be edge-triggered and deduplicated. They must not require an LLM,
spam hcom, or open the CCL automatically.

## 9. Security Boundary

- Keep the restricted authority key separate from administrative SSH.
- Keep password authentication disabled.
- Do not place secrets in Git, task files, hcom messages, or plan artifacts.
- Do not expose a new general-purpose TCP listener merely to move jobs.
- Prefer versioned, allowlisted SSH commands with argument-array execution.
- Add RUKI firewall rules before enabling any new network capability.
- Apply least privilege to job submission, status, artifact transfer, and
  cancellation independently.
- Require a functional review and a separate security-framed review for every
  new network-facing or write-capable component.
- Rotate the RUKI account password that was previously exposed in setup
  transcript history if that rotation has not already been completed.

## 10. Implementation Work Packages

These are proposed work packages, not pre-authorized task records.

### WP-1 — Record the two-host architecture

Deliver:

- an approved MAP decision naming RUKI and KUDU roles;
- machine-readable host-role configuration;
- authority and failover boundaries;
- explicit statement that Git source authority and SQLite state authority are
  different.

Acceptance:

- both hosts report exactly one role;
- only RUKI reports writable production database authority;
- the decision is independently reviewed and operator-approved where required.

### WP-2 — Git-based source convergence

Deliver:

- desired-revision manifest;
- clean-tree-safe fetch/check/activate tool;
- host-specific installer render step;
- revision/status reporting;
- rollback to the last approved revision without deleting local work.

Acceptance:

- both hosts report the same approved commit;
- dirty-tree simulation blocks activation without changing files;
- offline, fetch-failure, test-failure, and install-failure cases preserve the
  last working version;
- no live-tree `rsync` is required for normal updates.

### WP-3 — Cross-host health supervisor

Deliver:

- deterministic health schema;
- RUKI aggregator and KUDU publisher;
- incident deduplication, retry, recovery, and CCL status feed;
- boot-safe systemd units.

Acceptance:

- unplug/reconnect, stopped service, stale mirror, wrong revision, disk-low,
  Ollama-down, and GPU-fallback drills produce the expected single incident
  and recovery;
- no Codex, Claude, or local-model tokens are consumed.

### WP-4 — Capability-aware router

Deliver:

- live machine capability inventory;
- routing rules based on task tier, authority, compute need, and health;
- explicit fallback when the preferred machine or worker is unavailable;
- dispatch evidence visible in CCL.

Acceptance:

- architecture/authority work cannot route to a local model;
- GPU work prefers KUDU;
- database lifecycle operations always execute on RUKI;
- unavailable capacity produces a visible fallback or blocked reason.

### WP-5 — KUDU bounded-job lane

Deliver:

- versioned job packet;
- allowlisted submit/status/cancel/result operations;
- bounded workspace and resource limits;
- artifact and provenance record;
- CCL visibility and stop control before model-backed jobs are enabled.

Acceptance:

- duplicate jobs are idempotent;
- malformed, oversized, unauthorized, or traversal-bearing packets are
  rejected;
- cancellation and timeout are verified;
- job output cannot mutate canonical MAP state directly;
- security review passes separately from functional review.

### WP-6 — Unified CCL cross-host surface

Deliver:

- host role, connectivity, revision, services, GPU/Ollama, incidents, and
  queued/running job status;
- operator controls for retry, cancel, and inspect;
- clear distinction between deterministic services and model-backed agents.

Acceptance:

- the operator can answer “what is running, where, why, and who owns it?”
  without opening a hidden tab or SSH session;
- no agent is represented as active solely because a stale durable identity
  exists.

### WP-7 — Failover and recovery runbook

Deliver:

- RUKI outage procedure;
- KUDU outage procedure;
- database restoration procedure;
- deliberate authority-transfer procedure with a one-writer invariant;
- source rollback and divergence reconciliation procedure.

Acceptance:

- tabletop and live drills prove that both databases are never writable
  authorities at the same time;
- last-known-good source and state backups remain recoverable;
- restoration steps are executable without an AI session.

## 11. Dependency Order

```text
WP-1 architecture decision
        |
        +--> WP-2 source convergence
        |
        +--> WP-3 health supervisor
                  |
                  +--> WP-4 capability router
                              |
                              +--> WP-5 KUDU job lane
                                          |
                                          +--> WP-6 unified CCL surface

WP-2 + WP-3 + WP-5 --> WP-7 recovery drills
```

Recommended delivery sequence:

1. Approve roles and invariants.
2. Eliminate source-version ambiguity.
3. Make failures visible without AI.
4. Route work intentionally.
5. Add bounded remote job execution.
6. Expose control in CCL.
7. Prove outage and rollback behavior.

## 12. Non-Goals

- Making RUKI and KUDU interchangeable active database writers.
- Running two unsynchronized CCL programs.
- Keeping permanent cloud-agent identities alive.
- Booting the CCL UI automatically.
- Hiding model-backed work as a background service.
- Giving a local model review, release, policy, or architecture authority.
- Replacing Git with shared-folder synchronization.
- Automatically resolving a dirty tree, merge conflict, failed review, or
  authority outage.

## 13. Success Criteria

The two-PC orchestration project is complete when:

- both hosts boot into their declared background roles without opening CCL;
- either host can open CCL and see the same authoritative task state;
- RUKI is the sole writable task-state authority;
- both hosts report the same approved program revision;
- KUDU reliably receives the work that benefits from its GPU and development
  capacity;
- RUKI reliably performs coordination, integration, and maintenance;
- failures and recoveries are visible without requiring an active AI session;
- no source update discards uncommitted work;
- no model output mutates canonical state without an accountable owner and
  review;
- tested recovery procedures preserve the one-writer invariant.

## 14. CCL Review Request

CCL should review this proposal for:

1. Whether the RUKI control-plane / KUDU compute-plane split matches existing
   MAP authority decisions.
2. Whether Git-based activation sufficiently prevents two program versions.
3. Whether the proposed KUDU job lane is necessary, or whether task branches
   plus visible agents are enough for the first release.
4. Whether local-model visibility requirements are satisfied without booting
   the UI.
5. Missing security boundaries, failure modes, or rollback tests.
6. The smallest first task that moves the system forward without combining
   architecture, networking, UI, and worker execution into one unsafe change.

Recommended first promotion: **WP-1 only**, followed by **WP-2** and **WP-3**
as separate reviewed tasks.

## 15. Evidence Used

- `MAP_System/artifacts/operations/cross-pc-convergence-2026-07-28.md`
- `MAP_System/artifacts/operations/cross-pc-authority-2026-07-28.md`
- `MAP_System/artifacts/operations/opensnitch-cross-pc-2026-07-28.md`
- `MAP_System/artifacts/operations/command-center-fixed-roster-2026-07-28.md`
- `MAP_System/notes/cross-pc-map-authority.md`
- `MAP_System/notes/local-model-helper-guide.md`
- `MAP_System/shared/architecture.md`
- `MAP_System/shared/agent-capability-matrix.md`
- `MAP_System/ORCHESTRATION_ENTRYPOINT_SYSTEM.md`

