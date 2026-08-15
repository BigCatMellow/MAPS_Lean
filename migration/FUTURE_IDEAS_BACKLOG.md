# MAPS Lean Future Ideas Backlog

Status: `PRESERVED IDEA BACKLOG — NOT ACTIVE AUTHORITY`

Purpose: preserve promising system ideas discovered while reviewing the legacy
MAPS implementation and the current Lean runtime, without treating their mere
existence as a reason to build them.

This is a **future-options document**, not a roadmap and not an execution
instruction. Active behavior continues to be defined by `AGENTS.md`, the active
playbooks, runtime code, task state, and approved project decisions.

Related sources:

- [Legacy Knowledge & Implementation Audit](LEGACY_KNOWLEDGE_AUDIT.md)
- [Legacy Promotion Ledger](LEGACY_PROMOTION_LEDGER.md)
- [Legacy Idea Recovery Audit](LEGACY_IDEA_RECOVERY_AUDIT.md)
- [Active Runtime](../runtime/README.md)
- [Execution Integrity](../playbook/EXECUTION_INTEGRITY.md)
- [Repair and Learning](../playbook/REPAIR_AND_LEARNING.md)
- [Helpers and Communication](../playbook/HELPERS_AND_COMMUNICATION.md)
- [Information Lifecycle](../playbook/INFORMATION_LIFECYCLE.md)

---

## Preservation rule

The legacy audit already established the governing rule:

> Preserve invariants, evidence, tests, and useful implementation techniques.
> Do not preserve a subsystem merely because it existed.

Apply the same rule here.

Before promoting any item in this document, answer:

```text
What real problem are we solving?
        ↓
Does Lean already solve it?
        ↓
What evidence says the problem is material?
        ↓
What is the smallest behavior that solves it?
        ↓
Can success and failure be measured?
        ↓
Can it remain provider-neutral and authority-safe?
        ↓
Can it be added without creating another source of truth?
```

If those questions cannot be answered, keep the idea here rather than turning
it into runtime machinery.

---

# Current Lean baseline

These ideas should be judged against what MAPS Lean already has. Do not build a
second version of an existing control.

The active runtime already provides:

- SQLite canonical task truth;
- structural AGI readiness gates;
- atomic claims and leases;
- submission and review evidence;
- policy metadata and operator approvals;
- worker capability envelopes;
- durable halt state;
- deterministic route selection through LangGraph;
- separate LangGraph checkpoint state;
- project-isolated hcom transport;
- RnS recovery with bounded retry/backoff;
- bounded helper lanes;
- immutable run manifests;
- execution-time context/scope binding;
- staleness checks;
- writable/forbidden Git scope proof;
- run budgets;
- continuity-aware review support;
- criterion-level evidence where justified.

Future work should therefore focus primarily on **observability, outcome
measurement, context efficiency, parallel-work isolation, deterministic routine
flows, and controlled learning** rather than rebuilding basic orchestration.

---

# Candidate summary

| Priority | Candidate | Main value | Default disposition |
|---|---|---|---|
| P1 | Telemetry/event secret-safety boundary | Prevent observability from persisting sensitive material | Audit Lean before expanding telemetry |
| P1 | Session replay / trace reconstruction | Explain exactly what happened | Preserve and simplify |
| P1 | Outcome feedback and eval corpus | Distinguish passing MAPS from real success | Preserve and measure |
| P1 | Context builder | Supply the smallest trustworthy context packet | Preserve principle; build narrowly |
| P1 | Operational-learning promotion loop | Carry proven temporary lessons into future startup/context safely | Preserve as controlled learning |
| P1 | Negative operating contract | Prevent agents from recreating complexity, verbosity, guessing, and scope drift | Short default prohibitions; promote into instructions only after review |
| P1 | Git worktree isolation | Prevent parallel agents colliding in one worktree | Lean synthesis; prototype when concurrency warrants |
| P1 | Deterministic `maps flow` procedures | Remove routine bureaucracy from LLM reasoning | Add only for repeated stable procedures |
| P2 | Small Mission Control / `maps status` | Give the operator one truthful attention surface | Read-only and minimal |
| P2 | Helper dispatch no-progress signal | Distinguish slow work from stuck/silent work | Advisory experiment only |
| P2 | Persistent helper continuity | Resume useful specialist context without durable authority | Defer until repeated need |
| P2 | Controlled harness evaluation/refinement | Improve routing/instructions from measured history | Proposal-only; never self-authorizing |
| P2 | Cost/yield and escaped-defect metrics | Optimize for useful outcomes, not activity | Add when enough runs exist to measure |
| P2 | Risk-specific review lenses | Make reviewers explicitly inspect applicable failure classes | Lightweight review refinement |
| P2 | Bounded phase-boundary discovery | Find useful cross-cutting omissions without a permanent scout | Proposal-only, evidence-linked, occasional |
| P2 | Bounded system-adherence audit | Detect mechanisms that exist but are not actually used | Periodic audit, not permanent process police |
| P2 | Authority provenance / ratification guard | Prevent proposals becoming policy by citation | Preserve as decision-integrity invariant |
| P2 | Review-time evidence freshness | Prevent stale submission evidence from being approved | Re-derive or revision-bind important evidence |
| P2 | Explainable wait projection | Make stranded requests visible from existing communication metadata | Derived/read-only first |
| P3 | Scoped temporary halt authority | Allow narrowly bounded safety intervention without permanent authority | Preserve only; high bar to promote |

---

# Recovered historical candidates — 2026-08-15 audit

This section records ideas recovered during a deeper pass through legacy task,
Emergence, experiment, and follow-up records after the first Lean backlog had
already been created.

The point of this section is not to revive every old task. It distinguishes:

- genuinely missing candidates;
- useful refinements of candidates already in this backlog;
- old problems that Lean already solves and therefore should **not** be rebuilt.

## A. Telemetry/event secret-safety boundary

Legacy chain: `TASK-191` -> `TASK-200` -> `IDEA-0016`.

The old redaction work deliberately left `events.jsonl` appenders outside its
initial guard and recorded a follow-up to cover them later. `IDEA-0016` remained
parked rather than rejected.

The Lean translation should not restore the old file-specific mechanism. The
preserved invariant is broader:

> Any MAPS surface that durably stores task summaries, messages, traces,
> recovery notes, diagnostic records, outcomes, or replay material should have a
> defined secret-safety/redaction boundary.

Why this matters now: replay, outcome recording, trace sampling, and richer
operator status all increase observability. Expanding telemetry before defining
how sensitive material is handled could multiply leakage surfaces.

Smallest useful action:

1. enumerate every durable event/trace/log write path in Lean;
2. classify what user/agent content can enter each one;
3. test representative secret-like values;
4. decide whether protection belongs at one shared write boundary or at typed
   callers;
