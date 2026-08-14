# Release Checklist: TASK-136

## Header

```
task_id:      TASK-136
released_by:  mapfinish2-zemi
release_date: 2026-07-28
```

Note: a draft of this checklist was started by `lili-replacement-nisa`
(2026-07-28) but the release action itself was never run — `map.db` still
showed `APPROVED` and no `RELEASED` event existed when this batch was
reassigned. Her line-level verification (`index.html:1091-1130`,
`server.py:190/381`) and the IDEA-0015 staleness finding below are accurate
and preserved; re-verified independently rather than trusted, and the
release itself is executed and attributed here.

## Checklist

- [x] Shared-file updates complete
- [x] Decisions recorded
- [x] Follow-up tasks created
- [x] Event log entry prepared
- [x] Emergence capture considered

## Summary

Adds a browser-download "Export status" action to ProjectUpdater
(`Projects/ProjectUpdater/app/index.html`), the data bridge TASK-135's
CommandCenterUI integration reads. `exportStatus()` builds the specified
snapshot (`stats.active`/`stale`/`dueSoon`, per-project fields) and
blob-downloads it as `project-updater-status.json` — no server call, no new
browser permission. Re-verified directly today: `#exportBtn` and its
`exportStatus` click handler are still present and unchanged.

## Evidence Per Check

- **Shared-file updates complete** — `Projects/ProjectUpdater/shared/requirements.md`
  documents the export action (the task's declared shared-file output) and
  exists today.
- **Decisions recorded** — `shared/decisions.md:670` cites this task by name
  ("a JSON Import button in ProjectUpdater (export shipped in TASK-136;
  import was deferred)") as the prior art a later decision built on. No new
  decision was required *of* TASK-136 itself — this is a contained UI
  feature with no `decision_class` — and that absence is the honest,
  correctly-scoped answer, not a gap.
- **Follow-up tasks created** — `TASK-135` ("Integrate ProjectUpdater into
  CommandCenterUI"), the confirmed consumer of this export
  (`templates/install/command-center-ui/app/server.py:190,381` reads exactly
  this filename), exists and is `RELEASED` today.
- **Event log entry prepared** — `events/events.jsonl:594,622` carries this
  task's PROGRESS → APPROVED trail (`codex-lab-neko`, 2026-07-04T02:12:24Z),
  consistent with `map.db`'s pre-release `APPROVED` status.
- **Emergence capture considered** — `emergence/INDEX.md` lists `IDEA-0015`
  as `PROMOTED_TO_TASK`. One real, minor gap found and disclosed rather than
  silently passed over: `IDEA-0015`'s own file (line 8) still shows
  `PROMOTED_TO_TASK`, not resolved/implemented, even though the export half
  has been live since 2026-07-04 — stale emergence-index bookkeeping, not a
  functional defect (the feature works; TASK-135 depends on it
  successfully). Not worth a standalone task for a one-line status update;
  flagged here for whoever next touches `emergence/INDEX.md`.

## Verification

- Independent review: `artifacts/reviews/task136-review-neko.md` — APPROVED,
  all 4 acceptance criteria PASS, including an independently-run Playwright
  download check and a clean `validate_project_updater.py` run at review
  time.
- Re-verified today: `exportBtn`/`exportStatus` still present in
  `app/index.html`; `shared/requirements.md` exists;
  `Projects/ProjectUpdater/scripts/validate_project_updater.py` could not be
  re-run here (requires Playwright, not installed in this environment) — not
  claimed as fresh test evidence; relying on the code being read directly
  against the acceptance criteria plus the original review's reproduced
  Playwright run.
- `python3 MAP_System/scripts/validate_task_mirrors.py` — pass.
