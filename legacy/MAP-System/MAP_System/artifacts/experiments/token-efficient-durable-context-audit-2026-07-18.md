# Token-Efficient Durable Context Audit — 2026-07-18

## Question and method

Does MAP’s current indexing/selective-retrieval path reduce startup context while preserving enough authority, provenance, and operational detail to route helper work correctly?

Reproducible scenario: a newly opened core agent must answer, “While Claude is unavailable, which helper lane may handle routine review work, what visibility boundary applies, and when should the fallback be reconsidered?”

Measurements use `wc -w -c` (whitespace-delimited words and bytes), not provider tokens; `tiktoken` is not installed. Percentages therefore demonstrate relative payload reduction, not exact model billing.

Commands:

```bash
python3 MAP_System/scripts/operational_lessons.py validate --pretty
python3 MAP_System/scripts/operational_lessons.py orientation \
  --scope startup --scope helper-routing --scope review-routing --pretty
wc -wc <paths>
```

## Communication standard used

`optimal-agent-communication-guide.md` says shorthand is a pointer, not a summary: stable references must resolve through authoritative, versioned, deterministic retrieval, while novel reasoning and safety boundaries remain explicit. `Guidelines/llm-communication-rules.md` similarly favors state over history, compact tokens for routine messages, mandatory reasons for failures, and no hidden rationale side channel.

The audit therefore treats a smaller payload as successful only when it still answers the routing question and preserves a recoverable path to authority and provenance.

## Baseline versus indexed retrieval

### A. Mandatory startup baseline

The Command Center startup contract requires root `AGENTS.md`, quickstart, project map, `MAP_System/AGENTS.md`, current state, decisions, status, handoff inspection, operational orientation, and task/runner state. The seven directly measured mandatory files below total:

| Baseline files | Words | Bytes |
|---|---:|---:|
| Root `AGENTS.md`, quickstart, project map, MAP `AGENTS.md`, current state, decisions, agent status | 8,617 | 67,884 |

Observed: current indexes do **not** replace this baseline. Startup guidance explicitly requires the full files. The orientation projection is incremental context, not a reduction of the mandatory stack.

### B. Unindexed/raw discovery of the helper fallback

A plausible file-first search through general indexes and provenance is:

| Raw path | Words | Bytes |
|---|---:|---:|
| `shared/memory-map.md` | 606 | 4,813 |
| `notes/README.md` | 237 | 1,839 |
| `emergence/INDEX.md` | 1,983 | 17,866 |
| `INS-0027` | 190 | 1,211 |
| `inbox/helpers/helper-review-task222.md` | 225 | 1,717 |
| `MAP_System/AGENTS.md` | 1,986 | 14,039 |
| **Total** | **5,227** | **41,485** |

This route eventually exposes the incident, fallback, and visibility authority, but it loads broad registries and scoped historical notes. It also requires the reader to infer which record became active behavior.

### C. Scoped indexed projection

The operational-learning command returns two active matching lessons:

| Indexed path | Words | Bytes |
|---|---:|---:|
| Generated `startup + helper-routing + review-routing` orientation | 135 | 1,319 |

Measured reduction versus the raw discovery path: **97.4% fewer words** and **96.8% fewer bytes**. Added to the measured mandatory startup baseline, however, the projection adds about **1.9% bytes**; it does not reduce the 67,884-byte baseline itself.

## Retrieval correctness

### What the projection preserves

- Action: route routine helper/review work to a bounded Codex helper while Claude is unavailable.
- Safety boundary: every model-backed helper remains visible; never hidden/headless.
- Reconsideration condition: a Claude core session successfully answers a readiness check.
- Stable identity: `OPLESSON-0001` and `OPLESSON-0002`.
- Provenance pointers: the source Insight, helper note, and `MAP_System/AGENTS.md`.
- Deterministic filtering: only active lessons matching requested scopes (or `all`) are emitted; validation passes for both current lessons.