5. only then add new telemetry surfaces.

Hard boundary: redaction must not silently corrupt evidence needed for audit.
If a field must be removed, preserve enough metadata to say that content was
redacted rather than pretending it never existed.

Default disposition: **P1 audit candidate; do not blindly port legacy code.**

## B. Three-layer evaluation discipline and incident taxonomy

Legacy source: `IDEA-0018`.

This refines the existing outcome/eval and controlled-harness candidates.
Instead of one vague eval system, preserve three distinct layers:

```text
Layer 1 — mechanical regression
Did the discrete gate/router/recovery/control behave correctly?

Layer 2 — agent-quality regression
Was the implementation, review, context packet, or recommendation actually good?

Layer 3 — production trace/outcome sampling
What failures occur in real MAPS use that our fixtures do not model?
```

Maintain a small incident taxonomy so repeated failures become measurable rather
than anecdotal. Initial classes can remain intentionally coarse, for example:

- tool-call/integration failure;
- context omission or truncation;
- runaway/retry loop;
- routing error;
- helper failure;
- recovery failure;
- review miss;
- validator false positive / false negative;
- operator intervention caused by system friction.

Production incidents should feed new frozen regression cases rather than merely
producing dashboards.

Default disposition: **fold into Outcome Feedback / Eval Corpus and Controlled
Harness Evaluation.**

## C. Operational-learning promotion loop

Legacy source: `IDEA-0022`.

The historical failure was simple: MAP could discover and record a useful
operational lesson without guaranteeing that a future agent would ever load it.

Preserve the controlled mechanism, not an unlimited memory system:

```text
operational observation
        ↓
candidate lesson
        ↓
review / promotion
        ↓
active startup or task guidance
        ↓
expiry / supersession / retirement
```

This is distinct from the Context Builder and historical evals:

- Context Builder asks: **what information does this task need?**
- Operational Learning asks: **what currently applicable lesson did MAPS learn
  from recent operation?**
- Harness Evaluation asks: **which system configuration performs better over
  historical cases?**

Candidate record fields:

```text
lesson_id
claim
source incident/task/run
promoted_by
applicability / trigger
starts_at
expires_at or review_at
supersedes
status: candidate | active | expired | retired
```

Hard boundaries:

- lessons do not become authority merely because an agent observed them;
- temporary workarounds must be able to expire;
- superseded guidance must stop appearing in startup/context projection;
- the registry must not become a second policy system.

Default disposition: **P1 preserved candidate.**

## D. Exact claim/evidence projection for the Context Builder

Legacy source: `IDEA-0023` / `EXP-0006`.

Whole-file retrieval can find the right document while still failing to identify
the exact statement, section, code symbol, historical version, or negative
boundary that answers the task.

A later Context Builder experiment should therefore be able to produce
disposable evidence cards such as:

```text
CLAIM
Independent review cannot be performed by the submission author's continuity
lineage.

SOURCE
runtime/state/review.py
ReviewMixin.claim_review()

PROOF ROLE
active mechanical guard

SOURCE HASH
<hash>
```

Negative boundaries should be represented separately:

```text
BOUNDARY
This source establishes current review eligibility but does not establish the
historical state before the Lean migration.
```

Useful properties to preserve from the old proposal:

- exact Markdown section or code-symbol anchors;
- source hashes/watermarks;
- explicit proof role;
- positive evidence and negative boundaries stored/scored separately;
- disposable, rebuildable projections;
- independently frozen evaluation questions before treatment.

**Important experiment correction:** the completed legacy `EXP-0006` did **not**
validate its lexical claim-card retriever as a production direction. It scored
17/41 exact-source accuracy, 7/41 anchored-evidence accuracy, and correctly
abstained on only 2/5 negatives. Its decision was `REVISE`. What survived the
experiment was the evidence-integrity discipline: exact anchors, source hashes,
source-drift reporting, temporal attribution, explicit negatives, frozen
holdouts, and separate blind scoring. Do not port the old lexical retrieval
implementation merely because the evidence-card shape is useful.

Do **not** begin with a full knowledge graph or treat embeddings as automatically
required. However, later tests must include vocabulary-shift/paraphrase cases;
legacy evidence showed purely lexical retrieval can look solved on matched
wording and fail badly once the same meaning is expressed differently.

Default disposition: **fold evidence-integrity techniques into P1 Context
Builder; legacy retriever itself is not preserved.**

## E. Helper/dispatch no-progress signal

Legacy source: `IDEA-0030`, backed by repeated silent helper/local-model stalls.

RnS handles stopped sessions and retry/recovery. A different failure mode is a
session that remains nominally alive but produces no observable progress.

The first Lean experiment should remain advisory:

```text
dispatch helper
      ↓
no new status/event
AND
no output/terminal change
for a bounded interval
      ↓
NO-PROGRESS advisory
```

Do not use a single naive wall-clock timeout because local model latency varies
substantially. A signal should be based on absence of progress evidence, and it
should start on one bounded dispatch surface before becoming general behavior.

Possible integration point later:

```text
maps status

HELPERS
qwen-7b       TASK-042     working       38s
aider-2       TASK-046     NO PROGRESS   11m
```

Hard boundaries:

- advisory first;
- no auto-kill in the initial experiment;
- no new standing watcher-agent role;
- false positives must be visible and measurable.

Default disposition: **P2 experiment candidate.**

## F. Replay must include communication coverage and completeness

Historical task archaeology showed that replay designs can become misleading if
they reconstruct task/database events while omitting hcom or other communication
facts.

Therefore the Session Replay candidate should explicitly answer:

- which communication source(s) were queried;
- whether communication records are complete for the requested period;
- what messages/dispatches/acks are attributable to the task/run;
- what evidence is unavailable or ambiguous.

A replay that omits communication must say so. It must never render a clean,
complete-looking timeline from only the sources it happened to understand.

Default disposition: **fold into P1 Session Replay.**

## G. Outcome records need explicit actor/operator provenance

Historical operator-intervention work showed that generic messages are not a
safe proxy for human/operator intent.

When MAPS later records outcomes, intervention counts, overrides, or manual
corrections, the record should distinguish explicit identities/intent rather
than inferring them from arbitrary message text.

At minimum preserve:

```text
actor identity
actor class if known: operator | core agent | helper | system
recorded intent / action type
source record
confidence or UNKNOWN when attribution is incomplete
```

Do not infer "human intervention" merely because an event looks unusual.

Default disposition: **fold into P1 Outcome Feedback and metrics.**

## H. Risk-specific review lenses

Legacy source: `IDEA-0004`, created after an ordinary functional review missed
a real CSRF/write-endpoint issue that a security-framed second pass caught.

