# P0.3 Lifecycle Backlog Disposition Record — 2026-08-10

Prepared by: helper-task324-p03-fifi (bounded support to claude-lab-sumi, accountable owner of TASK-324)

Scope: TASK-295, 297, 298, 299, 300, 301, 302, 303, 305, 309, 311, 313 — all APPROVED,
none auto-qualified as low-risk by `batch_release_low_risk.py --dry-run`. Each task below
was checked against its **full** `events.jsonl` history (not just current status), its task
JSON, and every cited artifact's actual on-disk presence. Per scope, no release checklists
were written and nothing was released in this pass.

---

## TASK-295 — Add sanctioned `map_task.py` retire verb

**Disposition: ready-to-release-with-real-checklist**

- History: created → PROGRESS → SUBMISSION (mapfinish-guru) → **CHANGES_REQUESTED** (claude-lab-mimi: missing output-path registration for `db/claims.py`) → reworked → re-registered path → re-submitted (codex-lab-vumo) → APPROVED (claude-lab-mimi).
- Real rework cycle, not a rubber stamp. All 5 cited output-path artifacts exist on disk.
- No gaps found.

## TASK-297 — Add sanctioned `map_task.py` amend-criteria verb

**Disposition: ready-to-release-with-real-checklist**

- History: created → PROGRESS (output path registered) → SUBMISSION → APPROVED (helper-review-task297-308-halo). Single clean pass, no rejection.
- All 4 cited artifacts exist on disk.
- Note: task JSON requires operator approval (`requires_operator_approval: true`, this is the "most abusable" lifecycle verb per its own description) — confirm operator sign-off is captured before a release checklist is written; not found in events.jsonl itself (events only show peer APPROVED, no explicit operator-approval event logged for this one). Flag for checklist author to locate/attach.

## TASK-298 — Converge KUDU and RUKI on one authoritative tree

**Disposition: ready-to-release-with-real-checklist**

- History: created → SUBMISSION → APPROVED (claude-lab-mimi), single pass.
- Sole cited artifact (`cross-pc-convergence-2026-07-28.md`) exists.
- `destructive_action: true`, `task_tier: operator` — high blast radius. Only one artifact is cited as output for a task this large (SSH key setup, atomic tree swap, rollback); checklist author should verify the artifact's internal content actually documents all 6 acceptance criteria, not just spot-check existence.

## TASK-299 — Centralize cross-PC MAP SQLite authority on RUKI

**Disposition: ready-to-release-with-real-checklist**

- History: created → 6x PROGRESS (output paths registered) → SUBMISSION → APPROVED by `task299-security-review-todo`.
- That reviewer name looked like a placeholder at first glance — verified it's a real dedicated review session (visible in context-rotation and RnS watchdog events, later crashed ~2026-07-29T02:05 *after* completing this approval). Its review artifact (`task299-review.md`) is substantive: names 2 real pre-fix issues (WAL/SHM sidecar loss, installer mode-typo fallback), cites specific fix-verification tests, checksums reviewed files, and cross-checks live activation evidence.
- All 13 cited artifacts exist on disk.
- No gaps found.

## TASK-300 — Notify operator when cross-PC MAP authority unavailable

**Disposition: ready-to-release-with-real-checklist**

- History: created → PROGRESS → SUBMISSION → APPROVED (`task299-security-review-todo`, same reviewer as TASK-299, same session).
- All 7 cited artifacts exist on disk.
- No gaps found.

## TASK-301 — Keep cross-PC MAP links allowed by OpenSnitch

**Disposition: ready-to-release-with-real-checklist**

- History: created → SUBMISSION → APPROVED (`task299-security-review-todo`).
- All 5 cited artifacts exist on disk.
- No gaps found.

## TASK-302 — Restore fixed AI Command Center Lab startup roster

**Disposition: ready-to-release-with-real-checklist**

