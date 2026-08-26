# MAPS_Lean Deep Project Archaeology Audit
## Whole-project forensic reconciliation before the external Proof Phase

Status: `RECONCILIATION AUDIT — EVIDENCE / ROADMAP INPUT, NOT TASK AUTHORITY`

Date: `2026-08-26`

Audit baseline: `main@d22036bcebca3d7eb729c2b9dd70e82c229ac60a`

## Connections

- [Audit index](README.md)
- [Proof Phase Audit & External Test Plan](2026-08-26-maps-proof-phase-audit-and-test-plan.md)
- [Current reconciliation task](../tasks/reconcile-project-truth-20260826.md)
- [Current reconciliation / Proof Phase handoff](../handoffs/2026-08-26-project-reconciliation-and-proof-phase.md)
- [Roadmap index](../roadmaps/README.md)
- [Roadmap 06 — Portable Deployment](../roadmaps/agent-harness-capabilities/06-portable-deployment.md)
- [Information lifecycle](../../playbook/INFORMATION_LIFECYCLE.md)
- [Roadmap trajectory check](../../playbook/ROADMAP_TRAJECTORY_CHECK.md)
- [Tenth-Seat review](../../playbook/TENTH_SEAT_REVIEW.md)
- [Spiderweb Audit](../../playbook/SPIDERWEB_AUDIT.md) once PR #174 lands; until then PR #174 is the implementation source.

**Disposition:** use this audit to reconcile current meaning before the external
Proof Phase. A finding becomes work only when shaped into an authorized task,
roadmap item, operator decision, or other existing authority surface.

---

## 1. Executive diagnosis

A deep audit was warranted.

MAPS_Lean does not mainly suffer from a failure to record information. It
preserves a great deal:

- runtime code and SQLite state;
- `AGENTS.md` and playbooks;
- capability roadmaps/checklist;
- design notes and task briefs;
- reviews and handoffs;
- ideas, insights, research, and decisions;
- migration ledgers and future-idea records;
- historical context and legacy emergence records;
- Git branches and PR history.

The principal failure mode is more specific:

> **memory reconciliation and disposition drift.**

MAPS can preserve an original idea, later design, implementation, review
finding, and old status while failing to make their relationship obvious to the
next agent.

That creates several failure classes.

### Genuine idea loss

A good idea still exists in history, but no current navigation surface points to
it.

### Ghost loose end

An old note says something is future/unimplemented after later code already
implemented it. A new agent can rediscover and duplicate solved work.

### False completion

A status summary compresses a capability more strongly than production evidence
supports.

### False incompletion

A README/checklist says a capability does not exist after it has landed.

### Review-debt loss

A useful non-blocking reviewer finding is accepted as “carry forward” but has no
forward disposition.

### Decision-lifecycle drift

Implementation reality settles a question while the formal decision record
remains `PROPOSED` or otherwise stale.

### Temporary-workaround drift

A temporary workaround retains its removal condition but nobody verifies
whether the original reason still exists.

### Orientation drift

A dated “current” document remains on a recommended read path after it stops
being useful current orientation.

The correct response is **not another memory subsystem**. The immediate need is
reconciliation of mechanisms MAPS already has, then external proof that a fresh
agent can navigate them.

---

## 2. Existing information topology

MAPS already has sensible information classes. The risk is overlap and stale
relationships.

### Active authority

Examples:

- `AGENTS.md`;
- canonical SQLite task/run/review/evidence state;
- accepted task requirements;
- explicit operator instruction;
- merged implementation behavior;
- explicit policy/authority decisions.

These win on conflict.

### Active navigation / program steering

Examples:

- `state/CURRENT.md`;
- coordination README;
- capability checklist;
- program steering;
- roadmap trajectory check;
- current handoff.

These are not runtime authority, but they decide where agents look. Navigation
errors therefore create implementation risk indirectly.

### Design/explanatory memory

Examples:

- dated design notes;
- historical rationale;
- detailed roadmaps;
- research;
- reviews and repair records.

These preserve reasoning but should not silently become current status.

### Candidate/deferred/experimental memory

Examples:

- `migration/FUTURE_IDEAS_BACKLOG.md`;
- `work/ideas/`;
- `work/insights/`;
- research experiments;
- legacy emergence records.

These preserve options without authorizing them.

### Historical/provenance memory

Examples:

- dated capability reconciliations;
- old handoffs;
- migration audits;
- preserved legacy MAP;
- old task/review artifacts;
- branch history.

History is valuable when explaining why. It is dangerous when still presented
as present orientation.

---

## 3. MAPS already invented mechanisms for this problem

The archaeology found that MAPS has repeatedly designed correct preservation
mechanisms:

### Information lifecycle

`playbook/INFORMATION_LIFECYCLE.md` distinguishes active,
retired/superseded, and archived information and warns against archiving
stale-but-still-active material merely to avoid reconciliation.

### Emergence

`playbook/EMERGENCE.md` uses:

```text
observe → connect → synthesize → name → test → promote
```

This correctly separates noticing from authority.

### Program steering / trajectory checks

Agents are expected to trace self-selected work to operator/task/roadmap
authority and re-check long-running `IN PROGRESS` claims against current
`main`.

### Repair and learning

The repair playbook defines a path from incident → repair record → reproducer →
frozen regression case → evaluation.

### Future-idea preservation

Migration audit and future-idea backlog deliberately preserve valuable old
ideas without making them an execution queue.

### Decisions and handoffs

Formal decision status and compact current handoffs already exist as intended
cross-session mechanisms.

Therefore the problem is not “we forgot to design a loose-ends system.”

It is:

> **existing capture/disposition mechanisms are not always reconciled after
> later reality changes.**

---

## 4. Historical precedent: MAP suffered this exact failure before

### INS-0013 — capture was skipped

Legacy MAP recorded that a whole project shipped without Emergence capture even
though the mechanism already existed. The response was to make capture
mandatory through a release gate.

Necessary, but not sufficient.

### SYN-0004 — “Coverage debt lost its own fix”

A preserved synthesis explicitly records that MAP approved a fix for losing
ideas, then effectively lost the fix until rediscovering it later while building
tooling intended to find lost ideas.

This is nearly the exact failure being investigated now.

### EXP-0007 — idea scouting as cadence, not role

MAP then proposed a bounded 14-day experiment for startup idea-coverage checks,
with a planned window ending `2026-08-04`.

Its artifact still says `result: pending` and lacks a recorded closure.

Honest disposition:

```text
experiment window elapsed
planned closure not recorded
coverage evidence sparse
result = INCOMPLETE / INCONCLUSIVE
```

The lesson is structural:

```text
CAPTURE
→ REVIEW
→ DISPOSITION
→ later RECONCILIATION
```

Mandatory capture does not guarantee lifecycle closure.

---

## 5. A recovered “right idea”: prove MAP externally

A particularly important historical record, INS-0023, warned that MAP kept
building inward infrastructure without first proving a real external workflow.

That record remained `RAW`.

Its core direction is essentially the current Proof Phase:

> choose a real proving workflow before continuing internal machinery.

This demonstrates that external proof is not a sudden late pivot. It is a
long-standing unresolved concern that survived beneath later infrastructure
work.

The current [Portable Deployment roadmap](../roadmaps/agent-harness-capabilities/06-portable-deployment.md)
now contains the right proof shape:

- one real external repository;
- one real bounded task;
- target-native implementation/verification;
- independent review;
- inspectable PR/merge;
- no synthetic substitute counted as final DONE.

Use D3 as the first real Proof Phase vehicle rather than inventing a duplicate
pilot.

---

## 6. Historical insights that did survive into Lean

The archaeology also shows substantial continuity rather than wasted work.

### Durable blackboard / gates

Old insight: durable state and gates are the differentiator from ephemeral
agent swarms.

Lean descendant: SQLite task/run/evidence truth, immutable review binding,
lineage, guards.

### Prose-only rules fail

Old insight: a promoted rule hidden in guidance is often skipped; even the
agent that built a rule can violate it.

Lean descendants: deterministic hooks, exact-head evidence, CI, trust gates,
Context Builder projection.

### Coordination friction before retrieval sophistication

Old insight: stalled-worker/reviewer coordination deserved priority over more
retrieval.