The durable lesson is not necessarily "always add another reviewer." It is:

> A reviewer checks more effectively when the required risk questions are
> explicit.

A lightweight Lean form could attach lenses to medium/high-risk review:

```text
REVIEW LENSES
[x] functional correctness
[x] acceptance criteria
[x] security / trust boundary
[ ] destructive / data-loss
[ ] privacy
[ ] deployment / release path
```

One independent reviewer may satisfy multiple lenses when appropriate. A second
reviewer should be required only when the risk itself justifies it.

Default disposition: **P2 review-quality refinement.**

## I. Scoped temporary halt authority

Historical source: `TASK-201` halt-authority-window work.

The useful concept is temporary, scoped safety authority rather than permanent
validator power: a validator/system component may be allowed to halt a narrow
class of execution for a defined window, while remaining telemetry-only by
default.

If Lean ever needs this, require:

- disabled by default;
- explicit scope;
- explicit grantor;
- start and expiry;
- durable reason/evidence;
- no authority expansion beyond the grant;
- operator-controlled clearing for consequential halts.

Lean already has durable halt state, so this is **not** a request for another
halt subsystem. It is only a possible future delegation rule around the
existing halt mechanism.

Default disposition: **P3 preserve only; promote only after a concrete safety
case demonstrates need.**

## J. Historical candidates confirmed as already solved in Lean

Do not re-add these as future work unless a new failure proves the current
implementation insufficient.

### Atomic review claiming

Legacy `IDEA-0017` was promoted and implemented after chat-based review claims
raced. Lean already uses mechanically claimed reviews.

Disposition: **SOLVED — no new candidate.**

### Durable submission authorship + no-self-review integrity

`IDEA-0026` found that legacy no-self-review checks keyed off stale
`tasks.owner`; its prerequisite `IDEA-0027` became `TASK-274` and durably
recorded submission authorship.

Lean goes further: review eligibility is checked against the durable submission
author and continuity lineage, so a continuation identity cannot evade the
independence rule.

Disposition: **SOLVED/IMPROVED IN LEAN — preserve as regression invariant.**

### RnS suppression of superseded/disposable sessions

Legacy `IDEA-0009` was adopted to stop recovery from repeatedly waking sessions
that were intentionally terminal or whose work was no longer valid.

Lean recovery already suppresses terminal sessions and stops recovery when the
task/claim no longer matches.

Disposition: **SOLVED IN LEAN — preserve as regression invariant.**

## K. Bounded phase-boundary discovery / retrospective pass

Legacy source: `INS-0028` / `EXP-0003`.

A permanent discovery agent is unnecessary and risks idea inflation, scope drift,
and background-model cost. But the bounded legacy pilot is important evidence
that **occasional, visible, non-forcing discovery can work**: the completed
ClearFront phase pilot produced two genuinely new useful findings, one useful
rejection, zero scope drift, zero implementation edits, and no optional idea was
misrepresented as a requirement.

Preserve the method, not the standing role:

```text
completed phase / major milestone
        ↓
freeze known findings / current decisions
        ↓
bounded evidence-linked discovery pass
        ↓
classify each finding:
known | refinement | genuinely new | weak | scope drift
        ↓
proposal only
        ↓
normal E/I promotion path if warranted
```

Useful controls from the experiment:

- visible/bounded execution;
- no implementation during discovery;
- no idea quota;
- explicit fact / inference / proposal separation;
- check existing records before claiming novelty;
- name the decision owner;
- preserve rejected ideas when the rejection itself is useful;
- no continuous model loop.

Default disposition: **P2 preserved practice candidate; phase-boundary/event-
triggered, never an always-on agent.**

## L. Bounded system-adherence audit

Legacy source: `IDEA-0012` / `PROMO-0007` / `TASK-129`.

The old system discovered a practical failure mode: a subsystem can be fully
documented and technically implemented while agents simply do not use it. The
historical response was not a permanent "process steward" identity. It was a
bounded audit checking whether systems were:

1. complete against their stated purpose;
2. actually connected to the other systems they claimed to integrate with;
3. demonstrably used in real work rather than merely present in docs.

Lean should preserve the audit shape without reviving the old eleven-system
bureaucracy. A future lightweight audit might ask of each consequential MAPS
mechanism:

```text
Does it still solve a real problem?
Is it mechanically reachable?
Is it actually being exercised?
Does active behavior match the playbook?
Is another mechanism duplicating it?
```

Findings should become normal repair notes, experiments, or candidate tasks;
the audit itself must not silently rewrite policy or runtime state.

Default disposition: **P2 occasional audit candidate, especially after major
system additions or migrations.**

## M. Authority provenance: citation must not ratify a proposal

Legacy source: `INS-0043` and the later promotion-order failures in `INS-0046`.

A legacy artifact explicitly labeled `proposed decision` became a de facto gate
because later authoritative records cited it as though it had already been
approved. Repetition of the citation made the proposal look increasingly
canonical even though no explicit ratification occurred.

Preserve this decision-integrity invariant:

> Referencing an artifact does not change its authority class.

Any document or record used to block, authorize, or constrain work should have
explicit provenance showing why it is allowed to do so. Candidate/proposed
records must remain proposals until the actual approval/decision transition is
recorded.

Possible Lean checks later:

- surface the authority class alongside decision references;
- warn when a task/policy gate cites a proposal or retired decision;
- prevent derived context from dropping `PROPOSED`, `SUPERSEDED`, or similar
  status markers;
- make promotion order visible: approval first, implementation scope second.

Do not build a giant document-authority graph merely to solve this. Start with
load-bearing gate/decision references only.

Default disposition: **P2 decision-integrity invariant; mechanical warning only
if real recurrence justifies it.**

## N. Review-time evidence freshness / immutable revision binding

Legacy source: `INS-0058`.

Submission-time checksums, parity screenshots, metrics, and other evidence can
be correct when captured and false by the time an independent reviewer acts.
The legacy system observed this on unrelated tasks when live files changed
inside the submission/review window.

Preserve the rule:

> Review the state being approved, not merely the state that once produced the
> submission report.

For important evidence, use one of two patterns:

1. **revision binding** — evidence identifies an immutable commit/tree/run
   revision and review verifies that exact revision; or
2. **review-time re-derivation** — reviewer reruns the relevant property against
   the current submitted state.

A stale evidence record remains useful historical evidence; it simply must not
silently masquerade as proof of the current bytes/state.

Default disposition: **P2 review-integrity refinement; especially important for
security, release, parity, and generated metrics.**

## O. Security and authority tests should assert executed behavior

Legacy source: `INS-0060`, reinforced by the security-framed reviews behind
`INS-0059`.

