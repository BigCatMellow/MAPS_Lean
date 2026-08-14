# Research Summary

Summary ID: SUMMARY-EXTERNAL-BLUEPRINT-GAP-REVIEW-2026-07-21
Related brief: none — operator-directed review of two externally authored documents
Related claim matrix: none — every MAP-side claim below is verified against a named file or query
Related assumption register: none — scale and fit limits are retained inline
Owner: claude-lab-niko
Date: 2026-07-21
Status: COMPLETE

## Question

What, if anything, should MAP adopt from two externally authored multi-agent
management blueprints:
`/home/mellow/Projects/MultiAgentProject/deep-research-report.md` (43 KB) and
`/home/mellow/Projects/MultiAgentProject/Ideal_Multi-Manager_System.md` (69 KB)?

## Answer

Roughly 70% of both documents is already implemented in MAP, which is
meaningful independent corroboration of the existing design rather than a
finding. The residual value is concentrated in four mechanisms MAP genuinely
lacks: coverage scheduling for durable records, incidents as a first-class
record type, a reliability budget, and risk level on the task row.

The documents' organizational content — a six-office org chart, Governing
Command, a permanent Incident Commander pool — should be rejected. It is
calibrated for "10s of managers, 100s of agents"; MAP runs about two core
agents plus bounded helpers. Adopting it would create roles with no occupants.

## Confidence

- [x] MEDIUM — every MAP-side claim is verified against the current schema,
      file tree, or tool output, but the judgment about which gaps matter most
      is an engineering opinion that has not been independently reviewed.

## Confidence decays after

Re-verify after the TASK-256..262 retrieval chain is reviewed and released,
since its measured results are the main input to whether a graph/embedding
layer is ever warranted. Also re-verify if MAP's active agent count grows
enough to make the documents' scale assumptions relevant.

## Open questions

- Does the coverage ledger shipped with this review actually change E/I
  behavior, or does it become another signal nobody reads?
- Should incidents be a new table or a `task_type` discriminator on the
  existing `tasks` table? The cheaper option may be good enough.
