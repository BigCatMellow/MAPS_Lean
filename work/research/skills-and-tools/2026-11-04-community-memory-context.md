# Community GitHub mechanisms — context, compaction, memory, provenance (2026-11-04)

Status: **RESEARCH — NOT ACTIVE AUTHORITY**. Direct upstream READMEs examined 2026-11-04; implementation claims and project-authored numbers are not independently replicated. Existing owners: MAPS_L context builder, memory-trust classes, information lifecycle, run lineage, and `6.33` retrieval evaluation. Earlier [skills/tools research](2026-09-04-to-2026-09-09-competitive-systems-mechanisms.md) already describes Letta/MCP/A2A; avoid duplicate architecture.

## 1. SLICE (youxi-huang): source-linked compact checkpoints
- Source: https://github.com/youxi-huang/slice (redirect from `pi-context-compaction` verified).
- Mechanism described: compaction output references original session entries; verify references *before* committing the checkpoint; selectively retrieve old source turns.
- MAPS_L comparison: already distinguishes handoff vs source authority and has explicit references; missing test is whether summarization retains a usable **route to primary evidence**.
- Smallest adaptation: reference-integrity check on a compact handoff/context receipt, not a new memory DB. Test interrupted/renamed/deleted source refs, stale decisions, and compaction across task revisions.
- Success: correct original constraint can be recovered without injecting full transcript; absent refs remain UNKNOWN. **TEST FIRST.**

## 2. Pi Smart Compact (alpertarhan): verify before replacing context
- Source: https://github.com/alpertarhan/pi-smart-compact.
- Mechanism described: Extract–Explore–Synthesize–Verify compaction, handoff/checkpoint support, recoverable cleanup, limited deterministic verification; author explicitly says verification cannot prove all semantic truth.
- MAPS_L comparison: current recovery and context already preserve task state but may not detect omitted hard constraints during a context reduction.
- Smallest test: frozen pre/post compaction task packets with required authority/acceptance/forbidden-path anchors; check coverage and retrieval of removed material.
- Caveat: reference validation does not establish semantic completeness. **TEST rather than implement a second summarizer.**

## 3. josephkern/pi-memory: tiny trusted index + deferred detail
- Source: https://github.com/josephkern/pi-memory.
- Mechanism described: separate global/project memory, bounded `MEMORY.md` index, topic files read on demand, archived stale material excluded from injected context, project trust gate and traceable writeback.
- MAPS_L comparison: progressive skill/context loading and trust classes already exist; copying another always-loaded memory file would regress the one-authority rule.
- Extract: evaluate whether **bounded routing pointers** outperform loading full guidance on difficult tasks; test stale and unauthorized project memory.
- Caveat: small extension, no independently established performance advantage. **STUDY/TEST narrow routing index only.**

## 4. Graphiti: temporal validity of knowledge assertions
- Source: https://github.com/getzep/graphiti.
- Mechanism described: dynamically updated entity/relationship graph with temporal information and source provenance.
- MAPS_L comparison: exact-file context and trust classes are stronger than uncontrolled semantic memory, but time-sensitive facts still need tests for supersession and conflicting evidence.
- Extract: small evaluation case where the same fact changes at times T1/T2; retrieval must return current supported fact and trace stale claims to source, without building a graph DB.
- Caveat: entity graph ingestion/hosting overhead and extraction errors; not a default adoption. **TEST temporal contradiction cases.**

## 5. datapace-ai/agent-memory-benchmark: file search is a serious baseline
- Source: https://github.com/datapace-ai/agent-memory-benchmark.
- Upstream describes a common prompt/model/judge for comparing Mem0, Graphiti, LangMem, Cognee and simpler baselines. Its September 2026 **ten-question, single-seed pilot** reported no system surpassing file search.
- MAPS_L implication: **do not assume semantic memory outperforms explicit search**. On a frozen corpus test exact-file retrieval, bounded indices, semantic augmentation, and no-retrieval; score correctness, provenance, stale/conflicting claims, context cost and missing evidence.
- Caveat: ten-question pilot is weak evidence and project-authored. **ADAPT CONTROL DESIGN, not reported ranking.**

## 6. Entelligence agentplay + pacifio Atlas: reconstruct source behind a change
- Sources: https://github.com/Entelligence-AI/agentplay ; https://github.com/pacifio/atlas.
- Described mechanics: import/render multi-provider session timelines (agentplay); Atlas links code checkpoints/commits to source sessions and tool activity, with local redaction.
- MAPS_L comparison: task traces/Run Records exist but may not link the exact external artifact to the execution segment that produced it.
- Extract: test a provenance projection `commit or PR revision -> task/run -> invocation/tool evidence -> review`, with explicit coverage gaps. Prefer read-only derived projection, never a parallel source of task truth.
- Caveat: session traces contain sensitive data; redaction and opt-in are mandatory before any new capture. **TEST with synthetic sanitized traces first.**

## Cross-cutting priority
1. **Source-linked compact handoff + reference-integrity failure tests.**
2. **Temporal stale/contradictory memory hard negatives.**
3. **File-search baseline before expanding semantic retrieval.**
Avoid installing memory servers, automatically promoting retrieved text to authority, or creating a second persistent task store.
