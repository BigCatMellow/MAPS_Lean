# Claude/Codex skills, MCP, and tool-interface mechanisms — 2026-08-27 through 2026-09-03

Status: `RESEARCH — NOT ACTIVE AUTHORITY`

Purpose: consolidate useful external mechanisms related to Skills, MCP/tool interfaces, capability packaging, retrieval, and provider portability.

Related research:
- [Research routing index](../README.md)
- [Harness findings](../agent-harness/2026-08-27-to-2026-09-03-claude-codex-mechanisms.md)
- [Evaluation/reliability findings](../evaluation-and-reliability/2026-08-27-to-2026-09-03-claude-codex-mechanisms.md)
- [Security/authority findings](../security-and-authority/2026-08-27-to-2026-09-03-claude-codex-mechanisms.md)

## Executive findings

1. tool capability can remain rich while the model-facing surface stays small;
2. provider-neutral workflow guidance must travel with the capability, not live only in one provider's Skill system;
3. retrieval units should match information structure and current evidence type;
4. tool outputs should expose the minimum sufficient representation and withhold irrelevant sensitive data;
5. canonical semantic contracts should be provider-neutral, with provider quirks isolated in adapters;
6. Skills should earn promotion through measured benefit rather than accumulate by default.

---

## 1. Smaller model-facing tool surfaces

**Source:** agent-memory-mcp — https://github.com/ipiton/agent-memory-mcp

**Mechanism:** collapse many narrow operations into a few coherent capability groups while preserving underlying functionality.

**Problem solved:** large MCP/tool catalogs consume context and increase wrong-tool selection.

**Evidence:** project reports reducing roughly 41 exposed tools to about eight grouped meta-tools and about 42% less schema payload; project-authored evidence only.

**Failure modes:** a giant `action=` union can merely move ambiguity inside one tool. Group only operations that genuinely share semantics and authority.

**MAPS disposition:** `TEST INTERFACE PRINCIPLE`; do not install another memory MCP server.

---

## 2. Provider-neutral workflow card + on-demand help

**Source:** agent-device MCP redesign — https://github.com/callstack/agent-device/pull/1839

**Mechanism:** ship a compact universal operating contract through the capability interface itself, then expose deeper procedure on demand from one shared source.

**Problem solved:** Claude may know how to use a capability through a native Skill while Codex/MCP-only clients see only schemas and therefore miss required procedure.

**Evidence:** real portability failure drove the redesign; review also caught false claims where CLI-only operations were incorrectly presented as MCP tools.

**Failure modes:** duplicated help sources drift; overlong startup cards recreate prompt bloat.

**MAPS disposition:** `ADAPT PRINCIPLE`. For any portable capability, test whether fresh Claude and Codex agents can both discover the minimum operating contract without provider-specific hidden knowledge.

---

## 3. One semantic contract; provider encoding at the edge

**Sources:**
- tool-schema — https://github.com/slegarraga/tool-schema
- toolschema — https://github.com/false200/toolschema

**Mechanism:** maintain one canonical tool meaning/schema, then translate into OpenAI/Anthropic/MCP/runtime-specific representations at adapters.

**Problem solved:** parallel provider-specific schemas silently drift.

**Evidence:** multiple independent community libraries converge on this pattern; OpenHands has had real schema-conversion failures where wrappers exposed the wrong input shape.

**Failure modes:** a schema compiler is unnecessary infrastructure if MAPS has only a few provider-specific tools.

**MAPS disposition:** `STUDY BOUNDARY RULE`; likely ignore the libraries until actual cross-provider schema emission is needed.

---

## 4. Retrieval unit should match code structure

**Source:** jCodeMunch — https://github.com/jgravelle/jcodemunch-mcp

**Mechanism:** index code structurally using syntax trees and retrieve symbols, definitions, references, file outlines, or narrow source regions rather than whole files by default.

**Problem solved:** semantic/whole-file retrieval often overfeeds context and obscures the exact unit of code relevant to the task.

**Evidence:** project-authored benchmarks report large token reductions, including examples around 7,500 to 1,449 tokens; not sufficient evidence of better end-task correctness by itself.

**Failure modes:** indexing daemon/cache complexity; token savings can fail to translate into task-quality gains.

**MAPS disposition:** `TEST` against ordinary grep/read/navigation on a real unfamiliar repository before adding indexing infrastructure.

---

## 5. Retrieval strategy should depend on available evidence

**Source:** Agent Retrieval Bench — https://github.com/eyuansu62/agent-retrieval-bench and https://arxiv.org/abs/2607.24882

**Mechanism:** choose retrieval strategy based on evidence type: failure trace, known symbol, review comment, anchored edit, broad concept, etc.