- Is the write-path divergence (every agent writes `map.db` directly, versus
  both blueprints' single control-plane authority) worth a decision record now
  or only once a corruption is actually observed?

## Downstream effect

- [x] One mechanism implemented: `map_emergence.py coverage` plus seven tests in
      `MAP_System/tests/test_map_emergence.py`. Independently reviewed by
      claude-lab-soba: CHANGES_REQUESTED
      (`artifacts/reviews/coverage-ledger-review-soba.md`), one REQUIRED finding
      — the shared closed-status set is not kind-aware, so an experiment reaching
      `APPROVED` would have dropped out of coverage permanently, and
      `COMPLETE`/`REVIEWED` experiments would have surfaced as false debt. Fixed
      via `coverage_closed_statuses()` plus a regression test; open records fell
      39 → 35 with overdue unchanged at 9. Still needs an operator task record
      and soba's re-review before it counts as accepted.
- [x] Otherwise informational. The remaining recommendations are proposals, not
      adopted rules.

## Evidence sources

1. `/home/mellow/Projects/MultiAgentProject/deep-research-report.md` — reviewed in full. **Citation integrity caveat:** contains unresolved `citeturn...` markers throughout instead of real citations, so its external factual claims cannot be verified in that form. Under MAP's own review standard these are unsupported claims.
2. `/home/mellow/Projects/MultiAgentProject/Ideal_Multi-Manager_System.md` — reviewed in full. Citations resolve (FEMA, NASA IV&V, Google SRE, Toyota, DARPA, NIST, GraphRAG, RAPTOR, Anthropic contextual retrieval). Prefer this document where the two overlap.
3. `MAP_System/map.db` schema — 17 tables; `tasks` columns enumerated below.
4. `MAP_System/emergence/INDEX.md` — 36 insights, 25 ideas; status distribution below.
5. `MAP_System/scripts/map_emergence.py coverage` output, 2026-07-21.
6. `MAP_System/graph/runner.py` output, 2026-07-21.

## Retrieval capsule

- Purpose: Records what MAP can and cannot learn from two externally authored
  multi-agent management blueprints, checked against MAP's actual schema and files.
- Proves: Most of both blueprints is already implemented in MAP; the residual
  value is concentrated in coverage scheduling, first-class incidents,
  reliability budgets, and risk on the task row.
- Applies to: MAP system design decisions and the system-improvement backlog.
- Does not provide: Approved decisions, task records, or authority to implement
  the remaining recommendations.
- Evidence type: analysis
- Status: current

## Already implemented — do not rebuild

| Blueprint recommendation | Where MAP already has it |
|---|---|
| Unified command, one operational owner per task | `AGENTS.md` Core Protocol #3; `db/claims.py` atomic claim + lease |
| Independent review, no self-review | `db/claims.py:claim_review`; `tests/test_no_self_review.py`; `notes/review-guide.md` |
| Stop-the-line authority | `scripts/halt_state.py`; `halt_state` block in `graph/runner.py` output |
| Risk-based approval gates | `RISK_SYSTEM.md`; `DECISION_CLASSES.md`; `scripts/pre_dispatch_policy.py`; `approval_gates` table |
| Append-only event log | `events/events.jsonl` + `events` table |
| Git = history, SQLite = coordination, Markdown = meaning | MAP's stated design (DEC-009); identical split |
| Task capsules / retrieval capsules | `notes/retrieval-capsule-guide.md`; `AGENTS.md` itself carries a capsule header |
| Layered retrieval (exact → FTS → capsule → semantic) | **in flight now**: TASK-256 through TASK-262, all SUBMITTED |
| R&D separated from production, transition gates | `RESEARCH_SYSTEM.md`; `emergence/experiments/`; `IDEA_PROMOTION_RULES.md` |
| Lessons learned lifecycle | `RETROSPECTIVE_SYSTEM.md`; `notes/operational-learning-guide.md` |
| Span of control | `helper_capacity` max 4 in `graph/runner.py` |
| Structured assignment/result packets | `notes/task-authoring-guide.md`; hcom intent protocol |

The retrieval chain in TASK-256..262 is independently arriving at the same
layered-retrieval conclusion the second document reaches in §8-§10. That
backlog should be reviewed and released before any new retrieval design opens.

## Genuine gaps, ranked

### 1. Coverage scheduling — IMPLEMENTED by this review

Searched `MAP_System/` for `coverage debt`, `coverage_debt`, `coverage ledger`,
`coverage scheduler` before implementing: **zero hits.**

MAP already exhibited the symptom the second document predicts (§14). The
emergence system captures well and sweeps poorly:

| Insight status | Count |
|---|---:|
| PROMOTED | 12 |
| RAW | 10 |
| OPEN | 6 |
| CLARIFIED | 3 |
| DISMISSED | 2 |
| PARKED | 1 |
| LINKED | 1 |
| CAPTURED | 1 |
| **total** | **36** |

*(Corrected 2026-07-21 after review by claude-lab-soba. The first version of this
table reported 15/10/6/3/2/1/1 = 38 and omitted `OPEN` entirely. It was produced
by grepping `INDEX.md` for a hard-coded status list, which both missed a status
the list did not anticipate and counted rows across all artifact kinds while
labelling them "insights". The corrected figures are counted from the 36 files
in `emergence/insights/`. The error is the same class this review criticises the
deep-research report for — a claim asserted without a reproducible check — and is
recorded rather than quietly patched.)*

The existing `map_emergence.py stale` command does not catch this. `stale` only
flags a record whose *related task* has closed while the record stayed open — it
found 2 findings. A record with `Related task: NONE` that nobody has revisited
is invisible to it.

`map_emergence.py coverage` reports (after the kind-aware closed-status fix from soba's review):

```
Emergence coverage debt: 9 of 35 open records unreviewed for >= 14 days.
- INS-0008 [CAPTURED] 19d, never reviewed
- INS-0009 [LINKED] 19d, never reviewed
- SYN-0001 [CLARIFIED] 19d, never reviewed
- IDEA-0009 [CANDIDATE] 19d, never reviewed
- IDEA-0013 [APPROVED_FOR_EXPERIMENT] 19d, never reviewed
- INS-0017..0020 [RAW] 15-17d, never reviewed
```

IDEA-0013 is the sharpest single result: it is `APPROVED_FOR_EXPERIMENT` — a
record that cleared promotion review — and it has sat unexecuted for 19 days
with nothing in the system pointing at it.

Deliberately kept minimal, in line with this review's own objection to
over-design: one interval knob (`--interval-days`, default 14), no pairwise
community matrix, no multi-factor score. Debt is plain age since last review,
falling back to the record's own `Date` when never reviewed. Closed statuses are
excluded, matching `stale`'s existing convention. State lives in
`emergence/coverage.json` — a file, consistent with the emergence system being
file-based, and reviewable in Git.

### 2. Incidents are not a durable record type

MAP has the vocabulary (`notes/agent-incident-taxonomy.md`,
`SELF_REPAIR_SYSTEM.md`, `scripts/resilience_controls.py`) and the runtime
behavior (limit_watcher opens and closes RnS incidents), but no `incidents`
table. Every RnS incident is written as a PROGRESS or BLOCKED event pinned to
`task_id: TASK-083`, with the incident's identity embedded in a summary string:

```
{"type": "BLOCKED", "task_id": "TASK-083", "sender": "limit_watcher",
 "summary": "RnS: codex-lab-kiri presumed down without a status record ..."}
```

Consequences: incident count, mean time to resolve, and repeat rate cannot be
queried. Both documents treat incidents as a separate state machine from tasks
for exactly this reason, and that judgment holds here — MAP is currently
overloading one task row as an incident bucket. This is also the prerequisite
for gap 3.

### 3. No reliability or error budget

Searched for `error budget`, `error_budget`, `SLO`: no hits in MAP source or
docs (only an unrelated research summary and one review).

MAP already emits the signals — review rejection rate, blocked age, rework,
repeat incidents — but has no policy stating what happens when they degrade.
The current session is a live example: 12 tasks are SUBMITTED without review,
and TASK-250 carries an APPROVED review artifact
(`artifacts/reviews/task250-review-lure.md`) that was never recorded in
`map.db`, so the runner keeps re-routing it. A review-latency budget would have
fired on this.

Recommended first budget, deliberately narrow:

```yaml
reliability_budget:
  review_latency_p50: 8h        # submitted -> disposition
  submitted_backlog_max: 5
  on_exhaustion: pause new task creation; divert core agents to review
```

### 4. Four of six core-agent approval gates are unreachable (UPGRADED — was "risk level is not on the task row")

This started as a schema-tidiness observation and turned into the most serious
finding in this review. It should be read before the coverage work.

`tasks` columns: `task_id, project_id, title, description, task_type, role,
status, priority, required_agent, owner, claimed_by, lease_expires_at,
heartbeat_at, attempt, max_attempts, created_at, updated_at`.

`pre_dispatch_policy.py` defines six `REQUIRE_*` approval gates for tier-1 core
agents. Four of them are keyed on task fields that **do not exist in that
schema and have no text fallback** (`pre_dispatch_policy.py:308-311`):

| Gate | Keyed on | Fallback | Reachable? |
|---|---|---|---|
| `REQUIRE_OPERATOR_APPROVAL` | `requires_operator_approval` field | none | **no** |
| `REQUIRE_COMMAND_CENTER_DECISION` | `decision_class` field | none | **no** |
| `REQUIRE_OPERATOR_TIER_APPROVAL` | `task_tier` field | none | **no** |
| `REQUIRE_SECURITY_STRUCTURAL_APPROVAL` | `risk_class` / `risk_severity` fields | none | **no** |
| `REQUIRE_CORE_DESTRUCTIVE_APPROVAL` | `is_destructive()` | task text | yes |
| `REQUIRE_UNKNOWN_TRUST_BOUNDARY_APPROVAL` | `crosses_trust_boundary()` | task text | yes |

Verified by loading every task the runner actually feeds the policy engine:

```
risk_class:                  truthy on 0/253 tasks
risk_severity:               truthy on 0/253 tasks
trust_boundary:              truthy on 0/253 tasks
trust_boundary_crossing:     truthy on 0/253 tasks
requires_operator_approval:  truthy on 0/253 tasks
```

And by evaluating all 253 through the real policy engine at tier 1:

```
decisions: {'allow': 253}
reasons ever fired: {'ALLOW_WITHIN_TIER': 253}
```

**No approval gate has ever fired for a core agent on any task in this
database.** The two reachable gates do work — a synthetic task whose
description contains "git reset --hard / force push" correctly returns
`require_approval` with `REQUIRE_CORE_DESTRUCTIVE_APPROVAL` — so the engine is
not broken. It is starved. It reads five decision inputs that the canonical
store never supplies.

The sharp part: `DECISION_CLASSES.md` and `RISK_SYSTEM.md` are fully written
systems defining exactly the `decision_class`, `risk_class`, and `risk_severity`
values these gates test for. Those values live in prose and in task JSON
(1 of 253 files carries `risk_class`) and never reach the enforcement point.
MAP's safety story reads as six gates; the operating reality is two text
heuristics.

This is the failure mode both blueprints warn about in different words — the
deep-research report's "dashboards that track activity rather than outcomes",
and Toyota's point that detecting an abnormality is worthless if nothing stops
the line. A control that cannot fire is worse than a missing control, because
it is counted as present.

#### The engine's design is right; only its input is missing

`pre_dispatch_policy.py` was built with a correct dual interface — a task may
either *declare* a property or have it *inferred* from text. Setting the
declared field explicitly is honoured in every case tested:

```
destructive_action      HONOURED      broad_rewrite            HONOURED
final_review            HONOURED      canonical_map_mutation   HONOURED
final_decision          HONOURED      shell_required           HONOURED
broad_architecture      HONOURED      trust_boundary_crossing  HONOURED
```

The canonical store simply supplies none of them, so only the text half ever
runs. Five further fields (`decision_class`, `risk_class`, `risk_severity`,
`task_tier`, `requires_operator_approval`) have no inference path at all.

#### Concrete failure scenario

Safety therefore depends on a task author happening to use trigger vocabulary.
A genuinely destructive task worded neutrally passes clean:

```
title:       Clean up the deployment mirror
description: Remove the stale exports directory and regenerate it from source.
-> decision: allow   reasons: ['ALLOW_WITHIN_TIER']
```

The same work described as "git reset --hard" correctly gates. Identical
action, opposite safety outcome, decided by phrasing.

Minimum fix: add `risk_class`, `risk_severity`, `decision_class`, `task_tier`,
and `requires_operator_approval` to `tasks`, populate them at task creation, and
add a regression test asserting that a task carrying `risk_class: SECURITY`
returns `require_approval`. The schema change is the small part; the test is the
part that keeps it from silently dying again. Note the eight predicate-backed
fields deserve the same treatment for the same reason, but they degrade to a
working heuristic rather than to nothing, so they are second priority.

Separately, there is still no WAITING state carrying `waiting_for`, `since`,
`next_check`, `escalate_after`, and `fallback_action`. TASK-186 — IN_PROGRESS
with no claimant, lease, or heartbeat since before 2026-07-18 — is exactly the
orphan that structured waiting plus an escalation deadline prevents. It was
eventually caught by the advisory monitor, but only after the fact.

### 5. Write-path centralization (note, not action)

Both documents insist all writes funnel through one control-plane authority
because SQLite permits one writer. MAP lets every agent write `map.db` directly
via `db/claims.py`. No corruption has been recorded, so this is not urgent — but
it is a real divergence from both blueprints and deserves a decision record
rather than silent drift.

## Where the documents should be pushed back on

1. **Scale mismatch.** The deep-research report explicitly assumes "10s of
   managers, 100s of agents" and estimates 34-52 weeks with 3-5 platform
   engineers. MAP runs roughly two core agents plus bounded helpers. Its org
   chart — Governing Command, Project DRI, Independent Assurance Office,
   Incident Commander Pool, six permanent offices — would create roles with no
   occupants. MAP already has 19 top-level `*_SYSTEM.md` documents and fewer
   agents than systems; INS-0023 raised this concern and it remains open.

2. **Table proliferation.** MAP has 17 tables. The second document proposes ~18
   more (`knowledge_nodes`, `knowledge_edges`, `communities`,
   `community_summaries`, `embeddings`, `chunks`, `entities`, ...). Building a
   graph and embedding layer before the FTS5 retrieval experiments in
   TASK-256..262 have even been reviewed is over-design before validation, which
   `AGENTS.md` explicitly warns against.

3. **The Idea Score formula (§13) is pseudo-precision.** Multiplying seven
   0.1-1.0 factors and dividing by three produces a number with no calibration
   and no error bars. MAP's existing status ladder
   (RAW → CAPTURED → LINKED → CLARIFIED → PROMOTED) is less impressive and more
   honest. Do not adopt the formula.

4. **Citation integrity.** `deep-research-report.md` contains unresolved
   `citeturn...` markers instead of real citations. Its factual claims cannot
   be verified in that form. The second document's citations do resolve and
   should be preferred where the two overlap.

## On the organizational hierarchy specifically

The hierarchy diagram (Ideal §2, deep-research "Organizational structure") is
the least useful part of either document *as drawn*, and the most useful part
once reduced to its one load-bearing sentence:

> "These should be understood as roles, not necessarily as permanently running
> models. One model may fill several roles at different times, provided
> conflicting roles are never combined on the same task."

MAP agents are ephemeral sessions, not staffed positions. Boxes on a chart
cannot be filled. But the *role-conflict* rule is real, and MAP enforces a good
deal of it mechanically already — more than a first reading suggests:

- `db/claims.py:claim_block_reason` returns `self_review` when the claimant
  owns the task under review (`tests/test_no_self_review.py`).
- `scripts/pre_dispatch_policy.py` carries 12 `REJECT_*` codes covering helper
  and local-model role boundaries: `REJECT_HELPER_FINAL_REVIEW`,
  `REJECT_HELPER_FINAL_DECISION`, `REJECT_HELPER_BROAD_ARCHITECTURE`,
  `REJECT_HELPER_BROAD_REWRITE`, `REJECT_HELPER_DESTRUCTIVE`,
  `REJECT_HELPER_SHELL_NETWORK`, `REJECT_HELPER_CANONICAL_MUTATION`,
  `REJECT_HELPER_AUTHORITY_POLICY_FINALIZATION`, `REJECT_LOCAL_SHELL_NETWORK`,
  `REJECT_LOCAL_CANONICAL_MUTATION`, `REJECT_LOCAL_NON_DRAFT_TIER`,
  `REJECT_AIDER_BROAD_SCOPE`.
- `AGENT_PERMISSION_LEVELS.md` already documents tier → read/write/execute
  /network/destructive permissions.

So a new role-conflict *policy* would duplicate existing work and should not be
written. The real gap is narrower and is a traceability one: no single place
maps a stated rule to the mechanism that enforces it, the reason code it emits,
and the test that pins it. An agent that hits `REJECT_HELPER_BROAD_REWRITE` —
as TASK-263 does right now — cannot look up what that means without reading
source. That, plus finding 4 above, is the concrete cost: nobody can currently
answer "which of our stated controls actually fire?" without instrumenting the
policy engine by hand, which is how finding 4 went unnoticed.

Recommended: extend `AGENT_PERMISSION_LEVELS.md` with a rule → enforcement
point → reason code → test column. Do not create a new policy document, and do
not import the org chart.

## Recommended next actions

Ordered, smallest first. Items 2-6 are proposals needing operator disposition
and task records.

| Order | Action | Status |
|---|---|---|
| 1 | Drain the review backlog (12 SUBMITTED); record lure's TASK-250 approval | blocked on operator: agent cannot write `map.db` |
| 2 | Add a role-conflict table; mark each row enforced vs prose-only | proposed |
| 3 | Add `incidents` + `incident_actions`; stop overloading TASK-083 | proposed |
| 4 | Define one narrow reliability budget (review latency) | proposed |
| 5 | Add `risk_level` to `tasks`; add structured WAITING | proposed |
| 6 | Open a decision record on write-path centralization | proposed |
| — | Coverage ledger for the emergence system | **implemented, needs review** |

Explicitly deferred: knowledge graph, embeddings, community summaries, the
six-office org chart, and the idea-scoring formula.

## Single strongest learning

Both documents converge independently on one claim: the index is the project's
thinking memory, not its search box, and **coverage is the hard part, not
retrieval**. MAP's in-flight work (TASK-256..262) is building the retrieval half
well. Without the coverage half, MAP ends up with excellent retrieval and still
fails to notice its own unprocessed records — which, before this change, was
already happening to nine of them, including one approved-for-experiment idea.
