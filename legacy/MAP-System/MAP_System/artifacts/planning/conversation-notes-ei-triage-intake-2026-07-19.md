<!-- hpom: file: artifacts/planning/conversation-notes-ei-triage-intake-2026-07-19.md -->
<!-- hpom: project: MAP -->
<!-- hpom: state_owner: codex-lab-kiri -->
<!-- hpom: status: SCOPED -->
<!-- hpom: last_verified: 2026-07-19 -->
<!-- hpom: verified_against: TASK-255; operator-provided conversation_notes.md; current MAP E/I, operational-learning, trace, liveness, indexing, and advisory-monitor artifacts -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# Conversation Notes Intake: Retrieval, E/I, and Explainable Triage

- task: TASK-255
- date: 2026-07-19
- owner: codex-lab-kiri
- source: `/home/mellow/Projects/MultiAgentProject/conversation_notes.md`
- status: architecture intake; no implementation authority

## 1. Conclusion

The conversation notes are useful because they do not reveal that MAP needs a
new orchestration system. They reveal a **missing middle layer** in the system
MAP already has.

MAP currently preserves substantial raw evidence and has several good compact
current-state projections. It also has early E/I detection, operational
lessons, trace IDs, liveness recovery, and a proposal-only advisory monitor.
What it does not yet have is a cheap, consistent way to answer:

> Which small pieces of prior work are likely to matter to this task, and
> which full sources should the agent open only if needed?

The smallest coherent answer is:

1. generate a tiny fingerprint for each completed task or resolved incident;
2. maintain compact, source-linked workstream digests;
3. search fingerprints before full documents, under a fixed token budget;
4. expand only the strongest few matches into primary evidence;
5. record waits and incidents in an explainable structure so they can later
   become useful E/I evidence;
6. keep all of this subordinate to `map.db`, current task records, decisions,
   and primary artifacts.

This is a retrieval projection, not a new memory authority and not a reason to
load more context at startup.

## 2. Source handling and evidentiary limit

The operator-provided file is a design conversation containing both original
reasoning and references to external systems and publications. This intake
compares its proposals to the local MAP implementation. It does **not**
independently validate the external references, quotations, or product claims.
They may support a later Research System pass, but they are not treated here as
verified evidence or as authorization to adopt an external tool.

No GitHub repository, issue, project, webhook, or external service was changed.
No new agent, helper, background process, database table, policy, or task-state
authority was created.

## 3. What MAP already has

| Idea from the notes | Existing MAP substrate | Assessment |
|---|---|---|
| Full history remains available but is not loaded by default | `map.db`, task mirrors, artifacts, events, handoffs, archive, brain compaction | Present as a storage and context-routing principle. |
| Compact current views over deeper truth | JSON/file projections, `shared/current-state.md`, task graph, Command Center cards | Present; MAP already behaves like an event-backed system with materialized views. |
| A navigation index | `shared/memory-map.md`, `notes/context-routing-guide.md` | Present but needs reconciliation through TASK-227; this is governing-document navigation, not historical retrieval. |
| Link summaries to primary evidence | Task output paths, artifact records, E/I wikilinks, trace fields | Present in pieces; not consistently generated for completed-task memory. |
| Long-range E/I | `emergence/`, `map_emergence.py`, the E/I Sentinel, Discovery Agent guide | Present as a governed pipeline. The current deterministic sentinel has narrow recall. |
| Selective behavioral memory | `agents/operational-lessons.json` and `operational_lessons.py orientation` | Present and appropriately gated: only promoted, scoped lessons enter startup behavior. |
| Live triage | RnS/limit watcher, liveness reaper, task claims and leases, advisory monitor | Present as several bounded mechanisms, but their findings do not share one explainable wait/incident envelope. |
| Traceability | `scripts/event_trace.py` and task trace IDs | Present; do not rebuild trace identity. |
| Outcome feedback | `outcome_pass` / `outcome_fail` metrics and event shape | Mechanism exists, but the current kickoff evidence found no real outcome-event sample. |
| Human attention surface | Command Center attention history/popups and hcom intent rules | Present; routine telemetry should remain outside operator-attention requests. |
| Proposal-only automated judgment | E/I Sentinel, MAP Steward, advisory monitor boundaries | Present and should remain the default authority ceiling. |

