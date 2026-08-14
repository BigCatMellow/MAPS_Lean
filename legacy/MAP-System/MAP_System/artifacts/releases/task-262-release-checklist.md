# Release Checklist: TASK-262

## Header

```
task_id:      TASK-262
released_by:  mapfinish-guru
release_date: 2026-07-28
```

## Checklist

- [x] Shared-file updates complete
- [x] Decisions recorded
- [x] Follow-up tasks created
- [x] Event log entry prepared
- [x] Emergence capture considered

## Summary

Bounded pilot: structured retrieval-capsule convention for durable Markdown,
plus a separate capsule-aware evidence-selection experiment. Explicitly
scoped **not** to integrate into startup/routing/UI/embeddings — completeness
is judged against that narrower, stated scope, not a broader capsule rollout.
Touches `MAP_System/AGENTS.md` directly, classifies `full` tier.

**Deliverable verified today** (independent check, not copied from the
2026-07-28 triage table):

- All 11 output paths exist on disk.
- `MAP_System/AGENTS.md` itself carries a live `## Retrieval capsule` section
  (Purpose/Proves/Applies to/Does not provide/Evidence type/Status fields) —
  confirmed by directly reading the file at the start of this session, not
  just grepped.
- `MAP_System/.venv/bin/python -m unittest MAP_System.tests.test_task_memory_capsule_pilot -v`:
  **11/11 pass**, including `test_all_six_pilot_documents_have_valid_capsules`
  (acceptance criterion 3's "at least six representative documents") and the
  full parser/validator rejection suite (duplicate heading, missing/unknown
  fields, invalid type/status, excessive/too-short length, fenced-example
  false positives) — acceptance criterion 2.
- **TASK-261 preservation (acceptance criterion 4)**: `MAP_System/.venv/bin/python
  -m unittest MAP_System.tests.test_task_memory_packet_selector` — **7/7
  pass**, confirming TASK-261's own selector still functions standalone,
  untouched by this pilot's separate capsule-aware selector.
- Single clean review: approved by claude-lab-rose 2026-07-21 with no
  rejection/rework round.

**Shared-file updates complete**: `MAP_System/notes/retrieval-capsule-guide.md`
documents the convention; `MAP_System/AGENTS.md`'s own capsule section is
the canonical worked example. No other shared doc required a change for
this bounded pilot's scope.

**Decisions recorded**: none required — the task's own description is
explicit that capsules "explicitly remain descriptive metadata rather than
authority" and the pilot must not integrate into startup, canonical
authority, routing, UI, embeddings, or every Markdown file; this is a
self-contained experiment, not a policy change. `decision_class=null`,
unchallenged.

**Follow-up tasks created**: none needed — `task_dependencies` shows nothing
currently depends on TASK-262, consistent with its explicitly bounded,
non-integrating scope; the report is required to include "a fresh-holdout
recommendation," which is future guidance for a possible follow-up, not a
task this release is obligated to spawn itself.

**Event log entry prepared**: appended automatically by `map_task.py
release`.

**Emergence capture considered**: considered, none warranted for release
itself — the pilot's own deliverable already includes the required staleness-
risk/negative-query/benefit-vs-cost analysis as its report content; that is
the capture, not a separate emergence entry.
