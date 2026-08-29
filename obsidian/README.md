# Obsidian View of MAP Lean

Open the repository root as an Obsidian vault. The active navigation spine uses
**standard relative Markdown links**. Obsidian recognizes them in Graph view,
Local Graph, and Backlinks, while GitHub and ordinary coding agents can follow
the same paths directly. Use `[[wikilinks]]` only where a surface specifically
needs them; do not maintain a second link syntax just for the vault.

## Recommended Graph view

Filter out `path:legacy` when exploring the active system. The preserved legacy
corpus will otherwise dominate the graph visually. Start with the Local Graph for
[FIRST_RUN](../docs/FIRST_RUN.md), the [playbook index](../playbook/INDEX.md), or
the [work router](../work/README.md), then widen depth only for a concrete need.

A global graph is not an authority map: node size measures links, not correctness,
freshness, or decision authority. A dense graph is not automatically efficient.
The target is a road network with a few stable hubs and short useful routes.

## Digital Fungus workflow

Run the read-only analyzer from the vault root:

```bash
python3 tools/digital_fungus.py --root . --output-dir work/reports
```

It reports link edges, orphan candidates, FIRST_RUN reachability/resilience, and
**least-read-cost routes** to the stable navigation hubs. The token values are a
rough `characters / 4` comparison proxy, not model billing data.

Review findings before adding links. Prefer a direct route to the canonical owner
over topical cross-linking that only increases graph density.
