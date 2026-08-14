# Research Summary

Summary ID: SUMMARY-HPOM-OPERATING-MODELS-2026-07-18
Related brief: none — bounded comparative advisory research
Related claim matrix: none — source links and claim limits are retained below
Related assumption register: none — fit limits and caveats are retained below
Owner: codex-lab-lilo
Date: 2026-07-18
Status: COMPLETE

## Question

Which practices improve HPOM efficiency, accountability, learning, and human
control without importing an organizational framework wholesale?

## Answer

The comparison supports small, owned, reversible improvement loops; temporary
facilitation rather than permanent helper bureaucracy; clear mutable-work and
communication lanes during true recovery; and visible self-service checks only
after a workflow is genuinely repeatable. It does not support importing an
organizational framework wholesale or treating AI adoption as proof of faster,
safer delivery. The detailed source evidence, fit limits, and five bounded
candidate experiments follow.

## Confidence

- [x] MEDIUM — six authoritative or primary operating-model sources support
      the direction, but their organization-scale evidence is not causal proof
      for a small MAP workspace.

## Confidence decays after

Re-verify before treating a candidate experiment as a standing HPOM convention,
or after a material change to helper routing, recovery ownership, or the
operator status surface.

## Open questions

- Which candidate experiment, if any, reduces real operator interpretation or
  coordination cost in a measured MAP practice run?
- Whether the proposed attention classes reduce follow-up questions without
  becoming a permanent incident-role system.

## Downstream effect

- [x] Informational only — no direct task or decision. The current synthesis
      `MAP_System/emergence/synthesis/SYN-0002-a-goal-first-evidence-budgeted-practice-loop-makes-map-coordinat.md`
      cites this as evidence, not as an adopted operating rule.

## Evidence sources