Tests for security, authority, defaults, or isolation properties should prefer
observable behavior over exact source spelling. Legacy tests repeatedly broke or
passed for the wrong reason because they matched implementation text rather than
the property the text was supposed to enforce.

Examples:

```text
BAD PROXY
"server.py contains DEFAULT_HOST = '127.0.0.1'"

BETTER PROPERTY
"with a clean environment, the computed bind address is loopback-only"
```

Use isolated imports, mocks, and narrow execution boundaries so behavior-level
security tests do not accidentally trigger side effects.

Default disposition: **preserve as a testing/review invariant, not a new
subsystem.**

## P. One fact, multiple readers: declare authority, make mutation atomic, or reconcile

Legacy source: `SYN-0001`.

Several apparently unrelated failures—task ID collisions, status drift, stale
agent mirrors, event-schema divergence, generator-owned files being mistaken for
task-owned files—shared one structure: **one conceptual fact had multiple
readers/copies and no clearly declared winner.**

The historical synthesis identified three successful repair shapes:

```text
1. Declare one view authoritative and make the others derived.
2. Make the read/write operation atomic so concurrent actors cannot interleave.
3. Add an automatic reconcile/cross-check where multiple representations are
   genuinely necessary.
```

Review question worth preserving:

> Who else reads this state, and which copy wins?

Do not apply this mechanically to state with only one reader. The point is to
prevent hidden duplicate truth, not to add locks and reconcilers everywhere.

Default disposition: **architecture/review invariant; use when introducing new
durable state or projections.**

## Q. Explainable waits from communication metadata

Legacy source: `INS-0036`.

The old system found that much of a "why are we waiting?" record could be
derived from hcom metadata already present: requester, addressee, request body,
message/thread ID, and timestamp. Agents only needed to add exceptional fields
such as `resumes_when`, `timeout_action`, or impact when safe defaults were not
enough.

A Lean-native form could remain a read-only projection:

```text
WAITING
review request 84
requester: agent-a
recipient: agent-b
sent: 10:14
age: 18m
thread: ...
resume condition: reply / recipient unavailable / explicit reroute
```

This can later improve `maps status`, replay, and recovery triage without
creating a second messaging authority.

Hard boundaries:

- derive from structured communication metadata where possible;
- do not infer recipients from prose if structured mentions exist;
- projection is diagnostic, not task-state authority;
- no automatic reassignment in the first version.

Default disposition: **P2 read-model candidate; promote only if stranded waits
remain an operator/coordinator cost.**

## R. Retrieval must be tested against vocabulary shift, not only corpus-matched wording

Legacy source: `INS-0035` plus the later `EXP-0006` result.

One legacy retrieval chain appeared to have 100% task recall on its frozen
questions, but merely paraphrasing those questions into non-corpus vocabulary
reduced task recall from 9/9 to 3/9 and source visibility from 81% to 31%.
This means a retrieval benchmark can accidentally measure "does the query reuse
words from the source?" instead of "can the system recover the right evidence
when the user expresses the same meaning differently?"

Any future Context Builder/retrieval experiment should therefore include:

- vocabulary-matched controls;
- meaning-preserving paraphrases;
- hard negatives / near-miss tasks;
- abstention quality;
- end-to-end acceptable-evidence rank, not just task/file recall;
- magnet-document tests where one broad source could dominate ranking;
- frozen questions/labels before treatment where practical.

This does **not** prove that embeddings are the answer. It proves that purely
lexical success is insufficient evidence for deferring all semantic fallback or
query-expansion work.

Default disposition: **fold into Context Builder evaluation requirements.**

## S. Release review should inspect every user-visible acquisition path

Legacy source: `INS-0005` / `PROMO-0005`.

Source-tree correctness is not enough if users install/download/run a stale ZIP,
generated bundle, copied asset tree, packaged binary, README command, or other
release path. Legacy release review caught defects that ordinary source review
could not see because the user-facing artifact diverged from the source that
had been reviewed.

Preserve this as a release-flow/review lens:

```text
source state
→ generated/package state
→ documented acquisition path
→ clean install/run smoke
```

A deterministic future `maps flow release` is a natural place for this once the
procedure repeats often enough. Do not create a second release system solely for
this checklist.

Default disposition: **fold into Risk-specific Review Lenses and deterministic
release flow.**

## T. Evidence emitted by scanners/retrievers must remain independently checkable

Legacy source: `INS-0061`.

The legacy emergence scanner produced correct-looking candidate counts while
some `evidence_refs` pointed at the wrong event lines. A curator trusting the
scanner's citations could investigate unrelated evidence and reach the wrong
conclusion.

Preserve the invariant:

> Retrieval/scanner output is a locator or claim about evidence, not evidence
> authority by itself.

For consequential use, evidence references should be reproducible from stable
identifiers/hashes/queries or directly re-openable and verifiable. A system that
cannot prove where a derived claim came from should report uncertainty rather
than provide a falsely precise anchor.

Default disposition: **fold into Context Builder, replay, and diagnostic-tool
evidence integrity.**

## U. Negative operating contract / anti-pattern instructions

Operator direction: 2026-08-15.

MAPS should not define only what an agent **should** do. It should also define a
small set of behaviors agents should **not** fall into by default. This is meant
to keep Lean lean: less ceremony, less guessing, less scope drift, less prose,
and fewer self-created systems.

Core rule:

> Do the smallest thing that correctly solves the actual problem. Do not invent
> complexity, facts, authority, requirements, or work.

Candidate negative instructions:

```text
DO NOT overcomplicate the task.
Use the smallest sufficient approach. Do not add architecture, roles, services,
state, abstractions, or process unless the problem actually requires them.

DO NOT over-explain.
Use brevity in the face of grammar for the sake of concision. Prefer short,
clear statements, fragments, tables, or checklists when full prose adds no
information. Never sacrifice correctness or a necessary warning merely to be
short.

DO NOT assume.
If a material fact, intent, requirement, authority boundary, or desired outcome
is unknown, do not invent it. Inspect available evidence first. If the unknown
still matters, ask for help/clarification rather than guessing.

DO NOT silently expand scope.
Solve the requested problem. Record adjacent ideas separately instead of turning
them into unrequested implementation work.

DO NOT confuse capability with permission.
Being able to perform an action does not mean the agent is authorized to decide
that it should happen.

DO NOT create duplicate truth.
Before adding state, a registry, an index, a status file, or a cache, identify
which existing source remains authoritative and why the new representation is
needed.

DO NOT create permanent machinery for a one-off problem.
Prefer a bounded helper, script, checklist, or experiment before introducing a
standing agent, daemon, watcher, workflow, or new subsystem.

DO NOT treat prose as proof.
Check the actual state, behavior, evidence, or authoritative record when the
answer can be verified mechanically.

DO NOT hide uncertainty.
If evidence is missing, contradictory, stale, or incomplete, say so. Unknown is
better than fabricated certainty.

DO NOT continue consequential work through an unresolved blocker.
When uncertainty could materially change a destructive, external, security,
authority, or scope decision, surface the blocker and ask for help.

DO NOT mistake activity for progress.
Stop when the requested result is complete. Do not manufacture extra tasks,
reports, agents, or ceremony merely to appear thorough.
```

