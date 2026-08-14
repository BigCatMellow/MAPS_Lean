# Helper Librarian Validation — 2026-07-29

- status: complete
- owner: command-center
- provider: codex
- model: gpt-5
- created_at: 2026-07-29
- scope: Read-only audit of reusable MAP durable state, backlinks, task records, and review/release artifacts.

## Audit addendum — 2026-08-09 current rerun

### Required findings

- Task mirrors drifted during the rerun: SQLite owns `TASK-320` with
  `rotation-replacement-duma-bono`, while both `tasks/TASK-320.json` and
  `workflow/task_graph.json` name `codex-lab-duma`.
- `validate_task_graph.py` fails because retired `TASK-319` has neither
  acceptance criteria nor output paths.
- `validate_canonical_repo_paths.py` fails because
  `scripts/ai-command-center-antigravity` still embeds the missing legacy root
  `/home/home/Projects/MultiAgentProject`.
- Event validation still fails at line 18,785 of `events/events.jsonl` on the
  existing NUL-byte corruption. No new warnings appear after the baseline.
- SQLite's `TASK-315` release record still points to the nonexistent legacy
  `/home/home/.../task-315-release-checklist.md` path. The checklist at the
  current repository path passes the tier-specific validator.
- Wikilink validation still reports 22 findings: six code/literal scanner
  false positives, eleven shorthand emergence IDs whose long-form files
  exist, four ambiguous bare `AGENTS` links, and one missing
  `haiku-agents-need-no-approval-tasks` target. The index builds with 122
  targets and 275 edges.

### Provenance and artifact checks

- All 309 task JSON records pass schema validation, and the generated
  `shared/current-state.md` active-lane table matches SQLite. The mirror and
  graph failures above remain blocking durable-state inconsistencies.
- Of 133 SQLite release rows, 132 recorded checklist paths exist and pass the
  current tier-specific validator; `TASK-315` is the sole path failure. The
  artifact tree contains 241 release checklists and 319 review Markdown files.
- All 50 first-line `review_record` backlinks in release checklists resolve.
  `TASK-288` and `TASK-290` first name their `CHANGES_REQUESTED` pass, then
  name separate `APPROVED` rereviews; both rereviews pass
  `validate_review.py`.
- Current review artifacts checked for `TASK-311`, `TASK-313`, `TASK-315`,
  `TASK-316`, and the combined `TASK-316`/`TASK-317` review all pass
  `validate_review.py`.
- Historical SQLite provenance debt is unchanged: 244 tasks are `RELEASED`,
  111 lack a release row, and 198 `APPROVED`/`RELEASED` tasks lack a completed
  `APPROVED` review row. Treat this as migration debt, not proof that newer
  gated releases skipped review.
- Strict shared-state, decisions, research, repair, context-packet, risk, and
  emergence-structure validators pass. Emergence stale checking reports 16
  lifecycle/reference findings.
- This rerun changed only this helper note. It did not mutate task, SQLite,
  event, backlink, review, release, or source records.

## Audit — 2026-08-09

### Required findings

- `validate_events.py --fail-on-new` fails: line 18,785 of
  `events/events.jsonl` contains a long NUL-byte run before an otherwise valid
  event. The file was already dirty and actively written; this audit did not
  rewrite append-only history.
- SQLite's `TASK-315` release record points to the nonexistent legacy path
  `/home/home/Projects/MultiAgentProject/Source/MAP_System/artifacts/releases/task-315-release-checklist.md`.
  The checklist exists at the current repository path and validates there, but
  the durable release-record backlink does not resolve.
- Wikilink validation reports 22 findings: six are code/literal examples that
  the scanner misreads, eleven are shorthand IDs whose long-form targets do
  exist, four are ambiguous bare `AGENTS` links, and one points to a missing
  `haiku-agents-need-no-approval-tasks` memory file. The backlink index still
  builds with 122 targets and 275 edges.

### Provenance debt

- SQLite contains 244 `RELEASED` tasks but only 133 release rows; 111 released
  tasks have no release row. It also has 198 `APPROVED`/`RELEASED` tasks with
  no completed `APPROVED` review row. This is longstanding bootstrap/migration
  debt, not evidence that the newer gated releases bypassed review.

### Passing checks

- All 308 task records pass schema validation; SQLite, task JSON, and task-graph
  mirrors agree, and `shared/current-state.md` matches SQLite.
- Shared-state strict validation, decisions, canonical paths, research,
  repairs, context packets, and risk registers pass.
- Of 133 SQLite release rows, 132 recorded checklist paths exist and satisfy
  the current tier-specific checklist validator; `TASK-315` is the sole path
  failure. Across 241 release artifacts, all 49 explicit `review_record`
  references resolve.
- The current approved review artifacts sampled for `TASK-315`, `TASK-316`,
  and the combined `TASK-316`/`TASK-317` review pass `validate_review.py`.
- This audit changed only this helper note. It did not mutate tasks, SQLite,
  events, backlinks, reviews, releases, or source files.