Lean descendants: explainable waits, stalled-worker triage, helper continuity,
no-progress advisory, recovery production composition.

### Firewall/provider-health ambiguity

Historical helpers could look alive while blocked on local process/network
approval. Current no-progress/helper continuity does not prove provider health.

This remains a useful external test scenario; do not auto-approve or hallucinate
the cause.

### False recovery wakeups

Old RnS concern: repeatedly waking workers without actionable owned work.
Current recovery design appears to address the state distinction, but behavior
should still be confirmed externally.

### Privileged gateway/adversarial review

Old insight: privileged state/action boundaries deserve adversarial review.
Current risk-specific reviews and the bounded Tenth-Seat method are compatible
descendants.

---

## 7. Ghost loose ends found during archaeology

A major correction to the first loose-end pass was the environment-report
design.

An August 21 note proposed:

- task→EnvironmentSpec association;
- report envelope;
- spec hash/task revision/project root;
- freshness/stale handling;
- pure router behavior.

At first glance it looked like a valuable orphaned future task.

Deeper reconciliation showed much of it had already landed later.

Lesson:

> **Never classify a dated “future implementation” note as an orphan until it
> is reconciled against current code, current checklist, and merged PR history.**

This is why Spiderweb must flag candidates but must not semantically auto-link
or create work.

---

## 8. Current documentation/status contradictions found

### Capability checklist verification header

The checklist advertised an old verification date while later rows had newer
evidence. That made the document neither a clean historical snapshot nor a
fully current scoreboard.

### H4 validation tiers

Old prose said there was no production call site.

Current reality includes a production recovery composition and PR #172's
advisory validation hook-in.

The real remaining gap is more precise: production invocation exists, but the
validator is generally inert because normal production runs do not yet supply
the run-bound environment evidence it consumes.

### H5 Harness recovery

Production recovery construction now exists, but default production composition
does not yet use HarnessService. “No production recovery” and “fully wired” are
both inaccurate.

### SEC3 destructive/external action guard

A guard primitive exists. It is not a general production execution boundary.
Do not describe it as either “not built” or “fully enforced.”

### SEC7 incident→regression workflow

A concrete repair/regression procedure now exists. The real open question is
whether it has been demonstrated on a real incident without excessive process
cost.

### Root/runtime README drift

Several descriptions lagged later operational-learning, review-evidence,
semantic-eval, and validation production work. PR #173 reconciles the clearest
cases.

---

## 9. Orientation drift

### `state/CURRENT.md`

The previous current-state pointer lagged the actual work arc. Live GitHub could
recover code/PR/CI facts but not all rationale/deferred decisions.

PR #173 refreshes current orientation and adds a compact current handoff.

### Historical “current-state” files

Some files correctly identify themselves as historical but remain named or
recommended like current onboarding material. Preserve them as provenance, but
do not make them the shortest path to present truth.

### Dated capability reconciliation on the roadmap path

A dated reconciliation can remain useful evidence while ceasing to be current
orientation. Current roadmap navigation should point first at reconciled live
planning surfaces.

Principle:

> **Preserve history deeply, surface current meaning shallowly.**

---

## 10. Decision-lifecycle drift

The repo has substantial historical rationale, so the problem is not absence of
decision memory.

The issue is split lifecycle across:

- formal decisions;
- historical rationale;
- dated design notes;
- operator-decision notes;
- implementation reality.

Example: DEC-001 still says `PROPOSED` while much of its target operating model
exists in current structure.

A maintenance pass should not silently promote operator decisions. Instead,
link the record to current implementation and flag formal status for explicit
authority.

---

## 11. Review debt is a separate loss channel

PR #172's independent review is a concrete example.

It approved the PR while recording multiple non-blocking findings. Some were
corrected/discharged; several were explicitly “carried forward.”

Before reconciliation, those findings were not normal tasks/issues/checklist
items. Their only durable future path was review/PR prose.

PR #173 adds an explicit disposition note so carried-forward findings have one
of:

```text
TEST
WATCH
DEFERRED
ACCEPTED RISK
SUPERSEDED
FIX IN EXISTING TASK
```