Suggested resolution order when an agent does not know something:

```text
1. Check the explicit task/request.
2. Check the authoritative/current evidence already available.
3. Resolve it with a safe, read-only inspection if possible.
4. If the unknown still materially affects the answer or action: ASK FOR HELP.
5. Do not guess your way past the uncertainty.
```

The phrase **"no assumptions"** should be interpreted as "no material
assumptions presented or acted on as fact." It should not force an agent to ask
about harmless formatting details or choices that can be safely resolved from
existing context. The purpose is to prevent consequential guessing, not to
replace initiative with constant clarification.

If promoted, this belongs near the top of agent-grade operating instructions so
it constrains every downstream system rather than becoming another optional
process document.

Default disposition: **P1 instruction-quality candidate; short enough to be
loaded routinely, but still not active authority merely because it appears in
this backlog.**

---

# P1 — Session replay / trace reconstruction

## Problem

As MAPS becomes more capable, failures can span task state, routing, helper
work, communication, retries, review, recovery, and Git changes. Looking at the
final task row is not enough to answer:

> What exactly happened?

The legacy system had `session_replay.py` and a design for a disposable,
rebuildable diagnostic read model. The promotion ledger already marks that
behavior as worth preserving and simplifying.

## Smallest Lean version

Start with a read-only command:

```text
maps trace TASK-042
```

Example output:

```text
TASK-042

10:14  created
10:15  AGI passed
10:16  routed -> codex
10:16  claimed by codex-1
10:17  run RUN-91 started
10:18  helper qwen-3 spawned
10:23  helper returned
10:31  verification passed
10:32  submitted
10:35  review claimed by claude-2
10:39  changes requested
10:52  resubmitted
10:56  approved
10:57  DONE
```

A deeper form could expose the execution contract:

```text
maps trace RUN-91 --full
```

Potential fields:

- task revision;
- run manifest ID;
- instruction/context hash;
- worker/model/harness;
- tools and permissions;
- writable and forbidden scope;
- budget;
- helper activity;
- policy decisions;
- verification evidence;
- recovery events;
- review events;
- communication/hcom coverage and completeness;
- final outcome if known.

## Hard boundaries

The replay layer MUST:

- be read-only;
- derive from canonical sources;
- be disposable/rebuildable;
- never grant authority;
- never become a second mutable task history;
- report missing or contradictory evidence rather than silently repairing it;
- state which communication sources were included or unavailable.

## Promotion trigger

Promote when debugging a failed or confusing run repeatedly requires manually
joining multiple SQLite/event/hcom/runtime sources.

## Proof

A trace should be reconstructable from canonical records after deleting the
replay index/cache.

---

# P1 — Outcome feedback and historical eval corpus

## Problem

A task can pass MAPS structural checks and review while still failing in the
real world later.

Examples:

```text
verification: PASS
review: PASS
outcome: SUCCESS
```

and:

```text
verification: PASS
review: PASS
outcome: FAILURE
reason: regression discovered later
```

must not be treated as equivalent.

The legacy audit specifically preserves the lesson to measure escaped defects
and validator blind spots rather than only activity or throughput. The
promotion ledger also retains `map_metrics.py` as a possible future eval/health
source.

## Smallest Lean version

Add a small outcome record linked to a completed task/run, without changing the
original immutable evidence.

Candidate fields:

```text
outcome_status
outcome_recorded_at
outcome_source
failure_class
rework_count
operator_intervention_count
escaped_defect
actor / operator provenance when applicable
notes/provenance
```

Do not require an outcome for every trivial task. Unknown is a valid state.

## Why it matters

Without real outcome feedback MAPS can accidentally optimize for:

> Agents are good at satisfying MAPS.

The desired target is:

> Agents are good at accomplishing the operator's actual goal.

## Eval corpus

Once enough outcome-linked runs exist, create a reproducible historical eval
set containing representative:

- successful tasks;
- failed tasks;
- tasks requiring rework;
- escaped defects;
- routing mistakes;
- context failures;
- helper failures;
- recovery events;
- review catches;
- false-positive/false-negative validators.

Use the recovered three-layer discipline:

1. mechanical/unit regression on discrete controls;
2. qualitative agent/review/context regression;
3. production trace and outcome sampling.

Maintain a small incident taxonomy and turn repeated real failures into frozen
regression cases.

The corpus should use frozen historical inputs and expected properties so that
changes to prompts, routing, policies, helpers, and validators can be compared
against the same cases.

## End-to-end practice outcome

Legacy `SYN-0002` adds an important evaluation guardrail: do not score isolated
components only. At least one recurring eval should measure whether an operator-
guided project can move through the whole useful lifecycle:

```text
correct orientation
→ safe first action
→ useful implementation/research result
→ interruption recovery
→ independent review
→ release/completion
```

and measure the context/coordination cost required to get there. A context
packet or helper policy that looks excellent in isolation but increases end-to-
end rework has not improved MAPS.

## Hard boundaries

Outcome data MUST NOT rewrite the original task history.

Later knowledge is appended as later knowledge.

An outcome label should record provenance because many outcomes require human
or downstream-system judgment. Operator/human attribution should be explicit or
`UNKNOWN`, not inferred from generic message text.

## Promotion trigger

Promote once Lean has enough completed runs that recurring failure/rework
patterns can be measured instead of discussed anecdotally.

---

# P1 — Context builder

## Problem

Agents should receive the information necessary to do the task, not the entire
repository and not an arbitrary semantic-search dump.

The legacy audit's strongest retained context principle is:

> Context packet, not context dump.

The promotion ledger preserves the context packet shape:

- Required;
- Optional/triggered;
- Excluded;
- staleness information.

## Historical evidence

Legacy `EXP-0004` and `EXP-0005` tested a scoped orientation packet rather than
merely proposing one. The first attempt was revised because it compressed away
an immediate read-before-mutate boundary. The repeated experiment froze a
six-row rubric/control first and then achieved all six passes with a treatment
of 2,619 bytes against a 44,432-byte scenario control (94.11% scenario-local
reduction).

That is **evidence for the packet pattern**, not proof that MAPS should replace
its full startup contract with a generated manifest. The preserved lesson is:
context compression is valuable only when authority, safety, uncertainty, and
the first required action survive the compression and the comparison uses a
frozen control/rubric.

