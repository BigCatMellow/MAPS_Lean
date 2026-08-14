<!-- hpom: file: notes/system-improvement-implementation-plan.md -->
<!-- hpom: project: MAP -->
<!-- hpom: state_owner: claude-lab-gome -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-18 -->
<!-- hpom: verified_against: TASK-227 rework; task227-review-lilo.md (5 REQUIRED); coordination-surface + durable-memory-index readiness audits; map-practice-lifecycle-audit; system-improvement-plan-challenge -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# System Improvement Implementation Plan (TASK-227)

Resumable context: this plan turns
[[system-improvement-kickoff]] (`MAP_System/notes/system-improvement-kickoff.md`)
into implementation actions, using
[[book-lessons-agent-system]] (`MAP_System/notes/book-lessons-agent-system.md`)
as the design rationale. Read those two first when resuming; this note
deliberately does not restate their content.

Design spine (unchanged): MAP is a coordination system that uses AI
workers. Improvements target structure, visibility, feedback, authority,
and durable learning. Hidden state and hidden authority are the failure
modes. Prefer leverage-point changes over added process.

## North-star outcome (what all of this jointly serves)

**One operator can guide a real project from intent through
interruption and recovery to a reviewed release, and trust the system's
visible state at every step without reading the repo by hand.**

That single sentence is the fitness target. The workstreams below are
not ends in themselves — "more status, more notes, more rules" is a
failure mode, not progress (Thinking in Systems: optimize the loop, not
the motions). Each immediate task therefore names (a) the slice of that
lifecycle it improves and (b) one observable measure or practice
scenario it must move. **If a shipped change does not move its measure,
the honest result is to record the negative and revert it, not to keep
it because it was built.**

The lifecycle this outcome spans, with the concrete seams the read-only
practice audits already found
(`artifacts/experiments/map-practice-lifecycle-audit-2026-07-18.md`,
F1–F5):

| Lifecycle stage | Current state | Seam this plan targets |
|---|---|---|
| Intent → task | Works (intake → `map_task.py`, SQLite-first) | F1 startup-read ambiguity (touched by 2a) |
| Implementation | Works when task metadata complete | — |
| Interruption | Recoverable capacity; partial final-turn loss | F4 handoff not directly discoverable (backlog, below) |
| Resume | Durable evidence exists, discovery costs | F1/F4 (2a index route + backlog) |
| Review → release | Executable gates | F5 review/release tier disagreement (backlog, below) |
| Visible state throughout | **Weakest link** | 1a coordination surface |

Priority order below is derived from "which seam most blocks the
north-star for the operator right now," not from workstream numbering.

## What is already shipped (do not re-plan it)

The kickoff was written before this week's releases landed. Honest
inventory first, per its own "fix the loop, not the symptom" principle:

| Kickoff workstream | Already-shipped coverage |
|---|---|
| 5. Monitoring and nudge behavior | **Largely done by TASK-221** (released 2026-07-18): deterministic, provenance-gated, SQLite-first limit supervisor; visible systemd service; bounded retries; evidence + focused tests. Remaining: only the generic "scheduled reminders tracked as durable records" convention (action 5a, now bounded per C4). |
| 4. Discovery and review loop | **Partially codified**: risk-tiered review (TASK-218, `notes/review-guide.md`), review claims (TASK-199), debate pre-escalation (TASK-204), emergence promotion gates (`emergence/IDEA_PROMOTION_RULES.md`), Discovery Agent guide (`notes/discovery-agent-guide.md`, EXP-0003/TASK-226). Remaining: confirm the proposal-only rule is stated where the Discovery Agent role reads it (action 4a). |
| 3. Helper boundaries | **Mostly written already** in `MAP_System/AGENTS.md` (Elastic Helper Agents). Remaining: the "no unreviewed policy engine / no direct core-truth mutation" rule, which is an **AUTHORITY-class decision**, not documentation (action 3a). |
| 2. Durable memory and learning | **Pattern exists** (notes/, decisions.md, emergence, delivery notes per TASK-219) but has a real gap and an existing host: `shared/memory-map.md` already claims to be the durable index and has a stale link. Reconcile it, do not add a peer index (action 2a). |
| 1. Visible coordination surface | **Partially**: Command Center exists; `agents/status.json` is durable; TASK-203 added MAP-health rows; `chat.html` already shows hcom presence, queue counts, and a limited "Needs you" inbox. The north-star's per-agent trust question is not yet answered (action 1a). |
| 6. Command Center UX cleanup | Not started; depends on 1a's data contract being correct first. |

## Workstream actions

