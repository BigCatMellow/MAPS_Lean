# Biggie/Smalls Relay Recovery and CCL Preflight

- Date: 2026-07-29
- Coordinator: `codex-lab-mebo`
- Source: Biggie / KUDU / `mellow@192.168.1.177`
- Destination: Smalls / RUKI / `home@192.168.1.153`
- CCL direction: Biggie to Smalls only
- Status: relay recovered on both hosts; read-only CCL preflight complete;
  gateway review and all CCL writes still pending

## Relay recovery

Both hosts had the same stale relay PID failure: the relay state named a
namespace PID that resolved to an unrelated host process, so the service
appeared started while its worker was unresponsive.

Recovery was limited to relay process state:

1. stop or quiesce the affected relay launcher;
2. move the stale PID record to a timestamped quarantine name;
3. start a fresh relay worker;
4. verify both devices through the relay CLI.

No hcom messages, agent sessions, MAP records, credentials, or project files
were deleted. After recovery:

- KUDU reported `connected`;
- RUKI reported `connected`;
- KUDU reported RUKI online `just now`;
- the local queue reported `up to date`;
- a cross-device hcom message from `codex-lab-vumo:RUKI` reached
  `codex-lab-mebo`.

## Confirmed Smalls identity

Read-only SSH preflight returned:

- hostname: `MediaCenter`;
- user: `home`;
- home: `/home/home`;
- MAP source present at
  `/home/home/Projects/MultiAgentProject/Source`;
- CCL present at `/home/home/Projects/CommandCenterUI`.

This matches the operator-approved host mapping. RUKI remains the sole
writable MAP authority.

## Biggie canonical bundle

The repository-owned Biggie bundle verifies cleanly against:

`MAP_System/templates/install/command-center-ui/version.json`

Version:

`2026-07-29-orchestrator-v2-recap`

The verifier reported all 11 managed files matching the manifest.

## Smalls dry-run findings

No CCL write was made.

Smalls is running the older layout:

- `src/orchestrator.html` is missing;
- `src/orchestrator.js` is missing;
- `src/orchestrator.css` is missing;
- `src/bcmagent.svg` is missing;
- `README.md` differs from the Biggie manifest;
- `app/server.py` differs from the Biggie manifest.

The Smalls CCL Git worktree also contains pre-existing local modifications,
including host/UI files. These are user state and must not be silently
discarded.

The operator previously designated Biggie as canonical. The resulting safe
deployment policy is:

1. preserve the complete current Smalls CCL installation in a timestamped
   backup;
2. transfer only the 11 manifest-managed files to a staging directory;
3. preserve Smalls runtime data, credentials, hcom state, MAP data,
   host-rendered files, and excluded legacy UI files;
4. verify the staged bundle against Biggie's manifest;
5. activate with a recoverable rename/swap;
6. verify live parity and perform a server smoke test;
7. retain the backup for rollback.

## Remaining gates

1. Independent functional and security-framed review of TASK-307.
2. Checksum-staged deployment of the reviewed gateway patch to RUKI.
3. Live verification of `register-agent`, `rotation-transfer`, and
   `rotation-restore`.
4. Timestamped Smalls CCL backup and reviewed staged deployment.
5. Post-activation CCL parity, smoke, hcom communication, and rollback
   evidence.

The stale canonical TASK-307 review claim remains attributed to unavailable
`claude-lab-muza`; it has not been impersonated or overwritten.
`codex-lab-vumo:RUKI` is performing the independent review without claiming,
which `MAP_System/notes/review-guide.md` explicitly permits.
