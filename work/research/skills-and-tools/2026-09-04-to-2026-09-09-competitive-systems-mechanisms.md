# Competitive systems mechanisms — skills and tools — 2026-09-04 to 2026-09-09

Status: `RESEARCH — NOT ACTIVE AUTHORITY`

Main question: **Which public interface, adapter, tool, and remote-agent mechanisms should MAPS_L reuse or test instead of inventing new protocol/runtime plumbing?**

## Evidence snapshot

Deep extraction owner: `BigCatMellow/Pilot_Projects` PR #5 at `f6d584465e15b0fcf3cd09fea9e056bc23852e94`.

- Source index: https://github.com/BigCatMellow/Pilot_Projects/blob/f6d584465e15b0fcf3cd09fea9e056bc23852e94/complete-ai-work-system/research/competitive-architecture/production-accelerators/SOURCE_INDEX.md
- Protocol packet: https://github.com/BigCatMellow/Pilot_Projects/blob/f6d584465e15b0fcf3cd09fea9e056bc23852e94/complete-ai-work-system/research/competitive-architecture/production-accelerators/P1-AGENT-TOOL-PROTOCOL-INTEROP.md
- Runtime/source manifest: https://github.com/BigCatMellow/Pilot_Projects/blob/f6d584465e15b0fcf3cd09fea9e056bc23852e94/complete-ai-work-system/research/competitive-architecture/production-accelerators/SOURCES.yaml

## Findings that strengthen existing MAPS_L design

### 1. MCP and A2A solve different interoperability jobs

Current protocol evidence supports a clean split:

- **MCP**: expose tools/resources/prompts and invoke capabilities through a client/server interface;
- **A2A**: communicate with opaque remote agents through capability discovery plus stateful Tasks, Messages, and Artifacts.

Neither protocol should become MAPS task authority.

```text
capability advertised by MCP/A2A
!=
permission for this MAPS task/run to use it
```

**MAPS_L implication:** preserve current capability/policy intersection. If external tool servers or remote agents are added, prefer adapting to established protocol semantics instead of creating a MAPS-specific wire protocol unless a measured gap requires one.

Relevant current areas: 6.10 Skill provenance/trust, 6.12 Capability Packs, 6.24 least privilege, 6.35 portable deployment.

### 2. Provider/runtime abstraction should be narrow and post-resolution facts should be inspectable

Optio's adapter interface is small: validate secrets, build execution/container configuration, parse result. Hermes independently separates provider resolution from execution backend selection across local/container/SSH/cloud-style targets.

Taskplane's fix history is a warning: declared reviewer/model/tool configuration did not always reach the actual subprocess. It also consolidated duplicated executable resolution into one canonical resolver.

**MAPS_L implication:** keep adapter/provider contracts small and centralized. For consequential runs, record the **effective** post-resolution runtime facts rather than trusting the requested config.

Candidate evidence fields when useful:

```text
provider/model actually selected
runtime/backend actually selected
resolved executable/version
resolved tool/capability set
credential capability profile
run/task revision
```

This is evidence/trace material, not a new authority manifest by itself.

### 3. Capability discovery and capability grant must stay separate

Several systems expose rich capability metadata, but none of that should imply authorization.

MAPS_L already has the stronger design rule:

```text
available capability
∩ task scope
∩ policy
∩ explicit approvals
∩ environment availability
= effective capability
```

Competitor evidence strengthens that rule rather than replacing it.

### 4. Tool/result protocols need semantic completion, not process-success inference

Taskplane and Optio failures show that:

```text
subprocess exit 0
!=
semantic task/review success
```

Similarly, an agent printing a GitHub PR URL is not proof the PR exists or is the expected artifact.

**MAPS_L implication:** bounded structured results and target-system verification remain preferable to parsing agent prose for completion. This supports current normalized ACI/result work and review-evidence discipline.

### 5. Letta V2 offers one useful memory-as-files pattern, but not memory authority

Current Letta source moved to `letta-ai/letta-code`. Its ordinary memory writer uses Git-backed Markdown with commit-at-write provenance. Clean concurrent committed changes can converge through non-fast-forward detection -> rebase -> retry; textual conflicts stop explicitly.

Useful property:

```text
inspectable memory change history
+
ordinary Git conflict semantics
```

Insufficient property:

```text
clean textual merge
== semantic agreement / authority
```

**MAPS_L implication:** if MAPS later chooses Git-backed project/working memory for #247, Letta provides implementation prior art for inspectable provenance and optimistic convergence. Promotion/trust still belongs to MAPS.

## Portable regression cases worth importing

1. configured reviewer/model X -> spawned subprocess uses Y -> evidence must expose mismatch;
2. resolver logic differs across worker/reviewer/recovery -> one canonical resolver test fails until unified;
3. agent prints plausible PR URL but external GitHub object does not exist -> completion rejected/unknown;
4. tool server advertises dangerous write capability -> discovery alone does not put it in the run's effective grant;
5. remote A2A agent advertises skill/capability -> MAPS still checks local task/policy before delegation;
6. MCP/A2A disconnect after accepted operation -> caller does not infer absence of effect from transport failure;
7. compatible Git-backed memory edits from two writers -> rebase/retry can converge;
8. conflicting Git-backed memory edits -> explicit conflict, no silent semantic merge/promotion.

## Disposition

`STRENGTHEN_EXISTING_OWNER`.

Prefer established MCP/A2A and narrow adapter/resolver patterns where they fit. Do not add a new MAPS protocol, capability authority, or memory authority merely because upstream systems expose one.