## Smallest Lean version

A command such as:

```text
maps context TASK-042
```

could resolve an explicit packet:

```text
REQUIRED
AGENTS.md
TASK-042
runtime/state/sqlite_store.py
tests/test_state.py
DEC-007

OPTIONAL — trigger only if needed
CONTROL_PLANE.md
TASK-031 handoff

EXCLUDED
legacy/
unrelated tasks
superseded decisions
obsolete architecture notes
```

The packet should be assembled primarily from **known relationships and active
authority**, not merely vector similarity.

Conceptually:

```text
TASK
 +
explicit inputs
 +
applicable authority
 +
applicable decisions
 +
current state
 +
relevant prior evidence
        ↓
   CONTEXT PACKET
```

## Ranking principle

Prefer:

1. explicit task references;
2. active authority/policy;
3. canonical project state;
4. dependency relationships;
5. exact paths/symbols;
6. provenance-backed prior evidence;
7. semantic retrieval only as a bounded supplement.

## Exact evidence refinement

After the file-level packet works, experiment with disposable claim/evidence
cards containing exact sections or code symbols, source hashes, proof roles, and
separate negative boundaries. Preserve the evidence-integrity techniques from
`EXP-0006`, but **do not** treat its failed lexical retrieval implementation as
a baseline to port.

Evaluation must include meaning-preserving paraphrase/vocabulary-shift cases,
not only queries that reuse source terminology.

## What not to revive

Do **not** recreate the old full Library/knowledge-management subsystem merely
because retrieval is useful. The legacy evidence did not justify that amount of
machinery.

## Promotion trigger

Promote when agents repeatedly receive too much irrelevant context, miss known
required project information, or spend significant time rediscovering the same
canonical inputs.

## Proof

Evaluate against historical tasks:

- required-fact recall;
- exact-source/anchor recall when tested;
- irrelevant-context reduction;
- source visibility;
- stale/superseded-source rejection;
- negative-boundary/abstention quality;
- paraphrase/vocabulary-shift robustness;
- end-to-end acceptable-evidence rank;
- task success/rework impact.

---

# P1 — Operational-learning promotion loop

## Problem

Operational lessons discovered during real work can remain trapped in task
notes, incidents, or session continuity and therefore fail to affect later
agents.

A historical promotion record for this idea (`PROMO-0011`) is itself a useful
warning: it was marked `APPROVED` while its approval fields and destination were
left incomplete. Treat the idea as **preserved but not reliably completed** in
the legacy system.

## Smallest Lean version

Create a narrow registry that can promote a proven operational lesson into
startup/context guidance with explicit applicability, provenance, and expiry.

```text
observation -> candidate -> reviewed active lesson -> expiry/supersession
```

The projection into startup/context should be derived and rebuildable. The
lesson registry must not become a second task or policy authority.

## Promotion trigger

Promote when the same operational mistake recurs because a prior documented
lesson was not presented to the next applicable agent/task.

## Proof

A fresh agent/task should receive an active applicable lesson automatically,
not receive an expired/superseded one, and be able to trace the lesson back to
its source incident/task/run.

---

# P1 — Negative operating contract

## Problem

Positive instructions alone leave a large behavioral gap. An agent may obey the
stated goal while still making MAPS worse through unnecessary architecture,
verbosity, guessed requirements, scope expansion, duplicate state, or process
ceremony.

The negative contract should make the Lean philosophy operational by saying
what agents must avoid by default.

## Candidate form

Keep the active version short enough to survive routine context loading. The
longer rationale and examples can remain in supporting documentation.

A compact form might be:

```text
DO NOT overcomplicate. Use the smallest sufficient solution.
DO NOT over-explain. Use brevity in the face of grammar for the sake of concision.
DO NOT assume material facts, intent, authority, or requirements. Check; then ask.
DO NOT silently expand scope. Record adjacent ideas separately.
DO NOT confuse capability with permission.
DO NOT create duplicate truth.
DO NOT build permanent machinery for a one-off need.
DO NOT treat prose or memory as proof when current evidence can be checked.
DO NOT hide uncertainty or guess through consequential blockers.
DO NOT manufacture work after the requested result is complete.
```

## Uncertainty rule

"No assumptions" should mean no **material** assumption is acted on or presented
as fact. When something important is unknown:

```text
inspect existing evidence
→ resolve safely if possible
→ ask for help if it still matters
→ never fabricate certainty
```

This preserves agent initiative for harmless/reversible details while ensuring
unknown requirements, authority, destructive impact, external side effects,
security boundaries, and user intent are surfaced rather than guessed.

## Promotion trigger

Promote after review of the exact wording and place the compact form near the
top of agent-grade operating instructions. Treat violations as review/learning
signals before considering any mechanical enforcement.

## Proof

Historical or staged tasks should show fewer instances of:

- needless subsystem/process creation;
- scope expansion;
- guessed requirements or authority;
- verbose handoffs/reports that obscure the actual action;
- duplicate state/read models with unclear authority;
- unnecessary clarifying questions when evidence already answers the issue;
- consequential decisions made despite unresolved uncertainty.

---

# P1 — Git worktree isolation for parallel coding

Provenance: `LEAN SYNTHESIS FROM MULTI-AGENT FAILURE MODE`

## Problem

Git scope proof tells MAPS whether a run changed allowed files. It does not
physically stop two coding agents from interfering with the same working tree
while they execute.

As true parallel implementation increases, that becomes a separate isolation
problem.

## Smallest Lean version

For coding tasks that need writable repository access:

```text
claim task
   ↓
create dedicated Git worktree
   ↓
run agent inside that worktree
   ↓
verify changes/tests/scope
   ↓
review
   ↓
integrate or discard
   ↓
remove worktree
```

Example layout:

```text
repo/
worktrees/
  TASK-041/
  TASK-042/
  TASK-043/
```

## Hard boundaries

Worktree isolation MUST NOT imply authority to merge.

It should integrate with existing:

- task ownership;
- run manifests;
- writable/forbidden scope;
- review independence;
- repo-global mutation locks;
- recovery/cleanup.

Shared resources outside the worktree still require explicit concurrency
control.

## Promotion trigger

Prototype when two or more implementation workers are intentionally allowed to
modify the same repository concurrently often enough that worktree collisions
or branch hygiene become a material risk.

## Proof

Parallel integration tests should demonstrate that independent workers cannot
silently modify one another's uncommitted working state.

---

# P1 — Deterministic `maps flow` procedures

Provenance: `LEAN SYNTHESIS FROM REPEATED ORCHESTRATION`

## Problem

