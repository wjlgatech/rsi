## 🕸️ Living Knowledge Graph

This list is not just tables — it **compiles**. Every paper, repo, person, lab, talk and benchmark below is a node in a typed knowledge graph, with `authored_by` / `has_code` / `member_of` / `builds_on` edges connecting them:

- **🗺️ [Explore the interactive map](https://wjlgatech.github.io/awesome-auto-ai-research/)** — force-layout graph with search, type filters, and click-to-inspect (self-contained HTML; also works locally: open [`docs/index.html`](docs/index.html))
- **✨ Ask the field** — hit the *Ask* button on the map for grounded Q&A: a frontier model (GLM 5.1 / DeepSeek v4 / Kimi K2.6 on **NVIDIA's free API**) answers from the graph and cites nodes as clickable chips. Bring your own free key from [build.nvidia.com/models](https://build.nvidia.com/models) — it stays in your browser
- **🧩 [`knowledge/graph.json`](knowledge/graph.json)** — the full machine-readable graph (139 nodes · 246 edges) for your own agents, RAG pipelines, or analysis
- **🧬 [`knowledge/enrichments.json`](knowledge/enrichments.json)** — curator-written lineage edges (Gödel Machine → AI-GAs → DGM …) that survive regeneration

**It stays alive automatically.** Editing the README is all a contributor ever does — on every merge, [a GitHub Action](.github/workflows/knowledge.yml) recompiles the graph and the map, and [a weekly freshness check](.github/workflows/freshness.yml) probes every link and opens an issue if any die.

```bash
# regenerate locally (stdlib-only, deterministic, zero LLM calls)
python3 scripts/awesome_kg.py build README.md \
  --out knowledge/graph.json --html docs/index.html \
  --enrich knowledge/enrichments.json --title "Awesome Automated AI Research"

# check every link is still alive
python3 scripts/check_freshness.py README.md
```

> Built with the [`living-repo`](https://github.com/wjlgatech/sos/tree/main/plugins/sos/skills/living-repo) skill from the [sos toolkit](https://github.com/wjlgatech/sos) — point it at any awesome-list to get the same treatment.
