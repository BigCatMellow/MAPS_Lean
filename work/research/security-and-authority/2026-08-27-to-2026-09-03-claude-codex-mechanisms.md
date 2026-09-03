# Claude/Codex security and authority mechanisms — 2026-08-27 through 2026-09-03

Status: `RESEARCH — NOT ACTIVE AUTHORITY`

Purpose: consolidate useful external mechanisms for consequential-action grounding, containment, ambiguous authority, Skill supply-chain review, and safe integration admission.

Related research:
- [Research routing index](../README.md)
- [Harness findings](../agent-harness/2026-08-27-to-2026-09-03-claude-codex-mechanisms.md)
- [Skills/tools findings](../skills-and-tools/2026-08-27-to-2026-09-03-claude-codex-mechanisms.md)
- [Evaluation/reliability findings](../evaluation-and-reliability/2026-08-27-to-2026-09-03-claude-codex-mechanisms.md)

## Executive findings

1. permission is insufficient when the specific value/target can be stale or poisoned;
2. ambiguity in target or blast radius should become an explicit stop state rather than an invitation to guess;
3. containment boundaries generally outperform repeated human approval prompts;
4. untrusted project content must not influence control-plane configuration before trust is established;
5. allowlisted destinations are weaker than capability/provenance-aware controls;
6. Skills require joint review of declared purpose, instructions, and executable behavior;
7. integration inspection should not activate the integration being inspected.

---

## 1. Fresh-value grounding immediately before consequential action

**Source:** ActionRail — https://github.com/ToolJet/ActionRail

**Mechanism:** immediately before execution, validate consequential arguments against the current system of record. Distinguish `may call this action` from `these exact values are currently correct`.

**Problem solved:** an action can be authorized and syntactically valid while containing a stale, poisoned, or wrong customer/account/order/target value.

**Evidence:** project reports red-team testing across eight models/four providers, with manipulated values executing in unprotected runs but 0/480 executing behind the boundary; also reports 0/480 false blocks on legitimate look-alikes. Evidence is project-authored but unusually concrete.

**Failure modes:** grounding can grow into a large policy/database/rules subsystem; the system of record may itself be stale or unavailable.

**MAPS disposition:** `TEST ONE NARROW VALUE BOUNDARY`. Do not build a general grounding platform first.

---

## 2. Ambiguous target/authority becomes unresolved state

**Source:** UnderSpecBench — https://arxiv.org/abs/2607.02294

**Mechanism:** when intent, exact target, or blast radius is materially underspecified, stop before the consequential boundary rather than infer the missing fact.

**Problem solved:** coding/DevOps agents frequently guess under ambiguity.

**Evidence:** across 2,208 prompt variants and five Claude/Codex/OpenCode configurations, authors report 55.8–67.8% of runs violating at least one action boundary under underspecification; target ambiguity was especially harmful.

**Failure modes:** stopping on every minor ambiguity can paralyze useful work; only material boundaries should trigger this state.

**MAPS disposition:** `TEST AS PROOF-PHASE SAFETY SCENARIO`. Passing behavior is recognition of unresolved authority/target, not lucky guessing.

---

## 3. Containment over approval fatigue

**Source:** Anthropic containment engineering — https://www.anthropic.com/engineering/how-we-contain-claude

**Mechanism:** constrain what the agent can physically reach through mature sandbox/filesystem/process/network boundaries instead of relying mainly on repeated human approval prompts.

**Problem solved:** frequent prompts become rubber-stamped and therefore weak security boundaries.

**Evidence:** Anthropic reports users approved about 93% of Claude Code permission prompts and sandboxing reduced prompts by 84%. Official vendor evidence, but useful at mechanism level.

**Failure modes:** sandboxes are imperfect; bespoke containment infrastructure can be weaker than mature OS/hypervisor primitives.

**MAPS disposition:** `STUDY / TURN INTO TESTS`. Prefer existing mature isolation primitives over custom security machinery.

---

## 4. Establish trust before project-local configuration can influence control plane

**Source:** Anthropic containment engineering — https://www.anthropic.com/engineering/how-we-contain-claude

**Mechanism:** do not process untrusted repository-local configuration, hooks, or integrations before the repository trust decision is established.

**Problem solved:** hostile project content can alter startup/control behavior before the user has agreed to trust the project.

**Evidence:** Anthropic documents a real failure class in its containment work.

**Failure modes:** trust prompts can become coarse; some safe metadata may be useful before full trust.

**MAPS disposition:** `ADAPT AS ADVERSARIAL TEST/BOUNDARY RULE` for Portable Deployment.

---

## 5. Destination allowlist is weaker than capability/provenance validation

**Source:** Anthropic containment engineering — https://www.anthropic.com/engineering/how-we-contain-claude