1. [Toyota Way 2001](https://www.toyota-global.com/company/history_of_toyota/75years/data/conditions/philosophy/toyotaway2001.html) — Toyota identifies continuous improvement and respect for people as its two pillars, while explicitly treating the method as evolving with conditions.
2. [Google SRE: Managing Incidents](https://sre.google/sre-book/managing-incidents/) — Incident command holds high-level state; operations is the only group modifying the system during an incident; communication and planning are separable roles.
3. [Google SRE: Incident Management Guide](https://sre.google/resources/practices-and-processes/incident-management-guide/) — Google frames incident work as coordinate, communicate, and control, with roles chosen by incident context rather than reporting hierarchy.
4. [Team Topologies: Key Concepts](https://teamtopologies.com/key-concepts) — distinguishes stream-aligned, platform, enabling, and complicated-subsystem teams plus collaboration, X-as-a-Service, and facilitation interaction modes.
5. [Team Topologies: X-as-a-Service](https://teamtopologies.com/news-blogs-newsletters/x-as-a-service) — defines self-service capability consumption as a way to remove recurring coordination overhead; warns implicitly against undefined handoffs.
6. [Google Cloud DORA 2024 summary](https://cloud.google.com/blog/products/devops-sre/2024-dora-survey-now-open) — reports associations between higher documentation quality, faster reviews, and delivery performance, while also reporting that AI adoption alone can correlate with lower throughput/stability without fundamentals such as small batches and robust testing.

## Model comparison

| Model | Source fact | Strength relevant to HPOM | Failure mode / fit limit |
|---|---|---|---|
| Lean continuous improvement (Toyota) | Continuous improvement is paired with respect for people and is expected to evolve. | Treat each observed friction as a hypothesis for a small, owned improvement instead of adding permanent controls. | Do not import manufacturing rituals, velocity targets, or a universal stop-the-line mechanism into a small agent workspace. |
| Incident command / SRE | Command, operations, communications, and planning separate as needed; operations alone mutates during an incident. | Gives HPOM a temporary high-urgency mode: one accountable coordinator, one mutable-work lane, one concise operator-update lane. | Routine tasks are not incidents. Permanent IC-style roles would add ceremony and duplicate task ownership. |
| Team Topologies | Facilitation is temporary and focused; X-as-a-Service reduces repeated high-bandwidth coordination when a capability is stable. | Clarifies when a helper is worthwhile: temporary enabling/facilitation, or a deterministic self-service tool after the workflow stabilizes. | Do not label individual agents as permanent "teams" or turn every helper into a platform product. |
| DORA-style delivery improvement | Documentation/review speed associate with delivery performance; AI alone does not guarantee speed or stability. | Measure a few outcome metrics around small batches and tests before crediting added helpers/model use with improvement. | DORA’s organization-scale correlations are not causal proof for MAP’s tiny sample; avoid copying industry benchmarks. |

## Problem-to-practice comparison

| Current HPOM problem/opportunity | Evidence-backed practice | MAP inference | Token / coordination-cost implication | Fit limit |
|---|---|---|---|---|
| Operator cannot quickly distinguish an ordinary wait from a real blocked lane. | SRE separates command, operations, and communications and maintains live state. | Add an attention class to the existing operator projection: routine, needs-owner, or incident-like; show owner, mutable lane, and next update. | Fewer raw hcom/file reads and fewer duplicated status questions; one concise state projection costs less than repeated narratives. | Only activate incident-like structure for defined high-impact cases. |
| Helpers sometimes help, but can add handoff overhead. | Team Topologies treats facilitation as temporary; stable capabilities can become self-service. | Route a helper only when it has a time-boxed enabling outcome or can validate a repeatable deterministic tool. | Reduces idle helper/context-transfer cost; a reusable validator can amortize one-time setup. | Do not turn local/model helpers into unsupervised services or permanent bureaucracy. |
| Process improvements risk becoming new rules faster than they prove value. | Toyota’s improvement model is continuous/evolving; DORA cautions that AI/process adoption alone does not ensure performance. | Every HPOM change should have a baseline, a success/failure signal, an owner, and an expiry/review date. | Limits tokens spent maintaining unproven conventions; enables removal of controls that do not reduce operator questions or cycle time. | Avoid demanding metrics for trivial, low-risk documentation moves. |
| Recovery/escalation work can distract implementation and create conflicting writes. | Google SRE gives operations the only mutation lane and lets roles collapse when the incident is small. | During an active recovery, designate one integration/mutation owner; helpers may inspect, summarize, or communicate but do not edit the recovery surface. | Avoids duplicate diagnostics, conflicting patches, and reviewer reconstruction cost. | Use only for declared recovery/incident scope; MAP’s usual task ownership remains sufficient otherwise. |
| Repeated coordination tasks may be manual despite stable inputs. | Team Topologies’ X-as-a-Service emphasizes clear, self-service interfaces. | Promote a repeated deterministic check into a documented command/API only after it has passed a bounded trial and has a clear source of truth. | Can replace recurring coordination turns with one visible command and durable output. | No automatic promotion for ambiguous judgment, authority, or human-intent work. |

## Candidate experiments (not decisions)

| # | Candidate experiment | Evidence basis | Minimal measure and stop rule |
|---|---|---|---|
| 1 | Add three read-only attention classes to the planned operator status projection: routine, needs-owner, and incident-like. | Google SRE’s explicit command/control/communication separation. | For two weeks, log time from status change to correct owner identification and count operator follow-up questions. Remove/revise classes that do not change either measure. |
| 2 | Require a helper-routing hypothesis: expected wall-clock saving, bounded facilitation output, and whether the result could become a deterministic self-service check. | Team Topologies’ temporary facilitation and X-as-a-Service distinction. | Sample ten helper assignments; compare expected versus actual saving and integration rework. Drop the field if it only restates scope/stop conditions. |
| 3 | Run a one-task recovery drill with an explicit coordinator, sole mutable-work owner, and communication summary owner. | Google SRE incident command. | Use a synthetic/staged state only; measure duplicate edits/messages and operator clarity. Do not adopt an incident role system if the drill adds overhead without preventing a real conflict. |
| 4 | Put an expiry/review trigger and one outcome measure on the next three HPOM conventions. | Toyota’s evolving improvement stance and DORA’s caution against assuming adoption equals improvement. | Review after 30 days: retain only conventions that reduced a named friction without raising review/coordination cost. |
| 5 | Convert one repeatedly manual, deterministic MAP check into a visible self-service command with a stable output contract. | Team Topologies X-as-a-Service; existing MAP validator precedent. | Compare execution/reconstruction time across three uses; revert to documented manual procedure if it creates new state or false confidence. |

## Conclusions

**Source fact:** the models consistently favor clear ownership, temporary
facilitation, visible state, small feedback loops, and stable self-service
interfaces where work is genuinely repeatable.

**MAP inference:** HPOM already has most of the needed authority boundaries.
Its highest-value refinement is an evidence loop for routing and attention—not
more tiers, permanent roles, or autonomous model control.

**Proposal boundary:** run at most one or two candidate experiments at a time,
with a reversible stop rule. Do not promote any experiment into HPOM policy
without an owner-reviewed result showing lower operator interpretation or
coordination cost while preserving MAP’s visible-authority safeguards.
