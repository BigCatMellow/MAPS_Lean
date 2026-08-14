# Obsidian View of MAP Lean

Open the `MultiAgentProject-Lean` root as an Obsidian vault. The active
navigation spine uses standard Markdown links, which Obsidian recognizes in
Graph view, Local Graph, and Backlinks while remaining portable to GitHub,
VS Code, and coding agents.

## Recommended Graph view filter

Filter out `path:legacy` when exploring the active system. The legacy tree
contains the preserved original MAP corpus and will otherwise dominate the
graph visually. Start with the Local Graph for [FIRST_RUN](../docs/FIRST_RUN.md)
or [the playbook index](../playbook/INDEX.md), then widen depth deliberately.

Do not use a global graph layout as an authority map: node size measures links,
not correctness, freshness, or decision authority. Use task/status fields and
the control-plane rules for that.

## Digital Fungus workflow

Run the read-only analyzer from the vault root:

```bash
python3 tools/digital_fungus.py --root . --output-dir work/reports
```

It reports actual link edges separately from code-styled file mentions. Review
its proposals before adding links; deliberate links should improve navigation,
not merely inflate graph density.