The notes therefore fit MAP best as a unifying model for existing components,
not as a parallel architecture.

## 4. The actual gaps

### 4.1 No completed-task fingerprint

A task record says what work was intended. Its artifacts and review say what
happened. MAP has no standard compact record that joins the two after release:
goal, result, changed surfaces, produced evidence, surprises, friction, and
reusable concepts.

Without that record, an agent must either know a task ID already, search broad
prose, or open several artifacts to learn whether a past task is relevant.

### 4.2 No workstream digest projection

Current-state files describe the system broadly, and task records describe one
unit of work. MAP lacks a compact projection for a continuing workstream such
as ClearFront UI, Command Center UI, agent liveness, or E/I experiments. A
digest should explain the current shape, recent changes, unresolved tension,
and most useful source links without copying mutable task status.

### 4.3 Historical retrieval has no token contract

The Librarian validates links and can measure structural compression. The
emergence index provides a compact registry. Session replay builds a disposable
index over approved sources. These are valuable components, but MAP has no
common retrieval contract that limits candidate count, snippet size, search
hops, or evidence-expansion cost.

### 4.4 Waits are observable but not uniformly explainable

MAP can represent task status, agent availability, leases, provider reset
times, liveness incidents, and advisory findings. It cannot yet express every
wait with the same minimum answers:

- why it is waiting;
- what the wait affects;
- what other work remains possible;
- what will resume it;
- when it should be checked again;
- what action, if any, is recommended.

### 4.5 Resolved incidents do not consistently feed E/I

The operational-learning path is sound once an insight exists. The missing
join is a compact, structured incident closeout that the E/I Sentinel can scan
without reading raw transcripts or inferring meaning from repeated status
events alone.

## 5. Two indexes with different jobs

MAP should not solve every form of retrieval with one giant index.

### 5.1 Navigation index: which governing source should I read?

`shared/memory-map.md` already claims this role. TASK-227 and its durable-memory
readiness audit own the open work to reconcile its stale link, routing
contract, and bounded population. It should remain small, maintained, and
authority-aware.

It should answer questions such as:

- Which file governs review?
- Where is current system state?
- Which source controls helper authority?
- What must be read for a CHANGES_REQUESTED task?

It should not contain hundreds of task summaries.

### 5.2 Retrieval index: which historical evidence might help now?

This should be a generated, disposable projection over compact fingerprints
and digests. It should answer questions such as:

- Have we changed these files before?
- Did another project encounter the same failure mechanism?
- Which prior review discovered a related blind spot?
- Is there a promoted lesson or unresolved contradiction relevant to this
  task?

It may rank and link evidence. It may not change task scope, promote an idea,
declare a source canonical, or make a hidden coordination decision.

## 6. Proposed task fingerprint

The fingerprint should be structured enough for deterministic filtering and
short enough to scan cheaply. Initial experiment values are deliberately
small; measurement should change them if needed.

| Field | Purpose |
|---|---|
| `task_id`, `project_id`, `workstream` | Stable scope and grouping. |
| `goal` | One sentence describing intended outcome. |
| `result` | One sentence describing the actual outcome, including non-delivery. |
| `changed_paths` | Normalized files or components actually changed. |
| `produced_paths` | Primary artifacts, reviews, tests, or release evidence. |
| `concepts` | Small controlled/free-tag set for mechanisms and domain ideas. |
| `unexpected` | Surprise, contradiction, or important discovery; empty is valid. |
| `friction` | Failure, delay, rework, or coordination cost; empty is valid. |
| `outcome` | Later reality signal when known: pass, fail, mixed, or unknown. |
| `source_refs` | Direct paths/event IDs supporting each nontrivial claim. |
| `source_hashes`, `generated_at`, `generator_version` | Staleness and reproducibility. |

