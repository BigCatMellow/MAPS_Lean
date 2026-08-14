# TASK-271 Security and Failure-Mode Self-Check

- reviewer: codex-lab-lime (implementation security pass; not final task review)
- date: 2026-07-22
- scope: `context_rotation.py`, token metrics, limit-watcher notification wiring,
  snapshot/ledger writes, SQLite claim transfer, mirror export, and hcom notice
- result: PASS for submission; independent non-owner review still required

## Trust boundaries checked

- Snapshot drafts are untrusted input. Version, identity, exact live claims,
  required fields, touched paths, and workspace containment are checked before
  the immutable snapshot becomes ledger-referenced.
- Durable snapshot text passes through the existing secret-redaction guard.
  A focused test proves a synthetic OpenAI key is replaced before disk write.
- Touched paths outside the repository are never read for hashing; they are
  recorded as unverified external paths.
- Subprocesses use argument arrays without a shell. Rotation never accepts or
  executes a command from snapshot content.
- Replacement identity must differ from the old identity, and its supplied
  session ID must exactly match the live hcom roster before it can acknowledge
  the immutable snapshot SHA-256. Finalize rechecks the same binding.

## Integrity and recovery checked

- `.locks/context-rotation.lock` serializes prepare, ACK, finalize, and master
  ledger writers. An atomic replace writes each individual durable file.
- Prepare writes the immutable snapshot first and the ledger commit pointer
  last. A master-write failure can leave only an unreferenced evidence file,
  never a ledger reference to a missing snapshot.
- The master ledger is classified as protocol-generated path evidence rather
  than hashed into the state that rewrites it. Its revision and deterministic
  render are checked instead. A failed pre-ACK attempt can be explicitly
  abandoned and retained in ledger history before a replacement is prepared.
- Before ACK, snapshot tampering, rendered-ledger edits, canonical task drift,
  and touched-path drift block continuation.
- Finalize transfers only the exact live claims in the acknowledged snapshot.
  Missing tasks and claim races refuse the operation.
- Export failure restores task and agent rows and attempts to export the
  restored view. Final master-ledger failure performs the same rollback. Tests
  simulate both failures and prove the ledger stays `acknowledged` and the old
  identity remains recoverable.
- Raw snapshots and transcripts are never deleted. Finalize cannot run before
  a checksum-bound ACK.

## Notification safety checked

- The existing local watcher sends `inform`, not `request`, and never launches
  or clears an agent. It records one fingerprint for checkpoint and one for
  rotation, atomically persisting a successful send before unrelated recovery
  work can block or fail the poll.
- Codex uses its latest context count. Claude uses only the latest successful
  prompt-input estimate; cumulative cache/read traffic is explicitly ignored.
- Missing or unknown metrics degrade to no automatic notice rather than a
  fabricated percentage or forced rotation.

## Validation evidence

- `test_context_rotation.py`: 15/15 pass, including live-dogfood regressions
  for generated-ledger self-reference, abandon/reprepare history, master-render
  gating, live-session binding/recheck, and launcher guidance.
- `test_agent_token_status.py`: 2/2 pass.
- `test_limit_watcher.py`: 39/39 pass, including persistence before a synthetic
  later-poll failure.
- Live deployment: the user service was still running code loaded at
  2026-07-22 14:14:47 EDT, before `limit_watcher.py` changed at 15:48:53 EDT.
  After review rework it was restarted again through
  `systemctl --user restart map-rns-watcher.service`; the replacement process
  is active/running as PID 143411 with start time 2026-07-22 16:09:49 EDT.
  Its first poll sent and recorded a TASK-271 `rotation_due` notice for
  `codex-lab-veto`, and `agents/limit-watcher-state.json` was atomically updated
  at 16:09:50 with both the veto and prior Gabi fingerprints even though the
  same poll continued into unrelated recovery work.
- full `run_tests.sh`: 72 pass, 2 unrelated established failures caused by
  noncanonical `TASK_SUBMITTED` at `events/events.jsonl:2145` and its Layer-1
  aggregate.