**Problem solved:** no single retrieval method dominates across repository tasks.

**Evidence:** benchmark of 427 cases across 25 repositories and about 392,000 files found different winners for different task types; agent trajectories missed all gold files in roughly 27–35% of samples.

**Failure modes:** routing among too many retrieval methods can become its own complexity layer.

**MAPS disposition:** `ADAPT PRINCIPLE`; measure MAPS retrieval failures before adding vector/graph infrastructure.

---

## 6. Minimum sufficient tool representation + pre-model redaction

**Source:** Oculo — https://github.com/xidik12/oculo

**Mechanism:** transform environment state into a compact task-relevant representation before exposing it to the model; remove secrets/PII before model context.

**Problem solved:** raw DOM/environment output is noisy and may expose data the model does not need.

**Evidence:** project reports compact page descriptions and low token counts; security architecture is visible in implementation, but performance claims are project-authored.

**Failure modes:** overcompression can hide a detail needed for correct reasoning.

**MAPS disposition:** `STUDY / ADAPT AS TOOL-OUTPUT GUIDANCE`; no need for another browser.

---

## 7. Skills should be promoted by measured marginal value

**Sources:**
- SWE-Skills-Bench — https://github.com/GeniusHTX/SWE-Skills-Bench
- paper — https://arxiv.org/abs/2603.15401

**Mechanism:** paired evaluation of the same task with and without the relevant Skill.

**Problem solved:** a Skill can look useful while adding context cost, stale guidance, or no behavioral benefit.

**Evidence:** 49 public software-engineering Skills; 39 produced zero pass-rate improvement, average gain about +1.2 points, some raised token use by up to 451%, while a small number of specialized Skills produced meaningful gains and several reduced performance.

**Failure modes:** benchmark task mismatch can undervalue procedural knowledge used in other environments.

**MAPS disposition:** `ADAPT AS PROMOTION GATE`. Distinguish exists, trusted, applicable, and demonstrably helpful.

---

## 8. Skills are hybrid instruction + executable supply-chain objects

**Source:** MalSkillBench — https://github.com/lxyeternal/MalSkillBench and https://arxiv.org/abs/2606.07131

**Mechanism:** review Skill instructions, scripts/executable content, and declared purpose together rather than independently.

**Problem solved:** some malicious behavior emerges only from the interaction of plausible Markdown and plausible code.

**Evidence:** benchmark includes 3,944 runtime-confirmed malicious and 4,000 benign Skills; specialized detection performs strongly on ordinary code injection but weaker on prompt/control-plane attacks.

**Failure modes:** building a full new Skill-security platform duplicates scanners, sandboxing, provenance, and policy systems.

**MAPS disposition:** `TEST EXISTING GATE` with hybrid examples; add only the smallest missing check if failures appear.

---

## 9. Skill/procedure portability through shared folders

**Sources:**
- dot-agents — https://github.com/joelhooks/dot-agents
- official Agent Skills ecosystem across Claude/Codex implementations

**Mechanism:** keep provider-neutral procedural knowledge in simple shared filesystem packages and map/symlink into provider-specific discovery paths.

**Problem solved:** duplicating nearly identical procedural instructions for each agent runtime.

**Evidence:** ecosystem convergence rather than controlled benchmark evidence.

**Failure modes:** provider-specific semantics can be hidden behind supposedly neutral Skills; shared packages can spread stale guidance broadly.

**MAPS disposition:** `STUDY / USE OPEN FORMAT WHERE FIT`. Do not build another Skill package manager.

---

## 10. Capability description should not imply activation

**Source:** Codex lazy MCP startup proposal and pre-start policy discussions, including https://github.com/openai/codex/issues/42170

**Mechanism:** allow a controller to inspect configured integrations/capability metadata without starting every server or exercising the capability.

**Problem solved:** discovery itself can trigger network/OAuth/plugin side effects before admission policy is decided.

**Failure modes:** keeping metadata fresh without activation can be difficult; configuration can change after inspection.

**MAPS disposition:** `STUDY`; bind inspected state to later execution if this becomes a real portability need.

---

## Complexity warnings

Do not infer that these findings justify:

- a universal vector database;
- another MCP server just for memory/retrieval;
- a large Skill marketplace or package manager;
- a schema compiler before MAPS has schema-drift failures;
- exposing every provider capability through one giant meta-tool.

## Highest-value next mechanism tests

1. **Skill ablation:** same model/task/harness with and without one MAPS Skill.
2. **Provider-neutral capability discovery:** fresh Claude and Codex agents use the same capability without hidden provider-specific procedure.
3. **Retrieval-unit ablation:** ordinary repository navigation versus symbol/evidence-aware retrieval on one real task.