Recommended size for the first experiment: **100–180 words per task**, with no
more than eight concepts and no copied review prose. A deterministic extractor
should populate IDs, paths, status, and artifacts. A core owner may curate the
semantic fields during the experiment; a model-generated fingerprint remains
a draft until accepted by the accountable owner.

The fingerprint is not an additional completion report. It is a search record
that links back to the actual task, review, and evidence.

## 7. Proposed workstream digest

A workstream digest is not a concatenation of fingerprints. It is a small
materialized view, rebuilt only after a meaningful release, outcome, resolved
incident, or explicit workstream reassignment.

Proposed fields:

- workstream and project;
- current objective and boundary;
- recent material changes, each linked to a task fingerprint;
- current known tensions or contradictions;
- active promoted lessons;
- unresolved candidates that are evidence, not instructions;
- last verified time and source watermark;
- five to ten best primary references.

Recommended experimental ceiling: **500–800 words per workstream**. A digest
must identify its source watermark and report itself stale when newer relevant
records exist. It cannot mirror live task ownership or agent presence; those
remain live queries.

## 8. Token-budgeted retrieval contract

The agent should never start by loading the full index into context. Retrieval
should happen as a bounded query:

```text
current task + project + touched paths + concepts + failure clues
                              |
                              v
       deterministic filters and lexical ranking over fingerprints
                              |
                              v
     <= 6 compact candidates with match reasons and source references
                              |
                              v
       open <= 2 primary sources only when evidence is actually needed
```

### 8.1 Query seed

Use facts already present in the active task and current observation:

- project/workstream;
- title and goal terms;
- registered and currently changed paths;
- task type and role;
- explicit error text or incident category;
- concepts already named by the operator or task owner.

Do not infer sensitive or private query terms from raw transcripts.

### 8.2 First-stage retrieval

Start with deterministic filters plus lexical/full-text search over the compact
records. Useful ranking signals include:

1. same changed path or component;
2. same project/workstream;
3. matching concept or failure category;
4. a direct task, artifact, or trace relation;
5. promoted lesson or verified outcome relevance;
6. recent material evidence, with older direct matches still eligible;
7. penalties for stale, historical-only, superseded, or weakly sourced items.

The first experiment should use SQLite/full-text or an equivalently local,
deterministic lexical index. Embeddings and a vector service add cost,
staleness, privacy, and ranking opacity; they should be tested only if the
lexical baseline misses known useful evidence.

### 8.3 Retrieval packet

The result returned to the agent should contain:

- the query and token/evidence budget;
- no more than six candidates;
- for each candidate: ID, 40–80 word summary, why it matched, lifecycle,
  confidence, and primary source paths;
- an explicit `no strong match` result when appropriate;
- index watermark and staleness warning;
- suggested next source, not automatically loaded source content.

Initial experimental ceiling: **1,200 estimated tokens for discovery**. The
agent may then open at most two primary sources in the normal context budget.
More expansion requires a concrete reason recorded in the task notes; it must
not become automatic recursive retrieval.

### 8.4 Retrieval feedback

For measurement, record only compact operational feedback:

- query ID and task trace ID;
- candidate IDs shown;
- sources actually opened;
- useful / not useful / missed-known-evidence adjudication;
- approximate discovery size and latency.

Do not store the agent's hidden reasoning or duplicate the retrieved source.

## 9. Index lifecycle and staleness

The retrieval index must be rebuildable from approved durable sources.

- Source records remain authoritative; index rows are disposable.
- Every row carries source hashes and a generator version.
- A release, review closeout, resolved incident, or later outcome can mark the
  relevant fingerprint/digest stale.
- Rebuilding is deterministic and idempotent where fields are mechanical.
- Curated semantic fields retain curator identity and evidence references.
- Deleted or superseded sources remain discoverable only with an explicit
  historical lifecycle label.
- A broken source link is an index-health failure, not permission to guess.

The index should initially cover a small frozen corpus. It should not scan raw
hcom/model transcripts, browser history, arbitrary home files, secrets, or all
repository prose.

## 10. E/I and triage remain separate loops