Risk lanes per `notes/review-guide.md` (TASK-218). "Task now" items get
records immediately; "backlog" items go to `shared/improvement-backlog.md`
until their trigger fires.

### 1. Visible coordination surface

**1a (task now, medium risk).** A read-only per-agent coordination card
for live core agents and running helpers. **This is a read model, not a
new store, and it must make disagreement visible rather than synthesize
a single status** — the exact stale-state risk C1 flagged. Contract
(from `artifacts/experiments/coordination-surface-readiness-audit-2026-07-18.md`):

- **Field authority / source of each field:**
  - *Durable status* (`status`/`reason`/`resume_after`) ← `agents/status.json`,
    shown verbatim; authoritative only for the durable board. No per-agent
    update timestamp exists, so only whole-file capture age may be shown
    (clearly labelled as file-level, never as per-agent freshness).
  - *Active claim* ← `MAP_System/map.db` read-only; active **only** when
    task status is `IN_PROGRESS`, `claimed_by` set, and `lease_expires_at`
    not passed at read time. Task JSON/graph mirrors never decide claim
    liveness. Expired/malformed lease → attention reason, not a claim.
  - *Latest meaningful action* ← latest valid action-bearing MAP event for
    that sender, with its `created_at`; not proof the agent is live or the
    action completed. Parse error / missing timestamp → `unknown`.
  - *Needs-attention* ← source-labelled multi-reason set, no single
    authority: unanswered live request (hcom), pending approval gate
    (SQLite), fresh blocked terminal (hcom), expired claim (SQLite),
    pending review = `SUBMITTED` task (SQLite). A historical `BLOCKED`
    event alone is history, never a current attention fact.
- **Conflict/unknown behavior:** when live hcom presence and durable
  status disagree, show **both** values plus a visible `conflict/unknown`
  result. Never infer capacity/availability or a replacement durable value.
- **Live-helper inclusion rule (C5):** join live hcom identity with a
  matching active `inbox/helpers/*.md` note; show unmatched/ambiguous
  identities as attention warnings, never silently guessed cards; drop
  cards for terminated sessions.
- **Acceptance — one deterministic mixed-state test per fixture, plus a
  staged screenshot** (screenshot alone insufficient):
  1. Stale durable status: hcom `listening` + durable `standby/out_of_tokens`
     with passed `resume_after` → renders both + `conflict/unknown`, no
     capacity claim.
  2. Live action newer than durable file: event at `T1` > board file mtime
     `T0` → action shows event time, durable shows only whole-file age,
     card states per-agent durable freshness unknown.
  3. Expired claim: `IN_PROGRESS` + `lease_expires_at` < read time → `no
     active claim` + `expired claim` attention reason naming task+claimant.
- **Output paths (from the audit):** CommandCenterUI `app/server.py`,
  `src/chat.{html,js,css}`, `agents/README.md` (authority/freshness/conflict
  contract text), `MAP_System/tests/test_coordination_surface.py`,
  `scripts/run_tests.sh` (register the test).
- **Lifecycle slice:** "visible state throughout." **Measure:** in the
  three staged fixtures an operator names each agent's durable state,
  owned work, latest action, and exceptions from the card alone — versus
  today's manual join of presence panel + raw hcom + event log + SQLite.

**1b folded into 1a** — the `agents/README.md` read/write contract is
now part of 1a's output (C1 required it there), not a separate item.

### 2. Durable memory and learning

**2a (task now, low risk).** **Reconcile the existing navigation host;
do NOT create `notes/INDEX.md`.** `shared/memory-map.md` already presents
itself as the durable Markdown-memory index and already has a stale link
(names missing `notes/task-metadata-repair-plan.md`); a second index
would create a shadow route (C2, resolved by
`artifacts/experiments/durable-memory-index-readiness-audit-2026-07-18.md`).

- **First decision in the task:** repair `memory-map.md` in place, or (only
  if that task shows why) add a thin subordinate notes projection. Prefer
  repair.
- **Bounded initial population — max 12 routes**, not a directory dump:
  the 7 baseline/conditional orientation entries (current-state,
  memory-map, project-brief, requirements, decisions, operational-lessons,
  assigned-task) plus one each for review, helper routing, task authoring,
  operational recovery, and emergence/promotion.
- **Per-route schema:** `path` (must resolve), `role`
  (authority/current-state/task/navigation/procedure/historical-evidence —
  a navigation entry never confers authority), `lifecycle`
  (CURRENT/HISTORICAL/SCOPED; SCOPED needs a trigger), `read_when` (trigger
  + next hop), `canonical_for` (or `none`; never mirrors mutable status),
  `owner`, `verified_against` (or `unverified` — stale is visible, not
  silently authoritative).
