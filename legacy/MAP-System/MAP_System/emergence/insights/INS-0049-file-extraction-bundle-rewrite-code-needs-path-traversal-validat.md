# Insight Record

Insight ID: INS-0049
Project: MAP
Related task: TASK-207
Detected by: claude-lab-nora
Date: 2026-07-27
Status: PROMOTED

## Short description


- obs: File-extraction/bundle-rewrite code needs path-traversal validation and atomic staged writes as a paired default, not two separate rework cycles

## Trigger


- src: TASK-207 (Projects/ClearFront/scripts/extract_bundle.py) needed two separate CHANGES_REQUESTED rounds: first for missing path-traversal validation (safe_asset_path() had to check canonical UUID + confirm resolved path stays under assets_dir), second for missing atomic write safety (extraction had to move to staging in a fresh sibling tempdir and atomically swap outputs only after validation).

## The synthesis


- synth: Both findings are the same class of gap approached separately: code that extracts/rewrites files from an archive or bundle onto disk needs (1) path-traversal validation on every derived output path and (2) atomic stage-then-swap writes so a failed/interrupted run cannot leave partial or unsafe output. A reviewer catching one rarely prompts a check for the other unless it's named as a paired default.

## Why it might matter


- why: This is the kind of narrow, easy-to-miss default that costs a full extra review cycle per occurrence when it's rediscovered per-task instead of established as a standing expectation. [[emergence/ideas/IDEA-0004-require-a-second-security-focused-review-pass-for-any-task-that-]] (second security-focused review pass) is adjacent but broader; this is a specific, checkable pair for extraction/rewrite code specifically.

## Evidence


- ev: MAP_System/events/events.jsonl SUBMISSION events for TASK-207 at 2026-07-17T00:49:58Z, 00:56:57Z (path-traversal fix), 02:42:04Z (atomic staging fix).

## Risk


- risk: Acting without promotion could bypass HPOM governance.

## Scope


- scope: Applies to any task that extracts, decodes, or rewrites files from an external bundle/archive/package onto disk.

## Recommended next action

- [ ] ignore
- [ ] park
- [ ] task
- [ ] idea
- [ ] experiment
- [ ] escalate-human

## Notes

- note:

## Resolution (2026-07-27, claude-lab-nora)

Promoted directly to a standing review checklist item (bounded, no task
needed): `MAP_System/notes/review-guide.md`, "Extraction/Bundle-Rewrite
Safety (INS-0049)".
