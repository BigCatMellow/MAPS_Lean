# MAP Practice Lifecycle Evidence Audit — 2026-07-18

## Scope and scenario

Hypothetical project: an operator requests a small, two-session utility with one implementation task. The implementer reaches a provider limit after partial verification; another session resumes it; a different agent reviews it; the task is released.

This is a read-only trace of current MAP guidance, scripts, and worked records. “Observed” means directly present in a cited durable file or executable interface. “Inference” means the likely operational effect.

## Compact lifecycle trace

| Stage | Minimum durable path observed | Result |
|---|---|---|
| Operator brief | `scripts/command_center_intake.py` classifies the request, emits an intake event unless `--no-event`, and prints runner routing; `ORCHESTRATION_ENTRYPOINT_SYSTEM.md` says the packet is not task authority. | Clear separation between intent and executable authority, but the packet has no named durable file of its own. |
| Kickoff | `PROJECT_BOOTSTRAPPING_SYSTEM.md` / `NEW_PROJECT_WIZARD.md` require project intent, requirements, assumptions/research disposition, risk register, decision paths, and Emergence folders before the first task; trivial/throwaway work may skip steps 3–7. | Strong continuity foundation for multi-session work; judgment is required to decide whether a “small” project earns the full structure. |
| Task shaping | `map_task.py create` writes SQLite first, assigns an ID atomically, derives `READY` only when description/output/criterion exist, then exports task and graph mirrors. `task-authoring-guide.md` makes output paths ownership boundaries. | One accountable, machine-checkable work record; no chat reconstruction is required. |
| Implementation | `CONTEXT_SYSTEM.md` and `notes/context-routing-guide.md` direct the worker to the task, current state, inputs, and outputs, expanding only on triggers. Claims/heartbeats live in `db/claims.py`; progress belongs in `events/events.jsonl`. | Bounded context and explicit ownership work when the task metadata is complete. |
| Session-limit interruption | `notes/limit-exhaustion-protocol.md` calls for availability state, claim heartbeat/submit, a handoff with exact resume commands, and an hcom notice. Its worked `HANDOFF-DEC012-git-sequence-codex-lab-limo.md` preserves completed gates, blocker, safe scope, commands, and remaining steps. TASK-221 adds a persistent deterministic watcher for sessions that cannot write a final turn. | Lost execution capacity is recoverable; lost final-turn context is only partly recoverable because the watcher can restart a session but cannot manufacture the missing handoff. |
| Next-session resume | Quickstart points to current state, tasks, events, and handoffs; the handoff README specifies continuation fields. Task JSON has no handoff pointer field, and generic MAP has no `LATEST_STATE.md` convention like Pathwell’s documented one. | Durable evidence exists, but locating the authoritative resume packet can require directory/event searching. |
| Review | `notes/review-guide.md` requires task/output-first reading, independent review, concrete findings, verification, and a template artifact; `claim_review()` reduces duplicate reviews. TASK-220’s events show a real `CHANGES_REQUESTED` → rework path. | Independent verification and rework are explicit and evidenced. |
| Release | `release_task.py` validates mirrors, requires an approved task and five checked lines, records release in SQLite/events, and exports mirrors. TASK-221 has an APPROVED then RELEASED event and a checklist artifact. | State transition is mechanically guarded, but policy text is inconsistent about whether low-risk work needs the same standalone release record. |

## What worked — observed facts

1. SQLite-first task creation/claiming plus human-readable mirrors gives both atomic ownership and inspectable recovery state (`map_task.py`, `db/claims.py`, `validate_task_mirrors.py`).
2. Task descriptions, output paths, and acceptance criteria are sufficient to bound work without replaying chat (`task-authoring-guide.md`; current TASK records).
3. The interruption protocol preserves exact continuation evidence, and its TASK-079 handoff demonstrates safe recovery across agents rather than merely describing it.
4. Review and release have executable gates, durable artifacts, and event transitions; TASK-220 and TASK-221 provide current worked evidence of rework and release respectively.
5. Context guidance explicitly discourages full-tree/history loading and names triggers for expanding context (`CONTEXT_SYSTEM.md`, `context-routing-guide.md`).

## Friction and failure points

### F1 — startup reading authority conflicts (observed)

Root quickstart says reusable MAP work starts with root/MAP `AGENTS.md`; `MAP_System/AGENTS.md` additionally requires `shared/project-brief.md`, `shared/requirements.md`, and `shared/decisions.md` before editing. The Context System’s implementation minimum instead requires `AGENTS.md`, `shared/current-state.md`, the task, and task inputs; the routing guide also adds `shared/memory-map.md`. There is no single identical minimum stack.

Inference: a careful agent over-reads to satisfy every source, while a context-optimized agent risks violating the broader AGENTS rule. This is unnecessary context and compliance ambiguity at every task start.

### F2 — small-project bootstrap threshold is subjective (observed)

The wizard defines seven pre-task setup areas and permits skipping most for “genuinely trivial or throwaway” projects. No executable bootstrap validator or decision test observed here distinguishes a small durable project from a throwaway one.

Inference: similar small projects can receive radically different ceremony depending on the first agent, weakening both efficiency comparisons and continuity expectations.

### F3 — intake packet is transient between event and task (observed)

The intake wrapper can record an event and print a structured packet, while the orchestration doc explicitly says that packet is not a task. The packet has no required durable artifact path; only the later task becomes authority.