- History: created → 6x PROGRESS → SUBMISSION → APPROVED (codex-lab-replacement-mudo) → later a `REVIEW_RECORD_CORRECTED` event (2026-07-29T14:14) fixed a SQLite review-record durability mismatch (verdict/date) to match the actual review artifact `task302-independent-review-codex-lab-rosa.md`, per a librarian audit finding.
- This is exactly the kind of "stale status field contradicted by later events" pattern to watch for — but here it resolved correctly: the correction event shows the DB record was repaired to match the real artifact, not the other way around. Confirmed `task302-independent-review-codex-lab-rosa.md` — checked, exists.
- All 13 cited output artifacts exist on disk (both `/home/mellow/...` live paths and template copies).
- No unresolved gaps; note the self-correction in the checklist for auditability.

## TASK-303 — Align canonical MAP authority hierarchy across operator surfaces

**Disposition: ready-to-release-with-real-checklist, with a caveat**

- History: created → SUBMISSION → APPROVED (claude-lab-vanu), all within ~3 minutes.
- Fast turnaround for a `policy`-tier, `requires_operator_approval: true`, 6-criteria task touching AGENTS.md and 12 files — no dedicated independent-review artifact was found under `MAP_System/artifacts/reviews/` for TASK-303 (unlike every other task here).
- However, the delivered artifact itself (`canonical-authority-hierarchy-2026-07-29.md`) documents its own operator approval inline: *"operator_approval: bigboss/user 'go for it,' relayed by codex-lab-rosa in hcom request 30843 on 2026-07-29"*. All 12 cited output paths exist on disk.
- Caveat for checklist author: verify hcom request 30843 independently (or accept the citation) before treating operator-approval as satisfied — the 3-minute review-to-approve gap plus absence of a standalone review artifact is thin evidence for a policy-tier authority change, even though nothing found here is false.

## TASK-305 — Integrate INS-0054–0057 into MAP guidance and release evidence

**Disposition: ready-to-release-with-real-checklist**

- History: created → PROGRESS (owner reassigned codex-lab-mebo → codex-lab-replacement-valo, operator-authorized handoff, reason logged) → SUBMISSION → **CHANGES_REQUESTED** (claude-lab-nene: required provenance disclosure for incidental PROMO-0012 completion) → reworked (registered PROMO-0012 output path, corrected annotation) → re-submitted → APPROVED (claude-lab-nene).
- Real rework cycle with a substantive finding (undisclosed incidental completion) caught and fixed.
- All 21 cited artifacts exist on disk, including the added PROMO-0012 file.
- No gaps found.

## TASK-309 — MAP recovery Phase 2 integration epic

**Disposition: ready-to-release-with-real-checklist, with a documented caveat**

- History: created (codex-lab-risa) → owner reassigned twice more via documented coordinator handoffs (map-coordinator-hobo per DEC-039 stale-lease reason; then claude-lab-luzo per stale coordinator not in live roster; then coordinator-replacement-rose) → SUBMISSION (claude-lab-luzo, 2026-08-06) → APPROVED (codex-lab-rani, 2026-08-10 — same day as this disposition pass).
- **Finding**: the task JSON's own description cites `MAP_System_Recovery_2026-07-29/03_kickoff/MAP_RECOVERY_PLAN_REVIEW.md` as "Approval evidence." That entire `03_kickoff/` subdirectory does not exist anywhere in the tree (only `00_control/` and `01_preserved_snapshot/` exist). This is a citation to a path that was apparently never created/tracked, not a fabricated or altered artifact.
- The actual output artifact, `00_control/phase2-status.md`, exists and is unusually transparent about a related gap: it states it was **regenerated from live canonical state on 2026-08-04 by claude-lab-luzo** because the original file "could not be located (no git history for this path; it was evidently always an untracked/local-only working file)."
- Substance check: phase2-status.md's workstream table cross-references real, independently-checked evidence — WS-1 (TASK-310/313/314), WS-2 (TASK-311), WS-3 (TASK-312) are each shown RELEASED/APPROVED with named reviewers and review-artifact paths, consistent with what this pass independently found for TASK-311/313 below. Operator authorization for the recovery effort overall is corroborated in `MAP_System/shared/decisions.md` (DEC-036, coordinator-role decisions ~line 1050+), independent of the missing 03_kickoff file.
- Caveat for checklist author: the cited "Approval evidence" path in TASK-309.json is dead and should be corrected or removed before release rather than left pointing at a nonexistent file; the substantive gate (WS-1/2/3 sequencing) is otherwise real and satisfied.