The source correctly distinguishes two timescales.

### E/I asks

> Across completed or resolved work, what reusable relationship, recurring
> cause, contradiction, opportunity, or method is becoming visible?

Its output remains a candidate for visible curation and the existing
Insight → Synthesis → Idea → Experiment → Promotion lifecycle.

### Triage asks

> What is preventing or delaying progress now, what is its impact, and what
> bounded response is justified?

Its output is an advisory finding, recovery action already authorized by a
narrow runbook, or an operator request when authority is required.

Triage must not promote its own lesson. E/I must not seize control of live
work. A **resolved incident summary** is the explicit bridge between them.

## 11. Explainable wait and incident envelope

The notes propose a rich task-state vocabulary. MAP should not immediately
replace its established task state machine with many new waiting states. That
would affect claiming, routing, graph logic, review, metrics, and UI behavior.

Instead, first test a subordinate wait/incident envelope linked by the existing
task trace ID:

| Field | Meaning |
|---|---|
| `finding_id`, `trace_id`, `task_id` | Identity and causal link. |
| `kind` | wait, blocker, retry, failure, degradation, or recovery. |
| `waiting_on` | agent, human, tool, external system, time, dependency, or none. |
| `reason` | Observable cause, not an invented root cause. |
| `impact` | What cannot proceed and what remains unaffected. |
| `alternative_work` | Safe useful work that may continue. |
| `resume_condition` / `check_after` | Evidence or time that justifies another check. |
| `recommended_action` | Observe, recommend, bounded intervention, or escalate. |
| `authority_needed` | none, assigned owner, reviewer, or operator. |
| `evidence_refs` | Events, status, task, tool output, or incident sources. |
| `state` | open, resolved, superseded, or false_positive. |
| `resolution` / `prevention_candidate` | Compact closeout and possible E/I input. |

The core rule is:

> A task may wait, but its waiting state must be explainable.

The UI can render this envelope without treating every wait as an alert. Only
operator authority, an unresolved blocker, privacy/scope risk, conflict, or
failed recovery belongs in the operator attention queue.

TASK-236's advisory monitor is the natural existing host for detection and
proposal formatting. Its independent review requested broader fixtures and
source-accurate malformed-claim handling. TASK-255 does not edit or transfer
that task; its owner should incorporate this envelope only after completing
the existing rework.

## 12. Adopt, extend, experiment, defer

| Disposition | Proposal |
|---|---|
| Adopt as a design principle now | All history searchable, not all history loaded. Consolidation replaces accumulation. Summaries link to evidence. Waiting must be explainable. E/I and triage have different authority and timescales. |
| Extend existing systems | Add task fingerprints and workstream digests as generated retrieval projections; give resolved incidents a compact E/I bridge; expand sentinel inputs to approved review/incident/outcome sources. |
| Experiment before adoption | Lexical fingerprint retrieval, token-budgeted result packets, digest usefulness, wait-envelope UI, and later semantic retrieval if the lexical baseline fails. |
| Defer | Embeddings/vector database, a full knowledge graph, a new always-on triage agent, a new E/I authority, automatic promotion, raw-transcript indexing, or broad task-state replacement. |
| Separate operator decision later | GitHub issue/project/PR mirroring, webhooks, or any external write/integration. GitHub may become secondary institutional memory, never MAP's live task database or semantic memory. |

## 13. Bounded experiment sequence

### Experiment 0 — reconcile navigation, do not add a peer index

Finish TASK-227's existing rework: choose and repair the current navigation
host, prove five governing-document lookups in two hops, and remove the stale
route. This is a prerequisite for clarity, not the historical retrieval index
itself.

### Experiment 1 — frozen task-fingerprint retrieval

- Corpus: approximately 20 completed tasks from one bounded workstream plus a
  small number of deliberately related cross-project tasks.
- Freeze 10–15 realistic queries and a human-reviewed truth set of useful
  evidence before tuning ranking.
- Compare the current manual/`rg` path with fingerprint-first lexical search.
- Return at most six candidates and no more than 1,200 estimated discovery
  tokens.