- **Link rule:** index points to canonical sources and says when to read
  them; it must not mirror task status, agent presence, capacity, authority
  rules, or lesson text.
- **New-note classification:** the task owner who adds/supersedes/materially
  changes a CURRENT operating doc proposes its row in the same task;
  ambiguous classification → `unverified`, never an inferred route.
  Maintainer = current `memory-map.md` state owner (`command-center`).
- **Acceptance — five reproducible ≤2-hop lookup samples** from a fresh
  context packet, each naming the governing doc and its CURRENT/HISTORICAL/
  SCOPED label: (1) active-task rework — **must route to the latest review
  record when status is CHANGES_REQUESTED**, (2) review, (3) helper routing
  — must name live-availability + operational-lesson checks as conditional,
  (4) startup/recovery, (5) E/I promotion. Every entry resolves to an
  existing path; the missing link is removed/corrected/marked HISTORICAL.
  Validator deferred until measured drift (one stale link ≠ a new gate).
- **Lifecycle slice:** "resume / F1 startup ambiguity." **Measure:** a
  fresh session following only `AGENTS.md` → reconciled index reaches the
  governing doc for each of the five lookups in ≤2 hops; today the startup
  read-lists in AGENTS Core Protocol, context-routing-guide, and the lab
  restart note disagree (F1), forcing over-read or non-compliance.

### 3. Helper boundaries

**3a — split into an AUTHORITY decision + a documentation follow-on
(C3).** The "helpers may summarize/draft/classify/check but never mutate
core truth (`map.db`, `shared/`, task records) directly — mutations go
through the accountable owner" rule **changes who may act**, so
`DECISION_CLASSES.md` makes it **AUTHORITY class, requiring
command-center approval** per `DECISION_AUTHORITY_SYSTEM.md`. It is not
independently-implementable low-risk prose.

- **3a-i (decision, command-center approval required):** propose the
  no-direct-core-mutation rule as an AUTHORITY-class `DEC-NNN` in
  `shared/decisions.md`; route the request to command-center; do not
  change any cross-reference or helper-permission text until approved.
  Note the current-state check: this must reconcile with existing helper
  permission text in `AGENTS.md` rather than silently overriding it.
- **3a-ii (task now, low risk, AFTER 3a-i approval):** once approved,
  consolidate the helper rules scattered across `AGENTS.md`,
  `notes/helper-agent-guide.md`, and `notes/local-model-helper-guide.md`
  into one canonical section (AGENTS.md canonical; notes point at it),
  and add the approved rule's cross-reference.
- **Lifecycle slice:** "hidden authority" prevention. **Measure:** after
  approval, exactly one canonical statement of helper mutation authority
  exists, and `DECISION_CLASSES.md` classification is satisfiable by
  inspection.

**3b (backlog).** Mechanical fitness check (`validate_helper_notes.py`):
every active helper tag in hcom events has a matching
`inbox/helpers/*.md` note with owner + scope. Trigger: next helper
incident, or a quiet week. One data point is not yet a pattern.

### 4. Discovery and review loop

**4a (task now, low risk, batchable with 2a).** Confirm the
proposal-only rule is stated where the Discovery Agent role actually
reads it (`notes/discovery-agent-guide.md` and
`emergence/IDEA_PROMOTION_RULES.md`): candidate cards only, promotion
always through the existing gate with a core-agent owner, findings freeze
before helper output is read. The plan-challenge memo found no material
issue here (matches EXP-0003/TASK-226); this is a confirmation, not new
machinery. **Measure:** a discovery pass can register a candidate without
any path to auto-promotion.

**4b (no action).** The rest is shipped review machinery; explicitly
declining to add steps (audit lesson: ceremony is a cost).

### 5. Monitoring and nudge behavior

**5a (task now, low risk, batchable with 2a/4a) — bounded per C4.**
Before writing any convention, **inventory the currently-active recurring
processes** (limit_watcher/TASK-221 supervisor, any Sentinel/monitor
timers, UI polling loops). Then draw the boundary explicitly:
**state-changing or message-sending** processes require a durable record
(trigger, interval, intent level inform/request, output location);
**pure read-only rendering/polling** (e.g. the 8s presence poll) is
documented where it already lives and is **not** in scope. Apply the
convention **prospectively** — no retroactive untestable debt. TASK-221's
supervisor is the worked example of the record shape. **Measure:** every
message-sending recurring process has a findable record; no safe UI
timer is misclassified as prohibited automation.

**5b (no action).** Supervisor itself shipped/reviewed/released
(TASK-221); one RECOMMENDED refinement (narrow Codex `agent_message`
provenance) already tracked in that review.