LLMs should reason about uncertain work. They should not repeatedly improvise
stable administrative procedures whose transitions are already known.

For example, release is mostly procedural:

```text
verify task state
↓
verify required evidence
↓
verify independent review
↓
verify approval/policy
↓
perform permitted integration/release action
↓
record result
```

## Smallest Lean version

Introduce a deliberately small deterministic flow layer only for mature,
repeated procedures:

```text
maps flow release TASK-042
maps flow review TASK-042
maps flow recover RUN-091
maps flow handoff TASK-042
```

A flow is a named sequence of existing guarded runtime operations. It should
not become a second workflow engine or a second task state machine.

## Good early candidates

- review preparation/routing;
- release/integration checks, including user-visible acquisition paths;
- recovery sequence;
- handoff/continuity checks;
- projection/read-model repair;
- possibly project bootstrap after the procedure stabilizes.

## Bad candidates

Do not encode genuinely creative or uncertain implementation/research work into
procedures simply to make everything look uniform.

## Promotion trigger

Promote a flow when the same multi-step procedure is performed frequently, its
branches are well understood, and operator/agent mistakes come mostly from
forgetting steps rather than from hard reasoning.

## Proof

The deterministic flow should produce the same guarded transitions as manual
use of the underlying runtime operations, with explicit failure reasons at the
step that failed.

---

# P2 — Small Mission Control / operator status surface

## Problem

The operator needs a compact answer to:

- what is running;
- what is blocked;
- what needs attention;
- which workers are active;
- whether the control plane is healthy;
- what recently completed or failed.

The old Command Center/Mission Control implementation carried too much UI and
fixed-roster baggage, but its **read-only operator-content contract** remains
useful. The promotion ledger explicitly drops the old UI while retaining this
possibility.

## Smallest Lean version

Start with CLI text, not an application:

```text
maps status
```

Example:

```text
MAPS
────────────────────────────────

TASKS
Active       3
Ready        5
Review       2
Blocked      1

WORKERS
Codex-1      TASK-041   14m
Claude-1     REVIEW-42   3m
Qwen-local   helper      1m

SYSTEM
SQLite       OK
LangGraph    OK
hcom         OK
RnS          OK

ATTENTION
TASK-038     lease stale
TASK-042     review requested
TASK-051     budget 88%

RECENT
TASK-037     DONE
TASK-036     DONE
TASK-035     FAILED -> recovered
```

A later version may surface advisory helper `NO PROGRESS` signals and explainable
wait records, but the status surface itself remains read-only.

## Design rule

Mission Control is a **read model**, not a control authority.

It may invoke explicit existing commands, but the screen itself must never
become canonical state.

## Promotion trigger

Promote when normal operation regularly requires several commands/files just to
understand current system state.

---

# P2 — Helper dispatch no-progress signal

## Problem

A helper can remain nominally live while producing no observable progress. This
is not the same as a stopped session and should not be handled by a naive fixed
timeout.

## Smallest Lean version

Read-only/advisory pilot on one helper surface: flag a dispatch only when both
status/event activity and output change have been absent for a bounded interval.

## Hard boundaries

- advisory first;
- no automatic kill/escalation in the initial experiment;
- no standing watcher-agent role;
- record false positives;
- keep the signal separate from task authority.

## Promotion trigger

Promote only after repeated live incidents show coordinators are spending real
turns manually polling apparently-alive helpers.

---

# P2 — Persistent helper continuity without persistent authority

## Problem

Some bounded specialists may benefit from remembering recent work across tasks:

- security helper;
- test helper;
- docs helper;
- repository-specific local helper.

Respawning them from zero can waste context, but giving them durable ownership
or authority would undermine Lean's helper model.

## Core distinction

```text
persistent identity/context     MAYBE
persistent resumable session    MAYBE
persistent task authority       NO
persistent ownership            NO
persistent review authority     NO
```

A resumed helper still receives a fresh bounded request from the current task
owner and remains subordinate to that request's scope.

## Promotion trigger

Promote only after repeated evidence that rebuilding a specialist's context is
costly and that bounded resumable context improves outcomes enough to justify
the lifecycle complexity.

## Proof

Tests must show that old helper context cannot expand a new request's scope or
inherit authority from a prior task.

---

# P2 — Controlled harness evaluation and refinement

## Problem

Once MAPS records runs and real outcomes, it can compare alternative operating
configurations rather than relying on intuition about which prompt, routing
rule, model/harness pairing, context packet, or validator is better.

This is the useful core of a "continual harness" idea.

## Safe architecture

```text
historical runs + outcomes
          ↓
reproducible eval corpus
          ↓
compare candidate configuration
          ↓
report measured differences
          ↓
refine.propose
          ↓
operator/review approval
          ↓
normal change process
```

The key operation is **propose**, not silently mutate.

## Candidate things to evaluate

- AGI instruction templates;
- context packet construction;
- worker/model/harness routing;
- helper use thresholds;
- validation rules;
- review routing;
- retry/recovery thresholds;
- deterministic flow designs.

Use the three-layer eval discipline described in the recovered historical
section so configuration improvements are tested mechanically, qualitatively,
and against sampled real outcomes/traces.

Use paraphrase/vocabulary-shift variants where retrieval/context behavior is
part of the candidate configuration so a lexical benchmark cannot create a
false sense of robustness.

## Hard boundaries

The refinement system MUST NOT:

- grant itself new permissions;
- weaken safety/review gates without normal approval;
- rewrite historical expected outcomes;
- optimize only for speed/cost while hiding defects;
- train against the same eval examples in a way that makes the benchmark
  meaningless;
- change active configuration simply because a candidate scores better on one
  metric.

## Promotion trigger

Promote after outcome feedback and a representative eval corpus exist. Before
that, "self-improvement" would mostly be speculation.

---

# P2 — Cost/yield and escaped-defect metrics

## Problem

Raw task counts, token use, elapsed time, or agent utilization can produce a
misleading picture of system performance.

Useful measurement should connect resource use to outcomes.

## Candidate metrics

```text
successful outcome / run
rework rate
escaped defect rate
review catch rate
validator blind-spot rate
operator intervention rate
recovery success rate
cost per successful outcome
time per successful outcome
context bytes/tokens per successful outcome
helper yield
routing correction rate
```

These should be interpreted together rather than collapsed prematurely into one
magic score.

Operator-intervention and actor metrics must use explicit provenance where
available and `UNKNOWN` where attribution cannot be established safely.

## Promotion trigger

Add only once enough homogeneous runs exist for the metric to mean something.
A dashboard over five incomparable tasks is not evidence.

---

# P2 — Risk-specific review lenses

## Problem

