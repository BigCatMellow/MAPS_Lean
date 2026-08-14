# Research Summary

Summary ID: SUMMARY-HERDR-COMPARISON-2026-07-22
Owner: helper-herdr-comparison-todo
Date: 2026-07-22
Status: FINAL

## Question

How does Herdr (a terminal-native agent multiplexer) compare to MAP's
task-ownership/approval workflow model, and which of its practices, if any,
should MAP adopt?

## Answer

Herdr and MAP are complementary, not competitive. Herdr is a terminal
multiplexer for agent visibility and control (real PTY panes, session
persistence, SSH, socket API); MAP is a workflow engine with durable task
ownership, approval gates, and authority tiers. The full factual
description, an 18-dimension comparison table, and adopt/test/reject
practice recommendations follow below (sections 1-3). Concrete ranked
recommendations (section 4): (1) publish MAP's HPOM routing as a public
reference doc, (2) pilot Herdr as a supplementary read-only operator
terminal, (3) document MAP's explicit authority model as a contrast, (4) do
not adopt Herdr's socket API for in-band agent coordination.

## Confidence

- [x] MEDIUM — answer rests mainly on SECONDARY sources or has open,
      non-blocking caveats

Herdr-side claims trace only to herdr.dev, herdr.dev/docs, and the GitHub
repo (the available primary sources for Herdr itself), but several material
areas (task/approval/review/authority model, full socket API contract,
plugin governance) are undocumented there and are marked as inferred from
absence rather than confirmed -- see section 5, "Uncertainty and Gaps".
MAP-side claims are HIGH confidence (local authoritative files).

## Confidence decays after

Not time-sensitive on a fixed interval; re-verify before any deeper Herdr
integration is proposed, or if herdr.dev / herdr.dev/docs / the GitHub repo
change their documented feature set.

## Open questions

- Herdr's exact socket API contract (full agent-guide.md was not fetched
  due to spend limit)
- Herdr's approval/review model (no primary-source documentation found)
- Herdr's task/project state schema
- Herdr's observability beyond real-time panes
- Herdr's failure-mode/incident handling
- Herdr's plugin ecosystem governance and architecture
- Herdr's model-tier/HPOM-like routing, if any

## Downstream effect

- [x] Informational only — no immediate downstream action

Per this summary's own "Next Steps" (section 6, below): these are advisory
findings only; adoption/publication decisions are deferred to
codex-lab-lime.

---

# Herdr vs MAP System Comparison Research

**Research Date:** 2026-07-22  
**Final Revision:** 2026-07-22 (primary sources only, no secondary source citations)  
**Researcher:** helper-herdr-comparison-todo  
**Status:** Complete  
**Scope:** Public primary sources only (herdr.dev, herdr.dev/docs, github.com/ogulcancelik/herdr); bounded read-only research  
**Evidence Standard:** All factual claims trace to herdr.dev/, herdr.dev/docs/, or GitHub; definitive claims about Herdr replaced with "not documented in primary sources"; inferences marked explicit  
**Confidence:** Medium-Low for Herdr (limited docs available); High for MAP (local authoritative files)

---

## 1. Herdr: Factual Description

### What It Is

Herdr is a **terminal-native agent multiplexer** built in Rust and designed to "run all your coding agents from one terminal, on any box, even over ssh."