**Mechanism:** validate what capability/credential/provenance is being exercised, not merely whether the network destination/domain is allowlisted.

**Problem solved:** attacker-controlled credentials can use an approved API/domain for exfiltration or unauthorized action.

**Evidence:** documented Anthropic security design change following adversarial testing.

**Failure modes:** provenance-aware policy is more complex than domain allowlists and can become provider-specific.

**MAPS disposition:** `STUDY`; use only where a concrete credential/capability boundary demands it.

---

## 6. Skill supply-chain review must combine purpose + instructions + executable content

**Source:** MalSkillBench — https://github.com/lxyeternal/MalSkillBench and https://arxiv.org/abs/2606.07131

**Mechanism:** judge whether scripts/tool behavior make sense given the Skill's declared purpose and instructions; do not review code and Markdown independently.

**Problem solved:** mixed prompt/code attacks can look benign when each component is inspected alone.

**Evidence:** 3,944 runtime-confirmed malicious and 4,000 benign Skills; strong results for ordinary code injection but weaker prompt/control-plane attacks.

**Failure modes:** a comprehensive new Skill-security stack would duplicate existing MAPS security mechanisms.

**MAPS disposition:** `TEST EXISTING SKILL GATE` with hybrid attack examples; add only the smallest missing mechanism.

---

## 7. Cheap suspicion filter before expensive semantic review

**Source:** Anthropic Claude Code Auto Mode — https://www.anthropic.com/engineering/claude-code-auto-mode

**Mechanism:** first apply a cheap classifier/filter to every action, then use expensive semantic review only for suspicious cases; independently screen incoming tool content for prompt injection.

**Problem solved:** applying the heaviest review to every action is costly and creates approval/review fatigue.

**Evidence:** Anthropic reports large differences between manual review and Auto Mode on disguised harmful actions; vendor evidence, not independent validation.

**Failure modes:** false negatives become less visible when ordinary actions are automatically allowed.

**MAPS disposition:** `ADAPT ESCALATION PRINCIPLE` where MAPS already has cheap deterministic guards plus heavier review. Do not copy Auto Mode itself.

---

## 8. Pre-start policy receipt: inspect without activating

**Source:** OpenAI Codex proposal — https://github.com/openai/codex/issues/42170

**Mechanism:** resolve effective project/integration configuration without starting optional integrations, return a redacted policy/capability receipt, and bind its digest to subsequent execution.

**Problem solved:** inspecting MCP/plugin configuration can itself start servers, perform OAuth discovery, or sync external state before admission is decided; configuration can also change between check and use.

**Evidence:** open architecture proposal rather than implemented benchmark.

**Failure modes:** universal plugin/MCP admission engines would add large complexity; digest binding must define what exactly is frozen versus intentionally live.

**MAPS disposition:** `STUDY FOR PORTABLE DEPLOYMENT`; no implementation until an external pilot needs it.

---

## 9. Shared configuration writes must preserve fields outside actor ownership

**Source:** Codex Desktop config overwrite report — https://github.com/openai/codex/issues/42116

**Mechanism:** mutate only fields the actor owns, preserve unknown/unmanaged fields, and preferably condition writes on the version read.

**Problem solved:** reconstruct-and-replace writes can silently destroy configuration owned by another actor/version.

**Evidence:** concrete user bug report; OpenAI root cause not confirmed.

**Failure modes:** generalized merge frameworks can be overkill for simple config files.

**MAPS disposition:** `ADAPT WRITE-BOUNDARY RULE`; test with unknown sentinel fields where MAPS shares external configuration.

---

## 10. Execution provenance should answer causal forensic questions

**Source:** From Agent Traces to Trust — https://arxiv.org/abs/2606.04990

**Mechanism:** preserve relationships among retrieved evidence, tool outputs, observations, intermediate claims, actions, and conclusions so consequential decisions can be traced to evidence.

**Problem solved:** final-answer correctness and raw logs do not explain why a consequential action was justified.

**Evidence:** academic taxonomy/survey rather than a proof that a large provenance graph improves agent performance.

**Failure modes:** provenance systems can become huge observability projects with little decision value.

**MAPS disposition:** `STUDY TAXONOMY`. Add relationships only when they answer a concrete forensic/review question faster or more reliably.

---

## Complexity warnings

Do not infer that these findings justify:

- another general policy engine;
- a custom sandbox/hypervisor stack;
- a universal integration-admission service;
- continuous semantic review of every action;
- a full provenance graph;
- broad automatic Skill trust based only on repository reputation.

## Highest-value next mechanism tests

1. **Fresh-value grounding:** one authorized action with deliberately stale/wrong target data.
2. **Underspecified-target failure injection:** omit one material target/authority fact and verify MAPS refuses to guess.
3. **Hybrid Skill attack:** plausible instructions + plausible script whose combined behavior is malicious, tested against current MAPS gates.