Do not automatically turn every reviewer nit into a task. Preserve disposition
and revisit trigger.

---

## 12. Branch archaeology result

The many surviving non-main branches initially looked like a possible place for
lost implementation.

Deeper comparison showed most examined branches correspond to already-merged
PRs and look divergent mainly because squash merges preserve different commit
objects.

The previously uncertain
`switchyard/context-evidence-stage1-sync-20260816` was behind current `main`
with no unique commits ahead at audit time.

Conclusion:

> **branch surface is mostly noise/ambiguity, not evidence of major hidden
> unmerged product work.**

Still perform a final containment/PR mapping check before deleting branches.

---

## 13. Open Skill lifecycle work

At audit baseline PR #171 was the active Skill lifecycle persistence Half 1.
Its own contract deliberately did not authorize production caller/authority
Half 2 or capability completion.

Boundary:

1. finish/fail Half 1 through normal review;
2. do not automatically start Half 2;
3. freeze further lifecycle expansion;
4. use external/adversarial evidence to decide if authority wiring is needed.

---

## 14. Real production gaps after removing ghost gaps

The remaining gaps are more precise than “not implemented.”

### Recovery

Production invocation exists; default composition does not fully use
HarnessService and there is no trusted automatic worker→session binding source.

### Environment validation

Production-reachable validation exists but lacks a normal production evidence
writer supplying the bound spec/report input.

### Destructive/external guard

Primitive exists; general production action path does not use it.

### Skills

Metadata selection/trust foundations exist; full procedural Skill-body
activation remains a Proof Phase candidate.

### Helper continuity / no-progress

Remain advisory by design. Do not add auto-kill/reassign authority until real
failure evidence justifies it.

### Harness configuration identity

Structurally representable, operational value not proven.

### Regression-case process

Procedure exists; real use must be demonstrated.

---

## 15. Temporary hcom fork pin needs re-verification

MAPS pins hcom to a fork originally associated with exact `hcom send --json`
event receipt behavior.

Current `HcomAdapter.send()` no longer appears to use that form and current
lineage reads stable IDs from event history.

That does **not** prove the fork is unnecessary.

Disposition:

> re-verify all current callers/contracts before removal; keep the pin until
> absence of a live dependency is demonstrated.

Temporary decisions need both a reason and a revisit/removal condition.

---

## 16. “Nothing durable should be an island”

The archaeology supports making this an explicit project-wide information rule.
PR #173 adds the operating-contract form.

Every forward-relevant durable artifact should answer at least one of:

```text
What caused this?
What does this support?
What is this related to?
What did this become?
What replaced this?
What evidence supports it?
When should it be revisited?
```

Apply to:

- tasks/projects/roadmaps;
- decisions;
- instructions/playbooks;
- AGI checks;
- research;
- E/I insights/syntheses/ideas/experiments;
- repair/regression records;
- reviews/findings;
- handoffs;
- risks/workarounds;
- important design notes.

Prefer standard relative Markdown links and stable IDs.

Principle:

> **Wiki behavior, standard Markdown storage.**

Do not manually maintain duplicate backlinks when they can be derived.

---

## 17. Spiderweb Audit

The evidence in this archaeology justifies a bounded relationship-integrity
mechanism, not a knowledge-graph service.

PR #174 implements the proposed shape:

```text
repository
→ deterministic Markdown relationship scan
→ structural candidates
→ bounded AGI semantic reconciliation
→ human/authorized disposition
```

Objective/advisory categories include broken links, duplicate stable IDs,
orphan/thin connections, stale disposition candidates, and overdue experiments.

The AGI must not:

- auto-promote ideas;
- auto-create tasks;
- infer authority;
- reopen decisions from thematic similarity;
- auto-link semantically;
- optimize for graph density.

The graph is a derived view, not authority.

---

## 18. Tenth-Seat status

The Tenth-Seat protocol is a real active playbook method.

Its purpose is not generic devil's advocacy. It asks, when a consequential
consensus becomes unusually clean:

> **What is the strongest credible case that the consensus is wrong?**

It is deliberately rare, non-veto, non-daemon, and preserves a minority report
when triggered.