Verdict: the 1,319-byte projection is adequate to perform this routine routing decision because the action, boundary, trigger, IDs, and source paths survive.

### What the projection loses

Compared with canonical `agents/operational-lessons.json`, orientation omits:

- lesson owner;
- `activated_at`;
- exact `review_after` (only derived `review_due` remains);
- explicit status (active is implicit in filtering);
- supersession fields;
- store/schema identity.

These omissions do not change the tested routine action today, but they matter when authority is disputed, two lessons conflict, a reader must distinguish “not due” from “no review date,” or a cached projection outlives a store change. The source paths make recovery possible, but neither source for `OPLESSON-0001` alone is the active authority: one is a `CLARIFIED` Insight and the other is a task-scoped helper note. The canonical authority is the validated operational-lessons store, which the projection does not name.

### Short links versus adequate context

- `notes/README.md` and `shared/memory-map.md` do not currently list `operational-learning-guide.md` or the operational-lessons store. They are short, but cannot discover this active behavior.
- `emergence/INDEX.md` resolves `INS-0027`, but is 17,866 bytes and mixes actionable, raw, parked, promoted, dismissed, and withdrawn records. Its link proves existence/provenance, not adopted authority.
- Wikilinks and file paths are valuable retrieval pointers only when the reader also knows the target’s authority class and current status. A path without that context is not an instruction.
- The optimal guide’s proposed `@MAP/1` approach requires a deterministic parser and versioned registry. No MAP/1 parser/registry was observed in the tested startup path. Current MATOCP tokens are useful wire shorthand, but should not be treated as self-decoding authoritative references beyond their documented fixed meanings.

## Proven savings and limits

1. **Proven:** scope-filtered operational orientation reduces this lesson lookup from 41,485 to 1,319 bytes without losing the immediate action, safety boundary, reconsideration trigger, or provenance links.
2. **Not proven:** indexes reduce total startup context. Current startup still mandates 67,884 measured bytes before task/handoff contents, and the projection is additional.
3. **Not proven:** whitespace words equal model tokens. Exact savings need the tokenizer/model actually used.
4. **Failure:** the two general note indexes do not expose the operational-learning mechanism, so a reader outside the launcher path may miss it.
5. **Risk:** projected lessons are compact enough to act on but not independently sufficient to adjudicate authority/lifecycle conflicts.

## Reversible recommendations

1. **Measure and slim the mandatory startup manifest.** Replace full-file startup loading with a generated, task-type/scope-selected manifest while retaining links to complete canonical files. Pilot beside the existing launcher and compare correct routing, bytes/tokens, and follow-up fetches before switching.
2. **Add minimal authority metadata to orientation output.** Include canonical store path, schema version, lesson owner, activation time, and exact review date (nullable). Keep source paths and summary; measure the small byte increase against conflict-resolution accuracy.
3. **Validate index coverage and freshness.** Add a report-only check that every CURRENT note intended for discovery appears in the appropriate index and that index verification dates are not older than linked active mechanisms. Start report-only and remove it if it produces no actionable misses.
4. **Query Emergence instead of loading its full index.** Prefer a deterministic status/project/ID query returning compact rows plus resolvable paths; retain the generated full index for human browsing. Test retrieval of `INS-0027` for correctness and bytes before adopting.
5. **Benchmark shorthand only with retrieval-correctness fixtures.** Measure current MATOCP/file-reference messages versus any MAP/1 prototype using actual provider tokenizers when available, but require both to recover owner, authority, state, safety constraints, and source targets. Do not add a DSL layer until its parser/registry beats the present scoped JSON projection on total coordination cost.

## Conclusion

MAP has one successful selective-retrieval mechanism: operational orientation delivers a roughly 97% smaller payload than raw provenance discovery for the tested routing question and remains actionable. The larger startup system has not yet realized the same benefit; it layers compact retrieval on top of mandatory full-document loading. The next efficiency gain should come from routing the existing canonical sources more selectively, not shortening links until their authority becomes implicit.
