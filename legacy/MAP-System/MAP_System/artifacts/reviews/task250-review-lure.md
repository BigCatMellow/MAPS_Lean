# Review: TASK-250 Plain-English academic deep dive to the MAP system

task_id: TASK-250
reviewer: claude-lab-lure
task_owner: codex-lab-kiri

## Verdict

APPROVED

An accurate, well-structured, genuinely system-wide explanation. Every checkable
factual claim I sampled matched the real implementation, and the document is
disciplined about current-vs-aspirational honesty. One minor wording nit
(RECOMMENDED) and one environmental note on AC4 (below); neither is a defect in
the document.

## Acceptance Criteria

| Criterion | Result | Evidence |
|---|---|---|
| AC1 — Explains MAP as an integrated socio-technical system: why each subsystem exists, its inputs/outputs, and how it relates to the rest. | PASS | §1–§2 frame the coordination problem and the interacting planes; each subsequent section states why the subsystem exists and its I/O (e.g. §3 three truths, §5 HPOM, §8 routing, §10 review/release, §12 emergence, §14 recovery). The plane diagram (§2) and "MAP is the relationship among them" capture integration, not a feature list. |
| AC2 — Covers task/state authority, HPOM, routing, hcom, review/release, helpers/local models, recovery, UI/observability, RnS, emergence, practice scenarios, and known limitations without presenting stale behavior as current. | PASS | All topics present (§3,§4,§5,§8,§9,§10,§12,§14,§15,§16,§19). Current-vs-aspirational is handled explicitly: §21 intro ("not every tool is a continuously running service"), §6 ("remains partly behavioral"), §8.4 ("capability, not evidence… fully unattended"), §22 (seven concrete non-guarantees), §22.6 ("check current state/code/tests before assuming a design doc describes deployed behavior"). Recent reality is reflected accurately — §16 lists the TASK-237 attention popup and the message-intent send semantics. |
| AC3 — Plain English, concrete end-to-end examples, diagrams, and distinguishes system facts from interpretation/tradeoffs. | PASS | Plain register throughout; ASCII diagrams (§2,§7.1,§8,§11.1,§12); a full 8-step end-to-end example (§20); explicit interpretation/tradeoff sections (§2.1, §23.6 failure-mode catalog, Closing). Facts vs interpretation are separated (e.g. §2.1 "academic interpretation", §23 reasoning framework). |
| AC4a — References point to current canonical MAP documents. | PASS | All 20 references in §25 exist on disk (verified each path). No broken or obsolete references. |
| AC4b — The task graph validates after export. | PASS (scoped) — see Risks | TASK-250's only output is `notes/map-system-deep-dive.md`, which collides with nothing; its export leaves its own record clean and `validate_task_schema`/mirrors pass. Repo-wide `validate_task_graph` is currently RED, but from unrelated concurrent tasks — see Risks. |

## Files Reviewed

- `MAP_System/notes/map-system-deep-dive.md` (full, 8137 words)
- Cross-checked against: `graph/runner.py` (route names, `DEPENDENCY_SATISFIED_STATUSES`), `scripts/pre_dispatch_policy.py`, `db/claims.py`, `scripts/` catalog, and every `§25` reference path.

## Accuracy Spot-Checks (all confirmed)

- §8.1 route names — exact match to `runner.py`: `review`, `policy_gate`, `wait_for_agent`, `propose_helper`, `claim_or_assign`, `wait_or_reconcile`.
- §8.2 dependency terminal states "DONE, APPROVED, or RELEASED" — exact match to `runner.py:39 DEPENDENCY_SATISFIED_STATUSES = {"DONE","APPROVED","RELEASED"}`; `DONE` is a real status (e.g. `tasks/TASK-011.json`).
- §5.1 tiers, §4.2 decision classes — match `pre_dispatch_policy.py` tier inference and AUTHORITY/POLICY handling.
- §8.3 "heuristics can produce false positives, so they are tested and reviewed as policy code" — accurate and timely (cf. the TASK-249 is_destructive prohibition-clause false positive).
- §21 catalog — every listed tool exists in `scripts/` (no fabricated tools).
- §14.2 RnS `out_of_tokens` + `resume_after` — matches `agents/status.json` and `limit_watcher.py`.

## Forbidden Changes Check

PASS — TASK-250 adds a single explanatory note under its registered output path.
No code, policy, authority, task-state, or shared-state change; the guide
explicitly subordinates itself to canonical sources (§25 closing) and to
executable evidence.

## Risks / Notes

- AC4b environmental (not a document defect): repo-wide `validate_task_graph`
  currently reports output-path collisions among **TASK-241/243/247/248**
  (`chat.css` x2 and `test_command_center_attention_history.py`) — the rapid
  UI-iteration serial-release issue kiri is already reconciling. TASK-250
  introduces none of these. Recommend confirming a green `validate_task_graph`
  at the APPROVED→RELEASED transition. Blocking the document itself on unrelated
  tasks' collisions would reproduce the exact serial-release anti-pattern the
  guide documents (§7.3, §22.5), so it does not gate this verdict.
- RECOMMENDED (minor wording): §16 says operator send uses
  "update/request/acknowledgment semantics"; align to the document's own §3.3
  and the real hcom intents — **inform / request / ack** ("update" → "inform").

## Verification

- `ls` on all 20 §25 reference paths — all present.
- `ls scripts/<tool>.py` for all §21 catalog tools — all present.
- `graph/runner.py` grep — route names and `DEPENDENCY_SATISFIED_STATUSES` confirmed.
- `validate_task_graph.py` — RED, collisions isolated to TASK-241/243/247/248 (not TASK-250).
- `validate_task_schema.py` / `validate_task_mirrors.py` — pass.