Inference: if shaping is interrupted after intake but before task creation, the event summary may be the only recovery source and may not preserve the full packet/decomposition reasoning.

### F4 — interruption evidence is durable but not directly discoverable (observed)

Handoffs have naming/content rules, but task schema contains no `handoff_paths`/`resume_from` field and generic MAP documentation does not designate a per-task latest handoff index. Events can link artifacts, but discovery requires searching the log or directory.

Inference: resume cost rises with handoff volume, and an older packet can be mistaken for the current one. This is most damaging exactly when a session died before its final update.

### F5 — risk-tier review and release policy disagree (observed)

The 2026-07-17 Review Guide says low-risk work may be owner-verified, batched behind one review, and skip a standalone release checklist. `CHANGE_CONTROL_SYSTEM.md` says every task is reviewed before approval, and `release_task.py` always requires a standalone checklist to reach `RELEASED`.

Inference: agents must either ignore the new tiering advice, leave low-risk tasks at `APPROVED`, or bypass the canonical release command. The intended efficient path is not executable as documented.

### F6 — release checklist duplicates mechanically known state (observed)

The gate requires checked lines for shared updates, decisions, follow-ups, event preparation, and Emergence consideration. Task outputs, event writes, and state are already machine-visible; only the reasoning and Emergence judgment inherently require human text. The template does not require a review-record field or verification block, although `CHANGE_CONTROL_SYSTEM.md` says release records require both.

Inference: checkbox completion can become rote while the higher-value provenance fields remain convention-only, creating verification friction without consistently improving evidence.

### F7 — hard-wall resume restores execution, not working memory (observed)

RnS v3 can detect provider limits and visibly resume a session without a surviving cloud agent. The same protocol states a resumed agent with no handoff is “awake but lost.”

Inference: the most failure-prone interruption mode still depends on the task/event/output trail being sufficiently current before the wall; automatic resume does not close the continuity gap by itself.

## First-principles structural-layer test

**Layer tested:** the full per-project bootstrap layer (`PROJECT_BOOTSTRAPPING_SYSTEM.md` / `NEW_PROJECT_WIZARD.md`).

**Test:** A structural layer earns its coordination cost only if, compared with the next-simpler durable path, it prevents a material lifecycle failure that is (a) plausible for this project, (b) not already prevented by task/claim/review/release records, and (c) worth more than the repeated cost of creating, reading, synchronizing, and validating the layer’s records.

**Concrete evidence:**

- The hypothetical utility spans two sessions and two agents, so durable intent and quality criteria are material; a chat-only approach fails the continuity test.
- A shaped task already preserves executable scope, owner, outputs, and acceptance criteria. The interruption handoff preserves partial state and resume commands. Review/release records preserve verification and outcome. These records cover much of the lifecycle failure surface without a full project shell.
- The full wizard additionally requires dispositions for assumptions/research, risks, decision authority, and four Emergence directories before the first task. For a small local utility with no external facts, sensitive data, or policy decision, no concrete failure in this scenario requires all of those records.
- ClearFront is counter-evidence for larger/riskier work: its project-local brief, requirements, decisions, risks, and emergence records supported a multi-task refactor, but its independent audit measured 89 MAP events and 60 artifacts across eight released tasks and found full ceremony excessive for a 78-line mechanical move (`Projects/ClearFront/artifacts/reviews/clearfront-independent-delivery-audit-2026-07-17.md`; adopted in `notes/review-guide.md`).

**Verdict:** The bootstrap layer earns its cost for projects expected to accumulate multiple interacting tasks, agents, risks, or decisions. It does **not** earn the full cost for this hypothetical small utility. The minimum sufficient structure is a project/task anchor carrying intent and quality criteria, one shaped task, event/claim state, and a handoff when interrupted; research, risk, decision, and Emergence structures should activate on explicit triggers. This is a reduction of unused structure, not removal of durable continuity.

## Ranked recommendations

1. **Unify one executable startup context contract.** Make `AGENTS.md`, Context System, and quickstart point to the same task-type minimum; generate or validate the packet from task metadata. Measure files/tokens loaded before first action and task-start rule violations.
2. **Make risk tier a task field and align gates to it.** Define low/medium/high once during shaping; have approval/release commands enforce the corresponding review and record requirements. Measure artifacts/events per released task, review defects found, and escaped defects by tier.
3. **Persist intake until promotion.** Store the complete dispatch packet as a bounded intake record with status `UNSHAPED`/`PROMOTED` and backlink the created task; do not create a second task authority. Measure interrupted intakes recovered without chat replay and orphaned packet age.
4. **Add a canonical resume pointer without duplicating handoff content.** A task/event-derived `resume_from` reference or generated per-task latest-handoff index should point to the authoritative packet and reject stale/superseded pointers. Measure median files searched and time-to-first-valid-action after resume.
5. **Derive release evidence mechanically, request judgment explicitly.** Generate known facts (task, review, validators, changed canonical paths, event readiness) and ask humans only for exceptions, rollback notes, follow-ups, and Emergence judgment. Align the template with the fields the policy already claims are required. Measure checklist authoring time and missing/incorrect provenance.

## Bottom line

MAP’s durable spine works: a future session can reconstruct authority, ownership, changes, verification, and release without chat history. The principal lifecycle risk is not missing storage; it is conflicting process contracts and weak pointers between already-existing records. The highest-value experiments therefore simplify and connect the current evidence path rather than add new artifact classes.