## Audit — 2026-07-29

### Required findings

- Task-graph validation fails: `MAP_System/scripts/map_task.py` is registered
  to both submitted `TASK-295` and ready/operator-gated `TASK-297`.
- Backlink validation reports 18 findings: 15 broken links and three ambiguous
  bare `AGENTS` links. Three are literal resolver examples in TASK-238
  review/release records; the remainder are emergence cross-links.
- `artifacts/research/SUMMARY-herdr-comparison-2026-07-22.md` fails the
  Research Summary contract with all eight required fragments absent.
- `emergence/insights/INS-0047-*.md` is empty/malformed and fails required
  insight metadata and summary validation.
- `TASK-301` is `APPROVED` in SQLite with an independent approved review row,
  but no durable review artifact was found. `TASK-299` and `TASK-300` each
  have a review artifact that passes `validate_review.py`.

### Recommended cleanup

- Event validation has zero errors but one new warning: line 2145 uses
  noncanonical event type `TASK_SUBMITTED`.
- Twelve emergence insights retain RAW/CANDIDATE lifecycle state after their
  related tasks became RELEASED. The emergence sentinel is scan-stale but has
  zero pending candidates.
- Historical provenance is incomplete in SQLite: 111 of 239 RELEASED tasks
  have no `task_release_records` row, and 189 APPROVED/RELEASED tasks have no
  approved review row. Treat this as legacy migration debt, not evidence that
  the current 128 registered releases failed their gates.
- Nine legacy approved Markdown reviews do not satisfy today's review-template
  validator; all 67 currently registered full-tier releases nevertheless have
  a structurally valid approved review artifact.

### Passing checks

- All 291 task JSON files pass schema validation. SQLite/task JSON/task-graph
  mirrors agree, `shared/current-state.md` matches SQLite, and every declared
  output of the current IN_PROGRESS/SUBMITTED/APPROVED tasks resolves.
- All 128 registered release checklists exist and validate: 67 full and 61
  low tier. Every full-tier release has a valid approved review artifact,
  including ClearFront-local records.
- Shared-state metadata, decisions, canonical paths, context packets, repair
  artifacts, and risk registers pass. The backlink index builds with 115
  targets and 259 edges.
- This audit changed only this helper note; no task, database, event, backlink,
  review, release, or source record was mutated.

---

## Prior audit — 2026-07-28

- REQUIRED — Task-graph validation fails because `MAP_System/scripts/map_task.py`
  is owned by both submitted `TASK-295` and ready/operator-gated `TASK-297`.
- REQUIRED — The generated active-lane table in `shared/current-state.md` is
  stale: `TASK-289`, `TASK-268`, `TASK-274`, and `TASK-264` are shown as
  SUBMITTED/APPROVED although SQLite records all four as RELEASED.
- REQUIRED — `validate_research_artifacts.py` still rejects
  `artifacts/research/SUMMARY-herdr-comparison-2026-07-22.md`; the completed
  document is missing all eight required Research Summary contract fragments.
- REQUIRED — `map_emergence.py validate` rejects the empty
  `emergence/insights/INS-0047-*.md` file: its ID, project, detector, date,
  status, and short-description fields are absent or invalid.
- REQUIRED — `librarian.py validate` reports 18 wikilink findings: 15 broken
  links and three ambiguous bare AGENTS links in `INS-0039`, `INS-0042`, and
  `INS-0053`. Three broken links are known literal resolver examples in the
  TASK-238 review/release records; the other 12 are emergence cross-links.
- REQUIRED — Four released tasks declare eight output paths that do not resolve
  in the current workspace: `TASK-079` (ephemeral lock), `TASK-082` (old
  `/home/home` path), `TASK-085` (three old installed-binary paths), and
  `TASK-237` (three missing sibling `CommandCenterUI` paths). Preserve history,
  but reconcile provenance before treating these paths as current evidence.
- RECOMMENDED — Event validation has 0 errors but still has 1 new warning at
  line 2145: non-canonical type `TASK_SUBMITTED`; line 2146 contains the
  canonical `SUBMISSION` correction.
- RECOMMENDED — Emergence stale checking reports 12 lifecycle mismatches:
  `INS-0024`, `INS-0025`, `INS-0038` through `INS-0046`, and `INS-0050`
  remain RAW/CANDIDATE after their related tasks became RELEASED.

## Passing checks

- All 291 task files pass schema validation, and SQLite/task JSON/task-graph
  mirrors agree. Shared-state metadata, decisions, canonical paths, context
  packets, repair artifacts, and risk registers pass.
- All 128 SQLite-registered release checklists validate (67 full, 61 low).
  Every full-tier release has a structurally valid APPROVED review artifact,
  and every release has APPROVED and RELEASED events. Of 638 registered release
  output paths, 630 resolve and the eight exceptions are listed above.
- The backlink index builds with 115 targets and 260 edges.
- No task, database, event, backlink, review, release, or source state was
  changed. This audit updated only this helper note and preserved the existing
  dirty worktree.