## TASK-311 — WS-2: Resolve active MAP output ownership collisions

**Disposition: genuinely-blocked with evidence (missing deliverable artifact)**

- History: created (codex-lab-risa) → SUBMISSION (rotation-replacement-kite-veni) → APPROVED (claude-lab-mimi).
- **Finding — matches the TASK-307/308 pattern flagged in the assignment**: the sole cited output path, `MAP_System/artifacts/recovery/ws2-output-collision-resolution.md`, **does not exist anywhere in this tree** (`find`/`git log --all` both empty for it).
- The reviewer's own record (`task311-independent-review-mimi.md`) discloses this directly: *"Files Reviewed: `.../ws2-output-collision-resolution.md` (relayed via hcom; not directly filesystem-visible from Biggie)"* — i.e., the deliverable was produced on a remote host (RUKI/Smalls) and reviewed there, but never synced into this canonical (Biggie) tree.
- This is narrower than a fabricated review: the reviewer independently re-verified the *substance* live rather than trusting the missing document — re-ran `validate_task_graph.py` (0 collisions), confirmed TASK-297/304/308 gating untouched via live `task show`, and confirmed the actual mutation (TASK-254 retirement) in `events.jsonl` with a real reason string citing WS-2/Group D and operator sign-off. This pass independently re-ran `validate_task_graph.py` just now: still 0 collision-related failures (only an unrelated TASK-319 issue).
- **Blocking gap**: the required output artifact is absent from the canonical tree a release checklist would need to point to as evidence. Do not release TASK-311 by citing this path as existing evidence until the file is actually retrieved from wherever it was written (RUKI/Smalls) and committed to this tree, or the task's output_paths / evidence citation is corrected to point at where it truly lives.

## TASK-313 — WS-1 prerequisite: resolve runner/Command Center path ownership

**Disposition: ready-to-release-with-real-checklist**

- History: created (codex-lab-risa) → SUBMISSION (codex-lab-vumo) → APPROVED (claude-lab-mimi).
- Cited artifact `ws1-path-ownership-prerequisite.md` exists; a companion review artifact `ws1-path-ownership-prerequisite-review-mimi.md` also exists (not itself cited in events but present in `artifacts/recovery/`), reinforcing the trail.
- Also independently listed in TASK-309's phase2-status.md workstream table as APPROVED with the same reviewer (mimi) and same review-artifact path — consistent across both sources.
- No gaps found.

---

## Summary

| Task | Disposition | Key issue |
|---|---|---|
| 295 | ready | none |
| 297 | ready | operator-approval event not directly visible in events.jsonl — confirm before checklist |
| 298 | ready | single-artifact evidence for a large destructive task — verify content depth |
| 299 | ready | none |
| 300 | ready | none |
| 301 | ready | none |
| 302 | ready | self-corrected stale review record, resolved correctly |
| 303 | ready | thin review trail (3 min, no standalone review artifact) for a policy-tier task |
| 305 | ready | none |
| 309 | ready | dead citation path (`03_kickoff/MAP_RECOVERY_PLAN_REVIEW.md`) in task JSON, should be corrected |
| 311 | **blocked** | cited deliverable artifact does not exist in this tree (cross-machine sync gap); substance independently re-verified live and appears real |
| 313 | ready | none |

11 of 12 are ready for a real hand-checked release checklist. TASK-311 is genuinely blocked on retrieving/committing its missing deliverable artifact before it can be released with honest evidence citations.