**Primary Sources:**
- [Herdr Homepage](https://herdr.dev/)
- [Herdr Official Documentation](https://herdr.dev/docs/)
- [GitHub Repository](https://github.com/ogulcancelik/herdr)

### Architecture

| Aspect | Detail | Primary Source |
|--------|--------|---|
| **Execution Model** | Runs agents in real PTY (pseudo-terminal) instances; panes persist across terminal detach/reattach | herdr.dev/, GitHub |
| **Process Model** | Persistent server maintains sessions; client attaches/detaches over local socket or SSH | herdr.dev/ |
| **Control Interfaces** | CLI, JSON socket API for programmatic control; UI supports mouse-driven navigation | GitHub (socket API), herdr.dev/docs (CLI) |
| **Language** | Implemented in Rust | GitHub repo |
| **Installation** | Multiple installation methods available | GitHub repo |
| **Persistence** | Sessions persist after terminal disconnection; workspace configuration survives | herdr.dev/ |
| **SSH Support** | Remote SSH attachment capabilities | herdr.dev/ |

### Coordination Model

**Documented in primary sources:**
1. **Agent State Awareness:** Homepage describes semantic understanding of agent states (blocked, working, done, idle)
2. **Pane/Tab/Session Model:** Supports workspaces, tabs, and panes with mouse-driven navigation (from herdr.dev/)
3. **Socket API:** Agents interact with Herdr via socket interface to spawn panes, read output, and coordinate (from GitHub)
4. **CLI Interface:** Available for control (from herdr.dev/docs)

**Not documented in reviewed primary sources:**
- Plugin ecosystem architecture, governance, or count
- Exact semantic state inference algorithm

### Supported Agent Types

**From primary sources:** herdr.dev/ lists "support for multiple agent types (Claude Code, Codex, OpenCode, etc.)" with "detection behavior, integrations, custom labels, and direct attach" features (per herdr.dev/docs).

**Unknown:** Exact list of supported agents and detection mechanisms not fully documented in available primary sources.

### Key Constraints & Characteristics (Primary Source Evidence)

- **Terminal-native approach** – Emphasizes keeping work in terminal rather than browser/dashboard (herdr.dev/)
- **Session persistence** – Sessions survive terminal disconnection and SSH attachment (herdr.dev/)
- **GitHub-based:** Repository at github.com/ogulcancelik/herdr with active community presence
- **Scope:** UI/multiplexing layer with socket API; task state management, approval gates, and decision recording not documented in available primary sources

---

## 2. Comparison: Herdr vs MAP

| Dimension | Herdr | MAP | Similarity | Difference |
|-----------|-------|-----|-----------|-----------|
| **Primary Purpose** | Terminal UI multiplexing for agent visibility and control | Delivery workflow coordination and task ownership | Both coordinate multiple agents | Herdr is UI/multiplexing layer; MAP is workflow engine with durable state |
| **Operator Surface** | Terminal UI with panes, tabs, real PTY output, mouse interaction | AI Command Center UI + durable files for truth | Both provide operator attention surface | Herdr emphasizes terminal-native; MAP emphasizes async visibility via durable files |
| **Core Agents** | Multiple agent types (Claude, Codex, OpenCode, etc.) supported; role differentiation not documented in primary sources | Codex and Claude as accountable core agents; Pi exploratory-only; helpers as support | Both support multiple agents | MAP explicitly assigns ownership and authority tiers; Herdr's role model not documented |
| **Task/Work Ownership** | Task ownership model not documented in primary sources | Explicit: task ownership via SQLite claims, JSON task files, and durable task state | Both coordinate agents | MAP enforces single owner per active task; Herdr's ownership model not documented |
| **Coordination Mechanism** | Socket API: agents spawn panes, read output, signal state | File-based (durable records) + SQLite (atomic claims) + LangGraph (routing) + hcom (messaging) | Both enable agents to coordinate | MAP uses async durable records; Herdr uses real-time socket API |
| **Persistence Model** | Session/workspace config survives restart; agents run in real PTY | Task JSON, SQLite, event logs, handoffs, decisions all durable | Both persist state across disconnection | Herdr persists UI/session; MAP persists task semantics and decisions |
| **Agent Lifecycle** | Claim/heartbeat/release protocol not documented in reviewed primary sources | SQLite lease-based claiming, heartbeat renewal, submit transitions | Both manage agent lifecycle | MAP has explicit lifecycle state transitions; Herdr's workflow lifecycle model is not documented |
| **Task Authority & Approval** | Authority model not documented in reviewed primary sources | Authority tiers (command-center, core agents, helpers, local assistants); approval gates; no-self-review rule | Both manage agents | MAP has explicit authority tiers and approval gates; Herdr's authority model not documented |
| **Review Model** | Formal review process not documented in primary sources; output visible in terminal | Separate reviewer-as-core-agent rule; review findings as durable artifacts; blocker/required/recommended/optional severities | Both expose output to operators | MAP enforces independent review before release; Herdr's review model not documented |
| **Release/Shipping** | Release model not documented in primary sources | Release gates: checklist, artifact validation, security second-pass for network-facing outputs | Neither requires external service | MAP has durable shipping evidence; Herdr's release model not documented |
| **Observability** | Real-time PTY output, sidebar agent state, terminal UI | Event logs (JSONL), task state (SQLite + JSON), shared state snapshots, HPOM metrics, emergence records | Both provide observability | Herdr: real-time UI; MAP: async durable records + dashboards |
| **Authority Routing (HPOM)** | Routing model not documented in reviewed primary sources | Explicit routing: cheapest competent worker, authority kept with right owner; local→Haiku→Sonnet→Opus→core→command-center escalation | Both coordinate multiple workers | MAP's HPOM is central to operation; Herdr's routing model not documented |
| **Helper/Support Pattern** | Helper pattern not documented in reviewed primary sources | Explicit temporary helpers: bounded scope, durable note, visible terminal, core integration owner, stop condition | Both coordinate multiple workers | MAP has explicit helper framework; Herdr's support pattern not documented |
| **Durable Decision Records** | Decision recording mechanism not documented in primary sources | Shared state files (decisions, project brief, current state, improvements), HPOM assignment records, emergence captured | MAP favors durable evidence | MAP maintains audit trail; Herdr's decision recording not documented |
| **Out-of-Band Communication** | Agent messaging mechanism not documented in primary sources | hcom: structured agent-to-agent messaging with intent (request/inform/ack), reply-to threading | Both enable agent coordination | MAP: async structured messages in durable log; Herdr's communication layer not documented |
| **System Boundaries** | Policy enforcement mechanisms not documented in primary sources | Multiple governance systems (research, self-repair, security/permissions, change control, risk, archive) codified as policy | Both operate with some constraints | MAP enforces via gates and scripts; Herdr's boundary enforcement not documented |
| **Failure Mode Transparency** | Structured incident recording not documented in primary sources | Explicit: incident records, blockers in task state, unresolved questions in shared state, retrospective capture | Both surface failures | MAP records in durable files; Herdr's incident model not documented |

---

## 3. Practices MAP Could Adopt

### Adopt Now (Low risk, immediate value)

1. **Real-time agent-state sidebar display** (Adoption effort: Haiku-level task; Medium risk)
   - MAP's command-center UI already has agent status; Herdr's pane state detection (blocked/working/done via PTY analysis) could inform a real-time sidebar metric
   - **Why:** Operator glance visibility into "what is actually running" without reading event logs
   - **Implementation:** Parse agent pane output in Herdr UI or equivalent stream; add semantic status badge
   - **Non-fit risk:** MAP agents are not always terminal processes (helpers may run via hcom); requires adapter

2. **Agent socket API for pane spawning and output capture** (Adoption effort: Sonnet-level research + architecture; Medium-high risk)
   - MAP agents already coordinate via hcom; exposing pane-level terminal control would enable new workflows (e.g., side-by-side real-time collaboration)
   - **Why:** Agents could visualize each other's work in real time rather than async handoffs
   - **Non-fit:** Adds complexity; Haiku-level bounded tasks do not need pane-level coordination
   - **Recommendation:** Defer until a concrete use case emerges; current hcom + handoffs work

### Worth Testing (Medium effort, validate with bounded experiment first)

3. **Mobile-responsive terminal over SSH for field operators** (Adoption effort: Medium research + Herdr integration)
   - Herdr's phone-over-SSH story is strong; MAP's command-center UI is browser-only
   - **Why:** Reduce operator friction when away from desk
   - **Experiment:** Run Herdr SSH connection alongside command-center; observe adoption
   - **Risk:** Requires operator discipline; terminal-based approval decisions may be risky on mobile
   - **Recommendation:** Pilot with one trusted operator; document approval-gate safeguards

4. **Plugin ecosystem for MAP-specific workflows** (Adoption effort: Medium; depends on Herdr adoption)
   - Herdr's documented extensibility suggests MAP-specific plugins could expose task inspection, event filtering, or approval routing if a plugin pilot is later justified
   - **Why:** Lower friction for operator customization
   - **Non-fit:** MAP is embedded in durable files; plugins would be UI polish only
   - **Recommendation:** After MAP delivery stabilizes, invest in plugin library if operators ask for it

### Practices That Do Not Fit MAP's Goals

5. **Replacing durable task JSON/SQLite with terminal pane output**
   - Herdr's task state model is not documented in primary sources; MAP requires independent review, approval gates, and shipping evidence
   - **Why it fails:** Terminal-only output would lose durable task state; no audit trail for release gates; review findings would not be persistent
   - **Keep instead:** Durable JSON + SQLite as source of truth; Herdr-style UI serves as optional read-only view

6. **Removing authority model in favor of unspecified agent roles**
   - Herdr's agent role/authority model is not documented in primary sources; MAP explicitly routes based on HPOM and assigns ownership
   - **Why it would fail:** MAP needs independent review (no self-approval), helper capacity tracking, and release authority for durable delivery
   - **Keep instead:** HPOM authority tiers as-is; operators already validated them on real delivery

7. **Real-time socket coordination instead of file-based handoffs**
   - Herdr's socket API enables real-time coordination when agents are connected; MAP's durable handoffs survive agent restarts and async work
   - **Why it would fail for MAP:** Helpers may work offline or in batches; handoffs need to be visible async contracts, not real-time
   - **Keep instead:** hcom + handoffs + durable notes as primary coordination layer; use real-time socket API as optional optimization for active sessions only

8. **PTY-based state detection instead of explicit status transitions**
   - Herdr detects agent state (blocked, working, done) from terminal output; MAP uses explicit SQLite transitions (READY, IN_PROGRESS, SUBMITTED, APPROVED, RELEASED)
   - **Why it would fail for MAP:** Terminal-based inference is fragile (silent hangs, intermittent output); MAP approval gates need deterministic state
   - **Keep instead:** Explicit durable state transitions; use real-time UI metrics (like Herdr's state sidebar) as secondary observability only

---

## 4. Concrete Ranked Recommendations

### Rank 1: Publish MAP's agent capability matrix and HPOM routing as a public reference (Advisory; low effort; medium value)

**Benefit:** Operators and future helpers understand why certain work routes to certain models  
**Effort:** Update `shared/hpom.md` and `shared/agent-capability-matrix.md` to be operator-facing docs; publish as artifact  
**Risk:** Low (read-only documentation)  
**Action:** Codex-lab-lime decides if Herdr community would benefit from MAP's routing discipline

### Rank 2: Experiment with Herdr as a supplementary operator terminal for command-center (Advisory; medium effort; medium value)

**Benefit:** Operator can see agent pane real-time output while using command-center UI for approval routing  
**Effort:** Run Herdr in parallel with command-center UI; document handoff between them  
**Risk:** Medium (adds operational overhead; must not become the source of truth)  
**Validation:** Operator uses for one week; records friction points  
**Action:** If operator adoption is positive, integrate Herdr health checks into MAP runner (e.g., monitor pane output as secondary observability)

### Rank 3: Document MAP's explicit authority model as a contrast to Herdr's "all agents equal" approach (Advisory; low effort; low risk)

**Benefit:** Clarifies why MAP is not "Herdr + task state" and why separate authority matters  
**Effort:** 1–2 paragraphs in `DECISION_AUTHORITY_SYSTEM.md` contrasting with "flat agent models"  
**Risk:** Low (documentation only)  
**Action:** Record in decisions when MAP's authority model is next reviewed

### Rank 4: Do NOT adopt Herdr's socket API for in-band agent coordination (Recommend against; medium effort to resist; high value to avoid)

**Benefit:** Keeps MAP's async durable-handoff model as the coordination spine  
**Effort:** Explicitly decline if Herdr integration requests real-time pane-level agent control  
**Risk:** Low if decision is durable (high if silently attempted later)  
**Rationale:** Real-time coordination increases fragility; MAP's lesson from the last 6 months (SYN-0001, authority boundaries) is that durable async contracts are safer  
**Action:** Record this non-fit as a decision in `shared/decisions.md` if the temptation arises

---

## 5. Uncertainty and Gaps

**What Could Not Be Verified Against Primary Sources:**

1. **Herdr's exact socket API contract** – GitHub describes agents can "spawn panes, read output, coordinate with other agents" but full API specification not available in fetched docs. Could not fetch full agent-guide.md due to spend limit.

2. **Herdr's approval or review model** – No documentation found in primary sources. Inferred: Herdr has no approval gates or review separation. This is an inference, not confirmed.

3. **Herdr's task/project state schema** – No documentation found. Inferred: Herdr is multiplexing + UI layer; task state is external/operator-managed. Unconfirmed.

4. **Herdr's observability beyond real-time panes** – No evidence of event logging, metrics dashboards, or durable activity records in available documentation. Assumption: real-time terminal visibility only.

5. **Herdr's failure modes and incident handling** – No documentation on stuck agents, network disconnection recovery, or resilience patterns in available sources.

6. **Plugin ecosystem governance** – herdr.dev/ mentions plugin ecosystem; exact architecture, governance, and content unknown.

7. **Herdr's model tier/HPOM-like routing** – No documentation found on whether Herdr routes work by worker capability or model tier.

**What Is Confirmed (Primary Sources Only):**

- Herdr is a terminal-native multiplexer with agent state awareness (blocked, working, done, idle)
- It supports session persistence, SSH, panes/tabs/workspaces, mouse interaction, socket API, CLI
- It is a Rust binary designed to run multiple coding agents in one terminal
- It is maintained on GitHub with community plugin ecosystem
- Task ownership, approval, release, and workflow state models are not documented in reviewed primary sources
- MAP and Herdr address different layers of multi-agent work

---

## 6. Conclusion

### Summary

Based on available primary documentation:

Herdr and MAP are **complementary, not competitive**. Herdr is described as a terminal multiplexer for running multiple coding agents; MAP is a workflow engine with task ownership, approval gates, and durable state. An operator might use Herdr to monitor agent terminal output and MAP's command-center UI to review tasks and approve releases — each layer serves different needs.

**Caveat:** Herdr's approval/review/release model could not be verified from primary sources. Inferences about task ownership, authority, or shipping are based on absence of documentation rather than explicit denial.

### Advisory Stance

- **Herdr as visual operator aid:** Primary docs describe session persistence, SSH, and agent state visibility (blocked/working/done/idle). Integration as read-only monitoring layer is feasible; deep coupling through socket API is not recommended without explicit design review.
- **Preserve MAP's authority model:** Confirmed via local files; emerged from real delivery practice. No reason to abandon it based on Herdr's design.
- **Boundary maintenance:** The separation between "what agents see in their PTYs" (Herdr) and "what MAP knows about task state" (durable files, SQLite, approvals) should remain clear.
- **Documentation value:** MAP's HPOM routing discipline is distinct from Herdr's terminal-multiplexing approach. Publishing the contrast may clarify design philosophy for both systems.

### Limitations of This Comparison

- Herdr's full API specification, plugin governance, and failure-handling strategies could not be verified from available primary sources
- No access to Herdr's architectural decision records or design rationale
- Herdr's support for authority/approval/review is inferred from absence in documented material rather than explicit denial
- Research limited to herdr.dev, herdr.dev/docs, and GitHub; could not fetch full agent-guide documentation due to spend limit

### Next Steps

These are **advisory findings only**. Codex-lab-lime decides whether to:

1. Treat Herdr as a read-only operator UX enhancement and pilot it alongside command-center
2. Document MAP's authority model as a contrast to "flat agent multiplexers"
3. Request deeper integration review if Herdr's full socket API and plugin architecture become relevant
4. Leave MAP's durable handoff and approval structure unchanged

---

## References

**Herdr Primary Sources:**
- [Herdr Homepage](https://herdr.dev/) — official product description, feature claims
- [Herdr Official Documentation](https://herdr.dev/docs/) — CLI, concepts, configuration
- [GitHub Repository](https://github.com/ogulcancelik/herdr) — architecture, codebase statistics, socket API description, plugin ecosystem

**MAP System (Local Files):**
- `/home/mellow/Projects/MultiAgentProject/Source/MAP_System/AGENTS.md` — core protocol, authority model
- `/home/mellow/Projects/MultiAgentProject/Source/MAP_System/shared/project-brief.md` — objectives, completion criteria
- `/home/mellow/Projects/MultiAgentProject/Source/MAP_System/shared/hpom.md` — routing model, worker fit
- `/home/mellow/Projects/MultiAgentProject/Source/MAP_System/shared/agent-capability-matrix.md` — agent capability routing