A generic functional review can miss trust-boundary or safety problems even when
the reviewer is competent. Historical MAP evidence showed that an explicitly
security-framed pass found real issues that ordinary functional/architecture
review plausibly would have missed.

## Smallest Lean version

For medium/high-risk tasks, make applicable review questions explicit without
requiring a second reviewer by default.

```text
functional correctness
acceptance criteria
security / trust boundary
privacy
destructive / data-loss
release / deployment path
```

For security/authority properties, prefer behavior-level verification over
source-text matching. For release/deployment, inspect the actual user-visible
acquisition path and packaged/generated artifact when one exists.

Only activate lenses relevant to the task. Require additional independent
reviewers only when the actual risk warrants them.

---

# P2 — Bounded phase-boundary discovery

Use the method from recovered item K: a visible, evidence-linked, proposal-only
pass after a significant phase/milestone. It is explicitly **not** a permanent
Discovery Agent or continuous model loop.

Promote only if occasional cross-cutting omissions continue to survive ordinary
task closeout/review and the bounded pass shows useful yield above its curation
cost.

---

# P2 — Bounded system-adherence audit

Use the method from recovered item L when a cluster of MAPS mechanisms has been
added or materially changed. Measure whether each mechanism is reachable,
actually used, and still consistent with its playbook rather than merely
counting documentation presence.

The audit is diagnostic and proposal-producing only.

---

# P2 — Authority provenance / ratification guard

Preserve the recovered item M invariant: proposal status survives citation.
Consider a mechanical warning only for load-bearing task/policy/decision
references if authority drift recurs in Lean.

---

# P2 — Review-time evidence freshness

Preserve recovered item N: consequential evidence must either bind to an
immutable revision or be re-derived by the reviewer against the state actually
being approved.

---

# P2 — Explainable wait projection

Preserve recovered item Q as a read-only projection over structured hcom/request
metadata. It may improve status/replay/recovery diagnosis but cannot itself
reassign work or mutate task authority.

---

# P3 — Scoped temporary halt authority

## Problem

A monitoring/validation component may someday need narrowly delegated power to
halt a dangerous execution class without gaining permanent broad authority.

Lean already has durable halt state. This candidate concerns delegation around
that existing mechanism, not a new halt subsystem.

## Promotion trigger

Only after a concrete safety incident demonstrates that telemetry-only behavior
was insufficient and a bounded temporary grant would have materially reduced
risk.

---

# Ideas intentionally not revived by default

The following may contain useful concepts but should **not** return simply
because the old system or external tools supported them.

| Idea | Default decision | Reason |
|---|---|---|
| Large always-running `mapd` daemon rewrite | Skip | Adds a new central service before proven need |
| Full Library / giant knowledge graph | Skip | Retrieval principle is useful; old subsystem cost was not justified |
| Old Command Center / Mission Control UI | Drop implementation | Preserve only read-only content contract |
| Fixed agent roster | Drop | Conflicts with capability-based provider-neutral routing |
| WezTerm-dependent orchestration | Drop | Terminal is presentation, not authority |
| Provider-specific permanent identities | Drop | Runtime should remain provider-neutral |
| Debate-agent bureaucracy | Optional experiment only | Independent review is valuable; staged debate is not automatically valuable |
| More role/persona prompting | Skip | Specify outcome, authority, evidence, and capability instead |
| Temporal | Defer | Consider only if current LangGraph/RnS durability proves insufficient |
| Cedar/policy-language rewrite | Defer | Current policy should be replaced only by demonstrated complexity need |
| A2A interoperability | Defer | Useful only when cross-system interoperability becomes real work |
| MCP-everywhere architecture | Defer | Use adapters where valuable; do not make protocol adoption the architecture |
| Firecracker/microVM per worker | Threat-model dependent | Isolation cost should match actual threat model |
| Large-scale formal-methods program | Optional | Prefer executable invariants/tests first; formalize only high-risk state/concurrency rules |
| Continuous discovery/emergence agents | Do not revive | Bounded phase-boundary discovery tested useful; continuous role/loop did not earn its cost |
| Legacy lexical claim-card retriever | Do not revive | EXP-0006 failed overall retrieval/abstention targets; preserve evidence-integrity techniques only |

---

# Suggested development order if these become necessary

This is an ordering of dependency/value, **not an approved roadmap**.

```text
CURRENT MAPS LEAN
       │
       ▼
0. telemetry / secret-safety audit
       │
       ▼
1. trace / session replay
       │
       ▼
2. real outcome recording
       │
       ▼
3. three-layer historical eval corpus + useful metrics
       │
       ├───────────────┐
       ▼               ▼
4. context builder   worktree isolation
       │               │
       ▼               │
5. operational learning
       │               │
       └───────┬───────┘
               ▼
6. deterministic flows for mature procedures
               │
               ▼
7. small operator status surface
               │
               ▼
8. controlled harness evaluation
               │
               ▼
          refine.propose
```

The negative operating contract is an instruction-quality candidate rather than
a subsystem dependency. If promoted, it should be reviewed and then loaded near
the top of the agent operating contract so it constrains all later work.

Independent supporting practices can be tested when their triggering evidence
appears:

- helper no-progress detection;
- explainable waits;
- bounded phase-boundary discovery;
- bounded system-adherence audits;
- authority-provenance warnings;
- risk-specific review lenses;
- review-time evidence freshness;
- persistent helper continuity.

---

# Promotion template

When one of these ideas becomes a real candidate, create a normal project/task
rather than implementing directly from this file.

Use this minimum record:

```markdown
## Candidate

### Problem observed
What happened, how often, and what evidence exists?

### Existing Lean behavior
What currently handles this problem? Why is it insufficient?

### Smallest proposed behavior
What is the minimum change worth testing?

### Authority boundary
What may the new component read, write, recommend, or execute?

### Source of truth
Which existing canonical state remains authoritative?

### Verification
How will we prove the behavior works?

### Outcome metric
What measurable result would justify keeping it?

### Failure / rollback
How can the experiment fail safely or be removed?

### Decision
PROMOTE / KEEP EXPERIMENTAL / REJECT / DEFER
```

---

# Final principle

The useful unfinished direction is not "more agents" or "more orchestration."

It is making MAPS increasingly able to:

```text
protect what observability records
        ↓
reconstruct what happened
        ↓
measure whether it actually worked
        ↓
provide better bounded context
        ↓
carry forward proven operational lessons
        ↓
constrain itself against unnecessary complexity and guessing
        ↓
verify authority/evidence provenance
        ↓
isolate parallel execution
        ↓
automate stable procedure
        ↓
compare alternative configurations
        ↓
propose evidence-backed improvements
```

while retaining the existing rule:

> Capability does not create authority.

MAPS should become easier to inspect and improve **without becoming harder to
trust**.