### 6. Command Center UX cleanup

**6a (backlog, gated on 1a).** Consequence-labelled controls, per-role
cards, hover detail — implemented against 1a's corrected, source-labelled
data, with a before/after screenshot pair as acceptance. Trigger: 1a
released. UI polish before the underlying state is truthful is backwards
(Design of Everyday Things: visibility of *true* state).

## Evidence intake and iteration (C4)

This plan is a snapshot, not a standing policy engine. New investigation
results feed the *next revision* of this plan as **candidates**, never as
automatically-added tasks.

- **Completed evidence already folded in** (read-only, no ownership
  transfer): the two readiness audits (coordination-surface,
  durable-memory-index) resolving C1/C2; the practice-lifecycle audit
  (F1–F5); the discovery-practice lifecycle pass; the plan-challenge memo
  (C1–C5). All under `MAP_System/artifacts/experiments/` and
  `.../reviews/`.
- **Intake rule:** a new experiment/audit result becomes a candidate line
  in `shared/improvement-backlog.md` (or, if it has an observable
  acceptance check and touches a currently-felt pain, a task). It does
  **not** silently grow the immediate slate. The next revision of this
  plan explicitly weighs each candidate's *measured* evidence against the
  north-star before promoting it.
- **Guardrail:** no permanent autonomous process may convert evidence
  into tasks. A core agent owns each promotion decision (mirrors the
  Discovery Agent proposal-only rule).
- **Open seams parked as backlog, not tasks** (from the lifecycle audit,
  awaiting operator/measured justification): F4 per-task handoff
  discoverability (task schema has no `resume_from` field), F2 small-project
  bootstrap threshold, F3 intake-packet durability. These are real but need
  a decision or a repeat incident before they earn a task.
- **F5 resolved 2026-07-28** (review/release-tier disagreement between the
  2026-07-17 review guide and `CHANGE_CONTROL_SYSTEM.md`/`release_task.py`):
  the repeat incident arrived — zero releases for 5 days and a 90-task
  APPROVED backlog. TASK-288 reconciled the three sources into one rule
  (`classify_release()` in `scripts/release_task.py`); DEC-032 is the
  command-center approval that authorized a core agent to execute it. See
  `CHANGE_CONTROL_SYSTEM.md`'s Release tier section for the reconciled
  rule.

## Immediate task slate

Honest to the risk-lane model, not six ceremonial tasks:

1. **Coordination-surface task** = 1a (1b folded in). Medium risk, one
   review at completion, three deterministic fixtures + staged screenshot.
   Output paths per the readiness audit. Owner: whichever core agent takes
   CommandCenterUI work.
2. **Durable-conventions batch** = 2a + 4a + 5a. Low risk,
   documentation-only, one batched light review. Owner: claude-lab-gome
   unless reassigned. **Excludes 3a** — the authority decision is split
   out.
3. **Helper-authority decision** = 3a-i. Not a low-risk doc task: an
   AUTHORITY-class decision requiring command-center approval before
   3a-ii's documentation follow-on can proceed.

Backlog entries for `shared/improvement-backlog.md`: 2b, 3b, 6a, and the
parked lifecycle seams F2/F3/F4/F5 — each with its trigger as written.

## Answers to the kickoff's open questions

- **Task now vs backlog note:** task when the action has an observable
  acceptance check *and* touches a currently-felt pain; backlog when it
  needs a trigger (incident, dependency, operator input, or a decision)
  to be worth its review cost.
- **Which helper roles need UI cards now:** live core agents and
  currently-running helpers only (1a), joined to an active helper note;
  ambiguous identities show as warnings, not guessed cards.
- **Which reminders become operator-facing events:** any
  state-changing/message-sending recurring process (5a); pure read-only
  dashboards/polling do not.
- **decisions.md vs notes/:** if it changes what an agent *may* do
  (authority, boundary, gate) → `shared/decisions.md` with a
  DECISION_CLASSES class; if it explains *how* to do something within
  existing authority → `notes/`. The helper no-mutation rule (3a-i) is
  the one item here that is decisions.md **and AUTHORITY-class**.

## Fitness checks (govern, don't narrate)

Existing validators cover tasks/graph/mirrors/events/decisions/risk
registers. This plan adds at most two, both deferred until observed
drift justifies them: 3b (helper-note coverage) and a possible index-line
presence check (2a follow-on). No other new gates — six shipped
validators plus risk-tiered review is the right amount of governance for
the system's current size. The north-star measure, not a validator, is
how each shipped change is judged: if it does not move its named
lifecycle measure, record the negative and revert.