- Do not integrate into startup or the Command Center yet.

Provisional success evidence:

- recall@6 at least 80% on the frozen truth set;
- zero critical known-evidence misses;
- every result cites a resolvable primary source;
- median discovery packet stays below the token ceiling;
- fewer full documents are opened than the baseline;
- a fresh reviewer judges at least 70% of shown candidates useful.

These are experiment thresholds, not permanent policy.

### Experiment 2 — one workstream digest

Build one digest from the same corpus. Ask a fresh agent to answer a frozen set
of current-shape, recent-change, unresolved-tension, and source-location
questions. Measure correctness, tokens loaded, stale claims, and whether the
agent still reaches primary evidence when needed.

### Experiment 3 — approved-source E/I recall

Extend the existing E/I Sentinel experiment to scan compact review findings,
resolved incident summaries, and later outcome events. Reuse the existing four
item truth set and add positive discoveries. Measure recall, duplicate rate,
useful-candidate rate, and source-specific noise. Do not read raw transcripts
or auto-promote candidates.

### Experiment 4 — explainable waits

After TASK-236 rework, stage fixtures for a provider wait, human decision wait,
tool failure with alternative work, malformed claim, external dependency, and
clean no-finding state. Measure source accuracy, false positives, recovery
clarity, operator interruptions, and whether a resolved summary is usable by
E/I without reopening raw telemetry.

### Experiment 5 — semantic retrieval only if earned

Review lexical misses. If important matches consistently use different
language and cannot be recovered with controlled concepts, test embeddings on
the same frozen corpus and truth set. Adoption requires a material recall gain
without violating privacy, token, staleness, or explainability limits.

## 14. Measures that matter

The index succeeds only if it helps agents find better evidence with less
context and less operator burden.

- retrieval recall and precision on a frozen truth set;
- discovery tokens and number of full sources opened;
- time to first useful primary source;
- broken/stale reference rate;
- candidate usefulness and duplicate rate;
- critical evidence misses;
- E/I truth-set recall and false-positive load;
- triage detection latency and factual accuracy;
- unnecessary operator attention requests;
- documentation/curation overhead per completed task;
- later real-world outcome pass/fail, not validator pass alone.

## 15. Ownership and next decision boundaries

- TASK-227 remains the owner of governing-document navigation reconciliation.
- TASK-236 remains the owner of the advisory-monitor rework.
- The existing E/I Sentinel and emergence lifecycle remain the learning path.
- The current operational-learning mechanism remains the only route from a
  promoted lesson into scoped startup behavior.
- A future fingerprint experiment should be its own small task after the
  current prove-it roadmap selects the workstream and evidence budget.
- Any schema migration, background service, GitHub integration, new autonomous
  authority, or operator-facing deployment requires a separately scoped task
  and the appropriate decision/review gate.

The recommended next implementation is not a universal memory engine. It is a
small offline retrieval experiment over a frozen corpus, judged against known
answers and a hard context budget.

## 16. Sources inspected

- operator source: `/home/mellow/Projects/MultiAgentProject/conversation_notes.md`
- `MAP_System/shared/current-state.md`
- `MAP_System/shared/memory-map.md`
- `MAP_System/migration/schema.sql`
- `MAP_System/scripts/event_trace.py`
- `MAP_System/scripts/librarian.py`
- `MAP_System/scripts/emergence_sentinel.py`
- `MAP_System/scripts/advisory_monitor.py`
- `MAP_System/notes/discovery-agent-guide.md`
- `MAP_System/notes/operational-learning-guide.md`
- `MAP_System/notes/agent-incident-taxonomy.md`
- `MAP_System/artifacts/tests/emergence-sentinel-pilot.md`
- `MAP_System/artifacts/experiments/durable-memory-index-readiness-audit-2026-07-18.md`
- `MAP_System/artifacts/command-center-ui/map-steward.md`
- `MAP_System/notes/system-improvement-implementation-plan.md`
- TASK-227, TASK-236, TASK-250, TASK-251, and their relevant review/planning artifacts
