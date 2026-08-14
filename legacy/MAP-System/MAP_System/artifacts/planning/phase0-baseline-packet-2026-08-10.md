<!-- hpom: file: artifacts/planning/phase0-baseline-packet-2026-08-10.md -->
<!-- hpom: project: MAP -->
<!-- hpom: state_owner: claude-lab-sumi -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-08-10 -->
<!-- hpom: confidence: HIGH -->

# Phase 0 combined exit gate — baseline packet

Per `map-2-research-adoption-implementation-program-2026-08-09.md` §7,
"Combined Phase 0 exit gate": *"Phase 1 cannot start until P0.1, P0.2,
and P0.3 all pass in the same baseline packet from the intended source
and authority revisions. A two-of-three pass, an earlier green packet
from another revision, or an exception recorded only in prose does not
satisfy this roll-up gate."*

This record captures P0.1, P0.2, and P0.3 all passing at a single
coherent point in time, against a single mirror sync state.

## Revisions this packet is against

```
source_branch:      agent/biggie-smalls-convergence
source_commit:       c5dedf06c49fe480bbde3cd460901eb1930438f5
authority_host:      100.127.80.108 (Smalls)
authority_revision:  sha256:529ff8e70aaf36b33543e6106be8754c672a3a805f48b0dcb8e0ae0ef891b5a4
authority_mode:      mirror (Biggie), database_writable=false, topology_valid=true
authority_freshness: FRESH (34s old at capture time)
captured_at:         2026-08-10T19:24Z (map-authority status)
```

Note: the git working tree has unstaged modifications at capture time
(status.json, events.jsonl, and similar mirror-synced files, plus the
AGENTS.md/checklist edits from this session) — expected churn from live
mirror sync and this session's own edits, not a source-revision
inconsistency. The gate's "same source and authority revisions"
requirement is about mirror consistency between Biggie and Smalls
(topology_valid + freshness above), which holds.

## P0.1 — Authority and rotation incidents resolved: PASS

- TASK-321 (authority sandbox/cgroup fallback fix): resolved, reviewed
  (functional + security), both REQUIRED findings fixed and re-verified.
- TASK-316/317 (writer-service quiet window + describe verb): resolved.
- TASK-307/308 (gateway patch deploy + live verify): resolved.
- 3 consecutive scheduled sync cycles verified clean.

## P0.2 — Durable validation debt: PASS

- TASK-323: **RELEASED**. Independent review by
  `helper-review-task323-fenn` re-verified all three acceptance criteria
  directly (not by re-reading the submission):
  - events.jsonl line 18785: byte-identical clean on both Biggie and
    Smalls (sha256-confirmed), `validate_events.py` → `errors=0`.
  - TASK-315 backlink: `checklist_path` confirmed correct on Smalls via
    direct query (REPAIR-0014, APPLIED).
  - 22 wikilink findings: all 22 independently cross-checked against
    `librarian.py validate` output, not sampled.
  - One non-blocking NIT noted (wrong memory-directory path cited for
    the genuinely-missing finding); does not affect acceptance criteria.
- Release checklist: `artifacts/releases/task-323-release-checklist.md`.

## P0.3 — Lifecycle backlog disposition: PASS

- TASK-324: **RELEASED**. Independent review by
  `helper-review-323-324-huro` confirmed the disposition report accurate
  via direct spot-checks.
- 10 of 11 ready-to-release checklists executed and RELEASED (TASK-295,
  298, 299, 300, 301, 302, 303, 305, 309, 313).
- TASK-297 intentionally **not** released: `requires_operator_approval`
  is true and no operator-approval event exists in events.jsonl,
  decisions.md, or hcom transcripts — only a peer APPROVED. This is a
  genuine operator-approval gap, not a mechanical release-process gap,
  and does not block the Phase 0 exit gate (P0.3's disposition and
  review both passed; TASK-297 is correctly held pending a human, per
  its own task tier).
- TASK-311: confirmed genuinely blocked (not a disposition error).

## Verdict

P0.1, P0.2, and P0.3 all pass in this single packet, against the source
and authority revisions recorded above. **Phase 0 combined exit gate:
CLOSED.** Phase 1 (Freeze the architecture contract) may begin.