---

## Prior audit — 2026-07-22

- REQUIRED — Research validation fails for
  `artifacts/research/SUMMARY-herdr-comparison-2026-07-22.md`. The completed
  document does not use the Research Summary contract and is missing all eight
  required fragments: title/ID, Question, Answer, Confidence, confidence-decay,
  open-questions, and downstream-effect fields.
- REQUIRED — `librarian.py validate` reports three broken wikilinks, all literal
  resolver examples in the TASK-238 release/review records (`dot-slash stem`,
  `dot-slash angle-bracket stem`, and `dot-slash b`). The backlink index still
  builds (96 targets, 222 edges); the helper note no longer repeats those strings
  as parseable links.
- RECOMMENDED — Event validation has 0 errors but 1 new warning at line 2145:
  non-canonical type `TASK_SUBMITTED`. Line 2146 already carries the canonical
  `SUBMISSION` correction; preserve append-only history and reconcile the
  warning baseline or validator treatment intentionally.
- RECOMMENDED — Emergence structure passes for 86 records, but the stale check
  reports `INS-0024` and `INS-0025` still `RAW` after related tasks were
  released, plus `INS-0038` still `CANDIDATE` after `TASK-269` was approved.

## Passing checks

- Task schema, graph structure, and all SQLite/file mirrors pass; the earlier
  `TASK-266` drift is resolved. Shared state, decisions, canonical paths,
  repair, context, risk, and emergence structure pass.
- All 27 SQLite-recorded release checklist paths exist and validate. Their
  registered task output paths resolve, and each has a valid independent
  `APPROVED` review artifact.
- The 11-system Related-files matrix has 60 directed links, 30 bidirectional
  pairs, and no one-directional gaps.
- No task, database, event, backlink, review, release, or source state was
  changed. This audit updated only this helper note and preserved the existing
  dirty worktree.

## Prior audit — 2026-07-18

## Findings

- REQUIRED — `TASK-232` is `RELEASED`, but its only declared output path, `MAP_System/artifacts/research/hpom-operating-models-comparative-2026-07-18.md`, does not exist. The released evidence is instead `MAP_System/artifacts/research/SUMMARY-HPOM-OPERATING-MODELS-2026-07-18.md`. Reconcile the task record/output-path provenance before treating the task record as complete.
- REQUIRED — `librarian.py validate` reports three ambiguous bare AGENTS backlinks: `MAP_System/RISK_SYSTEM.md`, `MAP_System/SECURITY_PERMISSIONS_SYSTEM.md`, and `MAP_System/artifacts/planning/map-protocol-validator-spec.md`. Point each explicitly to `MAP_System/AGENTS.md`.
- Follow-up — `TASK-236` remains `CHANGES_REQUESTED`; no release action is indicated.

## Passing Checks

- Task schema, task graph, SQLite/file task mirrors, shared-state metadata, decisions, canonical paths, context packets, risk registers, repair artifacts, research artifacts, and emergence artifacts pass.
- Event validation: 0 errors and 0 new warnings (33 baselined legacy warnings).
- All 22 release-checklist paths recorded in SQLite for `TASK-206` through `TASK-234` validate, including the ClearFront-local `TASK-220` checklist.
- Sampled MAP and ClearFront review records validate, including the batched `TASK-223`–`225` review. Approved `TASK-222`–`226` have SQLite review provenance; they are not yet released.

## Scope Note

- No task, database, event, review, release, or source state was changed. The pre-existing dirty worktree was preserved; this audit updated only this helper note.

## Resolution — 2026-07-18 (claude-lab-lure)

- REQUIRED (`TASK-232` output path) — RESOLVED. The stale `hpom-operating-models-comparative-2026-07-18.md` path was the task's *original* unrecognized input, which TASK-232 normalized into `SUMMARY-HPOM-OPERATING-MODELS-2026-07-18.md` (per its own title/description). Removed the nonexistent path from all three mirrors: `tasks/TASK-232.json`, `workflow/task_graph.json`, and `map.db` `task_output_paths`. Remaining outputs (SUMMARY + `SYN-0002`) exist on disk; JSON/graph/db now agree.
- REQUIRED (3 bare AGENTS backlinks) — RESOLVED. Disambiguated to `[[./AGENTS.md]]` (the only ROOT-relative form the resolver accepts for a top-level file that shares the `AGENTS` stem with `templates/install/command-center-ui/AGENTS.md`) in `RISK_SYSTEM.md`, `SECURITY_PERMISSIONS_SYSTEM.md`, and `artifacts/planning/map-protocol-validator-spec.md`.
- Verification: `librarian.py validate` → 0 findings; `validate_task_mirrors`, `validate_task_graph`, `validate_task_schema`, `validate_research_artifacts`, `validate_canonical_repo_paths` → pass; `validate_events` → errors=0, new_warnings=0.
- Follow-up `TASK-236` (`CHANGES_REQUESTED`) untouched — no release action indicated.
