# Repair Record

Repair ID: REPAIR-0013
Related task: TASK-323
Found by: helper-task323-p02-tina
Date: 2026-08-10
Severity: BLOCKING
Status: APPLIED

## What was found

events.jsonl line 18785 had 1526 leading NUL bytes prefixing an otherwise-valid JSON event, causing validate_events.py to fail JSON decode.

## Surfaced by

helper-librarian.md 2026-08-09 rerun; validate_events.py errored at line 18785

## Severity rationale

BLOCKING: validate_events.py --fail-on-new errored on this line, blocking a clean validation pass; classified mechanical because the fix required no judgment - the NUL bytes were pure padding with zero information content, and the bytes immediately following them formed a complete, well-formed JSON event matching the exact structure/pattern of the five surrounding sibling lines (same limit_watcher RnS template, same timestamp, only the agent-name token differs: mapfinish-guru).

## Proposed or applied fix

Saved the original corrupted line's exact bytes and sha256 to MAP_System/artifacts/recovery/evidence/events-jsonl-line-18785-original.bin(.sha256) before any edit. Then stripped only the 1526 leading NUL bytes from line 18785 (lstrip on NUL, verified byte-for-byte elsewhere unchanged); no other line in the 6.8MB file contained any NUL byte (file-wide NUL count matched the line-18785 count exactly, confirming isolation). Recovered line: {"created_at": "2026-08-07T14:55:10-04:00", "type": "PROGRESS", "task_id": "TASK-083", "sender": "limit_watcher", "summary": "RnS: recorded resume window passed for mapfinish-guru (resume_after 2026-07-28T17:41:18-04:00); visible resume nudge FAILED.", "artifact_paths": []}

## Authority check

- [ ] DRIFT or mechanical BLOCKING — core agent applied directly

## Verification

python3 MAP_System/scripts/validate_events.py -> errors=0, new_warnings=0 (previously errored at line 18785). Whole-file sha256 before=010dd2af...29f5c5a after=50252312...4ea7cfe, delta=exactly 1526 bytes removed (matches NUL count). No other lines touched.

## Recurrence check

Second-observed instance of this line's corruption (librarian audits from 2026-08-09 and earlier flagged it read-only without fixing). Root cause of the original NUL-padding write (crash/partial-flush during append) is not investigated here - out of scope for this bounded repair.

## Mirror-sync revert (2026-08-10, helper-releases-batch2-bela)

Found by claude-lab-sumi: this fix had only landed on Biggie's local mirror copy of events.jsonl. Because events.jsonl is listed in MIRROR_FILES, the next scheduled `install_snapshot()` mirror sync from Smalls silently overwrote Biggie's corrected copy with Smalls' still-corrupted original, reintroducing the same 1526 leading NUL bytes on line 18785 with zero visible error (mirror sync succeeds either way; it does not diff or warn on reverting a local-only fix). Root cause of the revert: the original repair was applied on the read-only mirror (Biggie) instead of the sole writable lifecycle authority (Smalls), so it could never survive a sync.

Re-applied the identical fix directly on Smalls via the normal (non-gateway) `smalls` ssh alias, with explicit operator authorization for the remote write:
- Backed up Smalls' events.jsonl to `/tmp/events.jsonl.before-repair0013-followup` before editing.
- Verified line 18785 on Smalls had exactly 1526 leading NUL bytes prefixing the identical TASK-083/limit_watcher JSON event, and that these were the only NUL bytes in the whole file (file-wide NUL count == line-18785 NUL count == 1526), confirming isolation, same as the original finding.
- Stripped exactly those 1526 bytes; whole-file sha256 before=25fdc3a602d8861ae1d06d01fe3108d785e7d2ba8c8b06a13bd8dea624185b6a, after=ca1fd955bdd71ceaf6038c0c5469fad62377eddb3cf3a7d941b288e2bc3f1064; delta confirmed exactly 1526 bytes removed by the script itself (hard assertion, not just observed).
- `validate_events.py` on Smalls afterward: errors=0, new_warnings=0 (previously errored at line 18785).
- Because events.jsonl is append-only and the file grew by ~37 lines between an earlier read-only check and this fix (live agents appending events), line 18785 itself was unaffected by that growth - it only ever gets appended to, not inserted into.

This time the fix is durable against mirror sync because it was applied at the authority (Smalls) rather than the mirror (Biggie): the next sync will pull the now-corrected line down to Biggie, not overwrite a correction with corruption.

## Notes

Filed as bounded support for TASK-323 (owner claude-lab-sumi); reported to owner via hcom. Full writeup cross-referenced at MAP_System/artifacts/recovery/p02-validation-debt-repair-2026-08-10.md.
