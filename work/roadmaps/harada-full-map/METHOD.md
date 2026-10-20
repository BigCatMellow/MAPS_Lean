# Method: recursive success-condition mapping, not fixed file count

- **Record:** planning methodology and rules for *this* candidate full roadmap
- **Status:** proposal, not globally adopted MAPS_L policy or validated THINK/PLAN runtime
- **Entry:** [Full MAPS_L goal](README.md) · [Coverage](COVERAGE.md) · [Execution sequence](WAVES.md)
- **Harada grounding:** [Pilot method research](https://github.com/BigCatMellow/Pilot_Projects/blob/main/harada-method/RESEARCH.md). Original Open Window 64 is a finite 8-domain/8-action brainstorming form; *unbounded recursive goal decomposition* is our untested adaptation.

## One recursive question

At any node **G**, ask: *What materially must be true for G's externally observable outcome and safety conditions to hold?*

For each resulting necessary condition **G.n**:

1. State **why** it is necessary, or mark it optional/enabling rather than silently making it compulsory.
2. Identify current evidence: \`EVIDENCED\` (code + verified relevant proof), \`PARTIAL\` (real mechanism, insufficient integration), \`UNKNOWN\`, \`UNMET\`, \`TRIGGERED\`, \`NOT REQUIRED\`.
3. State observable DONE and the least costly discriminating test.
4. Identify capability, data, scope/authority, environment, external prerequisites and cross-branch dependencies **by link**.
5. Diagnose the missing condition: **decompose**, **inspect/test**, **reuse**, **repair**, **replan**, **return to THINK**, **escalate permission** or **stop**.
6. Only further decompose the affected condition if it remains materially untestable/coarse. Repeat with *no arbitrary depth or fan-out limit*.
7. Stop at an actionable/inspectable leaf, a valid unknown needing investigation, a genuine external human boundary, or already proven DONE. Do not manufacture descendant work.

Logical depth and physical file depth are independent. \`H04.3.2.2\` can live in \`branches/H04.3-recovery.md\`; it does **not** require four directory levels. Branches are split into files when independent navigation, evidence, or editing justifies a distinct information owner. Tiny leaves stay in parent files.

## File and identity conventions for this roadmap

- \`README.md\` is the *single entry/index* with a direct file link to each major and deep branch (one-hop navigation).
- \`H01\`–\`H09\` are **stable logical goal identifiers**, not ordered task ranks or GitHub issue IDs. Their numerical labels can survive changed priority; don't renumber nodes because a task moved.
- \`Hxx.y\` children inherit the parent's goal and cannot widen the accepted scope/permission envelope.
- A parent file lists the direct child and *links* to a larger child file; the child owns its actual detailed requirements and evidence. Do not maintain duplicate normative definitions.
- \`DEPENDENCIES.md\` owns cross-branch "requires" edges; cross-branch references in branches are read-only pointers. No duplicated children, duplicate "task databases," or circular required edges.
- \`COVERAGE.md\` is a dated **derived crosswalk**, not an editable live status ledger; all 45 old milestones and 35 master capability areas remain traceable.
- \`WAVES.md\` owns proposed work order, eligibility and phase gates; no branch file independently promises scheduling or promotion.
- Other original detailed roadmaps stay the implementation-design owners. \`AGENTS.md\`, approved roadmap/task scope, code and live canonical state outrank this research.

### Sample targeted navigation

**Question:** "Why does an incompatible worker resume?" → [H04.3 recovery](branches/H04.3-recovery.md), especially \`H04.3.2.2\`; then read [H06.3](branches/H06.3-consequential-actions.md) if it exercises a policy boundary, and consult exact source tests. There is no need to read all nine branches.

**Question:** "Do we need semantic retrieval?" → [H05.5](branches/H05-knowledge.md); if no experimental trigger/evidence, record TRIGGERED and stop. Do **not** create a semantic-search implementation task from its existence on the roadmap.

## The THINK → PLAN → MAPS_L interface

\`\`\`text
HUMAN APPROVED OBJECTIVE + CANONICAL MAPS_L STATE
  → THINK-style challenge: what success condition might be missing? alternatives?
  → selective recursive condition exploration / evidence labels
  → PLAN-style diagnosis: already actionable vs insufficient, blocked or invalid
  → minimum first-wave accepted task contracts (not duplicate task state)
  → MAPS_L execution, deterministic policy, reviews and evidence
  → desired versus observed state reconciliation
        same valid strategy: repair/replan through PLAN
        strategy invalid: return to THINK
        new scope/permission: human
        all proof met: stop
\`\`\`

Neither the Harada-inspired adaptation nor Pilot PLAN's candidate decomposition has demonstrated production superiority. The review of this roadmap should compare omission detection, clarity, decision value, navigation cost, irrelevant work and safety/authority errors against MAPS_L's existing [Project Bootstrap](../../playbook/PROJECT_BOOTSTRAP.md). Adoption may legitimately be \`NO CHANGE\`.

## Minimal node contract

The normal branch file should answer **parent and observable purpose; present evidence; necessary children; proof of DONE; material cross-branch dependencies; near-term diagnostic or action; boundary/stop**. Add no formal schema, JSON node database, permanent index generator or elaborate lifecycle until retrieval/maintenance measurements warrant one.

Review for infinite recursive loops: each additional depth must resolve a *new distinct ambiguity* rather than restate an ancestor. No automatic planning method decides it is authorized to spend, merge, deploy or approve its own output.
