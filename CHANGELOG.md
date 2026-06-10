# Changelog

All notable changes to this repo are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- **"✨ Ask the field"** on the interactive map: grounded Q&A over the knowledge graph,
  answered by frontier models on **NVIDIA's free NIM API** (GLM 5.1 / DeepSeek v4 /
  Kimi K2.6). Visitors bring their own free key (build.nvidia.com/models, ~40 req/min);
  it lives only in their browser's localStorage and reaches NVIDIA via a keyless CORS
  bridge (nim-bridge.vercel.app — needed because NVIDIA's API only allows CORS from
  build.nvidia.com). Answers cite graph nodes as clickable chips that select them on
  the map. Retrieval is client-side over `knowledge/graph.json` — no backend, no
  tracking, the page stays a static file.
- **Living knowledge graph**: the README's tables now compile into a typed graph
  (`knowledge/graph.json`, 139 nodes · 246 edges: papers/repos/people/labs/talks/benchmarks
  with `authored_by`/`has_code`/`member_of`/`part_of`/`builds_on` edges) plus a
  self-contained interactive map at `docs/index.html` (GitHub Pages-ready) — so readers
  can interrogate the field, not just scroll it.
- `knowledge/enrichments.json` — curator-written lineage edges (Gödel Machine → AI-GAs →
  DGM, FunSearch → AlphaEvolve, …) that survive every regeneration.
- `scripts/awesome_kg.py` — deterministic, stdlib-only README→graph compiler (vendored
  from the [sos `living-repo` skill](https://github.com/wjlgatech/sos)); zero LLM calls,
  CI-safe, never invents a node.
- `scripts/check_freshness.py` + `.github/workflows/freshness.yml` — weekly link check
  that opens an issue on dead links. The README has claimed "automated weekly freshness
  checks via GitHub Actions" since day one; **this makes the claim true.**
- `.github/workflows/knowledge.yml` — recompiles graph + map on every README merge, so
  contributors only ever edit the README.

### Fixed
- 5 dead links found by the first freshness run: the ACL placeholder URL
  (`acl-long.xxx`) and the Springer DOI now point to their verified arXiv pages
  (2505.13259, 2110.05242); AgentRxiv code → agentrxiv.github.io;
  richard.socher.org → www.socher.org; ICLR 2025 keynote → iclr.cc/virtual/2025.

### Investigated / Rejected
- **LLM-extracted graph via dreammaketrue `kgfy`**: with the engine on its local
  qwen2.5:7b backup it produced 53 thin nodes and 25 edges, including hallucinated
  content ("Karpathy alchemy quote" — Karpathy appears nowhere in this README), vs the
  deterministic compiler's 139 fully-traceable nodes and 246 edges. Rejected until the
  engine runs a frontier model; the deterministic parse is also the only approach that
  can run in CI on every merge.