The archaeology found a discoverability gap: the Tenth-Seat playbook assigned
trigger ownership to trajectory checking, but the trajectory procedure lacked
the reciprocal reference.

PR #173 adds that cross-link rather than automating the protocol.

---

## 19. Corrections to the earlier loose-end pass

The deeper audit changed several earlier conclusions:

1. **Do not immediately add another `LOOSE_ENDS.md` database/index.** MAPS
   already has future ideas, E/I, decisions, handoffs, trajectory checks,
   repair records, and roadmaps. Reconcile them first.
2. **Environment-report sourcing was not simply orphaned.** Later work
   implemented substantial portions.
3. **Decision rationale is not absent.** Current lifecycle/discoverability is
   fragmented.
4. **SEC7 has a process.** What is missing is demonstrated use.
5. **Branches mostly reflect merged history.** No major hidden unmerged product
   work was supported by examined evidence.
6. **Some old zero-production-caller insights are historical/partly resolved.**
   Reconcile their disposition instead of rediscovering them.

This section is why this later audit should supersede conflicting loose-end
claims in the companion Proof Phase document.

---

## 20. Recommended reconciliation-only pass

Before external expansion:

1. reconcile the capability checklist against complete current `main`;
2. refresh current orientation/handoff;
3. remove old historical “current” records from the shortest onboarding path;
4. reconcile forward-relevant ideas/insights with later implementation;
5. close EXP-0007 honestly as incomplete/inconclusive;
6. reconcile DEC-001's formal status through proper authority;
7. disposition carried-forward reviewer findings;
8. re-verify hcom fork necessity;
9. clean stale branches only after containment checks;
10. finish/fail current bounded PRs, then freeze new architecture;
11. begin the external D3 Proof Phase.

PR #173 implements the small documentation/information-lifecycle subset of this
plan without changing runtime behavior or capability status.

---

## 21. What not to build before external proof

This audit does **not** justify:

- another task database;
- a new memory service;
- permanent loose-end/watch agents;
- automatic review-debt task creation;
- generic auto-remediation;
- automatic worker kill/reassignment;
- Capability Packs;
- universal snapshot/sandbox machinery;
- a semantic knowledge graph merely to connect Markdown;
- a second roadmap status system.

The project already has enough structure to test the discovered problem.

---

## 22. Fresh-Agent continuity test

After reconciliation, give a fresh agent only the repo and ask:

- What is MAPS trying to prove next?
- What is active?
- What is intentionally incomplete?
- What is blocked on operator authority?
- Which historical ideas remain worth testing?
- Which old gaps are already resolved?
- What temporary workarounds remain?
- What decisions should not be reopened?

Measure:

- missed important items;
- ghost gaps rediscovered as new;
- false completion claims;
- historical files read;
- tool calls/time to orient.

This directly tests MAPS's continuity claim on itself.

---

## 23. Then run the external Proof Phase

Use the companion [Proof Phase plan](2026-08-26-maps-proof-phase-audit-and-test-plan.md)
and D3 external pilot.

Questions include:

- did shaping prevent scope drift?
- did authority boundaries prevent unsafe assumptions?
- did independent review catch meaningful defects?
- did durable state improve handoff/recovery?
- did Context Builder reduce or increase burden?
- did Skills help?
- did EnvironmentSpec improve reproducibility?
- did recovery/no-progress catch a real interruption?
- what was the control-plane tax?
- which mechanisms can be removed?

The next architectural move should be:

```text
STOP ADDING
→ RECONCILE CURRENT TRUTH
→ PRESERVE / DISPOSITION OLD THREADS
→ PROVE MAPS ON A REAL EXTERNAL TASK
→ MEASURE WHAT HELPED
→ REMOVE OR SIMPLIFY WHAT DID NOT
```

---

## 24. Central conclusion

MAPS_Lean has not wasted its prior work. The archaeology shows strong continuity
from older MAP lessons into Lean mechanisms.

The problem is that the record of that evolution has not always been reconciled
after mechanisms land.

That produces a repository with strong memory but growing interpretation cost.

The design principle to preserve is:

> **MAPS does not need to remember more; it needs to get better at knowing what
> its remembered information means now.**
